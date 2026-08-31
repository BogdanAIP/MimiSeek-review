# ADR 0007 — One ChatGPT skill is the user entry point for reviewer evolution

## Context

The internal evolution pipeline has multiple roles for authority separation, but requiring the user to manually invoke collector, learner, regression, evaluator, promotion, and distribution would defeat the automation goal.

## Decision

Expose one primary ChatGPT skill, `mimiseek-evolve`, that starts and coordinates the full evolution pipeline.

Internal roles remain separate. In particular, promotion semantic evaluation must run in a new isolated ChatGPT context using the internal reviewer-evaluation contract.

## Consequences

- User interaction is one command/invocation.
- Internal separation of authority is preserved.
- Missing fresh-context execution fails closed rather than falling back to same-chat promotion judgment.
