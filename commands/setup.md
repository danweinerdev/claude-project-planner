---
name: setup
description: "Set up a repository for sdd-planner — generates planning-config.json, bootstraps planning directories, creates launcher script. Triggers: /setup, setup repo, configure repo, setup worktree, initialize planner, bootstrap planner"
---

# /setup — Configure Repository for SDD Planner

## When to Use
When setting up a new or existing repository to work with the sdd-planner plugin. This generates `planning-config.json`, bootstraps planning artifact directories, and creates launcher scripts.

**Idempotent and safe to re-run.** Overwrites `planning-config.json` and launcher scripts. Creates missing directories without touching existing ones.

## What It Does

1. Detects the repository type (normal repo, worktree, or bare repo)
2. For worktrees, searches sibling worktrees for an existing `planning-config.json` and inherits settings
3. Generates `planning-config.json` — the config that tells the plugin where planning artifacts live
4. Bootstraps planning directories (Plans/New/, Plans/Ready/, Plans/Active/, Plans/Complete/, Research/, Brainstorm/, Specs/, Designs/, Retro/) if they don't exist
5. Creates a launcher script (`claude.sh` / `claude.cmd`) for launching Claude with the plugin
6. Sets up `.gitignore` for generated files
7. Cleans any stale legacy symlinks or file copies from older plugin versions

## What It Does NOT Do

- Copy skills, agents, or plugin files — the plugin discovers its own files via `--plugin-dir`
- Generate CLAUDE.md — the plugin provides its own context
- Copy templates or frontmatter schemas
- Handle bare repos directly — run setup on individual worktrees instead

## Arguments

The user may provide these inline with the command:
- **repo path** — target repository (defaults to current working directory)
- **--planning-root `<path>`** — where planning artifacts live (defaults to plugin directory)
- **--dashboard** — set the `dashboard: true` flag in `planning-config.json` so the companion `sdd-dashboard` plugin (if installed) will generate HTML output

Examples:
```
/setup                                    # current directory
/setup /path/to/my-project               # specific repo
/setup my-repo                           # config key lookup
/setup /path/to/repo --planning-root /path/to/planning
/setup /path/to/repo --dashboard          # opt into HTML dashboard generation
```

## Process

### 1. Determine Target

- If the user specified a path, resolve it to an absolute path
- If the user specified a name (not a path), look it up in `planning-config.local.json` under `repositories.<name>.path` (or as a plain string value)
- Otherwise, use the **current working directory**
- Verify the target directory exists

### 2. Detect Repository Type

Check the target directory to determine what kind of git repository it is:

1. **Bare repo check**: If a `.bare/` directory exists, this is a bare repo → **stop with an error**: "This is a bare repository. Run setup on individual worktrees instead."
2. **Worktree check**: If `.git` is a **file** (not a directory), this is a worktree → proceed as worktree
3. **Bare repo fallback**: Run `git -C <target> rev-parse --is-bare-repository` — if output is `true`, this is a bare repo → **stop with error** as above
4. **Normal repo**: If `.git` is a **directory**, this is a normal repo → proceed normally
5. **Not a repo**: If none of the above → **stop with error**: "Not a git repository"

### 3. Resolve Planning Root

Determine where planning artifacts will live, in this priority order:

1. **Explicit flag**: If `--planning-root` was provided, use that path (resolve to absolute)
2. **Sibling inheritance** (worktrees only): Run `git -C <target> worktree list --porcelain` to find sibling worktrees. For each sibling (excluding the target itself), check if `<sibling>/planning-config.json` exists. If found, read its `planningRoot` value and use it. Report: "Inheriting planningRoot from sibling worktree: `<sibling-path>`"
3. **Default**: Use the plugin directory. The plugin directory contains `commands/`, `agents/`, and `shared/` as siblings — find it by globbing for `**/commands/setup.md` in both the current directory and `~/.claude/plugins/cache/`. If multiple matches are found (e.g., multiple cached plugin versions), sort by version number and use the highest. Then go one level up.

### 4. Ask Configuration Questions (if needed)

Ask the user about options that aren't already clear from context or arguments. For most setups the defaults are correct — skip questions when the answer is obvious.

**Planning root** — skip if `--planning-root` was provided, inherited from sibling, or context makes it obvious:
> Where do your planning artifacts live?
> - In the sdd-planner plugin directory (default)
> - In a separate directory (provide path)

**Dashboard** — skip if `--dashboard` was provided or inherited from sibling config:
> Do you want to opt in to the HTML dashboard? (rendered by the companion `sdd-dashboard` plugin via `/sdd-dashboard:dashboard`)
> - No (default) — `dashboard` flag is omitted; nothing is generated
> - Yes — sets `"dashboard": true` in `planning-config.json`. The flag is read by the `sdd-dashboard` plugin if installed; `sdd-planner` ignores it.

### 5. Write planning-config.json

Write (or overwrite) `planning-config.json` in the target repository:

```json
{
  "planningRoot": "<resolved-planning-root>"
}
```

`planningRoot` is just a path. Use `"."` for "artifacts at the repo root", a relative subdirectory name like `"Planning"` for "artifacts inside this repo", or an absolute path for "artifacts in an external directory". There's no `mode` field — the path itself tells the plugin where to look.

If the user opted into the dashboard, also include `"dashboard": true` along with `"title"` and `"description"` fields (the companion `sdd-dashboard` plugin reads these for the page chrome):

```json
{
  "planningRoot": "<resolved-planning-root>",
  "dashboard": true,
  "title": "<project-name> Dashboard",
  "description": "Plans, specs, designs, research, and progress tracking"
}
```

If the file already exists and the `planningRoot` matches, report "planning-config.json: OK" and skip overwriting (but still add/update the `dashboard` field if the user explicitly requested it).

### 6. Bootstrap Planning Directories

In the **planning root**, create these directories if they don't already exist:

```
Plans/New/
Plans/Ready/
Plans/Active/
Plans/Complete/
Research/
Brainstorm/
Specs/
Designs/
Retro/
```

Use `mkdir -p` — safe to run on existing directories. Report which directories were created vs already existed.

### 7. Clean Stale Legacy Files

Check `<target>/.claude/skills/` and `<target>/.claude/agents/` for leftover files from older plugin versions:

**Symlinks**: Remove any `.md` symlinks that point into the plugin directory (these are from the legacy symlink-based setup).

**Copies**: Compare filenames in `.claude/skills/*.md` against `commands/*.md` in the plugin directory, and `.claude/agents/*.md` against `agents/*.md`. Remove matching files (these are stale copies from before the plugin system). Keep non-matching files — they may be user-created.

Remove empty `.claude/skills/` or `.claude/agents/` directories after cleanup.

Report what was cleaned, if anything.

### 8. Write Launcher Script

Create a launcher script in the target repository that starts Claude with the planning root:

**Unix** (`claude.sh`):
```bash
#!/usr/bin/env bash
# Launch Claude Code with planning context
exec claude \
    --add-dir="<planning-root>" \
    "$@"
```
Make it executable (`chmod +x`).

**Windows** (`claude.cmd`):
```cmd
@echo off
claude --add-dir="<planning-root>" %*
```

### 9. Set Up .gitignore

Ensure the target repository's `.gitignore` includes these entries (add them if missing, don't duplicate):
- `Dashboard/` (generated HTML — only relevant if the `sdd-dashboard` companion plugin is installed; harmless to add unconditionally)
- `planning-config.local.json` (local filesystem paths)

### 10. Report Results

Display a summary of what was created or updated:

```
## Setup Complete

**Repo:** <path>
**Type:** normal repo / worktree
**Planning root:** <path>
**Dashboard flag:** enabled / disabled (rendered by the companion `sdd-dashboard` plugin)

### Created/Updated
- planning-config.json
- Planning directories (list any that were created)
- claude.sh
- .gitignore entries

### Next Steps
- `cd <repo> && ./claude.sh`
```

## Context
- Config: `planning-config.json`, `planning-config.local.json`
