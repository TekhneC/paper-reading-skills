# D0006 Site Design Decisions Moved to Governance

Status: accepted
Date: 2026-06-24
Scope: governance/site
Supersedes: site/DESIGN_DECISIONS.md
Superseded by:
Related: D0002, D0003

## Decision

`site/DESIGN_DECISIONS.md` 停用为主设计决策容器。当前和后续的项目治理、site governance、accepted decisions、open explorations 与 development priorities 应维护在根目录 `/governance` 下。`site/README.md` 保留为运行说明和当前功能入口。

## Context

旧的 site design file 混合了目标、信息架构、Daily、编辑器、思路图、共读聊天、状态同步和 deep-read interaction 等内容。它曾经适合作为局部设计记录，但现在项目已经需要跨 skill、site、state 和 workflow 的共同记忆层。继续把主要决策放在 site 目录下，会让 governance 被误认为只属于网页实现。

## Options Considered

一种方案是继续扩写 `site/DESIGN_DECISIONS.md`。另一种方案是删除旧文件。第三种方案是保留旧文件作为 deprecated pointer，并把稳定内容压缩迁移到 governance。

## Rationale

保留停用指针能避免断链，也能提醒后续开发者不要继续向旧文件追加长决策。将治理内容移到根目录级 `governance/`，更符合项目记忆层的定位。

## Consequences

新设计取舍应写入 `governance/decisions/` 或 `governance/explorations/`。Site 运行说明仍维护在 `site/README.md`。旧文件不再承载长期决策。

## Boundary

本决策不删除旧文件，不改变 site runtime behavior，也不把 Governance 加入 site 普通导航。
