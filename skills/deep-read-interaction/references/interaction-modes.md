# Interaction Modes

## Automatic Classification

Before answering, classify the user's latest input into one primary mode:

```text
confirmation
clarification
follow_up
divergent_thinking
```

When a caller passes `auto`, infer the mode from the user's wording and the
conversation context. When a caller passes one of the four modes explicitly,
treat it as a user override unless the latest question clearly belongs to a
different mode.

The classification is for workflow routing and history filtering. Do not expose
it in the chat answer unless the user asks why a message was classified that
way.

## Confirmation

Use when the user asks whether an interpretation is correct.

Procedure:

1. Restate the user's understanding briefly.
2. Check original source evidence first when the claim is factual.
3. Answer with one of:

```text
基本正确
部分正确，需要修正
证据不足，不能确认
与原文不符
```

4. Cite source locations when the user asks for evidence or when the answer
   depends on precise source support.
5. Provide a corrected formulation when useful.

## Clarification

Use when the user asks what a term, claim, figure, table, method, metric, or
limitation means.

Procedure:

1. Check original source evidence first when factual precision matters.
2. Distinguish, when useful:

```text
作者明确说了什么
可以从文本推出什么
deep-read 报告如何解释
仍不确定什么
```

3. Keep the answer direct. Do not paste long report excerpts.
4. Cite page, figure, table, or extracted-source location only when requested or
   necessary.

## Follow-Up Question

Use when the user asks a question extending the existing deep-read report.

Procedure:

1. Answer from the report first.
2. Answer the user's question directly before discussing evidence status.
3. Keep the default response concise and conversational.
4. Do not paste report excerpts or source-cache text into the answer.
5. Re-check original sources if factual precision matters.
6. Provide detailed source locations only when the user asks for evidence,
   verification, correction, or page/figure/table support.
7. Suggest a tighter question if the user question is too broad.

For ordinary follow-up questions, a brief note such as `这是基于当前 deep-read
报告的解释` is enough when evidence status matters. Do not include a metadata
block.

## Divergent Thinking

Use when the user wants research ideas, design implications, comparisons, or
hypotheses inspired by the report.

Procedure:

1. Start from the deep-read report.
2. Separate paper-grounded points from user-side extrapolation.
3. Mark speculation clearly.
4. Prefer concrete outputs:

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

Evidence is demand-driven in chat mode.

For direct conceptual follow-ups, do not include detailed citations unless the
user asks for them. When the user asks for evidence or verification, cite when
available:

```text
（文件名：xxx.pdf，第 x 页，Figure x）
（pages.json，第 x 页）
（tables.md，Table candidate x / Page x）
（figures.json，Figure x / Page x）
```

When evidence is missing or extraction is unreliable, say so directly.
