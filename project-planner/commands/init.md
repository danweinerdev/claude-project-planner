---
name: init
description: "Bootstrap a new project-planner instance (standalone or embedded). Triggers: /init, initialize planner, setup planning, bootstrap planner"
---

# /init — Bootstrap Project Planner

## When to Use
When setting up a new project-planner instance — either as a standalone planning repository or embedded within an existing project.

## Modes

- **Standalone**: Dedicated planning repo (like a separate Jira-style project). Plans reference code in external repos via config.
- **Embedded**: Planning lives inside an existing project as a subdirectory (e.g., `Planning/`).

## Process

### 1. Gather Configuration

Ask the user:

1. **Mode**: Standalone or embedded?
2. **Path**:
   - Standalone: absolute path for the new repo (or current directory)
   - Embedded: subdirectory name (e.g., `Planning`, `docs/planning`)
3. **Project title**: Dashboard title (e.g., "My App Planning Dashboard")
4. **Description**: Short description for the dashboard
5. **Repositories** (standalone only, optional): Target code repositories
   - For each: a key name, GitHub URL (e.g., `org/repo`), and optionally a local filesystem path

### 2. Compute Paths

Determine the key path:
- **`planningRoot`**: Where artifact directories and `planning-config.json` live
  - Standalone: the repo root (path = `"."` in config)
  - Embedded: the subdirectory (path = subdirectory name in config, e.g., `"Planning"`)

### 3. Create Directory Structure

Under `planningRoot`, create:
```
Plans/
Research/
Brainstorm/
Specs/
Designs/
Retro/
Shared/
Dashboard/      (will be gitignored)
```

### 4. Write `planning-config.json` (Primary Output)

Write `planning-config.json` into `planningRoot`. This is the skill's **primary output** — the single config file that drives all path resolution.

**Standalone example:**
```json
{
  "mode": "standalone",
  "planningRoot": ".",
  "title": "My Project Dashboard",
  "description": "Plans, specs, designs, research, and progress tracking",
  "repositories": {
    "my-app": { "github": "org/my-app" }
  },
  "planRepository": "<planning-repo-key>",
  "planMapping": {}
}
```

**Embedded example:**
```json
{
  "mode": "embedded",
  "planningRoot": "Planning",
  "title": "My Project Dashboard",
  "description": "Plans, specs, designs, research, and progress tracking"
}
```

Only include `repositories`, `planRepository`, and `planMapping` for standalone mode when the user configures repositories.

### 5. Write `planning-config.local.json` (Standalone Only)

If the user provided local filesystem paths for repositories, write `planning-config.local.json` (gitignored):
```json
{
  "repositories": {
    "my-app": { "path": "/home/user/Code/my-app" }
  }
}
```

### 6. Copy Shared Files into `planningRoot`

Copy from the project-planner plugin directory into the target `planningRoot`:
- `Shared/` directory (templates, frontmatter schema)
- `generate-dashboard.py`
- `Makefile`

Read each source file and write it to the target. The plugin directory contains `commands/`, `agents/`, and `Shared/` as siblings — find it by globbing for `**/commands/research.md` in both the current directory and `~/.claude/plugins/cache/`, then go one level up.

### 7. Write or Append CLAUDE.md

At `<projectRoot>/CLAUDE.md`:

- **Standalone**: Write a full CLAUDE.md using `Shared/templates/claude-md-standalone.md`. Replace `{{TITLE}}` with the project title, `{{DESCRIPTION}}` with the description, and `{{PLANNING_ROOT}}` with the planning root name.
- **Embedded**: If CLAUDE.md already exists, **append** the content from `Shared/templates/claude-md-embedded.md`. If it doesn't exist, create it with a basic header plus the embedded template. Replace `{{PLANNING_ROOT}}` with the subdirectory name.

### 8. Set Up `.gitignore`

At `<planningRoot>/.gitignore` (standalone) or append to `<projectRoot>/.gitignore` (embedded):

Ensure these entries are present:
```
# Generated dashboard
Dashboard/

# Local config (paths, not committed)
planning-config.local.json

# Python
__pycache__/
*.py[cod]
```

For embedded mode, prefix Dashboard path: `<planningRoot>/Dashboard/`.

### 9. Print Summary

Display:
```
## Project Planner Initialized

**Mode:** standalone/embedded
**Planning root:** <path>
**Config:** <path>/planning-config.json

### Created
- Directory structure (Plans/, Research/, Brainstorm/, Specs/, Designs/, Retro/)
- planning-config.json
- CLAUDE.md
- generate-dashboard.py + Makefile

### Next Steps
1. Run `make dashboard` (or `make -C <dir> dashboard` for embedded) to verify
2. Use `/research` to investigate a topic
3. Use `/plan` to create your first implementation plan
4. Use `/status` to check progress at any time
```

## Key Rules
- `generate-dashboard.py` and `Makefile` always live inside `planningRoot`
- `planning-config.json` lives in `planningRoot`
- Commands and agents are provided by the marketplace plugin — do not copy them into `.claude/`

## Context
- Templates: `<plugin-dir>/Shared/templates/claude-md-standalone.md`, `<plugin-dir>/Shared/templates/claude-md-embedded.md`
- Schema: `<plugin-dir>/Shared/frontmatter-schema.md`
- Config: `planning-config.json`
- The plugin directory contains `commands/`, `agents/`, and `Shared/` as siblings — find it by globbing for `**/commands/research.md` in both the current directory and `~/.claude/plugins/cache/`, then go one level up.
