# ADR 0007 — Two ChatGPT skills form the practical evolution boundary

## Context

MimiSeek needs independent promotion evaluation, but the current ChatGPT environment cannot rely on one chat automatically creating another ordinary chat and retrieving its result. Requiring the user to copy technical evaluation prompts would add unnecessary manual ceremony.

## Decision

Expose two user-facing skills:

1. **`mimiseek-run`** — invoked as **«Запусти Мимисик»** in the current chat. It collects evidence, learns, builds/evaluates a candidate, and freezes a durable `PENDING_UPDATE` package. It cannot promote or distribute.
2. **`mimiseek-update`** — invoked as **«Обнови Мимисик»** in a new chat. It independently reconstructs and evaluates the pending package. Only authoritative `PROMOTE` may advance stable and create consumer update PRs.

The repository, not copied chat text, is the handoff between the two skills.

## Consequences

- The workflow is usable with current ChatGPT capabilities.
- The user performs only one non-technical action between phases: open a new chat.
- Candidate creation and promotion remain context-isolated.
- Future automatic fresh-chat execution may automate the handoff without changing the semantic two-role contract.