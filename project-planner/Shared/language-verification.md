# Language-Specific Verification — What Good Looks Like

What "good and complete" looks like beyond passing tests. Each language file covers **structural verification tools** (sanitizers, static analysis, type checkers) and **quality patterns** (idioms, safety conventions, review checkpoints) specific to that language. These run during implementation, not as deferred acceptance criteria.

## How to Use

1. Detect the project language from file extensions, build files, or project config
2. Read the matching file from `Shared/Languages/`
3. Include the relevant checks in your output (verification fields, testing strategy, review findings)

When a project uses multiple languages, read and apply each relevant file.

## Skill Integration

- **`/design`** — include relevant tools in the Testing Strategy section
- **`/plan` and `/breakdown`** — include in task `verification` fields where appropriate
- **`/implement`** — run these checks as part of verifying task completion
- **`/code-review`** — check that structural verification was actually performed

## Languages

| Language | File |
|----------|------|
| C / C++ | `Shared/Languages/cpp.md` |
| Rust | `Shared/Languages/rust.md` |
| Go | `Shared/Languages/go.md` |
| Python | `Shared/Languages/python.md` |
| TypeScript / JavaScript | `Shared/Languages/typescript.md` |
| Java / Kotlin | `Shared/Languages/java.md` |
| Swift | `Shared/Languages/swift.md` |

## Unlisted Languages

For languages not listed: look for an existing CI config, Makefile, or package scripts to identify the project's structural checks. If the project already runs static analysis, linting, or sanitizers in CI, those same checks belong in task verification. Don't introduce new tooling the project doesn't already use — but do ensure existing tools are actually run.
