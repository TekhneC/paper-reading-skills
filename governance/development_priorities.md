# Development Priorities

## Priority Principle

优先开发能够强化以下能力的功能：

1. main workflow loop；
2. state traceability；
3. user decision visibility；
4. skill-site coordination。

仅改善展示、但不能稳定工作流的功能应延后。

## P0

### 1. Workflow state validator

Reason:
Site 当前允许更新状态，但 workflow transitions 应根据项目工作流规则进行验证。

Related:
- E0004

### 2. Co-reading collection builder minimal design

Reason:
目标工作流要求用户从已有 deep-read papers 中选择若干篇，形成 co-reading collection/theme。

Related:
- E0001

### 3. Add paper during co-reading

Reason:
Theme co-reading 必须支持中途加入 paper，同时避免把 co-reading 变成 stateless chat。

Related:
- E0002

## Baseline / Maintenance

### Governance layer bootstrap

Status:
基本完备。

Reason:
`governance/` 已建立项目共识、决策索引、accepted decisions、open explorations、workflow 边界与开发优先级。后续工作以维护、漂移检查和设计收敛为主，不再作为 P0 bootstrap 项。

Related:
- D0001
- D0002
- D0006

## P1

- 改进 site-mediated skill invocation feedback。
- 澄清 approval 与 deep-read execution 的耦合关系。
- 改进 interaction-driven document update workflow。

## P2

- Reading experience enhancements。
- Advanced visualization。
- 未来如确有需要，可增加 developer-only governance viewer。
