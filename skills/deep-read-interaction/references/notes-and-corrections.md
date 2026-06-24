# Notes and Corrections

## Consensus Notes

Maintain notes only when the user explicitly asks to record, save, update, or maintain them.

Default paths:

```text
outputs/papers/<paper_key>/interaction_notes.md
outputs/papers/<paper_key>/interaction_notes.json
```

Daily-run copies may also be written:

```text
outputs/daily/YYYY-MM-DD/deep_read_interactions/<paper_key>.md
outputs/daily/YYYY-MM-DD/deep_read_interactions/<paper_key>.json
```

Record only consensus reached during interaction. Do not log every question, every answer, or unconfirmed speculation.

Recommended Markdown sections:

```markdown
# Deep Read Interaction Notes - <Paper Title>

## Confirmed Understanding
## Clarified Points
## Corrected Misunderstandings
## User Research Ideas Agreed As Useful
## Open Questions
## Source-checked Corrections
```

Recommended JSON fields:

```json
{
  "schema_version": 1,
  "paper_key": "",
  "title": "",
  "updated_at": "",
  "confirmed_understanding": [],
  "clarified_points": [],
  "corrected_misunderstandings": [],
  "agreed_research_ideas": [],
  "open_questions": [],
  "source_checked_corrections": []
}
```

## Correcting Deep-Read Reports

Correct factual errors in the original deep-read report only when all conditions are true:

1. the claim is factual, not interpretive;
2. original source or verified external source contradicts the report;
3. corrected wording is clear;
4. the user request allows editing the report, or the user confirms the correction.

Before editing, back up:

```text
outputs/papers/<paper_key>/deep_read.backup_YYYY-MM-DD_HHMMSS.md
outputs/papers/<paper_key>/deep_read.backup_YYYY-MM-DD_HHMMSS.json
```

Then update:

```text
outputs/papers/<paper_key>/deep_read.md
outputs/papers/<paper_key>/deep_read.json
```

If daily-run copies exist, either update them too or record that the canonical report was corrected and the daily copy is stale.

Correction records should include:

```text
original claim
corrected claim
source evidence
backup path
updated paths
```

Interpretive disagreements are not factual errors; record them as consensus or open questions.
