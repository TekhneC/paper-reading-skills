# Evidence and Reading Rules

## Source Priority

Use the strongest available source first:

1. original PDF or full text
2. `state/cache/deep_read_sources/<paper_key>/pages.json`
3. `state/cache/deep_read_sources/<paper_key>/tables.md`
4. `state/cache/deep_read_sources/<paper_key>/figures.json` and figure images
5. page-aware or layout-aware extraction
6. `state/cache/quick_read_sources/<paper_key>.layout.txt`
7. `state/cache/quick_read_sources/<paper_key>.flow.txt`
8. `outputs/papers/<paper_key>/quick_read.json`
9. `outputs/papers/<paper_key>/quick_read.md`
10. Zotero metadata and reading queue metadata

Quick-read outputs are supporting context, not sufficient evidence for a formal deep read unless the user explicitly accepts an evidence-limited report.

## Evidence Requirements

Preferred evidence level:

```text
PDF available
full text available
page numbers available
figures and tables available
references available
appendix available when relevant
```

If only metadata or abstract is available, do not produce a formal deep-read report.

Distinguish:

```text
作者明确声称
可由文本支持的推断
我的判断
```

Use precise citations when available:

```text
（文件名：xxx.pdf，第 x 页）
（文件名：xxx.pdf，第 x 页，Figure x）
（文件名：xxx.pdf，第 x 页，Table x）
```

If page numbers are unreliable, write: `页码未能可靠识别。`

## Figures, Tables, and Extraction Artifacts

For two-column PDFs, tables, figures, equations, or extraction artifacts:

1. prefer layout-aware text when column order matters;
2. inspect table/figure captions and surrounding paragraphs before interpreting results;
3. use extracted figure images when a figure is central to method or claim explanation;
4. if extraction is unreliable, state that page-level or visual inspection is needed;
5. do not reconstruct numeric results from garbled tables.

For the first report section, select at most one key visual anchor. Prefer absolute local `crop_image_path` from `figures.json`, wrapped in angle brackets:

```markdown
![Key figure: <short description>](<C:\absolute\path\to\figure_crop.png>)
```

Use repo-relative paths only when the user asks for portable Markdown.

## Preprint and External Verification

When a paper appears to be a preprint, OpenReview submission, unpublished manuscript, or technical report, verify status when network/external search is available:

```text
publisher page
official proceedings
OpenReview
arXiv version history
DOI landing page
project or author page
```

Report one:

```text
published version confirmed
accepted but not yet published
preprint only
status unknown
```

If external verification is unavailable, mark status unknown/unverified. Do not infer acceptance.

For preprints, apply stricter checks for missing experiments, weak ablations, public review issues, version differences, missing code/data, selective reporting, evaluation bias, and overclaiming.

## Alignment Checks

Research articles require claim-evidence alignment:

```text
core claim
evidence
evidence strength: strong / moderate / weak / unclear
alignment judgment
what the evidence does not prove
```

Survey articles require scope-taxonomy alignment:

```text
survey scope
inclusion/exclusion boundary
taxonomy dimensions
coverage evidence
missing categories or adjacent surveys
alignment judgment
```

Do not convert missing evidence into a confident critique. Mark uncertainty explicitly.

## Critical and Transferable Perspectives

For research articles, consider novelty, technical soundness, evaluation validity, baseline choice, ablation design, reproducibility, generalization, user-study design, and claim-evidence alignment.

For survey articles, consider scope clarity, inclusion criteria, taxonomy validity, coverage bias, comparison depth, adjacent surveys, future-direction quality, and scope-taxonomy alignment.

Connect transferable insights to the user's likely contexts:

```text
digital painting process generation
human-AI co-creation
process-level evaluation
interactive generation systems
art persona modeling
multi-modal creative systems
literature review writing
experimental design
```
