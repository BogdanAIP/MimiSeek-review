# Evaluation Policy

Status: bootstrap policy; detailed numeric thresholds are intentionally deferred until real baseline data exist.

## Purpose

Define who may decide that a reviewer candidate is good enough to become stable and what evidence that decision must use.

## Separation rule

A candidate reviewer and the learner that produced it may not authoritatively change the evaluation policy governing that candidate's promotion.

Changes to this policy are separate governed changes and cannot retroactively weaken an already-started candidate evaluation.

## Evaluator

Semantic promotion evaluation is intended to use a fresh ordinary ChatGPT context operating independently and read-only against immutable candidate/stable identities and evidence.

The evaluator returns exactly one terminal recommendation:

- `PROMOTE`
- `REJECT`
- `ABSTAIN`

`ABSTAIN` means evidence is insufficient or ambiguous; stable remains unchanged.

## Evidence classes

Candidate evaluation may use:

1. known BUGGY cases with confirmed target defects;
2. corresponding FIXED cases to detect memorized/over-broad findings;
3. protected-capability regression cases;
4. rejected-finding/false-positive cases;
5. suitable shadow runs on fresh real PR heads;
6. later external holdout benchmarks.

Historical corpus is not by itself a neutral external benchmark.

## Minimum semantic requirements for promotion

A candidate must demonstrate all of the following under the finalized quantitative gate:

- no critical protected-capability regression;
- target improvements are supported by confirmed defects, not merely more emitted findings;
- old target findings do not persist incorrectly on corresponding FIXED cases;
- false-positive behavior does not deteriorate beyond allowed policy;
- review identity/evidence is complete and current;
- any required real-world shadow evidence is satisfied;
- no candidate-controlled modification weakened the governing evaluation.

Until numeric thresholds are established from baseline data, uncertainty resolves to `ABSTAIN`, not automatic promotion.

## Ground truth

Ground truth comes from adjudicated defect evidence, reproducible behavior, accepted fixes, and other governed evidence. Reviewer agreement or majority vote is not sufficient by itself.

## Promotion transaction

Future implementation must make promotion atomic and auditable:

`candidate identity + evaluation policy identity + evidence set → decision → new stable identity`

Failed, rejected, stale, or ambiguous evaluation must leave the current stable unchanged.
