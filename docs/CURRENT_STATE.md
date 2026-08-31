# Current State

Last synchronized: 2026-08-31

## Repository state

- Project: MimiSeek Review
- Repository: `BogdanAIP/MimiSeek-review`
- Stable branch: `main`
- Development status: bootstrap
- Active PR: #1 — `Bootstrap continuous development foundation`
- Active branch: `bootstrap/continuous-development-docs`
- Stable reviewer version: **not established yet**
- Candidate reviewer version: none
- Registered initial consumers: `BogdanAIP/chat-agent-platform`, `BogdanAIP/uv-studio`
- User-facing ChatGPT skills: `mimiseek-run` and `mimiseek-update`
- Active implementation focus: finalize Stage 0 product boundary, two-chat evolution workflow, and safe consumer rollout contract

For exact active HEAD, resolve the live PR/branch ref from GitHub. Do not duplicate a self-referential current commit SHA here during active development.

## Established product boundary

- MimiSeek Review is standalone and multi-project, not owned by CAP or UV.
- Its job is to collect accepted reviewer outcomes, learn, build candidate reviewers, independently evaluate them, publish a better stable reviewer, and distribute stable-version updates when each consumer is safe to change.
- MimiSeek does **not** own the ordinary code-review/fix loop inside consumer repositories.
- Consumer repositories are evidence producers + stable-reviewer consumers.
- Stable and candidate reviewer roles are separate.
- Learner/candidate cannot change their own evaluation policy.
- Routine reviewer evolution uses two user-visible chats/skills:
  1. `Запусти Мимисик` / `mimiseek-run` — collect, learn, build candidate, regression, freeze `PENDING_UPDATE`;
  2. in a new chat, `Обнови Мимисик` / `mimiseek-update` — independently evaluate candidate, promote only if proven, then safety-check each consumer before rollout.
- Global MimiSeek promotion and consumer installation are separate transactions.
- A consumer may remain pinned to an older stable while its live project state makes an update unsafe.
- Already-running agent/reviewer/procedure runs remain bound to the reviewer version with which they started.

## Historical data role

The audited reviewer-statistics workbook created before this repository is the bootstrap learning/regression source. It includes historical CAP/UV review outcomes and 84 BUGGY→FIXED cases.

Stage 1 will import those data into canonical machine-readable text datasets under `data/`. Excel remains a human report/import artifact, not the only source of truth.

## What is intentionally not done yet

- Historical workbook data are not yet imported into canonical MimiSeek datasets.
- No CAP/UV `code-review` skill has yet been selected or derived as first MimiSeek stable.
- No collector, outcome store, learner, regression runner, promotion registry, or consumer safe-window detector/distributor implementation exists yet.
- The two ChatGPT skills currently define the required contracts; later roadmap stages implement the machinery behind them.
- Consumer repositories do not yet expose the final machine-readable safe-update signal/contract; until that exists, inability to prove a safe update window must defer distribution.

The existing CAP and UV reviewer policies differ. The first stable baseline must be derived explicitly rather than accidentally copying one consumer's current policy.

## Next canonical action

Complete review/acceptance of PR #1. Then Stage 1 must do two bootstrap jobs together:

1. import/reconcile the existing historical reviewer workbook into canonical MimiSeek data, preserving the 84 BUGGY→FIXED cases and provenance;
2. inventory accepted CAP/UV review policies at exact refs and derive the first reusable stable MimiSeek reviewer while retaining project-specific overlays.

Consumer integration must also define how CAP/UV expose a trustworthy live `SAFE_TO_UPDATE` / defer state so MimiSeek never changes reviewer policy while an agent, frozen exact-head gate, or protected project stage is in progress.

## Open risks

- A naive common baseline could silently lose CAP- or UV-specific obligations.
- Historical outcomes are selection-biased; they are learning/regression evidence, not a neutral leaderboard.
- Consumer safe-window detection must not infer safety from silence or absence of visible GitHub activity.
- Distribution must remain versioned, compatible, and non-disruptive to already-running agent/review/procedure runs.