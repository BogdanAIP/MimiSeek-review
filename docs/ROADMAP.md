# Roadmap

The roadmap is ordered. Later stages may be refined, but a stage is not complete merely because implementation exists; its acceptance conditions must be satisfied.

## Stage 0 — Continuous-development foundation — IN REVIEW

Goal: make the repository self-describing so any fresh development chat can continue without previous-chat memory.

Acceptance:

- canonical product/current-state/roadmap/architecture/protocol owners exist;
- document ownership is explicit;
- durable architectural decisions are recorded;
- branch/PR workflow is established.

## Stage 1 — First stable reviewer baseline — NEXT

Goal: derive the first reusable MimiSeek Review baseline from the accepted CAP and UV review policies.

Work:

- resolve exact accepted CAP/UV policy refs;
- classify each rule as generic or project-specific;
- define stable reviewer identity/version format;
- define a deterministic consumer pin/synchronization mechanism;
- preserve project-specific policy overlays.

Acceptance:

- both CAP and UV can invoke the common reviewer without losing their own governing requirements;
- the stable version is immutable and identifiable by version + commit/hash;
- compatibility behavior is documented and tested.

## Stage 2 — Consumer integration

Goal: make CAP and UV real consumers of the standalone stable reviewer.

Acceptance:

- both repositories pin an exact stable reviewer identity;
- updates are explicit and auditable;
- project-local policy remains authoritative for project-specific semantics;
- stale or mismatched reviewer identity fails closed.

## Stage 3 — Review outcome collection

Goal: collect structured real-world evidence from review cycles.

Model at minimum:

- review run identity;
- reviewer/version;
- exact BASE/HEAD;
- finding identity/category/severity;
- disposition (`CONFIRMED`, `REJECTED`, `SUPERSEDED`);
- discovery source (MimiSeek, Codex, development, other);
- fix/verified head when known.

Acceptance: a closed PR can be reconstructed into a trustworthy sequence of review outcomes without relying on chat history.

## Stage 4 — Learning events and regression corpus

Goal: transform adjudicated outcomes into reusable learning evidence.

Events include:

- OUR_HIT;
- OUR_MISS_CODEX_HIT;
- OUR_HIT_CODEX_MISS;
- OUR_FALSE_POSITIVE;
- BOTH_MISS_LATER_CONFIRMED;
- other evidence-backed variants.

Acceptance: events are derived from immutable identities and adjudicated evidence; BUGGY→FIXED pairs are usable as regression cases.

## Stage 5 — Learner

Goal: analyze repeated successes/misses and propose transferable reviewer changes.

Acceptance:

- proposed mechanics are generic, not SHA/file memorization;
- each proposal cites learning evidence;
- learner can create a candidate but cannot make it stable;
- existing protected capabilities are identified.

## Stage 6 — Candidate regression evaluation

Goal: automatically evaluate candidate reviewer versions against known BUGGY/FIXED and protected-capability cases.

Acceptance:

- target BUGGY detection is measured;
- old findings must disappear on FIXED;
- false-positive/regression behavior is measured;
- candidate cannot modify the evaluation policy governing its run.

## Stage 7 — Fresh independent evaluator

Goal: use a fresh ordinary-chat evaluator to independently validate promotion evidence.

Result: `PROMOTE`, `REJECT`, or `ABSTAIN`.

Acceptance:

- evaluator resolves evidence independently and read-only;
- insufficient evidence yields `ABSTAIN`;
- candidate/learner cannot authoritatively decide promotion.

## Stage 8 — Shadow real-PR evaluation

Goal: run stable and candidate on suitable new PR heads without allowing the candidate to control merge decisions.

Acceptance: real-world confirmed/rejected outcomes can compare protected capabilities and new gains without reviewer-result leakage where isolation is required.

## Stage 9 — Automated promotion and distribution

Goal: promote a candidate to stable only after the fixed evaluation gate passes, then make the new stable version available to consumers.

Acceptance:

- promotion is atomic and auditable;
- rollback remains possible;
- consumers can update or remain pinned according to contract;
- no project is silently moved to an incompatible reviewer.

## Stage 10 — Continuous self-improvement

Goal: close the loop:

`real PRs → outcomes → learning → candidate → regression/shadow evaluation → fresh evaluator → stable → more real PRs`.

Acceptance: the loop can operate without technical adjudication by the human project owner except for policy/product choices or ambiguous cases explicitly escalated by product policy.
