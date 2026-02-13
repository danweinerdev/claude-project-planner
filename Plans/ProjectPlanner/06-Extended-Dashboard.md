---
title: "Extended Dashboard"
type: phase
plan: ProjectPlanner
phase: 6
status: planned
created: 2026-02-13
updated: 2026-02-13
deliverable: "Dashboard supports all artifact types with cross-navigation"
tasks:
  - id: "6.1"
    title: "Add knowledge base page"
    status: planned
  - id: "6.2"
    title: "Add retros page"
    status: planned
  - id: "6.3"
    title: "Add spec/design detail pages"
    status: planned
  - id: "6.4"
    title: "Add recent activity to index"
    status: planned
  - id: "6.5"
    title: "Add cross-artifact navigation"
    status: planned
---

# Phase 6: Extended Dashboard

## Overview
Extend the dashboard generator to handle all artifact types beyond plans: research, brainstorm, specs, designs, and retros.

## 6.1: Add knowledge base page

### Subtasks
- [ ] Parse Research/ and Brainstorm/ frontmatter
- [ ] Generate knowledge.html with index cards
- [ ] Add navigation link from main index

## 6.2: Add retros page

### Subtasks
- [ ] Parse Retro/ frontmatter
- [ ] Generate retros.html with chronological index
- [ ] Add navigation link from main index

## 6.3: Add spec/design detail pages

### Subtasks
- [ ] Parse Specs/ and Designs/ frontmatter
- [ ] Generate detail pages with content rendering
- [ ] Add to main navigation

## 6.4: Add recent activity to index

### Subtasks
- [ ] Track file modification times
- [ ] Show recently updated artifacts on main index

## 6.5: Add cross-artifact navigation

### Subtasks
- [ ] Parse `related` frontmatter field
- [ ] Render cross-links between artifacts
- [ ] Add breadcrumb navigation for all artifact types

## Acceptance Criteria
- [ ] All artifact types appear on dashboard
- [ ] Cross-links between related artifacts work
- [ ] Navigation is consistent across all pages
