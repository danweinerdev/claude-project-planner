---
name: setup
description: "Set up a directory for sdd-planner — generates planning-config.json, bootstraps planning directories, creates launcher script. Triggers: /setup, setup repo, configure repo, setup worktree, initialize planner, bootstrap planner"
---

# /setup — Configure a Directory for SDD Planner

## When to Use
When configuring a directory (an existing repo, a fresh `git init`, a Perforce workspace, or even an empty directory) to work with the sdd-planner plugin. This generates `planning-config.json`, bootstraps planning artifact directories, and creates launcher scripts.

**Idempotent and safe to re-run.** Overwrites `planning-config.json` and launcher scripts. Creates missing directories without touching existing ones.

## What It Does

1. Detects the VCS rooted at the target directory using `shared/vcs-detection.md` (one of: `git`, `git-worktree`, `git-bare`, `perforce`, `none`)
2. For `git-worktree`, searches sibling worktrees for an existing `planning-config.json` and inherits settings
3. Generates `planning-config.json` — the config that tells the plugin where planning artifacts live
4. Bootstraps planning directories (Plans/New/, Plans/Ready/, Plans/Active/, Plans/Complete/, Research/, Brainstorm/, Specs/, Designs/, Retro/) if they don't exist
5. Creates a launcher script (`claude.sh` / `claude.cmd`) for launching Claude with the plugin
6. Sets up the appropriate ignore file for the detected VCS (`.gitignore`, `.p4ignore`, or skipped for `none`)
7. Cleans any stale legacy symlinks or file copies from older plugin versions

## What It Does NOT Do

- **Resolve paths.** Whatever path the user gives — relative or absolute — is preserved verbatim in `planning-config.json`. Setup never silently rewrites a relative path into an absolute one.
- **Initialize a VCS.** If the target has no VCS (`none`), setup proceeds without one. The user can `git init` (or set up a Perforce client) afterward — setup is not in that business.
- Copy skills, agents, or plugin files — the plugin discovers its own files via `--plugin-dir`
- Generate CLAUDE.md — the plugin provides its own context
- Copy templates or frontmatter schemas
- Handle git-bare repos directly — run setup on individual worktrees instead

## Arguments

The user may provide these inline with the command:
- **target path** — directory to configure (defaults to current working directory). May be relative or absolute; **kept as-given**.
- **--planning-root `<path>`** — where planning artifacts live. **Kept as-given** — relative stays relative, absolute stays absolute.
- **--dashboard** — set the `dashboard: true` flag in `planning-config.json` so the companion `sdd-dashboard` plugin (if installed) will generate HTML output

Examples:
```
/setup                                       # current directory
/setup ../my-project                         # relative path, kept relative
/setup /path/to/my-project                   # absolute path, kept absolute
/setup my-repo                               # config key lookup
/setup . --planning-root Planning            # planningRoot stored as "Planning"
/setup . --planning-root /home/u/plans       # planningRoot stored as "/home/u/plans"
/setup /path/to/repo --dashboard             # opt into HTML dashboard generation
```

## Process

### 1. Determine Target

- If the user specified a path, use it **as given**. Do not resolve symlinks or convert relative paths to absolute. Just verify the directory exists.
- If the user specified a name (not a path), look it up in `planning-config.local.json` under `repositories.<name>.path` (or as a plain string value). Use whatever value is stored there as-given.
- Otherwise, use the **current working directory**.

### 2. Detect VCS

Apply the algorithm in `shared/vcs-detection.md` to the target directory. Record the result as one of: `git`, `git-worktree`, `git-bare`, `perforce`, `none`.

If the result is `git-bare`, **stop with an error**: "This is a bare git repository. Run setup on individual worktrees instead."

For every other result (`git`, `git-worktree`, `perforce`, `none`), proceed. Setup is VCS-agnostic from here on — the only place the VCS affects behavior is the ignore-file step (Step 9).

### 3. Resolve Planning Root

Determine where planning artifacts will live, in this priority order. **The value is stored verbatim** in `planning-config.json` — never resolved to absolute:

1. **Explicit flag**: If `--planning-root` was provided, use that path verbatim.
2. **Sibling inheritance** (only when VCS is `git-worktree`): Run `git -C <target> worktree list --porcelain` to find sibling worktrees. For each sibling (excluding the target itself), check if `<sibling>/planning-config.json` exists. If found, read its `planningRoot` value and use it verbatim. Report: "Inheriting planningRoot from sibling worktree: `<sibling-path>`". This step is skipped for non-git VCS.
3. **Default**: Use the plugin directory. The plugin directory contains `commands/`, `agents/`, and `shared/` as siblings — find it by globbing for `**/commands/setup.md` in both the current directory and `~/.claude/plugins/cache/`. If multiple matches are found (e.g., multiple cached plugin versions), sort by version number and use the highest. Then go one level up. The plugin directory lives outside the user's project, so this default is recorded as an absolute path.

### 4. Ask Configuration Questions (if needed)

Skip questions when the answer is obvious from arguments or context.

**Planning root** — skip if `--planning-root` was provided, inherited from sibling, or context makes it obvious:
> Where do your planning artifacts live?
> - In the sdd-planner plugin directory (default — kept as an absolute path)
> - In a relative subdirectory of this repo (e.g., `Planning`) — stored as a relative path
> - In an absolute path elsewhere on disk — stored as an absolute path

**Dashboard** — skip if `--dashboard` was provided or inherited from sibling config:
> Do you want to opt in to the HTML dashboard? (rendered by the companion `sdd-dashboard` plugin via `/sdd-dashboard:dashboard`)
> - No (default) — `dashboard` flag is omitted; nothing is generated
> - Yes — sets `"dashboard": true` in `planning-config.json`. The flag is read by the `sdd-dashboard` plugin if installed; `sdd-planner` ignores it.

### 5. Write planning-config.json

Write (or overwrite) `planning-config.json` in the target directory:

```json
{
  "planningRoot": "<the path the user gave, verbatim>"
}
```

`planningRoot` is just a path. Relative paths are interpreted relative to the directory containing `planning-config.json`; absolute paths are used as-is. The plugin doesn't care which kind you pick.

If the user opted into the dashboard, also include `"dashboard": true` along with `"title"` and `"description"` fields (the companion `sdd-dashboard` plugin reads these for the page chrome):

```json
{
  "planningRoot": "<verbatim>",
  "dashboard": true,
  "title": "<project-name> Dashboard",
  "description": "Plans, specs, designs, research, and progress tracking"
}
```

If the file already exists and `planningRoot` matches, report "planning-config.json: OK" and skip overwriting (but still add/update the `dashboard` field if the user explicitly requested it).

### 6. Bootstrap Planning Directories

Resolve the planning root path *for this step only*: if relative, join with the target directory; if absolute, use as-is. (The stored value in `planning-config.json` does not change.) Then create these directories if they don't already exist:

```
<resolved-planning-root>/Plans/New/
<resolved-planning-root>/Plans/Ready/
<resolved-planning-root>/Plans/Active/
<resolved-planning-root>/Plans/Complete/
<resolved-planning-root>/Research/
<resolved-planning-root>/Brainstorm/
<resolved-planning-root>/Specs/
<resolved-planning-root>/Designs/
<resolved-planning-root>/Retro/
```

Use `mkdir -p` — safe to run on existing directories. Report which directories were created vs already existed.

### 7. Clean Stale Legacy Files

Check `<target>/.claude/skills/` and `<target>/.claude/agents/` for leftover files from older plugin versions:

**Symlinks**: Remove any `.md` symlinks that point into the plugin directory (these are from the legacy symlink-based setup).

**Copies**: Compare filenames in `.claude/skills/*.md` against `commands/*.md` in the plugin directory, and `.claude/agents/*.md` against `agents/*.md`. Remove matching files (these are stale copies from before the plugin system). Keep non-matching files — they may be user-created.

Remove empty `.claude/skills/` or `.claude/agents/` directories after cleanup.

Report what was cleaned, if anything.

### 8. Write Launcher Script

Create a launcher script in the target directory that starts Claude with the planning root added to its allowed-paths list. Pass the `planningRoot` value through verbatim — `claude --add-dir` accepts both relative and absolute paths.

**Unix** (`claude.sh`):
```bash
#!/usr/bin/env bash
# Launch Claude Code with planning context
exec claude \
    --add-dir="<planning-root verbatim>" \
    "$@"
```
Make it executable (`chmod +x`).

**Windows** (`claude.cmd`):
```cmd
@echo off
claude --add-dir="<planning-root verbatim>" %*
```

### 9. Set Up Ignore File (VCS-aware)

Pick the ignore file based on the detected VCS:

| VCS | File | Action |
|---|---|---|
| `git` / `git-worktree` | `.gitignore` | Ensure both entries below are present (add if missing, don't duplicate) |
| `perforce` | `.p4ignore` | Same — write entries in `.p4ignore` syntax (one path per line, no leading slash) |
| `none` | (skip) | No VCS to ignore for; nothing to write |

Entries:
- `Dashboard/` — generated HTML; only relevant if the `sdd-dashboard` companion plugin is installed; harmless to add unconditionally
- `planning-config.local.json` — local filesystem paths to other repos

### 10. Report Results

Display a summary:

```
## Setup Complete

**Target:** <path-as-user-provided>
**VCS:** git | git-worktree | perforce | none
**Planning root:** <verbatim, with a note if relative or absolute>
**Dashboard flag:** enabled | disabled (rendered by the companion `sdd-dashboard` plugin)

### Created/Updated
- planning-config.json
- Planning directories (list any that were created)
- claude.sh
- ignore file (.gitignore | .p4ignore | none)

### Next Steps
- `cd <target> && ./claude.sh`
```

## Context
- VCS detection: `shared/vcs-detection.md`
- Config: `planning-config.json`, `planning-config.local.json`
