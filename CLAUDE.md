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
| `code-reviewer` | Sonnet | **Orchestrator** — dispatches the 4 specialized reviewers in parallel and synthesizes their reports |
| `drift-detector` | Sonnet | Diff + plan only — flags missing work, scope creep, approach drift |
| `quality-scanner` | Sonnet | Diff + code only (intent-blind) — correctness, safety, maintainability, over-engineering |
| `spec-compliance` | Sonnet | Diff + specs/designs only — requirements coverage, contract violations |
| `blind-spot-finder` | Sonnet | Diff only — adversarial fresh-eyes reviewer |

### Code Review Architecture

`/code-review` uses a **tiered dispatch** model to keep the primary context lean while preserving intent isolation between reviewers:

1. **Primary context** (`/code-review` command) identifies only the minimum references: plan path, phase doc path, target repo path, and diff scope. It does **not** read plans, specs, designs, or git diffs.
2. **`code-reviewer` orchestrator** (fresh context) loads everything itself — plan, phase, related specs/designs, prior debriefs, diffs — then dispatches the four specialized reviewers in parallel, each with exactly the inputs for its lane.
3. **Specialized reviewers** each run in their own fresh context. Intent isolation is enforced by what they're given:
   - `drift-detector` sees diff + plan (no specs/designs)
   - `quality-scanner` sees diff + code only (intent-blind)
   - `spec-compliance` sees diff + specs/designs (no plan)
   - `blind-spot-finder` sees diff only (no context at all)
4. **`code-reviewer`** synthesizes the four reports — highlighting agreements, disagreements, and findings only `blind-spot-finder` caught — and returns one complete report (synthesis + raw sub-reports) back to primary.

`drift-detector`, `quality-scanner`, and `blind-spot-finder` are required to validate every finding against the actual code (full file + calling context), not just the diff hunk, because diffs lie by omission.

`/implement` and `/simplify` bypass the orchestrator and invoke `quality-scanner` directly for fast intent-blind quality checks on a single task or file.

### MCP Server Inheritance

Agents fall into two groups based on how they handle MCP servers:

**Inherit all session tools (no `tools:` frontmatter)** — these agents automatically pick up whatever MCP servers the user's project has configured (e.g., `context7` for docs, Linear/Jira MCPs for tickets, Slack, Notion, etc.):
- `researcher` — uses doc-lookup MCPs for library research; falls back to WebFetch/WebSearch
- `code-implementer` — uses doc-lookup MCPs to verify current API syntax while writing code
- `quality-scanner` — uses doc-lookup MCPs when judging whether diff code uses a library correctly

**Restricted allowlist (`tools:` frontmatter)** — intent isolation matters more than MCP access:
- `plan-reviewer`, `spec-reviewer` — narrow artifact review; no need for outside tools
- `code-reviewer` — orchestrator only; the specialized reviewers it dispatches are where the work happens
- `drift-detector`, `spec-compliance`, `blind-spot-finder` — each is deliberately given only what its lane needs. Adding MCPs to these would dilute the intent isolation that makes the orchestrated review valuable.

The inheriting agents carry behavioral guardrails in their bodies (`researcher` and `quality-scanner` are read-only even though they could technically inherit Write/Edit from the session). Projects that want stricter guarantees can drop overrides into `.claude/agents/<name>.md` at the project level — those take precedence over plugin-provided agents.

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
