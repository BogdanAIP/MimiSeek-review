# ADR 0007 — Two ChatGPT roles split development from independent update

## Context

MimiSeek needs an independent new-chat decision before a candidate can become stable. Requiring the user to copy technical evaluation prompts between chats would be fragile and unnecessary because MimiSeek state is durable in the repository.

The run entry point also has to remain useful while MimiSeek itself is still being built; it cannot assume the later collector/learner/regression pipeline already exists.

## Decision

Expose exactly two user-facing ChatGPT roles:

1. Native identity `mimiseek-review-run`, backed by `.agents/skills/mimiseek-run/SKILL.md`. It reconstructs live repository state and continues the next canonical work. During bootstrap it continues repository development; once the operational learning stages exist, it collects evidence, learns, creates and regression-checks a candidate, then freezes independent-update state. It cannot promote or distribute.
2. Native identity `mimiseek-review-update`, backed by `.agents/skills/mimiseek-update/SKILL.md`. It is invoked in a new independent chat, independently evaluates an eligible frozen candidate, and may promote only on authoritative `PROMOTE`. After promotion it performs per-consumer safe-update checks before any rollout. It may also retry previously deferred distributions when no new candidate exists.

Repository state is the handoff between the two chats.

## Consequences

- The installed/native roles remain stable entry points while implementation details evolve in the repository.
- The user performs only one simple manual independence boundary when promotion evaluation is required: open a new chat and invoke the second role.
- No technical evaluation prompt needs to be copied between chats.
- The first role cannot silently approve its own candidate.
- Bootstrap work cannot pretend later operational stages already exist.
- The second role can reconcile deferred consumer distributions independently of candidate creation.
