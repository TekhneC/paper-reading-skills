---

name: single-paper-quick-read
description: Use this skill for a quick read of one research paper. It produces a concise Chinese quick-read card with English terminology, triage judgment, evidence status, and deep-reading recommendation. Do not use it for formal deep-reading reports or multi-paper synthesis.
---

# Single Paper Quick Read Skill

## Purpose

This skill performs a quick read of one research paper.

It answers one main question:

```text
这篇论文是否值得进入精读（deep reading）？
```

It is responsible for:

1. identifying the paper’s basic metadata
2. summarizing the paper’s problem and contribution
3. classifying the paper type
4. judging its relevance to the user’s research
5. identifying why it may or may not deserve deep reading
6. producing a concise quick-read card
7. recommending one triage action

It must not produce a formal deep-reading report.

Formal deep reading belongs to:

```text
skills/single-paper-deep-read/SKILL.md
```

Multi-paper synthesis belongs to:

```text
skills/theme-coreading/SKILL.md
```

Daily queue ranking belongs to:

```text
skills/daily-paper-triage/SKILL.md
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
* If evidence is insufficient, state that directly.
* Use Chinese by default.
* Preserve English technical terms when relevant.

Do not duplicate or override global Zotero, Git, state, or safety rules from `AGENTS.md`.

---

## Language and terminology policy

Default output language is Chinese.

However, this skill must preserve English academic usability because quick-read results may later support:

* English paper drafts
* English final reports
* English oral presentations
* English literature-review sections

Therefore:

1. Keep original paper titles in English.
2. Keep method names, model names, dataset names, metric names, benchmark names, and system names in English.
3. When a key term first appears in Chinese, include its English term in parentheses.

Examples:

```text
任务定义（task formulation）
过程生成（process generation）
中间状态（intermediate state）
评估指标（evaluation metric）
消融实验（ablation study）
用户研究（user study）
生态效度（ecological validity）
```

4. Do not over-translate established technical terms.
5. If the Chinese translation is uncertain, keep the English term and mark the translation as provisional.
6. The quick-read card should preserve English-ready phrasing for later reuse.

Example:

```text
建议精读重点：模型机制与消融逻辑（model mechanism and ablation logic）
```

---

## When to use this skill

Use this skill when the user asks to:

* quickly read one paper
* skim one paper for triage
* decide whether one paper deserves deep reading
* generate a quick-read card
* summarize one paper briefly before deeper analysis
* evaluate one paper’s relevance to the user’s project
* process a paper from the daily reading queue

Typical requests:

```text
帮我快速读一下这篇论文。
```

```text
这篇论文是否值得精读？
```

```text
先给我这篇论文的快读结果。
```

```text
为这篇论文生成 quick-read card。
```

---

## When not to use this skill

Do not use this skill for:

* formal deep reading
* full method reconstruction
* full experiment analysis
* full reviewer-style critique
* multi-paper comparison
* theme-reading synthesis
* writing a literature-review section
* ranking a batch of papers for daily reading
* debugging Zotero indexing scripts

Use the corresponding skill instead:

```text
single-paper-deep-read    For one approved formal deep-reading report.
theme-coreading           For comparative multi-paper theme reading.
daily-paper-triage        For daily queue triage and candidate ranking.
```

---

## Inputs

Resolve all repository-local paths through:

```text
config/paths.toml
```

When this skill is discovered through a symbolic link under `~/.agents/skills/`, do not assume the current working directory is the repository root. Treat `[repository].root` in `config/paths.toml` as the canonical repository root, and resolve relative state, output, template, script, and skill paths from that root.

Use available inputs when present:

```text
state/library_index.jsonl
state/reading_queue.json
outputs/papers/<paper_key>/quick_read.md
outputs/papers/<paper_key>/quick_read.json
config/paths.toml
templates/quick_read.md
scripts/extract_quick_read_source.py
state/cache/quick_read_sources/<paper_key>.flow.txt
state/cache/quick_read_sources/<paper_key>.layout.txt
```

A single paper may be identified by:

1. Zotero item key
2. PDF path
3. paper title
4. DOI or arXiv ID
5. user-provided metadata
6. entry from `state/reading_queue.json`

If the paper cannot be uniquely identified, report the ambiguity instead of guessing.

When a paper is handed off from `daily-paper-triage`, prefer the matching entry in `state/reading_queue.json` as the initial metadata source. Use its `paper_key`, title, authors, DOI, URL, tags, abstract availability, and PDF status before attempting any Zotero or PDF lookup.

Use `scripts/extract_quick_read_source.py <paper_key>` to resolve Zotero attachment metadata, locate the read-only PDF path, and create a derived text cache under `state/cache/quick_read_sources/` when PDF text extraction is available.

For quick reading, use the default dual extraction mode:

```text
<paper_key>.flow.txt
<paper_key>.layout.txt
```

Use `flow` as the primary source for reading order and prose understanding. Use `layout` only to cross-check tables, metrics, baselines, ablation details, equations, or layout-sensitive claims.

Do not rely on quick-read extraction for exhaustive table reconstruction. Page-level extraction, dedicated table extraction, and page-image inspection belong to deep-reading workflows.

Cache files under `state/cache/quick_read_sources/` are temporary and may be cleaned after the configured TTL, defaulting to 7 days.

---

## Outputs

This skill may produce:

```text
outputs/papers/<paper_key>/quick_read.md
outputs/papers/<paper_key>/quick_read.json
```

If `paper_key` is unavailable, use a safe slug based on the title:

```text
outputs/papers/<title_slug>/quick_read.md
outputs/papers/<title_slug>/quick_read.json
```

Create `outputs/papers/<paper_key>/` if it does not exist.

Do not silently overwrite an existing quick-read output. If `quick_read.md` or `quick_read.json` already exists, update it only when the user explicitly allows replacement, or write a timestamped backup such as:

```text
outputs/papers/<paper_key>/quick_read_YYYY-MM-DD_HHMM.md
outputs/papers/<paper_key>/quick_read_YYYY-MM-DD_HHMM.json
```

The Markdown output is for human reading. The JSON output is for `daily-paper-triage` aggregation.

This skill must not produce:

```text
outputs/papers/<paper_key>/deep_read.md
outputs/themes/<theme_id>/synthesis_report.md
```

---

## Quick-read workflow

### Step 1. Identify the paper

Collect or infer basic metadata:

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

Allowed `paper_type` values:

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

If the paper type is uncertain, write:

```text
paper_type: unknown
```

Do not force a classification.

---

### Step 2. Determine evidence availability

Check what evidence is available:

```text
metadata only
abstract available
full text available
PDF available
figures/tables available
page numbers available
PDF text cache available
```

If only metadata or abstract is available, the quick-read result must clearly mark low evidence strength.

Use this field:

```text
evidence_status:
```

Allowed values:

```text
metadata_only
abstract_only
full_text_available
pdf_available
pdf_text_cache_available
page_numbers_available
insufficient_evidence
```

Do not make detailed method or experiment claims from metadata alone.

---

### Step 3. Extract the paper’s core problem

Summarize the paper’s research problem in 1 to 3 sentences.

The summary should answer:

1. What problem does the paper address?
2. Why does the problem matter?
3. What gap or limitation does it respond to?

Use this section title:

```markdown
## 1. 研究问题（research problem）
```

Keep English terms in parentheses for important concepts.

---

### Step 4. Identify the paper’s main contribution

Summarize the main contribution in concise terms.

Use this section title:

```markdown
## 2. 核心贡献（main contribution）
```

Classify the contribution when possible:

```text
new task formulation
new model or algorithm
new system
new dataset
new benchmark
new evaluation method
new taxonomy
new empirical finding
new theoretical framing
```

Do not exaggerate novelty.

If the contribution is unclear, write:

```text
核心贡献尚不清晰，需要精读确认。
```

---

### Step 5. Summarize the method or approach briefly

Give a high-level method summary.

Use this section title:

```markdown
## 3. 方法概览（method overview）
```

For quick reading, this should be brief.

Focus on:

1. input
2. output
3. core mechanism
4. training or inference setup if clearly available
5. important conditions or assumptions

Avoid detailed reconstruction.

Detailed method reconstruction belongs to deep reading.

If the method is not available from the accessible evidence, write:

```text
当前证据不足，无法可靠概括方法机制。
```

---

### Step 6. Check evaluation signals

Summarize only the evaluation signals that are clearly available.

Use this section title:

```markdown
## 4. 评估线索（evaluation signals）
```

Mention:

1. datasets
2. baselines
3. metrics
4. user studies
5. ablations
6. qualitative examples
7. reported limitations

Use English terms for metrics and benchmarks.

Examples:

```text
FID
LPIPS
SSIM
PSNR
human evaluation
ablation study
user study
```

If evaluation details are not available, write:

```text
评估细节尚不充分，需要精读确认。
```

Do not infer baselines, metrics, or results without evidence.

---

### Step 7. Judge relevance to the user’s research

Use this section title:

```markdown
## 5. 与当前研究的关系（relation to current research）
```

Assess relevance to the user’s ongoing interests when applicable:

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

Explain the relation in concrete terms.

Avoid vague statements such as:

```text
这篇论文很有启发。
```

Instead, write:

```text
这篇论文可能有助于比较过程建模（process modeling）中的中间状态表示（intermediate-state representation）。
```

---

### Step 8. Decide why to read or defer

Use this section title:

```markdown
## 6. 阅读价值与暂缓理由（why read / why defer）
```

Include two short lists:

```markdown
### 值得读的理由

### 可以暂缓的理由
```

Possible reasons to read:

```text
directly related to current project
important baseline
useful evaluation design
representative method
survey taxonomy value
strong conceptual framing
useful for presentation
```

Possible reasons to defer:

```text
low relevance
overlapping with already-read work
insufficient evidence
weak evaluation signal
too far from current writing goal
requires domain background not currently needed
```

Both sides should be honest.

A paper may be useful but not urgent.

---

### Step 9. Recommend a triage action

Use this section title:

```markdown
## 7. 分诊结论（triage decision）
```

Choose exactly one action:

```text
deep_read_candidate
quick_read_only
defer
archive_candidate
needs_metadata_fix
needs_pdf_check
```

Definitions:

```text
deep_read_candidate
The paper is worth recommending for formal deep reading.

quick_read_only
The paper is useful to know, but does not currently require deep reading.

defer
The paper may be useful later, but is not urgent now.

archive_candidate
The paper appears low-priority or irrelevant, but must not be archived without user approval.

needs_metadata_fix
Metadata is incomplete or ambiguous.

needs_pdf_check
The PDF is missing, inaccessible, or unreadable.
```

Do not mark the paper as archived automatically.

---

### Step 10. Suggest deep-read focus if relevant

If the action is:

```text
deep_read_candidate
```

include:

```markdown
## 8. 建议精读重点（suggested deep-read focus）
```

Use concise focus statements.

Examples:

```text
任务定义与评估指标（task formulation and evaluation metrics）
模型机制与消融逻辑（model mechanism and ablation logic）
过程建模与中间状态表示（process modeling and intermediate-state representation）
用户研究设计与生态效度（user-study design and ecological validity）
综述分类框架与遗漏边界（taxonomy and omission boundary）
```

If the action is not `deep_read_candidate`, this section may be omitted or written as:

```text
当前不建议进入正式精读。
```

---

## Required quick-read card format

Use `templates/quick_read.md` if available.

The quick-read card should include a stable machine-readable summary block near the top so `daily-paper-triage` can aggregate results even when only Markdown is available.

If the template is missing, use this fallback format:

```markdown
# Quick Read - <Paper Title>

## Metadata

- Paper key:
- Title:
- Authors:
- Year:
- Venue:
- Paper type:
- PDF path:
- Evidence status:

## 1. 研究问题（research problem）

## 2. 核心贡献（main contribution）

## 3. 方法概览（method overview）

## 4. 评估线索（evaluation signals）

## 5. 与当前研究的关系（relation to current research）

## 6. 阅读价值与暂缓理由（why read / why defer）

### 值得读的理由

### 可以暂缓的理由

## 7. 分诊结论（triage decision）

## 8. 建议精读重点（suggested deep-read focus）

## 9. 证据与不确定点（evidence and uncertainty）
```

---

## Evidence and uncertainty section

Every quick-read card must include:

```markdown
## 9. 证据与不确定点（evidence and uncertainty）
```

This section should state:

1. what parts of the paper were available
2. whether page numbers were available
3. which claims are well-supported
4. which judgments are uncertain
5. what should be checked in deep reading

If page numbers are available, use the citation format from `AGENTS.md`.

If page numbers are not reliable, write:

```text
页码未能可靠识别。
```

If full text is unavailable, write:

```text
当前仅基于元数据或摘要判断，结论置信度较低。
```

---

## State update guidance

This skill may propose the following state updates:

```text
queued -> quick_read_done
quick_read_done -> deep_read_candidate
```

Apply state updates only when:

1. the state file exists
2. the user request allows writing state
3. the transition is allowed by `AGENTS.md`
4. no approval gate is bypassed

Do not approve deep reading.

Do not generate deep-reading reports.

Do not archive papers automatically.

---

## Output style

Use Chinese by default.

Keep the quick-read card concise.

Preserve English terms for:

* paper title
* method name
* model name
* dataset name
* metric name
* benchmark name
* established technical concepts

Use Chinese explanation plus English terminology for important concepts.

Avoid:

* long detailed method reconstruction
* unsupported claims
* exaggerated contribution statements
* fabricated baselines
* fabricated metrics
* fabricated page numbers
* formal reviewer-style critique

This is a triage document, not a final reading report.

---

## Failure handling

If the paper cannot be identified, write:

```text
无法唯一识别论文，需要提供 paper key、标题、PDF 路径或 Zotero 记录。
```

If metadata is incomplete, write:

```text
元数据不完整，需要检查 Zotero 记录。
```

If the PDF is missing, write:

```text
PDF 缺失，无法完成可靠快读。
```

If only the abstract is available, write:

```text
当前仅能基于摘要完成低置信度快读。
```

If the method or evaluation is not visible, write:

```text
当前证据不足，无法可靠判断方法或评估细节。
```

---

## Completion criteria

This skill is complete when it produces either:

1. a quick-read card for one paper
2. a clear explanation of why the quick-read card cannot be produced

A complete quick-read card must include:

1. metadata
2. evidence status
3. research problem
4. main contribution
5. method overview
6. evaluation signals
7. relation to user research
8. why read / why defer
9. triage decision
10. evidence and uncertainty

If the paper is recommended for deep reading, include a suggested deep-read focus.
