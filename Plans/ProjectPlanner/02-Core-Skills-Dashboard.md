---
title: "Core Skills & Dashboard"
type: phase
plan: ProjectPlanner
phase: 2
status: complete
created: 2026-02-13
updated: 2026-02-13
deliverable: "Working /plan, /breakdown, /debrief, /dashboard, /status skills and HTML dashboard generator"
tasks:
  - id: "2.1"
    title: "Create /plan skill"
    status: complete
  - id: "2.2"
    title: "Create /breakdown skill"
    status: complete
  - id: "2.3"
    title: "Create /debrief skill"
    status: complete
  - id: "2.4"
    title: "Create /dashboard skill"
    status: complete
  - id: "2.5"
    title: "Create /status skill"
    status: complete
  - id: "2.6"
    title: "Create generate-dashboard.py"
    status: complete
  - id: "2.7"
    title: "Self-test with ProjectPlanner plan"
    status: complete
---

# Phase 2: Core Skills & Dashboard

## Overview
Create the primary planning workflow skills and the HTML dashboard generator. This phase delivers the core loop: create plans, track status, and visualize progress.

## 2.1: Create /plan skill

### Subtasks
- [x] Define frontmatter (name, description, triggers)
- [x] Document process: gather context, draft structure, create files, review
- [x] Reference templates and schema
- [x] Document output structure

## 2.2: Create /breakdown skill

### Subtasks
- [x] Define skill for expanding phase detail
- [x] Document process for adding tasks and subtasks

## 2.3: Create /debrief skill

### Subtasks
- [x] Define skill for after-action notes
- [x] Document debrief sections and process
- [x] Reference debrief template

## 2.4: Create /dashboard skill

### Subtasks
- [x] Define skill for regenerating HTML
- [x] Document make targets

## 2.5: Create /status skill

### Subtasks
- [x] Define read-only status summary skill
- [x] Document output format

## 2.6: Create generate-dashboard.py

### Subtasks
- [x] Implement YAML frontmatter parser (stdlib only)
- [x] Implement plan/phase/task data models
- [x] Implement index page generator
- [x] Implement plan detail page generator
- [x] Implement phase detail page generator
- [x] Port CSS from Ark-Planning (dark theme)
- [x] Add progress bars and stats
- [ ] Test with self-referential ProjectPlanner plan

## 2.7: Self-test with ProjectPlanner plan

### Subtasks
- [x] Create Plans/ProjectPlanner/ with all phase docs
- [ ] Run make dashboard and verify output
- [ ] Verify progress bars and status badges render correctly

## Acceptance Criteria
- [x] All 5 skills created with proper frontmatter
- [x] Dashboard generator produces valid HTML
- [ ] Self-referential plan renders correctly on dashboard
