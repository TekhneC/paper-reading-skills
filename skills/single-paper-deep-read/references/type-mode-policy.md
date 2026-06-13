# Type, Mode, and Template Policy

## Paper Type

Determine one:

```text
research_article
survey_article
default_or_unknown
```

Use `research_article` for method, system, benchmark, dataset, empirical, theory-oriented, or default technical papers.

Use `survey_article` for survey, review, systematic review, literature review, meta-review, tutorial-style overview, or position-style review.

Use `default_or_unknown` when uncertain and state the uncertainty.

## Research Subtype

For research articles only, determine one:

```text
classic_paper
new_paper
ordinary_research_article
```

Use `classic_paper` when the user calls the work classic, foundational, representative, historically important, or mainly asks for lineage and influence. Keep reviewer-style criticism balanced and connect limitations to later work when possible.

Use `new_paper` when the user calls the paper new, recent, latest, newly published, or asks to understand current work. Apply stricter scrutiny to baselines, evaluation design, metrics, reproducibility, generalization, and overclaiming.

Use `ordinary_research_article` when neither classic nor new clearly applies.

## Report Mode

Determine one:

```text
full_report
compact_report
```

Use `full_report` when the user asks for full/careful/deep reading, the paper is central, the user is entering a new direction, or the paper is a core reference, baseline, survey, or framework source.

Use `compact_report` when the paper is medium-importance, used for screening/background, or the user asks for a brief/compressed report. Compact means less expansion, not less reading.

Defaults:

```text
research_article + classic_paper: full if central, compact otherwise
research_article + new_paper: full if central/current writing, compact otherwise
research_article + ordinary_research_article: compact by default
survey_article: full for literature-review framework work, compact for screening
default_or_unknown: compact by default
```

State the selected mode briefly when not obvious.

## Analysis Order

Research articles use metrics-first analysis:

```text
research motivation -> research idea -> evaluation metrics -> research method -> experimental setup/results -> claim-evidence alignment -> limitations -> transferable insights
```

Survey articles use scope-taxonomy-first analysis:

```text
survey scope -> inclusion/exclusion boundary -> adjacent surveys -> organizing perspective -> taxonomy -> content synthesis -> challenges/future directions -> scope-taxonomy alignment -> transferable insights
```

Do not force method-paper structure on surveys.

## Template Selection

Use the matching template:

```text
research_article + full_report -> ../../templates/deep_read_research_full.md
research_article + compact_report -> ../../templates/deep_read_research_compact.md
survey_article + full_report -> ../../templates/deep_read_survey_full.md
survey_article + compact_report -> ../../templates/deep_read_survey_compact.md
default_or_unknown + full_report -> ../../templates/deep_read_default_full.md
default_or_unknown + compact_report -> ../../templates/deep_read_default_compact.md
```

Do not mix templates unless the user explicitly requests a hybrid report.

## Required Major Sections

Research full: executive takeaway; problem/motivation/idea; evaluation metrics/evidence design; method/mechanism/results; claim-evidence alignment/discussion/limitations; lineage/team/verification; transferable insights/follow-up; English-ready takeaways.

Research compact: executive takeaway; problem/motivation/idea; evaluation metrics/evidence design; method/results; claim-evidence alignment/limitations; lineage/verification; transferable insights/English-ready material.

Survey full: executive takeaway/scope; scope/boundary/adjacent surveys; review logic/taxonomy; content synthesis; scope-taxonomy alignment/challenges/future directions; author follow-up/verification/limitations; transferable insights/follow-up; English-ready takeaways.

Survey compact: executive takeaway/scope; scope/boundary/adjacent surveys; review logic/taxonomy; content synthesis; scope-taxonomy alignment/challenges/directions; limitations/verification; transferable insights/English-ready material.

Default reports follow the closest matching structure while stating uncertainty.
