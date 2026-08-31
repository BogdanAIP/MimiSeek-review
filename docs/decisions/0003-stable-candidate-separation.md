# ADR 0003 — Stable and candidate reviewer separation

## Context

A self-improving reviewer needs to propose changed behavior without immediately making unproven changes authoritative for real projects.

## Decision

Reviewer versions have separate stable and candidate roles. Learning may produce a candidate, but consumers use stable versions unless a separate explicit experimental path says otherwise.

## Consequences

- Candidate evaluation can fail without changing the current stable reviewer.
- Rollback/history remain meaningful.
- Shadow evaluation is possible without letting experimental behavior control project acceptance.
