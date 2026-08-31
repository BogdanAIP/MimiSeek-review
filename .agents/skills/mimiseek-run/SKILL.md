# Skill: mimiseek-run

## User invocation

Primary natural-language trigger:

> Запусти Мимисик.

Equivalent explicit invocations such as `mimiseek-run` are acceptable.

## Purpose

Run the **development half** of the MimiSeek reviewer-improvement loop in the current ChatGPT chat.

This skill does not promote a candidate and does not update consumer repositories. Its terminal responsibility is to leave durable repository state that a completely new chat can independently evaluate through `mimiseek-update`.

## Bootstrap

Before mutations:

1. Resolve live `BogdanAIP/MimiSeek-review` state from GitHub.
2. Read `AGENTS.md`, `docs/PRODUCT.md`, `docs/CURRENT_STATE.md`, `docs/REVIEWER_LIFECYCLE.md`, `docs/EVALUATION_POLICY.md`, `docs/INTEGRATION_CONTRACT.md`, and `docs/CHATGPT_ENTRYPOINT.md`.
3. Resolve current stable reviewer identity, registered consumers, collection cursors, pending candidate state, and applicable immutable policy refs.
4. Never treat previous-chat prose as authority.

## Preconditions

- If an unresolved `PENDING_UPDATE` candidate already exists, do not create another competing candidate. Collecting additional evidence may be allowed only if the governing lifecycle says it cannot mutate the already-frozen evaluation package.
- If durable state is corrupt, ambiguous, or cannot be reconciled, stop fail-closed.

## Pipeline

### 1. COLLECT

Gather new review/outcome evidence from registered consumer repositories.

Collection must be idempotent and provenance-bound. Import only evidence whose repository/PR/BASE/HEAD/reviewer identities can be resolved.

Do not infer a reviewer MISS merely from absence of a finding.

### 2. NORMALIZE

Normalize new review runs, findings, dispositions, discovery sources, fix heads, verified heads, and evidence links into the canonical MimiSeek data model.

Preserve historical exact-head truth; later heads do not rewrite earlier review results.

### 3. DERIVE LEARNING EVENTS

Derive only evidence-supported events, including when applicable:

- `OUR_HIT`
- `OUR_MISS_CODEX_HIT`
- `OUR_HIT_CODEX_MISS`
- `OUR_FALSE_POSITIVE`
- `BOTH_MISS_LATER_CONFIRMED`

Respect exact-head, timing, visibility, and adjudication constraints. Use `UNKNOWN` when a miss or comparison cannot be proven.

### 4. LEARN

Analyze new evidence together with the historical learning/regression corpus and protected capabilities.

A useful improvement must be transferable beyond one SHA/file/line. Record:

- supporting learning events;
- generalized mechanic;
- expected capability gain;
- protected capabilities potentially affected;
- false-positive/overfitting risks;
- why the change is preferable to leaving stable unchanged.

If no defensible improvement is supported, persist collected evidence and finish `NO_CHANGE`.

### 5. BUILD CANDIDATE

Create an immutable candidate reviewer version separate from current stable.

The candidate/learner may not modify the evaluation policy used to judge this candidate.

### 6. REGRESSION

Run the candidate and stable under the fixed evaluation protocol on the required evidence set.

At minimum cover:

- target BUGGY detection;
- old target finding absent on FIXED;
- protected capabilities;
- false-positive/rejected-finding behavior;
- identity/provenance completeness.

A mandatory regression failure marks the candidate `REJECTED` and ends the run. Do not create `PENDING_UPDATE` for a candidate that cannot pass the mechanical/regression prerequisites.

### 7. FREEZE UPDATE PACKAGE

If the candidate is eligible for independent semantic evaluation, persist a frozen `PENDING_UPDATE` package containing at least:

- stable immutable identity;
- candidate immutable identity;
- governing evaluation-policy ref;
- exact evaluation dataset/result identities;
- candidate diff/change rationale;
- regression/protected-capability evidence;
- any required fresh real-world/shadow evidence already available;
- package nonce/run identity as defined by implementation.

The package must be sufficient for a new chat to independently reconstruct the evaluation without relying on this chat.

### 8. FINALIZE

Update canonical current/evidence owners when their truth changes.

Return one of:

- `NO_CHANGE` — evidence collected but no defensible candidate;
- `REJECTED_PRE_UPDATE` — candidate failed mandatory pre-update evaluation;
- `PENDING_UPDATE` — frozen candidate package is ready for a new chat.

When returning `PENDING_UPDATE`, tell the user only that they can open a new ChatGPT chat and invoke **«Обнови Мимисик»**. They must not need to copy a technical evaluation prompt manually.

## Fail-closed rules

Never:

- promote stable;
- update CAP/UV/other consumer reviewer pins;
- evaluate promotion in the same chat;
- create a second competing pending candidate;
- weaken the candidate's governing evaluation policy;
- fabricate missing review/adjudication evidence.

An interrupted run must leave the previous stable usable and durable state resumable.