# Project Planner

A [Claude Code](https://docs.anthropic.com/en/docs/claude-code) plugin for structured project planning. It provides slash commands that guide you through a full planning lifecycle — from research to retrospective — with YAML-frontmatter-driven artifacts and a generated HTML dashboard.

## How It Works

Project Planner is a Claude Code **plugin**. When loaded, it registers 17 slash commands (namespaced under `/planner:*`) and 3 review agents that Claude can delegate to. All artifacts are Markdown files with YAML frontmatter — the dashboard generator reads frontmatter exclusively, so there's no brittle table parsing.

```mermaid
graph LR
    subgraph Plugin ["project-planner (plugin)"]
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
        dashboard["Dashboard/ (generated HTML)"]
    end

    CC -->|--plugin-dir| Plugin
    CC -->|reads| config
    commands -->|create & update| artifacts
    artifacts -->|make dashboard| dashboard
```

## Quick Start

### Use with an existing project (embedded mode)

```bash
# From your project root
claude --plugin-dir /path/to/project-planner

# Then inside Claude:
> /planner:init
# Choose "embedded", pick a subdirectory (e.g., "Planning")
```

### Use as a standalone planning repo

```bash
# Create a new repo for planning
mkdir my-planning && cd my-planning && git init
claude --plugin-dir /path/to/project-planner

# Then inside Claude:
> /planner:init
# Choose "standalone"
```

### Use with git worktrees

If you use bare-repo worktrees, create a launcher script in each worktree:

```bash
# claude.sh
#!/usr/bin/env bash
exec claude \
    --add-dir="/path/to/planning-repo" \
    --plugin-dir="/path/to/project-planner" \
    "$@"
```

Then run `./claude.sh` from any worktree to get planning commands and context.

## Slash Commands

All commands are namespaced as `/planner:*` automatically by the plugin system.

### Lifecycle Commands

| Command | Purpose | Output |
|---------|---------|--------|
| `/planner:init` | Bootstrap a new planner instance | `planning-config.json`, directory structure |
| `/planner:research` | Investigate a topic | `Research/<topic>.md` |
| `/planner:brainstorm` | Explore possibilities | `Brainstorm/<topic>.md` |
| `/planner:specify` | Write requirements | `Specs/<feature>/README.md` |
| `/planner:design` | Technical architecture | `Designs/<component>/README.md` |
| `/planner:plan` | Create implementation plan | `Plans/<Name>/README.md` + phase docs |
| `/planner:breakdown` | Add detail to plan phases | Updates phase `.md` with tasks/subtasks |
| `/planner:implement` | Execute a plan phase | Code + updated task/phase statuses |
| `/planner:simplify` | Post-implementation cleanup | Simplified code, tests verified |
| `/planner:debrief` | After-action notes | `Plans/<Name>/notes/<phase>.md` |
| `/planner:retro` | Capture learnings | `Retro/YYYY-MM-DD-<slug>.md` |

### Utility Commands

| Command | Purpose | Output |
|---------|---------|--------|
| `/planner:poke-holes` | Adversarial critical analysis | Inline findings (no artifact) |
| `/planner:tend` | Artifact hygiene | Updates stale statuses, tags, conventions |
| `/planner:diagram` | Generate Mermaid diagrams | `Diagrams/<subject>.md` or inline |
| `/planner:excavate` | Progressive codebase discovery | `Research/<codebase>.md` |
| `/planner:dashboard` | Regenerate HTML dashboard | `Dashboard/` |
| `/planner:status` | Quick status summary | Text output (read-only) |

## Workflow Lifecycle

Commands follow a natural planning progression. You don't have to use every step — jump in wherever makes sense. Utility commands can be used at any point.

```mermaid
graph TD
    init["/planner:init"] --> research["/planner:research"]
    research --> brainstorm["/planner:brainstorm"]
    brainstorm --> specify["/planner:specify"]
    specify --> design["/planner:design"]
    design --> plan["/planner:plan"]
    plan --> breakdown["/planner:breakdown"]
    breakdown --> implement["/planner:implement"]
    implement --> simplify["/planner:simplify"]
    simplify --> debrief["/planner:debrief"]
    debrief --> retro["/planner:retro"]

    poke["⚡ /planner:poke-holes"]
    tend["🔧 /planner:tend"]
    diagram["📊 /planner:diagram"]
    excavate["🔍 /planner:excavate"]
    status["📋 /planner:status"]
    dashboard["📈 /planner:dashboard"]

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

    class init,research,brainstorm discovery
    class specify,design definition
    class plan,breakdown execution
    class implement,simplify implementation
    class debrief,retro review
    class poke,tend,diagram,excavate,status,dashboard utility
```

| Phase | Commands | What happens |
|-------|----------|-------------|
| **Discovery** | `research`, `brainstorm`, `excavate` | Gather context, explore options, map codebases |
| **Definition** | `specify`, `design` | Lock down requirements and architecture |
| **Execution** | `plan`, `breakdown` | Structure work into phases, tasks, subtasks |
| **Implementation** | `implement`, `simplify` | Build it, then clean it up |
| **Review** | `debrief`, `retro` | Capture what happened and what you learned |
| **Utilities** | `poke-holes`, `tend`, `diagram`, `status`, `dashboard` | Challenge, maintain, visualize, monitor |

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
| **Plan** | `Plans/<Name>/README.md` frontmatter | `draft` `approved` `active` `complete` `archived` |
| **Phase** | `Plans/<Name>/01-Phase.md` frontmatter | `planned` `in-progress` `complete` `blocked` `deferred` |
| **Task** | Phase frontmatter `tasks:` array | `planned` `in-progress` `complete` `blocked` `deferred` |
| **Subtask** | Phase body as `- [ ]` checklists | Checkbox state |

## Agents

The plugin includes 3 review agents that Claude can delegate to:

| Agent | Model | Purpose |
|-------|-------|---------|
| `researcher` | Sonnet | Gathers context from artifacts, codebase, and web |
| `plan-reviewer` | Sonnet | Reviews plans for completeness, feasibility, and conventions |
| `spec-reviewer` | Haiku | Reviews specs for testability, completeness, and ambiguity |

## Deployment Modes

```mermaid
graph TB
    subgraph standalone ["Standalone Mode"]
        direction TB
        PR["Planning Repo"]
        PR --> PC1["planning-config.json<br/>planningRoot: '.'"]
        PR --> Plans1["Plans/ Research/ ..."]
        PR --> Gen1["generate-dashboard.py"]

        CR["Code Repo (separate)"]
        PC1 -. "repositories: { app: ... }" .-> CR
    end

    subgraph embedded ["Embedded Mode"]
        direction TB
        ER["Project Repo"]
        ER --> PD["Planning/"]
        PD --> PC2["planning-config.json<br/>planningRoot: 'Planning'"]
        PD --> Plans2["Plans/ Research/ ..."]
        PD --> Gen2["generate-dashboard.py"]
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
  "title": "My Project Dashboard",
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
  "planningRoot": "Planning",
  "title": "My Project Dashboard"
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

A static HTML dashboard generated from artifact frontmatter. Python 3 stdlib only — no dependencies.

All artifact-mutating skills auto-regenerate the dashboard after writing. You can also trigger it manually:

```bash
make dashboard        # generate
make open             # generate and open in browser
make clean            # remove generated files
make test             # run test suite
```

To disable dashboard generation, set `"dashboard": false` in `planning-config.json`.

### Pages

| Page | Content |
|------|---------|
| `index.html` | Stats, in-progress work, plan cards, recent activity |
| `<plan>/index.html` | Plan detail with phase status table |
| `<plan>/<phase>.html` | Phase detail with task table and body content |
| `knowledge.html` | Research and brainstorm index |
| `specs.html` | Specifications index |
| `designs.html` | Designs index |
| `retros.html` | Retrospectives index |

## Directory Structure

```
project-planner/                   # The plugin itself (not your project)
├── .claude-plugin/
│   └── plugin.json               # Plugin manifest (name: "planner")
├── commands/                     # Slash commands → /planner:*
│   ├── brainstorm.md
│   ├── breakdown.md
│   ├── dashboard.md
│   ├── debrief.md
│   ├── design.md
│   ├── diagram.md
│   ├── excavate.md
│   ├── implement.md
│   ├── init.md
│   ├── plan.md
│   ├── poke-holes.md
│   ├── research.md
│   ├── retro.md
│   ├── simplify.md
│   ├── specify.md
│   ├── status.md
│   └── tend.md
├── agents/                       # Review agents
│   ├── researcher.md
│   ├── plan-reviewer.md
│   └── spec-reviewer.md
├── Shared/
│   ├── frontmatter-schema.md     # Artifact metadata schema
│   └── templates/                # Document templates
├── dashboard/                    # Dashboard generator package
├── generate-dashboard.py         # Dashboard entry point (Python 3, stdlib only)
├── tests/                        # pytest test suite
├── Makefile                      # make dashboard / make open / make clean / make test
├── CLAUDE.md                     # Claude Code project instructions
└── README.md
```

## Requirements

- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) CLI
- Python 3 (stdlib only, for dashboard generation)
