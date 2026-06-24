---
name: single-paper-deep-read
description: Use this skill for an approved formal deep reading of one research paper or survey paper: verify approval, classify paper_type and report_mode, select the correct template, read PDF/text evidence, perform metrics-first or scope-taxonomy-first analysis, check claim-evidence or scope-taxonomy alignment, and produce Chinese deep-read Markdown plus JSON. Do not use it for quick triage, daily queue ranking, post-report interaction, or multi-paper theme synthesis.
---

# Single Paper Deep Read

Use this skill only after a paper is approved for formal deep reading.

Follow `../../AGENTS.md`: Zotero and original PDFs are read-only, generated outputs stay in this repository, every paper-specific claim needs the strongest available evidence location, and missing evidence must be stated plainly.

## Approval Gate

Deep reading is allowed when at least one condition is true:

1. the user explicitly asks to deep-read this paper in the current request;
2. the paper appears in `state/approvals/`;
3. the paper state is `deep_read_approved`;
4. the user confirms a deep-reading candidate from daily triage.

If none is true, do not generate a deep-read report. Offer `$single-paper-quick-read` or ask for approval.

## Load Only What You Need

- Read `../../config/paths.toml` before resolving repository-local paths.
- Read `references/type-mode-policy.md` before selecting paper type, research subtype, report mode, and template.
- Read `references/evidence-and-reading.md` before extracting evidence, handling preprints, using figures/tables, or making alignment judgments.
- Read `references/output-schema.md` before writing Markdown/JSON outputs or proposing state updates.
- Use `../../scripts/extract_deep_read_source.py <paper_key>` when deep-read source caches are missing or stale.
- Use the selected template under `../../templates/`.

## Core Procedure

1. Verify approval and identify the paper.
2. Resolve metadata, quick-read sources, PDF path, source caches, and daily-run context.
3. Determine `paper_type`: `research_article`, `survey_article`, or `default_or_unknown`.
4. Determine `research_subtype` for research articles: `classic_paper`, `new_paper`, or `ordinary_research_article`.
5. Determine `report_mode`: `full_report` or `compact_report`.
6. Check preprint/publication status when relevant and possible.
7. Select the matching template.
8. Read evidence from original PDF or deep-read caches before writing final interpretation.
9. Write an analytical Chinese report with English terminology and evidence locations.
10. Write the JSON sidecar.
11. Propose `deep_read_approved -> deep_read_done` only after both Markdown and JSON are generated and state writing is allowed.

## Output Requirements

Produce either:

- `outputs/papers/<paper_key>/deep_read.md` plus `deep_read.json`, optionally mirrored under `outputs/daily/YYYY-MM-DD/deep_reads/`; or
- a clear explanation of why the formal deep read cannot be produced.

Do not produce theme synthesis, final literature-review prose, or post-report interaction notes from this skill.
