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

## Intent Classification

Classify each user input into exactly one primary interaction mode before
answering:

```text
confirmation
clarification
follow_up
divergent_thinking
```

Use `confirmation` when the user asks whether their understanding is correct.
Use `clarification` when the user asks what a term, claim, figure, method,
metric, or limitation means. Use `follow_up` when the user asks a question that
extends the existing report. Use `divergent_thinking` when the user asks for
research implications, comparisons, hypotheses, design ideas, or possible
future work.

If the website or user provides a manual classification, respect it unless the
latest question clearly contradicts that mode. If you override it, keep the
answer direct and do not explain the classification unless the user asks.

## Output Requirements

Default output is a chat answer, not a standalone Markdown document.

For ordinary questions, produce only the direct response to the user's latest
question. Do not include metadata blocks, repeated user questions, long report
excerpts, full context dumps, or generic saving advice. Keep the answer concise
and conversational while remaining evidence-grounded.

Only produce structured notes or correction records when the user explicitly asks
to record, save, update notes, or correct the report.

Produce one of:

- a direct confirmation or clarification answer;
- a direct report-based follow-up answer;
- a clearly marked but concise divergent research idea;
- an updated consensus note;
- a backed-up and corrected deep-read report for a verified factual error.

For follow-up questions, do not provide detailed evidence locations by default.
Provide citations only when the user asks for evidence, asks to verify a claim,
asks for correction, or the answer depends on a precise factual point.

Default language is Chinese. Preserve English technical terms when useful.
