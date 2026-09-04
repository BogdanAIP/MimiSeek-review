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
- When Track R review-job coordination is accepted but incomplete, implement only the next MimiSeek-side slice authorized by `CURRENT_STATE`, `ROADMAP`, `ARCHITECTURE`, and `INTEGRATION_CONTRACT`; do not pretend external CAP/session prerequisites are already accepted.
- Once the Track R runtime is actually implemented and its generic external execution capabilities are proven, it may coordinate explicitly requested independent review jobs under the exact immutable job contract.
- Once the reviewer-learning pipeline exists, run the current governed learning/evolution cycle.
- If the repository says another prerequisite must be completed first, do that prerequisite instead of pretending the later pipeline already exists.

The product goal remains constant: build and continuously improve one reusable reviewer from verified evidence, independently evaluate candidate versions, distribute promoted stable versions safely, and provide bounded project-neutral independent-review job coordination without taking over consumer development authority.

## Execution contract

After reconstructing live state:

1. Identify the single next canonical action from repository-owned state and roadmap, or one explicitly authorized parallel workstream when the roadmap permits it.
2. Verify its prerequisites and governing policy at exact refs.
3. Execute the work autonomously with available tools.
4. Use branches/PRs and repository acceptance rules; do not bypass project governance merely to make progress faster.
5. Run the required tests/checks/evidence collection for the work performed.
6. Re-read live state after consequence-bearing changes when needed to detect drift.
7. Update only the canonical owner documents whose truth changed.
8. Leave the repository in a resumable, internally coherent state for a completely fresh next chat.

Do not ask the user to reconstruct prior technical context that can be recovered from GitHub.

## Review-job coordination boundary

When Track R is implemented, this run-side system may coordinate an **explicitly requested** independent review job, but only within the accepted narrow boundary.

MimiSeek may:

- freeze the exact repository/PR/BASE/HEAD/`review_policy_ref` identity;
- create one immutable `REVIEW_JOB_V1` identity;
- request one fresh qualified reviewer through a separately accepted generic session/execution substrate;
- accept only a correlated exact-job result;
- re-resolve live source identity after result capture and classify moved source state as stale;
- persist the exact result durably in MimiSeek-owned GitHub state without moving the reviewed consumer HEAD;
- request one generic return/wake delivery to the originating conversation through an opaque/private route contract.

MimiSeek must not:

- decide that a consumer PR is ready for review without a governed explicit request;
- adjudicate project-specific findings on behalf of the consumer;
- edit consumer code as a consequence of the review job merely because it coordinates the job;
- decide whether a changed consumer HEAD needs re-review;
- merge a consumer PR because a reviewer returned `PASS`;
- turn a review-job `PASS` into MimiSeek reviewer-promotion or distribution authority;
- publish raw/private ChatGPT/browser/session capabilities into GitHub;
- require CAP or another generic session substrate to know UV/MimiSeek/CAP project semantics, PR semantics, or `PASS`/`FINDINGS` semantics.

Until `CURRENT_STATE.md` says the runtime and exact external prerequisites are accepted, treat this section as an implementation boundary, not as proof that the operational path already exists.

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

A Track R review-job result is not automatically an adjudicated learning event. It enters the reviewer-evolution pipeline only through the governed evidence/outcome contract.

## Consumer-project boundary

CAP, UV, and future consumers own their ordinary development/review/fix workflows and project-specific governance.

MimiSeek Review may read their governed evidence, later distribute a promoted reviewer according to the integration contract, and—when Track R is implemented—coordinate an explicitly requested independent review job. This run skill is still **not** a replacement owner for their normal PR development/fix/merge cycles.

The consumer remains authoritative for review readiness, project-local policy, finding disposition, remediation, re-review decisions, terminal acceptance, and merge consequences.

## Activation behavior

Execute real repository work only when the user actually asks to run/start/continue MimiSeek Review.

Installing, inspecting, explaining, or discussing the skill is not by itself authorization to mutate repositories.

A consumer review job must likewise have a governed explicit request/trigger; the existence of an open PR is not by itself authorization for MimiSeek to launch a reviewer.

Never invent a fake user task or fake project state to demonstrate the skill. If the user explicitly asks for a simulation, keep the simulation read-only unless they separately request a real run.

## Fail closed

Stop rather than guess when any consequence-bearing transition depends on unresolved repository identity, stale/mismatched exact refs, missing governing policy, corrupt durable state, ambiguous authority, an unproven external capability version, or an ambiguous review-job launch/result/return boundary.

Never:

- operate on a different MimiSeek project;
- fabricate review evidence or finding dispositions;
- silently weaken `EVALUATION_POLICY.md` to make a candidate pass;
- overwrite project-specific consumer governance with generic reviewer rules;
- change an already-running consumer agent/reviewer/procedure to a different reviewer version mid-run;
- treat absence of visible activity as proof that a consumer is safe to update;
- retry an ambiguous reviewer launch or wake blindly;
- treat a stale/mismatched review-job result as current;
- expose a usable private session capability in public repository state;
- smuggle project-specific routing/review semantics into the generic session transport.

## Completion

Finish with a concise state-based result, not a narrative diary. State:

- what canonical action was performed;
- exact repository/PR/HEAD identity relevant to the result;
- tests/evidence outcome;
- resulting MimiSeek state;
- the next canonical action, if work remains;
- whether a fresh new chat should invoke the independent MimiSeek update skill.
