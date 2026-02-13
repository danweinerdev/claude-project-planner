---
title: "Project Planner"
type: plan
status: active
created: 2026-02-13
updated: 2026-02-13
tags: [claude-code, plugin, planning, dashboard]
related: []
phases:
  - id: 1
    title: "Bootstrap"
    status: complete
    doc: "01-Bootstrap.md"
  - id: 2
    title: "Core Skills & Dashboard"
    status: complete
    doc: "02-Core-Skills-Dashboard.md"
  - id: 3
    title: "Research & Brainstorm"
    status: complete
    doc: "03-Research-Brainstorm.md"
    depends_on: [2]
  - id: 4
    title: "Specify & Design"
    status: complete
    doc: "04-Specify-Design.md"
    depends_on: [2]
  - id: 5
    title: "Retro Skill"
    status: complete
    doc: "05-Retro-Skill.md"
    depends_on: [2]
  - id: 6
    title: "Extended Dashboard"
    status: in-progress
    doc: "06-Extended-Dashboard.md"
    depends_on: [3, 4, 5]
  - id: 7
    title: "Polish"
    status: planned
    doc: "07-Polish.md"
    depends_on: [6]
---

# Project Planner

## Overview
A Claude Code plugin for structured project planning that combines Ark-Planning's multi-phase plan depth with skill-driven workflow and an auto-generated HTML dashboard. The plugin is self-referential: it plans and builds itself.

## Architecture
- **Skills** (slash commands): 10 skills covering the full planning lifecycle from research through retrospective
- **Agents** (subprocesses): 3 agents for research, plan review, and spec review
- **Dashboard** (Python generator): Reads YAML frontmatter from all artifact types, generates static HTML
- **Templates**: Shared document templates ensure consistency across all artifact types

## Key Decisions
- YAML frontmatter as the sole machine-readable data layer (no markdown table parsing)
- Jira-like hierarchy: Plan > Phase > Task > Subtask
- Python 3 stdlib-only dashboard generator (ported from Ark-Planning)
- Self-referential: the plugin plans its own implementation

## Dependencies
- Claude Code CLI with skills and agents support
- Python 3 for dashboard generation
- No external Python packages required
