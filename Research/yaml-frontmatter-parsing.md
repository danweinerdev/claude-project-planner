---
title: "YAML Frontmatter Parsing Approaches"
type: research
status: active
created: 2026-02-13
updated: 2026-02-13
tags: [yaml, parsing, python]
related: [Plans/ProjectPlanner]
---

# YAML Frontmatter Parsing Approaches

## Context
The dashboard generator needs to parse YAML frontmatter from markdown files without external dependencies (stdlib only).

## Findings

### Key Insights
- Python stdlib has no YAML parser; PyYAML is the standard library but adds a dependency
- A custom parser handling the subset we use (scalars, inline lists, block lists of objects) is straightforward
- Our frontmatter is well-structured and predictable — no need for full YAML spec compliance

### Sources
- YAML 1.2 specification
- Python dataclasses documentation

## Analysis

### Implications
A custom parser keeps the project dependency-free while handling all our use cases.

### Recommendations
Implement a focused parser that handles our specific frontmatter patterns rather than attempting full YAML compliance.

## Open Questions
- Should we validate frontmatter against the schema?
