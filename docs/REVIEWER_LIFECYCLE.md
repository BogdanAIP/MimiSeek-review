# Reviewer Lifecycle

## States

### Stable

The reviewer version approved for real consumer use. Stable identity must be immutable and resolvable.

### Candidate

A proposed next reviewer version. It may be evaluated and shadow-run but is not authoritative for consumer acceptance merely because it exists.

### Rejected candidate

A candidate that failed evaluation. Its evidence remains useful for later learning; rejection does not rewrite history.

## Learning loop

Real project work naturally produces learning evidence:

- development finds defects before review;
- Codex may find defects MimiSeek missed;
- MimiSeek may find defects Codex missed;
- MimiSeek findings may be confirmed or rejected;
- later fixes create BUGGY→FIXED pairs;
- post-review defects expose misses.

The intended loop is:

```text
stable reviewer
    ↓
real PR outcomes
    ↓
learning events
    ↓
learner analysis
    ↓
candidate
    ↓
regression evaluation
    ↓
shadow/real evidence when required
    ↓
fresh independent evaluator
    ↓
PROMOTE / REJECT / ABSTAIN
```

## Learning event principles

Events must be derived from evidence, not reviewer popularity.

Examples:

- `OUR_HIT`: MimiSeek finding was confirmed.
- `OUR_MISS_CODEX_HIT`: MimiSeek did not report a defect on the relevant identity; Codex did; defect was later confirmed.
- `OUR_HIT_CODEX_MISS`: MimiSeek confirmed finding was not reported by a suitable Codex run on the same relevant identity.
- `OUR_FALSE_POSITIVE`: MimiSeek finding was rejected after falsification.
- `BOTH_MISS_LATER_CONFIRMED`: suitable runs missed a later-confirmed defect.

Exact comparison requirements must prevent different-head fixes from being mislabelled as reviewer misses.

## What the learner should learn

Prefer transferable mechanics, such as:

- enumerate every writer to a durable object;
- trace consequence-bearing operations through effect, observation, verification, durable receipt, crash, restart, and reconciliation;
- prove capability unreachability rather than trusting a policy statement;
- inspect callers/consumers when local correctness depends on cross-file semantics;
- require evidence that survives falsification before publishing a finding.

Do not encode exact SHA, file name, line number, or historical answer as the learned rule unless that identity is itself a generic protocol element.

## Protected capabilities

A demonstrated strength can be marked as protected evaluation coverage. A later candidate should not be promoted if it loses that capability beyond the governing evaluation tolerance.

## Promotion authority

The learner proposes. The evaluator judges under `EVALUATION_POLICY.md`. A candidate cannot promote itself.
