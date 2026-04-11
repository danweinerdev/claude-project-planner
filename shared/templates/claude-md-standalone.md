# {{TITLE}}

{{DESCRIPTION}}

## Directory Structure

```
{{PLANNING_ROOT}}/
├── CLAUDE.md                     # This file
├── Makefile                      # make dashboard / make open / make clean
├── generate-dashboard.py         # Dashboard generator (Python 3, stdlib only)
├── planning-config.json          # Planning configuration
├── .gitignore
├── shared/
│   ├── frontmatter-schema.md     # Single source of truth for artifact metadata
│   └── templates/                # Document templates
├── Research/                     # Research artifacts (flat)
├── Brainstorm/                   # Brainstorm artifacts (flat)
├── Specs/                        # Specs (subdirectory per feature)
│   └── <feature>/README.md
├── Designs/                      # Designs (subdirectory per component)
│   └── <component>/README.md
├── Plans/                        # Implementation plans
│   ├── New/                      # Draft plans, not yet approved
│   ├── Ready/                    # Approved, ready to implement
│   ├── Active/                   # Currently being implemented
│   └── Complete/                 # Done, frozen — AI skips unless asked
│   └── <status>/<PlanName>/
│       ├── README.md             # Frontmatter with phases[], overview
│       ├── 01-Phase-Name.md      # Frontmatter with tasks[], details
│       └── notes/                # After-action notes
│           └── 01-Phase-Name.md  # Debrief for Phase 1
├── Retro/                        # Retrospectives
│   └── YYYY-MM-DD-<slug>.md
└── Dashboard/                    # Generated HTML (gitignored)
```

## Conventions

### Frontmatter
All artifacts use YAML frontmatter as the machine-readable data layer. See `shared/frontmatter-schema.md` for the complete schema. The dashboard reads exclusively from frontmatter — no markdown table parsing.

### Plan Hierarchy
```
Plan (README.md)       <- like a Jira Project
 └── Phase (01-*.md)   <- like a Jira Epic
      └── Task          <- defined in phase frontmatter
           └── Subtask  <- checklist items in body
```

### Status Values
| Level | Statuses |
|-------|----------|
| plan | `draft`, `approved`, `active`, `complete`, `archived` |
| phase | `planned`, `in-progress`, `complete`, `blocked`, `deferred` |
| task | `planned`, `in-progress`, `complete`, `blocked`, `deferred` |

### Plan Lifecycle Folders
Plans move between status folders as they progress:

| Folder | Status | When |
|--------|--------|------|
| `New/` | `draft` | Plan created, not yet reviewed |
| `Ready/` | `approved` | Plan reviewed and approved, waiting to start |
| `Active/` | `active` | Implementation in progress |
| `Complete/` | `complete` | All phases done, plan frozen |

Commands that change plan status also move the plan directory:
- `/plan` creates in `New/`, moves to `Ready/` on approval
- `/implement` moves from `Ready/` to `Active/` when starting
- `/debrief` or `/tend` moves from `Active/` to `Complete/` when all phases are done

AI commands limit their scan scope to relevant folders to reduce context processing.

### File Naming
- Plans: `Plans/{New,Ready,Active,Complete}/<PlanName>/README.md`, `01-Phase-Name.md`
- Phases numbered with zero-padded prefixes: `01-`, `02-`, etc.
- Retros: `YYYY-MM-DD-<slug>.md`
- Specs/Designs: `<Name>/README.md`

### Templates
Always use templates from `shared/templates/` when creating new artifacts. Replace `{{PLACEHOLDERS}}` with actual values.

## Skills

| Skill | Purpose |
|-------|---------|
| `/research` | Investigate a topic → `Research/<topic>.md` |
| `/brainstorm` | Explore possibilities → `Brainstorm/<topic>.md` |
| `/specify` | Write requirements → `Specs/<feature>/README.md` |
| `/design` | Technical architecture → `Designs/<component>/README.md` |
| `/plan` | Create implementation plan → `Plans/New/<Name>/` |
| `/breakdown` | Add detail to plan phases |
| `/code-review` | Orchestrated code review — drift + quality + spec compliance + blind spots |
| `/debrief` | After-action notes for completed phases |
| `/retro` | Capture learnings → `Retro/YYYY-MM-DD-<slug>.md` |
| `/dashboard` | Regenerate HTML dashboard |
| `/status` | Quick status summary (read-only) |

## Agents

| Agent | Model | Role |
|-------|-------|------|
| `researcher` | Sonnet | Gathers context from artifacts, codebase, and web |
| `plan-reviewer` | Sonnet | Reviews plans for completeness, feasibility, conventions |
| `spec-reviewer` | Haiku | Reviews specs for testability, completeness, ambiguity |
| `code-implementer` | Opus | Implements code from plan tasks in the target codebase |
| `code-reviewer` | Sonnet | Orchestrator — dispatches the 4 specialized reviewers in parallel and synthesizes their reports |
| `drift-detector` | Sonnet | Diff + plan only — missing work, scope creep, approach drift |
| `quality-scanner` | Sonnet | Diff + code only (intent-blind) — correctness, safety, maintainability, over-engineering |
| `spec-compliance` | Sonnet | Diff + specs/designs only — requirements coverage, contract violations |
| `blind-spot-finder` | Sonnet | Diff only — adversarial fresh-eyes reviewer |

### Code Review Architecture

`/code-review` uses a tiered dispatch model:

1. **Primary context** passes only references (plan path, phase path, repo path, diff scope) to `code-reviewer`. No diffs or plan content touch primary.
2. **`code-reviewer`** runs in a fresh context, loads plan/phase/specs/designs/diffs itself, then dispatches the four specialized reviewers in parallel with exactly the inputs each lane needs.
3. **Each specialized reviewer** runs in its own fresh context. Intent isolation is enforced by what they're given — `quality-scanner` and `blind-spot-finder` never see the plan, `drift-detector` never sees specs, etc.
4. **`code-reviewer`** synthesizes the four reports — highlighting confirmed findings, disagreements, and blind spots only `blind-spot-finder` caught — and returns one complete report (synthesis + raw sub-reports) to primary.

`drift-detector`, `quality-scanner`, and `blind-spot-finder` are required to validate findings against the full file and calling context, not just the diff hunk.

`/implement` and `/simplify` bypass the orchestrator and invoke `quality-scanner` directly for fast intent-blind checks on a single task or file.

## Workflow Lifecycle

The typical flow through skills:
```
/research → /brainstorm → /specify → /design → /plan → /breakdown → [implement] → /code-review → /debrief → /retro
```
Use `/dashboard` or `/status` at any point to check progress.

## Artifact Status Values

| Type | Statuses |
|------|----------|
| research | `draft`, `active`, `archived` |
| brainstorm | `draft`, `active`, `archived` |
| spec | `draft`, `review`, `approved`, `implemented`, `superseded` |
| design | `draft`, `review`, `approved`, `implemented`, `superseded` |
| debrief | `draft`, `complete` |
| retro | `draft`, `complete` |

## Configuration

### planning-config.json
The planning root's `planning-config.json` drives all path resolution:
- `mode`: `"standalone"` (own repo) or `"embedded"` (subdirectory of project)
- `planningRoot`: `"."` for standalone, subdirectory name for embedded
- `repositories`: map of external repo keys to GitHub URLs (standalone mode)
- `planMapping`: map of plan names to target repos
- `dashboard`: `true` to enable dashboard generation (off by default)
- `planRepository`: key for the planning repo itself

### planning-config.local.json (gitignored)
Local filesystem paths for external repositories:
```json
{ "repositories": { "repo-key": { "path": "/absolute/path" } } }
```

## Dashboard

Opt-in: requires `"dashboard": true` in `planning-config.json`. Generated via `make dashboard` (or `make open` to also open in browser). Python 3, stdlib only. Reads YAML frontmatter from all artifact types, generates static HTML in `Dashboard/`.

### Dashboard Pages
- `index.html` — stats bar, nav links, in-progress phases, plan cards, recent activity
- `<plan>/index.html` — plan detail with phase status table
- `<plan>/<phase>.html` — phase detail with task table and content
- `knowledge.html` — research + brainstorm index
- `specs.html` — specifications index
- `designs.html` — designs index
- `retros.html` — retrospectives index
- `knowledge/<slug>.html`, `specs/<slug>.html`, etc. — artifact detail pages
