---
name: tend
description: "Artifact hygiene — verify statuses, unify tags, check conventions, clean up stale artifacts. Triggers: /tend, tend, check health, what's stale, artifact hygiene, tag audit, organize"
---

# /tend — Artifact Hygiene

## Path Resolution
**Artifacts** (Plans/, Research/, Specs/, etc.) are read from and written to the **planning root**.
Read `planning-config.json` (at repo root) to find the planning root:
- `planningRoot` of `"."` or absent → artifacts at repository root
- `planningRoot` of `"<dir>"` → artifacts under `<dir>/` from repo root
- `planningRoot` of `"/absolute/path"` → artifacts in an external directory (standalone planning repo)

**Templates and schema** (`Shared/`) are read from the **plugin directory** (the project-planner repo loaded via `--plugin-dir`), not from the planning root.

Run dashboard commands (`make dashboard`) from the planning root directory.

## When to Use
- Artifacts have accumulated and status is unclear
- Before starting new work, to understand what's active
- Periodically, to keep planning artifacts healthy
- After completing a feature cycle (good time to archive)
- When the dashboard feels out of sync with reality

## Modes

| Mode | Purpose | Produces |
|------|---------|----------|
| `status` | Verify and update document status fields | Accuracy: documents reflect reality |
| `tags` | Unify tag variants, find connections, identify clusters | Semantics: tags are consistent and meaningful |
| `filenames` | Check naming conventions, suggest renames | Findability: names match content |
| `completeness` | Check for missing frontmatter fields, empty sections | Quality: artifacts are well-formed |

**Dependency chain**: status → tags → filenames → completeness

Each mode builds on prior work. Status must be accurate before tag analysis is meaningful.

## Invocation

```
/tend                    # Run all modes sequentially (pause between each)
/tend status             # Run only status mode
/tend tags               # Run only tags mode
/tend filenames          # Run only filenames mode
/tend completeness       # Run only completeness mode
```

## Common Pattern

All modes follow dry-run → confirm → apply:

1. **Scan**: Gather information without changing anything
2. **Report**: Present findings in categorized format
3. **Confirm**: Wait for user decisions on proposed changes
4. **Apply**: Make confirmed changes and report final state

Never skip confirmation for changes to existing content.

## Mode Details

### Status Mode
Scan all artifacts and verify status fields match reality:
- Plans with all phases complete but plan status is still `active` → suggest `complete`
- Phases where all tasks are complete but phase status is `in-progress` → suggest `complete`
- Specs/designs marked `approved` but their plan is `complete` → suggest `implemented`
- Research/brainstorm still `active` but older than 30 days with no recent changes → flag as potentially stale
- Phase status `in-progress` but no task has started → flag inconsistency

### Tags Mode
Scan all artifact frontmatter for tags and analyze:
- **Variants**: Find tags that are likely the same thing (`api`/`APIs`/`rest-api`)
- **Orphans**: Tags used in only one document (might be too specific)
- **Missing**: Artifacts with empty tags that could be inferred from content
- **Clusters**: Groups of artifacts that share tag patterns (reveals implicit categories)

### Filenames Mode
Check naming conventions defined in CLAUDE.md:
- Plans: `Plans/<PlanName>/README.md`, phases `01-Phase-Name.md`
- Specs: `Specs/<FeatureName>/README.md`
- Designs: `Designs/<ComponentName>/README.md`
- Research: `Research/<topic-slug>.md` (kebab-case)
- Brainstorm: `Brainstorm/<topic-slug>.md` (kebab-case)
- Retro: `Retro/YYYY-MM-DD-<slug>.md`
- Phase numbering: zero-padded, sequential, no gaps

### Completeness Mode
Check each artifact against `Shared/frontmatter-schema.md`:
- Required frontmatter fields present (title, type, status, created, updated)
- Body has expected sections per template
- Plans have at least one phase defined
- Phases have at least one task defined
- Related links point to artifacts that exist

## Sequential Execution

When running `/tend` without arguments:

1. Run status mode to completion
2. Ask: "Status complete. Continue to tags?"
3. On confirmation, run tags mode
4. Ask: "Tags complete. Continue to filenames?"
5. On confirmation, run filenames mode
6. Ask: "Filenames complete. Continue to completeness?"
7. On confirmation, run completeness mode
8. Present final summary

User can stop after any mode.

## Output
Modifies artifacts in place based on user-confirmed changes. No new artifacts created.

After making changes:
- Run `make dashboard` from the planning root to update the HTML dashboard

## Context
- Schema: `Shared/frontmatter-schema.md`
- Conventions: `CLAUDE.md`
