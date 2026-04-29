# SDD Planner

A Claude Code plugin for spec-driven development — structured project planning with lifecycle skills and review agents. The optional HTML dashboard lives in a companion plugin: [sdd-dashboard](https://github.com/danweinerdev/sdd-dashboard-plugin).

## Directory Structure

```
sdd-planner/                      # Repository root = plugin root
├── .claude-plugin/
│   └── plugin.json               # Plugin manifest (name: "sdd-planner")
├── CLAUDE.md                     # This file
├── Makefile                      # make bump-patch / bump-minor / bump-major
├── planning-config.json          # Planning configuration
├── .gitignore
├── commands/                     # Slash commands (auto-namespaced /sdd-planner:*)
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
└── Retro/                        # Retrospectives
    └── YYYY-MM-DD-<slug>.md
```

## Conventions

### Frontmatter
All artifacts use YAML frontmatter as the machine-readable data layer. See `shared/frontmatter-schema.md` for the complete schema. The companion `sdd-dashboard` plugin reads exclusively from frontmatter — no markdown table parsing.

### VCS-agnostic operations
The plugin works with git, git worktrees, Perforce, and unversioned directories. Skills that inspect files or history detect the VCS first using the algorithm in `shared/vcs-detection.md`, then use the corresponding command from that file's operations table (`git mv` / `p4 move` / plain `mv`, `git diff` / `p4 diff2`, etc.). Don't hard-code `git` in skills.

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
| `/sdd-planner:research` | Investigate a topic → `Research/<topic>.md` |
| `/sdd-planner:brainstorm` | Explore possibilities → `Brainstorm/<topic>.md` |
| `/sdd-planner:specify` | Write requirements → `Specs/<feature>/README.md` |
| `/sdd-planner:design` | Technical architecture → `Designs/<component>/README.md` |
| `/sdd-planner:plan` | Create implementation plan → `Plans/New/<Name>/` |
| `/sdd-planner:breakdown` | Add detail to plan phases |
| `/sdd-planner:implement` | Execute a plan phase — implement tasks, track progress |
| `/sdd-planner:simplify` | Post-implementation code cleanup and simplification |
| `/sdd-planner:code-review` | Review code against the plan — drift, gaps, blind spots |
| `/sdd-planner:debrief` | After-action notes for completed phases |
| `/sdd-planner:retro` | Capture learnings → `Retro/YYYY-MM-DD-<slug>.md` |
| `/sdd-planner:poke-holes` | Adversarial critical analysis of any artifact |
| `/sdd-planner:tend` | Artifact hygiene — verify statuses, tags, conventions |
| `/sdd-planner:diagram` | Generate Mermaid diagrams from artifacts |
| `/sdd-planner:excavate` | Progressive codebase discovery → `Research/<slug>.md` |
| `/sdd-planner:setup` | Set up a repo — generates planning-config.json, bootstraps directories, creates launcher |

## Agents

| Agent | Model | Role |
|-------|-------|------|
| `researcher` | Sonnet | Gathers context from artifacts, codebase, and web |
| `plan-reviewer` | Sonnet | Reviews plans for completeness, feasibility, conventions |
| `spec-reviewer` | Haiku | Reviews specs for testability, completeness, ambiguity |
| `code-implementer` | Opus | Implements code from plan tasks in the target codebase |
| `drift-detector` | Sonnet | Diff + plan only — flags missing work, scope creep, approach drift |
| `quality-scanner` | Sonnet | Diff + code only (intent-blind) — correctness, safety, maintainability, over-engineering |
| `spec-compliance` | Sonnet | Diff + specs/designs only — requirements coverage, contract violations |
| `blind-spot-finder` | Sonnet | Diff only — adversarial fresh-eyes reviewer |

### Code Review Architecture

`/code-review` orchestrates the four specialized reviewers **from the primary context**. Claude Code does not allow subagents to spawn subagents, so the orchestration has to live in the slash command (which runs in the primary context), not in an orchestrator subagent.

1. **`/code-review` (primary context)** identifies the minimum references — plan path, phase doc path, target repo path, diff scope — and resolves just enough planning metadata to dispatch with the right inputs (plan's `related` frontmatter for spec/design paths, a concrete git diff range). It does **not** read plan/spec/design bodies or diff contents.
2. **Four specialized reviewers** are dispatched in parallel via `Task` (a single message with four tool calls) using the plugin-namespaced form: `sdd-planner:drift-detector`, `sdd-planner:quality-scanner`, `sdd-planner:spec-compliance`, `sdd-planner:blind-spot-finder`. Each runs in its own fresh context. Intent isolation is enforced by what they're given:
   - `drift-detector` sees diff + plan (no specs/designs)
   - `quality-scanner` sees diff + code only (intent-blind)
   - `spec-compliance` sees diff + specs/designs (no plan)
   - `blind-spot-finder` sees diff only (no context at all)
3. **Primary context** synthesizes the four reports — highlighting agreements, disagreements, and findings only `blind-spot-finder` caught — and presents the unified review to the user.

**Hard contract**: `/code-review` MUST dispatch the four sub-agents via Task. It MUST NOT read the plan body, spec bodies, design bodies, or full diff and write findings itself — that would collapse the intent isolation and produce a single-pass review cosplaying as a four-lane review. If any dispatch fails, `/code-review` returns a loud error and stops; it does not fall back to self-synthesis.

`drift-detector`, `quality-scanner`, and `blind-spot-finder` are required to validate every finding against the actual code (full file + calling context), not just the diff hunk, because diffs lie by omission.

`/implement` dispatches `quality-scanner` directly (via `sdd-planner:quality-scanner`) for per-task reviews, and `/simplify` dispatches it in `simplify` mode for complexity analysis. Both bypass the full four-lane review because the question they're asking is local to the code at hand.

### MCP Server Inheritance

Agents fall into two groups based on how they handle MCP servers:

**Inherit all session tools (no `tools:` frontmatter)** — these agents automatically pick up whatever MCP servers the user's project has configured (e.g., `context7` for docs, Linear/Jira MCPs for tickets, Slack, Notion, etc.):
- `researcher` — uses doc-lookup MCPs for library research; falls back to WebFetch/WebSearch
- `code-implementer` — uses doc-lookup MCPs to verify current API syntax while writing code
- `quality-scanner` — uses doc-lookup MCPs when judging whether diff code uses a library correctly

**Restricted allowlist (`tools:` frontmatter)** — intent isolation matters more than MCP access:
- `plan-reviewer`, `spec-reviewer` — narrow artifact review; no need for outside tools
- `drift-detector`, `spec-compliance`, `blind-spot-finder` — each is deliberately given only what its lane needs. Adding MCPs to these would dilute the intent isolation that makes the orchestrated review valuable.

The inheriting agents carry behavioral guardrails in their bodies (`researcher` and `quality-scanner` are read-only even though they could technically inherit Write/Edit from the session). Projects that want stricter guarantees can drop overrides into `.claude/agents/<name>.md` at the project level — those take precedence over plugin-provided agents.

## Workflow Lifecycle

The typical flow through skills:
```
/sdd-planner:setup → /sdd-planner:research → /sdd-planner:brainstorm → /sdd-planner:specify → /sdd-planner:design → /sdd-planner:plan → /sdd-planner:breakdown → /sdd-planner:implement → /sdd-planner:code-review → /sdd-planner:simplify → /sdd-planner:debrief → /sdd-planner:retro
```
Install the companion [`sdd-dashboard`](https://github.com/danweinerdev/sdd-dashboard-plugin) plugin to add `/sdd-dashboard:dashboard` (HTML dashboard) and `/sdd-dashboard:status` (quick text summary) for checking progress.
Use `/sdd-planner:poke-holes` before approving any artifact. Use `/sdd-planner:tend` periodically for hygiene.
Use `/sdd-planner:excavate` to understand unfamiliar codebases. Use `/sdd-planner:diagram` to visualize any artifact.

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
- `planningRoot`: where artifacts live, as a path. Use `"."` if planning artifacts are at the repo root, a relative subdirectory name (e.g., `"Planning"`) if they live inside a project, or an absolute path (e.g., `"/home/user/Code/my-planning-repo"`) if they live in an external directory shared by multiple repos. There is no other distinction — the path is just a path.
- `repositories`: map of external repo keys to GitHub URLs (used when plans target code in other repos)
- `planMapping`: map of plan names to target repos
- `planRepository`: key for the planning repo itself

The companion `sdd-dashboard` plugin reads two additional fields when generating its HTML dashboard: `dashboard: true` (opt-in switch), and `title` / `description` for the page chrome. They are ignored if the plugin isn't installed.

### planning-config.local.json (gitignored)
Local filesystem paths for external repositories:
```json
{ "repositories": { "repo-key": { "path": "/absolute/path" } } }
```

## Dashboard

The HTML dashboard previously lived here has moved to a companion plugin: [`sdd-dashboard`](https://github.com/danweinerdev/sdd-dashboard-plugin). Install it alongside `sdd-planner` to get `/sdd-dashboard:dashboard` (HTML) and `/sdd-dashboard:status` (text summary). The dashboard is opt-in via `"dashboard": true` in `planning-config.json`.

## Maintenance Rules

When adding, removing, or renaming skills (`commands/`), agents (`agents/`), or modifying user-facing behavior, update these files to stay in sync:
- **`README.md`** — command/agent counts, tables, Mermaid diagrams, directory listing
- **`CLAUDE.md`** — skill table, agent table, workflow lifecycle
- **`shared/templates/claude-md-full.md`** — full CLAUDE.md template for a planning-only repo (skill table, agent table, workflow lifecycle)
- **`shared/templates/claude-md-snippet.md`** — embeddable section to drop into an existing project's CLAUDE.md (skill table only)

## Versioning

The plugin uses `vMAJOR.MINOR.PATCH` semver. The version is declared in `.claude-plugin/plugin.json`. Claude Code caches plugins by version — **users will not see changes unless the version is bumped**.

| Bump | When | Command |
|------|------|---------|
| **patch** | Bug fix, wording tweak, small correction | `make bump-patch` |
| **minor** | New or completed feature, new skill, meaningful behavior change | `make bump-minor` |
| **major** | Breaking changes to artifact format, config schema, or skill interface | `make bump-major` |

Each `make bump-*` target updates `plugin.json`, creates a commit (`v1.2.3`), and adds a git tag (`v1.2.3`). Always bump before pushing a release.
