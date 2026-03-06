---
name: setup
description: "Set up a repository for project-planner — generates planning-config.json and bootstraps planning directories. Triggers: /setup, setup repo, configure repo, setup worktree, initialize planner, bootstrap planner"
---

# /setup — Configure Repository for Project Planner

## When to Use
When setting up a new or existing repository to work with the project-planner plugin. This generates `planning-config.json`, bootstraps planning artifact directories, and creates launcher scripts.

**Idempotent and safe to re-run.** Overwrites `planning-config.json` and launcher scripts. Creates missing directories without touching existing ones.

## What It Does

1. Detects the repository type (normal repo, worktree, or bare repo)
2. For worktrees, searches sibling worktrees for an existing `planning-config.json` and inherits settings
3. Generates `planning-config.json` — the config that tells the plugin where planning artifacts live
4. Bootstraps planning directories (Plans/, Research/, Brainstorm/, Specs/, Designs/, Retro/, Shared/) if they don't exist
5. Creates a launcher script (`claude.sh` / `claude.cmd`) for launching Claude with the plugin
6. Sets up `.gitignore` for generated files
7. Cleans any stale legacy symlinks

## What It Does NOT Do

- Copy skills, agents, or plugin files — the plugin discovers its own files via `--plugin-dir`
- Generate CLAUDE.md — the plugin provides its own context
- Copy templates, frontmatter schemas, or dashboard generators
- Handle bare repos directly — run setup on individual worktrees instead

## Detection Logic

The setup tool auto-detects the target repository type:

1. **Worktree** (`.git` is a file) → normal setup, inherits settings from sibling worktrees if available
2. **Bare repo** (`.bare/` exists or `git rev-parse --is-bare-repository` returns `true`) → error with guidance to run on worktrees instead
3. **Normal repo** (`.git/` is a directory) → normal setup
4. **Not a git repo** → error

## Process

### 1. Determine Target

- If the user specified a path or repo name, use that
- Otherwise, use the **current working directory**
- The target can also be a key from `planning-config.local.json` (resolved to a local path)

### 2. Ask Configuration Questions (if needed)

Ask the user about options that aren't already clear from context or arguments:

**Planning root** — skip if `--planning-root` was provided, inherited from sibling, or context makes it obvious:
> Where do your planning artifacts live?
> - In the project-planner plugin directory (default)
> - In a separate directory (provide path)

**Dashboard** — skip if `--no-dashboard` was provided or inherited from sibling:
> Do you want the HTML dashboard?
> - Yes (default) — generates a static HTML dashboard from artifacts via `make dashboard`
> - No — disables dashboard generation (sets `"dashboard": false` in config)

For most setups the defaults are correct — skip questions when the answer is obvious.

### 3. Run the Setup Tool

The setup tool lives in the **project-planner plugin directory** (the directory containing this command file).

The plugin directory contains `commands/`, `agents/`, and `Shared/` as siblings — find it by globbing for `**/commands/setup.md` in both the current directory and `~/.claude/plugins/cache/`. If multiple matches are found (e.g., multiple cached plugin versions), sort by version number and use the highest. Then go one level up.

```bash
python3 <planner-dir>/setup-repo.py <target-repo> [--planning-root <path>] [--no-dashboard]
```

This writes (or overwrites) `planning-config.json` and `claude.sh`/`claude.cmd` in the repo, and bootstraps planning directories.

For worktrees, it automatically discovers sibling planning configs unless `--planning-root` is explicitly provided.

### 4. Report Results

Display what was created or updated:

```
## Setup Complete

**Repo:** <path>
**Type:** normal repo / worktree
**Planning root:** <path>

### Created/Updated
- planning-config.json
- Planning directories (if any were missing)
- claude.sh
- .gitignore entries

### Next Steps
- `cd <repo> && ./claude.sh`
```

## Arguments

The user may provide these inline with the command:
- **repo path** — target repository (defaults to current directory)
- **planning root** — where planning artifacts live (defaults to project-planner dir)
- **--no-dashboard** — disable dashboard generation

Examples:
```
/setup                                    # current directory
/setup /path/to/my-project               # specific repo
/setup my-repo                           # config key lookup
/setup /path/to/repo --planning-root /path/to/planning
/setup /path/to/repo --no-dashboard      # skip dashboard
```

## Context
- Tool: `setup-repo.py`
- Shared library: `setup/` package
- Config: `planning-config.json`, `planning-config.local.json`
