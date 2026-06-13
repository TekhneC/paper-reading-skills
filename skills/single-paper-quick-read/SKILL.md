---
name: single-paper-quick-read
description: Use this skill to quickly read one research paper for triage: identify metadata, extract concise evidence from PDF/text/abstract sources, summarize problem, contribution, method, evaluation signals, relation to the user's research, and produce Chinese quick-read Markdown plus JSON with a recommendation. Do not use it for formal deep-reading reports, multi-paper synthesis, daily queue ranking, or Zotero indexing scripts.
---

# Single Paper Quick Read

Use this skill to answer: 这篇论文是否值得进入精读？

Follow `../../AGENTS.md`: Zotero and original PDFs are read-only, paper-specific claims need evidence locations when available, unsupported details must be marked uncertain, and generated outputs stay inside this repository.

## Load Only What You Need

- Read `../../config/paths.toml` before resolving repository-local paths.
- Read `references/workflow.md` for identification, evidence handling, triage decisions, and state guidance.
- Read `references/output-schema.md` when writing `quick_read.md` or `quick_read.json`.
- Use `../../templates/quick_read.md` when available.
- Use `../../scripts/extract_quick_read_source.py <paper_key>` when a Zotero-backed PDF source must be resolved and cached.

## Core Procedure

1. Identify one paper by Zotero item key, PDF path, title, DOI/arXiv ID, user metadata, or `state/reading_queue.json`.
2. If the paper is ambiguous, stop and ask for a unique identifier.
3. Resolve metadata and PDF/readable text using configured paths and read-only scripts.
4. Determine evidence status before making claims.
5. Write a concise quick-read card: problem, contribution, method overview, evaluation signals, relation to current research, why read/defer, triage decision, evidence and uncertainty.
6. Write the JSON sidecar for `$daily-paper-triage` aggregation.
7. Avoid overwriting existing outputs unless the user allows replacement; otherwise write timestamped alternates.
8. Propose state updates only when allowed; never approve deep reading or archive papers automatically.

## Output Requirements

Produce either:

- `outputs/papers/<paper_key>/quick_read.md` and `quick_read.json`; or
- a clear explanation of why quick reading cannot proceed.

Default language is Chinese. Preserve English titles, method names, model names, datasets, metrics, benchmarks, and established technical terms.
