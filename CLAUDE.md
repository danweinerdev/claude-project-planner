# Project Planner

A Claude Code plugin for structured project planning with lifecycle skills, review agents, and an HTML dashboard.

## Directory Structure

```
project-planner/
├── CLAUDE.md                     # This file
├── Makefile                      # make dashboard / make open / make clean
├── generate-dashboard.py         # Dashboard generator (Python 3, stdlib only)
├── dashboard-config.json         # Dashboard metadata
├── .gitignore
├── .claude/
│   ├── settings.local.json
│   ├── skills/                   # Slash-command skills
│   └── agents/                   # Subagent definitions
├── Shared/
│   ├── frontmatter-schema.md     # Single source of truth for artifact metadata
│   └── templates/                # Document templates
├── Research/                     # Research artifacts (flat)
├── Brainstorm/                   # Brainstorm artifacts (flat)
├── Specs/                        # Specs (subdirectory per feature)
│   └── <feature>/README.md
├── Designs/                      # Designs (subdirectory per component)
│   └── <component>/README.md
├── Plans/                        # Implementation plans
│   └── <PlanName>/
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
All artifacts use YAML frontmatter as the machine-readable data layer. See `Shared/frontmatter-schema.md` for the complete schema. The dashboard reads exclusively from frontmatter — no markdown table parsing.

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

### File Naming
- Plans: `Plans/<PlanName>/README.md`, `01-Phase-Name.md`
- Phases numbered with zero-padded prefixes: `01-`, `02-`, etc.
- Retros: `YYYY-MM-DD-<slug>.md`
- Specs/Designs: `<Name>/README.md`

### Templates
Always use templates from `Shared/templates/` when creating new artifacts. Replace `{{PLACEHOLDERS}}` with actual values.

## Skills

| Skill | Purpose |
|-------|---------|
| `/research` | Investigate a topic → `Research/<topic>.md` |
| `/brainstorm` | Explore possibilities → `Brainstorm/<topic>.md` |
| `/specify` | Write requirements → `Specs/<feature>/README.md` |
| `/design` | Technical architecture → `Designs/<component>/README.md` |
| `/plan` | Create implementation plan → `Plans/<Name>/` |
| `/breakdown` | Add detail to plan phases |
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

## Workflow Lifecycle

The typical flow through skills:
```
/research → /brainstorm → /specify → /design → /plan → /breakdown → [implement] → /debrief → /retro
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

## Dashboard

Generated via `make dashboard` (or `make open` to also open in browser). Python 3, stdlib only. Reads YAML frontmatter from all artifact types, generates static HTML in `Dashboard/`.

### Dashboard Pages
- `index.html` — stats bar, nav links, in-progress phases, plan cards, recent activity
- `<plan>/index.html` — plan detail with phase status table
- `<plan>/<phase>.html` — phase detail with task table and content
- `knowledge.html` — research + brainstorm index
- `specs.html` — specifications index
- `designs.html` — designs index
- `retros.html` — retrospectives index
- `knowledge/<slug>.html`, `specs/<slug>.html`, etc. — artifact detail pages
