# Theme Session State

## User-Controlled Theme and Question

Prioritize user-provided:

```text
core_theme
research_question
paper_list
expected_output
writing_goal
current_research_context
```

The skill may clarify, restate, split, or operationalize the research question, but must not silently decide the final question for the user.

Track `research_question_status`:

```text
confirmed
provisional
missing
revised
```

If no confirmed question exists, propose exactly three provisional research question options and ask the user to confirm or revise before writing a formal synthesis report. If the user explicitly approves proceeding with a provisional question, mark synthesis confidence as provisional.

## Theme State File

Default path:

```text
outputs/themes/<theme_id>/theme_state.md
```

Maintain:

```text
theme_id
core_theme
research_question
research_question_status
writing_goal
paper_set
paper_roles
comparison_dimensions
field_lineage_status
supplementary_candidates
quick_read_handoffs
deep_read_handoffs
user_confirmed_decisions
user_interaction_focus
open_questions
evidence_status
synthesis_confidence
report_version
next_actions
```

Use `../../templates/theme_state.md` when available.

## Interaction Focus and Decisions

Maintain this section in state and synthesis:

```markdown
## 用户交互重点与决策记录（user interaction focus and decision log）
```

Record questions the user repeatedly asked, terms clarified, confirmed/rejected interpretations, emphasized dimensions, include/exclude decisions, priority changes, unresolved issues, and papers needing quick/deep read.

Use a concise table:

```markdown
| Interaction focus | User decision / preference | Impact on synthesis |
|---|---|---|
```

## Consensus and Next Actions

Maintain:

```markdown
## 共读关键共识与后续决策（co-reading consensus and next actions）
```

Record confirmed conclusions, user preferences, unresolved questions, hypotheses needing verification, supplementary reading plan, quick/deep read handoffs, and next recommended actions.

Do not log every interaction; record only durable decisions and consensus.

## Focus Modes

Determine `co_reading_focus`:

```text
orientation
comparison
taxonomy
evaluation
field_lineage
writing_support
```

Use `orientation` for entering a new topic; `comparison` for structured comparison; `taxonomy` for classification; `evaluation` for metrics/user-study/benchmark questions; `field_lineage` for missing anchors and supplementary reading; `writing_support` for literature-review claims and review arc.
