---
title: "Extended Dashboard"
type: phase
plan: ProjectPlanner
phase: 6
status: complete
created: 2026-02-13
updated: 2026-02-13
deliverable: "Dashboard supports all artifact types with cross-navigation"
tasks:
  - id: "6.1"
    title: "Add knowledge base page"
    status: complete
  - id: "6.2"
    title: "Add retros page"
    status: complete
  - id: "6.3"
    title: "Add spec/design detail pages"
    status: complete
  - id: "6.4"
    title: "Add recent activity to index"
    status: complete
  - id: "6.5"
    title: "Add cross-artifact navigation"
    status: complete
---

# Phase 6: Extended Dashboard

## Overview
Extend the dashboard generator to handle all artifact types beyond plans: research, brainstorm, specs, designs, and retros.

## 6.1: Add knowledge base page

### Subtasks
- [x] Parse Research/ and Brainstorm/ frontmatter
- [x] Generate knowledge.html with index cards
- [x] Add navigation link from main index

## 6.2: Add retros page

### Subtasks
- [x] Parse Retro/ frontmatter
- [x] Generate retros.html with chronological index
- [x] Add navigation link from main index

## 6.3: Add spec/design detail pages

### Subtasks
- [x] Parse Specs/ and Designs/ frontmatter
- [x] Generate detail pages with content rendering
- [x] Add to main navigation

## 6.4: Add recent activity to index

### Subtasks
- [x] Track file modification times
- [x] Show recently updated artifacts on main index

## 6.5: Add cross-artifact navigation

### Subtasks
- [x] Parse `related` frontmatter field
- [x] Render cross-links between artifacts
- [x] Add breadcrumb navigation for all artifact types

## Acceptance Criteria
- [x] All artifact types appear on dashboard
- [x] Cross-links between related artifacts work
- [x] Navigation is consistent across all pages
