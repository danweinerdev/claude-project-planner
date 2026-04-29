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
- `planningRoot` of `"/absolute/path"` → artifacts in an external directory

**Templates and schema** (`shared/`) are read from the **plugin directory**, not from the planning root. The plugin directory contains `commands/`, `agents/`, and `shared/` as siblings — find it by globbing for `**/commands/research.md` in both the current directory and `~/.claude/plugins/cache/`. If multiple matches are found (e.g., multiple cached plugin versions), sort by version number and use the highest. Then go one level up.

## When to Use
- Artifacts have accumulated and status is unclear
- Before starting new work, to understand what's active
- Periodically, to keep planning artifacts healthy
- After completing a feature cycle (good time to archive)
- When the plan artifacts feel out of sync with reality

## Pre-flight: Legacy Layout Detection

Before running any mode, check whether `Plans/` uses the **legacy flat layout** (plan directories directly under `Plans/`) instead of the current **status subfolder layout** (`Plans/{New,Ready,Active,Complete}/`).

**Detection**: List the contents of `Plans/`. If there are plan directories (containing `README.md`) directly under `Plans/` — i.e., not inside `New/`, `Ready/`, `Active/`, or `Complete/` — the layout is legacy.

If legacy layout is detected:

1. **Report** the finding and show which plans were detected:
   ```
   Legacy Plans/ layout detected — plans are stored flat instead of in status subfolders.

   Found N plans to migrate:
     - PlanName (status: active) → Plans/Active/PlanName/
     - OtherPlan (status: complete) → Plans/Complete/OtherPlan/
     - NewPlan (status: draft) → Plans/New/NewPlan/
   ```

2. **Warn** the user:
   ```
   This migration will move plan directories into status subfolders (New/, Ready/, Active/, Complete/).
   It will cause a significant number of file moves in version control.
   This is completely optional — the plugin still supports the flat layout as a fallback.
   ```

3. **Wait for confirmation**. If the user declines, skip the migration and continue to the requested mode(s) normally.

4. **If confirmed**, perform the migration:
   - Create `Plans/New/`, `Plans/Ready/`, `Plans/Active/`, `Plans/Complete/` if they don't exist
   - For each plan directory directly under `Plans/`:
     - Read the plan's `README.md` frontmatter `status` field
     - Map status to folder: `draft` → `New/`, `approved` → `Ready/`, `active` → `Active/`, `complete` or `archived` → `Complete/`
     - If status is missing or unrecognized, default to `New/`
     - Use the VCS-appropriate move command from `shared/vcs-detection.md` to move the plan directory into the appropriate status folder
   - After all moves, report the results

If status subfolders already exist (even if empty), skip this check entirely — the layout is already migrated.

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
/tend migrate            # Run only legacy layout migration check
/tend status             # Run only status mode
/tend tags               # Run only tags mode
/tend filenames          # Run only filenames mode
/tend completeness       # Run only completeness mode
```

## Common Pattern

All modes follow delegate-scan → review-findings → confirm → apply:

1. **Scan**: Invoke the `sdd-planner:researcher` agent to scan artifacts and gather findings (no changes made)
2. **Report**: Primary context presents the agent's findings in categorized format
3. **Confirm**: Wait for user decisions on proposed changes
4. **Apply**: Make confirmed changes and report final state

Never skip confirmation for changes to existing content.

## Mode Details

### Status Mode
Invoke the `sdd-planner:researcher` agent to scan all four status folders (`Plans/New/`, `Plans/Ready/`, `Plans/Active/`, `Plans/Complete/`) and compare status fields against reality. The agent returns a list of findings — what is stale, what is inconsistent, and what should be updated. Checks to perform:
- Plans with all phases complete but plan status is still `active` → suggest `complete`
- Phases where all tasks are complete but phase status is `in-progress` → suggest `complete`
- Specs/designs marked `approved` but their plan is `complete` → suggest `implemented`
- Research/brainstorm still `active` but older than 30 days with no recent changes → flag as potentially stale
- Phase status `in-progress` but no task has started → flag inconsistency
- Plan folder does not match frontmatter status (e.g., plan in `New/` but status is `active`, or plan in `Active/` but all phases complete) → suggest moving to the correct folder
- Plans in `Active/` with all phases complete → suggest moving to `Complete/`

### Tags Mode
Invoke the `sdd-planner:researcher` agent to scan all artifact frontmatter for tags and analyze for variants, orphans, missing tags, and clusters. The agent returns the analysis. Checks to perform:
- **Variants**: Find tags that are likely the same thing (`api`/`APIs`/`rest-api`)
- **Orphans**: Tags used in only one document (might be too specific)
- **Missing**: Artifacts with empty tags that could be inferred from content
- **Clusters**: Groups of artifacts that share tag patterns (reveals implicit categories)

### Filenames Mode
Invoke the `sdd-planner:researcher` agent to check naming conventions across all artifacts. The agent returns any violations found. Conventions to check (defined in CLAUDE.md):
- Plans: `Plans/{New,Ready,Active,Complete}/<PlanName>/README.md`, phases `01-Phase-Name.md`
- Specs: `Specs/<FeatureName>/README.md`
- Designs: `Designs/<ComponentName>/README.md`
- Research: `Research/<topic-slug>.md` (kebab-case)
- Brainstorm: `Brainstorm/<topic-slug>.md` (kebab-case)
- Retro: `Retro/YYYY-MM-DD-<slug>.md`
- Phase numbering: zero-padded, sequential, no gaps

### Completeness Mode
Invoke the `sdd-planner:researcher` agent to check each artifact against `shared/frontmatter-schema.md`. The agent returns missing fields and empty sections. Checks to perform:
- Required frontmatter fields present (title, type, status, created, updated)
- Body has expected sections per template
- Plans have at least one phase defined
- Phases have at least one task defined
- Related links point to artifacts that exist

## Sequential Execution

When running `/tend` without arguments:

1. Run legacy layout detection pre-flight (if applicable)
2. Run status mode to completion
3. Ask: "Status complete. Continue to tags?"
4. On confirmation, run tags mode
5. Ask: "Tags complete. Continue to filenames?"
6. On confirmation, run filenames mode
7. Ask: "Filenames complete. Continue to completeness?"
8. On confirmation, run completeness mode
9. Present final summary

User can stop after any mode.

## Output
Modifies artifacts in place based on user-confirmed changes. No new artifacts created.

## Context
- Orchestration: `shared/orchestration.md`
- Schema: `shared/frontmatter-schema.md`
- Conventions: `CLAUDE.md`
- Agent: `sdd-planner:researcher`
