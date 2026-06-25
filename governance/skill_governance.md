# Skill Governance

## Scope

Skill governance 是轻量的、interface-oriented 的治理。

它记录：

- 哪些 skills 存在；
- skills 如何对应系统工作流；
- 哪些 skills 可以由 site 触发；
- site 期待每个 skill 产生什么输出。

它不复制完整 `SKILL.md` procedures。

## Current Skills

- `daily-paper-triage`
- `single-paper-quick-read`
- `single-paper-deep-read`
- `deep-read-interaction`
- `theme-coreading`
- `project-governance-maintainer`

## Site-triggered Skills

### daily-paper-triage

由 site 的 Daily 按钮触发。

Expected outputs:

- `outputs/daily/YYYY-MM-DD/digest.md`
- `outputs/daily/YYYY-MM-DD/quick_reads.json`
- `outputs/daily/YYYY-MM-DD/deep_read_candidates.json`

### single-paper-deep-read

在用户 approval 后触发。

Precondition:

- `state/approvals/<paper_key>.json`

Expected outputs:

- `outputs/papers/<paper_key>/deep_read.md`
- `outputs/papers/<paper_key>/deep_read.json`

### deep-read-interaction

从 deep-read interaction panel 触发。

Expected behavior:

- 以 chat form 回答用户问题；
- 保留 evidence uncertainty；
- 除非用户明确要求，不生成完整新报告。

### theme-coreading

从 co-reading workspace 触发。

Expected behavior:

- 回答 theme-level co-reading questions；
- 使用 theme state 作为上下文；
- 帮助用户手动更新 matrix 或 synthesis。

## Developer-triggered Skills

### project-governance-maintainer

由 Codex 在用户询问项目状态、治理共识、设计决策、开放探索、开发优先级、治理漂移，或要求更新 `governance/` 时触发。

Expected behavior:

- 维护轻量 governance layer；
- 判断请求属于 ordinary TODO、Exploration、Decision、priority update 或 drift；
- 不复制 `AGENTS.md` 或其他 `SKILL.md` 的完整流程；
- 不作为普通 site-triggered reading workflow 暴露。
