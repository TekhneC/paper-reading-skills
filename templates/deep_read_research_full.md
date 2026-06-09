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
* Reading focus:
* Selected template: templates/deep_read_research_full.md

---

## 0. 核心结论先行（executive takeaway）

用 3–5 句话写出这篇论文最值得记住的抓手。

应回答：

1. 这篇论文最值得记住的一点是什么；
2. 它解决了什么问题；
3. 它的核心思路是什么；
4. 它的评估标尺是什么；
5. 它对用户研究的主要价值是什么。

注意：本节不是方法摘要，不展开复杂技术细节。

---

## 1. 研究动机（research motivation）

### 1.1 作者明确声称的问题

说明作者在文中如何定义问题，以及为什么认为该问题重要。

证据：

* （文件名：xxx.pdf，第 x 页）

### 1.2 已有工作的不足

说明论文认为此前方法、系统、数据、任务设定或评价方式有什么不足。

证据：

* （文件名：xxx.pdf，第 x 页）

### 1.3 我的判断

区分：

* 作者明确声称：
* 可由文本支持的推断：
* 我的判断：

---

## 2. 研究思路（research idea）

说明论文的核心洞察（central insight）。

应回答：

1. 作者为什么想到这个思路；
2. 它与前人方法的关键差异是什么；
3. 它依赖什么假设；
4. 为什么作者认为它会有效。

证据：

* （文件名：xxx.pdf，第 x 页）

---

## 3. 评估指标（evaluation metrics）

> 指标先行（metrics-first）：先理解论文如何定义“好”、如何评估、优化目标是什么，再进入方法机制。

### 3.1 评估目标

说明论文希望评估什么能力或效果。

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

### 3.3 人工评价、用户研究或定性评估（human evaluation / user study / qualitative evaluation）

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

说明这些指标是否真正支撑作者的核心 claim。

重点判断：

1. 指标是否覆盖论文真正关心的能力；
2. 指标是否只测最终结果而忽略过程；
3. 指标是否与用户体验或真实任务脱节；
4. 指标是否容易被投机优化；
5. 人评或用户研究是否足够支撑主张。

我的判断：

*

---

## 4. 研究方法（research method）

### 4.1 方法总览

用一段话解释整体 pipeline。

### 4.2 输入、输出与中间表示（input, output, and intermediate representation）

* Input:
* Output:
* Conditioning signals:
* Intermediate representation:
* Assumptions:

### 4.3 核心模块或机制（core components / mechanism）

| Component | Function | Evidence            |
| --------- | -------- | ------------------- |
|           |          | （文件名：xxx.pdf，第 x 页） |

### 4.4 训练目标、优化方式或系统流程（training objective / optimization / system workflow）

如适用，说明：

* Training objective:
* Loss function:
* Inference process:
* Interaction loop:
* System workflow:
* Implementation assumptions:

### 4.5 方法成立的关键假设

*

---

## 5. 实验设置与结果（experimental setup and results）

### 5.1 实验设置

* Dataset / material:
* Task:
* Baselines:
* Conditions:
* Evaluation protocol:
* Implementation details:
* Hardware / compute if reported:

证据：

* （文件名：xxx.pdf，第 x 页）

### 5.2 主结果

| Result | Evidence            | What it supports | What it does not prove |
| ------ | ------------------- | ---------------- | ---------------------- |
|        | （文件名：xxx.pdf，第 x 页） |                  |                        |

### 5.3 消融实验（ablation study）

| Ablation | Purpose | Finding | Evidence            |
| -------- | ------- | ------- | ------------------- |
|          |         |         | （文件名：xxx.pdf，第 x 页） |

### 5.4 定性结果、可视化或案例分析（qualitative results / visualization / case study）

*

### 5.5 失败案例与边界条件（failure cases / boundary conditions）

*

---

## 6. Claim-evidence 检查（claim-evidence alignment）

检查作者核心 claim 是否被实验、指标、消融、用户研究或定性结果支撑。

| Claim | Evidence            | Evidence strength                  | What it supports | What it does not prove |
| ----- | ------------------- | ---------------------------------- | ---------------- | ---------------------- |
|       | （文件名：xxx.pdf，第 x 页） | strong / moderate / weak / unclear |                  |                        |

重点检查：

1. claim 是否超出实验范围；
2. 指标是否真正衡量该 claim；
3. baseline 是否足够强；
4. ablation 是否证明关键模块有效；
5. 结果是否只在特定数据集或场景成立；
6. 定性展示是否被当成强证据；
7. 是否存在 overclaiming。

---

## 7. 讨论与不足（discussion and limitations）

### 7.1 作者承认的局限（author-stated limitations）

*

证据：

* （文件名：xxx.pdf，第 x 页）

### 7.2 我的补充判断（additional critical judgment）

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

### 7.3 对后续工作的影响

尤其针对 classic_paper，说明这些局限如何被后续工作继承、修正或绕开。

---

## 8. 谱系追踪（lineage tracing）

### 8.1 论文中明确引用的前序工作（paper-cited prior work）

| Work | Year | Relation to this paper | Evidence            |
| ---- | ---: | ---------------------- | ------------------- |
|      |      |                        | （文件名：xxx.pdf，第 x 页） |

### 8.2 如果是 classic_paper

重点追踪：

* prior work
* same-team prior work
* follow-up work
* same-team follow-up work
* representative citing works

| Work | Year | Relation                                                                | Evidence source | Confidence                                  |
| ---- | ---: | ----------------------------------------------------------------------- | --------------- | ------------------------------------------- |
|      |      | prior / same-team prior / follow-up / same-team follow-up / citing work |                 | confirmed / likely / candidate / unverified |

说明：

* 不强制新增“why it became classic”章节；
* 经典性判断可并入 executive takeaway 或 discussion；
* 审稿人视角不必过度展开，重点是客观局限及其对后续工作的影响。

### 8.3 如果是 new_paper

重点追踪：

* prior work
* same-team prior work
* baseline works
* closely related concurrent work

| Work | Year | Relation                                             | Evidence source | Confidence                                  |
| ---- | ---: | ---------------------------------------------------- | --------------- | ------------------------------------------- |
|      |      | prior / same-team prior / baseline / concurrent work |                 | confirmed / likely / candidate / unverified |

说明：

* 新论文不强制追踪 citing works；
* 如果是 preprint，应结合 preprint status 做更严格审稿式判断。

### 8.4 如果是 ordinary_research_article

追踪：

* key prior work
* key baseline work
* visible same-team work
* follow-up or citing work if relevant and verifiable

| Work | Year | Relation | Evidence source | Confidence                                  |
| ---- | ---: | -------- | --------------- | ------------------------------------------- |
|      |      |          |                 | confirmed / likely / candidate / unverified |

---

## 9. 团队研究线索（lightweight team research tracing）

本节只做轻量团队研究跟踪，不生成完整团队谱系。

### 9.1 核心作者线索（author and team signals）

* First author:
* Corresponding author:
* Senior / last author:
* Affiliation:
* Email domain:
* Lab / project page:
* ORCID / Semantic Scholar authorId / OpenAlex author ID:
* Evidence:

### 9.2 可能的同团队前序工作（candidate same-team prior work）

| Work | Year | Relation | Evidence | Confidence                                  |
| ---- | ---: | -------- | -------- | ------------------------------------------- |
|      |      |          |          | confirmed / likely / candidate / unverified |

### 9.3 可能的同团队后续工作（candidate same-team follow-up work）

| Work | Year | Relation | Evidence | Confidence                                  |
| ---- | ---: | -------- | -------- | ------------------------------------------- |
|      |      |          |          | confirmed / likely / candidate / unverified |

### 9.4 需要外部确认的线索（needs external verification）

*

---

## 10. 思辨视角一：审稿人视角的潜在不足（reviewer-style weaknesses）

根据 research_subtype 调整严格度：

* classic_paper：简要指出客观局限，重点说明后续工作如何回应；
* new_paper：严格检查 claim、baseline、metric、generalization、reproducibility；
* preprint：额外检查未发表状态带来的证据不稳定风险。

具体问题：

1.
2.
3.

---

## 11. 思辨视角二：同行研究者视角的后续研究方向（peer-researcher follow-up directions）

提出具体可延展方向。

| Direction | Responds to which limitation | How to extend this paper | Needed data / method / evaluation |
| --------- | ---------------------------- | ------------------------ | --------------------------------- |
|           |                              |                          |                                   |

---

## 12. 借鉴视角：对用户研究的可借鉴之处（transferable insights for the user’s research）

结合用户研究方向，说明：

### 12.1 可以借鉴什么

*

### 12.2 不能直接照搬什么

*

### 12.3 可转化为综述比较维度的内容

*

### 12.4 可转化为实验、评价或系统设计的内容

*

### 12.5 对用户当前研究 arc 的影响

*

---

## 13. 英文写作与 oral 可用素材（English-ready takeaways）

### 13.1 Key terms

| 中文术语 | English term |
| ---- | ------------ |
|      |              |

### 13.2 Possible English phrasing

* This paper addresses ...
* The key idea is ...
* The evaluation mainly measures ...
* The evidence supports ..., but does not prove ...
* This work is useful for my project because ...

### 13.3 One-slide takeaway

*
*
*

### 13.4 Oral explanation

用自然英文写一段 30–60 秒 oral 说明：

>