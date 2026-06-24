# E0001 Co-reading Collection Builder

Status: open
Scope: site/workflow
Related decisions: D0001, D0003

## Question

用户应如何从已有 `deep_read_done` 文献中选择若干篇，形成 co-reading theme 或 collection？

## Current Context

Theme co-reading 的目标是比较与综合，而不是连续摘要。当前系统已有 deep-read papers、theme outputs 和 co-reading workspace，但尚未明确 collection builder 的最小交互与状态结构。

## Options

1. 只允许从 `deep_read_done` 文献中手动勾选创建 theme。
2. 允许从候选列表、标签或搜索结果中组合 collection。
3. 允许 Codex 根据研究问题推荐初始 collection，但由用户确认。

## Trade-offs

纯手动方案清晰、可审计，但对大文献库效率较低。搜索与标签方案更灵活，但需要更稳定的索引和过滤逻辑。Codex 推荐方案能降低启动成本，但必须避免把未确认文献直接纳入正式 theme。

## Current Leaning

先实现最小手动 builder：仅从已有 `deep_read_done` 文献中选择，创建或更新 theme collection。推荐与搜索能力可作为后续增强。

## What Would Decide This

需要明确 theme state 的最小字段、collection 与 Zotero collection 的关系，以及用户是否需要在创建 theme 时写入研究问题。

## Next Step

定义最小 theme collection state 草案，并检查 site 当前可读取的 deep-read paper metadata 是否足够支撑选择界面。
