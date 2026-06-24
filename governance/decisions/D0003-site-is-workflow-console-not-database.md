# D0003 Site Is Workflow Console, Not Database

Status: accepted
Date: 2026-06-24
Scope: site
Supersedes:
Superseded by:
Related: D0001, D0004

## Decision

Local site 被定义为 workflow console，不建立独立数据库，不替代 Zotero，也不成为新的 bibliographic source。Site 读取和写入仓库内派生状态与输出，用于呈现用户决策、审批、编辑、共读和 skill invocation 结果。

## Context

本项目已有 Zotero 作为书目来源，也已有 `state/` 与 `outputs/` 保存派生工作流数据。Site 的价值在于把这些数据组织为可操作界面。如果 site 引入独立数据库，系统将出现多个事实来源，增加同步、迁移和冲突处理成本，并可能模糊 Zotero 与仓库的边界。

## Options Considered

一种方案是让 site 后端维护完整数据库，集中管理 papers、状态和消息。另一种方案是让 site 完全只读。第三种方案是让 site 写入 repository-local derived artifacts，并把 Zotero 保持为只读来源。

## Rationale

第三种方案与当前项目边界一致。它允许 site 提供审批、编辑、消息和状态更新等必要操作，同时避免引入新的长期数据层。仓库中的 JSON、JSONL 和 Markdown 文件可以被 Codex、脚本和人类开发者共同审阅。

## Consequences

Site 后续功能应优先扩展 state/output 协议，而不是创建隐藏数据库。任何缓存或索引都应被视为派生数据，并能从 Zotero 与仓库输出重新生成。

## Boundary

本决策不限制 site 使用临时内存结构或轻量聚合函数。它限制的是独立、持久、与仓库状态竞争的数据库事实源。
