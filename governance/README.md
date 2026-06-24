# Governance Layer

## Purpose

治理层是服务 human-AI collaborative development 的项目记忆层。

它维护：

1. 项目共识；
2. 设计决策；
3. 设计探索；
4. 开发优先级。

## What Governance Is Not

- 它不是 public user-facing site feature。
- 它不是 `AGENTS.md` 的替代品。
- 它不是复制完整 `SKILL.md` 流程的地方。
- 它不是详细 implementation log。

## Reading Order for Codex

始终先读：

1. `AGENTS.md`
2. `PROJECT_STATE.md`
3. `governance/README.md`

然后按需阅读：

- 当前边界：`project_consensus.md`
- 工作流：`workflows.md`
- Skill 相关变更：`skill_governance.md`
- Site 相关变更：`site_governance.md`
- 开发顺序：`development_priorities.md`
- 已接受决策：`decisions/`
- 开放设计问题：`explorations/`

## Numbering Rules

Decision ID 使用 `D0001`, `D0002`, ...
Exploration ID 使用 `E0001`, `E0002`, ...

不要删除、重排或复用 ID。
如果某个 decision 后续被证明错误，应创建新的 decision 来 supersede 或 revert 它。
