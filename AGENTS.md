# AGENTS.md

## Project scope

This repository is a local paper-reading workflow system.

Repository path:

```text
~/.agents/paper-reading-skills
```

The repository manages:

* Codex skills for paper reading workflows
* Zotero read-only indexing scripts
* Markdown templates
* reading-state records
* generated reading notes and reports
* theme-reading packets and outputs

This repository is not the Zotero data directory. Do not store original Zotero PDFs or the original Zotero database in this repository.

---

## Core boundaries

### Zotero is the bibliographic source

Zotero is the source of truth for:

* paper metadata
* attachment links
* tags
* collections
* PDF locations

This system may read Zotero data, but must not modify Zotero data directly.

### This repository stores derived workflow data

This repository may store:

* derived indexes
* queues
* approval records
* theme packets
* Markdown reading outputs
* scripts
* templates
* skill definitions
* configuration files

This repository must not store:

* `zotero.sqlite`
* Zotero backup databases
* original Zotero PDFs
* raw Zotero `storage/` contents
* large temporary extraction caches
* credentials or API keys

---

## Language and writing style

Default language: Chinese.

Writing style:

* formal
* concise
* academically precise
* structured
* evidence-grounded

Avoid:

* unsupported claims
* fabricated details
* vague praise
* invented terminology
* unnecessary repetition

When uncertain, write directly:

```text
文中未说明。
```

or:

```text
我不知道。
```

Do not invent missing methods, equations, baselines, numbers, datasets, page numbers, or claims.

---

## Evidence rules

When analyzing papers, separate:

1. what the paper explicitly says
2. what can be reasonably inferred from the paper
3. critical judgment by the assistant

When citing paper content, include the most precise available source location.

Preferred citation format:

```text
（文件名：xxx.pdf，第 x 页）
```

If page numbers cannot be reliably extracted, write:

```text
页码未能可靠识别。
```

Do not silently omit evidence locations when making paper-specific claims.

---

## Zotero access rules

Zotero paths are configured in:

```text
config/paths.toml
```

Expected fields:

```toml
[zotero]
data_dir = "~/Zotero"
storage_dir = "~/Zotero/storage"
db_path = "~/Zotero/zotero.sqlite"
```

On Windows, the path may be similar to:

```text
C:\Users\<UserName>\Zotero
```

If the configured Zotero path does not exist, stop the Zotero-reading step and report the missing path.

Do not guess an alternative path.

### Strict read-only policy

Never modify:

```text
zotero.sqlite
zotero.sqlite.bak
storage/
```

Never move, rename, delete, rewrite, or re-organize original Zotero PDF files.

When reading Zotero data, use read-only access or a temporary copy of the database.

Prefer reading `zotero.sqlite` through a temporary copy or an explicit SQLite read-only connection, such as `mode=ro` or `immutable=1`, to avoid creating or modifying SQLite sidecar files.

All derived data must be written inside this repository.

---

## Codex skill layout

This repository stores skill source files under:

```text
skills/
```

Expected skills:

```text
skills/daily-paper-triage/
skills/single-paper-quick-read/
skills/single-paper-deep-read/
skills/theme-coreading/
```

Each skill directory must contain a `SKILL.md`.

For Codex user-level discovery, create symbolic links under:

```text
~/.agents/skills/
```

Expected links:

```text
~/.agents/skills/daily-paper-triage -> ~/.agents/paper-reading-skills/skills/daily-paper-triage
~/.agents/skills/single-paper-quick-read -> ~/.agents/paper-reading-skills/skills/single-paper-quick-read
~/.agents/skills/single-paper-deep-read -> ~/.agents/paper-reading-skills/skills/single-paper-deep-read
~/.agents/skills/theme-coreading -> ~/.agents/paper-reading-skills/skills/theme-coreading
```

Do not duplicate skill directories manually unless explicitly requested.

---

## Repository structure

Expected repository structure:

```text
~/.agents/paper-reading-skills/
├─ AGENTS.md
├─ README.md
├─ config/
├─ skills/
├─ scripts/
├─ templates/
├─ state/
└─ outputs/
```

Directory roles:

```text
config/      Path settings, scoring rules, and theme configuration.
skills/      Codex skill definitions.
scripts/     Local workflow scripts.
templates/   Markdown report templates.
state/       Machine-readable workflow state.
outputs/     Human-readable generated reports.
```

---

## Output locations

Use the following output locations by default:

```text
outputs/daily/     Daily reading digests and quick-read batches.
outputs/papers/    Single-paper quick-read and deep-read reports.
outputs/themes/    Theme-reading packets, matrices, and synthesis reports.
```

Do not write generated reports outside this repository unless explicitly requested.

---

## State rules

Workflow state is stored under:

```text
state/
```

Allowed paper states:

```text
queued
quick_read_done
deep_read_candidate
deep_read_approved
deep_read_done
archived
```

Do not mark a paper as `deep_read_approved` unless the user explicitly approves it or an approval record exists.

Do not mark a paper as `deep_read_done` unless a deep-reading report has actually been generated.

Detailed state schema belongs in:

```text
state/state_schema.md
```

Do not duplicate full state-schema details in skill files.

---

## Daily reading boundary

Daily reading has an approval gate.

The system may:

* build a daily queue
* produce quick-read outputs
* recommend deep-reading candidates

The system must not:

* produce formal deep-reading reports before user approval
* silently change the reading queue source
* silently archive papers

Detailed daily-reading procedure belongs in:

```text
skills/daily-paper-triage/SKILL.md
```

---

## Single-paper reading boundary

Single-paper quick reading and deep reading are separate workflows.

Quick reading is for triage.

Deep reading is for approved papers.

Detailed quick-read procedure belongs in:

```text
skills/single-paper-quick-read/SKILL.md
```

Detailed deep-read procedure belongs in:

```text
skills/single-paper-deep-read/SKILL.md
```

---

## Theme-reading boundary

Theme reading is comparative synthesis, not a sequence of isolated summaries.

Theme reading should compare papers through shared dimensions and clearly state when papers are not directly comparable.

Detailed theme-reading procedure belongs in:

```text
skills/theme-coreading/SKILL.md
```

---

## Git rules

Commit workflow code and human-readable outputs as appropriate.

Commit:

```text
AGENTS.md
README.md
config/
skills/
scripts/
templates/
state/*.md
state/*.json
state/*.jsonl
outputs/**/*.md
```

Do not commit:

```text
~/Zotero/
~/Zotero/storage/
~/Zotero/zotero.sqlite
*.sqlite
*.sqlite-bak
*.bak
*.pdf
.env
state/cache/
state/tmp/
```

Generated Markdown reports may be committed unless the user decides otherwise.

Large machine-generated caches, extracted page images, temporary full-text dumps, and embeddings should not be committed by default.

Do not commit long verbatim paper excerpts, full-text reproductions, sensitive personal annotations, private attachment paths, credentials, or API keys unless the user explicitly approves it.

---

## Script safety rules

Scripts must be conservative.

Scripts should:

* use UTF-8
* avoid destructive operations
* create destination directories before writing
* report missing configuration clearly
* write derived outputs only inside this repository

Scripts must not:

* delete source files
* modify Zotero source files
* modify Zotero database records
* assume missing paths
* merge suspected duplicate papers automatically

If a PDF is missing, report it and continue with other available papers.

If metadata is missing, mark the field as null or unknown.

If page extraction fails, report the extraction failure.

---

## User research preferences

The user often reads papers in:

* AI
* computer vision
* HCI
* digital art
* generative models
* human-AI co-creation
* digital painting process generation

When relevant, prioritize:

1. task formulation
2. evaluation metrics
3. method mechanism
4. baseline choice
5. ablation logic
6. process-level or interaction-level validity
7. relation to the user's ongoing research

For literature review work, emphasize:

1. taxonomy clarity
2. research arc
3. comparison dimensions
4. gaps and unresolved problems
5. how the paper supports or challenges the user's own framing

---

## Conflict resolution

If this file conflicts with a specific skill, follow this file for global safety, repository, Zotero, Git, and state-boundary rules.

Follow the skill file for task-specific procedure and output structure.

If a required path, queue source, theme packet, or approval record is missing, report the missing item instead of guessing.
