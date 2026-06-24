# Project Consensus

## Project Identity

本项目是一个双入口的本地论文阅读工作流系统。

两个入口是：

1. Codex skills，用于执行阅读工作流。
2. Local site，用于可视化、管理、审批、编辑和 co-reading。

## Boundary with AGENTS.md

`AGENTS.md` 仍是 repository-level hard boundary。
本文档不重复 Zotero、state、output、script 或 evidence rules。

## Skill-Site Relationship

Skills 执行阅读和综合工作流。
Site 呈现用户动作，并管理 state/output interaction。

## Governance Relationship

Governance 是内部项目记忆层。
它不得作为普通 user-facing tab 出现在 local site 中。

## Current Non-goals

- 不构建独立数据库。
- 不修改 Zotero。
- 不将 Governance 暴露为普通用户页面。
- 不把 co-reading 变成 stateless chat。
- 不在 governance 文件中复制完整 skill procedures。
