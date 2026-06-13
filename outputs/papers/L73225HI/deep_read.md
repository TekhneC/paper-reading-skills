# Deep Read - Memory-V2V: Memory-Augmented Video-to-Video Diffusion for Consistent Multi-Turn Editing

## Metadata

* Paper key: L73225HI
* Title: Memory-V2V: Memory-Augmented Video-to-Video Diffusion for Consistent Multi-Turn Editing
* Authors: Dohun Lee; Chun-Hao Paul Huang; Xuelin Chen; Jong Chul Ye; Duygu Ceylan; Hyeonho Jeong
* Year: 2026
* Venue: arXiv preprint
* Paper type: research_article
* Research subtype: new_paper
* Report mode: full_report
* Preprint status: preprint only / status unknown
* PDF path: Zotero storage PDF, read-only
* Evidence status: page-level text, table candidates, figure candidates available
* Approval source: `state/approvals/L73225HI.json`
* Quick-read source: `outputs/papers/L73225HI/quick_read.md`; `outputs/papers/L73225HI/quick_read.json`
* Source cache: `state/cache/deep_read_sources/L73225HI/`
* Text extraction mode: `pdftotext` page-level flow/layout
* Page evidence status: page numbers available from extracted `pages.json`; table bodies require visual verification
* Output date: 2026-06-14
* Report path: `outputs/papers/L73225HI/deep_read.md`
* JSON sidecar path: `outputs/papers/L73225HI/deep_read.json`
* Reading focus: multi-turn editing, memory mechanism, consistency metrics, baseline design, ablation logic, process representation
* Selected template: `templates/deep_read_research_full.md`

---

## 1. 核心结论与阅读定位（executive takeaway）

这篇论文的关键抓手是：它把实际创作中的 iterative video editing 明确提出为 `multi-turn video editing`，核心难点是每一轮独立 denoising 后仍要保持 `cross-turn consistency`。Memory-V2V 的中心思路不是把历史结果当作连续视频上下文，而是把先前编辑结果存入 external memory，并作为后续生成的 structured constraints。证据最强的部分是问题定义、方法组件和两类任务上的实验/消融；相对较弱的是表格正文仍需视觉复核，且 preprint 状态未外部验证。对你的研究最有价值的是：它给“过程记忆如何约束后续生成”提供了一个可迁移的技术框架。

阅读定位：

* 为什么进入 deep read：它直接对应多轮生成、过程记忆、编辑历史保持和一致性控制。
* 本次阅读重点：task formulation、retrieval/tokenization/compression 机制、consistency evaluation、baseline/ablation、失败边界。
* 需要暂缓判断或外部验证的事项：正式发表状态、项目页视频结果、表格视觉核对和实现细节。

### Key figure / visual anchor

![Key figure: Memory-V2V framework](<C:\Users\tekhnec\.agents\paper-reading-skills\state\cache\deep_read_sources\L73225HI\figures\page_005_crop.png>)

Figure source:

* Figure / page: Fig. 2, page 5
* Why this is the key visual anchor: 它同时展示 external cache retrieval、dynamic tokenization 和 adaptive token merging，是整篇方法的核心结构。
* What it clarifies for the reader: 历史编辑不是简单拼进长上下文，而是先检索再按相关性分配 token 容量，最后压缩冗余 token。
* Extraction reliability: rendered page and cropped image available

---

## 2. 问题、动机与核心思路（problem, motivation, and central idea）

### 2.1 作者明确声称的问题

作者认为实际 video editing workflow 是迭代式的，用户会多轮修改结果；但现有 video-to-video diffusion models 往往把每一轮编辑当作独立任务，因此先前生成区域会漂移或被覆盖。作者将这一失败模式定义为 `cross-turn consistency` 问题，并把它放入 `multi-turn video editing` 的任务设定中。（文件名：Memory-V2V PDF，第 1-2 页）

### 2.2 既有工作的不足

论文指出 ReCamMaster 在 iterative novel view synthesis 中会让 novel-view regions 跨轮不一致；LucyEdit 在 long video editing 中能局部遵循 prompt，但全局外观会逐渐漂移，例如同一编辑对象在不同 segment 中表现不一致。（文件名：Memory-V2V PDF，第 2 页）

### 2.3 核心思路与关键假设

* Central insight: 多轮编辑需要 memory 作为 constraint mechanism，而不是作为 temporal continuation。
* Difference from prior work: 不使用所有历史编辑作为线性增长的上下文，而是进行 task-aware retrieval，只取 top-k relevant edits。
* Key assumptions: 当前编辑轮次只需要部分相关历史；相关性可以由任务特定信号定义，如 camera overlap 或 semantic similarity。
* Why it should work: 相关历史提供 consistency constraint，dynamic tokenization 给高相关历史更多容量，adaptive token merging 降低计算成本。（文件名：Memory-V2V PDF，第 2-5 页）

### 2.4 证据支持度与问题成立性判断

* 作者明确声称：multi-turn editing 是独立问题，关键难点是 independently denoised edits 之间的一致性。
* 可由文本支持的推断：该任务与创作流程中的“历史状态约束后续生成”高度同构。
* 判断：问题成立性较强，因为论文给出了明确 failure mode、任务形式、baseline 对照和两类应用任务。但其生态效度仍主要来自任务模拟和视频结果，不是用户研究。

---

## 3. 评价标尺与证据设计（evaluation metrics and evidence design）

### 3.1 评价目标

论文评价的核心不是单帧质量，而是多轮生成中的一致性与质量权衡：

* `cross-iteration consistency`
* camera adherence / camera accuracy
* visual quality
* long-video edited-object consistency
* computational overhead

### 3.2 数据集、benchmark 与指标

| Dataset / Benchmark | Metric | What it measures | Relation to claim | Limitation |
| --- | --- | --- | --- | --- |
| iterative video novel view synthesis on 40 public videos | MEt3R, VBench, rotation/translation errors | 跨视角几何一致性、视觉质量和 camera adherence | 支撑 multi-turn NVS consistency claim | 表格正文需视觉复核；任务仍是模拟迭代 |
| text-guided long video editing on 50 Señorita test videos | VBench, cross-frame DINO/CLIP similarity | subject/background/edited-object consistency 和视觉质量 | 支撑 long video editing consistency claim | 不是用户交互实验；指标可能不能覆盖创作者满意度 |
| computational cost analysis | FLOPs, latency | memory conditioning 的可扩展性 | 支撑 “without linear growth” | 依赖实现和硬件设置，外部复现需确认 |

证据：Table 2/3/4 captions and extracted table text（文件名：Memory-V2V PDF，第 10-11 页）；computational analysis（第 14 页）。

### 3.3 人工评价、用户研究或定性评价

未看到正式 user study。定性证据主要是多轮 novel view synthesis 和 long-video editing 的 qualitative comparisons，例如 Fig. 3、Fig. 5、Fig. 6、Fig. 17。（文件名：Memory-V2V PDF，第 7、10、13、25 页）

### 3.4 指标与研究目标的匹配度

指标与“多轮结果一致性”基本匹配，尤其 MEt3R、DINO/CLIP similarity 和 VBench 覆盖了几何/语义/视觉质量的不同侧面。但对交互式创作而言，它仍缺少过程级用户评价，例如用户是否更容易迭代、是否减少修正成本、是否提高可控性。对你的研究来说，这篇论文提供的是 process consistency 的技术评价框架，不是完整 creative workflow evaluation。

---

## 4. 方法机制与实验结果（method, mechanism, and results）

### 4.1 方法总览

Memory-V2V 在每次编辑后把输出视频的 latent representation 存入 external cache。下一轮编辑时，它根据任务相关性检索历史视频，把高相关历史以更高空间分辨率 tokenized，低相关历史更 aggressive compression；随后用 adaptive token merging 压缩低响应 token，避免计算随历史长度线性增长。（文件名：Memory-V2V PDF，第 5 页）

### 4.2 输入、输出与中间表示

* Input: 当前 source video、用户条件（text 或 camera pose）、历史 edited videos。
* Output: 当前轮 edited video。
* Conditioning signals: camera trajectory for NVS；source-video semantic similarity for long video editing。
* Intermediate representation: external cache 中的 latent videos；dynamic tokens；attention responsiveness for token merging。
* Assumptions: 历史编辑可以被检索为结构化约束；不同历史片段的相关性不同。

### 4.3 核心模块或机制

| Component | Function | Evidence |
| --- | --- | --- |
| External memory cache | 保存先前编辑输出，作为后续生成约束 | Fig. 2 and method overview（文件名：Memory-V2V PDF，第 5 页） |
| Task-aware retrieval | 为当前编辑轮次选择 top-k relevant prior videos | Introduction and Fig. 2（第 2、5 页） |
| FOV retrieval | 在 novel view synthesis 中用 camera overlap 排序历史 | Introduction / retrieval description（第 2-3 页） |
| Semantic segment retrieval | 在 text-guided long video editing 中按 source video 语义相似性检索 segment | Introduction（第 3 页） |
| Dynamic tokenization | 高相关视频保留更多细节，低相关视频压缩 | Fig. 2 caption（第 5 页） |
| Adaptive token merging | 基于 attention responsiveness 压缩冗余计算 | Fig. 2 caption and cost analysis（第 5、14 页） |

### 4.4 训练目标、优化方式或系统流程

论文使用 rectified flow matching loss 训练。NVS 部分从 ReCamMaster finetune，训练 self-attention layers、MLP projector、camera encoder 以及新增 tokenizers/compressors；训练时随机采样 1-6 个 memory videos，并随机启用 adaptive token merging。long video editing 部分基于 LucyEdit，并使用 Señorita-2M 过滤出的 56K samples，通过生成模型扩展 target videos 来构造 memory training data。训练在 32 A100 GPUs 上进行，总 batch size 32，1-2K finetuning steps 收敛。（文件名：Memory-V2V PDF，第 11 页；rectified flow details 第 15 页）

### 4.5 实验设置

* Dataset / material: 40 public videos for NVS；50 Señorita test videos for long video editing。
* Task: iterative video novel view synthesis；text-guided long video editing。
* Baselines: TrajCrafter、ReCamMaster Ind/AR、LucyEdit Ind/FIFO、TokenFlow、RAVE、CCEdit。
* Evaluation protocol: 多轮生成后比较跨轮一致性、视觉质量、camera error 和 long-video consistency。
* Implementation details: 32 A100 GPUs；rectified flow matching；memory videos randomly sampled during training。（文件名：Memory-V2V PDF，第 10-12 页）

### 4.6 主要结果、消融与失败案例

| Result / Ablation / Case | Evidence | What it supports | What it does not prove |
| --- | --- | --- | --- |
| Memory-V2V 在 NVS 中对三轮结果的 average consistency score 优于列出的 baselines | Table 2（文件名：Memory-V2V PDF，第 10 页） | 支持 cross-iteration consistency | 不证明所有视角/场景下都稳定 |
| Long video editing 中 Memory-V2V 多项指标优于 LucyEdit、TokenFlow、RAVE、CCEdit | Table 3（第 11 页） | 支持 long-sequence edited-object consistency | 不等于真实用户工作流更好 |
| Video retrieval 改善 consistency，adaptive token merging 降低计算成本 | Table 4 and ablation discussion（第 11-12 页） | 支持两个关键模块的必要性 | 表格视觉复核前不宜过度解读小数差异 |
| Adaptive merging 比直接丢弃 low-responsive tokens 更稳 | Discussion with Fig. 7/8（第 14 页） | 支持保留结构信息而非硬丢弃 | 机制解释仍依赖 attention responsiveness 分析 |
| 多 shot 大场景切换会失败 | Fig. 17 and discussion（第 25 页） | 界定方法边界 | 不说明所有 multi-shot 都不可处理 |

---

## 5. Claim-evidence 对齐与局限（alignment, discussion, and limitations）

### 5.1 Claim-evidence 检查

| Claim | Evidence | Evidence strength | What it supports | What it does not prove |
| --- | --- | --- | --- | --- |
| Multi-turn editing 是独立一致性问题 | Introduction failure examples and task formulation（第 1-3 页） | strong | 任务设定清楚，failure mode 合理 | 不证明这是用户最重要的问题 |
| Memory as structured constraints 比 naive history/context 更合适 | Method design and Fig. 2（第 2、5 页） | moderate | 支持设计动机 | 不证明所有 memory designs 都应如此 |
| Memory-V2V 提高跨轮一致性且保持质量 | Tables 2/3 and qualitative figures（第 10-12 页） | moderate-to-strong | 支持在两个任务上的有效性 | 表格需视觉复核；任务范围有限 |
| Adaptive token merging 降低开销 | computational cost analysis（第 14 页） | moderate | 支持 scalable conditioning | 不保证所有硬件/实现都有同等收益 |

### 5.2 作者承认的局限

作者承认 Memory-V2V 继承 underlying single-turn editing model 的限制，例如 large view changes；由于训练数据是 continuous single-shot videos，方法可能难以处理包含 abrupt scene transitions 的 multi-shot long videos。（文件名：Memory-V2V PDF，第 14、25 页）

### 5.3 证据缺口与迁移风险判断

* task boundary: 两类视频任务清楚，但数字绘画过程生成需要重新定义状态和历史相似性。
* metric validity: 一致性指标较强，用户可控性/创作满意度缺失。
* baseline fairness: baseline 覆盖较广，但实现细节和参数需复核。
* ablation sufficiency: retrieval 和 token merging 有消融，但表格细节需要视觉核对。
* generalization: multi-shot failure 表明真实长视频/复杂创作场景仍有风险。
* ecological validity: 没有真实用户多轮编辑 study。

### 5.4 对后续工作的影响

这篇论文可作为“memory-augmented iterative generation”的近期代表。后续工作可以沿着三条线扩展：更复杂的历史状态表示、更贴近真实创作交互的评价、更能处理场景切换或大幅编辑的 memory selection。

---

## 6. 谱系、团队线索与外部验证（lineage, team signals, and verification）

### 6.1 论文中明确引用的前序工作

| Work | Year | Relation to this paper | Evidence |
| --- | ---: | --- | --- |
| ReCamMaster | 2025/2026 unknown | base model / NVS baseline | Introduction and experiments（第 2、11-12 页） |
| LucyEdit | 2025/2026 unknown | base model / long video editing baseline | Introduction and experiments（第 2、11-12 页） |
| TrajectoryCrafter | unknown | NVS baseline | Table 2 and experiment setup（第 10-12 页） |
| TokenFlow | unknown | temporal consistency baseline | long video editing setup（第 12 页） |
| RAVE | unknown | consistent video editing baseline | long video editing setup（第 12 页） |
| CCEdit | unknown | keyframe guidance baseline | long video editing setup（第 12 页） |

### 6.2 按研究子类型调整追踪重点

| Work | Year | Relation | Evidence source | Confidence |
| --- | ---: | --- | --- | --- |
| ReCamMaster | unknown | key prior/base model for NVS | paper text | confirmed as cited |
| LucyEdit | unknown | key prior/base model for text-guided editing | paper text | confirmed as cited |
| long-video memory/context methods | unknown | contrast class; temporal continuation differs from constraint memory | paper text | likely |
| diffusion distillation / autoregressive generation frameworks | unknown | future direction for interactivity | limitations discussion（第 25 页） | candidate |

### 6.3 轻量团队研究线索

* First author: Dohun Lee
* Project/lab context: Adobe Research, KAIST AI
* Project page: `https://dohunlee1.github.io/MemoryV2V/`
* Evidence: title page（文件名：Memory-V2V PDF，第 1 页）

### 6.4 需要外部确认的线索

* arXiv v2 是否为最新版本。
* 是否已被会议/期刊接收。
* ReCamMaster、LucyEdit、TokenFlow、RAVE、CCEdit 的具体发表年份和官方实现。
* 项目页视频结果与论文定性 claim 是否一致。

---

## 7. 对用户研究的借鉴与后续方向（transferable insights and follow-up directions）

### 7.1 可以借鉴什么

* 把创作过程定义为 multi-turn generation，而非一次性 generation。
* 把历史状态作为 structured constraints，用于约束后续生成。
* 用 task-aware retrieval 选择相关历史，而不是全量上下文堆叠。
* 用 relevance-aware capacity allocation 解决历史信息多但预算有限的问题。
* 在评价中区分 final visual quality 和 process consistency。

### 7.2 不能直接照搬什么

* 视频 latent memory 不能直接对应绘画过程中的 stroke、layer、mask 或 semantic edit state。
* camera overlap / source-video semantic similarity 不一定适用于数字绘画，需要重新定义历史相关性。
* VBench、MEt3R、DINO/CLIP similarity 不能覆盖绘画过程的可控性、意图保持和用户满意度。

### 7.3 可转化为综述比较维度的内容

* history representation
* retrieval criterion
* memory compression
* consistency metric
* failure under distribution shift
* process vs final-output evaluation

### 7.4 可转化为实验、评价或系统设计的内容

* 设计 multi-turn drawing/editing benchmark，要求模型在多轮中保持先前局部编辑。
* 记录中间状态并检索相关历史步骤，作为后续生成 constraint。
* 增加 process consistency metrics，如局部状态保持、编辑意图不冲突、跨轮引用准确性。

### 7.5 审稿人视角的潜在追问

1. cross-turn consistency 指标是否覆盖真实用户关心的一致性？
2. baseline 是否在相同历史信息预算和相同推理成本下比较？
3. adaptive token merging 的收益是否依赖特定 transformer block 或 attention pattern？
4. 多 shot failure 是否说明 memory retrieval 缺乏 scene-boundary awareness？

### 7.6 同行研究者视角的后续方向

| Direction | Responds to which limitation | How to extend this paper | Needed data / method / evaluation |
| --- | --- | --- | --- |
| Scene-aware memory retrieval | multi-shot failure | 检测 scene boundary，再按 shot/context 选择 memory | multi-shot long-video data, scene-transition metrics |
| Creative process memory for drawing | video-specific latent memory | 将 stroke/layer/history graph 编码为 memory constraints | drawing process datasets, process consistency metrics |
| User-in-the-loop consistency evaluation | no user study | 让用户多轮编辑并评价修正成本和满意度 | interaction logs, task completion, subjective ratings |

---

## 8. 英文写作与 oral 可用素材（English-ready takeaways）

### 8.1 Key terms

| 中文术语 | English term |
| --- | --- |
| 多轮视频编辑 | multi-turn video editing |
| 跨轮一致性 | cross-turn consistency |
| 外部记忆缓存 | external memory cache |
| 任务感知检索 | task-aware retrieval |
| 动态 token 化 | dynamic tokenization |
| 自适应 token 合并 | adaptive token merging |
| 过程一致性 | process consistency |

### 8.2 Possible English phrasing

* This paper reframes iterative video editing as a multi-turn consistency problem rather than a sequence of independent single-turn edits.
* The key idea is to treat previous edits as structured constraints, not merely as additional temporal context.
* The evaluation mainly measures cross-iteration consistency, camera adherence, visual quality, and computational overhead.
* The evidence supports the usefulness of retrieval and adaptive compression, but it does not yet prove effectiveness in real user-facing creative workflows.
* This work is useful for my project because it offers a concrete mechanism for using process memory to constrain future generations.

### 8.3 One-slide takeaway

* Memory-V2V turns editing history into constraints for future generations.
* Its main technical recipe is retrieval + relevance-aware tokenization + adaptive compression.
* For process-generation research, it suggests evaluating not only final quality but also cross-turn state consistency.

### 8.4 Oral explanation

> Memory-V2V is useful because it makes iterative editing a first-class problem. Instead of treating each edit independently, it stores previous outputs in an external memory and retrieves the most relevant ones to constrain the next generation. This is especially relevant to process-level generation, where the history of intermediate states should shape future outputs. The main limitation is that the paper evaluates consistency mostly through video metrics and qualitative examples, so its implications for interactive creative workflows still need user-centered evaluation.
