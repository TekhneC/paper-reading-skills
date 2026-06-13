# Interaction Modes

## Confirmation

Use when the user asks whether an interpretation is correct.

Procedure:

1. restate the user's understanding briefly;
2. check original source evidence first;
3. answer with one of:

```text
基本正确
部分正确，需要修正
证据不足，不能确认
与原文不符
```

4. cite source locations when available;
5. provide a corrected formulation when useful.

## Clarification

Use when the user asks what a term, claim, figure, table, method, metric, or limitation means.

Procedure:

1. check original source evidence first;
2. distinguish:

```text
作者明确说了什么
可以从文本推出什么
deep-read 报告如何解释
仍不确定什么
```

3. cite page, figure, table, or extracted-source location when available.

## Follow-Up Question

Use when the user asks a question extending the existing deep-read report.

Procedure:

1. answer from the report first;
2. flag whether the answer is report-based or source-verified;
3. re-check original sources if factual precision matters;
4. suggest a tighter question if the user question is too broad.

## Divergent Thinking

Use when the user wants research ideas, design implications, comparisons, or hypotheses inspired by the report.

Procedure:

1. start from the deep-read report;
2. separate paper-grounded points from user-side extrapolation;
3. mark speculation clearly;
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

## Evidence Style

For source-checked answers, cite when available:

```text
（文件名：xxx.pdf，第 x 页，Figure x）
（pages.json，第 x 页）
（tables.md，Table candidate x / Page x）
（figures.json，Figure x / Page x）
```

When evidence is missing or extraction is unreliable, say so directly.
