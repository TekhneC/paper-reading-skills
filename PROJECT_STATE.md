# Project State

## Current Identity

本项目是一个双入口的本地论文阅读工作流系统：

- Codex skills 负责执行阅读、精读、交互和主题综合等工作流。
- 本地 site 负责可视化、管理用户决策、审批、编辑与共读过程。

## Current Work Blocks

1. 工作流优化
2. 本地 site 开发
3. 治理层设计

## Current Consensus Snapshot

- Zotero 仍是只读的书目来源。
- 本仓库只保存派生工作流状态和输出。
- 本地 site 是 workflow console，不是独立数据库。
- Governance 是内部项目记忆层，不是普通用户可见的站点表面。
- Skill governance 保持轻量，关注接口和协作边界。
- Site governance 更重，因为它控制用户动作、状态 I/O 和 skill 调用。

## Current P0 Priorities

1. 在 `/governance` 下新增治理层。
2. 将 `site/DESIGN_DECISIONS.md` 停用为主设计决策容器。
3. 澄清主阅读工作流和 site-mediated workflow。
4. 将 collection builder 和 add-paper-during-coreading 定义为 exploration。
5. 准备 workflow state validator exploration。

## Read Next

- `governance/README.md`
- `governance/project_consensus.md`
- `governance/development_priorities.md`
