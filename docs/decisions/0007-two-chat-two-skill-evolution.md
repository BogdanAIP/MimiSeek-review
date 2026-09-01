# ADR 0007 — Two ChatGPT roles split development from independent update

## Context

MimiSeek needs an independent new-chat decision before a candidate can become stable. Consequence-bearing deferred-distribution retries also act on the globally promoted reviewer/consumer boundary and must not silently collapse back into the run/development conversation.

Requiring the user to copy technical evaluation prompts between chats would be fragile and unnecessary because MimiSeek state is durable in the repository.

The run entry point also has to remain useful while MimiSeek itself is still being built; it cannot assume the later collector/learner/regression pipeline already exists.

## Decision

Expose exactly two user-facing ChatGPT roles:

1. Native identity `mimiseek-review-run`, backed by `.agents/skills/mimiseek-run/SKILL.md`. It reconstructs live repository state and continues the next canonical work. During bootstrap it continues repository development; once the operational learning stages exist, it collects evidence, learns, creates and regression-checks a candidate, then freezes independent-update state. It cannot promote or distribute.
2. Native identity `mimiseek-review-update`, backed by `.agents/skills/mimiseek-update/SKILL.md`. Every real invocation occurs in a new independent chat. When an eligible frozen candidate exists, it independently evaluates that candidate and may promote only on authoritative `PROMOTE`. It may perform per-consumer safe-update checks only for the exact current authoritatively promoted stable. It may also reconcile previously deferred distributions in a later fresh update chat when no new candidate exists and durable pending-distribution state proves the rollout authority.

Repository state is the handoff between the roles and between repeated update invocations.

## Consequences

- The installed/native roles remain stable entry points while implementation details evolve in the repository.
- Every consequence-bearing update invocation uses one simple manual boundary: open a new chat and invoke the second role.
- No technical evaluation or distribution prompt needs to be copied between chats.
- The first role cannot silently approve its own candidate or update consumers.
- Bootstrap work cannot pretend later operational stages already exist.
- The second role can reconcile deferred consumer distributions independently of candidate creation, but only for an already-authoritatively-promoted stable with durable pending-distribution authority.
