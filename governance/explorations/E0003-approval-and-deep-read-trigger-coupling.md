# E0003 Approval and Deep-read Trigger Coupling

Status: open
Scope: workflow/site
Related decisions: D0005

## Question

Approval 是否应立即触发 deep read，还是拆成 approval 与 run deep read 两步？

## Current Context

当前 site 可以在用户 approval 后触发 formal deep read。这个路径符合 approval gate，但 approval 与执行之间的耦合程度仍需澄清。不同用户情境下，批准一篇论文与立即消耗时间生成报告可能不是同一个动作。

## Options

1. Approval 后立即运行 deep read。
2. Approval 只写入 approval record，用户另点 run deep read。
3. 默认立即运行，但提供延后执行选项。
4. 批量 approval，随后按队列运行 deep read。

## Trade-offs

立即运行路径短，适合单篇阅读，但用户可能只想先标记候选。拆成两步更清晰、可控，但增加操作成本。批量模式适合阅读计划，却需要更完整的队列和进度反馈。

## Current Leaning

保留当前耦合关系作为可用默认，但在治理层记录该问题。后续若引入 validator 或任务队列，应考虑拆分 approval 与 execution。

## What Would Decide This

需要观察用户是否经常批准后不希望立即运行，以及 deep read 执行是否足够耗时到需要队列管理。

## Next Step

在 workflow state validator 设计中预留 `deep_read_approved` 与 `deep_read_running` 或等价状态的可能性。
