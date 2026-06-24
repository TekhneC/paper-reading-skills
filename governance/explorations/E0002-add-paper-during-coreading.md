# E0002 Add Paper During Co-reading

Status: open
Scope: site/theme
Related decisions: D0001, D0005

## Question

Co-reading 中途发现需要添加 paper 时，应加入引用、要求 quick read、要求 deep read，还是直接加入 comparison matrix？

## Current Context

Theme co-reading 不是 stateless chat。它依赖已有 theme state、comparison matrix 和 synthesis report。中途加 paper 会影响比较维度、证据完整性和后续综合结论，因此需要结构化规则。

## Options

1. 仅允许添加已有 `deep_read_done` paper。
2. 允许添加 quick-read paper，但标记为 provisional。
3. 允许添加 Zotero 中尚未阅读的 paper，并创建 quick-read 或 deep-read 请求。
4. 允许临时引用，但不进入 matrix，直到完成必要阅读。

## Trade-offs

只允许 deep-read paper 最稳健，但可能阻碍探索。允许 provisional paper 更贴近研究过程，但会让 matrix 的证据等级变复杂。直接纳入未读 paper 风险最高，容易制造未经验证的比较结论。

## Current Leaning

优先支持添加已有 `deep_read_done` paper；对未完成 deep read 的 paper 只创建待处理请求，不直接进入正式 matrix。

## What Would Decide This

需要确定 matrix 是否支持 evidence status 字段，以及 synthesis report 是否能清楚区分正式纳入与待验证文献。

## Next Step

为 add-paper action 设计状态流草案，区分 `add_to_theme`, `request_quick_read`, `request_deep_read` 和 `reference_only`。
