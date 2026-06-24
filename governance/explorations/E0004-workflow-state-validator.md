# E0004 Workflow State Validator

Status: open
Scope: state/site
Related decisions: D0003, D0005

## Question

Site 状态更新如何严格遵循 allowed transition，而不是依赖自由下拉选择或分散的前端判断？

## Current Context

`AGENTS.md` 已定义 allowed paper states，并要求 `deep_read_approved` 必须有 approval record，`deep_read_done` 必须有 deep-reading report。Site 当前能同步状态和检查部分 guards，但还缺少集中、可复用、可测试的 transition validator。

## Options

1. 在前端限制可选状态，后端只保存。
2. 在后端建立 transition validator，前端只展示后端允许的动作。
3. 在独立脚本中验证状态文件，作为维护工具使用。
4. 同时提供后端 validator 与离线 audit script。

## Trade-offs

前端限制体验直接，但无法防止其他脚本写入错误状态。后端 validator 更适合 site-mediated workflow。离线 audit script 有助于修复历史状态，但不能阻止实时错误。组合方案最稳健，但实现成本更高。

## Current Leaning

优先设计后端 transition validator，并保留未来导出 audit script 的可能。Validator 应引用项目工作流规则，而不是把状态变更视为任意枚举更新。

## What Would Decide This

需要梳理所有 site 写状态的 API、现有状态文件结构，以及 approval/deep-read output 的最小存在性检查。

## Next Step

列出当前状态写入入口，定义 transition table 草案，并标注每条 transition 的 preconditions。
