---
name: excavate
description: "Progressive codebase discovery and documentation. Triggers: /excavate, excavate, explore codebase, map the code, document the system, what does this code do"
---

# /excavate — Progressive Codebase Discovery

## Path Resolution
**Artifacts** (Plans/, Research/, Specs/, etc.) are read from and written to the **planning root**.
Read `planning-config.json` (at repo root) to find the planning root:
- `planningRoot` of `"."` or absent → artifacts at repository root
- `planningRoot` of `"<dir>"` → artifacts under `<dir>/` from repo root
- `planningRoot` of `"/absolute/path"` → artifacts in an external directory (standalone planning repo)

**Templates and schema** (`Shared/`) are read from the **plugin directory** (the project-planner repo loaded via `--plugin-dir`), not from the planning root.

Run dashboard commands (`make dashboard`) from the planning root directory.

## When to Use
When you need to understand an unfamiliar codebase or subsystem before planning work against it. Produces research artifacts from systematic code exploration — not a quick scan, but a deep dive that builds on itself.

## Process

1. **Choose Entry Point**
   - Ask what area of the codebase to explore (or the whole thing)
   - If a `planning-config.local.json` exists, read it to find local repo paths
   - Identify starting points:
     - Entry files (`main.py`, `index.ts`, `cmd/`, `src/main/`)
     - Configuration files (understand what's configurable)
     - Package manifests (understand dependencies)
     - README/docs (understand intent)

2. **Surface Survey**
   - Invoke the `researcher` agent to scan the target codebase:
     - Directory structure and file organization
     - Key modules/packages and their responsibilities
     - Entry points and public APIs
     - Configuration and environment setup
   - Map the high-level architecture: what talks to what

3. **Depth Passes**
   Work through the codebase layer by layer. For each pass:

   **Pass 1: Structure**
   - Module boundaries and dependency graph
   - Shared types / data models
   - Configuration flow

   **Pass 2: Behavior**
   - Request/data flow through the system
   - State management patterns
   - Error handling patterns
   - Key algorithms or business logic

   **Pass 3: Patterns**
   - Recurring patterns and conventions
   - Testing approach and coverage
   - Build/deploy pipeline
   - Known technical debt (TODOs, FIXMEs, deprecated code)

   Each pass produces findings that inform the next. Don't try to understand everything at once.

4. **Synthesize**
   - Create `Research/<codebase-or-subsystem-slug>.md` using `Shared/templates/research.md`
   - Organize findings into:
     - **Architecture**: How the system is structured
     - **Key Patterns**: Conventions the codebase follows
     - **Data Flow**: How data moves through the system
     - **Dependencies**: External and internal dependencies
     - **Findings**: Insights, risks, technical debt
     - **Open Questions**: What remains unclear after exploration

5. **Link**
   - Add cross-references to any related artifacts in `related` frontmatter
   - If the excavation reveals spec-worthy features, note them as recommendations

6. **Regenerate Dashboard**
   - Run `make dashboard` from the planning root to update the HTML dashboard

## Output
```
Research/<codebase-or-subsystem-slug>.md
```

## Depth Guidance

- **Breadth first, depth second**: Map the whole system before diving into any one part
- **Follow the data**: Understanding data flow reveals architecture faster than reading code top-down
- **Name the patterns**: If the codebase uses MVC, hexagonal, event-driven, etc., name it — this anchors future discussions
- **Note surprises**: Anything that doesn't match expectations is worth documenting — it's either a bug, a design decision, or tribal knowledge
- **Stop when diminishing returns**: You don't need to understand every line. Stop when you can confidently describe what each major component does and how they interact

## Context
- Template: `Shared/templates/research.md`
- Schema: `Shared/frontmatter-schema.md`
- Agent: `researcher`
- Local repo paths: `planning-config.local.json`
