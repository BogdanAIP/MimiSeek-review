# ADR 0007 — Two ChatGPT skills split development from independent update

## Context

MimiSeek needs an independent new-chat decision before a candidate can become stable, but ChatGPT does not currently expose a reliable in-chat capability for one conversation to create another ordinary isolated conversation automatically.

Requiring the user to copy technical evaluation prompts would be fragile and unnecessary because MimiSeek state is durable in the repository.

## Decision

Expose exactly two user-facing skills:

1. `mimiseek-run` — invoked by **«Запусти Мимисик»** in the development/learning chat. It collects evidence, learns, creates and regression-checks a candidate, then freezes `PENDING_UPDATE`. It cannot promote or distribute.
2. `mimiseek-update` — invoked by **«Обнови Мимисик»** in a new independent chat. It independently evaluates the frozen candidate and may promote only on authoritative `PROMOTE`. After promotion it performs per-consumer safe-update checks before any rollout.

Repository state is the handoff between the two chats.

## Consequences

- Independence is achievable today without an automatic chat-creation executor.
- The user performs only one simple manual boundary: open a new chat and invoke the second skill.
- No technical evaluation prompt needs to be copied between chats.
- The first skill cannot silently approve its own candidate.
- The second skill may also retry deferred consumer distributions even when no new candidate exists.