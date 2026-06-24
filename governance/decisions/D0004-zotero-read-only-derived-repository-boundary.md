# D0004 Zotero Read-only and Derived Repository Boundary

Status: accepted
Date: 2026-06-24
Scope: data
Supersedes:
Superseded by:
Related: D0003, D0005

## Decision

治理层承认并引用 `AGENTS.md` 中的 Zotero 只读边界。Zotero 是 paper metadata、attachments、tags、collections 和 PDF locations 的来源。本仓库只保存 derived workflow data，包括索引、队列、approval records、theme packets、Markdown outputs、脚本、模板、skill definitions 和配置。

## Context

项目需要治理层保存共识，但不能让治理文档变成第二套安全规则全集。Zotero 访问、仓库写入范围、PDF 和数据库禁存规则已经由 `AGENTS.md` 定义。若 governance 重新完整书写这些规则，未来两处文本可能产生差异，导致 Codex 或开发者误判权威来源。

## Options Considered

一种方案是在 governance 中复制完整 Zotero 规则。另一种方案是只在 governance 中写一句引用。第三种方案是明确 `AGENTS.md` 为 hard boundary，并在 governance 中记录其设计含义。

## Rationale

第三种方案既保持治理层可读，又避免规则漂移。Governance 负责说明为什么系统采用派生仓库模型；具体禁止项、路径约束和只读细节仍由 `AGENTS.md` 管理。

## Consequences

涉及 Zotero、原始 PDF、数据库、credentials 或仓库外写入的任务，仍必须先服从 `AGENTS.md`。Governance 文件不得成为绕过硬边界的理由。

## Boundary

本决策不新增 Zotero 操作规则，也不授权修改 Zotero。它只规定 governance 如何引用并维护对数据边界的共识。
