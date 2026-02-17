# Project Planner

A Claude Code plugin for structured project planning with lifecycle skills, review agents, and an HTML dashboard.

## Directory Structure

```
project-planner/
├── CLAUDE.md                     # This file
├── Makefile                      # make dashboard / make open / make clean
├── generate-dashboard.py         # Dashboard generator (Python 3, stdlib only)
├── setup-repo.py                 # Configure a normal repo for planner
├── setup-worktree.py             # Generate worktree-add.sh for bare repos
├── planning-config.json          # Planning configuration
├── .gitignore
├── .claude-plugin/
│   └── plugin.json               # Plugin manifest (name: "planner")
├── setup/                        # Shared library for setup tools
├── commands/                     # Slash commands (auto-namespaced /planner:*)
├── agents/                       # Subagent definitions
├── .claude/
│   └── settings.local.json
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
| `/planner:init` | Bootstrap a new project-planner instance |
| `/planner:research` | Investigate a topic → `Research/<topic>.md` |
| `/planner:brainstorm` | Explore possibilities → `Brainstorm/<topic>.md` |
| `/planner:specify` | Write requirements → `Specs/<feature>/README.md` |
| `/planner:design` | Technical architecture → `Designs/<component>/README.md` |
| `/planner:plan` | Create implementation plan → `Plans/<Name>/` |
| `/planner:breakdown` | Add detail to plan phases |
| `/planner:implement` | Execute a plan phase — implement tasks, track progress |
| `/planner:simplify` | Post-implementation code cleanup and simplification |
| `/planner:code-review` | Review code against the plan — drift, gaps, blind spots |
| `/planner:debrief` | After-action notes for completed phases |
| `/planner:retro` | Capture learnings → `Retro/YYYY-MM-DD-<slug>.md` |
| `/planner:poke-holes` | Adversarial critical analysis of any artifact |
| `/planner:tend` | Artifact hygiene — verify statuses, tags, conventions |
| `/planner:diagram` | Generate Mermaid diagrams from artifacts |
| `/planner:excavate` | Progressive codebase discovery → `Research/<slug>.md` |
| `/planner:setup` | Configure a repo for project-planner (auto-detects bare vs normal) |
| `/planner:dashboard` | Regenerate HTML dashboard |
| `/planner:status` | Quick status summary (read-only) |

## Agents

| Agent | Model | Role |
|-------|-------|------|
| `researcher` | Sonnet | Gathers context from artifacts, codebase, and web |
| `plan-reviewer` | Sonnet | Reviews plans for completeness, feasibility, conventions |
| `spec-reviewer` | Haiku | Reviews specs for testability, completeness, ambiguity |
| `code-reviewer` | Sonnet | Reviews code changes against plan, specs, and designs |

## Workflow Lifecycle

The typical flow through skills:
```
/planner:init → /planner:research → /planner:brainstorm → /planner:specify → /planner:design → /planner:plan → /planner:breakdown → /planner:implement → /planner:code-review → /planner:simplify → /planner:debrief → /planner:retro
```
Use `/planner:dashboard` or `/planner:status` at any point to check progress.
Use `/planner:poke-holes` before approving any artifact. Use `/planner:tend` periodically for hygiene.
Use `/planner:excavate` to understand unfamiliar codebases. Use `/planner:diagram` to visualize any artifact.

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
- `dashboard`: `true` (default) or `false` to disable dashboard generation
- `repositories`: map of external repo keys to GitHub URLs (standalone mode)
- `planMapping`: map of plan names to target repos
- `planRepository`: key for the planning repo itself

### planning-config.local.json (gitignored)
Local filesystem paths for external repositories:
```json
{ "repositories": { "repo-key": { "path": "/absolute/path" } } }
```

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

## Maintenance Rules

When adding, removing, or renaming skills (`commands/`), agents (`agents/`), or modifying user-facing behavior in the setup library (`setup/`), update these files to stay in sync:
- **`README.md`** — command/agent counts, tables, Mermaid diagrams, directory listing
- **`CLAUDE.md`** — skill table, agent table, workflow lifecycle
- **`commands/init.md`** — skill/agent copy lists and counts
- **`Shared/templates/claude-md-standalone.md`** — skill table, agent table, workflow lifecycle
- **`Shared/templates/claude-md-embedded.md`** — skill table
