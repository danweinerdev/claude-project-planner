# SDD Planner

A [Claude Code](https://docs.anthropic.com/en/docs/claude-code) plugin for spec-driven development — structured project planning end-to-end. It provides slash commands that guide you through a full planning lifecycle — from research to retrospective — with YAML-frontmatter-driven artifacts.

For the optional HTML dashboard view of these artifacts, install the companion [`sdd-dashboard`](https://github.com/danweinerdev/sdd-dashboard-plugin) plugin.

## How It Works

SDD Planner is a standalone Claude Code **plugin**. When loaded (via `--plugin-dir` or through a marketplace), it registers 16 slash commands (namespaced under `/sdd-planner:*`) and 8 review/implementation agents that Claude can delegate to. All artifacts are Markdown files with YAML frontmatter — companion tools (like `sdd-dashboard`) read frontmatter exclusively, so there's no brittle table parsing.

```mermaid
graph LR
    subgraph Plugin ["sdd-planner (plugin)"]
        commands["commands/*.md"]
        agents["agents/*.md"]
        manifest[".claude-plugin/plugin.json"]
    end

    subgraph Claude ["Claude Code"]
        CC[Claude Code CLI]
    end

    subgraph Project ["Your Project"]
        config["planning-config.json"]
        artifacts["Plans/ Research/ Specs/ ..."]
    end

    subgraph Optional ["sdd-dashboard (separate plugin)"]
        dash["Dashboard/ (generated HTML)"]
    end

    CC -->|--plugin-dir| Plugin
    CC -->|reads| config
    commands -->|create & update| artifacts
    artifacts -. "/sdd-dashboard:dashboard" .-> dash
```

## Quick Start

### Use with an existing project (embedded mode)

```bash
# From your project root
claude --plugin-dir /path/to/sdd-planner

# Then inside Claude:
> /sdd-planner:setup
# Generates planning-config.json, bootstraps directories
```

### Use as a standalone planning repo

```bash
# Create a new repo for planning
mkdir my-planning && cd my-planning && git init
claude --plugin-dir /path/to/sdd-planner

# Then inside Claude:
> /sdd-planner:setup
# Generates planning-config.json, bootstraps directories
```

### Use with git worktrees

Run `/sdd-planner:setup` in each worktree. Setup auto-detects worktrees and inherits `planningRoot` from siblings:

```bash
# In the first worktree — provide the planning root explicitly
claude --plugin-dir /path/to/sdd-planner
> /sdd-planner:setup /path/to/worktree --planning-root /path/to/planning-repo

# In subsequent worktrees — settings are inherited automatically
> /sdd-planner:setup /path/to/another-worktree
```

Each worktree gets its own `planning-config.json` and `claude.sh` launcher.

## Slash Commands

All commands are namespaced as `/sdd-planner:*` automatically by the plugin system.

### Lifecycle Commands

| Command | Purpose | Output |
|---------|---------|--------|
| `/sdd-planner:setup` | Set up a repo for planner | `planning-config.json`, `claude.sh`, directories |
| `/sdd-planner:research` | Investigate a topic | `Research/<topic>.md` |
| `/sdd-planner:brainstorm` | Explore possibilities | `Brainstorm/<topic>.md` |
| `/sdd-planner:specify` | Write requirements | `Specs/<feature>/README.md` |
| `/sdd-planner:design` | Technical architecture | `Designs/<component>/README.md` |
| `/sdd-planner:plan` | Create implementation plan | `Plans/New/<Name>/README.md` + phase docs |
| `/sdd-planner:breakdown` | Add detail to plan phases | Updates phase `.md` with tasks/subtasks |
| `/sdd-planner:implement` | Execute a plan phase | Code + updated task/phase statuses |
| `/sdd-planner:code-review` | Review code — orchestrated drift + quality + spec + blind-spot review | Unified report (synthesis + raw sub-reports) |
| `/sdd-planner:simplify` | Post-implementation cleanup | Simplified code, tests verified |
| `/sdd-planner:debrief` | After-action notes | `Plans/Active/<Name>/notes/<phase>.md` |
| `/sdd-planner:retro` | Capture learnings | `Retro/YYYY-MM-DD-<slug>.md` |

### Utility Commands

| Command | Purpose | Output |
|---------|---------|--------|
| `/sdd-planner:poke-holes` | Adversarial critical analysis | Inline findings (no artifact) |
| `/sdd-planner:tend` | Artifact hygiene | Updates stale statuses, tags, conventions |
| `/sdd-planner:diagram` | Generate Mermaid diagrams | `Diagrams/<subject>.md` or inline |
| `/sdd-planner:excavate` | Progressive codebase discovery | `Research/<codebase>.md` |

For the HTML dashboard and quick text status, install the companion [`sdd-dashboard`](https://github.com/danweinerdev/sdd-dashboard-plugin) plugin. It adds `/sdd-dashboard:dashboard` and `/sdd-dashboard:status`.

## Workflow Lifecycle

Commands follow a natural planning progression. You don't have to use every step — jump in wherever makes sense. Utility commands can be used at any point.

```mermaid
graph TD
    research["/sdd-planner:research"] --> brainstorm["/sdd-planner:brainstorm"]
    brainstorm --> specify["/sdd-planner:specify"]
    specify --> design["/sdd-planner:design"]
    design --> plan["/sdd-planner:plan"]
    plan --> breakdown["/sdd-planner:breakdown"]
    breakdown --> implement["/sdd-planner:implement"]
    implement --> codereview["/sdd-planner:code-review"]
    codereview --> simplify["/sdd-planner:simplify"]
    simplify --> debrief["/sdd-planner:debrief"]
    debrief --> retro["/sdd-planner:retro"]

    poke["⚡ /sdd-planner:poke-holes"]
    tend["🔧 /sdd-planner:tend"]
    diagram["📊 /sdd-planner:diagram"]
    excavate["🔍 /sdd-planner:excavate"]

    poke -. "before approving" .-> specify
    poke -. "before approving" .-> design
    poke -. "before approving" .-> plan
    excavate -. "understand code" .-> research

    classDef discovery fill:#4a6741,stroke:#333,color:#fff
    classDef definition fill:#5a4a7a,stroke:#333,color:#fff
    classDef execution fill:#6a5a3a,stroke:#333,color:#fff
    classDef implementation fill:#7a4a4a,stroke:#333,color:#fff
    classDef review fill:#3a5a6a,stroke:#333,color:#fff
    classDef utility fill:#555,stroke:#333,color:#fff

    class research,brainstorm discovery
    class specify,design definition
    class plan,breakdown execution
    class implement,codereview,simplify implementation
    class debrief,retro review
    class poke,tend,diagram,excavate utility
```

| Phase | Commands | What happens |
|-------|----------|-------------|
| **Setup** | `setup` | Configure a repo for planner |
| **Discovery** | `research`, `brainstorm`, `excavate` | Gather context, explore options, map codebases |
| **Definition** | `specify`, `design` | Lock down requirements and architecture |
| **Execution** | `plan`, `breakdown` | Structure work into phases, tasks, subtasks |
| **Implementation** | `implement`, `code-review`, `simplify` | Build it, verify it, then clean it up |
| **Review** | `debrief`, `retro` | Capture what happened and what you learned |
| **Utilities** | `poke-holes`, `tend`, `diagram`, `excavate` | Challenge, maintain, visualize, explore |

## Plan Hierarchy

Plans follow a four-level hierarchy, similar to Jira's project structure:

```mermaid
graph TD
    Plan["Plan (README.md)"] --> Phase1["Phase 1 (01-Setup.md)"]
    Plan --> Phase2["Phase 2 (02-API.md)"]
    Plan --> Phase3["Phase 3 (03-UI.md)"]
    Phase1 --> T1["Task 1.1"]
    Phase1 --> T2["Task 1.2"]
    T1 --> S1["☐ Subtask"]
    T1 --> S2["☐ Subtask"]
    T2 --> S3["☐ Subtask"]

    classDef plan fill:#5a4a7a,stroke:#333,color:#fff
    classDef phase fill:#4a6741,stroke:#333,color:#fff
    classDef task fill:#6a5a3a,stroke:#333,color:#fff
    classDef sub fill:#555,stroke:#333,color:#fff

    class Plan plan
    class Phase1,Phase2,Phase3 phase
    class T1,T2 task
    class S1,S2,S3 sub
```

| Level | Stored in | Status values |
|-------|-----------|---------------|
| **Plan** | `Plans/{New,Ready,Active,Complete}/<Name>/README.md` frontmatter | `draft` `approved` `active` `complete` `archived` |
| **Phase** | `Plans/<status>/<Name>/01-Phase.md` frontmatter | `planned` `in-progress` `complete` `blocked` `deferred` |
| **Task** | Phase frontmatter `tasks:` array | `planned` `in-progress` `complete` `blocked` `deferred` |
| **Subtask** | Phase body as `- [ ]` checklists | Checkbox state |

## Agents

The plugin includes review agents that Claude can delegate to:

| Agent | Model | Purpose |
|-------|-------|---------|
| `researcher` | Sonnet | Gathers context from artifacts, codebase, and web |
| `plan-reviewer` | Sonnet | Reviews plans for completeness, feasibility, and conventions |
| `spec-reviewer` | Haiku | Reviews specs for testability, completeness, and ambiguity |
| `code-implementer` | Opus | Implements code from plan tasks in the target codebase |
| `drift-detector` | Sonnet | Diff + plan only — missing work, scope creep, approach drift |
| `quality-scanner` | Sonnet | Diff + code only (intent-blind) — correctness, safety, maintainability, over-engineering |
| `spec-compliance` | Sonnet | Diff + specs/designs only — requirements coverage, contract violations |
| `blind-spot-finder` | Sonnet | Diff only — adversarial fresh-eyes reviewer |

### Code Review Architecture

`/code-review` dispatches the four specialized reviewers **from the primary context** (the slash command itself), because Claude Code does not allow subagents to spawn other subagents. The orchestration is inside the slash command, not an intermediate orchestrator agent.

```mermaid
graph TD
    primary["Primary context<br/>(/code-review command)<br/>loads only metadata,<br/>dispatches + synthesizes"]
    drift["sdd-planner:drift-detector<br/>diff + plan"]
    qual["sdd-planner:quality-scanner<br/>diff + code<br/>(intent-blind)"]
    spec["sdd-planner:spec-compliance<br/>diff + specs/designs"]
    blind["sdd-planner:blind-spot-finder<br/>diff only"]

    primary -->|parallel Task dispatch| drift
    primary -->|parallel Task dispatch| qual
    primary -->|parallel Task dispatch| spec
    primary -->|parallel Task dispatch| blind
    drift --> primary
    qual --> primary
    spec --> primary
    blind --> primary
    primary -->|synthesized report| user["User"]

    classDef primary fill:#5a4a7a,stroke:#333,color:#fff
    classDef sub fill:#3a5a6a,stroke:#333,color:#fff
    classDef user fill:#4a6741,stroke:#333,color:#fff

    class primary primary
    class drift,qual,spec,blind sub
    class user user
```

- **Primary context (`/code-review`)** identifies the plan/phase/repo/diff-scope references, reads only the plan's `related` frontmatter to find spec/design paths, and resolves a concrete `git diff` range. It does **not** read plan bodies, spec bodies, design bodies, or full diff contents.
- **Four specialized reviewers** run in parallel in their own fresh contexts. Each sees only the inputs for its lane. `blind-spot-finder` in particular sees only the diff — no plan, no specs, no designs — because its adversarial value depends on that isolation.
- **`drift-detector`, `quality-scanner`, and `blind-spot-finder`** validate every finding against the full file and calling context, not just the diff hunk, because diffs lie by omission.
- **Primary context** then synthesizes the four reports — highlighting confirmed findings (caught by 2+ reviewers), disagreements between reviewers (often the most valuable signal), and blind spots only `blind-spot-finder` caught — and presents the unified review to the user.

**Hard contract:** `/code-review` must dispatch the four sub-agents via Task. It must not do the review in primary and present it as a four-lane result. If any dispatch fails, the command returns a loud error and stops — there is no fallback to self-synthesis.

`/implement` dispatches `quality-scanner` directly after each task for a fast intent-blind quality check. `/simplify` dispatches it in `simplify` mode for complexity analysis. Both bypass the full four-lane review because the question they're asking is local to the code at hand.

### MCP Server Inheritance

The plugin aims to be **generic** — it should work with whatever MCP servers your project has configured without hard-coding server names. It achieves this by splitting agents into two groups:

| Group | Agents | Behavior |
|---|---|---|
| **Inherit session tools** (no `tools:` frontmatter) | `researcher`, `code-implementer`, `quality-scanner` | Automatically pick up any MCP servers available in the session — `context7`, Linear, Notion, Slack, whatever. They use these for library docs, ticket lookups, and API verification. Guardrails in the agent body keep `researcher` and `quality-scanner` read-only. |
| **Restricted allowlist** (`tools:` frontmatter) | `plan-reviewer`, `spec-reviewer`, `drift-detector`, `spec-compliance`, `blind-spot-finder` | Tight allowlist of built-in tools only. No MCP access. These agents depend on intent isolation — the value of `blind-spot-finder` is that it's given only the diff; adding MCPs would dilute that. |

If you want stricter guarantees on the inheriting agents (e.g., preventing `code-implementer` from touching your ticketing MCP), drop an override into your project's `.claude/agents/<name>.md` — project-local agents take precedence over plugin-provided ones and can declare an explicit `tools:` list of your choosing.

Recommended MCP servers to install for the best experience:
- **context7** — current library docs. `researcher`, `code-implementer`, and `quality-scanner` all benefit immediately.
- Any project-relevant knowledge-base MCP (Linear, Notion, Confluence, Jira) — `researcher` will use them to pull in reverse references during planning.

## Deployment Modes

```mermaid
graph TB
    subgraph standalone ["Standalone Mode"]
        direction TB
        PR["Planning Repo"]
        PR --> PC1["planning-config.json<br/>planningRoot: '.'"]
        PR --> Plans1["Plans/ Research/ ..."]

        CR["Code Repo (separate)"]
        PC1 -. "repositories: { app: ... }" .-> CR
    end

    subgraph embedded ["Embedded Mode"]
        direction TB
        ER["Project Repo"]
        ER --> PD["Planning/"]
        PD --> PC2["planning-config.json<br/>planningRoot: 'Planning'"]
        PD --> Plans2["Plans/ Research/ ..."]
        ER --> Src["src/ lib/ ..."]
    end

    classDef config fill:#6a5a3a,stroke:#333,color:#fff
    class PC1,PC2 config
```

### Standalone

A dedicated repository for planning. Plans reference external code repositories via `planning-config.json`:

```json
{
  "mode": "standalone",
  "planningRoot": ".",
  "repositories": {
    "my-app": { "github": "org/my-app" }
  }
}
```

Local filesystem paths go in `planning-config.local.json` (gitignored):

```json
{
  "repositories": {
    "my-app": { "path": "/home/user/Code/my-app" }
  }
}
```

### Embedded

Planning lives inside your project as a subdirectory:

```json
{
  "mode": "embedded",
  "planningRoot": "Planning"
}
```

### Cross-repo (standalone with absolute path)

Point multiple code repos at one shared planning repo using an absolute `planningRoot`:

```json
{
  "mode": "standalone",
  "planningRoot": "/home/user/Code/my-planning-repo"
}
```

## Dashboard

The HTML dashboard previously bundled with this plugin has moved to a companion plugin, [`sdd-dashboard`](https://github.com/danweinerdev/sdd-dashboard-plugin). Install it alongside `sdd-planner` to get:

- `/sdd-dashboard:dashboard` — regenerate the static HTML dashboard from artifact frontmatter
- `/sdd-dashboard:status` — quick text-only status summary (read-only)

The dashboard is opt-in via `"dashboard": true` in `planning-config.json` (plus optional `title` / `description` for the page chrome). If you don't install the companion plugin, those fields are simply ignored.

## Directory Structure

```
sdd-planner/                       # The plugin itself (not your project)
├── .claude-plugin/
│   └── plugin.json               # Plugin manifest (name: "sdd-planner")
├── commands/                     # Slash commands → /sdd-planner:*
│   ├── brainstorm.md
│   ├── breakdown.md
│   ├── code-review.md
│   ├── debrief.md
│   ├── design.md
│   ├── diagram.md
│   ├── excavate.md
│   ├── implement.md
│   ├── plan.md
│   ├── poke-holes.md
│   ├── research.md
│   ├── retro.md
│   ├── setup.md
│   ├── simplify.md
│   ├── specify.md
│   └── tend.md
├── agents/                       # Review agents
│   ├── blind-spot-finder.md
│   ├── code-implementer.md
│   ├── drift-detector.md
│   ├── plan-reviewer.md
│   ├── quality-scanner.md
│   ├── researcher.md
│   ├── spec-compliance.md
│   └── spec-reviewer.md
├── shared/
│   ├── frontmatter-schema.md     # Artifact metadata schema
│   └── templates/                # Document templates
├── Makefile                      # make bump-patch / bump-minor / bump-major
├── CLAUDE.md                     # Claude Code project instructions
└── README.md
```

## Requirements

- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) CLI
- Python 3 only if you also use the companion `sdd-dashboard` plugin
