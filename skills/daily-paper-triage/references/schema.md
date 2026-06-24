# Daily Triage Schemas

## Daily Quick-Read Aggregate

```json
{
  "schema_version": "1.0",
  "date": "YYYY-MM-DD",
  "queue_source": "",
  "papers": [
    {
      "paper_key": "",
      "title": "",
      "quick_read_status": "available | markdown_only | missing",
      "recommended_action": "",
      "one_sentence_summary": "",
      "relation_to_user_research": "",
      "evidence_source": "",
      "evidence_location": "",
      "uncertainty": ""
    }
  ]
}
```

## Deep-Read Candidate Record

```json
{
  "schema_version": "1.0",
  "date": "YYYY-MM-DD",
  "candidates": [
    {
      "rank": 1,
      "paper_key": "",
      "title": "",
      "decision_label": "strong_candidate | candidate | borderline | not_recommended",
      "recommendation_reason": "",
      "suggested_deep_read_focus": [],
      "risk_or_uncertainty": "",
      "evidence_source": "",
      "evidence_location": "",
      "qualitative_ratings": {},
      "high_rated_dimensions": []
    }
  ]
}
```

## Approval Block

```markdown
## 需要确认的精读候选

建议进入精读：

- [ ] <paper_key> - <title>
  - 推荐理由：
  - 建议精读重点：
  - 不确定点：

建议暂不精读：

- <paper_key> - <title>
  - 原因：
```
