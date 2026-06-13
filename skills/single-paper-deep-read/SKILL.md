---

name: single-paper-deep-read
description: Use this skill for an approved formal deep reading of one research paper or survey paper. It determines paper_type and report_mode separately, supports research-article and survey-article templates, applies metrics-first analysis for research articles, scope-taxonomy-first analysis for surveys, handles classic/new research article strategies, checks claim-evidence or scope-taxonomy alignment, and produces Chinese reports with English terminology and English-ready takeaways. Do not use it for quick triage, daily queue ranking, or multi-paper synthesis.
---

# Single Paper Deep Read Skill

## 1. Purpose

This skill performs a formal deep reading of one approved paper.

It answers the main question:

```text
这篇论文如何定义问题或领域、如何建立评价或分类标尺、如何展开方法或综述内容、证据是否支撑其主张，以及它对用户研究有什么借鉴意义？
```

This skill is responsible for:

1. verifying that the paper is approved for deep reading
2. determining `paper_type`
3. determining `report_mode`
4. selecting the appropriate template
5. producing a structured Chinese deep-reading report
6. preserving English terminology for later English writing and oral presentation
7. applying metrics-first analysis for research articles
8. applying scope-taxonomy-first analysis for survey articles
9. applying classic/new research-article strategy only when relevant
10. distinguishing paper claims, supported inference, and critical judgment
11. producing critical perspectives and transferable insights

This skill/model, not a pure script, is responsible for producing the analytical deep-reading prose. Scripts may prepare source bundles, approval records, validation reports, daily indexes, external verification records, and state transitions, but scripts must not be treated as sufficient to produce the final deep-read interpretation by themselves.

This skill must not perform:

* quick triage
* daily reading queue ranking
* full theme-based multi-paper synthesis
* full team research tracing
* full literature review writing
* automatic deep-read prose generation without model reading and evidence judgment
* post-report interactive confirmation, clarification, follow-up, or consensus-note maintenance

Related skills:

```text
single-paper-quick-read   Quick-read card for one paper.
daily-paper-triage        Daily reading queue and candidate ranking.
deep-read-interaction     Post-report confirmation, clarification, follow-up, and consensus notes.
theme-coreading           Comparative multi-paper synthesis.
team-research-tracing     Future dedicated skill for full team research tracking.
```

---

## 2. Approval gate

Formal deep reading requires approval.

Deep reading is allowed when at least one condition is true:

1. the user explicitly asks to deep-read this paper in the current request
2. the paper appears in `state/approvals/`
3. the paper state is `deep_read_approved`
4. the user confirms a deep-reading candidate from daily triage

If none of these conditions is met, do not generate a formal deep-reading report.

Write:

```text
该论文尚未获得精读批准，不能生成正式精读报告。可先生成 quick-read card 或等待用户确认。
```

Do not bypass the approval gate.

---

## 3. Global rules

Follow repository-level rules in:

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
* Do not fabricate methods, equations, datasets, baselines, metrics, results, page numbers, lineage, or claims.

Do not duplicate or override global Zotero, Git, state, or safety rules from `AGENTS.md`.

---

## 3.1 Repository path policy

This skill may be invoked through a symlink under:

```text
~/.agents/skills/single-paper-deep-read
```

Do not assume the current working directory is the repository root.

Resolve all repository-relative paths through:

```text
config/paths.toml
```

Use `[repository].root` as the canonical repository root. Resolve paths in `[state]`, `[outputs]`, `[templates]`, `[scripts]`, and `[skills]` relative to that root unless a path is absolute.

If `config/paths.toml` is unavailable, fall back to the nearest ancestor directory containing `AGENTS.md`, `config/paths.toml`, and `skills/`.

---

## 4. Language and terminology policy

Default output language is Chinese.

The report must remain useful for later:

* English paper drafts
* English final reports
* English literature-review sections
* English oral presentations
* English slide outlines

Therefore:

1. Keep original paper titles in English.
2. Keep method names, model names, system names, dataset names, metric names, benchmark names, task names, venue names, and project names in English.
3. When a key term first appears in Chinese, include its English term in parentheses.
4. Do not over-translate established technical terms.
5. If a Chinese translation is tentative, keep the English term and mark the translation as provisional.
6. Include English-ready material when the selected template requires it.

Common terminology pairs:

```text
报告模式 — report mode
完整报告 — full report
压缩报告 — compact report
研究论文 — research article
综述论文 — survey article
核心结论先行 — executive takeaway
研究动机 — research motivation
研究思路 — research idea
评估指标 — evaluation metrics
研究方法 — research method
实验设置 — experimental setup
实验结果 — experimental results
讨论与不足 — discussion and limitations
主张-证据一致性 — claim-evidence alignment
范围-分类一致性 — scope-taxonomy alignment
综述范围 — survey scope
纳入与排除边界 — inclusion and exclusion boundary
分类框架 — taxonomy / classification framework
前序工作 — prior work
后续工作 — follow-up work
引用该文的工作 — citing works
基线工作 — baseline works
通信作者 — corresponding author
同团队研究线索 — same-team research lineage
思辨视角 — critical perspective
借鉴视角 — transferable insight / borrowing perspective
```

---

## 5. Type and mode policy

Before writing the report, determine both:

```text
paper_type:
- research_article
- survey_article
- default_or_unknown

report_mode:
- full_report
- compact_report
```

These two axes must be kept separate.

Do not treat `classic_paper`, `new_paper`, or `survey_paper` as report modes.

---

## 6. Paper type policy

### 6.1 Research article

Use `research_article` for:

```text
method paper
system paper
benchmark paper
dataset paper
empirical study
theory-oriented article
default technical paper
```

A research article should be read through:

```text
research motivation -> research idea -> evaluation metrics -> research method -> experimental setup and results -> claim-evidence alignment -> limitations -> transferable insights
```

For research articles, apply the metrics-first rule.

### 6.2 Survey article

Use `survey_article` for:

```text
survey paper
review paper
systematic review
literature review
meta-review
tutorial-style overview
position-style review
```

A survey article should be read through:

```text
survey scope -> inclusion / exclusion boundary -> adjacent surveys -> organizing perspective -> taxonomy -> content synthesis -> challenges -> future directions -> limitations -> transferable insights
```

For survey articles, apply the scope-taxonomy-first rule.

Do not force method-paper structure on survey papers.

### 6.3 Default or unknown

Use `default_or_unknown` when the type is unclear.

State clearly:

```text
论文类型尚不明确，以下报告采用通用精读格式。
```

Use the closest suitable structure without forcing a wrong type.

---

## 7. Research article subtype policy

For research articles only, determine whether the paper is:

```text
classic_paper
new_paper
ordinary_research_article
```

This subtype affects lineage tracing and review strictness.

It must not determine report length by itself.

### 7.1 Classic paper strategy

Use `classic_paper` when the user explicitly calls the paper classic, foundational, representative, historically important, or when the paper is mainly read for lineage and influence.

For classic papers, lineage tracing should prioritize:

1. prior work
2. same-team prior work when available
3. follow-up work
4. same-team follow-up work when available
5. representative citing works

For classic papers, do not overemphasize reviewer-style criticism.

The report should:

* identify objective limitations
* explain how limitations affected later work
* connect limitations with lineage when possible

Do not create a required standalone section named:

```text
why it became classic
```

The classic value may be discussed in the executive takeaway or discussion.

### 7.2 New paper strategy

Use `new_paper` when the user explicitly calls the paper new, recent, latest, newly published, or when the task is to understand a current work.

For new papers, lineage tracing should prioritize:

1. prior work
2. same-team prior work when available
3. baseline works
4. concurrent work if verifiable

New papers do not require citing works unless the user explicitly asks.

For new papers, reviewer-style scrutiny should prioritize:

1. whether claims are supported by evidence
2. whether baselines are strong and fair
3. whether evaluation design is biased
4. whether metrics measure the claimed capability
5. whether results generalize
6. whether conclusions are reproducible
7. whether the paper overclaims beyond the evidence

### 7.3 Ordinary research article

Use `ordinary_research_article` when neither classic nor new strategy clearly applies.

For ordinary research articles, use balanced lineage tracing:

1. key prior work
2. key baseline work
3. related same-team work if visible
4. follow-up or citing works only if relevant and verifiable

---

## 8. Preprint status policy

When the paper appears to be a preprint or unpublished manuscript, first attempt to verify its publication status.

This applies to:

```text
arXiv preprint
bioRxiv preprint
OpenReview submission
under review manuscript
unpublished technical report
```

Check when possible:

1. whether the paper has been accepted by a conference, journal, or proceedings
2. whether a formal published version exists
3. whether multiple versions exist
4. whether the current reading version is the latest version
5. whether the preprint and published versions differ substantially

Report one of:

```text
Preprint status:
- published version confirmed
- accepted but not yet published
- preprint only
- status unknown
```

If a published version is confirmed, prioritize the published version.

If only a preprint is available or status is unknown, apply stricter reviewer-style scrutiny and claim-evidence checking.

Additional checks for preprints:

1. missing key experiments, ablations, or baselines
2. unresolved public review comments if available
3. inconsistency with later public versions
4. missing code, data, or experimental settings
5. selective reporting risk
6. instability caused by lack of peer review
7. overclaiming beyond evidence
8. bias in evaluation, data selection, or baseline choice

Do not dismiss a paper only because it is a preprint.

Mark uncertainty explicitly.

---

## 9. Report mode policy

### 9.1 Full report

Use `full_report` when:

1. the user explicitly asks for full, careful, or deep reading
2. the paper is central to current research, writing, presentation, or experiment design
3. the user is entering a new research direction and this paper may become a core reference
4. the paper is a representative work, core baseline, important survey, or framework source

A full report should preserve:

1. executive takeaway
2. problem, scope, or motivation
3. idea, organizing perspective, or taxonomy
4. evaluation metrics or scope-taxonomy alignment
5. method, experiments, or content synthesis
6. claim-evidence or scope-taxonomy checking
7. limitations
8. lineage, adjacent survey, or author-follow-up analysis when relevant
9. critical perspectives
10. transferable insights
11. English-ready takeaways

### 9.2 Compact report

Use `compact_report` when:

1. the paper is medium-importance
2. the goal is screening relevance
3. the paper is a background or auxiliary reference
4. the user explicitly asks for a compact, brief, or compressed report
5. the deep read follows daily reading and only key judgments are needed

A compact report means:

```text
少展开，不是少读。
```

Compact reports must preserve the core analytical judgment.

---

## 10. Default mode rules

Use these defaults when the user does not specify report mode.

```text
research_article + classic_paper:
  full_report if the paper is central; compact_report is allowed otherwise.

research_article + new_paper:
  full_report if central to current writing or research; compact_report is allowed otherwise.

research_article + ordinary_research_article:
  compact_report by default unless the user asks for full deep reading or the paper is central.

survey_article:
  full_report if used for literature-review writing, framework borrowing, or research-arc construction;
  compact_report if only screening relevance.

default_or_unknown:
  compact_report by default unless the user asks for full deep reading.
```

If uncertain, state the chosen mode and reason briefly.

Example:

```text
本报告采用 compact_report，因为该文目前用于判断是否纳入综述，而非作为核心参考文献。
```

---

## 11. Compression policy

### 11.1 Research article compact report

A compact research-article report must preserve:

1. executive takeaway
2. research motivation
3. research idea
4. evaluation metrics
5. research method
6. experimental setup and results
7. claim-evidence alignment
8. discussion and limitations
9. transferable insights

It may compress:

1. lineage tracing
2. team tracing
3. detailed experiment tables
4. figure-by-figure explanation
5. English oral material
6. reviewer-style questions

Compression guidance:

```text
- lineage tracing: keep only 2–4 key works
- team tracing: keep one compact table or one paragraph
- experiments: keep main results and key ablations only
- English material: keep key terms and one-slide takeaway
- critical perspective: keep 2–3 core weaknesses
```

### 11.2 Survey article compact report

A compact survey-article report must preserve:

1. executive takeaway
2. survey scope
3. inclusion / exclusion boundary
4. review logic and organizing perspective
5. research taxonomy / classification framework
6. current challenges
7. future research directions
8. discussion and limitations
9. transferable insights

It may compress:

1. relation to adjacent surveys
2. author follow-up works vs proposed future directions
3. detailed taxonomy content synthesis
4. representative work tables under each category
5. English oral material
6. reviewer-style and peer-researcher sections

If adjacent survey comparison is compressed, retain:

```text
该综述相对已有综述的主要差异在于……；但该判断仍需进一步检索相邻综述确认。
```

If author follow-up comparison is compressed, retain:

```text
作者后续工作需要外部检索确认；当前不能可靠判断其是否回应了综述中的 future directions。
```

---

## 12. Executive takeaway policy

Every report starts with:

```text
核心结论先行（executive takeaway）
```

This section is not a method summary and does not replace metrics-first analysis.

Its purpose is:

```text
帮助记忆这篇论文，并提供一个能触发后续细节回忆的抓手。
```

Keep it to 3–5 sentences.

It should answer:

1. what is the most memorable point of the paper
2. what problem it solves or what survey scope it defines
3. what its core idea, taxonomy, or organizing perspective is
4. what evaluation, evidence, or classification standard it uses
5. why it matters to the user’s research

Do not expand complex method details in this section.

When a reliable key figure is available, include a visual anchor in the first report section.

Choose the most important:

```text
research article -> model architecture / method pipeline / system workflow
survey article -> scope diagram / taxonomy overview / review framework
default_or_unknown -> central process, framework, or scope figure
```

Prefer `state/cache/deep_read_sources/<paper_key>/figures.json` and rendered figure/page images. If no reliable key figure is available, state that the key visual anchor requires visual verification rather than inserting a decorative or weakly related figure.

When `figures.json` provides both a full-page image and a cropped image, prefer `repo_relative_crop_image_path` for the Markdown image link. Fall back to the full-page image only when the crop is missing or visually misleading.

---

## 13. Metrics-first and scope-taxonomy-first rules

### 13.1 Metrics-first for research articles

For research articles, place evaluation metrics before detailed method reconstruction.

Required order:

```text
研究动机（research motivation）
研究思路（research idea）
评估指标（evaluation metrics）
研究方法（research method）
实验设置与结果（experimental setup and results）
```

Purpose:

```text
先理解论文如何定义“好”、如何评估、优化目标是什么，再进入方法机制。
```

If the paper does not provide explicit quantitative metrics, write:

```text
本文未提供明确的量化评估指标（quantitative evaluation metrics），需根据任务目标、用户研究或定性评估方式理解其评价逻辑。
```

For HCI or system papers, metrics may include:

```text
dependent variables
user-study measures
subjective ratings
task performance
interaction logs
qualitative codes
ecological validity
```

### 13.2 Scope-taxonomy-first for survey articles

For survey articles, first clarify:

1. survey scope
2. inclusion / exclusion boundary
3. relation to adjacent surveys when relevant
4. organizing perspective
5. taxonomy or classification framework

Purpose:

```text
先理解综述如何定义范围、边界和分类维度，再进入具体内容梳理。
```

---

## 14. Alignment checks

### 14.1 Claim-evidence alignment for research articles

All research-article reports must include:

```markdown
## Claim-evidence 检查（claim-evidence alignment）
```

This section checks whether the authors’ core claims are supported by experiments, metrics, ablations, user studies, or qualitative evidence.

Use this table when possible:

```markdown
| Claim | Evidence | Evidence strength | What it supports | What it does not prove |
|---|---|---|---|---|
|  | （文件名：xxx.pdf，第 x 页） | strong / moderate / weak / unclear |  |  |
```

Check:

1. whether claims exceed experimental scope
2. whether metrics measure the claimed ability
3. whether baselines are strong enough
4. whether ablations support the key module
5. whether results are limited to specific datasets or scenarios
6. whether qualitative examples are treated as strong evidence

### 14.2 Scope-taxonomy alignment for survey articles

Survey article reports must include:

```markdown
## Scope-taxonomy 检查（scope-taxonomy alignment）
```

This section checks whether survey scope, inclusion boundary, taxonomy, and synthesized content align.

Use this table when possible:

```markdown
| Survey claim / scope decision | Evidence | Strength | What it covers | What may be missing |
|---|---|---|---|---|
|  | （文件名：xxx.pdf，第 x 页） | strong / moderate / weak / unclear |  |  |
```

Check:

1. whether scope is clear
2. whether inclusion / exclusion criteria are transparent
3. whether taxonomy serves the survey question
4. whether categories are mutually exclusive or hierarchically clear
5. whether taxonomy covers major work
6. whether adjacent directions or adjacent surveys may be missing
7. whether challenges and future directions follow naturally from the synthesis

---

## 15. Adjacent survey search guidance

Survey full reports must attempt adjacent survey search.

Survey compact reports may do lightweight candidate search or mark this as needing verification.

Use available local evidence first:

1. survey paper references
2. related-work section
3. paper keywords
4. Zotero library index
5. existing theme packets

If external search is available, use queries such as:

```text
"<topic>" survey
"<topic>" review
"<topic>" systematic review
"<topic>" literature review
"<topic>" taxonomy
"<topic>" benchmark survey
"<topic>" evaluation survey
"<core task>" survey
"<core method>" survey
"<application domain>" review
"<evaluation target>" survey
```

For AI / HCI / creative AI topics, also consider:

```text
human-AI co-creation survey
generative models survey
digital art generation survey
creative AI evaluation survey
interactive AI systems review
```

Adjacent survey candidates must be marked with confidence:

```text
confirmed
likely
candidate
unverified
```

Use this table when possible:

```markdown
| Survey | Year | Scope | Taxonomy | Difference from target survey | Confidence |
|---|---:|---|---|---|---|
|  |  |  |  |  | confirmed / likely / candidate / unverified |
```

Do not present unverified survey candidates as confirmed adjacent surveys.

If external search is unavailable, write:

```text
相邻综述需要外部检索确认；当前仅能基于本地 PDF、references 与 Zotero 索引进行有限判断。
```

---

## 16. Author follow-up policy for survey articles

Survey full reports should attempt to trace whether the survey authors later worked on directions proposed in the survey.

Survey compact reports may compress this into a short note or a verification-needed statement.

Check whether:

1. the survey authors later continued in the same field
2. later work responded to the future directions proposed in the survey
3. authors shifted from survey to benchmark, system, method, dataset, or evaluation work
4. later work helps evaluate whether the proposed directions were productive

If external search is unavailable or evidence is insufficient, write:

```text
作者后续工作需要外部检索确认；当前不能可靠判断其是否回应了综述中的 future directions。
```

Do not fabricate author follow-up works.

---

## 17. External lineage and citation-tracing policy

Some tracing tasks may require information beyond the local PDF, especially:

```text
follow-up work
citing works
same-team follow-up work
author follow-up work
adjacent surveys
```

Use available local evidence first:

1. the paper’s related work section
2. the paper’s references
3. author names and affiliations
4. baseline tables
5. local Zotero records
6. existing quick-read reports
7. existing theme packets

If external search, citation databases, Google Scholar, Semantic Scholar, OpenAlex, Crossref, arXiv, publisher pages, project pages, or lab pages are available, use them to verify follow-up and citing works.

If external search is not available, do not fabricate.

Write:

```text
外部谱系、引用、作者后续工作或相邻综述需要外部检索确认；当前仅能基于本地论文和 Zotero 索引进行有限追踪。
```

When listing related works, distinguish:

```text
paper-cited prior work
baseline work
same-team candidate work
externally verified citing work
adjacent survey candidate
author follow-up candidate
unverified candidate
```

Do not present unverified candidate works as confirmed lineage.

---

## 18. Lightweight team research tracing

This skill performs only lightweight team research tracing.

Full team-level literature tracing belongs to a future dedicated skill:

```text
skills/team-research-tracing/SKILL.md
```

The purpose of lightweight tracing is to identify whether the target paper belongs to a visible research line, not to produce a complete genealogy.

Use multiple signals instead of relying on author names alone.

Preferred signals:

```text
corresponding author
first author
last author / senior author
author affiliation
email domain
lab or project page if available
ORCID
Semantic Scholar authorId
OpenAlex author ID
shared coauthors
shared project name
shared method name
shared task or benchmark
```

Do not treat name overlap alone as sufficient evidence.

If author identity is ambiguous, write:

```text
作者身份存在歧义，不能仅凭姓名判断为同一研究者。
```

Confidence levels:

```text
confirmed
likely
candidate
unverified
```

Definitions:

```text
confirmed
Verified by DOI, author ID, citation database, paper metadata, or explicit citation.

likely
Strong evidence from shared authors, affiliation, topic, and time order, but not fully verified.

candidate
Potentially related based on title, keywords, or local context.

unverified
Needs external search before being treated as related work.
```

---

## 19. Critical and transferable perspectives

Every report must include critical and transferable perspectives, with the depth depending on report mode.

### 19.1 Reviewer-style weaknesses

For research articles, emphasize:

```text
novelty
technical soundness
evaluation validity
baseline choice
ablation design
reproducibility
generalization
user-study design
claim-evidence alignment
```

For classic papers, this section may be shorter and may focus on objective limitations and how later works addressed them.

For new papers and preprints, this section should be stricter.

For survey articles, emphasize:

```text
scope clarity
inclusion criteria
taxonomy validity
coverage bias
comparison depth
relation to adjacent surveys
future direction quality
scope-taxonomy alignment
```

### 19.2 Peer-researcher follow-up directions

Propose concrete follow-up directions.

Avoid vague suggestions.

A good direction should explain:

1. what limitation or gap it responds to
2. how it extends the paper
3. what new data, method, system, task, or evaluation may be needed

### 19.3 Transferable insights

Connect the paper to the user’s research direction.

Possible user contexts:

```text
digital painting process generation
human-AI co-creation
process-level evaluation
interactive generation systems
art persona modeling
multi-modal creative systems
literature review writing
experimental design
```

Explain:

1. what can be borrowed
2. what should not be borrowed directly
3. what comparison dimension it suggests
4. what evaluation idea it contributes
5. what open problem it exposes

Avoid vague statements such as:

```text
对我的研究很有启发。
```

Use concrete statements such as:

```text
这篇论文可为过程级评估（process-level evaluation）提供一个对照维度，但其评估仍偏向最终结果，因此不能直接覆盖中间状态查询（intermediate-state querying）的交互价值。
```

---

## 20. Template selection

Use the appropriate template when available.

Template paths:

```text
templates.deep_read_research_full -> templates/deep_read_research_full.md
templates.deep_read_research_compact -> templates/deep_read_research_compact.md
templates.deep_read_survey_full -> templates/deep_read_survey_full.md
templates.deep_read_survey_compact -> templates/deep_read_survey_compact.md
templates.deep_read_default_full -> templates/deep_read_default_full.md
templates.deep_read_default_compact -> templates/deep_read_default_compact.md
```

Selection rule:

```text
research_article + full_report -> templates/deep_read_research_full.md
research_article + compact_report -> templates/deep_read_research_compact.md

survey_article + full_report -> templates/deep_read_survey_full.md
survey_article + compact_report -> templates/deep_read_survey_compact.md

default_or_unknown + full_report -> templates/deep_read_default_full.md
default_or_unknown + compact_report -> templates/deep_read_default_compact.md
```

If the corresponding template is missing, use the required sections defined in this skill.

Do not mix templates unless the user explicitly requests a hybrid report.

---

## 21. Inputs

Use available inputs when present:

```text
config/paths.toml
state/library_index.jsonl
state/reading_queue.json
state/approvals/
state/candidates/YYYY-MM-DD_deep_read_candidates.json
outputs/daily/YYYY-MM-DD/deep_read_candidates.json
outputs/papers/<paper_key>/quick_read.md
outputs/papers/<paper_key>/quick_read.json
outputs/daily/YYYY-MM-DD/quick_reads/<paper_key>.md
outputs/daily/YYYY-MM-DD/quick_reads/<paper_key>.json
state/cache/quick_read_sources/<paper_key>.flow.txt
state/cache/quick_read_sources/<paper_key>.layout.txt
state/cache/quick_read_sources/<paper_key>.source.json
state/cache/deep_read_sources/<paper_key>/pages.json
state/cache/deep_read_sources/<paper_key>/tables.md
state/cache/deep_read_sources/<paper_key>/figures.json
state/cache/deep_read_sources/<paper_key>/figures/
state/cache/deep_read_sources/<paper_key>/source.json
state/external_verification/<paper_key>.json
scripts/extract_quick_read_source.py
scripts/extract_deep_read_source.py
scripts/verify_external_evidence.py
scripts/validate_workflow_outputs.py
templates/deep_read_research_full.md
templates/deep_read_research_compact.md
templates/deep_read_survey_full.md
templates/deep_read_survey_compact.md
templates/deep_read_default_full.md
templates/deep_read_default_compact.md
```

Input priority:

1. current user request and explicit approval
2. approval record in `state/approvals/`
3. approved state record with `deep_read_approved`
4. daily triage candidate confirmed by the user
5. canonical quick-read outputs under `outputs/papers/<paper_key>/`
6. current daily-run quick-read outputs under `outputs/daily/YYYY-MM-DD/quick_reads/`
7. deep-read source cache under `state/cache/deep_read_sources/`
8. quick-read source cache under `state/cache/quick_read_sources/`
9. external verification records under `state/external_verification/`
10. reading queue and Zotero metadata

Candidate files such as `deep_read_candidates.json` are not approval by themselves. They only become approval when the user confirms the paper for deep reading or an approval/state record is written.

A single paper may be identified by:

1. Zotero item key
2. PDF path
3. paper title
4. DOI or arXiv ID
5. user-provided metadata
6. approved candidate record
7. entry from `state/reading_queue.json`

If the paper cannot be uniquely identified, report the ambiguity instead of guessing.

---

## 22. Outputs

This skill may produce:

```text
outputs/papers/<paper_key>/deep_read.md
outputs/papers/<paper_key>/deep_read.json
outputs/daily/YYYY-MM-DD/deep_reads/<paper_key>.md
outputs/daily/YYYY-MM-DD/deep_reads/<paper_key>.json
```

If `paper_key` is unavailable, use a safe slug based on the title:

```text
outputs/papers/<title_slug>/deep_read.md
outputs/papers/<title_slug>/deep_read.json
outputs/daily/YYYY-MM-DD/deep_reads/<title_slug>.md
outputs/daily/YYYY-MM-DD/deep_reads/<title_slug>.json
```

The paper directory is the canonical long-term location. The daily directory is the run view that shows which papers entered deep reading on that date.

The JSON sidecar should be machine-readable and suitable for later `theme-coreading`.

Minimum `deep_read.json` fields:

```json
{
  "schema_version": "1.0",
  "paper_key": "",
  "title": "",
  "paper_type": "research_article | survey_article | default_or_unknown",
  "research_subtype": "classic_paper | new_paper | ordinary_research_article | not_applicable",
  "report_mode": "full_report | compact_report",
  "template_used": "",
  "approval_source": "",
  "source_paths": [],
  "evidence_status": "",
  "page_evidence_status": "",
  "preprint_status": "",
  "key_takeaway": "",
  "key_figure_path": "",
  "key_figure_caption": "",
  "key_figure_page": null,
  "key_figure_role": "",
  "claim_evidence_summary": "",
  "transferable_insights": [],
  "generated_at": ""
}
```

This skill may propose a state update:

```text
deep_read_approved -> deep_read_done
```

This skill must not produce:

```text
outputs/themes/<theme_id>/synthesis_report.md
```

This skill must not modify Zotero records.

---

## 23. Deep-reading workflow

### Step 1. Verify approval and identify the paper

Confirm that the paper is approved for deep reading.

Then identify:

```text
paper_key
title
authors
year
venue
paper_type
research_subtype if applicable
report_mode
preprint_status if applicable
pdf_path
approval_source
quick_read_path
quick_read_json_path
source_cache_paths
daily_run_date if applicable
selected_template
```

If paper type is uncertain, choose `default_or_unknown`.

Do not force the paper into a wrong type.

### Step 2. Determine paper_type

Classify the paper as:

```text
research_article
survey_article
default_or_unknown
```

Use the rules in Section 6.

### Step 3. Determine research_subtype if applicable

Only for `research_article`, classify as:

```text
classic_paper
new_paper
ordinary_research_article
```

Use the rules in Section 7.

### Step 4. Determine report_mode

Classify as:

```text
full_report
compact_report
```

Use the user request and default mode rules.

State the selected mode briefly if it is not obvious.

### Step 5. Check preprint status if applicable

If the paper is a preprint, submission, or unpublished manuscript, apply Section 8.

Because publication and acceptance status can change, verify the latest status with the most authoritative available source when network or external search is available:

```text
publisher page
official conference proceedings
OpenReview
arXiv version history
DOI landing page
project page or author page
```

If external verification is unavailable, mark the status as `status unknown` or `unverified` rather than inferring acceptance.

When network access is available and the report depends on preprint status, adjacent surveys, author follow-up, or citing/follow-up work, perform or request external verification and record the result in:

```text
state/external_verification/<paper_key>.json
```

### Step 6. Select template

Select the matching template from Section 20.

### Step 7. Read and extract evidence

Extract evidence according to paper_type and report_mode.

Use the strongest available source first:

1. original PDF or full text
2. `state/cache/deep_read_sources/<paper_key>/pages.json`
3. `state/cache/deep_read_sources/<paper_key>/tables.md`
4. `state/cache/deep_read_sources/<paper_key>/figures.json` and figure images
5. page-aware or layout-aware extraction if available
6. `state/cache/quick_read_sources/<paper_key>.layout.txt`
7. `state/cache/quick_read_sources/<paper_key>.flow.txt`
8. `outputs/papers/<paper_key>/quick_read.json`
9. `outputs/papers/<paper_key>/quick_read.md`
10. Zotero metadata and reading queue metadata

Do not rely on quick-read outputs alone for a formal deep read unless the user explicitly accepts an evidence-limited report.

For two-column PDFs, tables, figures, equations, or extraction artifacts:

1. prefer layout-aware text over flow text when column order matters
2. inspect table/figure captions and surrounding paragraphs before interpreting results
3. use extracted figure images when a figure is central to the claim or method explanation
4. if a table or figure is central to the claim but extraction is unreliable, state that it requires page-level or visual inspection
5. do not reconstruct numeric results from garbled table text
6. mark page numbers as unreliable when the extraction source cannot preserve pages

For the first report section, select at most one key visual anchor. Do not include every detected figure there. Additional figures may be discussed later only when they support a specific claim.

For research articles, prioritize:

```text
research motivation
research idea
evaluation metrics
research method
experimental setup and results
claim-evidence alignment
limitations
lineage tracing
transferable insights
```

For survey articles, prioritize:

```text
survey scope
inclusion and exclusion boundary
adjacent surveys if full_report
review logic and organizing perspective
taxonomy
content synthesis
challenges
future directions
scope-taxonomy alignment
author follow-up if full_report
transferable insights
```

Record evidence locations while reading.

Do not write the final report from memory alone.

### Step 8. Write the report

Use the selected template.

For every major claim, include evidence locations when available.

Keep the report analytical rather than translational.

Do not produce a full literature-review section unless the user asks.

Do not turn a single-paper report into a complete multi-paper survey.

### Step 9. Add critical and transferable perspectives

Use the depth required by report_mode.

Compact reports may compress these sections but must not remove transferable insights.

### Step 10. Add English-ready takeaways

Every full report must include English-ready takeaways.

Compact reports may include only:

```text
key terms
one-slide takeaway
```

unless the user asks for oral material.

---

## 24. Required report sections

Templates should reduce reader pressure by grouping detailed checks into 7-8 major report sections. Do not expand a deep-read report into many small top-level sections unless the user explicitly asks.

Metadata is required but does not count as a report section.

### 24.1 Research article full report

Must include 8 major sections:

1. ??????????executive takeaway?
2. ???????????problem, motivation, and central idea?
3. ??????????evaluation metrics and evidence design?
4. ??????????method, mechanism, and results?
5. Claim-evidence ??????alignment, discussion, and limitations?
6. ?????????????lineage, team signals, and verification?
7. ??????????????transferable insights and follow-up directions?
8. ????? oral ?????English-ready takeaways?

### 24.2 Research article compact report

Must include 7 major sections:

1. ??????????executive takeaway?
2. ???????????problem, motivation, and idea?
3. ??????????evaluation metrics and evidence design?
4. ??????????method and results?
5. Claim-evidence ??????alignment and limitations?
6. ?????????????lineage and verification?
7. ??????????transferable insights and English-ready material?

Compact deep read is still a deep-read report. It may compress tables and explanatory prose, but it must preserve metrics-first reasoning, evidence judgment, limitations, and transferable insights.

### 24.3 Survey article full report

Must include 8 major sections:

1. ??????????executive takeaway and scope positioning?
2. ???????????scope, boundary, and adjacent surveys?
3. ??????????review logic and taxonomy?
4. ??????????content synthesis by taxonomy?
5. Scope-taxonomy ???????????alignment, challenges, and future directions?
6. ?????????????author follow-up, verification, and limitations?
7. ??????????????transferable insights and follow-up questions?
8. ????? oral ?????English-ready takeaways?

### 24.4 Survey article compact report

Must include 7 major sections:

1. ??????????executive takeaway and scope?
2. ???????????scope, boundary, and adjacent surveys?
3. ??????????review logic and taxonomy?
4. ??????????content synthesis?
5. Scope-taxonomy ???????????alignment, challenges, and directions?
6. ?????????????limitations and verification?
7. ??????????transferable insights and English-ready material?

### 24.5 Default full report

Must include 8 major sections:

1. ??????????type decision and executive takeaway?
2. ???????????problem, scope, and organizing perspective?
3. ???????????evaluation, evidence, or classification standard?
4. ?????????????method, content, or argument structure?
5. Alignment ??????alignment and limitations?
6. ???????????????related work, author signals, and verification?
7. ??????????????transferable insights and follow-up directions?
8. ????? oral ?????English-ready takeaways?

### 24.6 Default compact report

Must include 7 major sections:

1. ??????????type decision and executive takeaway?
2. ???????????problem, scope, and organizing perspective?
3. ???????????evaluation, evidence, or classification standard?
4. ?????????????method, content, or argument?
5. Alignment ??????alignment and limitations?
6. ??????????external notes and verification?
7. ??????????transferable insights and English-ready material?

---

## 25. Evidence requirements

Formal deep reading requires strong evidence.

Preferred evidence level:

```text
PDF available
full text available
page numbers available
figures and tables available
references available
appendix available if relevant
```

Evidence source hierarchy:

```text
original PDF or page-aware source
layout-aware extracted text
flow extracted text
quick_read.json
quick_read.md
Zotero metadata
reading_queue.json
```

For deep reading, metadata, abstracts, and quick-read summaries are supporting context, not sufficient evidence by themselves.

If only metadata or abstract is available, do not produce a formal deep-reading report.

Write:

```text
当前仅有元数据或摘要，证据不足，不能生成正式精读报告。
```

Every paper-specific claim should be grounded in the most precise available location.

Preferred citation format:

```text
（文件名：xxx.pdf，第 x 页）
```

For figures, tables, equations, and appendices, cite as precisely as possible:

```text
（文件名：xxx.pdf，第 x 页，Figure x）
（文件名：xxx.pdf，第 x 页，Table x）
（文件名：xxx.pdf，第 x 页，Appendix x）
```

If page numbers cannot be reliably extracted, write:

```text
页码未能可靠识别。
```

If table, figure, equation, or appendix evidence is needed but the extraction is unreliable, write:

```text
该证据需要页面级或图像级复核；当前文本抽取不足以可靠还原表格、图或公式。
```

Distinguish:

```text
作者明确声称
可由文本支持的推断
我的判断
```

---

## 26. State update guidance

This skill may propose or apply the following state update:

```text
deep_read_approved -> deep_read_done
```

Candidate and approval lifecycle:

```text
deep_read_candidate -> deep_read_approved -> deep_read_done
```

`deep_read_candidate` means the paper was recommended or shortlisted. It is not enough to start formal deep reading.

`deep_read_approved` means the user or state record has approved deep reading.

`deep_read_done` means both the Markdown report and JSON sidecar were generated successfully.

Apply the update only when:

1. the state file exists
2. the paper is approved for deep reading
3. the deep-reading Markdown report has actually been generated
4. the deep-reading JSON sidecar has actually been generated
5. the transition is allowed by `AGENTS.md`
6. the user request allows writing state

Do not archive papers automatically.

Do not modify Zotero records.

---

## 27. Failure handling

If the paper is not approved for deep reading, write:

```text
该论文尚未获得精读批准，不能生成正式精读报告。
```

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
PDF 缺失，无法完成正式精读。
```

If only metadata or abstract is available, write:

```text
当前仅有元数据或摘要，证据不足，不能生成正式精读报告。
```

If page numbers cannot be reliably extracted, write:

```text
页码未能可靠识别。
```

If method details are unavailable, write:

```text
方法细节不足，无法可靠重建完整机制。
```

If evaluation details are unavailable, write:

```text
评估细节不足，难以判断结论强度。
```

If external lineage, author follow-up, citing works, or adjacent surveys cannot be verified, write:

```text
外部谱系、引用、作者后续工作或相邻综述需要外部检索确认；当前不能可靠断言。
```

---

## 28. Completion criteria

This skill is complete when it produces either:

1. a formal type-aware and mode-aware deep-reading report for one approved paper
2. a clear explanation of why the report cannot be produced

A complete report must satisfy the required section list for its selected `paper_type` and `report_mode`.

If the report is generated successfully, propose the state update:

```text
deep_read_approved -> deep_read_done
```
