# D0005 Approval Gate Before Formal Deep Read

Status: accepted
Date: 2026-06-24
Scope: workflow
Supersedes:
Superseded by:
Related: D0001, E0003

## Decision

Formal deep read 必须经过用户 approval。Daily 和 quick read 可以推荐 deep-read candidates，但不得直接生成正式精读报告。只有在用户明确批准，或存在有效 approval record 时，系统才可以进入 formal deep read。

## Context

本项目区分 quick read 与 deep read。Quick read 服务 triage，目标是帮助用户判断是否值得投入更高阅读成本。Formal deep read 会生成更完整的分析产物，并可能进入后续 deep-read interaction 和 co-reading。因此，它应代表用户的明确研究选择，而不是自动批处理结果。

## Options Considered

一种方案是 daily triage 自动对高分论文执行 deep read。另一种方案是完全手动，不允许 site 或 skill 推荐候选。第三种方案是允许系统推荐候选，但在 formal deep read 前设置 approval gate。

## Rationale

Approval gate 保留用户判断权，同时允许系统承担筛选和推荐工作。它也让 state transitions 更可审计：`deep_read_candidate` 与 `deep_read_approved` 有明确差异，`deep_read_done` 需要真实报告产物支撑。

## Consequences

Site 可以提供 approval 操作，并在 approval 后触发 deep read。未来仍需探索 approval 与 run deep read 是否应拆分为两个动作，但无论是否拆分，正式精读都不能绕过 approval。

## Boundary

本决策不规定 approval UI 的具体形态，也不规定 deep read 的报告模板。它只固定 formal deep read 的前置条件。
