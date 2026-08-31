---
name: mimiseek-review-update
description: Run the independent MimiSeek Review update workflow only when the user explicitly asks to update MimiSeek Review, including "Обнови Мимисик" or an explicit invocation of mimiseek-review-update. The exact target is BogdanAIP/MimiSeek-review. Reconstruct live repository state, independently evaluate any eligible reviewer candidate under current repository governance, and apply consumer updates only where the live project state proves a safe update window.
---

# MimiSeek Review — Update

## Purpose

This is the independent ChatGPT entry point for **evaluating and applying MimiSeek Review updates**.

It is normally invoked in a new chat, separate from the chat that created or developed the candidate being evaluated.

The exact repository is:

`BogdanAIP/MimiSeek-review`

No other project, service, workspace, or repository called MimiSeek is in scope.

## Source of truth

Chat history is not authoritative project state.

On every invocation, independently reconstruct the live MimiSeek Review state from GitHub and read the governing repository-owned instructions before deciding whether any update is allowed.

Start with:

1. `AGENTS.md`
2. `docs/PRODUCT.md`
3. `docs/CURRENT_STATE.md`
4. `docs/ROADMAP.md`
5. relevant parts of `docs/ARCHITECTURE.md`
6. `docs/REVIEWER_LIFECYCLE.md`
7. `docs/EVALUATION_POLICY.md`
8. `docs/INTEGRATION_CONTRACT.md`
9. `docs/EVIDENCE_INDEX.md`
10. applicable records under `docs/decisions/`

Then independently resolve the live PR/branch/HEAD, candidate/update package identities, stable identity, CI/evaluation evidence, and registered consumer state required by those documents.

If repository truth conflicts with this installed copy of the skill on an implementation detail, follow the current repository governance. This installed skill defines the independent-update role and safety boundary; the repository defines the evolving implementation.

## What "Обнови Мимисик" means

Continue the **current governed independent-update workflow** from durable repository state.

Depending on current state this may mean:

- independently evaluating an eligible pending reviewer candidate;
- applying a valid promotion transaction when the evaluation policy authorizes it;
- reconciling previously deferred consumer distributions for an already-promoted stable version;
- doing nothing when no eligible update or deferred distribution exists.

Do not invent a candidate, update package, evaluation result, or safe rollout window.

## Independence boundary

When candidate promotion requires a fresh independent evaluator, this skill must not be used in the same conversation that created, modified, or advocated for that candidate.

If independence cannot be established under current repository policy, fail closed and leave stable unchanged.

The learner/candidate cannot redefine the evaluation policy that judges that same candidate.

## Candidate evaluation

When an eligible candidate exists, independently evaluate it under the exact governing `EVALUATION_POLICY.md` and repository-owned evidence.

Do not treat reviewer agreement, number of findings, or learner claims as ground truth by themselves.

Only the repository-governed terminal outcomes may control promotion, currently including:

- `PROMOTE`
- `REJECT`
- `ABSTAIN`

Insufficient, stale, mismatched, or ambiguous evidence must not produce promotion.

## Promotion and consumer rollout are separate

A reviewer may become MimiSeek Review stable without every consumer updating immediately.

After any valid promotion, evaluate each registered consumer independently under its own live governance before changing its reviewer binding.

An update is permitted only when the current repository/integration contract proves a safe update window.

Potential blockers include active agent/reviewer/procedure work, frozen exact-head acceptance or release gates, project stages that defer unrelated infrastructure changes, policy migrations, unresolved compatibility, or any other project-owned restriction.

Absence of visible activity is not proof of safety.

Already-running work remains bound to the reviewer version with which it started; an update may affect only future runs after the consumer update becomes effective.

## Execution contract

1. Reconstruct exact live MimiSeek Review state.
2. Determine whether there is an eligible pending candidate and/or deferred consumer distribution.
3. Verify exact identities, governing policy, evidence and independence prerequisites.
4. Evaluate candidate promotion only when eligible.
5. Apply the promotion transaction only when explicitly authorized by the governing result.
6. Re-resolve each consumer's live state before any rollout change.
7. Update only consumers proven safe now; defer all others without changing their current binding.
8. Record immutable promotion/distribution evidence and update canonical owner documents whose truth changed.
9. Leave all repository state resumable for a completely fresh next chat.

## Activation behavior

Execute real repository work only when the user actually asks to update MimiSeek Review.

Installing, inspecting, explaining, or discussing the skill is not by itself authorization to mutate repositories.

Never invent a fake candidate or fake consumer state to demonstrate the skill. A requested simulation stays read-only unless the user separately requests a real update attempt.

## Fail closed

Never:

- operate on a different MimiSeek project;
- promote from incomplete, stale, mismatched, or non-independent evidence;
- weaken the governing evaluation policy to allow a candidate through;
- modify a consumer whose safe update window is not proven;
- switch the reviewer version of already-running work;
- bypass consumer-specific governance or compatibility requirements.

A failed or interrupted update must leave the previous stable usable and every consumer either unchanged or durably reconciled to a proven-safe transition.

## Completion

Finish with a concise state-based result. State:

- exact MimiSeek repository/PR/HEAD identity relevant to the update;
- candidate/update-package identity if one existed;
- evaluation result or reason no evaluation was performed;
- stable before/after;
- per-consumer rollout result or defer reason;
- resulting repository state and next canonical action.
