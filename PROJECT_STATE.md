# Project State

## Current Identity

本项目是一个双入口的本地论文阅读工作流系统：

- Codex skills 负责执行阅读、精读、交互和主题综合等工作流。
- 本地 site 负责可视化、管理用户决策、审批、编辑与共读过程。

## Current Work Blocks

1. 工作流优化
2. 本地 site 开发
3. 治理层维护与设计收敛

## Current Consensus Snapshot

- Zotero 仍是只读的书目来源。
- 本仓库只保存派生工作流状态和输出。
- 本地 site 是 workflow console，不是独立数据库。
- Governance 是内部项目记忆层，不是普通用户可见的站点表面。
- Skill governance 保持轻量，关注接口和协作边界。
- Site governance 更重，因为它控制用户动作、状态 I/O 和 skill 调用。

## Current P0 Priorities

1. 设计并实现 workflow state validator。
2. 收敛 co-reading collection builder 的最小设计。
3. 收敛 add-paper-during-coreading 的工作流规则。

## Current Baseline

Governance layer bootstrap 已基本完备：`governance/` 已记录项目共识、决策索引、accepted decisions、open explorations、workflow 边界与开发优先级。后续治理工作以维护、漂移检查和设计收敛为主。

## Read Next

- `governance/README.md`
- `governance/project_consensus.md`
- `governance/development_priorities.md`
