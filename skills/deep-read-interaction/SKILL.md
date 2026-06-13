---
name: deep-read-interaction
description: Use this skill after a single-paper deep-read report exists, when the user wants to confirm understanding, clarify claims or evidence, ask follow-up questions, verify the report against original sources, develop research interpretations, maintain concise consensus notes, or correct verified factual errors in the deep-read report. Do not use it to create the initial deep-read report, daily triage, quick-read cards, or theme synthesis.
---

# Deep Read Interaction

Use this skill for post-report interaction after `outputs/papers/<paper_key>/deep_read.md` exists.

Follow `../../AGENTS.md`: original PDFs are read-only, factual claims need evidence locations when available, and report corrections must not invent unsupported content.

## Load Only What You Need

- Read `../../config/paths.toml` before resolving repository-local paths.
- Read `references/interaction-modes.md` for confirmation, clarification, follow-up, and divergent-thinking procedures.
- Read `references/notes-and-corrections.md` before writing interaction notes or editing an existing deep-read report.
- Use original-source caches before treating the deep-read report as factual ground truth.

## Source Priority

For confirmation, clarification, and source-checking, inspect original sources first:

```text
state/cache/deep_read_sources/<paper_key>/pages.json
state/cache/deep_read_sources/<paper_key>/tables.md
state/cache/deep_read_sources/<paper_key>/figures.json
state/cache/deep_read_sources/<paper_key>/figures/
original PDF when available
state/external_verification/<paper_key>.json
```

Then compare with:

```text
outputs/papers/<paper_key>/deep_read.md
outputs/papers/<paper_key>/deep_read.json
outputs/papers/<paper_key>/quick_read.md
outputs/papers/<paper_key>/quick_read.json
```

For exploratory follow-up or research ideas, answer from the report first and state whether the answer is report-based or source-verified.

## Output Requirements

Produce one of:

- a source-checked confirmation or clarification;
- a report-based follow-up answer with source-check status stated;
- a clearly marked divergent research idea;
- an updated consensus note;
- a backed-up and corrected deep-read report for a verified factual error.

Default language is Chinese. Preserve English technical terms when useful.
