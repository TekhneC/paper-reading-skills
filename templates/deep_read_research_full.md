<!-- FILE: templates/deep_read_research_full.md -->

# Deep Read - <Paper Title>

## Metadata

* Paper key:
* Title:
* Authors:
* Year:
* Venue:
* Paper type: research_article
* Research subtype: classic_paper / new_paper / ordinary_research_article
* Report mode: full_report
* Preprint status: published version confirmed / accepted but not yet published / preprint only / status unknown / not applicable
* PDF path:
* Evidence status:
* Approval source:
* Quick-read source:
* Source cache:
* Text extraction mode:
* Page evidence status:
* Output date:
* Report path:
* JSON sidecar path:
* Reading focus:
* Selected template: templates/deep_read_research_full.md

---

## 1. 核心结论与阅读定位（executive takeaway）

用 3-5 句话说明这篇论文最值得记住的抓手。

应回答：

1. 这篇论文解决什么问题；
2. 核心思路是什么；
3. 它用什么评价标尺证明自己；
4. 证据最强与最弱的地方分别是什么；
5. 它对用户研究有什么可迁移价值。

阅读定位：

* 为什么进入 deep read：
* 本次阅读重点：
* 需要暂缓判断或外部验证的事项：


### Key figure / visual anchor

Embed the most important figure when available, preferably a model architecture, process diagram, workflow, scope diagram, or taxonomy overview.

```markdown
![Key figure: <short description>](<absolute local path to extracted figure image>)
```

Figure source:

* Figure / page:
* Markdown image path policy: use absolute local `crop_image_path` or `image_path`, wrapped in angle brackets; use repo-relative paths only when portable Markdown is explicitly requested.
* Why this is the key visual anchor:
* What it clarifies for the reader:
* Extraction reliability: rendered page / extracted image / caption-only / needs visual verification


---

## 2. 问题、动机与核心思路（problem, motivation, and central idea）

### 2.1 作者明确声称的问题

说明作者如何定义问题，以及为什么认为该问题重要。

证据：

* （文件名：xxx.pdf，第 x 页）

### 2.2 既有工作的不足

说明论文认为此前方法、系统、数据、任务设定或评价方式有什么不足。

证据：

* （文件名：xxx.pdf，第 x 页）

### 2.3 核心思路与关键假设

说明论文的 central insight、关键差异、依赖假设和预期优势。

* Central insight:
* Difference from prior work:
* Key assumptions:
* Why it should work:

### 2.4 证据支持度与问题成立性判断

区分：

* 作者明确声称：
* 可由文本支持的推断：
* 证据支持度与问题成立性判断：

---

## 3. 评价标尺与证据设计（evaluation metrics and evidence design）

> Metrics-first：先理解论文如何定义“好”、如何评价、优化目标是什么，再进入方法机制。

### 3.1 评价目标

说明论文希望评价什么能力或效果。

可包括：

* accuracy / performance
* generation quality
* process quality
* user satisfaction
* interaction efficiency
* robustness
* generalization
* interpretability
* ecological validity

### 3.2 数据集、benchmark 与指标

| Dataset / Benchmark | Metric | What it measures | Relation to claim | Limitation |
| ------------------- | ------ | ---------------- | ----------------- | ---------- |
|                     |        |                  |                   |            |

### 3.3 人工评价、用户研究或定性评价

如适用，说明：

* Participants:
* Task:
* Conditions:
* Measures:
* Qualitative coding:
* Interaction logs:
* Main findings:

证据：

* （文件名：xxx.pdf，第 x 页）

### 3.4 指标与研究目标的匹配度

重点判断：

1. 指标是否覆盖论文真正关心的能力；
2. 指标是否只测最终结果而忽略过程；
3. 指标是否与用户体验或真实任务脱节；
4. 指标是否容易被投机优化；
5. 人评或用户研究是否足够支持主张。

指标有效性与证据支持度判断：

*

---

## 4. 方法机制与实验结果（method, mechanism, and results）

### 4.1 方法总览

用一段话解释整体 pipeline。

### 4.2 输入、输出与中间表示

* Input:
* Output:
* Conditioning signals:
* Intermediate representation:
* Assumptions:

### 4.3 核心模块或机制

| Component | Function | Evidence |
| --------- | -------- | -------- |
|           |          | （文件名：xxx.pdf，第 x 页） |

### 4.4 训练目标、优化方式或系统流程

如适用，说明：

* Training objective:
* Loss function:
* Inference process:
* Interaction loop:
* System workflow:
* Implementation assumptions:

### 4.5 实验设置

* Dataset / material:
* Task:
* Baselines:
* Conditions:
* Evaluation protocol:
* Implementation details:
* Hardware / compute if reported:

证据：

* （文件名：xxx.pdf，第 x 页）

### 4.6 主要结果、消融与失败案例

| Result / Ablation / Case | Evidence | What it supports | What it does not prove |
| ------------------------ | -------- | ---------------- | ---------------------- |
|                          | （文件名：xxx.pdf，第 x 页） |                  |                        |

---

## 5. Claim-evidence 对齐与局限（alignment, discussion, and limitations）

### 5.1 Claim-evidence 检查

| Claim | Evidence | Evidence strength | What it supports | What it does not prove |
| ----- | -------- | ----------------- | ---------------- | ---------------------- |
|       | （文件名：xxx.pdf，第 x 页） | strong / moderate / weak / unclear |                  |                        |

重点检查：

1. claim 是否超出实验范围；
2. 指标是否真正衡量该 claim；
3. baseline 是否足够强；
4. ablation 是否证明关键模块有效；
5. 结果是否只在特定数据集或场景成立；
6. 定性展示是否被当成强证据；
7. 是否存在 overclaiming。

### 5.2 作者承认的局限

*

证据：

* （文件名：xxx.pdf，第 x 页）

### 5.3 证据缺口与迁移风险判断

从以下角度检查：

* task boundary
* dataset bias
* metric validity
* baseline fairness
* ablation sufficiency
* reproducibility
* generalization
* ecological validity
* user diversity
* failure cases
* ethical concerns

### 5.4 对后续工作的影响

尤其针对 classic_paper，说明这些局限如何被后续工作继承、修正或绕开。

---

## 6. 谱系、团队线索与外部验证（lineage, team signals, and verification）

### 6.1 论文中明确引用的前序工作

| Work | Year | Relation to this paper | Evidence |
| ---- | ---: | ---------------------- | -------- |
|      |      |                        | （文件名：xxx.pdf，第 x 页） |

### 6.2 按研究子类型调整追踪重点

* classic_paper：prior work、same-team prior work、follow-up work、same-team follow-up work、representative citing works。
* new_paper：prior work、same-team prior work、baseline works、closely related concurrent work。
* ordinary_research_article：key prior work、key baseline work、visible same-team work、relevant follow-up or citing work。

| Work | Year | Relation | Evidence source | Confidence |
| ---- | ---: | -------- | --------------- | ---------- |
|      |      |          |                 | confirmed / likely / candidate / unverified |

### 6.3 轻量团队研究线索

* First author:
* Corresponding author:
* Senior / last author:
* Affiliation:
* Email domain:
* Lab / project page:
* ORCID / Semantic Scholar authorId / OpenAlex author ID:
* Evidence:

### 6.4 需要外部确认的线索

*

---

## 7. 对用户研究的借鉴与后续方向（transferable insights and follow-up directions）

### 7.1 可以借鉴什么

*

### 7.2 不能直接照搬什么

*

### 7.3 可转化为综述比较维度的内容

*

### 7.4 可转化为实验、评价或系统设计的内容

*

### 7.5 审稿人视角的潜在追问

根据 research_subtype 调整严格度：

* classic_paper：简要指出客观局限，重点说明后续工作如何回应。
* new_paper：严格检查 claim、baseline、metric、generalization、reproducibility。
* preprint：额外检查未发表状态带来的证据不稳定风险。

具体问题：

1.
2.
3.

### 7.6 同行研究者视角的后续方向

| Direction | Responds to which limitation | How to extend this paper | Needed data / method / evaluation |
| --------- | ---------------------------- | ------------------------ | --------------------------------- |
|           |                              |                          |                                   |

---

## 8. 英文写作与 oral 可用素材（English-ready takeaways）

### 8.1 Key terms

| 中文术语 | English term |
| -------- | ------------ |
|          |              |

### 8.2 Possible English phrasing

* This paper addresses ...
* The key idea is ...
* The evaluation mainly measures ...
* The evidence supports ..., but does not prove ...
* This work is useful for my project because ...

### 8.3 One-slide takeaway

*
*
*

### 8.4 Oral explanation

用自然英文写一段 30-60 秒 oral 说明：

>
