---
name: mimiseek-review-run
description: Run MimiSeek Review only when the user explicitly asks to start or continue the MimiSeek Review project, including "Запусти Мимисик" or an explicit invocation of mimiseek-review-run. The exact target is BogdanAIP/MimiSeek-review. Reconstruct live repository state and continue the next canonical work from the repository; do not invent demo tasks or operate on any other project named MimiSeek.
---

# MimiSeek Review — Run

## Purpose

This is the primary ChatGPT entry point for **continuing and operating MimiSeek Review**.

The user should be able to open a chat, invoke this skill, and have ChatGPT recover the project from durable repository state and continue the correct work without requiring a handoff from a previous chat.

The exact repository is:

`BogdanAIP/MimiSeek-review`

No other project, service, workspace, or repository called MimiSeek is in scope.

## Source of truth

Chat history is never authoritative project state.

On every real invocation, independently resolve the live GitHub repository and read the applicable repository-owned instructions before deciding what to do.

Start with:

1. `AGENTS.md`
2. `docs/PRODUCT.md`
3. `docs/CURRENT_STATE.md`
4. `docs/ROADMAP.md`
5. relevant parts of `docs/ARCHITECTURE.md`
6. `docs/DEVELOPMENT_PROTOCOL.md`
7. `docs/REVIEWER_LIFECYCLE.md`
8. `docs/EVALUATION_POLICY.md`
9. `docs/INTEGRATION_CONTRACT.md`
10. `docs/EVIDENCE_INDEX.md`
11. applicable records under `docs/decisions/`

Then independently resolve the live branch/PR/HEAD, CI, and other GitHub evidence required by those documents.

If repository truth conflicts with this installed copy of the skill on an implementation detail, follow the current repository governance. This installed skill defines the entry-point role and safety boundary; the repository defines the evolving implementation.

## What "Запусти Мимисик" means

Continue MimiSeek Review from its **actual current state**.

Do not assume the system is already fully implemented.

- During bootstrap/development stages, perform the next canonical repository-development work needed to make MimiSeek Review operational.
- Once the reviewer-learning pipeline exists, run the current governed learning/evolution cycle.
- If the repository says another prerequisite must be completed first, do that prerequisite instead of pretending the later pipeline already exists.

The product goal remains constant: build and continuously improve one reusable reviewer from verified evidence, independently evaluate candidate versions, and distribute promoted stable versions safely to registered consumer projects.

## Execution contract

After reconstructing live state:

1. Identify the single next canonical action from repository-owned state and roadmap.
2. Verify its prerequisites and governing policy at exact refs.
3. Execute the work autonomously with available tools.
4. Use branches/PRs and repository acceptance rules; do not bypass project governance merely to make progress faster.
5. Run the required tests/checks/evidence collection for the work performed.
6. Re-read live state after consequence-bearing changes when needed to detect drift.
7. Update only the canonical owner documents whose truth changed.
8. Leave the repository in a resumable, internally coherent state for a completely fresh next chat.

Do not ask the user to reconstruct prior technical context that can be recovered from GitHub.

## Reviewer-evolution boundary

When the operational evolution pipeline is available, the run-side responsibility is the **development/learning half** only. Under the repository's current lifecycle this may include:

- collecting new adjudicated review evidence from registered consumers;
- normalizing evidence and deriving supported learning events;
- learning transferable reviewer mechanics from hits, misses, and false positives;
- creating an immutable candidate separate from stable;
- regression/protected-capability evaluation;
- freezing the governed independent-update package/state.

This skill must **not** independently declare its own candidate the new stable reviewer when the governing lifecycle requires a fresh independent update chat.

It also must not install a new reviewer into CAP, UV, or another consumer merely because a candidate exists.

## Consumer-project boundary

CAP, UV, and future consumers own their ordinary development/review/fix workflows and project-specific governance.

MimiSeek Review may read their governed evidence and later distribute a promoted reviewer according to the integration contract, but this run skill is not a replacement orchestrator for their normal PR development cycles.

## Activation behavior

Execute real repository work only when the user actually asks to run/start/continue MimiSeek Review.

Installing, inspecting, explaining, or discussing the skill is not by itself authorization to mutate repositories.

Never invent a fake user task or fake project state to demonstrate the skill. If the user explicitly asks for a simulation, keep the simulation read-only unless they separately request a real run.

## Fail closed

Stop rather than guess when any consequence-bearing transition depends on unresolved repository identity, stale/mismatched exact refs, missing governing policy, corrupt durable state, or ambiguous authority.

Never:

- operate on a different MimiSeek project;
- fabricate review evidence or finding dispositions;
- silently weaken `EVALUATION_POLICY.md` to make a candidate pass;
- overwrite project-specific consumer governance with generic reviewer rules;
- change an already-running consumer agent/reviewer/procedure to a different reviewer version mid-run;
- treat absence of visible activity as proof that a consumer is safe to update.

## Completion

Finish with a concise state-based result, not a narrative diary. State:

- what canonical action was performed;
- exact repository/PR/HEAD identity relevant to the result;
- tests/evidence outcome;
- resulting MimiSeek state;
- the next canonical action, if work remains;
- whether a fresh new chat should invoke the independent MimiSeek update skill.
