# Deep-Read Outputs and State

## Inputs

Use available files:

```text
config/paths.toml
state/approvals/
state/candidates/YYYY-MM-DD_deep_read_candidates.json
outputs/daily/YYYY-MM-DD/deep_read_candidates.json
outputs/papers/<paper_key>/quick_read.md
outputs/papers/<paper_key>/quick_read.json
state/cache/deep_read_sources/<paper_key>/pages.json
state/cache/deep_read_sources/<paper_key>/tables.md
state/cache/deep_read_sources/<paper_key>/figures.json
state/cache/deep_read_sources/<paper_key>/figures/
state/external_verification/<paper_key>.json
templates/deep_read_*.md
```

Candidate files are not approval by themselves.

## Output Paths

Canonical outputs:

```text
outputs/papers/<paper_key>/deep_read.md
outputs/papers/<paper_key>/deep_read.json
```

Optional daily-run copies:

```text
outputs/daily/YYYY-MM-DD/deep_reads/<paper_key>.md
outputs/daily/YYYY-MM-DD/deep_reads/<paper_key>.json
```

If `paper_key` is unavailable, use a safe title slug.

## JSON Sidecar

Minimum fields:

```json
{
  "schema_version": "1.0",
  "paper_key": "",
  "title": "",
  "paper_type": "research_article | survey_article | default_or_unknown",
  "research_subtype": "classic_paper | new_paper | ordinary_research_article | not_applicable",
  "report_mode": "full_report | compact_report",
  "template_used": "",
  "approval_source": "",
  "source_paths": [],
  "evidence_status": "",
  "page_evidence_status": "",
  "preprint_status": "",
  "key_takeaway": "",
  "key_figure_path": "",
  "key_figure_caption": "",
  "key_figure_page": null,
  "key_figure_role": "",
  "claim_evidence_summary": "",
  "transferable_insights": [],
  "generated_at": ""
}
```

## State Update

May propose or apply:

```text
deep_read_approved -> deep_read_done
```

Apply only when:

1. the state file exists;
2. the paper is approved;
3. Markdown report exists;
4. JSON sidecar exists;
5. the transition is allowed by `AGENTS.md`;
6. the user request allows writing state.

Do not archive papers automatically and do not modify Zotero records.

## Failure Messages

- Not approved: `该论文尚未获得精读批准，不能生成正式精读报告。`
- Cannot identify paper: request paper key, title, PDF path, or Zotero record.
- Missing metadata: `元数据不完整，需要检查 Zotero 记录。`
- Missing PDF: `PDF 缺失，无法完成正式精读。`
- Metadata/abstract only: `当前仅有元数据或摘要，证据不足，不能生成正式精读报告。`
- Unreliable pages: `页码未能可靠识别。`
- Method unavailable: `方法细节不足，无法可靠重建完整机制。`
- Evaluation unavailable: `评估细节不足，难以判断结论强度。`
- External lineage unverified: state that external search is required before treating the relation as confirmed.
