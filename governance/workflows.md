# Workflows

## Main Reading Workflow

```text
daily trigger
  -> quick read
  -> deep read candidate recommendation
  -> user approval
  -> formal deep read
  -> deep-read interaction
  -> user-edited deep-read document
```

## Co-reading Workflow

```text
deep-read papers
  -> user-selected collection / theme
  -> theme co-reading
  -> comparison matrix
  -> synthesis report
  -> add papers during co-reading when needed
```

## Site-mediated Workflow

```text
user action on site
  -> repository-local state/output update
  -> optional external Codex skill invocation
  -> result persisted in outputs/ or state/
  -> site refreshes dashboard
```

## Workflow Boundaries

Formal deep read 必须经过 user approval。
Site 可以触发 Codex，但不应静默改变核心工作流规则。
Co-reading collection 与 add-paper-during-coreading 仍未完全定型；见 `explorations/`。
