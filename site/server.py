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
import os
import re
import shutil
import shlex
import subprocess
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

STATE_RANK = {
    "queued": 0,
    "quick_read_done": 1,
    "deep_read_candidate": 2,
    "deep_read_approved": 3,
    "deep_read_done": 4,
    "archived": 5,
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
DEEP_INTERACTION_MESSAGES_PATH = STATE_DIR / "deep_read_interaction_messages.jsonl"
DAILY_RUN_STATUS_PATH = STATE_DIR / "daily_run_status.json"
DAILY_RUN_LOG_PATH = STATE_DIR / "daily_run_log.jsonl"
ZOTERO_DB = Path(CONFIG.get("zotero", {}).get("db_path", "~/Zotero/zotero.sqlite")).expanduser().resolve()
ZOTERO_STORAGE = Path(CONFIG.get("zotero", {}).get("storage_dir", "~/Zotero/storage")).expanduser().resolve()
QUEUE_CONFIG = CONFIG.get("queue", {}) if isinstance(CONFIG.get("queue", {}), dict) else {}
REFRESH_QUEUE_DAILY_DEFAULT = bool(QUEUE_CONFIG.get("refresh_from_zotero_on_daily", True))
QUEUE_BUILDER_SCRIPT = configured_path(
    "scripts",
    "build_reading_queue_from_zotero_todo",
    "scripts/build_reading_queue_from_zotero_todo.py",
)

THEME_MARKDOWN_OUTPUTS = [
    ("theme_state", "主题状态", "theme_state.md", False),
    ("comparison_matrix", "比较矩阵", "comparison_matrix.md", True),
    ("synthesis_report", "综合报告", "synthesis_report.md", True),
]

DEEP_INTERACTION_MODE_LABELS = {
    "confirmation": "确认理解",
    "clarification": "澄清概念",
    "follow_up": "延伸问题",
    "divergent_thinking": "研究发散",
    "correction": "事实纠错",
}

CODEX_CONFIG = CONFIG.get("codex", {}) if isinstance(CONFIG.get("codex", {}), dict) else {}
CODEX_COMMAND = os.environ.get("PAPER_READING_CODEX_COMMAND") or CODEX_CONFIG.get("command", "codex")
CODEX_EXEC_ARGS = CODEX_CONFIG.get("exec_args", ["exec"])
CODEX_TIMEOUT_SECONDS = int(CODEX_CONFIG.get("timeout_seconds", 600))
RUN_CODEX_DAILY_DEFAULT = bool(CODEX_CONFIG.get("run_daily_from_site", True))
DAILY_FALLBACK_ON_CODEX_FAILURE_DEFAULT = bool(CODEX_CONFIG.get("daily_fallback_on_codex_failure", False))
RUNTIME_CONFIG = CONFIG.get("runtime", {}) if isinstance(CONFIG.get("runtime", {}), dict) else {}
PYTHON_COMMAND = (
    os.environ.get("PAPER_READING_PYTHON_COMMAND")
    or RUNTIME_CONFIG.get("python_command")
    or RUNTIME_CONFIG.get("python_path")
    or ""
)


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
    content = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    temp_path = path.with_name(f".{path.name}.tmp")
    temp_path.write_text(content, encoding="utf-8")
    temp_path.replace(path)


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


def try_append_jsonl(path: Path, payload: dict[str, Any]) -> str | None:
    try:
        append_jsonl(path, payload)
    except (OSError, ValueError) as exc:
        return f"{rel(path)}: {exc}"
    return None


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    require_inside_repo(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    content = "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows)
    temp_path = path.with_name(f".{path.name}.tmp")
    temp_path.write_text(content, encoding="utf-8")
    temp_path.replace(path)


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows: list[dict[str, Any]] = []
    try:
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return []
    for line in lines:
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


def compact_text(value: str, limit: int = 4000) -> str:
    text = re.sub(r"\s+", " ", value).strip()
    if len(text) <= limit:
        return text
    return f"{text[:limit].rstrip()}..."


def command_parts(value: Any) -> list[str]:
    if isinstance(value, list):
        return [str(part) for part in value if str(part).strip()]
    text = str(value or "").strip()
    if not text:
        return []
    return shlex.split(text, posix=os.name != "nt")


def codex_exec_args() -> list[str]:
    args = command_parts(CODEX_EXEC_ARGS)
    return args or ["exec"]


def is_windowsapps_python(path: str) -> bool:
    normalized = path.replace("\\", "/").lower()
    name = Path(path).name.lower()
    return "/windowsapps/" in normalized and name in {"python.exe", "python3.exe", "python", "python3"}


def bundled_python_candidates() -> list[Path]:
    candidates = [
        Path.home()
        / ".cache"
        / "codex-runtimes"
        / "codex-primary-runtime"
        / "dependencies"
        / "python"
        / ("python.exe" if os.name == "nt" else "python"),
    ]
    return [path for path in candidates if path.is_file()]


def resolved_python_command() -> list[str]:
    configured = command_parts(PYTHON_COMMAND)
    if configured:
        executable = configured[0]
        has_path_separator = any(sep in executable for sep in ("\\", "/")) or Path(executable).is_absolute()
        if has_path_separator and Path(executable).exists() and not is_windowsapps_python(executable):
            return configured
        if not has_path_separator:
            found = shutil.which(executable)
            if found and not is_windowsapps_python(found):
                return [found, *configured[1:]]

    if sys.executable and Path(sys.executable).exists() and not is_windowsapps_python(sys.executable):
        return [sys.executable]

    for candidate in bundled_python_candidates():
        return [str(candidate)]

    for executable in ("python", "python3", "py"):
        found = shutil.which(executable)
        if found and not is_windowsapps_python(found):
            return [found]
    return configured or ([sys.executable] if sys.executable else [])


def local_codex_candidates() -> list[Path]:
    root = Path.home() / "AppData" / "Local" / "OpenAI" / "Codex" / "bin"
    if not root.exists():
        return []
    candidates = [path for path in root.glob("*/codex.exe") if path.is_file()]
    return sorted(candidates, key=lambda path: path.stat().st_mtime, reverse=True)


def is_windowsapps_codex(path: str) -> bool:
    normalized = path.replace("\\", "/").lower()
    return "/windowsapps/openai.codex_" in normalized and normalized.endswith(("/codex", "/codex.exe"))


def resolved_codex_command() -> list[str]:
    configured = command_parts(CODEX_COMMAND)
    if not configured:
        return []
    executable = configured[0]
    has_path_separator = any(sep in executable for sep in ("\\", "/")) or Path(executable).is_absolute()
    if has_path_separator and Path(executable).exists() and not is_windowsapps_codex(executable):
        return configured
    # Windows exposes a Store/AppX shim on PATH that can exist but fail from
    # service-like subprocesses. Prefer the real desktop CLI binary when the
    # command is the generic `codex` or that AppX shim.
    if executable.lower() in {"codex", "codex.exe"} or is_windowsapps_codex(executable):
        for candidate in local_codex_candidates():
            return [str(candidate), *configured[1:]]
    if not has_path_separator:
        found = shutil.which(executable)
        if found and not is_windowsapps_codex(found):
            return [found, *configured[1:]]
    for candidate in local_codex_candidates():
        return [str(candidate), *configured[1:]]
    return configured


def run_external_codex(prompt: str) -> dict[str, Any]:
    """Run an external Codex turn and return a UI-safe result record."""
    command_base = resolved_codex_command()
    if not command_base:
        return {"ok": False, "status": "codex_command_missing", "reply": "未配置外部 Codex 命令。"}
    output_dir = STATE_DIR / "tmp" / "codex_interactions"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"codex_reply_{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S%f')}_{os.getpid()}.md"
    command = command_base + codex_exec_args() + ["--output-last-message", str(output_path), "-"]
    try:
        result = subprocess.run(
            command,
            cwd=REPO_ROOT,
            input=prompt,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=CODEX_TIMEOUT_SECONDS,
        )
    except FileNotFoundError:
        return {
            "ok": False,
            "status": "codex_command_not_found",
            "reply": f"未找到外部 Codex 命令：`{command[0]}`。请在环境变量 PAPER_READING_CODEX_COMMAND 或 config/paths.toml 的 [codex].command 中配置。",
            "command": command[:2],
        }
    except PermissionError as exc:
        return {
            "ok": False,
            "status": "codex_permission_denied",
            "reply": f"外部 Codex 命令无法执行：{exc}",
            "command": command[:2],
        }
    except subprocess.TimeoutExpired:
        return {
            "ok": False,
            "status": "codex_timeout",
            "reply": f"外部 Codex 调用超过 {CODEX_TIMEOUT_SECONDS} 秒，已停止等待。",
            "command": command[:2],
        }

    stdout = (result.stdout or "").strip()
    stderr = (result.stderr or "").strip()
    final_reply = (read_text(output_path) or "").strip()
    try:
        output_path.unlink(missing_ok=True)
    except OSError:
        pass
    if result.returncode != 0:
        detail = stderr or stdout or f"exit code {result.returncode}"
        return {
            "ok": False,
            "status": "codex_failed",
            "reply": f"外部 Codex 调用失败：\n\n```text\n{detail}\n```",
            "command": command[:2],
            "returncode": result.returncode,
        }
    return {
        "ok": True,
        "status": "codex_completed",
        "reply": final_reply or stdout or "外部 Codex 未返回文本。",
        "command": command[:2],
        "returncode": result.returncode,
    }


def refresh_reading_queue_from_zotero() -> dict[str, Any]:
    """Refresh the derived queue from Zotero's configured todo tag."""
    if not ZOTERO_DB.exists():
        return {
            "ok": False,
            "status": "zotero_db_missing",
            "message": f"Configured Zotero database does not exist: {ZOTERO_DB}",
            "db_path": str(ZOTERO_DB),
            "queue_path": rel(QUEUE_PATH),
        }
    if not QUEUE_BUILDER_SCRIPT.exists():
        return {
            "ok": False,
            "status": "queue_builder_missing",
            "message": f"Queue builder script does not exist: {rel(QUEUE_BUILDER_SCRIPT)}",
            "script": rel(QUEUE_BUILDER_SCRIPT),
            "queue_path": rel(QUEUE_PATH),
        }

    python_command = resolved_python_command()
    if not python_command:
        return {
            "ok": False,
            "status": "python_command_missing",
            "message": "No usable Python command is configured for queue refresh.",
            "queue_path": rel(QUEUE_PATH),
        }

    command = [
        *python_command,
        str(QUEUE_BUILDER_SCRIPT),
        "--config",
        str(REPO_ROOT / "config" / "paths.toml"),
        "--output",
        str(QUEUE_PATH),
        "--force",
    ]
    try:
        result = subprocess.run(
            command,
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=120,
        )
    except subprocess.TimeoutExpired:
        return {
            "ok": False,
            "status": "queue_refresh_timeout",
            "message": "Refreshing reading_queue.json from Zotero exceeded 120 seconds.",
            "command": command[:2],
            "queue_path": rel(QUEUE_PATH),
        }
    except OSError as exc:
        return {
            "ok": False,
            "status": "queue_refresh_error",
            "message": str(exc),
            "command": command[:2],
            "queue_path": rel(QUEUE_PATH),
        }

    stdout = (result.stdout or "").strip()
    stderr = (result.stderr or "").strip()
    queue = read_json(QUEUE_PATH, {})
    paper_count = queue.get("paper_count") if isinstance(queue, dict) else None
    if result.returncode != 0:
        return {
            "ok": False,
            "status": "queue_refresh_failed",
            "message": stderr or stdout or f"Queue builder exited with code {result.returncode}.",
            "command": command[:2],
            "returncode": result.returncode,
            "queue_path": rel(QUEUE_PATH),
        }
    return {
        "ok": True,
        "status": "queue_refreshed",
        "message": stdout or "reading_queue.json refreshed from Zotero todo tag.",
        "command": command[:2],
        "returncode": result.returncode,
        "queue_path": rel(QUEUE_PATH),
        "paper_count": paper_count,
        "generated_at": queue.get("generated_at") if isinstance(queue, dict) else None,
        "tag": (queue.get("source") or {}).get("tag") if isinstance(queue, dict) else None,
    }


def parse_deep_interaction_codex_reply(raw_reply: str, fallback_mode: str) -> dict[str, str]:
    """Extract the skill's machine envelope while keeping the UI chat-only."""
    text = raw_reply.strip()
    allowed_modes = {"confirmation", "clarification", "follow_up", "divergent_thinking"}
    safe_fallback = fallback_mode if fallback_mode in allowed_modes else "follow_up"
    parsed: Any = None
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, flags=re.DOTALL)
        if match:
            try:
                parsed = json.loads(match.group(1))
            except json.JSONDecodeError:
                parsed = None
    if isinstance(parsed, dict):
        mode = safe_key(str(parsed.get("interaction_mode") or safe_fallback))
        if mode not in allowed_modes:
            mode = safe_fallback
        answer = str(parsed.get("answer_markdown") or parsed.get("answer") or "").strip()
        if answer:
            return {"interaction_mode": mode, "answer_markdown": answer}
    return {"interaction_mode": safe_fallback, "answer_markdown": raw_reply}


def recent_turns(messages: list[dict[str, Any]], limit: int = 6) -> str:
    turns = []
    for message in messages[-limit:]:
        body = compact_text(str(message.get("body") or ""), 1200)
        reply = compact_text(str(message.get("assistant_reply") or message.get("reply_markdown") or ""), 1200)
        if message.get("reply_status") == "local_skill_draft" or "deep-read-interaction 回复草稿" in reply:
            reply = "[旧版报告式草稿已省略；后续请按聊天式直接回答。]"
        turns.append(f"- user ({message.get('created_at', '')}): {body}")
        if reply:
            turns.append(f"  assistant: {reply}")
    return "\n".join(turns) or "暂无历史对话。"


def build_deep_read_codex_prompt(record: dict[str, Any], history: list[dict[str, Any]]) -> str:
    paper_key = record["paper_key"]
    paper_dir = PAPERS_DIR / paper_key
    mode = record.get("interaction_mode") or "follow_up"
    return f"""Use $deep-read-interaction.

You are being called by the local paper-reading website as a chat assistant.
Answer the user's latest question directly. Do not produce a full Markdown
document, report, note template, metadata block, or source-context dump.

Do not directly edit files. The user will read your chat reply and then manually
edit `deep_read.md` or co-reading Markdown in the web UI.

Repository root: {REPO_ROOT}
paper_key: {paper_key}
interaction_mode: {mode}
mode_label: {DEEP_INTERACTION_MODE_LABELS.get(mode, mode)}
classification_policy:
- If interaction_mode is `auto`, infer exactly one of:
  `confirmation`, `clarification`, `follow_up`, `divergent_thinking`.
- If interaction_mode is one of those four values, treat it as the user's manual
  classification unless the latest question clearly contradicts it.
- Do not expose the classification process in the user-facing answer.

可用上下文路径：
- deep_read: {rel(paper_dir / "deep_read.md")}
- deep_read_json: {rel(paper_dir / "deep_read.json")}
- quick_read: {rel(paper_dir / "quick_read.md")}
- quick_read_json: {rel(paper_dir / "quick_read.json")}
- deep source cache: {rel(STATE_DIR / "cache" / "deep_read_sources" / paper_key)}
- external verification: {rel(STATE_DIR / "external_verification" / f"{paper_key}.json")}

最近对话：
{recent_turns(history)}

用户最新问题：
{record["body"]}

Chat answer contract:
- Reply in Chinese, preserving necessary English technical terms.
- Start with the direct answer to the user's question. No title is needed.
- Keep the default answer concise: usually 2-5 short paragraphs or bullets.
- Do not include `paper_key`, `interaction_mode`, `evidence_status`, "用户问题",
  "回复草稿", "保存前建议", or any similar wrapper.
- Do not paste long excerpts from `deep_read.md`, `quick_read.md`, source cache,
  or prior chat. Use those files only as private context.
- For ordinary follow-up questions, explain the reasoning first. Mention evidence
  only briefly when it is necessary for confidence.
- Provide detailed evidence locations only when the user asks for evidence,
  asks to verify a claim, asks for correction, or factual precision is critical.
- If evidence is insufficient, say so directly and explain what would need to be
  checked next.
- If suggesting edits, phrase them as short actionable suggestions, not as a
  complete replacement document.

Return contract:
Return only a valid JSON object with this shape:
{{
  "interaction_mode": "confirmation | clarification | follow_up | divergent_thinking",
  "answer_markdown": "直接展示给用户的聊天式回答"
}}
Do not wrap the JSON in Markdown fences.
"""


def build_coreading_codex_prompt(record: dict[str, Any], history: list[dict[str, Any]]) -> str:
    theme_id = record["theme_id"]
    theme_dir = THEMES_DIR / theme_id
    return f"""Use $theme-coreading.

你正在被本地 paper-reading 网站调用。请按 theme-coreading skill 与现有主题上下文回答用户问题，但不要直接编辑任何文件；网页端会把你的回复展示在共读聊天，用户会根据聊天记录自行编辑公开的共读 Markdown。

Repository root: {REPO_ROOT}
theme_id: {theme_id}
paper_key: {record.get("paper_key") or "未指定"}
intent: {record.get("intent") or "open_question"}

内部上下文（可读取但不要作为公开 Markdown 面板复述全文）：
- theme_state: {rel(theme_dir / "theme_state.md")}

公开可编辑产物：
- comparison_matrix: {rel(theme_dir / "comparison_matrix.md")}
- synthesis_report: {rel(theme_dir / "synthesis_report.md")}

最近对话：
{recent_turns(history)}

用户最新问题：
{record["body"]}

回复要求：
- 使用中文，保留必要英文术语。
- 将 theme_state 视为不对外展示的 context；只提炼必要结论，不复制状态文件全文。
- 对跨论文判断标注证据层级和不确定性。
- 给出可直接用于用户手动修改 comparison_matrix.md 或 synthesis_report.md 的建议，但不要替用户写入文件。
"""


def build_daily_triage_codex_prompt(day: str) -> str:
    python_command = json.dumps(resolved_python_command(), ensure_ascii=False)
    return f"""Use $daily-paper-triage.

You are being called by the local paper-reading website after the user pressed
the Daily workflow button. Run the daily triage workflow for {day}.

Repository root: {REPO_ROOT}
Stable Python command for repository scripts: {python_command}

Required behavior:
- Read AGENTS.md and the daily-paper-triage skill files before acting.
- Use derived local state only; do not modify Zotero or original PDFs.
- Do not use git and do not do broad source exploration; this is a bounded local
  workflow over the Zotero-derived todo queue and repository-local outputs.
- Inspect `state/reading_queue.json`, `state/workflow_state.json`,
  `state/approvals/`, and existing `outputs/papers/*/quick_read.*`.
- When running repository Python scripts such as
  `scripts/extract_quick_read_source.py`, use the stable Python command above;
  do not rely on PATH `python` when it resolves to a WindowsApps shim.
- For queued papers that are missing canonical quick-read outputs, invoke
  `$single-paper-quick-read` in the same external Codex run and generate:
  `outputs/papers/<paper_key>/quick_read.md`
  `outputs/papers/<paper_key>/quick_read.json`
- After quick reads are present or clearly failed, continue the
  `$daily-paper-triage` aggregation and record unresolved failures in the
  daily outputs rather than silently skipping them.
- Write or update exactly these daily outputs:
  `outputs/daily/{day}/digest.md`
  `outputs/daily/{day}/quick_reads.json`
  `outputs/daily/{day}/deep_read_candidates.json`
- Use the schemas from `skills/daily-paper-triage/references/schema.md`.
- Do not mark any paper as `deep_read_approved` or `deep_read_done`.
- Do not downgrade any existing state. A paper that already has approval or a
  canonical deep_read.md/deep_read.json must not appear as a new deep-read
  candidate.
- End with a concise Chinese summary of files written and any unresolved issues.
"""


def build_single_paper_deep_read_codex_prompt(paper_key: str) -> str:
    return f"""Use $single-paper-deep-read.

You are being called by the local paper-reading website immediately after the
user approved a formal deep read.

Repository root: {REPO_ROOT}
paper_key: {paper_key}

Required behavior:
- Read AGENTS.md and the single-paper-deep-read skill files before acting.
- Verify `state/approvals/{paper_key}.json`.
- Produce a compact formal deep-read report. Do not attempt a broad literature
  search, do not use git, and do not inspect unrelated papers.
- Use existing quick-read outputs and source caches. Source caches are already
  available for this paper; read only the portions needed for evidence-grounded
  claims. If a detail is not available, state the limitation instead of doing
  open-ended exploration.
- Generate or update the canonical outputs:
  `outputs/papers/{paper_key}/deep_read.md`
  `outputs/papers/{paper_key}/deep_read.json`
- The JSON sidecar must satisfy
  `skills/single-paper-deep-read/references/output-schema.md`.
- After both canonical outputs exist, update repository state to
  `deep_read_done` only where allowed by AGENTS.md.
- Do not archive the paper and do not modify Zotero or original PDFs.
- End with a concise Chinese summary of files written and any unresolved issues.
"""


def filter_deep_interaction_rows(
    path: Path,
    paper_key: str,
    message_id: str | None = None,
) -> tuple[int, int]:
    rows = read_jsonl(path)
    if not rows and not path.exists():
        return 0, 0
    kept = []
    removed = 0
    for row in rows:
        same_paper = row.get("paper_key") == paper_key
        same_message = message_id is None or row.get("message_id") == message_id
        if same_paper and same_message:
            removed += 1
            continue
        kept.append(row)
    if removed:
        write_jsonl(path, kept)
    return removed, len(kept)


def delete_deep_interaction_records(paper_key: str, message_id: str | None = None) -> dict[str, Any]:
    paper_dir = PAPERS_DIR / paper_key
    paper_inbox = paper_dir / "interaction_inbox.jsonl"
    removed_global, kept_global = filter_deep_interaction_rows(DEEP_INTERACTION_MESSAGES_PATH, paper_key, message_id)
    removed_paper, kept_paper = filter_deep_interaction_rows(paper_inbox, paper_key, message_id)
    return {
        "removed": removed_global + removed_paper,
        "global": {"removed": removed_global, "kept": kept_global, "path": rel(DEEP_INTERACTION_MESSAGES_PATH)},
        "paper": {"removed": removed_paper, "kept": kept_paper, "path": rel(paper_inbox)},
    }


def try_delete_deep_interaction_records(paper_key: str, message_id: str | None = None) -> dict[str, Any]:
    try:
        return {**delete_deep_interaction_records(paper_key, message_id), "ok": True}
    except OSError as exc:
        return {"ok": False, "removed": 0, "error": str(exc)}


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


def remove_from_reading_queue(paper_key: str) -> dict[str, Any]:
    queue = load_queue()
    papers = queue.get("papers", [])
    if not isinstance(papers, list):
        return {"removed": 0, "before": 0, "after": 0, "path": rel(QUEUE_PATH)}

    kept = [paper for paper in papers if not (isinstance(paper, dict) and paper.get("paper_key") == paper_key)]
    removed = len(papers) - len(kept)
    if removed:
        queue["papers"] = kept
        queue["paper_count"] = len(kept)
        queue["updated_at"] = utc_now()
        save_queue(queue)
    return {"removed": removed, "before": len(papers), "after": len(kept), "path": rel(QUEUE_PATH)}


def remove_from_workflow_state(paper_key: str) -> dict[str, Any]:
    workflow = load_workflow_state()
    papers = workflow.get("papers", {})
    if not isinstance(papers, dict):
        return {"removed": False, "path": rel(WORKFLOW_STATE_PATH)}
    removed = papers.pop(paper_key, None) is not None
    if removed:
        workflow["updated_at"] = utc_now()
        write_json(WORKFLOW_STATE_PATH, workflow)
    return {"removed": removed, "path": rel(WORKFLOW_STATE_PATH)}


def remove_file_if_exists(path: Path) -> dict[str, Any]:
    require_inside_repo(path)
    if path.exists() and path.is_file():
        path.unlink()
        return {"removed": True, "path": rel(path)}
    return {"removed": False, "path": rel(path)}


def remove_dir_if_exists(path: Path) -> dict[str, Any]:
    require_inside_repo(path)
    if path.exists() and path.is_dir():
        shutil.rmtree(path)
        return {"removed": True, "path": rel(path)}
    return {"removed": False, "path": rel(path)}


def remove_quick_source_cache(paper_key: str) -> dict[str, Any]:
    cache_dir = STATE_DIR / "cache" / "quick_read_sources"
    require_inside_repo(cache_dir)
    removed = []
    if cache_dir.exists():
        for path in cache_dir.glob(f"{paper_key}.*"):
            if path.is_file():
                path.unlink()
                removed.append(rel(path))
    return {"removed": removed, "path": rel(cache_dir)}


def delete_local_paper_record(paper_key: str) -> dict[str, Any]:
    """Delete repository-local paper artifacts without excluding future Zotero todo refreshes."""
    result = {
        "paper_key": paper_key,
        "reading_queue": remove_from_reading_queue(paper_key),
        "workflow_state": remove_from_workflow_state(paper_key),
        "approval": remove_file_if_exists(APPROVALS_DIR / f"{paper_key}.json"),
        "paper_outputs": remove_dir_if_exists(PAPERS_DIR / paper_key),
        "quick_read_source_cache": remove_quick_source_cache(paper_key),
        "deep_read_source_cache": remove_dir_if_exists(STATE_DIR / "cache" / "deep_read_sources" / paper_key),
        "deep_read_interactions": try_delete_deep_interaction_records(paper_key),
        "zotero": {
            "modified": False,
            "note": "Zotero metadata, todo tags, database, storage, and original PDFs are not modified.",
        },
        "processed_state": {
            "modified": False,
            "path": rel(configured_path("state", "processed_papers", "state/processed_papers.json")),
            "note": "The paper key is not written to processed/archived/excluded sets, so a remaining Zotero todo can re-enter the daily queue.",
        },
    }
    event_error = try_append_jsonl(
        EVENT_LOG_PATH,
        {
            "event_type": "paper_deleted_from_site",
            "created_at": utc_now(),
            "paper_key": paper_key,
            "reading_queue_removed": result["reading_queue"]["removed"],
            "workflow_state_removed": result["workflow_state"]["removed"],
            "paper_outputs_removed": result["paper_outputs"]["removed"],
            "approval_removed": result["approval"]["removed"],
            "quick_read_source_cache_removed": len(result["quick_read_source_cache"]["removed"]),
            "deep_read_source_cache_removed": result["deep_read_source_cache"]["removed"],
            "deep_read_interactions_removed": result["deep_read_interactions"]["removed"],
            "deep_read_interactions_ok": result["deep_read_interactions"].get("ok"),
            "zotero_modified": False,
            "processed_state_modified": False,
        },
    )
    if event_error:
        result["event_log_error"] = event_error
    return result


def append_daily_run_log(run_id: str, step: str, message: str, **payload: Any) -> dict[str, Any]:
    record = {
        "schema_version": "1.0",
        "run_id": run_id,
        "created_at": utc_now(),
        "step": step,
        "message": message,
        **payload,
    }
    append_jsonl(DAILY_RUN_LOG_PATH, record)
    return record


def write_daily_run_status(record: dict[str, Any]) -> dict[str, Any]:
    current = read_json(DAILY_RUN_STATUS_PATH, {})
    if not isinstance(current, dict) or current.get("run_id") != record.get("run_id"):
        current = {}
    status = {
        "schema_version": "1.0",
        **current,
        **record,
        "updated_at": utc_now(),
    }
    write_json(DAILY_RUN_STATUS_PATH, status)
    return status


def read_daily_run_status() -> dict[str, Any] | None:
    status = read_json(DAILY_RUN_STATUS_PATH, None)
    if not isinstance(status, dict):
        return None
    run_id = str(status.get("run_id") or "")
    logs = [
        row
        for row in read_jsonl(DAILY_RUN_LOG_PATH)
        if not run_id or row.get("run_id") == run_id
    ][-80:]
    status["logs"] = logs
    status["log_path"] = rel(DAILY_RUN_LOG_PATH)
    return status


def recent_daily_logs(limit: int = 120) -> list[dict[str, Any]]:
    return read_jsonl(DAILY_RUN_LOG_PATH)[-limit:]


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


def strongest_status(*values: str | None) -> str:
    valid = [value for value in values if value in STATE_RANK]
    if not valid:
        return "queued"
    return max(valid, key=lambda value: STATE_RANK[value])


def paper_from_key(key: str, queue_entry: dict[str, Any] | None, workflow_record: dict[str, Any] | None) -> dict[str, Any]:
    paper_dir = PAPERS_DIR / key
    quick_json = read_json(paper_dir / "quick_read.json", {})
    deep_json = read_json(paper_dir / "deep_read.json", {})
    quick_md = markdown_record(paper_dir / "quick_read.md")
    deep_md = markdown_record(paper_dir / "deep_read.md")
    approval = read_json(APPROVALS_DIR / f"{safe_key(key)}.json", None)
    pdf_path = find_pdf_path(key, queue_entry)
    interaction_by_id = {
        message.get("message_id") or f"global_{index}": message
        for index, message in enumerate(read_jsonl(DEEP_INTERACTION_MESSAGES_PATH))
        if message.get("paper_key") == key
    }
    for index, message in enumerate(read_jsonl(paper_dir / "interaction_inbox.jsonl")):
        interaction_by_id[message.get("message_id") or f"paper_{index}"] = message
    interaction_messages = sorted(interaction_by_id.values(), key=lambda message: message.get("created_at", ""))

    title = None
    for source in (deep_json, quick_json, queue_entry or {}):
        if isinstance(source, dict) and source.get("title"):
            title = source["title"]
            break

    status = strongest_status(
        (queue_entry or {}).get("status"),
        (workflow_record or {}).get("status"),
        infer_status(quick_md, deep_md, approval),
    )
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
        "interaction_messages": interaction_messages[-50:],
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


def daily_archive_record(day: str) -> dict[str, Any]:
    path = DAILY_DIR / day
    return {
        "date": day,
        "path": rel(path),
        "digest": markdown_record(path / "digest.md"),
        "deep_read_candidates": read_json(path / "deep_read_candidates.json", None),
        "quick_reads": read_json(path / "quick_reads.json", None),
        "mindmap": mindmap_record(path / "mindmap.json"),
    }


def sanitize_daily_candidates(day: str, papers: list[dict[str, Any]]) -> dict[str, Any] | None:
    path = DAILY_DIR / day / "deep_read_candidates.json"
    data = read_json(path, None)
    if not isinstance(data, dict):
        return None
    paper_by_key = {paper["paper_key"]: paper for paper in papers}
    cleaned = []
    for candidate in data.get("candidates", []):
        if not isinstance(candidate, dict):
            continue
        paper = paper_by_key.get(str(candidate.get("paper_key") or ""))
        if paper and (paper.get("approval") or paper.get("deep_read") or paper.get("status") in {"deep_read_approved", "deep_read_done", "archived"}):
            continue
        cleaned.append({**candidate, "rank": len(cleaned) + 1})
    if cleaned != data.get("candidates", []):
        data["candidates"] = cleaned
        data["schema_version"] = str(data.get("schema_version") or "1.0")
        data["date"] = data.get("date") or day
        write_json(path, data)
    return data


def theme_output_records(path: Path) -> list[dict[str, Any]]:
    """Return theme co-reading Markdown outputs in UI rendering order."""
    return [
        {
            "key": key,
            "label": label,
            "filename": filename,
            "public": public,
            "file": markdown_record(path / filename),
        }
        for key, label, filename, public in THEME_MARKDOWN_OUTPUTS
    ]


def list_themes() -> list[dict[str, Any]]:
    if not THEMES_DIR.exists():
        return []
    themes = []
    for path in sorted([p for p in THEMES_DIR.iterdir() if p.is_dir()], key=lambda p: p.name.lower()):
        outputs = theme_output_records(path)
        themes.append(
            {
                "theme_id": path.name,
                "theme_state": markdown_record(path / "theme_state.md"),
                "comparison_matrix": markdown_record(path / "comparison_matrix.md"),
                "synthesis_report": markdown_record(path / "synthesis_report.md"),
                "coreading_outputs": outputs,
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


def current_queue_source_label() -> str:
    queue = read_json(QUEUE_PATH, {})
    if not isinstance(queue, dict):
        return "local_site_trigger"
    source = queue.get("source")
    if isinstance(source, dict):
        source_type = source.get("type")
        tag = source.get("tag")
        if source_type and tag:
            return f"{source_type}:{tag}"
        if source_type:
            return str(source_type)
    return "local_site_trigger"


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
                "workflow_status": paper.get("status") or "queued",
                "recommended_action": paper.get("recommended_action") or "needs_quick_read",
                "one_sentence_summary": quick_json.get("one_sentence_summary") or "",
                "relation_to_user_research": quick_json.get("relation_to_user_research") or "",
                "evidence_source": quick_json.get("evidence_source") or "",
                "evidence_location": quick_json.get("evidence_location") or "",
                "uncertainty": quick_json.get("uncertainty") or "",
            }
        )
        candidate_eligible = (
            paper.get("recommended_action") == "deep_read_candidate"
            and not paper.get("approval")
            and not paper.get("deep_read")
            and paper.get("status") not in {"deep_read_approved", "deep_read_done", "archived"}
        )
        if candidate_eligible:
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

    quick_reads = {"schema_version": "1.0", "date": day, "queue_source": current_queue_source_label(), "papers": quick_papers}
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
        lines.append(f"- `{paper['paper_key']}` {paper['title']}：{paper['quick_read_status']} / {paper.get('workflow_status') or paper['recommended_action']}")
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
            "daily_run_status": rel(DAILY_RUN_STATUS_PATH),
            "daily_run_log": rel(DAILY_RUN_LOG_PATH),
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
        "daily_run_status": read_daily_run_status(),
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
        if parsed.path == "/api/daily/logs":
            query = parse_qs(parsed.query)
            limit_text = query.get("limit", ["120"])[0]
            try:
                limit = max(1, min(500, int(limit_text)))
            except ValueError:
                limit = 120
            self.send_json({"ok": True, "logs": recent_daily_logs(limit), "status": read_daily_run_status()})
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
            if parsed.path == "/api/papers/delete":
                self.delete_paper()
                return
            if parsed.path == "/api/coreading/messages":
                self.create_coreading_message()
                return
            if parsed.path == "/api/deep-read-interactions/messages":
                self.create_deep_read_interaction_message()
                return
            if parsed.path == "/api/deep-read-interactions/delete":
                self.delete_deep_read_interaction_message()
                return
            if parsed.path == "/api/deep-read-interactions/clear":
                self.clear_deep_read_interactions()
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

    def end_headers(self) -> None:
        self.send_header("Cache-Control", "no-store, max-age=0")
        self.send_header("Pragma", "no-cache")
        super().end_headers()

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
        codex_result = run_external_codex(build_single_paper_deep_read_codex_prompt(paper_key))
        deep_md = PAPERS_DIR / paper_key / "deep_read.md"
        deep_json = PAPERS_DIR / paper_key / "deep_read.json"
        deep_read_generated = deep_md.exists() and deep_json.exists()
        if deep_read_generated:
            state_record = set_workflow_state(paper_key, "deep_read_done", "deep-read generated after site approval", "single-paper-deep-read")
        append_event(
            "single_paper_deep_read_codex_completed",
            {
                "paper_key": paper_key,
                "reply_status": codex_result["status"],
                "deep_read_generated": deep_read_generated,
            },
        )
        self.send_json(
            {
                "ok": True,
                "approval": record,
                "workflow_state": state_record,
                "path": rel(path),
                "deep_read_generated": deep_read_generated,
                "deep_read": markdown_record(deep_md),
                "deep_read_json": read_json(deep_json, None),
                "codex_ok": codex_result["ok"],
                "codex_status": codex_result["status"],
                "codex_reply": codex_result["reply"],
                "codex_command": codex_result.get("command"),
                "codex_returncode": codex_result.get("returncode"),
            }
        )

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

    def delete_paper(self) -> None:
        payload = self.read_payload()
        paper_key = safe_key(str(payload.get("paper_key") or ""))
        if not paper_key:
            self.send_error(HTTPStatus.BAD_REQUEST, "Missing paper_key")
            return
        result = delete_local_paper_record(paper_key)
        self.send_json({"ok": True, **result})

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
            "intent": safe_key(str(payload.get("intent") or "open_question")),
            "source_view": safe_key(str(payload.get("source_view") or "coreading_chat")),
            "body": body,
        }
        theme_inbox = THEMES_DIR / theme_id / "message_inbox.jsonl"
        history = read_jsonl(theme_inbox) if theme_inbox.exists() else read_jsonl(COREADING_MESSAGES_PATH)
        codex_result = run_external_codex(build_coreading_codex_prompt(record, history))
        record.update(
            {
                "target": "theme-coreading",
                "assistant_sender": "external_codex",
                "assistant_reply": codex_result["reply"],
                "reply_markdown": codex_result["reply"],
                "reply_skill": "theme-coreading",
                "reply_status": codex_result["status"],
                "forward_status": codex_result["status"],
                "codex_ok": codex_result["ok"],
                "codex_command": codex_result.get("command"),
                "codex_returncode": codex_result.get("returncode"),
                "completed_at": utc_now(),
            }
        )
        append_jsonl(COREADING_MESSAGES_PATH, record)
        if (THEMES_DIR / theme_id).exists():
            append_jsonl(theme_inbox, record)
        append_event(
            "coreading_codex_reply_completed",
            {"message_id": record["message_id"], "theme_id": theme_id, "reply_status": record["reply_status"]},
        )
        self.send_json({"ok": True, "message": record})

    def create_deep_read_interaction_message(self) -> None:
        payload = self.read_payload()
        body = str(payload.get("body") or "").strip()
        paper_key = safe_key(str(payload.get("paper_key") or ""))
        if not paper_key or not body:
            self.send_error(HTTPStatus.BAD_REQUEST, "Missing paper_key or message body")
            return
        interaction_mode = safe_key(str(payload.get("interaction_mode") or "follow_up"))
        record = {
            "schema_version": "1.0",
            "message_id": f"dri_{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S%f')}",
            "created_at": utc_now(),
            "paper_key": paper_key,
            "sender": payload.get("sender") or "local_site",
            "target": payload.get("target") or "deep_read_interaction",
            "interaction_mode": interaction_mode,
            "source_view": safe_key(str(payload.get("source_view") or "deep_read_panel")),
            "body": body,
        }
        paper_dir = PAPERS_DIR / paper_key
        paper_inbox = paper_dir / "interaction_inbox.jsonl"
        history = read_jsonl(paper_inbox) if paper_inbox.exists() else [
            message for message in read_jsonl(DEEP_INTERACTION_MESSAGES_PATH) if message.get("paper_key") == paper_key
        ]
        codex_result = run_external_codex(build_deep_read_codex_prompt(record, history))
        parsed_reply = parse_deep_interaction_codex_reply(codex_result["reply"], interaction_mode)
        interaction_mode = parsed_reply["interaction_mode"]
        answer_markdown = parsed_reply["answer_markdown"]
        record.update(
            {
                "interaction_mode": interaction_mode,
                "target": "deep-read-interaction",
                "assistant_sender": "external_codex",
                "assistant_reply": answer_markdown,
                "reply_markdown": answer_markdown,
                "reply_skill": "deep-read-interaction",
                "reply_status": codex_result["status"],
                "forward_status": codex_result["status"],
                "codex_ok": codex_result["ok"],
                "codex_raw_reply": codex_result["reply"] if codex_result["reply"] != answer_markdown else "",
                "codex_command": codex_result.get("command"),
                "codex_returncode": codex_result.get("returncode"),
                "completed_at": utc_now(),
            }
        )
        persistence_errors: list[str] = []
        global_error = try_append_jsonl(DEEP_INTERACTION_MESSAGES_PATH, record)
        if global_error:
            persistence_errors.append(global_error)
        if paper_dir.exists():
            paper_error = try_append_jsonl(paper_inbox, record)
            if paper_error:
                persistence_errors.append(paper_error)
        record["persisted"] = not persistence_errors
        if persistence_errors:
            record["persistence_error"] = "; ".join(persistence_errors)
        try:
            append_event(
                "deep_read_interaction_codex_reply_completed",
                {
                    "message_id": record["message_id"],
                    "paper_key": paper_key,
                    "interaction_mode": interaction_mode,
                    "reply_status": record["reply_status"],
                    "persisted": record["persisted"],
                },
            )
        except OSError as exc:
            record["event_log_error"] = str(exc)
        self.send_json({"ok": True, "message": record})

    def delete_deep_read_interaction_message(self) -> None:
        payload = self.read_payload()
        paper_key = safe_key(str(payload.get("paper_key") or ""))
        message_id = str(payload.get("message_id") or "").strip()
        if not paper_key or not message_id:
            self.send_error(HTTPStatus.BAD_REQUEST, "Missing paper_key or message_id")
            return
        result = delete_deep_interaction_records(paper_key, message_id)
        append_event(
            "deep_read_interaction_deleted",
            {"paper_key": paper_key, "message_id": message_id, "removed": result["removed"]},
        )
        self.send_json({"ok": True, **result})

    def clear_deep_read_interactions(self) -> None:
        payload = self.read_payload()
        paper_key = safe_key(str(payload.get("paper_key") or ""))
        if not paper_key:
            self.send_error(HTTPStatus.BAD_REQUEST, "Missing paper_key")
            return
        result = delete_deep_interaction_records(paper_key)
        append_event("deep_read_interactions_cleared", {"paper_key": paper_key, "removed": result["removed"]})
        self.send_json({"ok": True, **result})

    def create_daily_archive(self) -> None:
        payload = self.read_payload()
        day = str(payload.get("date") or local_date())
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", day):
            self.send_error(HTTPStatus.BAD_REQUEST, "date must be YYYY-MM-DD")
            return
        run_id = f"daily_{day}_{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S%f')}"
        write_daily_run_status(
            {
                "run_id": run_id,
                "date": day,
                "status": "running",
                "step": "request_started",
                "message": "Daily workflow started from the local site.",
                "source": "local_site",
                "skill": "daily-paper-triage",
                "started_at": utc_now(),
            }
        )
        append_daily_run_log(run_id, "request_started", "Daily workflow started from the local site.", date=day)
        append_event("daily_archive_request_started", {"date": day, "source": "local_site"})
        refresh_queue = bool(payload.get("refresh_queue", REFRESH_QUEUE_DAILY_DEFAULT))
        queue_refresh = {
            "ok": None,
            "status": "not_requested",
            "message": "Queue refresh was not requested for this Daily run.",
            "queue_path": rel(QUEUE_PATH),
        }
        if refresh_queue:
            write_daily_run_status(
                {
                    "run_id": run_id,
                    "date": day,
                    "status": "running",
                    "step": "queue_refresh_started",
                    "message": "Refreshing state/reading_queue.json from the configured Zotero todo source.",
                }
            )
            append_daily_run_log(
                run_id,
                "queue_refresh_started",
                "Refreshing reading_queue.json from Zotero todo source.",
                queue_path=rel(QUEUE_PATH),
            )
            queue_refresh = refresh_reading_queue_from_zotero()
            write_daily_run_status(
                {
                    "run_id": run_id,
                    "date": day,
                    "status": "running" if queue_refresh["ok"] else "failed",
                    "step": "queue_refresh_completed",
                    "message": queue_refresh.get("message") or queue_refresh["status"],
                    "queue_refresh": queue_refresh,
                }
            )
            append_daily_run_log(
                run_id,
                "queue_refresh_completed",
                queue_refresh.get("message") or queue_refresh["status"],
                ok=queue_refresh["ok"],
                status=queue_refresh["status"],
                paper_count=queue_refresh.get("paper_count"),
                queue_path=queue_refresh.get("queue_path"),
            )
            append_event(
                "daily_queue_refresh_completed",
                {
                    "date": day,
                    "status": queue_refresh["status"],
                    "ok": queue_refresh["ok"],
                    "paper_count": queue_refresh.get("paper_count"),
                    "queue_path": queue_refresh.get("queue_path"),
                },
            )
            if not queue_refresh["ok"]:
                self.send_json(
                    {
                        "ok": False,
                        "error": queue_refresh["message"],
                        "queue_refresh": queue_refresh,
                        "daily_run_status": read_daily_run_status(),
                    },
                    HTTPStatus.FAILED_DEPENDENCY,
                )
                return
        run_codex = bool(payload.get("run_codex", RUN_CODEX_DAILY_DEFAULT))
        allow_fallback = bool(payload.get("allow_fallback", DAILY_FALLBACK_ON_CODEX_FAILURE_DEFAULT))
        if run_codex:
            write_daily_run_status(
                {
                    "run_id": run_id,
                    "date": day,
                    "status": "running",
                    "step": "codex_invocation_started",
                    "message": "Calling external Codex with $daily-paper-triage.",
                    "queue_refresh": queue_refresh,
                }
            )
            append_daily_run_log(
                run_id,
                "codex_invocation_started",
                "Calling external Codex with $daily-paper-triage.",
                skill="daily-paper-triage",
                queue_refresh_status=queue_refresh["status"],
            )
            append_event(
                "daily_codex_invocation_started",
                {"date": day, "skill": "daily-paper-triage", "queue_refresh_status": queue_refresh["status"]},
            )
            codex_result = run_external_codex(build_daily_triage_codex_prompt(day))
            required = [
                DAILY_DIR / day / "digest.md",
                DAILY_DIR / day / "quick_reads.json",
                DAILY_DIR / day / "deep_read_candidates.json",
            ]
            required_outputs_exist = all(path.exists() for path in required)
            missing_outputs = [rel(path) for path in required if not path.exists()]
            write_daily_run_status(
                {
                    "run_id": run_id,
                    "date": day,
                    "status": "running" if codex_result["ok"] and required_outputs_exist else "failed",
                    "step": "codex_invocation_completed",
                    "message": (
                        "External Codex completed and required outputs exist."
                        if codex_result["ok"] and required_outputs_exist
                        else "External Codex failed or did not produce all required outputs."
                    ),
                    "queue_refresh": queue_refresh,
                    "codex_ok": codex_result["ok"],
                    "codex_status": codex_result["status"],
                    "codex_reply": codex_result["reply"],
                    "codex_command": codex_result.get("command"),
                    "codex_returncode": codex_result.get("returncode"),
                    "required_outputs": [rel(path) for path in required],
                    "missing_outputs": missing_outputs,
                }
            )
            append_daily_run_log(
                run_id,
                "codex_invocation_completed",
                (
                    "External Codex completed and required outputs exist."
                    if codex_result["ok"] and required_outputs_exist
                    else "External Codex failed or did not produce all required outputs."
                ),
                ok=codex_result["ok"],
                status=codex_result["status"],
                returncode=codex_result.get("returncode"),
                required_outputs_exist=required_outputs_exist,
                missing_outputs=missing_outputs,
            )
            append_event(
                "daily_codex_invocation_completed",
                {
                    "date": day,
                    "skill": "daily-paper-triage",
                    "reply_status": codex_result["status"],
                    "ok": codex_result["ok"],
                    "required_outputs_exist": required_outputs_exist,
                },
            )
            if codex_result["ok"] and required_outputs_exist:
                sanitize_daily_candidates(day, list_papers())
                append_event(
                    "daily_archive_codex_generated",
                    {"date": day, "path": rel(DAILY_DIR / day), "reply_status": codex_result["status"]},
                )
                archive = daily_archive_record(day)
                archive["generated_by"] = "external_codex:daily-paper-triage"
                archive["fallback_generated"] = False
            else:
                if not allow_fallback:
                    write_daily_run_status(
                        {
                            "run_id": run_id,
                            "date": day,
                            "status": "failed",
                            "step": "required_outputs_missing",
                            "message": "Daily stopped because external Codex did not complete the required workflow.",
                            "completed_at": utc_now(),
                        }
                    )
                    append_daily_run_log(
                        run_id,
                        "required_outputs_missing",
                        "Daily stopped because external Codex did not complete the required workflow.",
                        missing_outputs=missing_outputs,
                    )
                    self.send_json(
                        {
                            "ok": False,
                            "error": "External Codex daily-paper-triage invocation failed or did not produce required outputs.",
                            "queue_refresh": queue_refresh,
                            "codex_ok": codex_result["ok"],
                            "codex_status": codex_result["status"],
                            "codex_reply": codex_result["reply"],
                            "codex_command": codex_result.get("command"),
                            "codex_returncode": codex_result.get("returncode"),
                            "required_outputs": [rel(path) for path in required],
                            "missing_outputs": missing_outputs,
                            "daily_run_status": read_daily_run_status(),
                        },
                        HTTPStatus.FAILED_DEPENDENCY,
                    )
                    return
                archive = write_daily_archive(day)
                append_event("daily_archive_local_completed", {"date": day, "path": archive.get("path")})
                archive["generated_by"] = "local_fallback_after_codex_failure"
                archive["fallback_generated"] = True
                append_daily_run_log(
                    run_id,
                    "local_fallback_completed",
                    "Local fallback archive was generated after Codex failure.",
                    path=archive.get("path"),
                )
            archive["codex_ok"] = codex_result["ok"]
            archive["codex_status"] = codex_result["status"]
            archive["codex_reply"] = codex_result["reply"]
            archive["codex_command"] = codex_result.get("command")
            archive["codex_returncode"] = codex_result.get("returncode")
        else:
            write_daily_run_status(
                {
                    "run_id": run_id,
                    "date": day,
                    "status": "running",
                    "step": "local_fallback_started",
                    "message": "Daily run_codex=false; generating local fallback archive.",
                    "queue_refresh": queue_refresh,
                }
            )
            append_daily_run_log(run_id, "local_fallback_started", "Daily run_codex=false; generating local fallback archive.")
            archive = write_daily_archive(day)
            append_event("daily_archive_local_completed", {"date": day, "path": archive.get("path")})
            archive["generated_by"] = "local_site_no_codex"
            archive["fallback_generated"] = True
            archive["codex_ok"] = None
            archive["codex_status"] = "not_requested"
            archive["codex_reply"] = "Daily run_codex=false；未调用外部 Codex。"
            archive["codex_command"] = None
            archive["codex_returncode"] = None
            append_daily_run_log(run_id, "local_fallback_completed", "Local fallback archive was generated.", path=archive.get("path"))
        archive["queue_refresh"] = queue_refresh
        write_daily_run_status(
            {
                "run_id": run_id,
                "date": day,
                "status": "completed",
                "step": "archive_ready",
                "message": "Daily outputs are ready and visible in the dashboard.",
                "archive_path": archive.get("path"),
                "generated_by": archive.get("generated_by"),
                "fallback_generated": archive.get("fallback_generated"),
                "queue_refresh": queue_refresh,
                "codex_ok": archive.get("codex_ok"),
                "codex_status": archive.get("codex_status"),
                "codex_reply": archive.get("codex_reply"),
                "codex_command": archive.get("codex_command"),
                "codex_returncode": archive.get("codex_returncode"),
                "completed_at": utc_now(),
            }
        )
        append_daily_run_log(
            run_id,
            "archive_ready",
            "Daily outputs are ready and visible in the dashboard.",
            path=archive.get("path"),
            generated_by=archive.get("generated_by"),
        )
        archive["daily_run_status"] = read_daily_run_status()
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
