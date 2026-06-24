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

共读页采用左右工作台，而不是单独的消息 outbox：

- 左侧展示 coreading skill 产出的 Markdown：`theme_state.md`、`comparison_matrix.md`、`synthesis_report.md`。
- 右侧展示当前主题的聊天记录、关联文献上下文、快捷共读提问和消息输入框。
- 快捷提问只填充草稿，不自动提交，避免在未确认时写入状态。

共读/交互消息采用聊天形态。消息发送到：

- `state/coreading_messages.jsonl`
- 若主题目录存在，同时写入 `outputs/themes/<theme_id>/message_inbox.jsonl`

每条消息包含 `intent` 与 `source_view`，便于后续桥接器区分开放问题、证据核查、维度澄清和下一步请求。当前仍是本地 outbox，不直接调用外部线程。后续可增加桥接器读取 JSONL 并转发到 Codex thread。

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

## Deep-read Interaction 协同设计

精读交互工作台与 `deep-read-interaction` skill 协同优化，而不是在网站侧复刻 skill 判断逻辑。

- `deep-read-interaction` 负责根据用户输入判断主要意图：`confirmation`、`clarification`、`follow_up`、`divergent_thinking`。
- 用户可以通过网站上的四个意图按钮手动指定或更改分类提示；若不指定，网站向后端传递 `auto`，由 skill 判断。
- 外部 Codex 返回机器可读 envelope；后端只把 `answer_markdown` 展示给用户，并把 `interaction_mode` 存入 JSONL，供历史筛选使用。
- 网站侧不再提供独立的“交互模式”下拉框，也不再提供状态筛选下拉框。
- 四个意图按钮既是历史筛选入口，也是下一次提问的分类提示；再次点击当前意图按钮回到全部历史。
- 关键词筛选和“一键清空历史”位于四个意图按钮同行右侧，减少纵向占用。
- 交互工作台采用紧凑布局：顶部显示 paper/report context，中部是可滚动聊天历史，底部是问题输入和触发按钮。

## Deep-read Interaction 中台界面优化

交互精读中台优先服务“边读边问、回到 Markdown 编辑”的工作流，因此界面应避免把分类、状态和技术信息前置成复杂表单。

- 顶部说明只保留一句动作提示：直接提问，系统自动判断意图；意图按钮既可筛选历史，也可作为下一问分类提示。
- Paper 与 Report 信息保持在右上角，但只显示短标签，完整路径通过 hover 查看，避免长路径挤压主操作区。
- 四个意图按钮是主要历史筛选入口，视觉上靠左排列；关键词筛选、显示计数和清空历史靠右排列。
- 聊天历史是中台主体，应独立滚动；底部输入框和“触发 skill 回复”按钮保持稳定可见。
- 用户消息内只显示中文分类，不暴露 `clarification`、`follow_up` 等内部枚举作为主视觉信息。
- `deep-read-interaction`、`codex_completed` 等技术状态降级为辅助信息；用户优先看到问题与 Codex 回复。
