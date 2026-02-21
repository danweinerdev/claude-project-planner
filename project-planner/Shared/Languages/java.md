# Java / Kotlin — Structural Verification

## Tools

| Tool | When | What it catches |
|------|------|-----------------|
| SpotBugs / Error Prone | If configured in project | Null dereference, concurrency bugs, resource leaks |
| Detekt (Kotlin) | Kotlin projects, if configured | Code smells, complexity, potential bugs |

## Minimum Bar

Run the project's existing static analysis if configured (check Gradle/Maven plugins). Don't introduce new tools unless the project already uses them.
