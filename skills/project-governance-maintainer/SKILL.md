---
name: project-governance-maintainer
description: Use this skill to orient, triage, and maintain a project's repository governance layer and current-state summary. Trigger when the user asks about current project state, stable consensus, accepted decisions, open explorations, development priorities, governance drift, whether a request should become a Decision or Exploration, wants to update governance records, or needs PROJECT_STATE.md/current-state files kept in sync. Do not use it for domain work, feature implementation, or generated outputs unless governance state is the main task.
---

# Project Governance Maintainer

Use this skill to maintain project governance as a method layer. This skill must not carry project-specific conclusions. Read project facts, consensus, decisions, explorations, priorities, boundaries, and domain rules from the current repository's `PROJECT_STATE.md`, `governance/`, and repository instruction files.

Always answer in concise Chinese unless the user explicitly requests another language.

## Required Reading

Read these first when present:

1. Repository instruction file, usually `AGENTS.md`.
2. Project state file, usually `PROJECT_STATE.md`.
3. Governance guide, usually `governance/README.md`.

If a required convention is missing, report the missing file and continue only with clearly available project context. Do not invent missing project facts.

Then read only the governance files needed for the request. Common conventions include:

- `governance/project_consensus.md` or equivalent for stable boundaries and current consensus.
- `governance/workflows.md` or equivalent for workflow responsibilities.
- `governance/development_priorities.md` or equivalent for priority order.
- `governance/decision_index.md` and `governance/decisions/` or equivalent for accepted decisions.
- `governance/explorations/` or equivalent for unresolved design questions.
- Other governance files for project-specific components, interfaces, tools, runtimes, user surfaces, data models, or integrations when they exist.

## Operating Modes

### Project Orientation

Use when the user asks what the project currently is, what has been decided, what remains open, what to do next, or whether prior governance covers a question.

Return a concise Chinese answer covering only relevant items:

1. current project identity;
2. stable consensus;
3. relevant accepted decisions;
4. relevant open explorations;
5. current priorities;
6. recommended next action.

Do not modify files in orientation mode unless the user explicitly asks to update governance.

### Governance Triage

Use before governance updates and before coding when a request may change project meaning.

Classify the request as one of:

- Ordinary TODO: already covered by current consensus or accepted decisions. Proceed to implementation or documentation work; do not create a new governance record.
- Exploration: an important unresolved design question with multiple plausible options. Record or update an Exploration and keep it open until a choice is accepted.
- Decision: a confirmed design choice that future work should follow by default. Record a Decision, update the decision index, and update affected consensus or priorities.
- Priority update: a change to development order derived from a Decision, Exploration, or drift finding.
- Drift: a mismatch among project instructions, governance records, documentation, implementation, state, configuration, or user-facing behavior.

Do not turn every TODO into governance. Create or update governance only when project meaning, workflow boundaries, state or data contracts, component responsibilities, interface contracts, tool responsibilities, or development order changes.

### Drift Check

Use when implementation or documentation appears inconsistent with governance.

Check only relevant project files. Typical sources include:

- repository instruction files;
- project state files;
- governance records;
- architecture or workflow documentation;
- configuration and schema files;
- implementation entry points;
- tests or validation scripts;
- generated state or output contracts when the project defines them.

For each mismatch, identify whether it is stale documentation, implementation bug, missing validation, or changed design reality. Update governance only if the accepted project meaning has changed; otherwise treat the issue as ordinary implementation or documentation work.

## Governance Updates

When creating or updating an Exploration, include:

- status;
- question;
- context;
- options;
- trade-offs;
- current leaning, if any;
- what would decide it;
- next step.

When creating or updating a Decision, include:

- accepted choice;
- rationale;
- consequences;
- superseded or related records, if any;
- implementation impact.

After a Decision, update only affected indexes, consensus files, workflow files, component governance files, or priority files. Keep governance concise and avoid copying full procedures from instruction files, skill files, implementation docs, or external specifications.

## Project State Maintenance

When the project has a current-state file, usually `PROJECT_STATE.md`, treat it as a compact current-state index rather than the full governance source of truth.

After any governance update, priority update, accepted Decision, newly opened or closed Exploration, drift finding, or user instruction that changes current project status, check whether the current-state file must be updated in the same turn.

Update the current-state file when any of these change:

- current phase or stage;
- current P0/P1/P2 priorities, if the project tracks them there;
- active Explorations or their status;
- project-specific operating context needed by generic skills;
- source map or required reading order;
- accepted Decision snapshot, if the project keeps one there.

Keep the current-state file concise. Prefer pointers to governance records over copied details. Do not write project facts into this skill; write them into the project's current-state and governance files.

## Priority Rules

Derive priorities from project governance rather than from this skill.

When project-specific priority principles exist, follow them. If they do not, use these fallback heuristics:

- prioritize work that protects correctness, safety, data/state integrity, user decision visibility, and interface contracts;
- prioritize work that unblocks the main workflow before optional enhancements;
- treat purely presentational or convenience improvements as lower priority unless they reduce workflow risk;
- convert open Explorations into design-closure, prototype, or validation priorities when needed;
- downgrade or remove tasks whose underlying Decision has been superseded or reverted.

When updating priorities, state which Decision, Exploration, drift finding, or user instruction caused the change.

## Numbering Rules

Follow the current project's numbering rules. If the project has no rule, use these defaults:

- Decisions: `D0001`, `D0002`, `D0003`, ...
- Explorations: `E0001`, `E0002`, `E0003`, ...

Never delete, renumber, or reuse IDs unless the current project explicitly defines a different archival policy. If an accepted Decision becomes wrong, create a new Decision that supersedes or reverts it.

## Non-goals

Do not:

- encode project facts, domain boundaries, product decisions, or priority conclusions in this skill;
- replace repository-level instruction files;
- duplicate full workflow procedures from other skills, scripts, or project docs;
- approve design Decisions without user confirmation or accepted governance evidence;
- implement open Explorations as accepted design;
- silently change project state, data, outputs, or external systems merely because governance changed.
