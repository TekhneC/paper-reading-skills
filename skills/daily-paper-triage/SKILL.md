---
name: daily-paper-triage
description: Use this skill for daily paper-reading triage from a Zotero-derived queue or user-provided paper batch: build or inspect today's queue, aggregate quick-read cards, rank deep-reading candidates, produce a Chinese decision-oriented daily digest, and prepare an approval block. Do not use it to generate formal deep-reading reports, single-paper deep reads, theme synthesis, or Zotero indexing architecture work.
---

# Daily Paper Triage

Use this skill to answer: 今天哪些论文值得快读，哪些值得进入精读候选？

Follow repository-wide rules in `../../AGENTS.md`: Zotero is read-only, generated state stays under `state/`, human-readable outputs stay under `outputs/`, paper claims need evidence locations when available, and formal deep reading requires explicit approval.

## Load Only What You Need

- Read `../../config/paths.toml` before resolving repository-local paths, especially when the skill is invoked through a symlink.
- Read `references/workflow.md` for the daily triage procedure, queue rules, scoring criteria, output files, and failure handling.
- Read `references/schema.md` when producing `quick_reads.json`, `deep_read_candidates.json`, or state-update proposals.
- Use `../../templates/daily_digest.md` for the digest when available.
- Use `../../scripts/build_reading_queue_from_zotero_todo.py` only for the configured todo-tag queue workflow.

## Core Procedure

1. Resolve the repository root and configured paths from `config/paths.toml`.
2. Inspect or build `state/reading_queue.json` from an allowed source. Do not directly scan Zotero except through approved read-only scripts or derived indexes.
3. For each queued paper, check canonical quick-read outputs under `outputs/papers/<paper_key>/`.
4. Add papers missing quick-read evidence to a handoff list for `$single-paper-quick-read`.
5. Aggregate available quick-read evidence into concise triage entries.
6. Rank deep-reading candidates conservatively using configured scoring when present, otherwise qualitative evidence-based dimensions.
7. Write a digest under `outputs/daily/YYYY-MM-DD/`, avoiding silent overwrites.
8. End with an approval block. Do not start formal deep reading.
9. Propose state updates only when allowed by `AGENTS.md` and the user request.

## Output Requirements

Produce either:

- a daily digest with queue status, quick-read status, ranked deep-reading candidates, approval block, and proposed state updates; or
- a clear explanation of why the digest cannot be produced.

Default language is Chinese. Preserve English paper titles, method names, datasets, metrics, benchmarks, and important terms in parentheses.
