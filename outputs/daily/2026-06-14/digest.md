# Daily Paper Reading Digest - 2026-06-14

Daily run directory: `outputs/daily/2026-06-14/`

## 1. 今日阅读概览

- Queue source: `state/reading_queue.json` from Zotero tag `todo`
- Queue size: 2
- Quick-read available: 2 / 2
- Needs quick read: 0
- Recommended deep-reading candidates: 2

本轮调用 `daily-paper-triage`，基于已有 canonical quick-read outputs 聚合判断；没有生成正式精读报告，也没有写入 approval。

## 2. 今日论文分诊表

| Paper key | Title | Quick-read status | Recommended action | Evidence | Uncertainty |
| --- | --- | --- | --- | --- | --- |
| L73225HI | Memory-V2V: Memory-Augmented Video-to-Video Diffusion for Consistent Multi-Turn Editing | available | deep_read_candidate | PDF text cache: flow/layout | 定量表格、ablation、计算开销和 consistency metrics 需要精读核对 |
| RZVWJTDS | PersonaVLM: Long-Term Personalized Multimodal LLMs | available | deep_read_candidate | PDF text cache: flow/layout | benchmark 构造、ablation、完整 baseline 表格和生态效度需要精读确认 |

## 3. 单篇快读摘要

### L73225HI - Memory-V2V: Memory-Augmented Video-to-Video Diffusion for Consistent Multi-Turn Editing

- One-sentence summary: 该文将多轮视频编辑定义为 cross-turn consistency 问题，并用外部 memory cache、task-aware retrieval、dynamic tokenization 和 adaptive token merging 约束后续生成。
- Relation to current research: 与数字内容生成的过程级建模、迭代编辑、历史状态保持和创作过程一致性高度相关。
- Evidence source: `state/cache/quick_read_sources/L73225HI.flow.txt`; `state/cache/quick_read_sources/L73225HI.layout.txt`
- Evidence location: PDF text cache, no reliable page map

### RZVWJTDS - PersonaVLM: Long-Term Personalized Multimodal LLMs

- One-sentence summary: 该文将长期个性化 MLLM 建模为 remembering、reasoning 和 response alignment 的组合问题，并提出 PersonaVLM 与 Persona-MME benchmark。
- Relation to current research: 不直接研究绘画过程生成，但对 human-AI co-creation 中的长期用户建模、偏好演化和交互评价有参考价值。
- Evidence source: `state/cache/quick_read_sources/RZVWJTDS.flow.txt`; `state/cache/quick_read_sources/RZVWJTDS.layout.txt`
- Evidence location: PDF text cache, no reliable page map

## 4. 推荐精读候选

| Rank | Paper key | Title | Decision label | Suggested deep-read focus | Risk or uncertainty |
| --- | --- | --- | --- | --- | --- |
| 1 | L73225HI | Memory-V2V: Memory-Augmented Video-to-Video Diffusion for Consistent Multi-Turn Editing | strong_candidate | task formulation; method mechanism; evaluation metrics; baseline design; ablation logic; process representation | 精确实验数值、ablation 贡献、token budget、retrieval top-k 和失败案例需要正式精读 |
| 2 | RZVWJTDS | PersonaVLM: Long-Term Personalized Multimodal LLMs | candidate | task formulation; method mechanism; evaluation metrics; process representation; interaction design; ecological validity | benchmark 数据合成、人格更新机制、baseline 表格和真实交互有效性需要正式精读 |

## 5. 推荐理由矩阵

Use qualitative ratings: `high`, `medium`, `low`, or `unknown`.

| Paper key | Research fit | Literature-review value | Task formulation | Method mechanism | Evaluation metrics | Baseline / comparison | Ablation logic | Process / interaction relevance | Novel framing | Evidence confidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| L73225HI | high | high | high | high | medium | high | medium | high | high | medium |
| RZVWJTDS | medium | high | high | medium | high | medium | unknown | high | high | medium |

### 高分项目及原因

#### L73225HI - Memory-V2V: Memory-Augmented Video-to-Video Diffusion for Consistent Multi-Turn Editing

- High-rated dimensions:
  - `research_fit`: 直接研究 iterative generative editing 与 cross-turn consistency，贴近过程级生成和编辑 workflow。
  - `task_formulation`: 明确将 multi-turn video editing 定义为先前编辑约束后续生成的问题。
  - `method_mechanism`: task-aware retrieval、dynamic tokenization 和 adaptive token merging 给出了可迁移的过程记忆机制。
  - `baseline_comparison`: 与 ReCamMaster、LucyEdit 和 long-video memory/context methods 形成清晰对照。
  - `process_interaction_relevance`: 将编辑视为多轮过程，而非单次独立生成。
- Why this matters for current research: 它可以作为“过程记忆如何约束后续生成”的核心技术参照。
- Evidence source: canonical quick-read JSON/Markdown and PDF text cache.
- Evidence location: PDF text cache, no reliable page map.
- Remaining uncertainty: 定量表格、ablation、计算开销和失败案例需要 deep reading。

#### RZVWJTDS - PersonaVLM: Long-Term Personalized Multimodal LLMs

- High-rated dimensions:
  - `literature_review_value`: 将长期 multimodal personalization 组织为 memory、reasoning 和 response alignment 的组合问题。
  - `task_formulation`: 强调用户偏好和 personality 在多轮交互中演化。
  - `evaluation_metrics`: Persona-MME 提供多维 evaluation framework，可用于比较个性化系统评价。
  - `process_interaction_relevance`: 关注 multi-turn interaction、memory updates 和 evolving preference。
  - `novel_framing`: 将 proactive remembering、multi-step reasoning 和 response alignment 串成 personalized MLLM agent 能力。
- Why this matters for current research: 它可支持 human-AI co-creation 中长期用户状态建模和个性化评价维度。
- Evidence source: canonical quick-read JSON/Markdown and PDF text cache.
- Evidence location: PDF text cache, no reliable page map.
- Remaining uncertainty: benchmark 构造、人格更新、ablation 和 baseline 表格需要 deep reading。

## 6. 需要确认的事项

- [ ] 是否批准 `L73225HI` 进入正式精读？
- [ ] 是否批准 `RZVWJTDS` 进入正式精读？
- [ ] 是否将两篇已有 quick-read 的论文记录为 `queued -> quick_read_done`？
- [ ] 是否将两篇候选记录为 `quick_read_done -> deep_read_candidate`？
- [ ] 是否需要围绕“过程记忆与多轮生成一致性”启动 `theme-coreading`？

## 7. 建议状态更新

```text
RZVWJTDS: queued -> quick_read_done
RZVWJTDS: quick_read_done -> deep_read_candidate
L73225HI: queued -> quick_read_done
L73225HI: quick_read_done -> deep_read_candidate
```

以上只是建议状态更新；本次未写入 `state/processed_papers.json`，也未创建 deep-read approval。

## 8. Approval block

建议进入精读：

- [ ] L73225HI — Memory-V2V: Memory-Augmented Video-to-Video Diffusion for Consistent Multi-Turn Editing
  - 推荐理由：最贴近过程级生成、多轮编辑、历史状态记忆和一致性控制。
  - 建议精读重点：multi-turn editing task formulation; memory mechanism; consistency metrics; baseline and ablation design.
  - 不确定点：定量指标、模块贡献、token budget 和失败案例。

- [ ] RZVWJTDS — PersonaVLM: Long-Term Personalized Multimodal LLMs
  - 推荐理由：适合作为长期个性化 MLLM、用户状态建模和交互评价的候选文献。
  - 建议精读重点：long-term personalization task; memory/personality update; Persona-MME benchmark; ecological validity.
  - 不确定点：benchmark 构造、真实交互有效性、ablation 和 baseline 公平性。

建议暂不精读：

- 当前无。
