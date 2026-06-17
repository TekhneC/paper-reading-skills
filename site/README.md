# Paper Reading Local Site

This is a zero-install local web console for the paper-reading skill cluster.

## Run

```powershell
.\site\run_site.ps1
```

The launcher reads `[runtime].python_path` from `config/paths.toml` when available,
so the site uses the same Python runtime as the repository scripts.

Or run the server directly:

```powershell
& 'C:\Users\tekhnec\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' site\server.py --host 127.0.0.1 --port 8765
```

Then open:

```text
http://127.0.0.1:8765
```

## Current Features

- View a unified Today workspace that combines the latest daily archive with actionable todos.
- Jump from each todo directly to the paper, archive, or theme view that handles it.
- View papers from `state/reading_queue.json`, `state/workflow_state.json`, approval records, and `outputs/papers/<paper_key>/`.
- Trigger Daily from the global sidebar workflow area, not from an individual paper.
- Edit rendered quick-read and deep-read Markdown notes with an optional source mode and a collapsible original PDF reference.
- Approve a paper for formal deep reading by writing `state/approvals/<paper_key>.json` and syncing workflow state.
- Sync allowed paper states back into local `state/`, with approval and deep-read completion guards.
- View local source PDFs when a queue entry or source cache records a readable PDF path.
- View dated archives from `outputs/daily/YYYY-MM-DD/`.
- View theme co-reading state, comparison matrix, and synthesis reports from `outputs/themes/<theme_id>/`.
- Use a co-reading workspace that shows public coreading Markdown outputs beside a Codex-backed chat composer.
- Edit and save idea maps by adding, dragging, deleting, and directly editing nodes.
- Send deep-read and co-reading questions to external Codex skill calls, then persist the user/Codex turns in local JSONL logs.

## Structure

```text
site/
  server.py              Local API and static-file server
  static/index.html      App shell
  static/styles.css      Layout and visual system
  static/js/api.js       API calls
  static/js/state.js     Client-side state normalization
  static/js/markdown.js  Lightweight Markdown rendering
  static/js/mindmap.js   Editable idea-map rendering
  static/js/app.js       UI orchestration
```

The server intentionally uses only the Python standard library. It is designed
to stay close to the repository's derived workflow data rather than becoming a
separate database-backed application.

## Design Decisions

See `site/DESIGN_DECISIONS.md`.
