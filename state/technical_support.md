# Technical Support Plan

This document records workflow-support components for the paper-reading skills.

Scripts support the skills, but they do not replace model reading, evidence judgment, or analytical report writing.

## Responsibility Boundary

Markdown reports are produced by the relevant skill/model using the selected template.

Scripts may:

* prepare source bundles
* create or restore workflow files from templates
* validate JSON/Markdown outputs
* apply guarded state transitions
* write explicit approval records
* build lightweight indexes
* record external verification evidence

Scripts must not be treated as the sole producer of analytical reading prose.

## Existing Scripts

These scripts already exist and may be referenced from `config/paths.toml`.

### `scripts/build_reading_queue_from_zotero_todo.py`

Builds `state/reading_queue.json` from a read-only Zotero tag query.

### `scripts/extract_quick_read_source.py`

Builds quick-read source bundles from Zotero metadata, PDF attachments, and `pdftotext` extraction.

### `scripts/extract_deep_read_source.py`

Builds page-level and visual evidence bundles for formal deep reading.

Outputs:

```text
state/cache/deep_read_sources/<paper_key>/pages.json
state/cache/deep_read_sources/<paper_key>/tables.md
state/cache/deep_read_sources/<paper_key>/figures.json
state/cache/deep_read_sources/<paper_key>/figures/
state/cache/deep_read_sources/<paper_key>/source.json
```

Figure extraction policy:

* Detect figure captions from page-level layout text.
* Prefer captions mentioning model, framework, architecture, pipeline, workflow, process, scope, taxonomy, or overview.
* Render candidate pages as PNG when embedded figure extraction is insufficient.
* Use bounding-box text extraction to crop the key figure region when possible.
* Mark the best candidate as `key_figure_candidate` in `figures.json`.
* Prefer `repo_relative_crop_image_path` in Markdown when a report embeds a visual anchor.
* If extraction is unreliable, mark the figure as needing visual verification.

The original Zotero PDF must remain unchanged.

## Planned Consolidated Scripts

Do not add separate scripts for approval, validation, state update, daily indexing, and external-verification record writing unless the combined interface becomes too large. Prefer the two consolidated scripts below.

### `scripts/workflow_state.py`

Purpose: one guarded entry point for workflow state, approvals, validation, and lightweight indexes.

Recommended subcommands:

```text
validate
transition
approve-deep-read
build-daily-deep-read-index
record-external-verification
```

`validate` checks:

```text
required fields exist
paired Markdown/JSON files agree on paper_key
referenced files exist when required
status values are known
state transitions are allowed
approval exists before deep_read_done
external verification status is explicit
theme state, comparison matrix, and synthesis files exist when required
```

`transition` applies guarded state transitions:

```text
--paper-key <paper_key>
--from-status <status>
--to-status <status>
--source <skill-or-script-name>
--notes <text>
```

Allowed transitions are defined in `state/state_schema.md`. The command must reject unexpected transitions by default.

`approve-deep-read` creates:

```text
state/approvals/<paper_key>.json
```

It should not directly update `state/processed_papers.json`; use `transition` for that.

`build-daily-deep-read-index` creates:

```text
outputs/daily/YYYY-MM-DD/deep_reads.json
```

`record-external-verification` writes externally checked evidence to:

```text
state/external_verification/<paper_key>.json
```

Network-backed findings must include source URLs and confidence labels. If network access is unavailable, write an explicit `unverified` or `skipped` status.

### `scripts/theme_session.py`

Purpose: support `theme-coreading` without turning synthesis into a script-generated report.

Recommended subcommands:

```text
init
restore
collect-inputs
validate
```

`init` creates:

```text
outputs/themes/<theme_id>/theme_state.md
outputs/themes/<theme_id>/comparison_matrix.md
outputs/themes/<theme_id>/synthesis_report.md
```

from:

```text
templates/theme_state.md
templates/comparison_matrix.md
templates/theme_synthesis.md
```

`restore` reports existing theme files and their last modified times.

`collect-inputs` gathers available quick-read and deep-read outputs for a paper set, but does not synthesize claims.

`validate` checks:

```text
theme_id is present
research_question_status is known
comparison_matrix.md exists when synthesis_report.md references it
synthesis_report.md does not proceed from an unapproved provisional question
evidence status and confidence fields are explicit
```
