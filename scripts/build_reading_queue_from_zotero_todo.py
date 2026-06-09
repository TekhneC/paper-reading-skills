#!/usr/bin/env python3
"""Build state/reading_queue.json from a read-only Zotero tag query.

The script reads Zotero through a temporary database copy and writes only derived
workflow state inside this repository.
"""

from __future__ import annotations

import argparse
import json
import shutil
import sqlite3
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG = REPO_ROOT / "config" / "paths.toml"
DEFAULT_OUTPUT = REPO_ROOT / "state" / "reading_queue.json"


def load_toml(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}

    try:
        import tomllib  # Python 3.11+
    except ModuleNotFoundError:
        return load_minimal_toml(path)

    with path.open("rb") as handle:
        return tomllib.load(handle)


def load_minimal_toml(path: Path) -> dict[str, Any]:
    """Tiny TOML reader for this config shape on older Python versions."""
    data: dict[str, Any] = {}
    section: dict[str, Any] | None = None

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.split("#", 1)[0].strip()
        if not line:
            continue
        if line.startswith("[") and line.endswith("]"):
            section_name = line[1:-1].strip()
            section = data.setdefault(section_name, {})
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


def expand_path(value: str | None, fallback: Path) -> Path:
    if not value:
        return fallback.expanduser()
    return Path(value).expanduser()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build state/reading_queue.json from Zotero items tagged by the configured todo tag."
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=DEFAULT_CONFIG,
        help="Path to config/paths.toml. Defaults to config/paths.toml.",
    )
    parser.add_argument(
        "--db-path",
        type=Path,
        help="Override Zotero sqlite path. Prefer config/paths.toml for normal use.",
    )
    parser.add_argument(
        "--tag",
        help='Zotero tag name to query. Defaults to [queue].todo_tag or "todo".',
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help="Output queue JSON path. Defaults to state/reading_queue.json.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        help="Maximum papers to include. Defaults to [queue].daily_limit, if set.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite an existing reading_queue.json.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the derived queue without writing it.",
    )
    parser.add_argument(
        "--list-tags",
        action="store_true",
        help="List Zotero tags and item counts instead of building the queue.",
    )
    parser.add_argument(
        "--tag-filter",
        default="todo",
        help='Filter used with --list-tags. Defaults to "todo".',
    )
    parser.add_argument(
        "--abstract-policy",
        choices=("full", "truncate", "omit"),
        help=(
            "How to store Zotero abstracts in reading_queue.json. "
            "Defaults to [queue].abstract_policy or truncate."
        ),
    )
    parser.add_argument(
        "--abstract-max-chars",
        type=int,
        help=(
            "Maximum characters used when --abstract-policy=truncate. "
            "Defaults to [queue].abstract_max_chars or 600."
        ),
    )
    parser.add_argument(
        "--processed-state",
        type=Path,
        default=REPO_ROOT / "state" / "processed_papers.json",
        help="Derived state file containing paper keys to exclude from new queues.",
    )
    return parser.parse_args()


def require_inside_repo(path: Path) -> Path:
    resolved = path.expanduser().resolve()
    repo = REPO_ROOT.resolve()
    if resolved != repo and repo not in resolved.parents:
        raise SystemExit(f"Refusing to write outside this repository: {resolved}")
    return resolved


def connect_temp_copy(db_path: Path) -> tuple[sqlite3.Connection, tempfile.TemporaryDirectory[str]]:
    if not db_path.exists():
        raise SystemExit(f"Missing Zotero database: {db_path}")
    if not db_path.is_file():
        raise SystemExit(f"Configured Zotero database is not a file: {db_path}")

    temp_dir = tempfile.TemporaryDirectory(prefix="zotero_readonly_")
    copied_db = Path(temp_dir.name) / "zotero.sqlite"
    shutil.copy2(db_path, copied_db)

    uri = copied_db.as_uri() + "?mode=ro&immutable=1"
    connection = sqlite3.connect(uri, uri=True)
    connection.row_factory = sqlite3.Row
    return connection, temp_dir


def scalar_field(fields: dict[str, list[str]], *names: str) -> str | None:
    for name in names:
        values = fields.get(name)
        if values:
            return values[0]
    return None


def item_fields(connection: sqlite3.Connection, item_id: int) -> dict[str, list[str]]:
    rows = connection.execute(
        """
        SELECT f.fieldName, v.value
        FROM itemData d
        JOIN fields f ON f.fieldID = d.fieldID
        JOIN itemDataValues v ON v.valueID = d.valueID
        WHERE d.itemID = ?
        ORDER BY f.fieldName
        """,
        (item_id,),
    ).fetchall()

    fields: dict[str, list[str]] = {}
    for row in rows:
        fields.setdefault(row["fieldName"], []).append(row["value"])
    return fields


def item_creators(connection: sqlite3.Connection, item_id: int) -> list[dict[str, str | None]]:
    rows = connection.execute(
        """
        SELECT c.firstName, c.lastName, ct.creatorType
        FROM itemCreators ic
        JOIN creators c ON c.creatorID = ic.creatorID
        LEFT JOIN creatorTypes ct ON ct.creatorTypeID = ic.creatorTypeID
        WHERE ic.itemID = ?
        ORDER BY ic.orderIndex
        """,
        (item_id,),
    ).fetchall()

    creators: list[dict[str, str | None]] = []
    for row in rows:
        full_name = " ".join(
            part for part in [row["firstName"], row["lastName"]] if part
        ).strip()
        creators.append(
            {
                "name": full_name or row["lastName"] or row["firstName"],
                "creator_type": row["creatorType"],
            }
        )
    return creators


def item_tags(connection: sqlite3.Connection, item_id: int) -> list[str]:
    rows = connection.execute(
        """
        SELECT t.name
        FROM itemTags it
        JOIN tags t ON t.tagID = it.tagID
        WHERE it.itemID = ?
        ORDER BY t.name
        """,
        (item_id,),
    ).fetchall()
    return [row["name"] for row in rows]


def pdf_status(connection: sqlite3.Connection, item_id: int) -> str:
    rows = connection.execute(
        """
        SELECT ia.contentType, ia.path
        FROM itemAttachments ia
        JOIN items i ON i.itemID = ia.itemID
        WHERE ia.parentItemID = ?
        """,
        (item_id,),
    ).fetchall()

    for row in rows:
        content_type = (row["contentType"] or "").lower()
        path = (row["path"] or "").lower()
        if content_type == "application/pdf" or path.endswith(".pdf"):
            return "available"
    return "missing" if rows else "unknown"


def tagged_items(connection: sqlite3.Connection, tag_name: str) -> list[sqlite3.Row]:
    return connection.execute(
        """
        SELECT DISTINCT
            i.itemID,
            i.key,
            i.libraryID,
            i.dateAdded,
            i.dateModified,
            it.typeName
        FROM tags t
        JOIN itemTags item_tags ON item_tags.tagID = t.tagID
        JOIN items i ON i.itemID = item_tags.itemID
        JOIN itemTypes it ON it.itemTypeID = i.itemTypeID
        WHERE t.name = ?
          AND it.typeName NOT IN ('attachment', 'note')
        ORDER BY i.dateAdded DESC, i.itemID DESC
        """,
        (tag_name,),
    ).fetchall()


def matching_tags(connection: sqlite3.Connection, tag_filter: str) -> list[sqlite3.Row]:
    return connection.execute(
        """
        SELECT t.name, COUNT(DISTINCT it.itemID) AS item_count
        FROM tags t
        LEFT JOIN itemTags it ON it.tagID = t.tagID
        WHERE lower(t.name) LIKE lower(?)
        GROUP BY t.tagID, t.name
        ORDER BY item_count DESC, t.name
        """,
        (f"%{tag_filter}%",),
    ).fetchall()


def load_processed_keys(path: Path) -> set[str]:
    if not path.exists():
        return set()

    data = json.loads(path.read_text(encoding="utf-8"))
    keys: set[str] = set()

    if isinstance(data, list):
        for value in data:
            if isinstance(value, str):
                keys.add(value)
        return keys

    if not isinstance(data, dict):
        return keys

    for field in ("processed_paper_keys", "archived_paper_keys", "excluded_paper_keys"):
        values = data.get(field, [])
        if isinstance(values, list):
            keys.update(value for value in values if isinstance(value, str))

    papers = data.get("papers", [])
    if isinstance(papers, list):
        for paper in papers:
            if not isinstance(paper, dict):
                continue
            key = paper.get("paper_key")
            status = paper.get("status")
            if isinstance(key, str) and status in {
                "quick_read_done",
                "deep_read_candidate",
                "deep_read_approved",
                "deep_read_done",
                "archived",
            }:
                keys.add(key)

    return keys


def format_abstract(value: str | None, policy: str, max_chars: int) -> str | None:
    if not value or policy == "omit":
        return None
    clean = " ".join(value.split())
    if policy == "full" or len(clean) <= max_chars:
        return clean
    return clean[: max_chars - 1].rstrip() + "..."


def build_queue(
    connection: sqlite3.Connection,
    tag_name: str,
    limit: int | None,
    processed_keys: set[str],
    processed_state_path: Path,
    abstract_policy: str,
    abstract_max_chars: int,
) -> dict[str, Any]:
    rows = [row for row in tagged_items(connection, tag_name) if row["key"] not in processed_keys]
    if limit is not None:
        rows = rows[:limit]

    papers: list[dict[str, Any]] = []
    for row in rows:
        fields = item_fields(connection, row["itemID"])
        title = scalar_field(fields, "title")
        date = scalar_field(fields, "date")
        abstract_note = scalar_field(fields, "abstractNote")

        papers.append(
            {
                "paper_key": row["key"],
                "zotero_item_id": row["itemID"],
                "library_id": row["libraryID"],
                "title": title or "unknown",
                "item_type": row["typeName"],
                "authors": item_creators(connection, row["itemID"]),
                "publication_title": scalar_field(
                    fields, "publicationTitle", "conferenceName", "proceedingsTitle"
                ),
                "date": date,
                "year": date[:4] if date and len(date) >= 4 else None,
                "doi": scalar_field(fields, "DOI"),
                "url": scalar_field(fields, "url"),
                "abstract_note": format_abstract(
                    abstract_note, abstract_policy, abstract_max_chars
                ),
                "abstract_policy": abstract_policy,
                "abstract_available": abstract_note is not None,
                "tags": item_tags(connection, row["itemID"]),
                "date_added": row["dateAdded"],
                "date_modified": row["dateModified"],
                "status": "queued",
                "quick_read_status": "missing",
                "pdf_status": pdf_status(connection, row["itemID"]),
                "priority_signals": [f"zotero_tag:{tag_name}"],
                "notes": None,
            }
        )

    return {
        "schema_version": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source": {
            "type": "zotero_tag",
            "tag": tag_name,
            "read_method": "temporary_sqlite_copy",
            "processed_state": str(processed_state_path),
        },
        "daily_limit": limit,
        "excluded_processed_count": len(processed_keys),
        "paper_count": len(papers),
        "papers": papers,
    }


def main() -> int:
    args = parse_args()
    config = load_toml(args.config.expanduser())

    zotero_config = config.get("zotero", {})
    queue_config = config.get("queue", {})

    db_path = (
        args.db_path.expanduser()
        if args.db_path
        else expand_path(zotero_config.get("db_path"), Path("~/Zotero/zotero.sqlite"))
    )
    tag_name = args.tag or queue_config.get("todo_tag") or "todo"
    limit = args.limit if args.limit is not None else queue_config.get("daily_limit")
    abstract_policy = (
        args.abstract_policy or queue_config.get("abstract_policy") or "truncate"
    )
    abstract_max_chars = (
        args.abstract_max_chars or queue_config.get("abstract_max_chars") or 600
    )

    if limit is not None and limit < 1:
        raise SystemExit("--limit must be a positive integer")
    if abstract_max_chars < 20:
        raise SystemExit("--abstract-max-chars must be at least 20")

    output_path = require_inside_repo(args.output)
    if output_path.exists() and not args.force and not args.dry_run:
        raise SystemExit(
            f"Refusing to overwrite existing queue without --force: {output_path}"
        )

    connection, temp_dir = connect_temp_copy(db_path)
    try:
        if args.list_tags:
            tags = [
                {"tag": row["name"], "item_count": row["item_count"]}
                for row in matching_tags(connection, args.tag_filter)
            ]
            print(json.dumps(tags, ensure_ascii=False, indent=2))
            return 0

        processed_keys = load_processed_keys(args.processed_state.expanduser())
        queue = build_queue(
            connection,
            tag_name,
            limit,
            processed_keys,
            args.processed_state,
            abstract_policy,
            abstract_max_chars,
        )
    finally:
        connection.close()
        temp_dir.cleanup()

    rendered = json.dumps(queue, ensure_ascii=False, indent=2)
    if args.dry_run:
        print(rendered)
        return 0

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(rendered + "\n", encoding="utf-8")
    print(f"Wrote {queue['paper_count']} queued papers to {output_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
