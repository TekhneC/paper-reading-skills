# Technical Support Plan

This document records workflow-support components for the paper-reading skills.

The scripts below support the skills, but they do not replace model reading, evidence judgment, or analytical report writing.

## Deep-read responsibility boundary

Deep-read Markdown is produced by the `single-paper-deep-read` skill/model using the selected template.

Scripts may:

* prepare source bundles
* convert approved candidates into approval records
* validate JSON/Markdown outputs
* update state with guarded transitions
* build daily indexes
* record external verification evidence

Scripts must not be treated as the sole producer of formal deep-reading prose.

## Planned script contracts

### `scripts/approve_deep_read_candidate.py`

Purpose: convert a pending deep-read candidate into an explicit approval record.

Inputs:

```text
--paper-key <paper_key>
--candidate-file state/candidates/YYYY-MM-DD_deep_read_candidates.json
--approver <name>
--approval-reason <text>
--report-mode full_report | compact_report
--approved-focus <text>
```

Outputs:

```text
state/approvals/<paper_key>.json
```

Side effects:

* May update `state/processed_papers.json` from `deep_read_candidate` to `deep_read_approved`.
* Must not approve a paper absent from the candidate file unless the current user request explicitly approves that paper.

### `scripts/extract_deep_read_source.py`

Purpose: build page-level and visual evidence bundles for formal deep reading.

Inputs:

```text
<paper_key>
--config config/paths.toml
--include-pages
--include-tables
--include-figures
```

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
* Render candidate pages as PNG when embedded figure extraction is insufficient, because model/scope diagrams are often vector graphics.
* Use bounding-box text extraction to crop the key figure region when possible.
* Mark the best candidate as `key_figure_candidate` in `figures.json`.
* The deep-read report may embed this candidate in Section 1 as the visual anchor.
* Prefer `repo_relative_crop_image_path` in Markdown. Fall back to the rendered full page only when crop extraction fails.
* If extraction is unreliable, mark the figure as needing visual verification.

The original Zotero PDF must remain unchanged.

### `scripts/validate_workflow_outputs.py`

Purpose: validate outputs from all paper-reading skills.

Inputs:

```text
--target reading_queue | quick_read | daily_triage | approval | deep_read | daily_deep_reads | all
--paper-key <paper_key>
--date YYYY-MM-DD
--config config/paths.toml
```

Checks:

* required fields exist
* paired Markdown/JSON files agree on `paper_key`
* referenced source files exist when required
* status values are known
* state transitions are allowed
* approval exists before `deep_read_done`
* external verification status is explicit

### `scripts/update_paper_state.py`

Purpose: apply guarded workflow state transitions.

Inputs:

```text
--paper-key <paper_key>
--from-status <status>
--to-status <status>
--source <skill-or-script-name>
--notes <text>
```

Allowed transitions are defined in `state/state_schema.md`.

The script must reject unexpected transitions by default.

### `scripts/build_daily_deep_reads_index.py`

Purpose: build a date-oriented index of completed deep reads.

Inputs:

```text
--date YYYY-MM-DD
--config config/paths.toml
```

Output:

```text
outputs/daily/YYYY-MM-DD/deep_reads.json
```

### `scripts/verify_external_evidence.py`

Purpose: record network-based verification for publication status, adjacent surveys, author follow-up work, and related/citing works.

Inputs:

```text
--paper-key <paper_key>
--query-type preprint_status | adjacent_surveys | author_followup | related_work | citing_work
--config config/paths.toml
```

Output:

```text
state/external_verification/<paper_key>.json
```

Network-backed findings must include source URLs and confidence labels. If network access is unavailable, write an explicit `unverified` or `skipped` status.
