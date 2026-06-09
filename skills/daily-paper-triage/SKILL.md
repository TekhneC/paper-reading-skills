---

name: daily-paper-triage
description: Use this skill for daily paper-reading triage, including 今日阅读, quick-read aggregation, deep-reading candidate ranking, and approval gating. It prepares a decision-oriented daily digest but must not generate formal deep-reading reports.
---

# Daily Paper Triage Skill

## Purpose

This skill manages the daily paper-reading triage workflow.

It answers one main question:

```text
今天哪些论文值得快读，哪些论文值得进入精读候选？
```

It is responsible for:

1. checking or building the daily reading queue
2. checking quick-read availability
3. aggregating quick-read results
4. ranking deep-reading candidates
5. preparing a user approval block
6. proposing safe state updates

It must not generate formal deep-reading reports.

Formal deep reading belongs to:

```text
skills/single-paper-deep-read/SKILL.md
```

---

## Global rules

Follow the repository-level rules in:

```text
AGENTS.md
```

In particular:

* Zotero data is read-only.
* Original Zotero PDFs must not be modified, moved, renamed, or deleted.
* Paper-specific claims require evidence locations when available.
* Deep-reading reports require explicit user approval.
* Workflow state must be stored under `state/`.
* Human-readable outputs must be stored under `outputs/`.

Do not duplicate or override global Zotero, Git, state, or safety rules from `AGENTS.md`.

---

## Language and terminology policy

Default output language is Chinese.

However, this workflow must preserve English academic usability because the user may later write:

* English paper drafts
* English final reports
* English oral presentations
* English literature-review sections

Therefore:

1. Keep original paper titles in English.
2. Keep method names, model names, dataset names, metric names, and benchmark names in English.
3. When a key term first appears in Chinese, include its English term in parentheses.

Example:

```text
过程生成（process generation）
中间状态查询（intermediate-state querying）
评估指标（evaluation metric）
消融实验（ablation study）
生态效度（ecological validity）
```

4. Do not over-translate established technical terms.
5. If a Chinese translation is tentative, keep the English term and mark the translation as provisional.
6. When producing a daily digest, include English-ready wording for recommended deep-reading focuses when useful.

Example:

```text
建议精读重点：任务定义与评估指标（task formulation and evaluation metrics）
```

---

## When to use this skill

Use this skill when the user asks to:

* perform daily paper reading
* build today’s reading queue
* process a to-read batch
* triage papers from Zotero
* aggregate quick-read results
* recommend deep-reading candidates
* prepare a daily reading digest
* decide which papers deserve formal deep reading

Typical requests:

```text
今天读哪些论文？
```

```text
从 Zotero 待读列表里做今日阅读。
```

```text
帮我快读今天的论文，并推荐精读候选。
```

```text
根据这批论文生成每日阅读摘要。
```

---

## When not to use this skill

Do not use this skill for:

* generating a formal deep-reading report
* deeply analyzing one approved paper
* building a full theme-reading synthesis
* comparing multiple papers around a specific research question
* writing a literature-review section
* writing or debugging Zotero indexing scripts
* designing the repository architecture

Use the corresponding skill instead:

```text
single-paper-quick-read   For one paper's quick-read card.
single-paper-deep-read    For one approved formal deep-reading report.
theme-coreading           For comparative multi-paper theme reading.
```

---

## Inputs

Use available workflow files when present:

```text
state/library_index.jsonl
state/reading_queue.json
state/processed_papers.json
state/approvals/
config/paths.toml
config/scoring.toml
scripts/build_reading_queue_from_zotero_todo.py
outputs/papers/*/quick_read.md
outputs/papers/*/quick_read.json
templates/daily_digest.md
```

Possible daily queue sources:

1. existing `state/reading_queue.json`
2. Zotero tag configured in `config/paths.toml`
3. Zotero collection configured in `config/paths.toml`
4. user-provided paper keys
5. recently indexed unread papers

This skill must not directly scan or parse the Zotero database. Queue building from Zotero tags, collections, or recent unread papers must use an existing derived index, such as `state/library_index.jsonl`, or an explicitly approved read-only indexing workflow.

For the default configured todo-tag workflow, use `scripts/build_reading_queue_from_zotero_todo.py` to derive `state/reading_queue.json` from the configured Zotero database.

Do not remove or rewrite Zotero todo tags during daily triage. To avoid repeated queue generation, record completed, archived, or intentionally skipped papers in `state/processed_papers.json`; queue-building scripts should exclude those paper keys.

If no queue source is available, report the missing queue source.

Do not invent paths, tags, collections, or paper identities.

---

## Outputs

This skill may produce or update:

```text
outputs/daily/YYYY-MM-DD_daily_digest.md
outputs/daily/YYYY-MM-DD/digest.md
outputs/daily/YYYY-MM-DD/quick_reads.json
outputs/daily/YYYY-MM-DD/deep_read_candidates.json
state/reading_queue.json
state/candidates/YYYY-MM-DD_deep_read_candidates.json
```

This skill may reference existing quick-read outputs:

```text
outputs/papers/<paper_key>/quick_read.md
outputs/papers/<paper_key>/quick_read.json
```

This skill must not produce:

```text
outputs/papers/<paper_key>/deep_read.md
```

---

## Workflow

### Step 1. Check required state

Check whether the following files exist:

```text
state/reading_queue.json
config/paths.toml
```

If `state/reading_queue.json` is missing, check whether a queue source is configured.

Require `state/library_index.jsonl` only when the selected queue source depends on the derived library index. The default configured todo-tag workflow may build `state/reading_queue.json` through `scripts/build_reading_queue_from_zotero_todo.py` without a full library index.

If no queue source can be identified, stop and report the missing configuration.

Do not guess the queue source.

---

### Step 2. Read or build today’s queue

Read today’s queue from `state/reading_queue.json` when available.

If the queue must be built from configuration, use the configured source.

If a daily paper limit is configured, follow it.

If no daily limit is configured, use this fallback:

```text
5 papers
```

Selection priority:

1. user-pinned papers
2. explicitly urgent papers
3. papers related to active research themes
4. recently added unread papers
5. papers without quick-read outputs

Do not remove unselected papers from the queue.

---

### Step 3. Check quick-read availability

For each paper in today’s queue, check whether a quick-read card exists:

```text
outputs/papers/<paper_key>/quick_read.md
outputs/papers/<paper_key>/quick_read.json
```

If `quick_read.json` exists, prefer it for daily aggregation and use `quick_read.md` as the human-readable companion.

If only `quick_read.md` exists, reuse it but mark machine-readable aggregation as unavailable.

If a quick-read card is missing, add the paper to a quick-read handoff list for:

```text
skills/single-paper-quick-read/SKILL.md
```

By default, include the quick-read handoff list in the daily digest under a "needs quick read" section. Write the handoff list to state only when the user request explicitly allows writing workflow state.

Do not assume this skill can fully replace the quick-read skill.

---

### Step 4. Aggregate quick-read results

For each queued paper, produce a short triage entry.

Each entry should include:

```text
paper_key
title
quick_read_status
one_sentence_summary
relation_to_user_research
recommended_action
reason
uncertainty
evidence_source
evidence_location
```

Allowed `recommended_action` values:

```text
deep_read_candidate
quick_read_only
defer
archive_candidate
needs_metadata_fix
needs_pdf_check
needs_quick_read
```

Do not mark a paper as archived automatically.

Use `archive_candidate` only as a recommendation.

Triage judgments must be grounded in existing quick-read cards, derived library metadata, or user-provided paper information. If evidence is unavailable or lacks reliable location information, state that limitation explicitly instead of making unsupported paper-specific claims.

---

### Step 5. Rank deep-reading candidates

Rank deep-reading candidates using explicit criteria.

Use `config/scoring.toml` when available.

Before ranking, apply eligibility gates. A paper should not be recommended as a deep-reading candidate when:

```text
required metadata is missing
the PDF or readable text is unavailable
no quick-read evidence exists unless the user explicitly asks to rank from metadata only
the paper is clearly outside the user's active research scope
the paper appears redundant with a stronger already-read paper unless it adds a distinct angle
```

If a paper fails an eligibility gate, use another recommended action such as `needs_metadata_fix`, `needs_pdf_check`, `needs_quick_read`, `quick_read_only`, or `defer`.

If no scoring configuration exists, use these default dimensions qualitatively:

```text
research fit
literature-review value
problem or task formulation value
method mechanism value
evaluation and metric value
baseline or comparison value
ablation value
process-level or interaction-level relevance
novel framing value
urgency
non-redundancy
evidence confidence
```

Rate each dimension qualitatively rather than computing a numeric total:

```text
high
medium
low
unknown
```

Use `unknown` when the available quick-read card, derived metadata, or user-provided context does not support a judgment.

Do not rank papers only by venue, citation count, popularity, or recency.

Use venue, citation count, popularity, or recency only as weak contextual signals. They may break ties but must not override weak research fit, missing evidence, or poor comparability.

Prefer papers that help answer at least one concrete research question for the user, such as:

```text
Does this paper clarify a task definition the user is actively shaping?
Does it offer an evaluation metric, baseline, dataset, or ablation logic worth reusing or challenging?
Does it expose a method mechanism that changes how related systems should be understood?
Does it provide evidence about process, interaction, or ecological validity?
Does it help organize a literature-review taxonomy or research arc?
Does it challenge the user's current framing in a useful way?
```

Use decision labels:

```text
strong_candidate   strong research fit, useful evidence, and clear deep-read focus
candidate          useful enough for deep reading, but with bounded uncertainty
borderline         potentially useful, but needs quick-read, metadata repair, or user confirmation
not_recommended    no current deep-read value or too little evidence
```

Apply decision rules conservatively:

```text
strong_candidate
  Requires high research fit, medium-or-better evidence confidence, and at least one high-value dimension such as task formulation, method mechanism, evaluation, process/interaction relevance, or literature-review value.

candidate
  Requires at least medium research fit, usable evidence, and a clear reason why deep reading would change the user's understanding, taxonomy, method design, or evaluation choices.

borderline
  Use when the paper may matter but evidence is incomplete, quick-read coverage is missing, metadata needs repair, or the relation to the user's current research requires confirmation.

not_recommended
  Use when research fit is low, evidence is too weak, the paper is redundant without a distinct angle, or it is only supported by venue, citation count, popularity, or recency.
```

Do not recommend a paper for deep reading unless the suggested focus is specific enough to guide the later deep-read workflow.

Recommend only a small number of deep-reading candidates by default. If many papers look useful, rank the top candidates and place the rest under `defer` or `quick_read_only` with a short reason.

For each recommended candidate, include:

```text
rank
paper_key
title
decision_label
recommendation_reason
suggested_deep_read_focus
risk_or_uncertainty
evidence_source
evidence_location
qualitative_ratings
high_rated_dimensions
```

The suggested deep-read focus should include English terminology when relevant.

For each high-rated dimension, include a short reason grounded in quick-read evidence, derived metadata, or user-provided context. Do not mark a dimension as `high` without explaining why it matters for the user's current research.

Use the following focus taxonomy when possible:

```text
task_formulation
method_mechanism
evaluation_metrics
baseline_design
ablation_logic
process_representation
interaction_design
ecological_validity
taxonomy_position
contrast_with_user_framing
```

Examples:

```text
任务定义与评估指标（task formulation and evaluation metrics）
模型机制与消融逻辑（model mechanism and ablation logic）
过程建模与中间状态表示（process modeling and intermediate-state representation）
用户研究设计与生态效度（user-study design and ecological validity）
```

---

### Step 6. Produce daily digest

Use the template if available:

```text
templates/daily_digest.md
```

Save daily outputs by default under a date-oriented run directory:

```text
outputs/daily/YYYY-MM-DD/
```

Recommended files:

```text
outputs/daily/YYYY-MM-DD/digest.md
outputs/daily/YYYY-MM-DD/reading_queue.snapshot.json
outputs/daily/YYYY-MM-DD/quick_reads.json
outputs/daily/YYYY-MM-DD/deep_read_candidates.json
outputs/daily/YYYY-MM-DD/quick_reads/<paper_key>.md
outputs/daily/YYYY-MM-DD/quick_reads/<paper_key>.json
```

Create `outputs/daily/YYYY-MM-DD/` if it does not exist.

Also keep canonical per-paper quick-read outputs under:

```text
outputs/papers/<paper_key>/quick_read.md
outputs/papers/<paper_key>/quick_read.json
```

Do not write the digest outside this repository unless the user explicitly requests it.

If the target daily run already exists, do not silently overwrite important files. Either update them only when the user explicitly allows replacement, or write timestamped files such as:

```text
outputs/daily/YYYY-MM-DD/digest_HHMM.md
```

If the template is missing, produce a concise digest with these sections:

```markdown
# Daily Paper Reading Digest - YYYY-MM-DD

## 1. 今日阅读概览

## 2. 今日论文分诊表

## 3. 单篇快读摘要

## 4. 推荐精读候选

## 5. 需要确认的事项

## 6. 建议状态更新
```

The digest should be decision-oriented.

It should answer:

1. 今天读了哪些论文？
2. 哪些论文只需快读？
3. 哪些论文建议进入精读？
4. 推荐精读的理由是什么？
5. 哪些地方证据不足？
6. 需要用户确认什么？

Avoid long paper-by-paper summaries.

---

### Step 7. Prepare approval block

At the end of the digest, prepare an approval block.

Use this structure:

```markdown
## 需要确认的精读候选

建议进入精读：

- [ ] <paper_key> — <title>
  - 推荐理由：
  - 建议精读重点：
  - 不确定点：

建议暂不精读：

- <paper_key> — <title>
  - 原因：
```

Do not proceed to formal deep reading.

Deep reading may begin only after the user confirms or edits the approval list.

---

### Step 8. Propose safe state updates

Propose state updates after triage.

Apply state updates only when:

1. the state file exists
2. the update follows allowed transitions in `AGENTS.md`
3. the user request allows writing state
4. no approval gate is being bypassed

Allowed daily-triage updates usually include:

```text
queued -> quick_read_done
quick_read_done -> deep_read_candidate
```

Mark `queued -> quick_read_done` only when a quick-read output already exists or has actually been generated and confirmed in the current workflow.

Do not perform:

```text
deep_read_candidate -> deep_read_approved
deep_read_approved -> deep_read_done
```

unless the required approval record or deep-reading output exists.

---

## Output style

Use Chinese by default.

Keep the digest concise and decision-oriented.

Use English terms in parentheses for important concepts.

Preserve original English titles and technical names.

Prioritize:

1. what should be read today
2. what deserves deep reading
3. why it matters
4. what is uncertain
5. what the user needs to confirm

Avoid:

* long generic summaries
* ungrounded claims
* exaggerated importance
* unsupported recommendations
* formal deep-reading analysis

---

## Failure handling

If the queue is empty, write:

```text
今日待读队列为空。
```

If the Zotero library index is missing, write:

```text
Zotero 派生索引尚未建立，无法生成今日阅读队列。
```

If a paper lacks a quick-read output, write:

```text
该论文尚无快读结果，需要交给 single-paper-quick-read。
```

If metadata is incomplete, write:

```text
元数据不完整，需要检查 Zotero 记录。
```

If the PDF is missing, write:

```text
PDF 缺失，无法完成快读或后续精读。
```

If no paper is worth deep reading, write that directly and explain why.

Do not force a deep-reading recommendation.

---

## Completion criteria

This skill is complete when it produces one of the following:

1. a daily digest with deep-reading candidates and an approval block
2. a clear explanation of why the digest cannot be produced

A complete daily digest should include:

1. queue status
2. quick-read status for each queued paper
3. ranked deep-reading candidates or a statement that none are recommended
4. approval block
5. proposed state updates

The final output must not start formal deep reading.
