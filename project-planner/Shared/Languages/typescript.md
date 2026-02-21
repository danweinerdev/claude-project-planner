# TypeScript / JavaScript — Structural Verification

## Tools

| Tool | When | What it catches |
|------|------|-----------------|
| `tsc --noEmit` | TypeScript projects | Type errors, missing properties, incorrect generics |
| Linter (eslint / biome) | If configured in project | Unused variables, unreachable code, common bugs |

## Minimum Bar

Type-check TypeScript projects. Run the linter if configured.
