# Go — Structural Verification

## Tools

| Tool | When | What it catches |
|------|------|-----------------|
| `go vet ./...` | Always | Printf format mismatches, unreachable code, suspicious constructs |
| `-race` flag on tests | Goroutines, channels, shared state | Data races |
| `staticcheck` | Always (if available) | Additional correctness checks beyond go vet |

## Minimum Bar

`go vet` on every phase. `-race` when goroutines or shared state are involved.
