# ADR 0004 — Fresh independent promotion evaluator

## Context

The learner and candidate should not be the sole judges of whether their own changes are improvements. The project owner is not expected to perform detailed technical adjudication of reviewer internals.

## Decision

Semantic promotion evaluation uses a separately governed fresh ordinary-chat evaluator operating read-only against immutable identities and evidence. Its result is `PROMOTE`, `REJECT`, or `ABSTAIN`.

## Consequences

- Technical promotion does not require the human owner to review reviewer implementation details.
- Insufficient evidence preserves the stable version through `ABSTAIN`.
- The evaluator itself requires a strict protocol and evidence contract.
