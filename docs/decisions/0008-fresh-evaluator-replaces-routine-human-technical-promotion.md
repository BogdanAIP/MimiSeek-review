# ADR 0008 — Fresh evaluator replaces routine human technical promotion approval

## Context

The project owner should not be required to inspect reviewer implementation, regression cases, or semantic code-review details to decide whether every candidate is technically better.

## Decision

Under a fixed accepted evaluation policy, a fresh independent ChatGPT evaluator returns the authoritative `PROMOTE`, `REJECT`, or `ABSTAIN` decision for a candidate.

Routine human technical approval is not a promotion requirement.

The human owner remains authority for explicit product/policy changes, not per-candidate technical adjudication under an already-fixed policy.

## Consequences

- Normal promotion can become fully automated.
- `ABSTAIN` safely preserves stable when evidence is insufficient.
- Evaluation-policy changes remain separate governed decisions and cannot be smuggled into a candidate promotion.
