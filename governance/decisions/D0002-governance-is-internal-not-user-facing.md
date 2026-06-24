# D0002 Governance Is Internal, Not User-facing

Status: accepted
Date: 2026-06-24
Scope: governance/site
Supersedes:
Superseded by:
Related: D0001, D0006

## Decision

Governance 是内部项目记忆层，不作为普通用户网页入口，不加入 site 的常规导航。它服务 human-AI collaborative development，用于保存项目共识、设计决策、开放探索和开发优先级，而不是作为阅读者日常使用的功能页面。

## Context

现有 site 公开导航面向阅读工作流，包括 Today、Papers、Co-reading、Archives 和 Messages。Governance 文档面向开发者与 AI coding agent，其中包含项目边界、取舍、优先级和未决问题。若将 Governance 作为普通页面暴露，用户界面会混入内部开发语义，削弱阅读工作台的清晰性。

## Options Considered

一种方案是在 site 中增加 Governance tab，让所有决策可视化。另一种方案是完全不建立 governance，只依赖 README 和 AGENTS.md。第三种方案是把 governance 保留为仓库内文档，并允许未来按需建立 developer-only viewer。

## Rationale

当前最重要的是稳定项目记忆，而不是扩展普通用户界面。文档层足以让 Codex 在进入项目时恢复上下文，也能让人类开发者审阅共识。把它放入普通导航会制造错误信号，使治理层看起来像产品功能。

## Consequences

Site 不新增 Governance tab。若未来需要可视化治理内容，应明确为 developer-only surface，并另行决策。普通用户路径继续围绕阅读、审批、编辑和共读展开。

## Boundary

本决策不禁止开发者阅读 governance 文档，也不禁止未来构建内部查看器。它只禁止把 Governance 作为普通 user-facing site surface。
