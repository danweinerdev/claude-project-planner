# Orchestration Model

The primary context acts as a **tech lead** — it reads enough to make informed decisions about what to delegate, then delegates execution to agents. Only summarized results return to the primary context.

## Roles

**Primary context** handles:
- User interaction (questions, confirmations, approvals)
- Scoping and delegation decisions (what work to do, which agent does it)
- Reviewing agent results and deciding next steps
- Lightweight reads needed to make delegation decisions (e.g., reading a plan README to know which phase to implement)

**Agents** handle:
- Heavy reading (scanning many artifacts, reading large codebases)
- Analysis (complexity analysis, artifact hygiene checks, adversarial review prep)
- Code changes (implementation, simplification, fixes)
- Reviews (code review, plan review, spec review)

## Principles

1. **Delegate execution, keep decisions.** If the work is reading 15 files and summarizing, that's an agent's job. If the work is choosing between two approaches based on a summary, that's the primary context's job.

2. **Not everything gets delegated.** Lightweight reads, user conversations, and creative judgment stay in the primary context. The overhead of spinning up an agent isn't worth it for a single file read or a quick decision.

3. **Agents return summaries, not raw content.** When an agent reads artifacts or code, it returns structured findings — not the full file contents. The primary context works from these summaries.

4. **Parallelize independent work.** When multiple agents can work independently (e.g., implementing tasks in a wave, scanning different artifact types), launch them concurrently.

5. **Resume agents for follow-ups.** When an agent's work needs a correction or continuation, resume it rather than starting fresh — preserves context and avoids re-reading.
