# Local Site Design Decisions

## 目标

本地网站是 paper-reading skill 集群的任务驱动工作台。它不替代 Zotero，不建立独立数据库，只聚合和更新本仓库内的派生状态、阅读产物与共读消息。

## 修订后的信息架构

一级入口：

1. `今日`：整合最新当日阅读归档和所有待办事项。
2. `文献`：查看文献列表、审批精读、编辑快读/精读。
3. `共读`：查看主题状态、比较矩阵、综合报告，并进行聊天式共读交互。
4. `归档`：原“每日”改为归档，按 `outputs/daily/YYYY-MM-DD/` 存储与浏览。
5. `消息`：查看本地共读消息 outbox。

## TODO 与入口联动

TODO 不再只是列表项。每条 TODO 都包含 `target`：

```json
{ "mode": "papers", "id": "L73225HI", "view": "deep" }
```

前端“处理该事项”按钮会根据 target 直接跳转到对应文献、共读主题或归档视图。若 TODO 动作为
`daily_triage`，按钮直接调用 `POST /api/daily/run` 生成当日归档，而不是只跳转到空归档页。

## Daily 触发与归档

Daily 是全局工作流动作，不绑定到某一篇文献。入口固定在左侧边栏底部工作流区域，用于从 Zotero 检索未读文献、执行 quick read、生成总结并推荐精读。后端 `POST /api/daily/run` 会根据当前本地队列、快读 JSON 和候选状态生成或更新：

- `outputs/daily/YYYY-MM-DD/digest.md`
- `outputs/daily/YYYY-MM-DD/quick_reads.json`
- `outputs/daily/YYYY-MM-DD/deep_read_candidates.json`

该动作只写本仓库的派生输出，不修改 Zotero，也不自动批准精读。

## 可收起边栏

左侧 Paper Reading 边栏可收起。桌面端收起后仅保留菜单按钮，以便快读/精读和原文对照获得更多横向空间。移动端保持完整导航，避免隐藏关键入口。

## 快读/精读编辑器

快读和精读不再是只读 Markdown 页面，而是默认渲染的可编辑 Markdown 笔记。编辑器提供：

- 默认渲染式 contenteditable 笔记
- 源码模式
- 保存按钮
- 可收起的右侧原文 PDF 对照

后端 `POST /api/markdown` 只允许写入 `outputs/**/*.md`，防止误改 Zotero 或仓库外文件。

## 可编辑思路图

思路图不再是只读 SVG，也不再依赖表单式大纲。页面显示可直接操作的节点画布：节点可新增、删除、拖动，节点内文字可直接编辑。保存时写入：

- `outputs/papers/<paper_key>/mindmap.json`
- `outputs/themes/<theme_id>/mindmap.json`
- `outputs/daily/<date>/mindmap.json`

若没有保存过思路图，前端仍会从快读、精读、主题综合或归档内容中派生初稿，并自动分配初始节点位置。

## 原文左右对照

快读与精读页采用左右双栏：左侧编辑 Markdown，右侧嵌入原文 PDF。原文对照不是独立 tab，而是阅读页内部的可收起面板；收起后 Markdown 编辑区获得更大横向空间。若 PDF 路径不可用，右栏显示缺失提示。

## 共读聊天

共读/交互消息采用聊天形态。消息发送到：

- `state/coreading_messages.jsonl`
- 若主题目录存在，同时写入 `outputs/themes/<theme_id>/message_inbox.jsonl`

当前仍是本地 outbox，不直接调用外部线程。后续可增加桥接器读取 JSONL 并转发到 Codex thread。

## 状态同步边界

网页端状态更新目标：

- `state/approvals/<paper_key>.json`
- `state/workflow_state.json`
- `state/reading_queue.json`
- `state/reading_events.jsonl`
- `state/coreading_messages.jsonl`

约束：

- `deep_read_approved` 必须有 approval record。
- `deep_read_done` 必须已有 `deep_read.md` 与 `deep_read.json`。
- 网页不提供归档文献按钮；文献归档仍需单独确认。

## 可扩展性

后端聚合成本地 dashboard JSON；前端通过 normalized item 渲染不同视图。新增 skill 输出时，优先扩展后端聚合函数，再在 `state.js` 增加 normalize 分支。
