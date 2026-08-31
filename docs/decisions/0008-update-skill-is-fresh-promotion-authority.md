# ADR 0008 — The update skill is the fresh promotion authority

## Context

The project owner should not be required to inspect reviewer implementation, regression cases, or semantic code-review details for each candidate. At the same time, the chat that created a candidate must not be the authority that promotes it.

## Decision

Under a fixed evaluation policy, `mimiseek-update` running in a new independent ChatGPT conversation returns the authoritative `PROMOTE`, `REJECT`, or `ABSTAIN` decision for the frozen pending candidate.

Routine human technical approval is not part of promotion. The human supplies context isolation by opening the new chat and invoking **«Обнови Мимисик»**.

Only `PROMOTE`, together with successful mechanical identity/transaction checks, may advance stable and trigger consumer update PRs.

## Consequences

- The system is usable now without automatic chat creation.
- Candidate creation and promotion remain context-isolated.
- `ABSTAIN` safely preserves stable when evidence is insufficient.
- Product/evaluation-policy changes remain separate governed decisions.