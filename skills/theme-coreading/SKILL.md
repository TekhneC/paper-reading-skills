---

name: theme-coreading
description: Use this skill for interactive theme-based co-reading of multiple papers. It supports literature-review writing, research design, and new-topic understanding by maintaining a user-confirmed theme, user-confirmed research question, paper roles, comparison dimensions, field lineage tracing, supplementary reading recommendations, quick/deep read handoffs, interaction logs, and evolving synthesis reports. Do not use it for single-paper quick read, single-paper deep read, daily triage, or final literature-review writing.
------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

---

name: theme-coreading
description: Use this skill for interactive theme-based co-reading of multiple papers. It supports literature-review writing, research design, and new-topic understanding by maintaining a user-controlled theme and research question, a persistent theme state, a comparison matrix, field lineage tracing, supplementary reading recommendations, quick/deep read handoffs, and an evolving synthesis report. Do not use it for single-paper quick read, single-paper deep read, daily triage, or final literature-review writing.
--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# Theme Co-reading Skill

## 1. Purpose

This skill supports interactive theme-based co-reading of multiple papers.

It answers the main question:

```text
在用户确认的核心主题和研究问题下，这组论文分别承担什么角色、如何相互关联、共同揭示了什么文献谱系、比较维度、研究空白，并如何支持用户的综述写作、研究设计或新主题理解？
```

This skill is responsible for:

1. preserving the user’s core theme
2. preserving or helping clarify the user’s research question
3. labeling paper roles relative to the user-confirmed research question
4. maintaining a persistent theme state
5. recording user interaction focus and decisions
6. building and updating a comparison matrix
7. tracing the field lineage around the provided paper set
8. recommending supplementary readings with evidence and confidence levels
9. handing papers off to quick read or deep read when needed
10. producing and updating a theme-level synthesis report

This skill must not replace the user’s role in deciding the research question.

Core principle:

```text
用户决定研究问题；skill 围绕该问题组织文献、比较论文、追踪谱系、补全阅读证据。
```

Co-reading is not:

```text
多篇论文摘要的拼接。
```

Co-reading is:

```text
围绕用户确认的主题和研究问题，建立比较框架、追踪领域谱系，并逐步形成可用于综述写作和研究设计的文献理解。
```

---

## 2. Related skills

Use related skills when appropriate:

```text
daily-paper-triage        Daily queue, quick-read aggregation, and deep-reading candidate ranking.
single-paper-quick-read   One-paper quick-read card for triage and inclusion decisions.
single-paper-deep-read    One-paper formal deep-reading report for core papers, baselines, and decisive works.
team-research-tracing     Future dedicated skill for full team or lab research trajectory tracing.
```

This skill may use outputs from:

```text
outputs/papers/<paper_key>/quick_read.md
outputs/papers/<paper_key>/deep_read.md
state/library_index.jsonl
state/reading_queue.json
state/approvals/
outputs/themes/<theme_id>/
```

This skill may hand off work to:

```text
single-paper-quick-read
single-paper-deep-read
```

However, it must not duplicate the full logic of those skills.

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
* Do not fabricate methods, datasets, baselines, metrics, results, page numbers, paper relations, citation links, author lineages, or supplementary readings.

Do not duplicate or override global Zotero, Git, state, or safety rules from `AGENTS.md`.

---

## 4. Language and terminology policy

Default output language is Chinese.

The output should remain useful for:

* Chinese literature-review drafting
* English final paper writing
* English oral presentation
* slide preparation
* research proposal writing
* experimental design

Therefore:

1. Keep original paper titles in English.
2. Keep method names, model names, dataset names, benchmark names, metric names, task names, and system names in English.
3. When a key term first appears in Chinese, include its English term in parentheses.
4. Do not over-translate established technical terms.
5. If a Chinese translation is tentative, keep the English term and mark the translation as provisional.
6. Include English-ready synthesis material when useful.

Common terminology pairs:

```text
主题共读 — theme-based co-reading
持续交互式共读 — interactive theme co-reading
核心主题 — core theme
研究问题 — research question
论文角色 — paper role
比较维度 — comparison dimension
比较矩阵 — comparison matrix
领域研究谱系 — field research lineage
补充阅读 — supplementary reading
阅读移交 — reading handoff
快速阅读 — quick read
深度阅读 — deep read
任务定义 — task formulation
方法范式 — methodological paradigm
评估协议 — evaluation protocol
评价指标 — evaluation metrics
基线工作 — baseline work
研究谱系 — research lineage
分类框架 — taxonomy / classification framework
研究空白 — research gap
张力 — tension
可迁移借鉴 — transferable insight
综述弧线 — review arc
用户交互重点 — user interaction focus
决策记录 — decision log
```

---

## 5. When to use this skill

Use this skill when the user asks to:

* co-read multiple papers around a user-defined theme
* understand a new research direction
* compare several papers under a research question
* build a taxonomy from a paper set
* synthesize a literature cluster
* prepare a literature review
* support research design
* identify field lineage and missing papers
* recommend supplementary readings
* update an existing theme-reading session
* revise comparison dimensions after user interaction
* connect a paper cluster to the user’s own project

Typical requests:

```text
请围绕数字绘画过程生成共读这几篇论文。
```

```text
我的研究问题是……请基于这组论文建立比较框架。
```

```text
请比较这些论文在任务定义、方法和评价上的差异。
```

```text
请基于这组论文形成综述分类框架。
```

```text
请继续上次的 theme co-reading，并根据新的论文更新矩阵。
```

---

## 6. When not to use this skill

Do not use this skill for:

* one-paper quick reading
* one-paper formal deep reading
* daily reading queue triage
* final publishable literature-review writing without user approval
* translating entire papers
* full team or lab research trajectory tracing

If the user provides only one paper, use:

```text
single-paper-quick-read
```

or:

```text
single-paper-deep-read
```

depending on the request.

---

## 7. Minimal output architecture

This skill uses only three persistent theme-level outputs:

```text
outputs/themes/<theme_id>/theme_state.md
outputs/themes/<theme_id>/comparison_matrix.md
outputs/themes/<theme_id>/synthesis_report.md
```

Do not create separate long-running template outputs such as:

```text
interaction_log.md
reading_plan.md
supplementary_readings.md
gap_analysis.md
writing_notes.md
```

Instead:

* interaction log belongs inside `theme_state.md`
* reading plan belongs inside `theme_state.md`
* supplementary readings belong inside `theme_state.md` and summarized in `synthesis_report.md`
* gaps belong inside `synthesis_report.md`
* writing claims belong inside `synthesis_report.md`

This keeps the workflow compact and recoverable.

---

## 8. User-controlled theme and research question

Theme co-reading must be centered on the user’s own theme and research question.

The skill may clarify, restate, split, or operationalize the research question.

The skill must not silently decide the final research question for the user.

### 8.1 User input priority

Prioritize user-provided:

```text
core_theme
research_question
paper_list
expected_output
writing_goal
current_research_context
```

If the user provides both `core_theme` and `research_question`, use them as the authoritative framing.

If the user provides only a theme but not a research question, do not invent a final question.

Instead:

1. keep `research_question` empty or marked as `not_confirmed`
2. use quick-read evidence when available
3. if needed, hand provided papers off to quick read
4. propose exactly three provisional research question options
5. ask the user to confirm or revise the question before writing a formal synthesis report

Use this format:

```markdown
## 临时研究问题备选（provisional research question candidates）

1. ...
2. ...
3. ...

状态：provisional，等待用户确认。
```

Do not write a formal final report using an unconfirmed research question unless the user explicitly approves proceeding with a provisional question.

### 8.2 Research question status

Every theme session must track:

```text
research_question_status:
- confirmed
- provisional
- missing
- revised
```

A final synthesis report should use only a confirmed or explicitly user-approved research question.

If the report proceeds with a provisional question, mark the synthesis confidence as provisional.

---

## 9. Persistent theme state

Theme co-reading is a continuing workflow, not a one-shot report generator.

Users may repeatedly ask for:

```text
细节确认
术语确认
单篇论文追问
跨论文比较
补充文献搜索
研究问题修正
分类框架调整
阅读范围与优先级调整
写作 arc 调整
```

The skill must maintain and update:

```text
outputs/themes/<theme_id>/theme_state.md
```

### 9.1 Required theme state fields

The state file should maintain:

```text
theme_id
core_theme
research_question
research_question_status
writing_goal
paper_set
paper_roles
comparison_dimensions
field_lineage_status
supplementary_candidates
quick_read_handoffs
deep_read_handoffs
user_confirmed_decisions
user_interaction_focus
open_questions
evidence_status
synthesis_confidence
report_version
next_actions
```

### 9.2 Co-reading consensus and next actions

The state file must include:

```markdown
## 共读关键共识与后续决策（co-reading consensus and next actions）
```

It should record:

1. confirmed conclusions
2. confirmed user preferences
3. unresolved questions
4. hypotheses needing verification
5. supplementary reading plan
6. quick/deep read handoffs
7. next recommended actions

This ensures the user can re-enter the co-reading session later and quickly restore context.

---

## 10. User interaction focus and decision log

The state file and the synthesis report must include a concise section:

```markdown
## 用户交互重点与决策记录（user interaction focus and decision log）
```

This section records:

1. questions the user repeatedly asked
2. terms the user asked to clarify
3. research questions or categories the user confirmed
4. interpretations the user rejected or revised
5. comparison dimensions the user emphasized
6. papers the user decided to include or exclude
7. reading priority changes
8. unresolved issues
9. papers needing quick read or deep read

Use this format:

```markdown
| Interaction focus | User decision / preference | Impact on synthesis |
|---|---|---|
|  |  |  |
```

Do not omit this section in `synthesis_report.md`.

---

## 11. Co-reading focus modes

Before writing the output, determine `co_reading_focus`.

Allowed values:

```text
orientation
comparison
taxonomy
evaluation
field_lineage
writing_support
```

### 11.1 orientation

Use when the user is entering a new topic.

Focus:

* theme state
* research question status
* paper roles
* provisional dimensions
* reading gaps
* supplementary reading candidates

### 11.2 comparison

Use when the user wants structured comparison.

Focus:

* comparison dimensions
* comparison matrix
* paper roles
* evidence strength
* cross-paper synthesis

### 11.3 taxonomy

Use when the user wants a classification framework.

Focus:

* categories
* definitions
* boundaries
* representative papers
* missing categories
* whether taxonomy supports the user’s research question

### 11.4 evaluation

Use when the user cares about evaluation.

Focus:

* evaluation targets
* metrics
* human evaluation
* user studies
* benchmark design
* validity of metrics
* process-level or interaction-level evaluation gaps

### 11.5 field_lineage

Use when the user needs to understand whether the current paper set is complete enough.

Focus:

* prior work
* baseline work
* adjacent surveys
* benchmark / dataset papers
* follow-up works
* same-team visible lines
* missing field anchors
* supplementary reading recommendations

### 11.6 writing_support

Use when the output will support literature-review writing.

Focus:

* review arc
* taxonomy
* paragraph-level synthesis
* comparison dimensions
* claims that can be safely made
* citations and evidence boundaries
* risk of overclaiming

---

## 12. Inputs

Use available inputs when present:

```text
state/library_index.jsonl
state/reading_queue.json
state/approvals/
outputs/papers/<paper_key>/quick_read.md
outputs/papers/<paper_key>/deep_read.md
outputs/themes/<theme_id>/theme_state.md
outputs/themes/<theme_id>/comparison_matrix.md
outputs/themes/<theme_id>/synthesis_report.md
config/paths.toml
templates/theme_state.md
templates/comparison_matrix.md
templates/theme_synthesis.md
```

A paper set may be identified by:

1. user-provided paper keys
2. Zotero collection
3. Zotero tag
4. local folder
5. existing quick-read outputs
6. existing deep-read outputs
7. a user-provided bibliography
8. a search result list

If the paper set is ambiguous, report the ambiguity.

Do not invent paper identities.

---

## 13. Paper role labeling

The skill must label each paper’s role relative to the user-confirmed theme and research question.

Allowed paper roles:

```text
core_paper
baseline_paper
method_paper
survey_paper
evaluation_paper
dataset_or_benchmark_paper
system_paper
theory_or_framework_paper
background_paper
adjacent_paper
candidate_supplementary_paper
uncertain
```

Do not label paper roles only by paper type.

A survey paper may be a `core_paper`.

A method paper may be only a `background_paper`.

Each role must include a reason.

Use this table:

```markdown
| Paper | Role | Why this role | Relation to research question | Evidence status |
|---|---|---|---|---|
|  |  |  |  |  |
```

If a role is uncertain, write:

```text
该论文角色尚不明确，需要 quick read 或用户确认。
```

---

## 14. Evidence requirements

Theme-level claims require evidence.

For every major synthesis claim, identify its basis:

```text
based on deep_read reports
based on quick_read cards
based on metadata / abstract only
based on external search
based on local inference
based on comparison matrix
based on author-stated claims
based on supported inference
based on assistant critical judgment
```

When citing paper-specific content, use the most precise available location.

Preferred citation format:

```text
（文件名：xxx.pdf，第 x 页）
```

If page numbers are unavailable, write:

```text
页码未能可靠识别。
```

If a comparison depends on external citation search or web search and it was not performed, write:

```text
该比较需要外部检索确认；当前仅基于本地论文和 Zotero 索引判断。
```

Do not convert uncertain relations into confirmed claims.

---

## 15. Evidence level and synthesis confidence

Every synthesis report must include:

```markdown
## 证据等级与综合置信度（evidence level and synthesis confidence）
```

Distinguish:

```text
based on deep_read reports
based on quick_read cards
based on metadata / abstract only
based on external search
based on local inference
```

Use this table:

```markdown
| Evidence source | Papers / claims supported | Confidence | Limitation |
|---|---|---|---|
| deep_read reports |  | high / medium / low |  |
| quick_read cards |  | high / medium / low |  |
| metadata / abstract only |  | high / medium / low |  |
| external search |  | high / medium / low |  |
| local inference |  | high / medium / low |  |
```

If core papers lack deep-read reports, mark theme-level synthesis confidence as limited.

---

## 16. Comparison matrix

The comparison matrix is the evidence base for synthesis.

Maintain:

```text
outputs/themes/<theme_id>/comparison_matrix.md
```

Default dimensions for research-article clusters:

```text
paper role
research problem
task formulation
input / output
method paradigm
data and representation
evaluation metrics
datasets / benchmarks
baselines
human evaluation or user study
limitations
claim-evidence alignment
relation to user research
evidence strength
```

Default dimensions for survey clusters:

```text
paper role
survey scope
inclusion / exclusion boundary
organizing perspective
taxonomy
coverage
relation to adjacent surveys
challenges
future directions
transferable review structure
evidence strength
```

Default dimensions for mixed clusters:

```text
paper role
problem / scope
task or taxonomy
method or organizing perspective
evaluation or evidence standard
contribution to theme
limitations
transferable insight
evidence strength
```

Adapt dimensions to the user’s confirmed research question.

Mark unknown values as:

```text
文中未说明。
```

or:

```text
证据不足。
```

Do not fill empty cells by guessing.

---

## 17. Field lineage tracing

Users often do not know all key papers when starting co-reading.

Therefore, this skill must perform field lineage tracing based on the user’s confirmed theme, research question, and provided paper set.

This is not free-form recommendation.

It is evidence-chain expansion.

### 17.1 Field lineage tracing goals

Field lineage tracing should answer:

1. What key prior works precede this paper set?
2. What baselines do these papers commonly rely on?
3. Which surveys or taxonomies define the field?
4. Which follow-up works developed these papers?
5. Which adjacent directions may be missing?
6. Is the current paper set sufficient to support the research question?

### 17.2 Tracing paths

Use this priority order:

```text
1. references in user-provided papers
2. related work sections in user-provided papers
3. baseline tables and comparison sections
4. cited-by / follow-up works if externally available
5. same-team prior / follow-up works
6. adjacent surveys
7. benchmark / dataset papers
8. recent papers using the same task, metric, dataset, or system framing
```

### 17.3 Candidate confidence levels

Every lineage relation or supplementary reading candidate must be assigned one confidence level:

```text
confirmed
likely
candidate
unverified
```

Definitions:

```text
confirmed
Verified by DOI, author ID, citation database, paper metadata, explicit citation, or user-confirmed evidence.

likely
Strong evidence from shared authors, shared task, shared method, shared dataset, shared metric, or repeated citation pattern, but not fully verified.

candidate
Potentially related based on title, keywords, local context, or weak citation clues.

unverified
Needs external search before being treated as related work.
```

Do not present `candidate` or `unverified` works as field anchors.

Store field lineage notes and supplementary candidates in:

```text
outputs/themes/<theme_id>/theme_state.md
```

Summarize confirmed or high-value items in:

```text
outputs/themes/<theme_id>/synthesis_report.md
```

---

## 18. Supplementary reading recommendations

The skill must recommend supplementary readings when the current paper set appears incomplete.

Supplementary recommendations should be grounded in:

1. missing prior work
2. missing baseline
3. missing survey or taxonomy
4. missing evaluation paper
5. missing dataset or benchmark paper
6. missing follow-up work
7. missing adjacent direction
8. user’s interaction focus

Each candidate must be marked with evidence and confidence.

Use this table:

```markdown
| Candidate paper | Year | Why recommended | Relation to current set | Suggested action | Confidence |
|---|---:|---|---|---|---|
|  |  |  |  | quick_read / deep_read_candidate / optional / verify_first | confirmed / likely / candidate / unverified |
```

Allowed `suggested_action` values:

```text
quick_read
deep_read_candidate
optional
verify_first
exclude_for_now
```

If external search is unavailable, write:

```text
补充文献推荐需要外部检索确认；当前仅基于本地 PDF、references、baseline 与 Zotero 索引进行有限判断。
```

Store detailed recommendations in `theme_state.md`.

Summarize only the most important recommendations in `synthesis_report.md`.

---

## 19. Quick read and deep read handoff

Theme co-reading may hand off papers to single-paper reading skills.

The co-reading skill decides what evidence is missing and records the handoff.

It does not duplicate full quick-read or deep-read logic.

### 19.1 When to hand off to quick read

Use or invoke:

```text
single-paper-quick-read
```

when:

1. a supplementary candidate has not been read
2. the goal is only to decide whether to include a paper
3. a paper’s role is unclear
4. the skill needs to know whether a paper is a baseline, survey, background, or core work
5. a paper is only used to expand the literature pool

Record in `theme_state.md`:

```markdown
| Paper | Reason for quick read | Expected decision |
|---|---|---|
|  |  | include / exclude / deep_read_candidate |
```

### 19.2 When to hand off to deep read

Use or invoke:

```text
single-paper-deep-read
```

when:

1. the paper is a `core_paper`
2. the paper is a key baseline
3. the paper determines the taxonomy or research arc
4. the user repeatedly asks about details in this paper
5. the paper conflicts with another paper in a way that affects synthesis
6. the paper’s claim-evidence or scope-taxonomy judgment affects the theme conclusion
7. the paper has not been deep-read but its importance reaches the threshold for deep reading

Record in `theme_state.md`:

```markdown
| Paper | Reason for deep read | Suggested report mode | Expected contribution to co-reading |
|---|---|---|---|
|  |  | full_report / compact_report |  |
```

### 19.3 Co-reading does not replace deep read

Co-reading can reference deep-read reports.

Co-reading should not rewrite a full single-paper deep-read report inside the theme synthesis.

If a key paper lacks a necessary deep-read report, write:

```text
该论文可能影响主题综合结论，但尚缺少 deep_read 报告；当前综合结论需标记为低置信度。
```

---

## 20. Workflow

### Step 1. Start or restore the session

Identify or create:

```text
theme_id
core_theme
research_question
research_question_status
paper_set
expected_output
writing_goal
existing_theme_state
```

If `theme_state.md` exists, read it first.

Do not restart the session from scratch unless the user asks.

### Step 2. Confirm user-controlled theme and research question

Use the user’s confirmed research question when available.

If no confirmed research question exists:

1. preserve the theme
2. read available quick-read or deep-read outputs
3. if needed, hand papers off to quick read
4. propose three provisional research question candidates
5. mark the state as `research_question_status: provisional`

Do not write final synthesis until the research question is confirmed or explicitly approved as provisional.

### Step 3. Verify paper set and label roles

For each paper, identify:

```text
paper_key
title
authors
year
venue
paper_type
available_outputs
evidence_status
role_in_theme
needed_next_step
```

Allowed `needed_next_step` values:

```text
none
quick_read
deep_read_candidate
verify_metadata
verify_pdf
external_search
user_confirmation
```

### Step 4. Update interaction focus and decisions

Update the relevant section in `theme_state.md`.

Record:

```text
user questions
user corrections
confirmed decisions
rejected interpretations
updated comparison dimensions
reading priority changes
open questions
```

### Step 5. Determine comparison dimensions

Define comparison dimensions before writing synthesis.

Use the user-confirmed research question as the controlling logic.

### Step 6. Build or update the comparison matrix

Create or update:

```text
outputs/themes/<theme_id>/comparison_matrix.md
```

The matrix must include evidence strength.

Do not write synthesis from memory alone.

### Step 7. Trace field lineage and recommend supplementary readings

Use references, related work, baselines, adjacent surveys, datasets, benchmarks, follow-up works, and external search when available.

Store detailed lineage notes and recommendations in `theme_state.md`.

Summarize only important recommendations in `synthesis_report.md`.

### Step 8. Decide quick/deep read handoffs

Update handoff tables in `theme_state.md`.

Do not mark papers as `deep_read_approved`.

### Step 9. Write or update synthesis

Write or update:

```text
outputs/themes/<theme_id>/synthesis_report.md
```

Only after:

1. theme is clear
2. research question is confirmed or explicitly marked provisional
3. paper roles are labeled
4. comparison dimensions are defined
5. evidence status is stated
6. matrix is created or updated

Do not summarize papers one by one.

Use cross-paper claims such as:

```text
这组论文的共同转向是……
它们的关键差异在于……
A 和 B 都关注……，但 A 通过……，B 通过……
该方向的评价仍然集中在……，尚未充分覆盖……
```

### Step 10. Update co-reading consensus and next actions

At the end of each co-reading update, update:

```markdown
## 共读关键共识与后续决策（co-reading consensus and next actions）
```

in `theme_state.md`.

---

## 21. Synthesis report rules

The synthesis report must not be a list of isolated paper summaries.

It should include:

1. confirmed or explicitly provisional theme and research question
2. paper set boundary
3. paper roles
4. user interaction focus and decision log
5. comparison dimensions
6. reference to the comparison matrix
7. cross-paper synthesis
8. method, task, taxonomy, or evaluation evolution
9. field lineage tracing summary
10. supplementary reading recommendations
11. quick/deep read handoff summary
12. tensions and research gaps
13. review-writing claims
14. implications for the user’s research
15. evidence level and synthesis confidence
16. co-reading consensus and next actions

---

## 22. Tensions and gaps

Theme-level reading should identify tensions, not only similarities.

Possible tension types:

```text
task tension
method tension
evaluation tension
dataset tension
interaction tension
theory-practice tension
claim-evidence tension
user-study validity tension
taxonomy tension
field-lineage tension
```

For each gap, state:

```text
gap
which papers reveal it
why it matters
whether it is directly usable for the user's research
what evidence supports it
what supplementary reading is needed
```

Avoid fake gaps.

A gap is valid only when it follows from comparison, evidence, or explicit uncertainty.

---

## 23. Review-writing claims

When co-reading supports literature-review writing, include:

```text
综述写作可用结论（review-writing claims）
```

Each claim should include:

```text
claim
supporting papers
evidence strength
safe wording
risk of overclaiming
```

Use this table:

```markdown
| Review-writing claim | Supporting papers | Evidence strength | Safe wording | Risk |
|---|---|---|---|---|
|  |  | strong / moderate / weak |  |  |
```

Do not write claims stronger than the paper set supports.

---

## 24. Implications for the user's research

The synthesis must include:

```text
对用户研究的启示（implications for the user's research）
```

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
3. what comparison dimensions are useful
4. what evaluation ideas are useful
5. what open problems the user could frame
6. how the cluster supports or challenges the user’s review arc

Avoid vague statements such as:

```text
这些论文对我的研究很有启发。
```

Prefer:

```text
这组论文共同说明，过程级生成任务不能只用最终图像质量评价；需要补充中间状态一致性、轨迹合理性和交互可用性等指标。
```

---

## 25. English-ready synthesis

When useful, include:

```text
英文写作与 oral 可用素材（English-ready synthesis）
```

This may include:

```text
key terms
possible English phrasing
one-slide takeaway
paragraph skeleton
oral explanation
```

For literature-review writing, include reusable English topic sentences.

Do not write a final English literature-review section unless the user asks.

---

## 26. Failure handling

If no theme is provided, write:

```text
缺少核心主题，无法进行主题共读。需要提供 core_theme 或论文集合所围绕的主题。
```

If no paper set is provided, write:

```text
缺少论文集合，无法进行主题共读。需要提供 paper keys、Zotero collection、Zotero tag 或论文列表。
```

If a theme is provided but no research question is confirmed, write:

```text
当前研究问题尚未确认。可以先基于已有文献 quick read 提出 3 个 provisional research question 备选。
```

If the paper set contains only one paper, write:

```text
当前只有一篇论文，不适合使用 theme-coreading。请改用 single-paper-quick-read 或 single-paper-deep-read。
```

If most papers lack quick-read or deep-read outputs, write:

```text
多数论文缺少基础阅读结果，建议先生成 quick-read card，再进行主题共读。
```

If comparison dimensions cannot be defined, write:

```text
当前主题或研究问题过于模糊，无法建立稳定比较维度。
```

If evidence is insufficient, write:

```text
证据不足，以下综合仅为低置信度初步判断。
```

If supplementary readings cannot be verified, write:

```text
补充文献推荐需要外部检索确认；当前不能可靠断言其为领域核心文献。
```

---

## 27. Completion criteria

This skill is complete when it produces or updates one of the following:

1. `theme_state.md`
2. `comparison_matrix.md`
3. `synthesis_report.md`
4. a clear explanation of why co-reading cannot proceed

A complete synthesis report must include:

1. confirmed or explicitly provisional theme and research question
2. paper set boundary
3. paper roles
4. user interaction focus and decision log
5. comparison dimensions
6. comparison matrix reference
7. cross-paper synthesis
8. field lineage tracing summary
9. supplementary reading recommendations
10. quick/deep read handoff summary
11. tensions and gaps
12. implications for the user's research
13. evidence level and synthesis confidence
14. co-reading consensus and next actions

The final output must not be a list of isolated paper summaries.
