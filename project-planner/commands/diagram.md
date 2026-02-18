---
name: diagram
description: "Generate Mermaid diagrams from plans, designs, or specs. Triggers: /diagram, draw a diagram, visualize, flowchart, sequence diagram, architecture diagram"
---

# /diagram — Generate Mermaid Diagrams

## Path Resolution
**Artifacts** (Plans/, Research/, Specs/, etc.) are read from and written to the **planning root**.
Read `planning-config.json` (at repo root) to find the planning root:
- `planningRoot` of `"."` or absent → artifacts at repository root
- `planningRoot` of `"<dir>"` → artifacts under `<dir>/` from repo root
- `planningRoot` of `"/absolute/path"` → artifacts in an external directory (standalone planning repo)

**Templates and schema** (`Shared/`) are read from the **plugin directory**, not from the planning root. The plugin directory contains `commands/`, `agents/`, and `Shared/` as siblings — find it by globbing for `**/commands/research.md` and going one level up.

## When to Use
When you need a visual representation of architecture, data flow, task dependencies, or system interactions. Produces Mermaid diagrams that render in GitHub, VS Code, and most markdown viewers.

## Process

1. **Determine Subject**
   - Ask what to diagram (or infer from context)
   - Read the relevant artifact(s) — plan, design, spec, or codebase
   - Identify the best diagram type for the subject

2. **Choose Diagram Type**

   | Subject | Recommended Type |
   |---------|-----------------|
   | Plan phase dependencies | `graph TD` (directed graph) |
   | Task breakdown | `graph TD` with subgraphs per phase |
   | Data flow | `flowchart LR` |
   | API interactions | `sequenceDiagram` |
   | System architecture | `graph TD` with subgraphs per component |
   | State transitions | `stateDiagram-v2` |
   | Timeline / Gantt | `gantt` |
   | Entity relationships | `erDiagram` |
   | Class structure | `classDiagram` |

3. **Generate Diagram**
   - Build the Mermaid source from the artifact data
   - Use clear, descriptive node labels
   - Group related nodes with `subgraph` where appropriate
   - Use consistent styling: status colors match dashboard conventions
     - Green (`:::complete`): complete / approved / implemented
     - Amber (`:::active`): in-progress / active / review
     - Gray (`:::planned`): planned / draft
     - Red (`:::blocked`): blocked

4. **Place Diagram**
   - **In an existing artifact**: Add a `## Diagram` section to the relevant document
   - **Standalone**: Create `Diagrams/<subject-slug>.md` with frontmatter:
     ```yaml
     ---
     title: "Diagram Title"
     type: diagram
     created: YYYY-MM-DD
     updated: YYYY-MM-DD
     tags: [diagram-type]
     related: [path/to/source/artifact]
     ---
     ```

5. **Present to User**
   - Show the Mermaid source in a code block
   - Explain what the diagram represents
   - Ask if adjustments are needed (more/less detail, different type, different scope)

## Diagram Conventions

### Plan Dependency Diagram
```mermaid
graph TD
    P1[Phase 1: Setup] --> P2[Phase 2: Core]
    P1 --> P3[Phase 3: API]
    P2 --> P4[Phase 4: Integration]
    P3 --> P4
    P4 --> P5[Phase 5: Polish]

    class P1 complete
    class P2 active
    class P3 planned
    class P4 planned
    class P5 planned
```

### Style Definitions
Include at the bottom of each diagram:
```
classDef complete fill:#10b981,stroke:#059669,color:#fff
classDef active fill:#f59e0b,stroke:#d97706,color:#fff
classDef planned fill:#6b7280,stroke:#4b5563,color:#fff
classDef blocked fill:#ef4444,stroke:#dc2626,color:#fff
```

## Output
Either modifies an existing artifact (adding a `## Diagram` section) or creates:
```
Diagrams/<subject-slug>.md
```

## Notes
- Keep diagrams focused — if it's too complex, split into multiple diagrams
- Prefer left-to-right (`LR`) for flows, top-down (`TD`) for hierarchies
- Use short node labels; add detail in surrounding markdown, not in the diagram
