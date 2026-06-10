---
name: deep-read-interaction
description: Use this skill after a single-paper deep-read report exists, when the user wants to confirm understanding, clarify claims or evidence, ask follow-up questions, check the report against the original paper, or develop their own interpretation from the report. It maintains concise consensus notes, verifies confirmation and clarification against original sources first, answers exploratory questions from the report unless original-source checking is requested, and backs up then corrects the deep-read report when a factual error is found.
---

# Deep Read Interaction Skill

## Purpose

This skill supports interactive reading after a formal deep-read report has been generated.

It helps the user:

1. confirm whether their understanding is accurate
2. clarify terms, claims, methods, evidence, figures, tables, and limitations
3. ask follow-up questions from the deep-read report
4. develop divergent research thoughts from the report
5. inspect the original paper when needed
6. maintain concise notes of consensus reached during interaction
7. correct factual errors in the original deep-read report when verified

This skill is not a replacement for `single-paper-deep-read`. It is a post-report interaction layer.

---

## Source priority

Use different source priority by task type.

For confirmation and clarification tasks, first check the original sources:

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

For follow-up questions and divergent thinking, answer from the deep-read report first:

```text
outputs/papers/<paper_key>/deep_read.md
outputs/papers/<paper_key>/deep_read.json
```

If the user says "从原文检查", "核对原文", "回到 PDF", "check the paper", "verify from source", or otherwise asks for source checking, re-check the original sources before answering.

Do not treat the deep-read report as the source of truth for factual claims.

---

## Interaction modes

### 1. Confirmation

Use when the user asks whether an interpretation is correct.

Procedure:

1. restate the user's understanding briefly
2. check original source evidence first
3. answer with one of:

```text
基本正确
部分正确，需要修正
证据不足，不能确认
与原文不符
```

4. cite source locations when available
5. if useful, provide a corrected formulation

### 2. Clarification

Use when the user asks what a term, claim, figure, table, method, metric, or limitation means.

Procedure:

1. check original source evidence first
2. distinguish:

```text
作者明确说了什么
可以从文本推出什么
deep-read 报告如何解释
仍不确定什么
```

3. cite page, figure, table, or extracted-source location when available

### 3. Follow-up Question

Use when the user asks a question that extends the existing deep-read report.

Procedure:

1. answer from the deep-read report first
2. flag whether the answer is report-based or source-verified
3. re-check original sources if the answer depends on factual precision
4. suggest a tighter question if the user's question is too broad

### 4. Divergent Thinking

Use when the user wants research ideas, design implications, comparisons, or hypotheses inspired by the report.

Procedure:

1. start from the deep-read report
2. separate paper-grounded points from user-side extrapolation
3. mark speculative ideas clearly
4. prefer concrete outputs:

```text
research question
comparison dimension
experiment idea
evaluation criterion
system-design implication
literature-review angle
```

Do not present speculation as a paper claim.

---

## Consensus notes

Maintain a notes file for each interacted paper:

```text
outputs/papers/<paper_key>/interaction_notes.md
outputs/papers/<paper_key>/interaction_notes.json
```

Daily-run copies may also be written when useful:

```text
outputs/daily/YYYY-MM-DD/deep_read_interactions/<paper_key>.md
outputs/daily/YYYY-MM-DD/deep_read_interactions/<paper_key>.json
```

Only record consensus reached during interaction.

Do not log every user question, every assistant answer, or unconfirmed speculation.

Recommended Markdown structure:

```markdown
# Deep Read Interaction Notes - <Paper Title>

## Confirmed Understanding

## Clarified Points

## Corrected Misunderstandings

## User Research Ideas Agreed As Useful

## Open Questions

## Source-checked Corrections
```

Recommended JSON fields:

```json
{
  "schema_version": 1,
  "paper_key": "",
  "title": "",
  "updated_at": "",
  "confirmed_understanding": [],
  "clarified_points": [],
  "corrected_misunderstandings": [],
  "agreed_research_ideas": [],
  "open_questions": [],
  "source_checked_corrections": []
}
```

Ask before writing notes unless the user explicitly asks to record, save, update, or maintain them.

---

## Correcting factual errors in the deep-read report

If interaction reveals a factual error in the original deep-read report, correct it only when all conditions are true:

1. the claim is factual, not merely interpretive
2. the original source or verified external source contradicts the report
3. the corrected wording is clear
4. the user request allows editing the report, or the user confirms the correction

Before editing, back up the original report:

```text
outputs/papers/<paper_key>/deep_read.backup_YYYY-MM-DD_HHMMSS.md
outputs/papers/<paper_key>/deep_read.backup_YYYY-MM-DD_HHMMSS.json
```

Then update:

```text
outputs/papers/<paper_key>/deep_read.md
outputs/papers/<paper_key>/deep_read.json
```

If daily-run copies exist, either update them as well or record that the canonical report was corrected and daily copy is stale.

Record the correction in:

```text
outputs/papers/<paper_key>/interaction_notes.md
outputs/papers/<paper_key>/interaction_notes.json
```

Correction record should include:

```text
original claim
corrected claim
source evidence
backup path
updated paths
```

Do not correct interpretive disagreements as factual errors. For interpretive disagreements, record the new consensus or open question in interaction notes.

---

## Output style

Default language: Chinese.

Preserve English technical terms when useful.

Keep answers concise unless the user asks for detailed reasoning.

For source-checked answers, include evidence locations when available:

```text
（文件名：xxx.pdf，第 x 页，Figure x）
（pages.json，第 x 页）
（tables.md，Table candidate x / Page x）
（figures.json，Figure x / Page x）
```

When evidence is missing or extraction is unreliable, say so directly.

---

## Completion criteria

This skill is complete when it provides one of:

1. a source-checked confirmation or clarification
2. a report-based follow-up answer with source-check status stated
3. a clearly marked divergent research idea
4. an updated consensus note
5. a backed-up and corrected deep-read report for a verified factual error
