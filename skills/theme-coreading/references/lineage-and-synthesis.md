# Lineage, Supplementary Reading, and Synthesis

## Field Lineage Tracing

Trace field lineage from the user's confirmed theme, research question, and paper set. This is evidence-chain expansion, not free-form recommendation.

Answer:

1. What key prior works precede this paper set?
2. What baselines do these papers rely on?
3. Which surveys or taxonomies define the field?
4. Which follow-up works developed these papers?
5. Which adjacent directions may be missing?
6. Is the current set sufficient for the research question?

Tracing priority:

```text
references in provided papers
related work sections
baseline tables and comparison sections
cited-by / follow-up works if externally available
same-team prior / follow-up works
adjacent surveys
benchmark / dataset papers
recent papers sharing task, metric, dataset, or system framing
```

Confidence labels:

```text
confirmed
likely
candidate
unverified
```

Do not present `candidate` or `unverified` works as field anchors.

## Supplementary Readings

Recommend supplementary readings when the current set appears incomplete. Ground recommendations in missing prior work, baseline, survey/taxonomy, evaluation paper, dataset/benchmark, follow-up work, adjacent direction, or user interaction focus.

Use:

```markdown
| Candidate paper | Year | Why recommended | Relation to current set | Suggested action | Confidence |
|---|---:|---|---|---|---|
```

Allowed `suggested_action`:

```text
quick_read
deep_read_candidate
optional
verify_first
exclude_for_now
```

If external search is unavailable, mark recommendations as needing verification.

## Synthesis Preconditions

Write or update `outputs/themes/<theme_id>/synthesis_report.md` only after:

1. theme is clear;
2. research question is confirmed or explicitly approved as provisional;
3. paper roles are labeled;
4. comparison dimensions are defined;
5. evidence status is stated;
6. comparison matrix is created or updated.

Use `../../templates/theme_synthesis.md` when available.

Do not summarize papers one by one. Write cross-paper claims:

```text
这组论文的共同转向是……
它们的关键差异在于……
A 和 B 都关注……，但 A 通过……，B 通过……
该方向的评价仍然集中在……，尚未充分覆盖……
```

## Required Synthesis Contents

Include:

1. confirmed or explicitly provisional theme and research question;
2. paper set boundary;
3. paper roles;
4. user interaction focus and decision log;
5. comparison dimensions;
6. reference to the comparison matrix;
7. cross-paper synthesis;
8. method, task, taxonomy, or evaluation evolution;
9. field lineage tracing summary;
10. supplementary reading recommendations;
11. quick/deep read handoff summary;
12. tensions and research gaps;
13. review-writing claims;
14. implications for the user's research;
15. evidence level and synthesis confidence;
16. co-reading consensus and next actions.

## Tensions and Gaps

Identify tensions, not only similarities:

```text
task tension
method tension
evaluation tension
dataset tension
interaction tension
theory-practice tension
claim-evidence tension
user-study validity tension
taxonomy tension
field-lineage tension
```

For each gap, state what it is, which papers reveal it, why it matters, whether it is usable for the user's research, what evidence supports it, and what supplementary reading is needed.

## Review-Writing Claims

For literature-review support, include:

```markdown
| Review-writing claim | Supporting papers | Evidence strength | Safe wording | Risk |
|---|---|---|---|---|
```

Do not write claims stronger than the paper set supports. Provide English-ready terms, possible phrasing, one-slide takeaway, or paragraph skeleton when useful. Do not write a final publishable literature-review section unless the user asks.

## Failure Handling

- Missing theme: ask for `core_theme` or the theme around the paper set.
- Missing paper set: ask for paper keys, Zotero collection/tag, or paper list.
- Missing confirmed research question: propose three provisional questions.
- Only one paper: use `$single-paper-quick-read` or `$single-paper-deep-read`.
- Most papers lack quick/deep reads: recommend quick-read cards first.
- Dimensions cannot be defined: state that the theme/question is too vague.
- Evidence insufficient: mark synthesis as low-confidence.
