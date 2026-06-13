---
name: theme-coreading
description: Use this skill for interactive theme-based co-reading of multiple papers around a user-controlled theme and research question: restore or create theme state, label paper roles, build a comparison matrix, trace field lineage, recommend supplementary readings, record quick/deep read handoffs, and update a synthesis report for literature-review or research-design support. Do not use it for single-paper quick reads, single-paper deep reads, daily triage, or final publishable literature-review prose unless explicitly requested.
---

# Theme Co-reading

Use this skill to synthesize a paper set around the user's theme and research question. Co-reading is comparative and stateful; it is not a sequence of isolated paper summaries.

Follow `../../AGENTS.md`: Zotero is read-only, paper relations and claims require evidence when available, generated outputs stay inside `outputs/`, and uncertain lineage must not be presented as confirmed.

## Load Only What You Need

- Read `../../config/paths.toml` before resolving repository-local paths.
- Read `references/session-state.md` when creating, restoring, or updating a theme session.
- Read `references/comparison-and-handoffs.md` when labeling paper roles, choosing comparison dimensions, updating the matrix, or handing papers to quick/deep read.
- Read `references/lineage-and-synthesis.md` when tracing field lineage, recommending supplementary readings, or writing the synthesis report.
- Use templates under `../../templates/`: `theme_state.md`, `comparison_matrix.md`, and `theme_synthesis.md`.

## Core Procedure

1. Identify or restore `theme_id`, `core_theme`, `research_question`, paper set, writing goal, and existing theme outputs.
2. Respect the user's research question. If missing, propose exactly three provisional options and mark status provisional; do not write final synthesis until confirmed or explicitly approved as provisional.
3. Verify the paper set and label each paper's role relative to the research question.
4. Define comparison dimensions before writing synthesis.
5. Build or update `outputs/themes/<theme_id>/comparison_matrix.md`.
6. Trace field lineage and recommend supplementary readings with confidence labels.
7. Record quick-read and deep-read handoffs instead of duplicating those workflows.
8. Write or update `outputs/themes/<theme_id>/synthesis_report.md` only after theme, question, roles, dimensions, evidence status, and matrix are ready.
9. Update `outputs/themes/<theme_id>/theme_state.md` with consensus, decisions, open questions, and next actions.

## Persistent Outputs

Use only three persistent theme-level outputs by default:

```text
outputs/themes/<theme_id>/theme_state.md
outputs/themes/<theme_id>/comparison_matrix.md
outputs/themes/<theme_id>/synthesis_report.md
```

Do not create separate long-running logs, reading plans, gap reports, or writing notes unless the user explicitly asks. Put those details into the three files above.

## Output Requirements

Produce or update one of:

- `theme_state.md`;
- `comparison_matrix.md`;
- `synthesis_report.md`;
- a clear explanation of why co-reading cannot proceed.

Default language is Chinese. Preserve English paper titles, methods, datasets, benchmarks, metrics, task names, and English-ready synthesis material when useful.
