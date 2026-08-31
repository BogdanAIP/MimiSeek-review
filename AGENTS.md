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
9. For ChatGPT orchestration/skill changes, read `docs/CHATGPT_ENTRYPOINT.md` and the applicable `.agents/skills/` file.
10. Independently resolve live Git/GitHub state before relying on branch, PR, CI, or review status.

Previous-chat prose is context only, never authority.

## Product boundary

MimiSeek Review improves, evaluates, releases, and distributes the generic reviewer.

It does **not** own the ordinary development/review/fix loop inside CAP, UV, or other consumer repositories. Consumers provide structured adjudicated outcomes and receive stable reviewer updates.

## Document ownership

One fact must have one canonical owner.

- Product purpose and non-goals: `docs/PRODUCT.md`
- Current project position and next canonical action: `docs/CURRENT_STATE.md`
- Future sequencing and acceptance conditions: `docs/ROADMAP.md`
- System boundaries and component authority: `docs/ARCHITECTURE.md`
- Cross-chat MimiSeek implementation process: `docs/DEVELOPMENT_PROTOCOL.md`
- Stable/candidate/learning lifecycle: `docs/REVIEWER_LIFECYCLE.md`
- Consumer evidence/update contract: `docs/INTEGRATION_CONTRACT.md`
- Candidate evaluation and promotion rules: `docs/EVALUATION_POLICY.md`
- ChatGPT one-skill entry point: `docs/CHATGPT_ENTRYPOINT.md`
- Accepted evidence pointers: `docs/EVIDENCE_INDEX.md`
- Durable architectural decisions and reasons: `docs/decisions/`
- Registered consumers: `config/consumers.json`
- Canonical structured learning/regression data: `data/`

Do not duplicate authoritative state in convenience documents or reports.

## Development rules

- Work through branches and pull requests after repository bootstrap.
- Bind semantic review evidence to immutable repository/base/head/reviewer identity.
- Findings are assertions until adjudicated as `CONFIRMED`, `REJECTED`, `SUPERSEDED`, or another explicitly governed state.
- Independent reviewer/evaluator roles must use fresh ordinary-chat contexts when their protocol requires independence.
- Learner/candidate may not change the evaluation policy used to judge that candidate.
- Project-specific rules stay in consuming repositories unless an extracted rule is demonstrably generic.
- Prefer fail-closed behavior when evidence, identity, freshness, compatibility, or authority is ambiguous.
- A promoted stable reviewer is distributed through auditable consumer update changes, normally PRs.

## Before ending significant work

Update only canonical owners whose truth changed:

1. code/tests/CI;
2. `docs/CURRENT_STATE.md` if project position changed;
3. `docs/ROADMAP.md` if stage state or acceptance changed;
4. `docs/EVIDENCE_INDEX.md` when accepted evidence changes;
5. applicable architecture/contract/policy owner;
6. decision record only for a durable architectural decision.

Do not create per-chat handoff files, daily logs, or shadow status documents. The next chat must continue from repository state.
