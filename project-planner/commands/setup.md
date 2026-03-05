---
name: setup
description: "Set up or re-setup a repository for project-planner. Overwrites existing setup files. Auto-detects normal repos vs worktrees, rejects bare repos. Triggers: /setup, setup repo, configure repo, setup worktree, re-setup"
---

# /setup — Configure Repository for Project Planner

## When to Use
When you want to configure a repository (the current working directory or a specified path) to work with the project-planner plugin. This sets up `planning-config.json`, a `claude.sh` launcher script, and cleans stale symlinks.

**Idempotent and safe to re-run.** Always overwrites existing setup files (`claude.sh`, `planning-config.json`) and cleans up stale file copies from previous setups. This is the correct way to repair or update a previously configured repo — for example after moving the planner directory or changing the planning root. Commands and agents are provided automatically by the marketplace plugin.

Automatically detects whether the target is a **normal repo** or **worktree** and runs the appropriate setup. Bare repos are rejected with a helpful error message.

## Detection Logic

Check the target repository to determine its type:

1. **`.git` is a file** → worktree (inherits settings from sibling worktrees)
2. **`.bare/` exists or `git rev-parse --is-bare-repository` is true** → bare repo → error, tell user to run setup on individual worktrees
3. **`.git/` is a directory** → normal repo
4. **None of the above** → error, inform the user

### Worktree Sibling Inheritance

When run on a worktree, setup searches sibling worktrees (via `git worktree list`) for an existing `planning-config.json` and reuses its `planningRoot`. This means you only need to specify `--planning-root` once — subsequent worktrees inherit the setting automatically.

Priority: explicit `--planning-root` flag > sibling discovery > default (planner directory).

## Process

### 1. Determine Target

- If the user specified a path or repo name, use that
- Otherwise, use the **current working directory**
- The target can also be a key from `planning-config.local.json` (resolved to a local path)

### 2. Ask for Planning Root (if needed)

If this is a standalone setup where planning artifacts live in a **separate** repository (not in the project-planner plugin directory itself), ask:

> Where do your planning artifacts live?
> - In the project-planner plugin directory (default)
> - In a separate planning repository (provide path)

For most setups the default is correct — skip the question if the user already specified `--planning-root` or if context makes the answer obvious. For worktrees, also skip if a sibling already has a config.

### 3. Run the Setup Tool

The setup tool lives in the **project-planner plugin directory** (the directory containing this command file).

The plugin directory contains `commands/`, `agents/`, and `Shared/` as siblings — find it by globbing for `**/commands/research.md` in both the current directory and `~/.claude/plugins/cache/`, then go one level up.

```bash
python3 <planner-dir>/setup-repo.py <target-repo> [--planning-root <path>]
```

This writes (or overwrites) `planning-config.json` and `claude.sh`/`claude.cmd` in the repo or worktree.

### 4. Report Results

Display what was created or updated:

```
## Setup Complete

**Repo:** <path>
**Type:** normal repo / worktree
**Planning root:** <path>

### Created/Overwritten
- planning-config.json
- claude.sh launcher
- Cleaned N stale symlinks (if any)
- Cleaned N stale file copies (if any)

### Next Steps
- `cd <repo> && ./claude.sh`
```

## What Gets Overwritten

Every run unconditionally overwrites these files with fresh versions:

| Files overwritten |
|-------------------|
| `claude.sh` (or `claude.cmd`), `planning-config.json` |

Setup also cleans up stale `.claude/skills/*.md` and `.claude/agents/*.md` files that were copied by previous versions of the setup tools. Commands and agents are now provided automatically by the marketplace plugin — no local copies needed.

## Arguments

The user may provide these inline with the command:
- **repo path** — target repository (defaults to current directory)
- **planning root** — where planning artifacts live (defaults to project-planner dir)

Examples:
```
/setup                                    # current directory
/setup /path/to/my-project               # specific repo
/setup my-repo                           # config key lookup
/setup /path/to/repo --planning-root /path/to/planning
```

## Context
- Tool: `setup-repo.py`
- Shared library: `setup/` package
- Config: `planning-config.json`, `planning-config.local.json`
