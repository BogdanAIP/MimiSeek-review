# Evaluation Policy

Status: bootstrap policy; detailed numeric thresholds are intentionally deferred until real baseline data exist.

## Purpose

Define when a reviewer candidate is sufficiently proven to become stable and which independent authority may make that transition.

The same promotion authority governs both creation of the **first** stable reviewer and every later stable transition. There is no separate bootstrap-stable shortcut.

## Separation rule

A candidate reviewer and the learner that produced it may not authoritatively change the evaluation policy governing that candidate's promotion.

Changes to this policy are separate governed product changes and cannot retroactively weaken an already-started candidate evaluation.

## Fresh evaluator authority

Semantic promotion evaluation uses a fresh ordinary ChatGPT context operating independently and read-only against immutable candidate/stable/policy/evidence identities.

That fresh evaluator returns exactly one authoritative decision:

- `PROMOTE`
- `REJECT`
- `ABSTAIN`

`PROMOTE` is sufficient semantic authority for the automated promotion transaction when all mechanical identity/transaction checks also pass. Routine human technical approval is **not** part of the normal promotion path.

If `stable_before = none`, authoritative `PROMOTE` establishes the first stable. `REJECT` or `ABSTAIN` leaves stable unset.

If a stable already exists, authoritative `PROMOTE` advances stable to the candidate. `REJECT` or `ABSTAIN` leaves the existing stable unchanged.

If the system cannot prove that the evaluator ran in the required fresh isolated context, the result is not promotion-authoritative.

## Human role

The human owner is not expected to inspect candidate implementation or regression evidence to decide routine promotion, including the first stable promotion once the fixed policy and evidence package exist.

Human decisions are reserved for explicit product/policy choices, such as changing evaluation philosophy, compatibility requirements, acceptable risk, or other owner-reserved governance. Such changes are separate from evaluating a specific candidate under already-fixed policy.

## Evidence classes

Candidate evaluation may use:

1. known BUGGY cases with confirmed target defects;
2. corresponding FIXED cases to detect memorized/over-broad findings;
3. protected-capability regression cases;
4. rejected-finding/false-positive cases;
5. suitable shadow runs on fresh real PR heads;
6. later external holdout benchmarks;
7. for the first candidate only, an immutable Stage 1 baseline seed as non-authoritative comparison evidence.

Historical corpus is learning/regression evidence and is not by itself a neutral external benchmark. The Stage 1 baseline seed is never promotion authority and is never a stable identity.

## Minimum semantic requirements for promotion

A candidate must demonstrate all requirements of the finalized quantitative gate, including:

- no critical protected-capability regression;
- target improvements supported by confirmed defects, not merely more emitted findings;
- old target findings do not persist incorrectly on corresponding FIXED cases;
- false-positive behavior does not deteriorate beyond allowed policy;
- review/evaluation identities and evidence are complete/current;
- any required real-world shadow evidence is satisfied;
- no candidate-controlled modification weakened the governing evaluation.

When no stable exists yet, stable-versus-candidate delta cannot be fabricated. The first candidate must instead satisfy the fixed absolute corpus/protected-capability requirements defined for first promotion; the non-authoritative baseline seed may be used only where the fixed policy explicitly permits comparison evidence.

Until numeric thresholds are established from baseline data, uncertainty resolves to `ABSTAIN`, not optimistic promotion.

## Ground truth

Ground truth comes from adjudicated defect evidence, reproducible behavior, accepted fixes, and other governed evidence. Reviewer agreement or majority vote is not sufficient by itself.

## Promotion transaction

Promotion must be atomic and auditable:

`candidate identity + stable_before identity (or none) + evaluation policy identity + evidence set + fresh evaluator result → decision → stable_after identity (or unchanged/none)`

Only authoritative `PROMOTE` may create or advance stable. Failed, rejected, stale, same-chat, or ambiguous evaluation leaves stable unchanged; before the first promotion that means stable remains unset.
