# AGENTS.md

This file governs development work in MimiSeek Review.

## Bootstrap for every new chat

Before changing the repository:

1. Read `docs/PRODUCT.md`.
2. Read `docs/CURRENT_STATE.md`.
3. Read `docs/ROADMAP.md`.
4. Read the relevant architecture section in `docs/ARCHITECTURE.md`.
5. Read applicable decisions under `docs/decisions/`.
6. Read `docs/DEVELOPMENT_PROTOCOL.md`.
7. For reviewer-version or learning changes, also read `docs/REVIEWER_LIFECYCLE.md` and `docs/EVALUATION_POLICY.md`.
8. For consumer integration, read `docs/INTEGRATION_CONTRACT.md`.
9. Independently resolve live Git/GitHub state before relying on branch, PR, CI, or review status.

Previous-chat prose is context only, never authority.

## Document ownership

One fact must have one canonical owner.

- Product purpose and non-goals: `docs/PRODUCT.md`
- Current project position and next canonical action: `docs/CURRENT_STATE.md`
- Future sequencing and acceptance conditions: `docs/ROADMAP.md`
- System boundaries and component authority: `docs/ARCHITECTURE.md`
- Cross-chat implementation/review process: `docs/DEVELOPMENT_PROTOCOL.md`
- Stable/candidate/learning lifecycle: `docs/REVIEWER_LIFECYCLE.md`
- Consumer repository contract: `docs/INTEGRATION_CONTRACT.md`
- Candidate evaluation and promotion rules: `docs/EVALUATION_POLICY.md`
- Accepted evidence pointers: `docs/EVIDENCE_INDEX.md`
- Durable architectural decisions and their reasons: `docs/decisions/`

Do not duplicate authoritative state in convenience documents.

## Development rules

- Work through branches and pull requests after repository bootstrap.
- Bind semantic review evidence to immutable `BASE_SHA..HEAD_SHA`.
- A material HEAD change makes earlier exact-head review evidence stale.
- Findings are not truth merely because a reviewer emitted them. They require disposition such as `CONFIRMED`, `REJECTED`, or `SUPERSEDED`.
- Independent reviewer and evaluator roles must use fresh ordinary-chat contexts when their governing protocol requires independence.
- The reviewer candidate may not change the evaluation policy used to judge that candidate.
- Project-specific rules stay in consuming repositories unless an extracted rule is demonstrably generic.
- Prefer fail-closed behavior when evidence, identity, or authority is ambiguous.

## Before ending significant work

Update only the canonical owners affected by the change:

1. code/tests and CI configuration;
2. `docs/CURRENT_STATE.md` if project position changed;
3. `docs/ROADMAP.md` if a stage changed state or acceptance criteria changed;
4. `docs/EVIDENCE_INDEX.md` when new accepted evidence exists;
5. the applicable architecture/contract/policy owner if its truth changed;
6. a decision record only for a durable architectural decision.

Do not create per-chat handoff files, daily logs, or shadow status documents. The next chat must be able to continue from the repository itself.
