# Comparison, Roles, and Handoffs

## Inputs

Use available files:

```text
state/library_index.jsonl
state/reading_queue.json
state/approvals/
outputs/papers/<paper_key>/quick_read.md
outputs/papers/<paper_key>/deep_read.md
outputs/themes/<theme_id>/theme_state.md
outputs/themes/<theme_id>/comparison_matrix.md
outputs/themes/<theme_id>/synthesis_report.md
config/paths.toml
templates/theme_state.md
templates/comparison_matrix.md
templates/theme_synthesis.md
```

Paper sets may come from user-provided paper keys, Zotero collection/tag, local folder, quick/deep-read outputs, bibliography, or search result list. If ambiguous, report ambiguity.

## Paper Roles

Label each paper relative to the confirmed or approved-provisional research question.

Allowed roles:

```text
core_paper
baseline_paper
method_paper
survey_paper
evaluation_paper
dataset_or_benchmark_paper
system_paper
theory_or_framework_paper
background_paper
adjacent_paper
candidate_supplementary_paper
uncertain
```

Do not label roles only by paper type. A survey can be a core paper; a method paper can be background.

Use:

```markdown
| Paper | Role | Why this role | Relation to research question | Evidence status |
|---|---|---|---|---|
```

## Evidence and Confidence

For every major theme-level claim, identify its basis:

```text
based on deep_read reports
based on quick_read cards
based on metadata / abstract only
based on external search
based on local inference
based on comparison matrix
based on author-stated claims
based on supported inference
based on assistant critical judgment
```

If external search was not performed, say so. Do not convert uncertain relations into confirmed claims.

## Comparison Matrix

Default path:

```text
outputs/themes/<theme_id>/comparison_matrix.md
```

Use `../../templates/comparison_matrix.md` when available.

Default dimensions for research clusters:

```text
paper role
research problem
task formulation
input / output
method paradigm
data and representation
evaluation metrics
datasets / benchmarks
baselines
human evaluation or user study
limitations
claim-evidence alignment
relation to user research
evidence strength
```

Default dimensions for survey clusters:

```text
paper role
survey scope
inclusion / exclusion boundary
organizing perspective
taxonomy
coverage
relation to adjacent surveys
challenges
future directions
transferable review structure
evidence strength
```

Default dimensions for mixed clusters:

```text
paper role
problem / scope
task or taxonomy
method or organizing perspective
evaluation or evidence standard
contribution to theme
limitations
transferable insight
evidence strength
```

Adapt dimensions to the user's confirmed question. Mark unknowns as `文中未说明。` or `证据不足。`

## Handoffs

Use `$single-paper-quick-read` when a paper has not been read, its role is unclear, or it is a supplementary candidate needing inclusion/exclusion judgment.

Record:

```markdown
| Paper | Reason for quick read | Expected decision |
|---|---|---|
```

Use `$single-paper-deep-read` when a paper is core, a key baseline, taxonomy-defining, repeatedly questioned by the user, conflicts with another paper in a synthesis-changing way, or its claim-evidence judgment affects the theme conclusion.

Record:

```markdown
| Paper | Reason for deep read | Suggested report mode | Expected contribution to co-reading |
|---|---|---|---|
```

Do not mark papers as `deep_read_approved`.
