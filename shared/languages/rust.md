# Rust — Structural Verification

## Tools

| Tool | When | What it catches |
|------|------|-----------------|
| `cargo clippy -- -D warnings` | Always | Common mistakes, anti-patterns, performance issues |
| `miri` | `unsafe` code, raw pointers, FFI boundaries | Undefined behavior, aliasing violations, memory errors |

## Minimum Bar

Clippy with warnings-as-errors on every phase.
