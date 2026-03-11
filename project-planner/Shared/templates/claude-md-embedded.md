## Planning

Planning artifacts under `{{PLANNING_ROOT}}/` — managed by project-planner.

### Planning Structure
```
{{PLANNING_ROOT}}/
├── Makefile                      # make dashboard / make open / make clean
├── generate-dashboard.py         # Dashboard generator (Python 3, stdlib only)
├── planning-config.json          # Planning configuration
├── Shared/
│   ├── frontmatter-schema.md     # Artifact metadata schema
│   └── templates/                # Document templates
├── Research/                     # Research artifacts
├── Brainstorm/                   # Brainstorm artifacts
├── Specs/                        # Specifications
│   └── <feature>/README.md
├── Designs/                      # Technical designs
│   └── <component>/README.md
├── Plans/                        # Implementation plans
│   └── <PlanName>/
│       ├── README.md
│       ├── 01-Phase-Name.md
│       └── notes/
├── Retro/                        # Retrospectives
│   └── YYYY-MM-DD-<slug>.md
└── Dashboard/                    # Generated HTML (gitignored)
```

### Planning Skills
| Skill | Purpose |
|-------|---------|
| `/research` | Investigate a topic → `{{PLANNING_ROOT}}/Research/<topic>.md` |
| `/brainstorm` | Explore possibilities → `{{PLANNING_ROOT}}/Brainstorm/<topic>.md` |
| `/specify` | Write requirements → `{{PLANNING_ROOT}}/Specs/<feature>/README.md` |
| `/design` | Technical architecture → `{{PLANNING_ROOT}}/Designs/<component>/README.md` |
| `/plan` | Create implementation plan → `{{PLANNING_ROOT}}/Plans/<Name>/` |
| `/breakdown` | Add detail to plan phases |
| `/code-review` | Review code against the plan — drift, gaps, blind spots |
| `/debrief` | After-action notes for completed phases |
| `/retro` | Capture learnings → `{{PLANNING_ROOT}}/Retro/YYYY-MM-DD-<slug>.md` |
| `/dashboard` | Regenerate HTML dashboard |
| `/status` | Quick status summary (read-only) |

### Planning Configuration
See `{{PLANNING_ROOT}}/planning-config.json`.
Dashboard generation is opt-in: set `"dashboard": true` in `planning-config.json`, then run `make -C {{PLANNING_ROOT}} dashboard`.
