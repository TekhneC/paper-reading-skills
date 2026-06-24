# Quick-Read Output Schema

Use `../../templates/quick_read.md` when available.

## Markdown Output

Default path:

```text
outputs/papers/<paper_key>/quick_read.md
```

If `paper_key` is unavailable, use a safe title slug. Do not silently overwrite existing outputs; use timestamped alternates unless replacement is approved.

The Markdown file must include a stable machine-readable summary block near the top so daily triage can aggregate even when JSON is unavailable.

## JSON Sidecar

Default path:

```text
outputs/papers/<paper_key>/quick_read.json
```

Minimum fields:

```json
{
  "schema_version": "1.0",
  "paper_key": "",
  "title": "",
  "authors": [],
  "year": null,
  "venue": "",
  "paper_type": "method paper | system paper | benchmark paper | dataset paper | survey paper | position paper | empirical study | theory paper | unknown",
  "evidence_status": "",
  "recommended_action": "deep_read_candidate | quick_read_only | defer | archive_candidate | needs_metadata_fix | needs_pdf_check",
  "decision_label": "strong_candidate | candidate | borderline | not_recommended",
  "one_sentence_summary": "",
  "relation_to_user_research": "",
  "why_read": [],
  "why_defer": [],
  "suggested_deep_read_focus": [],
  "evidence_source": "",
  "evidence_location": "",
  "uncertainty": "",
  "qualitative_ratings": {
    "research_fit": "unknown",
    "literature_review_value": "unknown",
    "task_formulation": "unknown",
    "method_mechanism": "unknown",
    "evaluation_metrics": "unknown",
    "baseline_comparison": "unknown",
    "ablation_logic": "unknown",
    "process_interaction_relevance": "unknown",
    "novel_framing": "unknown",
    "evidence_confidence": "unknown"
  },
  "high_rated_dimensions": []
}
```

Use `high`, `medium`, `low`, or `unknown` for qualitative ratings. Explain every high-rated dimension in the Markdown card.
