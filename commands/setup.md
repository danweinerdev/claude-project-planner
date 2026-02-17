---
name: setup
description: "Set up or re-setup a repository for project-planner. Overwrites existing setup files. Auto-detects bare vs normal repos. Triggers: /setup, setup repo, configure repo, setup worktree, re-setup"
---

# /setup — Configure Repository for Project Planner

## When to Use
When you want to configure a repository (the current working directory or a specified path) to work with the project-planner plugin. This sets up `planning-config.json`, a `claude.sh` launcher script, and cleans stale symlinks.

**Idempotent and safe to re-run.** Always overwrites existing setup files (`claude.sh`, `planning-config.json`, `worktree-add.sh`) with fresh versions. This is the correct way to repair or update a previously configured repo — for example after moving the planner directory, changing the planning root, or updating the project-planner plugin.

Automatically detects whether the target is a **bare repo** (worktree workflow) or a **normal repo** and runs the appropriate setup.

## Detection Logic

Check the target repository to determine its type:

1. **Bare repo with `.bare/`** → worktree mode (generates `worktree-add.sh`)
2. **Standard bare repo** (`git rev-parse --is-bare-repository` returns `true`) → worktree mode
3. **Normal repo** (has `.git/` directory) → normal repo mode
4. **Not a git repo** → error, inform the user

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

For most setups the default is correct — skip the question if the user already specified `--planning-root` or if context makes the answer obvious.

### 3. Run the Setup Tool

The setup tools live in the **project-planner plugin directory** (the directory containing this command file).

Determine the plugin directory path — it is the parent of the `commands/` directory where this skill file is located. You can find it by checking where the planner plugin is loaded from, or by looking for `setup-repo.py` and `setup-worktree.py` at the project-planner root.

**For a bare repo (worktree mode):**
```bash
python3 <planner-dir>/setup-worktree.py <target-repo> [--planning-root <path>]
```

This generates (or overwrites) a `worktree-add.sh` script in the bare repo root. After generation, inform the user:
```
Worktree script generated. Usage:
  cd <repo> && ./worktree-add.sh <branch>
```

**For a normal repo:**
```bash
python3 <planner-dir>/setup-repo.py <target-repo> [--planning-root <path>]
```

This writes (or overwrites) `planning-config.json` and `claude.sh`/`claude.cmd` in the repo.

### 4. Report Results

Display what was created or updated:

```
## Setup Complete

**Repo:** <path>
**Type:** normal repo / bare repo (worktree)
**Planning root:** <path>

### Created/Overwritten
- planning-config.json (normal) or worktree-add.sh (bare)
- claude.sh launcher (normal only — worktrees get theirs via worktree-add.sh)
- Cleaned N stale symlinks (if any)

### Next Steps
- Normal: `cd <repo> && ./claude.sh`
- Bare: `cd <repo> && ./worktree-add.sh <branch>`
```

## What Gets Overwritten

Every run unconditionally overwrites these files with fresh versions:

| Repo type | Files overwritten |
|-----------|-------------------|
| Normal | `claude.sh` (or `claude.cmd`), `planning-config.json` |
| Bare (worktree) | `worktree-add.sh` |

The generated `worktree-add.sh` itself also overwrites `claude.sh` and `planning-config.json` inside each worktree when run. Existing worktrees are not affected until `worktree-add.sh` is re-run on them.

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
- Tools: `setup-repo.py`, `setup-worktree.py`
- Shared library: `setup/` package
- Config: `planning-config.json`, `planning-config.local.json`
