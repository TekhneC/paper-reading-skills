#!/usr/bin/env python3
"""Build a page/table/figure source bundle for deep reading.

The script reads derived queue metadata and read-only Zotero attachment metadata,
then writes derived cache files inside this repository. It never modifies Zotero
metadata, the Zotero database, or original PDF attachments.
"""

from __future__ import annotations

import argparse
import html
import json
import re
import shutil
import sqlite3
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG = REPO_ROOT / "config" / "paths.toml"


FIGURE_KEYWORDS = (
    "architecture",
    "framework",
    "pipeline",
    "workflow",
    "overview",
    "method",
    "model",
    "system",
    "process",
    "scope",
    "taxonomy",
    "classification",
    "structure",
    "design",
)


def load_toml(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        import tomllib
    except ModuleNotFoundError:
        return load_minimal_toml(path)
    with path.open("rb") as handle:
        return tomllib.load(handle)


def load_minimal_toml(path: Path) -> dict[str, Any]:
    data: dict[str, Any] = {}
    section: dict[str, Any] | None = None
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.split("#", 1)[0].strip()
        if not line:
            continue
        if line.startswith("[") and line.endswith("]"):
            section = data.setdefault(line[1:-1].strip(), {})
            continue
        if "=" not in line or section is None:
            continue
        key, value = [part.strip() for part in line.split("=", 1)]
        if value.startswith('"') and value.endswith('"'):
            section[key] = value[1:-1]
        elif value.lower() in {"true", "false"}:
            section[key] = value.lower() == "true"
        elif value.isdigit():
            section[key] = int(value)
        else:
            section[key] = value
    return data


def resolve_repo_path(repo_root: Path, value: str | None, fallback: str) -> Path:
    raw = value or fallback
    path = Path(raw).expanduser()
    if path.is_absolute():
        return path
    return repo_root / path


def sibling_tool(configured_tool: str | None, tool_name: str) -> str | None:
    if configured_tool:
        configured_path = Path(configured_tool).expanduser()
        candidate = configured_path.with_name(tool_name)
        if candidate.exists():
            return str(candidate)
    return shutil.which(tool_name)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build a deep-read source bundle for one paper key."
    )
    parser.add_argument("paper_key", help="Zotero paper key to read.")
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--include-pages", action="store_true", default=True)
    parser.add_argument("--include-tables", action="store_true", default=True)
    parser.add_argument("--include-figures", action="store_true", default=True)
    parser.add_argument(
        "--max-rendered-figure-pages",
        type=int,
        default=3,
        help="Maximum candidate figure pages to render as PNG.",
    )
    return parser.parse_args()


def connect_temp_copy(db_path: Path) -> tuple[sqlite3.Connection | None, tempfile.TemporaryDirectory[str] | None]:
    if not db_path.exists() or not db_path.is_file():
        return None, None
    temp_dir = tempfile.TemporaryDirectory(prefix="zotero_deep_source_")
    copied_db = Path(temp_dir.name) / "zotero.sqlite"
    shutil.copy2(db_path, copied_db)
    uri = copied_db.as_uri() + "?mode=ro&immutable=1"
    connection = sqlite3.connect(uri, uri=True)
    connection.row_factory = sqlite3.Row
    return connection, temp_dir


def load_queue_entry(queue_path: Path, paper_key: str) -> dict[str, Any] | None:
    if not queue_path.exists():
        return None
    data = json.loads(queue_path.read_text(encoding="utf-8"))
    for paper in data.get("papers", []):
        if isinstance(paper, dict) and paper.get("paper_key") == paper_key:
            return paper
    return None


def attachment_rows(connection: sqlite3.Connection, zotero_item_id: int) -> list[dict[str, Any]]:
    rows = connection.execute(
        """
        SELECT child.key, ia.path, ia.contentType
        FROM itemAttachments ia
        JOIN items child ON child.itemID = ia.itemID
        WHERE ia.parentItemID = ?
        ORDER BY child.itemID
        """,
        (zotero_item_id,),
    ).fetchall()
    return [dict(row) for row in rows]


def resolve_storage_path(storage_dir: Path, attachment: dict[str, Any]) -> Path | None:
    raw_path = attachment.get("path")
    attachment_key = attachment.get("key")
    if not isinstance(raw_path, str) or not raw_path:
        return None
    if raw_path.startswith("storage:"):
        if not isinstance(attachment_key, str) or not attachment_key:
            return None
        return storage_dir / attachment_key / raw_path.removeprefix("storage:")
    path = Path(raw_path).expanduser()
    if path.is_absolute():
        return path
    return None


def is_pdf_attachment(attachment: dict[str, Any]) -> bool:
    content_type = str(attachment.get("contentType") or "").lower()
    raw_path = str(attachment.get("path") or "").lower()
    return content_type == "application/pdf" or raw_path.endswith(".pdf")


def get_page_count(pdfinfo_path: str | None, pdf_path: Path) -> tuple[int | None, str | None]:
    if not pdfinfo_path:
        return None, "missing_pdfinfo"
    result = subprocess.run(
        [pdfinfo_path, str(pdf_path)],
        capture_output=True,
        text=True,
        timeout=30,
    )
    if result.returncode != 0:
        return None, (result.stderr or result.stdout or "pdfinfo failed").strip()
    match = re.search(r"^Pages:\s+(\d+)\s*$", result.stdout, re.MULTILINE)
    if not match:
        return None, "pdfinfo did not report page count"
    return int(match.group(1)), None


def extract_page_text(pdftotext_path: str, pdf_path: Path, page_number: int, layout: bool) -> str:
    with tempfile.TemporaryDirectory(prefix="deep_read_page_text_") as temp_dir:
        output = Path(temp_dir) / "page.txt"
        command = [
            pdftotext_path,
            "-enc",
            "UTF-8",
            "-f",
            str(page_number),
            "-l",
            str(page_number),
        ]
        if layout:
            command.append("-layout")
        command.extend([str(pdf_path), str(output)])
        result = subprocess.run(command, capture_output=True, text=True, timeout=60)
        if result.returncode != 0:
            return ""
        return output.read_text(encoding="utf-8", errors="replace")


def caption_candidates(pages: list[dict[str, Any]], prefix_pattern: str) -> list[dict[str, Any]]:
    candidates: list[dict[str, Any]] = []
    pattern = re.compile(prefix_pattern, re.IGNORECASE)
    for page in pages:
        text = page.get("layout_text") or page.get("text") or ""
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        for idx, line in enumerate(lines):
            if not pattern.search(line):
                continue
            caption_lines = [line]
            for follow in lines[idx + 1 : idx + 3]:
                if re.match(r"^(fig(?:ure)?|table)\s*\d+", follow, re.IGNORECASE):
                    break
                if len(" ".join(caption_lines)) > 360:
                    break
                caption_lines.append(follow)
            caption = " ".join(caption_lines)
            candidates.append(
                {
                    "page_number": page["page_number"],
                    "caption": caption,
                    "keyword_score": keyword_score(caption),
                }
            )
    return candidates


def keyword_score(text: str) -> int:
    lowered = text.lower()
    return sum(1 for keyword in FIGURE_KEYWORDS if keyword in lowered)


def render_page(pdftoppm_path: str | None, pdf_path: Path, page_number: int, output_dir: Path) -> str | None:
    if not pdftoppm_path:
        return None
    output_prefix = output_dir / f"page_{page_number:03d}"
    command = [
        pdftoppm_path,
        "-png",
        "-r",
        "160",
        "-f",
        str(page_number),
        "-singlefile",
        str(pdf_path),
        str(output_prefix),
    ]
    result = subprocess.run(command, capture_output=True, text=True, timeout=90)
    output_path = output_prefix.with_suffix(".png")
    if result.returncode != 0 or not output_path.exists():
        return None
    return str(output_path)


def bbox_layout_lines(pdftotext_path: str, pdf_path: Path, page_number: int) -> dict[str, Any] | None:
    with tempfile.TemporaryDirectory(prefix="deep_read_bbox_") as temp_dir:
        output = Path(temp_dir) / "bbox.html"
        command = [
            pdftotext_path,
            "-bbox-layout",
            "-f",
            str(page_number),
            "-l",
            str(page_number),
            "-enc",
            "UTF-8",
            str(pdf_path),
            str(output),
        ]
        result = subprocess.run(command, capture_output=True, text=True, timeout=60)
        if result.returncode != 0 or not output.exists():
            return None
        text = output.read_text(encoding="utf-8", errors="replace")

    page_match = re.search(r'<page width="([^"]+)" height="([^"]+)">', text)
    if not page_match:
        return None
    page_width = float(page_match.group(1))
    page_height = float(page_match.group(2))
    lines: list[dict[str, Any]] = []
    line_pattern = re.compile(
        r'<line xMin="([^"]+)" yMin="([^"]+)" xMax="([^"]+)" yMax="([^"]+)">(.*?)</line>',
        re.DOTALL,
    )
    word_pattern = re.compile(r"<word [^>]*>(.*?)</word>", re.DOTALL)
    for match in line_pattern.finditer(text):
        words = [html.unescape(re.sub(r"<.*?>", "", word)) for word in word_pattern.findall(match.group(5))]
        line_text = " ".join(word.strip() for word in words if word.strip())
        if not line_text:
            continue
        lines.append(
            {
                "x_min": float(match.group(1)),
                "y_min": float(match.group(2)),
                "x_max": float(match.group(3)),
                "y_max": float(match.group(4)),
                "text": line_text,
            }
        )
    return {"page_width": page_width, "page_height": page_height, "lines": lines}


def caption_number(caption: str) -> str | None:
    match = re.search(r"\bfig(?:ure)?\.?\s*(\d+)", caption, re.IGNORECASE)
    if not match:
        return None
    return match.group(1)


def infer_crop_bbox_points(pdftotext_path: str, pdf_path: Path, candidate: dict[str, Any]) -> dict[str, float] | None:
    page_number = int(candidate["page_number"])
    bbox = bbox_layout_lines(pdftotext_path, pdf_path, page_number)
    if not bbox:
        return None
    lines = bbox["lines"]
    fig_number = caption_number(str(candidate.get("caption") or ""))
    if not fig_number:
        return None

    caption_index = None
    caption_re = re.compile(rf"^fig(?:ure)?\.?\s+{re.escape(fig_number)}\b", re.IGNORECASE)
    for idx, line in enumerate(lines):
        if caption_re.search(line["text"]):
            caption_index = idx
            break
    if caption_index is None:
        return None

    caption_line = lines[caption_index]
    caption_y_min = caption_line["y_min"]
    caption_lines = [caption_line]
    last_y = caption_line["y_max"]
    for line in lines[caption_index + 1 :]:
        if line["y_min"] - last_y > 16:
            break
        if re.match(r"^(fig(?:ure)?|table)\.?\s+\d+", line["text"], re.IGNORECASE):
            break
        caption_lines.append(line)
        last_y = line["y_max"]
        if len(caption_lines) >= 5:
            break

    visual_lines = [line for line in lines if 24 <= line["y_min"] < caption_y_min - 3]
    if not visual_lines:
        visual_lines = [line for line in lines if line["y_min"] < caption_y_min - 3]
    included = visual_lines + caption_lines
    if not included:
        return None

    pad = 10.0
    x_min = max(0.0, min(line["x_min"] for line in included) - pad)
    y_min = max(0.0, min(line["y_min"] for line in included) - pad)
    x_max = min(float(bbox["page_width"]), max(line["x_max"] for line in included) + pad)
    y_max = min(float(bbox["page_height"]), max(line["y_max"] for line in included) + pad)
    if x_max <= x_min or y_max <= y_min:
        return None
    return {
        "x_min": x_min,
        "y_min": y_min,
        "x_max": x_max,
        "y_max": y_max,
        "page_width": float(bbox["page_width"]),
        "page_height": float(bbox["page_height"]),
    }


def render_crop(
    pdftoppm_path: str | None,
    pdf_path: Path,
    page_number: int,
    bbox_points: dict[str, float] | None,
    output_dir: Path,
    dpi: int = 160,
) -> str | None:
    if not pdftoppm_path or not bbox_points:
        return None
    scale = dpi / 72.0
    x = max(0, int(round(bbox_points["x_min"] * scale)))
    y = max(0, int(round(bbox_points["y_min"] * scale)))
    width = max(1, int(round((bbox_points["x_max"] - bbox_points["x_min"]) * scale)))
    height = max(1, int(round((bbox_points["y_max"] - bbox_points["y_min"]) * scale)))
    output_prefix = output_dir / f"page_{page_number:03d}_crop"
    command = [
        pdftoppm_path,
        "-png",
        "-r",
        str(dpi),
        "-f",
        str(page_number),
        "-singlefile",
        "-x",
        str(x),
        "-y",
        str(y),
        "-W",
        str(width),
        "-H",
        str(height),
        str(pdf_path),
        str(output_prefix),
    ]
    result = subprocess.run(command, capture_output=True, text=True, timeout=90)
    output_path = output_prefix.with_suffix(".png")
    if result.returncode != 0 or not output_path.exists():
        return None
    return str(output_path)


def repo_relative(path: str | None, repo_root: Path) -> str | None:
    if not path:
        return None
    try:
        return str(Path(path).resolve().relative_to(repo_root.resolve())).replace("\\", "/")
    except ValueError:
        return path


def write_tables_md(path: Path, table_candidates: list[dict[str, Any]]) -> None:
    lines = ["# Extracted Table Candidates", ""]
    if not table_candidates:
        lines.extend(["No table captions detected.", ""])
    for idx, item in enumerate(table_candidates, 1):
        lines.extend(
            [
                f"## Table candidate {idx} / Page {item['page_number']}",
                "",
                "Caption:",
                "",
                item["caption"],
                "",
                "Reliability:",
                "",
                "caption_detected; table body requires page-level or visual verification.",
                "",
            ]
        )
    path.write_text("\n".join(lines), encoding="utf-8")


def build_bundle(config: dict[str, Any], paper_key: str, args: argparse.Namespace) -> dict[str, Any]:
    repo_root = Path(config.get("repository", {}).get("root", REPO_ROOT)).expanduser()
    state_config = config.get("state", {})
    zotero_config = config.get("zotero", {})
    pdf_config = config.get("pdf", {})

    queue_path = resolve_repo_path(repo_root, state_config.get("reading_queue"), "state/reading_queue.json")
    cache_root = args.output_dir or resolve_repo_path(
        repo_root,
        state_config.get("deep_read_source_cache_dir"),
        "state/cache/deep_read_sources",
    )
    output_dir = cache_root / paper_key
    figures_dir = output_dir / "figures"
    output_dir.mkdir(parents=True, exist_ok=True)
    figures_dir.mkdir(parents=True, exist_ok=True)

    entry = load_queue_entry(queue_path, paper_key)
    db_path = Path(zotero_config.get("db_path", "~/Zotero/zotero.sqlite")).expanduser()
    storage_dir = Path(zotero_config.get("storage_dir", "~/Zotero/storage")).expanduser()

    attachments: list[dict[str, Any]] = []
    zotero_item_id = entry.get("zotero_item_id") if entry else None
    if isinstance(zotero_item_id, int):
        connection, temp_dir = connect_temp_copy(db_path)
        if connection is not None:
            try:
                attachments = attachment_rows(connection, zotero_item_id)
            finally:
                connection.close()
                if temp_dir is not None:
                    temp_dir.cleanup()

    pdf_sources = []
    for attachment in attachments:
        if not is_pdf_attachment(attachment):
            continue
        resolved = resolve_storage_path(storage_dir, attachment)
        pdf_sources.append(
            {
                "attachment_key": attachment.get("key"),
                "zotero_path": attachment.get("path"),
                "content_type": attachment.get("contentType"),
                "resolved_path": str(resolved) if resolved else None,
                "exists": resolved.exists() if resolved else False,
            }
        )
    pdf_path = next((Path(src["resolved_path"]) for src in pdf_sources if src["exists"] and src["resolved_path"]), None)

    pdftotext_path = sibling_tool(pdf_config.get("pdftotext_path"), "pdftotext.exe")
    pdfinfo_path = sibling_tool(pdf_config.get("pdftotext_path"), "pdfinfo.exe")
    pdftoppm_path = sibling_tool(pdf_config.get("pdftotext_path"), "pdftoppm.exe")
    pdfimages_path = sibling_tool(pdf_config.get("pdftotext_path"), "pdfimages.exe")

    bundle: dict[str, Any] = {
        "schema_version": 1,
        "paper_key": paper_key,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "queue_entry": entry,
        "pdf_sources": pdf_sources,
        "tool_status": {
            "pdftotext": pdftotext_path,
            "pdfinfo": pdfinfo_path,
            "pdftoppm": pdftoppm_path,
            "pdfimages": pdfimages_path,
        },
        "outputs": {
            "output_dir": str(output_dir),
            "pages_json": str(output_dir / "pages.json"),
            "tables_md": str(output_dir / "tables.md"),
            "figures_json": str(output_dir / "figures.json"),
            "figures_dir": str(figures_dir),
            "source_json": str(output_dir / "source.json"),
        },
        "source_status": {
            "queue_entry_found": entry is not None,
            "pdf_available": pdf_path is not None,
            "page_text_extracted": False,
            "table_candidates_detected": False,
            "figure_candidates_detected": False,
            "key_figure_rendered": False,
        },
    }

    if pdf_path is None:
        return bundle
    if pdftotext_path is None:
        bundle["source_status"]["error"] = "missing_pdftotext"
        return bundle

    page_count, page_count_error = get_page_count(pdfinfo_path, pdf_path)
    if page_count is None:
        page_count = 1
        bundle["source_status"]["page_count_error"] = page_count_error

    pages: list[dict[str, Any]] = []
    for page_number in range(1, page_count + 1):
        flow_text = extract_page_text(pdftotext_path, pdf_path, page_number, layout=False)
        layout_text = extract_page_text(pdftotext_path, pdf_path, page_number, layout=True)
        pages.append(
            {
                "page_number": page_number,
                "text": flow_text,
                "layout_text": layout_text,
                "extraction_method": "pdftotext flow + layout",
                "quality_flags": [],
            }
        )

    (output_dir / "pages.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "paper_key": paper_key,
                "pdf_path": str(pdf_path),
                "page_count": page_count,
                "pages": pages,
                "generated_at": bundle["generated_at"],
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    bundle["source_status"]["page_text_extracted"] = True

    table_candidates = caption_candidates(pages, r"^(table|tab\.)\s*\d+")
    write_tables_md(output_dir / "tables.md", table_candidates)
    bundle["source_status"]["table_candidates_detected"] = bool(table_candidates)

    figure_candidates = caption_candidates(pages, r"^(fig(?:ure)?\.?)\s*\d+")
    figure_candidates.sort(key=lambda item: (item["keyword_score"], -item["page_number"]), reverse=True)
    rendered = 0
    for candidate in figure_candidates:
        candidate["image_path"] = None
        candidate["repo_relative_image_path"] = None
        candidate["crop_image_path"] = None
        candidate["repo_relative_crop_image_path"] = None
        candidate["crop_bbox_points"] = None
        candidate["crop_status"] = "not_rendered"
        candidate["role_hint"] = "model/process/scope candidate" if candidate["keyword_score"] > 0 else "figure candidate"
        if rendered < args.max_rendered_figure_pages:
            image_path = render_page(pdftoppm_path, pdf_path, candidate["page_number"], figures_dir)
            if image_path:
                candidate["image_path"] = image_path
                candidate["repo_relative_image_path"] = repo_relative(image_path, repo_root)
                bbox_points = infer_crop_bbox_points(pdftotext_path, pdf_path, candidate)
                candidate["crop_bbox_points"] = bbox_points
                crop_path = render_crop(pdftoppm_path, pdf_path, candidate["page_number"], bbox_points, figures_dir)
                if crop_path:
                    candidate["crop_image_path"] = crop_path
                    candidate["repo_relative_crop_image_path"] = repo_relative(crop_path, repo_root)
                    candidate["crop_status"] = "cropped"
                else:
                    candidate["crop_status"] = "crop_failed"
                rendered += 1

    figures_payload = {
        "schema_version": 1,
        "paper_key": paper_key,
        "selection_policy": "Prefer captions mentioning model, framework, architecture, pipeline, workflow, process, scope, or taxonomy. Render candidate pages because vector diagrams may not be extractable as embedded images.",
        "figures": figure_candidates,
        "key_figure_candidate": figure_candidates[0] if figure_candidates else None,
        "generated_at": bundle["generated_at"],
    }
    (output_dir / "figures.json").write_text(
        json.dumps(figures_payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    bundle["source_status"]["figure_candidates_detected"] = bool(figure_candidates)
    bundle["source_status"]["key_figure_rendered"] = any(item.get("image_path") for item in figure_candidates)
    bundle["source_status"]["key_figure_cropped"] = any(item.get("crop_image_path") for item in figure_candidates)

    return bundle


def main() -> int:
    args = parse_args()
    config = load_toml(args.config)
    bundle = build_bundle(config, args.paper_key, args)
    source_path = Path(bundle["outputs"]["source_json"])
    source_path.parent.mkdir(parents=True, exist_ok=True)
    source_path.write_text(json.dumps(bundle, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(bundle, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
