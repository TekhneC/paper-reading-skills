# Site Governance

## Site Identity

Local site 是 paper-reading skill cluster 的 workflow console。
它不是独立数据库，也不替代 Zotero。

## Public User Surfaces

当前 public navigation：

- Today
- Papers
- Co-reading
- Archives
- Messages

Governance 不得作为普通 user-facing tab 暴露。

## Current Site Responsibilities

Site 可以：

- 显示 queue、papers、approvals、daily archives、themes 和 messages；
- 触发 Daily；
- 批准 deep read；
- 在 approval 后触发 formal deep read；
- 编辑 quick-read 和 deep-read Markdown outputs；
- 在可用时显示 source PDFs；
- 发送 deep-read interaction questions；
- 发送 theme co-reading questions；
- 持久化本地 JSONL message records。

## State and Output Boundary

Site 只可写入 repository-local derived artifacts。

Expected writable targets include:

- `state/approvals/<paper_key>.json`
- `state/workflow_state.json`
- `state/reading_events.jsonl`
- `state/coreading_messages.jsonl`
- `state/deep_read_interaction_messages.jsonl`
- `outputs/**/*.md`
- `outputs/**/mindmap.json`

Site 不得修改 Zotero。

## Known Gaps

- 尚无明确的 co-reading collection builder。
- Co-reading 中途添加 paper 还不是结构化工作流。
- Workflow state transitions 仍需要更严格的 validator。
- Approval 与 deep-read execution 当前耦合，后续可能需要修订。

## Deprecated Site Design File

`site/DESIGN_DECISIONS.md` 不再是 design governance 的来源。
当前 site governance 维护在本文档中。
