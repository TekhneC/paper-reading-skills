# Single Paper Quick-Read Workflow

## Inputs

Use available files:

```text
config/paths.toml
state/library_index.jsonl
state/reading_queue.json
templates/quick_read.md
state/cache/quick_read_sources/<paper_key>.flow.txt
state/cache/quick_read_sources/<paper_key>.layout.txt
```

When handed off from daily triage, prefer the matching queue entry for initial metadata.

Use `../../scripts/extract_quick_read_source.py <paper_key>` to locate the read-only PDF and create derived text caches. Prefer default dual extraction:

```text
<paper_key>.source.json
<paper_key>.flow.txt
<paper_key>.layout.txt
```

Use `flow` for reading order and prose. Use `layout` to cross-check tables, metrics, baselines, ablations, equations, and layout-sensitive claims. Full table reconstruction and page-image inspection belong to deep reading.

## Identification and Evidence

Collect:

```text
paper_key
title
authors
year
venue
paper_type
pdf_path
source
```

Allowed `paper_type`:

```text
method paper
system paper
benchmark paper
dataset paper
survey paper
position paper
empirical study
theory paper
unknown
```

Set `paper_type: unknown` when uncertain.

Allowed `evidence_status`:

```text
metadata_only
abstract_only
full_text_available
pdf_available
pdf_text_cache_available
page_numbers_available
insufficient_evidence
```

Do not make detailed method, baseline, metric, or result claims from metadata alone.

## Reading Focus

Keep the card concise. This is triage, not a formal review.

Required analytical sections:

1. 研究问题 (research problem)
2. 核心贡献 (main contribution)
3. 方法概览 (method overview)
4. 评估线索 (evaluation signals)
5. 与当前研究的关系 (relation to current research)
6. 阅读价值与暂缓理由 (why read / why defer)
7. 理由矩阵 (reason matrix)
8. 分诊结论 (triage decision)
9. 建议精读重点 (suggested deep-read focus), when relevant
10. 证据与不确定点 (evidence and uncertainty)

Use concrete relation to the user's likely research contexts:

```text
digital painting process generation
human-AI co-creation
generative models
computer vision
HCI
evaluation of creative systems
process-level modeling
interactive systems
survey writing
```

Avoid vague praise. Explain what the paper contributes to task formulation, method mechanism, evaluation, baseline choice, ablation logic, process/interaction validity, or taxonomy.

## Triage Decision

Choose exactly one:

```text
deep_read_candidate
quick_read_only
defer
archive_candidate
needs_metadata_fix
needs_pdf_check
```

`archive_candidate` is only a recommendation. Never archive automatically.

If `deep_read_candidate`, include a suggested deep-read focus such as:

```text
task formulation and evaluation metrics
model mechanism and ablation logic
process modeling and intermediate-state representation
user-study design and ecological validity
taxonomy and omission boundary
```

## State Guidance

May propose:

```text
queued -> quick_read_done
quick_read_done -> deep_read_candidate
```

Apply only when the state file exists, the user request allows writing state, the transition is allowed by `AGENTS.md`, and no approval gate is bypassed.

## Failure Handling

- Cannot identify paper: request paper key, title, PDF path, or Zotero record.
- Incomplete metadata: mark `needs_metadata_fix`.
- Missing/inaccessible PDF: mark `needs_pdf_check`.
- Abstract only: produce low-confidence quick read only if the user accepts abstract-level evidence.
- Method/evaluation invisible: state that evidence is insufficient instead of guessing.
