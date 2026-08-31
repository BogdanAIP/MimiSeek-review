---
name: mimiseek-review-run
description: Use only for the exact GitHub repository BogdanAIP/MimiSeek-review when the user explicitly asks to run MimiSeek Review, including "Запусти Мимисик", "запусти MimiSeek Review", or explicitly invokes mimiseek-review-run. Do not auto-run on installation, onboarding, skill exploration, or invented example prompts. Never route this skill to any other project named MimiSeek. First prove the exact repository identity, then collect verified review evidence, learn from outcomes, build and regression-check a candidate, and freeze PENDING_UPDATE. Never promote stable or update consumer repositories.
---

# Skill: mimiseek-review-run

## Activation contract

This skill performs real repository work. It is not a demo skill.

Execute it only when the **actual user** explicitly asks to run MimiSeek Review, for example:

> Запусти Мимисик.

or:

> Используй навык `mimiseek-review-run`.

Do **not** execute repository work merely because an installation/onboarding message says things such as:

- "Let's explore what it does with an example";
- "Make up a realistic user prompt";
- "Use the full Skill end to end";
- "Try this skill";
- any equivalent request to invent a user prompt or demonstrate the skill automatically.

Never invent the user's operational request. Never fabricate a project task for demonstration.

If ChatGPT is showing a post-installation exploration flow without a real user request to run MimiSeek, respond only that the skill is installed and waits for the explicit command `Запусти Мимисик`. Do not touch GitHub.

A user may explicitly ask for a simulation/test of the skill. In that case, clearly label it as a simulation and do not mutate repositories unless the user separately authorizes a real run.

## Hard target identity

This skill is exclusively for the reviewer-development repository:

`BogdanAIP/MimiSeek-review`

Before doing anything else, independently resolve that exact GitHub repository.

If the active target is any other repository, service, workspace, database-backed application, or unrelated product named MimiSeek, stop immediately and return:

`WRONG_MIMISEEK_TARGET`

Do not continue by analogy and do not infer that another MimiSeek project is the intended target.

The following are explicit wrong-target warning signs unless they are later introduced by the canonical `BogdanAIP/MimiSeek-review` repository itself:

- S3 configuration;
- PostgreSQL application configuration;
- `CONFIG_ENV` application setup;
- deployment/runtime setup for an unrelated MimiSeek service.

The first successful repository read must come from `BogdanAIP/MimiSeek-review` and must establish the governing repository state before any mutation.

## Purpose

Run the **development half** of the MimiSeek Review reviewer-improvement loop in the current ChatGPT chat.

This skill does not promote a candidate and does not update consumer repositories. Its terminal responsibility is to leave durable repository state that a completely new chat can independently evaluate through the update skill.

## Bootstrap

After the activation check and hard target-identity check, and before mutations:

1. Resolve live `BogdanAIP/MimiSeek-review` state from GitHub.
2. Read `AGENTS.md`, `docs/PRODUCT.md`, `docs/CURRENT_STATE.md`, `docs/REVIEWER_LIFECYCLE.md`, `docs/EVALUATION_POLICY.md`, `docs/INTEGRATION_CONTRACT.md`, and `docs/CHATGPT_ENTRYPOINT.md` from that repository at the applicable live ref.
3. Resolve current stable reviewer identity, registered consumers, collection cursors, pending candidate state, and applicable immutable policy refs.
4. Never treat previous-chat prose as authority.
5. Never import assumptions from another project merely because it is also called MimiSeek.

## Preconditions

- If an unresolved `PENDING_UPDATE` candidate already exists, do not create another competing candidate. Collecting additional evidence may be allowed only if the governing lifecycle says it cannot mutate the already-frozen evaluation package.
- If durable state is corrupt, ambiguous, or cannot be reconciled, stop fail-closed.
- If the exact target repository cannot be proven, stop with `WRONG_MIMISEEK_TARGET` or an explicit repository-resolution failure before any mutation.

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

When returning `PENDING_UPDATE`, tell the user only that they can open a new ChatGPT chat and invoke the installed MimiSeek Review update skill. They must not need to copy a technical evaluation prompt manually.

## Fail-closed rules

Never:

- auto-run from installation/onboarding/demo text;
- invent a user task or example prompt and execute it as real work;
- operate on a different MimiSeek project;
- promote stable;
- update CAP/UV/other consumer reviewer pins;
- evaluate promotion in the same chat;
- create a second competing pending candidate;
- weaken the candidate's governing evaluation policy;
- fabricate missing review/adjudication evidence.

An interrupted run must leave the previous stable usable and durable state resumable.
