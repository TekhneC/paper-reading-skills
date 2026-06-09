#!/usr/bin/env python3
"""Build a quick-read source bundle for one paper.

The script reads derived queue metadata and, when available, read-only Zotero
attachment metadata. It does not extract or copy PDF contents.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import shutil
import sqlite3
import sys
import tempfile
import time
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG = REPO_ROOT / "config" / "paths.toml"


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


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build a quick-read source bundle for one paper key."
    )
    parser.add_argument("paper_key", help="Zotero paper key to read from queue state.")
    parser.add_argument(
        "--config",
        type=Path,
        default=DEFAULT_CONFIG,
        help="Path to config/paths.toml.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Optional JSON output path. Defaults to stdout.",
    )
    parser.add_argument(
        "--no-text",
        action="store_true",
        help="Skip PDF text extraction and only report attachment metadata.",
    )
    parser.add_argument(
        "--max-text-chars",
        type=int,
        help="Maximum characters to keep in the cached text file.",
    )
    parser.add_argument(
        "--text-mode",
        choices=("flow", "layout", "raw", "both"),
        help="pdftotext layout mode. Defaults to [pdf].text_mode or both.",
    )
    parser.add_argument(
        "--cleanup-cache",
        action="store_true",
        help="Delete quick-read source cache files older than the configured TTL.",
    )
    parser.add_argument(
        "--cache-ttl-days",
        type=int,
        help="Cache TTL in days for --cleanup-cache. Defaults to [pdf].cache_ttl_days or 7.",
    )
    return parser.parse_args()


def connect_temp_copy(db_path: Path) -> tuple[sqlite3.Connection | None, tempfile.TemporaryDirectory[str] | None]:
    if not db_path.exists() or not db_path.is_file():
        return None, None

    temp_dir = tempfile.TemporaryDirectory(prefix="zotero_quick_source_")
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
    papers = data.get("papers", [])
    if not isinstance(papers, list):
        return None
    for paper in papers:
        if isinstance(paper, dict) and paper.get("paper_key") == paper_key:
            return paper
    return None


def attachment_rows(connection: sqlite3.Connection, zotero_item_id: int) -> list[dict[str, Any]]:
    rows = connection.execute(
        """
        SELECT
            child.key,
            ia.path,
            ia.contentType
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


def find_pdftotext(configured_path: str | None) -> str | None:
    if configured_path:
        path = Path(configured_path).expanduser()
        if path.exists():
            return str(path)
    return shutil.which("pdftotext")


def extract_pdf_text(
    pdftotext_path: str,
    pdf_path: Path,
    cache_path: Path,
    max_chars: int,
    text_mode: str,
) -> dict[str, Any]:
    with tempfile.TemporaryDirectory(prefix="quick_read_pdf_text_") as temp_dir:
        raw_text_path = Path(temp_dir) / "paper.txt"
        command = [pdftotext_path, "-enc", "UTF-8"]
        if text_mode == "layout":
            command.append("-layout")
        elif text_mode == "raw":
            command.append("-raw")
        command.extend([str(pdf_path), str(raw_text_path)])
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=60,
        )
        if result.returncode != 0:
            return {
                "ok": False,
                "error": (result.stderr or result.stdout or "pdftotext failed").strip(),
            }
        text = raw_text_path.read_text(encoding="utf-8", errors="replace")

    clean_text = text[:max_chars]
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    cache_path.write_text(clean_text, encoding="utf-8")
    return {
        "ok": True,
        "cache_path": str(cache_path),
        "chars_written": len(clean_text),
        "truncated": len(text) > max_chars,
        "text_mode": text_mode,
    }


def cleanup_cache(cache_dir: Path, ttl_days: int) -> list[str]:
    if ttl_days < 1:
        raise SystemExit("--cache-ttl-days must be at least 1")
    if not cache_dir.exists():
        return []

    cutoff = time.time() - ttl_days * 24 * 60 * 60
    removed: list[str] = []
    for pattern in ("*.txt", "*.source.json"):
        candidates = list(cache_dir.rglob(pattern))
        for path in candidates:
            if not path.is_file():
                continue
            if path.stat().st_mtime < cutoff:
                path.unlink()
                removed.append(str(path))
    return removed


def build_bundle(
    config: dict[str, Any],
    paper_key: str,
    *,
    extract_text: bool,
    max_text_chars: int | None,
    text_mode: str | None,
) -> dict[str, Any]:
    repo_root = Path(config.get("repository", {}).get("root", REPO_ROOT)).expanduser()
    state_config = config.get("state", {})
    zotero_config = config.get("zotero", {})
    pdf_config = config.get("pdf", {})

    queue_path = resolve_repo_path(
        repo_root,
        state_config.get("reading_queue"),
        "state/reading_queue.json",
    )
    entry = load_queue_entry(queue_path, paper_key)

    bundle: dict[str, Any] = {
        "schema_version": 1,
        "paper_key": paper_key,
        "queue_entry": entry,
        "source_status": {
            "queue_entry_found": entry is not None,
            "zotero_attachments_checked": False,
            "pdf_available": False,
            "pdf_text_extracted": False,
        },
        "zotero_attachments": [],
        "pdf_sources": [],
        "text_source": None,
        "text_sources": {},
    }

    zotero_item_id = entry.get("zotero_item_id") if entry else None
    db_path = Path(zotero_config.get("db_path", "~/Zotero/zotero.sqlite")).expanduser()
    storage_dir = Path(zotero_config.get("storage_dir", "~/Zotero/storage")).expanduser()
    if isinstance(zotero_item_id, int):
        connection, temp_dir = connect_temp_copy(db_path)
        if connection is not None:
            try:
                bundle["zotero_attachments"] = attachment_rows(connection, zotero_item_id)
                bundle["source_status"]["zotero_attachments_checked"] = True
            finally:
                connection.close()
                if temp_dir is not None:
                    temp_dir.cleanup()

    pdf_sources: list[dict[str, Any]] = []
    for attachment in bundle["zotero_attachments"]:
        if not is_pdf_attachment(attachment):
            continue
        pdf_path = resolve_storage_path(storage_dir, attachment)
        pdf_source = {
            "attachment_key": attachment.get("key"),
            "zotero_path": attachment.get("path"),
            "content_type": attachment.get("contentType"),
            "resolved_path": str(pdf_path) if pdf_path else None,
            "exists": pdf_path.exists() if pdf_path else False,
        }
        pdf_sources.append(pdf_source)

    bundle["pdf_sources"] = pdf_sources
    bundle["source_status"]["pdf_available"] = any(src["exists"] for src in pdf_sources)

    should_extract = extract_text and bool(pdf_config.get("extract_text", True))
    max_chars = max_text_chars or int(pdf_config.get("max_text_chars", 60000))
    selected_text_mode = text_mode or pdf_config.get("text_mode") or "both"
    if selected_text_mode not in {"flow", "layout", "raw", "both"}:
        raise SystemExit(f"Unsupported pdf text_mode: {selected_text_mode}")
    cache_dir = resolve_repo_path(
        repo_root,
        state_config.get("quick_read_source_cache_dir"),
        "state/cache/quick_read_sources",
    )
    pdftotext_path = find_pdftotext(pdf_config.get("pdftotext_path"))
    first_existing_pdf = next(
        (Path(src["resolved_path"]) for src in pdf_sources if src["exists"] and src["resolved_path"]),
        None,
    )

    if should_extract and first_existing_pdf is not None:
        if pdftotext_path is None:
            bundle["text_source"] = {
                "status": "missing_pdftotext",
                "cache_path": None,
            }
        else:
            modes = ["flow", "layout"] if selected_text_mode == "both" else [selected_text_mode]
            for mode in modes:
                cache_suffix = "txt" if selected_text_mode != "both" else f"{mode}.txt"
                cache_path = cache_dir / f"{paper_key}.{cache_suffix}"
                extraction = extract_pdf_text(
                    pdftotext_path,
                    first_existing_pdf,
                    cache_path,
                    max_chars,
                    mode,
                )
                source = {
                    "status": "available" if extraction.get("ok") else "failed",
                    "tool": pdftotext_path,
                    "source_pdf": str(first_existing_pdf),
                    "purpose": "main reading order" if mode == "flow" else "tables, equations, visual layout",
                    **extraction,
                }
                bundle["text_sources"][mode] = source

            if selected_text_mode == "both":
                bundle["text_source"] = bundle["text_sources"].get("flow")
            else:
                bundle["text_source"] = bundle["text_sources"].get(selected_text_mode)

            bundle["source_status"]["pdf_text_extracted"] = any(
                source.get("status") == "available"
                for source in bundle["text_sources"].values()
            )

    return bundle


def main() -> int:
    args = parse_args()
    config = load_toml(args.config.expanduser())
    repo_root = Path(config.get("repository", {}).get("root", REPO_ROOT)).expanduser()
    state_config = config.get("state", {})
    pdf_config = config.get("pdf", {})
    cache_dir = resolve_repo_path(
        repo_root,
        state_config.get("quick_read_source_cache_dir"),
        "state/cache/quick_read_sources",
    )

    if args.cleanup_cache:
        ttl_days = args.cache_ttl_days or int(pdf_config.get("cache_ttl_days", 7))
        removed = cleanup_cache(cache_dir, ttl_days)
        print(json.dumps({"removed_count": len(removed), "removed": removed}, indent=2))
        return 0

    bundle = build_bundle(
        config,
        args.paper_key,
        extract_text=not args.no_text,
        max_text_chars=args.max_text_chars,
        text_mode=args.text_mode,
    )
    rendered = json.dumps(bundle, ensure_ascii=False, indent=2)

    if args.output:
        output_path = args.output.expanduser()
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(rendered + "\n", encoding="utf-8")
    else:
        print(rendered)
    return 0


if __name__ == "__main__":
    sys.exit(main())
