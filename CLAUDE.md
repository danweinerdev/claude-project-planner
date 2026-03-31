# Project Planner

A Claude Code plugin for structured project planning with lifecycle skills, review agents, and an HTML dashboard.

## Directory Structure

```
project-planner/                  # Repository root = plugin root
├── .claude-plugin/
│   └── plugin.json               # Plugin manifest (name: "planner")
├── CLAUDE.md                     # This file
├── Makefile                      # make dashboard / make open / make clean / make bump-*
├── generate-dashboard.py         # Dashboard generator (Python 3, stdlib only)
├── planning-config.json          # Planning configuration
├── .gitignore
├── commands/                     # Slash commands (auto-namespaced /planner:*)
├── agents/                       # Subagent definitions
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
| `/planner:research` | Investigate a topic → `Research/<topic>.md` |
| `/planner:brainstorm` | Explore possibilities → `Brainstorm/<topic>.md` |
| `/planner:specify` | Write requirements → `Specs/<feature>/README.md` |
| `/planner:design` | Technical architecture → `Designs/<component>/README.md` |
| `/planner:plan` | Create implementation plan → `Plans/New/<Name>/` |
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
| `/planner:setup` | Set up a repo — generates planning-config.json, bootstraps directories, creates launcher |
| `/planner:dashboard` | Regenerate HTML dashboard |
| `/planner:status` | Quick status summary (read-only) |

## Agents

| Agent | Model | Role |
|-------|-------|------|
| `researcher` | Sonnet | Gathers context from artifacts, codebase, and web |
| `plan-reviewer` | Sonnet | Reviews plans for completeness, feasibility, conventions |
| `spec-reviewer` | Haiku | Reviews specs for testability, completeness, ambiguity |
| `code-implementer` | Opus | Implements code from plan tasks in the target codebase |
| `code-reviewer` | Sonnet | Reviews code changes against plan, specs, and designs |

## Workflow Lifecycle

The typical flow through skills:
```
/planner:setup → /planner:research → /planner:brainstorm → /planner:specify → /planner:design → /planner:plan → /planner:breakdown → /planner:implement → /planner:code-review → /planner:simplify → /planner:debrief → /planner:retro
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
- `dashboard`: `true` to enable dashboard generation (off by default). When enabled, also set `title` and `description` for the dashboard HTML.
- `repositories`: map of external repo keys to GitHub URLs (standalone mode)
- `planMapping`: map of plan names to target repos
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

## Maintenance Rules

When adding, removing, or renaming skills (`commands/`), agents (`agents/`), or modifying user-facing behavior, update these files to stay in sync:
- **`README.md`** — command/agent counts, tables, Mermaid diagrams, directory listing
- **`CLAUDE.md`** — skill table, agent table, workflow lifecycle
- **`shared/templates/claude-md-standalone.md`** — skill table, agent table, workflow lifecycle
- **`shared/templates/claude-md-embedded.md`** — skill table

## Versioning

The plugin uses `vMAJOR.MINOR.PATCH` semver. The version is declared in `.claude-plugin/plugin.json`. Claude Code caches plugins by version — **users will not see changes unless the version is bumped**.

| Bump | When | Command |
|------|------|---------|
| **patch** | Bug fix, wording tweak, small correction | `make bump-patch` |
| **minor** | New or completed feature, new skill, meaningful behavior change | `make bump-minor` |
| **major** | Breaking changes to artifact format, config schema, or skill interface | `make bump-major` |

Each `make bump-*` target updates `plugin.json`, creates a commit (`v1.2.3`), and adds a git tag (`v1.2.3`). Always bump before pushing a release.
