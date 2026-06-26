# Project State

## Role of This File

本文档保存当前项目状态与项目特异操作上下文。

它供 generic governance skills 在本项目中正确表现时快速读取：

1. 当前阶段；
2. 当前 P0；
3. 当前 active explorations；
4. 必须从本项目记住的操作上下文；
5. 指向事实、共识、决策、探索和优先级来源的文件。

本文档不是完整治理层，不替代 `AGENTS.md`，也不复制完整 workflow 或 skill procedures。

## Current Stage

治理层 bootstrap 已基本完备。

当前阶段是：

1. 将 governance 从 bootstrap 转为维护、漂移检查和设计收敛；
2. 将 site-mediated workflow 的状态更新变得可验证；
3. 收敛 co-reading 相关开放设计问题；
4. 保持 generic governance skill 与本项目事实解耦。

## Current P0

1. 设计并实现 workflow state validator。
   - Source: `governance/explorations/E0004-workflow-state-validator.md`
   - Priority file: `governance/development_priorities.md`

2. 收敛 co-reading collection builder 的最小设计。
   - Source: `governance/explorations/E0001-coreading-collection-builder.md`
   - Priority file: `governance/development_priorities.md`

3. 收敛 add-paper-during-coreading 的工作流规则。
   - Source: `governance/explorations/E0002-add-paper-during-coreading.md`
   - Priority file: `governance/development_priorities.md`

## Active Explorations

| ID | Topic | Status | File |
|---|---|---|---|
| E0001 | Co-reading collection builder | open | `governance/explorations/E0001-coreading-collection-builder.md` |
| E0002 | Add paper during co-reading | open | `governance/explorations/E0002-add-paper-during-coreading.md` |
| E0003 | Approval and deep-read trigger coupling | open | `governance/explorations/E0003-approval-and-deep-read-trigger-coupling.md` |
| E0004 | Workflow state validator | open | `governance/explorations/E0004-workflow-state-validator.md` |

## Project-Specific Operating Context

Generic governance skills must remember the following when operating in this repository:

- 本项目是本地论文阅读工作流系统，入口包括 Codex skills 与 local site。
- Zotero 是只读 bibliographic source；本仓库只保存派生 workflow state、outputs、templates、scripts、skills 和 governance。
- Local site 是 workflow console，不是独立数据库。
- Governance 是内部 project memory layer，不是普通 user-facing site surface。
- Formal deep read 必须经过 user approval；不要把 open exploration 当作 accepted workflow rule。
- Skill governance 保持轻量，关注 interfaces、expected outputs 和协作边界；不要复制完整 `SKILL.md` procedures。
- Site governance 相对更重，因为 site 控制用户动作、state/output I/O 和 skill invocation。
- 默认写作语言为中文；论文标题、方法名、数据集、指标、代码标识和已固定术语可保留英文。
- 当治理变更影响当前阶段、当前 P0、active explorations、项目特异操作上下文、source map 或 accepted decision snapshot 时，应在同一轮更新 `PROJECT_STATE.md`。

Hard boundaries and evidence rules remain in `AGENTS.md`.

## Source Map

- Repository hard boundaries: `AGENTS.md`
- Governance guide: `governance/README.md`
- Current consensus: `governance/project_consensus.md`
- Workflow boundaries: `governance/workflows.md`
- Skill interfaces: `governance/skill_governance.md`
- Site responsibilities: `governance/site_governance.md`
- Development priorities: `governance/development_priorities.md`
- Decision index: `governance/decision_index.md`
- Accepted decisions: `governance/decisions/`
- Open explorations: `governance/explorations/`

## Current Accepted Decision Snapshot

详见 `governance/decision_index.md`。

当前 accepted decisions:

- D0001: Dual-entry local reading system
- D0002: Governance is internal, not user-facing
- D0003: Site is workflow console, not database
- D0004: Zotero read-only and derived repository boundary
- D0005: Approval gate before formal deep read
- D0006: Site design decisions moved to governance

## Read Next

默认阅读顺序：

1. `AGENTS.md`
2. `PROJECT_STATE.md`
3. `governance/README.md`

然后按任务读取 Source Map 中对应文件。
