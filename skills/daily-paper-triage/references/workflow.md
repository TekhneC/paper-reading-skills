# Daily Triage Workflow

## Inputs

Use available files when present:

```text
state/reading_queue.json
state/library_index.jsonl
state/processed_papers.json
state/approvals/
config/paths.toml
config/scoring.toml
outputs/papers/*/quick_read.md
outputs/papers/*/quick_read.json
templates/daily_digest.md
```

Allowed queue sources:

1. existing `state/reading_queue.json`
2. Zotero tag or collection configured in `config/paths.toml`
3. user-provided paper keys
4. recently indexed unread papers from a derived index

For the default todo-tag workflow, use `../../scripts/build_reading_queue_from_zotero_todo.py`. Do not remove Zotero todo tags during triage; use `state/processed_papers.json` for completed, archived, or intentionally skipped papers.

## Queue Selection

If `state/reading_queue.json` is missing, identify a configured source before building. If no source is available, stop and report the missing configuration.

Use configured `queue.daily_limit`; fallback is 5 papers. Prioritize:

1. user-pinned papers
2. urgent papers
3. papers related to active research themes
4. recently added unread papers
5. papers without quick-read outputs

Do not remove unselected papers from the queue.

## Quick-Read Aggregation

Prefer `outputs/papers/<paper_key>/quick_read.json` for machine aggregation and use `quick_read.md` as the human-readable companion. If only Markdown exists, reuse it and mark machine-readable aggregation as unavailable.

Each triage entry must include:

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

Never archive automatically.

## Candidate Ranking

Apply eligibility gates before ranking. Do not recommend deep reading when required metadata is missing, PDF/text is unavailable, quick-read evidence is absent, the paper is outside scope, or the paper is redundant without a distinct angle.

Use `config/scoring.toml` when available. Otherwise rate qualitatively:

```text
research_fit
literature_review_value
task_formulation
method_mechanism
evaluation_metrics
baseline_comparison
ablation_logic
process_interaction_relevance
novel_framing
urgency
non_redundancy
evidence_confidence
```

Use `high`, `medium`, `low`, or `unknown`. Explain every `high` rating with evidence and why it matters for the user's current research.

Decision labels:

```text
strong_candidate
candidate
borderline
not_recommended
```

Recommend only a small number by default. Suggested focus should be specific enough for `$single-paper-deep-read`, using this taxonomy when possible:

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

Do not rank by venue, citation count, popularity, or recency except as weak tie-breakers.

## Digest Output

Use `../../templates/daily_digest.md` when available. Default run directory:

```text
outputs/daily/YYYY-MM-DD/
```

Recommended files:

```text
digest.md
reading_queue.snapshot.json
quick_reads.json
deep_read_candidates.json
quick_reads/<paper_key>.md
quick_reads/<paper_key>.json
```

If the run directory already exists, do not silently overwrite important files. Use a timestamped filename unless the user allows replacement.

The digest should answer:

1. 今天读了哪些论文？
2. 哪些只需要快读？
3. 哪些建议进入精读？
4. 推荐精读的理由是什么？
5. 哪些地方证据不足？
6. 需要用户确认什么？

End with an approval block for deep-reading candidates. Candidate status is not approval.

## Safe State Updates

Usually allowed to propose:

```text
queued -> quick_read_done
quick_read_done -> deep_read_candidate
```

Apply state changes only when the state file exists, the user request allows writing state, the transition is allowed by `AGENTS.md`, and no approval gate is bypassed.

Never perform:

```text
deep_read_candidate -> deep_read_approved
deep_read_approved -> deep_read_done
```

## Failure Handling

- Empty queue: `今日待读队列为空。`
- Missing derived Zotero index when needed: `Zotero 派生索引尚未建立，无法生成今日阅读队列。`
- Missing quick read: `该论文尚无快读结果，需要交给 single-paper-quick-read。`
- Incomplete metadata: `元数据不完整，需要检查 Zotero 记录。`
- Missing PDF: `PDF 缺失，无法完成快读或后续精读。`
- No useful deep-read candidate: state that directly and explain why.
