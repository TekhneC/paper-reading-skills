# D0001 Dual-entry Local Reading System

Status: accepted
Date: 2026-06-24
Scope: project
Supersedes:
Superseded by:
Related: D0003, D0005

## Decision

本项目被定义为双入口的本地论文阅读工作流系统。Codex skills 是执行入口，负责 daily triage、quick read、formal deep read、deep-read interaction 与 theme co-reading 等工作。Local site 是管理入口，负责把队列、审批、编辑、共读状态和消息记录呈现给用户，并在必要时触发外部 Codex skill。

## Context

仓库已经同时包含 skill 定义、脚本、模板、状态、输出和本地网页。若不明确双入口关系，后续开发容易把 site 做成独立系统，或把 skill 做成不可见的后台细节。项目需要一个稳定模型，使人类开发者和 AI coding agent 能快速判断：哪些逻辑属于 skill，哪些交互属于 site，哪些状态必须落回仓库。

## Options Considered

一种方案是以 skills 为唯一入口，site 只做静态浏览器。另一种方案是以 site 为唯一入口，把 skill 逻辑重写为网页后端逻辑。第三种方案是保留双入口：skills 执行可复用工作流，site 管理用户动作和派生状态。

## Rationale

双入口方案最符合当前仓库形态。它保留 Codex skills 的可组合性，也让用户可以通过 site 看到状态、审批和阅读产物。该方案避免把阅读工作流完全埋入网页实现，同时也避免让用户只能通过命令或 skill 文档操作。

## Consequences

后续设计需要明确 skill-site interface。Site 可以触发 skills，但不应复制完整 skill 判断逻辑。Skills 可以生成输出，但需要满足 site 可读取的状态和产物约定。

## Boundary

本决策不改变 Zotero 只读边界，不建立独立数据库，也不定义每个 skill 的详细 procedure。
