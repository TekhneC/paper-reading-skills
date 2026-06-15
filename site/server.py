#!/usr/bin/env python3
"""Local web console for the paper-reading skills repository.

This server is intentionally small and standard-library only. It reads and
writes derived workflow artifacts inside this repository and never modifies
Zotero data.
"""

from __future__ import annotations

import argparse
import json
import mimetypes
import re
import sys
from datetime import datetime, timezone
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, quote, unquote, urlparse


SITE_ROOT = Path(__file__).resolve().parent
REPO_ROOT = SITE_ROOT.parent
STATIC_ROOT = SITE_ROOT / "static"

ALLOWED_STATES = {
    "queued",
    "quick_read_done",
    "deep_read_candidate",
    "deep_read_approved",
    "deep_read_done",
    "archived",
}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def local_date() -> str:
    return datetime.now().strftime("%Y-%m-%d")


def load_toml(path: Path) -> dict[str, Any]:
    try:
        import tomllib
    except ModuleNotFoundError:
        return load_minimal_toml(path)

    if not path.exists():
        return {}
    with path.open("rb") as handle:
        return tomllib.load(handle)


def load_minimal_toml(path: Path) -> dict[str, Any]:
    data: dict[str, Any] = {}
    section: dict[str, Any] | None = None
    if not path.exists():
        return data
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.split("#", 1)[0].strip()
        if not line:
            continue
        if line.startswith("[") and line.endswith("]"):
            section = data.setdefault(line[1:-1].strip(), {})
            continue
        if section is None or "=" not in line:
            continue
        key, value = [part.strip() for part in line.split("=", 1)]
        if value.startswith('"') and value.endswith('"'):
            section[key] = value[1:-1]
        elif value.isdigit():
            section[key] = int(value)
        elif value.lower() in {"true", "false"}:
            section[key] = value.lower() == "true"
        else:
            section[key] = value
    return data


CONFIG = load_toml(REPO_ROOT / "config" / "paths.toml")


def repo_path(*parts: str) -> Path:
    return (REPO_ROOT.joinpath(*parts)).resolve()


def configured_path(section: str, key: str, fallback: str) -> Path:
    value = CONFIG.get(section, {}).get(key, fallback)
    path = Path(value).expanduser()
    if not path.is_absolute():
        path = REPO_ROOT / path
    return path.resolve()


STATE_DIR = repo_path("state")
PAPERS_DIR = configured_path("outputs", "papers_dir", "outputs/papers")
THEMES_DIR = configured_path("outputs", "themes_dir", "outputs/themes")
DAILY_DIR = configured_path("outputs", "daily_dir", "outputs/daily")
APPROVALS_DIR = configured_path("state", "approvals_dir", "state/approvals")
QUEUE_PATH = configured_path("state", "reading_queue", "state/reading_queue.json")
WORKFLOW_STATE_PATH = STATE_DIR / "workflow_state.json"
EVENT_LOG_PATH = STATE_DIR / "reading_events.jsonl"
COREADING_MESSAGES_PATH = STATE_DIR / "coreading_messages.jsonl"
ZOTERO_STORAGE = Path(CONFIG.get("zotero", {}).get("storage_dir", "~/Zotero/storage")).expanduser().resolve()


def safe_key(value: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9_.-]+", "_", value.strip())
    return cleaned.strip("._")[:120] or "item"


def require_inside_repo(path: Path) -> Path:
    resolved = path.expanduser().resolve()
    repo = REPO_ROOT.resolve()
    if resolved != repo and repo not in resolved.parents:
        raise ValueError(f"Refusing to write outside repository: {resolved}")
    return resolved


def is_under(path: Path, root: Path) -> bool:
    resolved = path.resolve()
    base = root.resolve()
    return resolved == base or base in resolved.parents


def read_json(path: Path, default: Any = None) -> Any:
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        return {"_error": f"Could not parse {rel(path)}: {exc}"}


def write_json(path: Path, payload: Any) -> None:
    require_inside_repo(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_text_file(path: Path, content: str) -> None:
    require_inside_repo(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = path.with_name(f".{path.name}.tmp")
    temp_path.write_text(content, encoding="utf-8")
    temp_path.replace(path)


def append_jsonl(path: Path, payload: dict[str, Any]) -> None:
    require_inside_repo(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, ensure_ascii=False) + "\n")


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if not line.strip():
            continue
        try:
            value = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(value, dict):
            rows.append(value)
    return rows


def read_text(path: Path) -> str | None:
    if not path.exists():
        return None
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(encoding="utf-8", errors="replace")


def rel(path: Path | None) -> str | None:
    if path is None:
        return None
    try:
        return str(path.resolve().relative_to(REPO_ROOT.resolve())).replace("\\", "/")
    except ValueError:
        return str(path)


def file_record(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    return {
        "path": rel(path),
        "name": path.name,
        "size": path.stat().st_size,
        "modified_at": datetime.fromtimestamp(path.stat().st_mtime, timezone.utc).isoformat(),
    }


def markdown_record(path: Path) -> dict[str, Any] | None:
    record = file_record(path)
    if record is None:
        return None
    record["content"] = read_text(path) or ""
    return record


def mindmap_record(path: Path) -> dict[str, Any] | None:
    record = file_record(path)
    if record is None:
        return None
    data = read_json(path, None)
    record["data"] = data.get("data") if isinstance(data, dict) and "data" in data else data
    return record


def path_url(path: Path | None) -> str | None:
    return f"/api/file?path={quote(str(path), safe='')}" if path else None


def load_queue() -> dict[str, Any]:
    queue = read_json(QUEUE_PATH, {})
    return queue if isinstance(queue, dict) else {}


def save_queue(queue: dict[str, Any]) -> None:
    if queue:
        write_json(QUEUE_PATH, queue)


def load_workflow_state() -> dict[str, Any]:
    state = read_json(WORKFLOW_STATE_PATH, {})
    if not isinstance(state, dict):
        state = {}
    state.setdefault("schema_version", "1.0")
    state.setdefault("updated_at", utc_now())
    state.setdefault("papers", {})
    return state


def append_event(event_type: str, payload: dict[str, Any]) -> None:
    append_jsonl(EVENT_LOG_PATH, {"event_type": event_type, "created_at": utc_now(), **payload})


def update_queue_status(paper_key: str, status: str) -> None:
    queue = load_queue()
    changed = False
    for paper in queue.get("papers", []):
        if isinstance(paper, dict) and paper.get("paper_key") == paper_key:
            paper["status"] = status
            if status in {"quick_read_done", "deep_read_candidate", "deep_read_approved", "deep_read_done"}:
                paper["quick_read_status"] = "available"
            changed = True
    if changed:
        queue["updated_at"] = utc_now()
        save_queue(queue)


def set_workflow_state(paper_key: str, status: str, note: str = "", source: str = "local_site") -> dict[str, Any]:
    workflow = load_workflow_state()
    workflow["updated_at"] = utc_now()
    record = workflow["papers"].setdefault(paper_key, {})
    record.update(
        {
            "paper_key": paper_key,
            "status": status,
            "updated_at": workflow["updated_at"],
            "updated_by": source,
            "note": note,
        }
    )
    write_json(WORKFLOW_STATE_PATH, workflow)
    update_queue_status(paper_key, status)
    append_event("paper_state_updated", {"paper_key": paper_key, "status": status, "note": note})
    return record


def find_pdf_path(paper_key: str, queue_entry: dict[str, Any] | None) -> Path | None:
    candidates: list[str] = []
    if queue_entry:
        for field in ("pdf_path", "attachment_path", "local_pdf_path"):
            value = queue_entry.get(field)
            if isinstance(value, str):
                candidates.append(value)

    for source_json in [
        STATE_DIR / "cache" / "quick_read_sources" / f"{paper_key}.source.json",
        STATE_DIR / "cache" / "deep_read_sources" / paper_key / "source.json",
    ]:
        data = read_json(source_json, {})
        if isinstance(data, dict):
            for source in data.get("pdf_sources", []):
                if isinstance(source, dict) and isinstance(source.get("resolved_path"), str):
                    candidates.append(source["resolved_path"])
            for field in ("pdf_path", "attachment_path", "resolved_pdf_path"):
                value = data.get(field)
                if isinstance(value, str):
                    candidates.append(value)

    for value in candidates:
        path = Path(value).expanduser()
        if not path.is_absolute():
            path = REPO_ROOT / path
        if path.exists() and path.suffix.lower() == ".pdf":
            return path.resolve()
    return None


def is_allowed_file(path: Path) -> bool:
    allowed_roots = [REPO_ROOT.resolve()]
    if ZOTERO_STORAGE.exists():
        allowed_roots.append(ZOTERO_STORAGE)
    resolved = path.resolve()
    return any(resolved == root or root in resolved.parents for root in allowed_roots)


def infer_status(quick_md: Any, deep_md: Any, approval: Any) -> str:
    if deep_md:
        return "deep_read_done"
    if approval:
        return "deep_read_approved"
    if quick_md:
        return "quick_read_done"
    return "queued"


def paper_from_key(key: str, queue_entry: dict[str, Any] | None, workflow_record: dict[str, Any] | None) -> dict[str, Any]:
    paper_dir = PAPERS_DIR / key
    quick_json = read_json(paper_dir / "quick_read.json", {})
    deep_json = read_json(paper_dir / "deep_read.json", {})
    quick_md = markdown_record(paper_dir / "quick_read.md")
    deep_md = markdown_record(paper_dir / "deep_read.md")
    approval = read_json(APPROVALS_DIR / f"{safe_key(key)}.json", None)
    pdf_path = find_pdf_path(key, queue_entry)

    title = None
    for source in (deep_json, quick_json, queue_entry or {}):
        if isinstance(source, dict) and source.get("title"):
            title = source["title"]
            break

    status = (workflow_record or {}).get("status") or (queue_entry or {}).get("status") or infer_status(quick_md, deep_md, approval)
    return {
        "paper_key": key,
        "title": title or key,
        "authors": (queue_entry or {}).get("authors") or (quick_json or {}).get("authors") or [],
        "year": (queue_entry or {}).get("year") or (quick_json or {}).get("year") or (deep_json or {}).get("year"),
        "venue": (queue_entry or {}).get("publication_title") or (quick_json or {}).get("venue") or "",
        "status": status,
        "recommended_action": (quick_json or {}).get("recommended_action") or (queue_entry or {}).get("recommended_action"),
        "decision_label": (quick_json or {}).get("decision_label") or "",
        "evidence_status": (quick_json or {}).get("evidence_status") or (deep_json or {}).get("evidence_status") or "",
        "quick_read": quick_md,
        "quick_read_json": quick_json if isinstance(quick_json, dict) else {},
        "deep_read": deep_md,
        "deep_read_json": deep_json if isinstance(deep_json, dict) else {},
        "mindmap": mindmap_record(paper_dir / "mindmap.json"),
        "approval": approval,
        "workflow_state": workflow_record or {},
        "pdf": {"available": pdf_path is not None, "path": str(pdf_path) if pdf_path else None, "url": path_url(pdf_path)},
        "queue_entry": queue_entry,
    }


def list_papers() -> list[dict[str, Any]]:
    queue = load_queue()
    workflow = load_workflow_state()
    queue_entries: dict[str, dict[str, Any]] = {}
    for paper in queue.get("papers", []):
        if isinstance(paper, dict) and paper.get("paper_key"):
            queue_entries[paper["paper_key"]] = paper

    keys = set(queue_entries)
    if PAPERS_DIR.exists():
        keys.update(path.name for path in PAPERS_DIR.iterdir() if path.is_dir())
    keys.update(workflow.get("papers", {}).keys())
    return [
        paper_from_key(key, queue_entries.get(key), workflow.get("papers", {}).get(key))
        for key in sorted(keys, key=str.lower)
    ]


def list_daily_runs() -> list[dict[str, Any]]:
    if not DAILY_DIR.exists():
        return []
    runs = []
    for path in sorted([p for p in DAILY_DIR.iterdir() if p.is_dir()], reverse=True):
        runs.append(
            {
                "date": path.name,
                "digest": markdown_record(path / "digest.md"),
                "deep_read_candidates": read_json(path / "deep_read_candidates.json", None),
                "quick_reads": read_json(path / "quick_reads.json", None),
                "mindmap": mindmap_record(path / "mindmap.json"),
            }
        )
    return runs


def list_themes() -> list[dict[str, Any]]:
    if not THEMES_DIR.exists():
        return []
    themes = []
    for path in sorted([p for p in THEMES_DIR.iterdir() if p.is_dir()], key=lambda p: p.name.lower()):
        themes.append(
            {
                "theme_id": path.name,
                "theme_state": markdown_record(path / "theme_state.md"),
                "comparison_matrix": markdown_record(path / "comparison_matrix.md"),
                "synthesis_report": markdown_record(path / "synthesis_report.md"),
                "mindmap": mindmap_record(path / "mindmap.json"),
                "messages": read_jsonl(path / "message_inbox.jsonl")[-50:],
            }
        )
    return themes


def todo_target(mode: str, item_id: str, view: str = "overview") -> dict[str, str]:
    return {"mode": mode, "id": item_id, "view": view}


def build_todos(papers: list[dict[str, Any]], themes: list[dict[str, Any]], daily_runs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    todos: list[dict[str, Any]] = []
    for paper in papers:
        key = paper["paper_key"]
        if not paper.get("quick_read"):
            todos.append(
                {
                    "id": f"quick:{key}",
                    "kind": "paper",
                    "priority": "high",
                    "status": "open",
                    "title": f"补齐快读：{paper['title']}",
                    "paper_key": key,
                    "action": "quick_read",
                    "reason": "队列或缓存中存在文献，但 outputs/papers 下没有 quick_read.md。",
                    "target": todo_target("papers", key, "quick"),
                }
            )
        if paper.get("recommended_action") == "deep_read_candidate" and not paper.get("approval"):
            todos.append(
                {
                    "id": f"approve:{key}",
                    "kind": "approval",
                    "priority": "high",
                    "status": "open",
                    "title": f"审批精读：{paper['title']}",
                    "paper_key": key,
                    "action": "approve_deep_read",
                    "reason": "快读建议进入精读，但尚未形成 approval record。",
                    "target": todo_target("papers", key, "overview"),
                }
            )
        if paper.get("approval") and not paper.get("deep_read"):
            todos.append(
                {
                    "id": f"deep:{key}",
                    "kind": "paper",
                    "priority": "medium",
                    "status": "open",
                    "title": f"生成精读：{paper['title']}",
                    "paper_key": key,
                    "action": "deep_read",
                    "reason": "已审批，但还没有 canonical deep_read.md/deep_read.json。",
                    "target": todo_target("papers", key, "deep"),
                }
            )
    for theme in themes:
        if not theme.get("synthesis_report"):
            todos.append(
                {
                    "id": f"theme:{theme['theme_id']}",
                    "kind": "theme",
                    "priority": "medium",
                    "status": "open",
                    "title": f"完善共读综合：{theme['theme_id']}",
                    "theme_id": theme["theme_id"],
                    "action": "theme_synthesis",
                    "reason": "主题已有状态或矩阵，但 synthesis_report.md 不存在。",
                    "target": todo_target("themes", theme["theme_id"], "overview"),
                }
            )
    if not daily_runs:
        todos.append(
            {
                "id": "daily:missing",
                "kind": "daily",
                "priority": "low",
                "status": "open",
                "title": "生成当日阅读归档",
                "action": "daily_triage",
                "reason": "outputs/daily 下尚无按日期归档的阅读结果。",
                "target": todo_target("archives", "daily:latest", "overview"),
            }
        )
    return todos


def build_daily_payload(day: str, papers: list[dict[str, Any]], todos: list[dict[str, Any]]) -> tuple[str, dict[str, Any], dict[str, Any]]:
    quick_papers = []
    candidates = []
    for paper in papers:
        quick_json = paper.get("quick_read_json") or {}
        quick_papers.append(
            {
                "paper_key": paper["paper_key"],
                "title": paper["title"],
                "quick_read_status": "available" if paper.get("quick_read") else "missing",
                "recommended_action": paper.get("recommended_action") or "needs_quick_read",
                "one_sentence_summary": quick_json.get("one_sentence_summary") or "",
                "relation_to_user_research": quick_json.get("relation_to_user_research") or "",
                "evidence_source": quick_json.get("evidence_source") or "",
                "evidence_location": quick_json.get("evidence_location") or "",
                "uncertainty": quick_json.get("uncertainty") or "",
            }
        )
        if paper.get("recommended_action") == "deep_read_candidate":
            candidates.append(
                {
                    "rank": len(candidates) + 1,
                    "paper_key": paper["paper_key"],
                    "title": paper["title"],
                    "decision_label": paper.get("decision_label") or "candidate",
                    "recommendation_reason": quick_json.get("relation_to_user_research") or "由快读建议进入精读候选。",
                    "suggested_deep_read_focus": quick_json.get("suggested_deep_read_focus") or [],
                    "risk_or_uncertainty": quick_json.get("uncertainty") or "",
                    "evidence_source": quick_json.get("evidence_source") or "",
                    "evidence_location": quick_json.get("evidence_location") or "",
                    "qualitative_ratings": quick_json.get("qualitative_ratings") or {},
                    "high_rated_dimensions": quick_json.get("high_rated_dimensions") or [],
                }
            )

    quick_reads = {"schema_version": "1.0", "date": day, "queue_source": "local_site_trigger", "papers": quick_papers}
    deep_read_candidates = {"schema_version": "1.0", "date": day, "candidates": candidates}
    lines = [
        f"# Daily Archive - {day}",
        "",
        "## 今日工作台",
        "",
        f"- 待办数量：{len(todos)}",
        f"- 文献数量：{len(papers)}",
        f"- 精读候选：{len(candidates)}",
        "",
        "## 待办事项",
        "",
    ]
    if todos:
        for todo in todos:
            lines.append(f"- [{todo['priority']}] {todo['title']}：{todo['reason']}")
    else:
        lines.append("- 当前无派生待办。")
    lines.extend(["", "## 文献快读状态", ""])
    for paper in quick_papers:
        lines.append(f"- `{paper['paper_key']}` {paper['title']}：{paper['quick_read_status']} / {paper['recommended_action']}")
    lines.extend(["", "## 精读候选", ""])
    if candidates:
        for candidate in candidates:
            lines.append(f"{candidate['rank']}. `{candidate['paper_key']}` {candidate['title']} - {candidate['decision_label']}")
    else:
        lines.append("本次未形成精读候选。")
    lines.extend(["", "## 状态边界", "", "本归档由网页端触发生成，只写入本仓库 outputs/daily，不修改 Zotero。"])
    return "\n".join(lines) + "\n", quick_reads, deep_read_candidates


def write_daily_archive(day: str | None = None) -> dict[str, Any]:
    day = day or local_date()
    papers = list_papers()
    themes = list_themes()
    existing_runs = list_daily_runs()
    todos = build_todos(papers, themes, existing_runs)
    digest, quick_reads, candidates = build_daily_payload(day, papers, todos)
    target_dir = DAILY_DIR / day
    require_inside_repo(target_dir)
    target_dir.mkdir(parents=True, exist_ok=True)
    write_text_file(target_dir / "digest.md", digest)
    write_json(target_dir / "quick_reads.json", quick_reads)
    write_json(target_dir / "deep_read_candidates.json", candidates)
    append_event("daily_archive_generated", {"date": day, "path": rel(target_dir)})
    return {
        "date": day,
        "path": rel(target_dir),
        "digest": markdown_record(target_dir / "digest.md"),
        "quick_reads": quick_reads,
        "deep_read_candidates": candidates,
    }


def latest_daily(daily_runs: list[dict[str, Any]]) -> dict[str, Any] | None:
    return daily_runs[0] if daily_runs else None


def build_dashboard() -> dict[str, Any]:
    papers = list_papers()
    themes = list_themes()
    daily_runs = list_daily_runs()
    todos = build_todos(papers, themes, daily_runs)
    messages = read_jsonl(COREADING_MESSAGES_PATH)[-30:]
    return {
        "repo": {
            "root": str(REPO_ROOT),
            "papers_dir": rel(PAPERS_DIR),
            "themes_dir": rel(THEMES_DIR),
            "daily_dir": rel(DAILY_DIR),
            "workflow_state": rel(WORKFLOW_STATE_PATH),
            "coreading_messages": rel(COREADING_MESSAGES_PATH),
        },
        "summary": {
            "todo_count": len(todos),
            "paper_count": len(papers),
            "approved_count": sum(1 for paper in papers if paper.get("approval")),
            "quick_read_count": sum(1 for paper in papers if paper.get("quick_read")),
            "deep_read_count": sum(1 for paper in papers if paper.get("deep_read")),
            "archive_count": len(daily_runs),
            "theme_count": len(themes),
            "message_count": len(messages),
        },
        "todos": todos,
        "papers": papers,
        "themes": themes,
        "daily_runs": daily_runs,
        "latest_daily": latest_daily(daily_runs),
        "messages": messages,
    }


def markdown_path_from_payload(payload: dict[str, Any]) -> Path:
    raw_path = str(payload.get("path") or "").strip()
    if raw_path:
        path = Path(raw_path)
        if not path.is_absolute():
            path = REPO_ROOT / path
        path = path.resolve()
    else:
        paper_key = safe_key(str(payload.get("paper_key") or ""))
        doc_type = str(payload.get("doc_type") or "")
        if doc_type not in {"quick", "deep"} or not paper_key:
            raise ValueError("Missing path or valid paper_key/doc_type")
        filename = "quick_read.md" if doc_type == "quick" else "deep_read.md"
        path = (PAPERS_DIR / paper_key / filename).resolve()
    require_inside_repo(path)
    if path.suffix.lower() != ".md" or not is_under(path, REPO_ROOT / "outputs"):
        raise ValueError("Markdown edits are limited to outputs/**/*.md")
    return path


def mindmap_path_from_payload(payload: dict[str, Any]) -> Path:
    target_type = str(payload.get("target_type") or "").strip()
    target_id = safe_key(str(payload.get("target_id") or ""))
    if not target_type or not target_id:
        raise ValueError("Missing target_type or target_id")
    if target_type == "paper":
        path = PAPERS_DIR / target_id / "mindmap.json"
    elif target_type == "theme":
        path = THEMES_DIR / target_id / "mindmap.json"
    elif target_type == "archive":
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", target_id):
            raise ValueError("Archive mindmap target must be YYYY-MM-DD")
        path = DAILY_DIR / target_id / "mindmap.json"
    else:
        raise ValueError("Unsupported mindmap target_type")
    require_inside_repo(path)
    if not is_under(path, REPO_ROOT / "outputs"):
        raise ValueError("Mindmap edits are limited to outputs/")
    return path


class RequestHandler(SimpleHTTPRequestHandler):
    server_version = "PaperReadingSite/0.3"

    def translate_path(self, path: str) -> str:
        parsed = urlparse(path)
        clean = unquote(parsed.path).lstrip("/") or "index.html"
        target = (STATIC_ROOT / clean).resolve()
        try:
            target.relative_to(STATIC_ROOT.resolve())
        except ValueError:
            return str(STATIC_ROOT / "index.html")
        if target.is_dir():
            target = target / "index.html"
        return str(target)

    def do_GET(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        if parsed.path == "/api/dashboard":
            self.send_json(build_dashboard())
            return
        if parsed.path == "/api/file":
            self.serve_local_file(parsed)
            return
        if parsed.path == "/":
            self.path = "/index.html"
        super().do_GET()

    def do_POST(self) -> None:  # noqa: N802
        try:
            parsed = urlparse(self.path)
            if parsed.path == "/api/approvals":
                self.create_approval()
                return
            if parsed.path == "/api/paper-state":
                self.update_paper_state()
                return
            if parsed.path == "/api/coreading/messages":
                self.create_coreading_message()
                return
            if parsed.path == "/api/daily/run":
                self.create_daily_archive()
                return
            if parsed.path == "/api/markdown":
                self.update_markdown()
                return
            if parsed.path == "/api/mindmap":
                self.update_mindmap()
                return
            self.send_error(HTTPStatus.NOT_FOUND, "Unknown endpoint")
        except OSError as exc:
            self.send_json({"ok": False, "error": str(exc)}, HTTPStatus.INTERNAL_SERVER_ERROR)
        except ValueError as exc:
            self.send_json({"ok": False, "error": str(exc)}, HTTPStatus.BAD_REQUEST)

    def read_payload(self) -> dict[str, Any]:
        length = int(self.headers.get("Content-Length", "0"))
        try:
            payload = json.loads(self.rfile.read(length).decode("utf-8") or "{}")
        except json.JSONDecodeError:
            self.send_error(HTTPStatus.BAD_REQUEST, "Invalid JSON")
            return {}
        return payload if isinstance(payload, dict) else {}

    def create_approval(self) -> None:
        payload = self.read_payload()
        paper_key = safe_key(str(payload.get("paper_key") or ""))
        if not paper_key:
            self.send_error(HTTPStatus.BAD_REQUEST, "Missing paper_key")
            return
        record = {
            "schema_version": "1.0",
            "paper_key": paper_key,
            "title": payload.get("title") or "",
            "approved_at": utc_now(),
            "approval_source": "local_site",
            "approved_by": payload.get("approved_by") or "user",
            "note": payload.get("note") or "",
            "suggested_deep_read_focus": payload.get("suggested_deep_read_focus") or [],
        }
        path = APPROVALS_DIR / f"{paper_key}.json"
        write_json(path, record)
        state_record = set_workflow_state(paper_key, "deep_read_approved", record["note"], "local_site")
        append_event("deep_read_approved", {"paper_key": paper_key, "path": rel(path)})
        self.send_json({"ok": True, "approval": record, "workflow_state": state_record, "path": rel(path)})

    def update_paper_state(self) -> None:
        payload = self.read_payload()
        paper_key = safe_key(str(payload.get("paper_key") or ""))
        status = str(payload.get("status") or "")
        note = str(payload.get("note") or "")
        if not paper_key or status not in ALLOWED_STATES:
            self.send_error(HTTPStatus.BAD_REQUEST, "Missing paper_key or invalid status")
            return
        if status == "deep_read_approved" and not (APPROVALS_DIR / f"{paper_key}.json").exists():
            self.send_error(HTTPStatus.CONFLICT, "deep_read_approved requires an approval record")
            return
        if status == "deep_read_done":
            if not (PAPERS_DIR / paper_key / "deep_read.md").exists() or not (PAPERS_DIR / paper_key / "deep_read.json").exists():
                self.send_error(HTTPStatus.CONFLICT, "deep_read_done requires deep_read.md and deep_read.json")
                return
        if status == "archived":
            self.send_error(HTTPStatus.CONFLICT, "Archiving is intentionally disabled in the local site")
            return
        record = set_workflow_state(paper_key, status, note, "local_site")
        self.send_json({"ok": True, "workflow_state": record})

    def create_coreading_message(self) -> None:
        payload = self.read_payload()
        body = str(payload.get("body") or "").strip()
        if not body:
            self.send_error(HTTPStatus.BAD_REQUEST, "Missing message body")
            return
        theme_id = safe_key(str(payload.get("theme_id") or "general"))
        record = {
            "schema_version": "1.0",
            "message_id": f"msg_{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S%f')}",
            "created_at": utc_now(),
            "theme_id": theme_id,
            "paper_key": safe_key(str(payload.get("paper_key") or "")) if payload.get("paper_key") else "",
            "sender": payload.get("sender") or "local_site",
            "target": payload.get("target") or "codex_thread_bridge",
            "body": body,
            "forward_status": "queued_for_local_bridge",
        }
        append_jsonl(COREADING_MESSAGES_PATH, record)
        theme_inbox = THEMES_DIR / theme_id / "message_inbox.jsonl"
        if (THEMES_DIR / theme_id).exists():
            append_jsonl(theme_inbox, record)
        append_event("coreading_message_queued", {"message_id": record["message_id"], "theme_id": theme_id})
        self.send_json({"ok": True, "message": record})

    def create_daily_archive(self) -> None:
        payload = self.read_payload()
        day = str(payload.get("date") or local_date())
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", day):
            self.send_error(HTTPStatus.BAD_REQUEST, "date must be YYYY-MM-DD")
            return
        archive = write_daily_archive(day)
        self.send_json({"ok": True, "archive": archive})

    def update_markdown(self) -> None:
        payload = self.read_payload()
        content = payload.get("content")
        if not isinstance(content, str):
            self.send_error(HTTPStatus.BAD_REQUEST, "Missing Markdown content")
            return
        path = markdown_path_from_payload(payload)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        append_event("markdown_updated", {"path": rel(path)})
        self.send_json({"ok": True, "file": markdown_record(path)})

    def update_mindmap(self) -> None:
        payload = self.read_payload()
        data = payload.get("data")
        if not isinstance(data, dict):
            self.send_error(HTTPStatus.BAD_REQUEST, "Missing mindmap data")
            return
        path = mindmap_path_from_payload(payload)
        record = {
            "schema_version": "1.0",
            "updated_at": utc_now(),
            "target_type": payload.get("target_type"),
            "target_id": safe_key(str(payload.get("target_id") or "")),
            "data": data,
        }
        write_json(path, record)
        append_event("mindmap_updated", {"path": rel(path)})
        self.send_json({"ok": True, "file": mindmap_record(path)})

    def serve_local_file(self, parsed: Any) -> None:
        query = parse_qs(parsed.query)
        raw = query.get("path", [""])[0]
        if not raw:
            self.send_error(HTTPStatus.BAD_REQUEST, "Missing path")
            return
        path = Path(raw).expanduser()
        if not path.is_absolute():
            path = REPO_ROOT / path
        path = path.resolve()
        if not path.exists() or not path.is_file() or not is_allowed_file(path):
            self.send_error(HTTPStatus.NOT_FOUND, "File not available")
            return
        mime = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", mime)
        self.send_header("Content-Length", str(path.stat().st_size))
        self.end_headers()
        with path.open("rb") as handle:
            self.copyfile(handle, self.wfile)

    def send_json(self, payload: Any, status: HTTPStatus = HTTPStatus.OK) -> None:
        body = json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format: str, *args: Any) -> None:
        sys.stderr.write("[%s] %s\n" % (self.log_date_time_string(), format % args))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Serve the local paper-reading web console.")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    server = ThreadingHTTPServer((args.host, args.port), RequestHandler)
    print(f"Paper reading site: http://{args.host}:{args.port}")
    print(f"Repository: {REPO_ROOT}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping server.")
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
