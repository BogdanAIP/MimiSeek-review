# Skill: mimiseek-evolve

## Purpose

Run the complete MimiSeek reviewer-improvement pipeline from ChatGPT with one user invocation.

This skill evolves and releases MimiSeek Review. It does **not** run the ordinary code-review/fix loop of CAP, UV, or other consumer repositories.

## Invocation

When the user explicitly asks to run `mimiseek-evolve` (or unmistakably asks to start the MimiSeek reviewer evolution skill), begin execution immediately. Do not ask the user to manually sequence internal phases.

## Bootstrap

Before mutations:

1. Resolve live `BogdanAIP/MimiSeek-review` default branch, active evolution state, current stable reviewer identity, and applicable governing documents.
2. Read `AGENTS.md`, `docs/PRODUCT.md`, `docs/CURRENT_STATE.md`, `docs/REVIEWER_LIFECYCLE.md`, `docs/EVALUATION_POLICY.md`, `docs/INTEGRATION_CONTRACT.md`, and `docs/CHATGPT_ENTRYPOINT.md`.
3. Resolve the registered consumers and exact previously collected cursors/identities from durable state.
4. Never rely on previous-chat memory as authority.

## Pipeline

Execute in order and persist every transition durably.

### 1. COLLECT

Gather new review/outcome evidence from every registered consumer repository.

Import only evidence with resolvable provenance and exact identity. Collection must be idempotent. Absence of a finding is not automatically a MISS.

### 2. NORMALIZE

Normalize new review runs, findings, dispositions, discovery sources, fix heads, and verification evidence into the canonical MimiSeek data model.

Do not overwrite historical truth when later heads supersede earlier results.

### 3. DERIVE LEARNING EVENTS

Derive only evidence-supported events such as `OUR_HIT`, `OUR_MISS_CODEX_HIT`, `OUR_HIT_CODEX_MISS`, `OUR_FALSE_POSITIVE`, and `BOTH_MISS_LATER_CONFIRMED`.

Respect exact-head, timing, visibility, and adjudication requirements. When a miss cannot be established, record UNKNOWN rather than inventing a comparison.

### 4. LEARN

Analyze new events together with historical corpus and protected capabilities.

If no defensible transferable improvement is supported, finish with `NO_CHANGE` after persisting the new evidence.

Any proposed change must describe:

- source learning events;
- generalized mechanic;
- expected capability gain;
- protected capabilities potentially affected;
- falsification/overfitting risk.

Do not encode a historical SHA/file/line answer as a generic rule.

### 5. BUILD CANDIDATE

Create an immutable candidate reviewer version separate from current stable.

The learner may not alter `docs/EVALUATION_POLICY.md` as part of the candidate it is asking to evaluate.

### 6. REGRESSION EVALUATION

Evaluate stable and candidate under the fixed evaluation protocol using appropriate BUGGY→FIXED cases and protected capabilities.

At minimum verify:

- target BUGGY detection;
- absence of the old target finding on FIXED;
- false-positive behavior;
- protected-capability regressions;
- completeness and identity of evaluation evidence.

A failed mandatory regression terminates the candidate as `REJECTED` without promotion.

### 7. FRESH EVALUATION

If regression gates permit promotion consideration, create a **new isolated ChatGPT context** through the configured fresh-context executor.

The fresh context must execute `.agents/skills/reviewer-evaluation/SKILL.md` against immutable stable/candidate/evaluation identities.

Do not expose learner advocacy beyond the evidence package required by evaluation policy. Do not substitute same-chat judgment if fresh-context execution is unavailable.

If fresh execution cannot be obtained, persist `EVALUATION_BLOCKED` and leave stable unchanged.

### 8. APPLY EVALUATOR RESULT

- `PROMOTE`: atomically register candidate as new stable with immutable promotion evidence.
- `REJECT`: keep current stable; preserve candidate and rejection evidence.
- `ABSTAIN`: keep current stable; preserve candidate for possible later re-evaluation when new evidence exists.

No other result may change stable.

### 9. DISTRIBUTE

Only after authoritative `PROMOTE`, create an auditable reviewer-version update PR for each registered compatible consumer repository.

Do not push directly to consumer stable branches. If compatibility cannot be proven for a consumer, leave it pinned and record that state.

### 10. FINALIZE

Persist:

- collection cursors/identities;
- normalized new evidence;
- learning events;
- candidate and evaluation identities;
- promotion result;
- distribution PRs/status;
- updated `CURRENT_STATE` / `EVIDENCE_INDEX` when their canonical truth changed.

Return a concise run summary including stable before/after, evidence collected, candidate identity if any, evaluator result, and consumer update PRs.

## Fail-closed rules

Never promote when:

- evaluation evidence is incomplete or mismatched;
- candidate modified its governing evaluation policy;
- a mandatory regression failed;
- fresh evaluator context is unavailable or cannot be proven fresh;
- evaluator returns anything other than authoritative `PROMOTE`;
- promotion identity is ambiguous.

A failed or interrupted run must leave the previous stable reviewer usable.
