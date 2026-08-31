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
- Primary ChatGPT entry point contract: `.agents/skills/mimiseek-evolve/SKILL.md`
- Active implementation focus: finalize Stage 0 product boundary and continuous-development/evolution contracts

For exact active HEAD, resolve the live PR/branch ref from GitHub. Do not duplicate a self-referential current commit SHA here during active development.

## Established product boundary

- MimiSeek Review is standalone and multi-project, not owned by CAP or UV.
- Its job is to collect accepted reviewer outcomes, learn, build candidate reviewers, evaluate them independently, publish a better stable reviewer, and distribute stable-version updates.
- MimiSeek does **not** own the ordinary code-review/fix loop inside consumer repositories.
- Consumer repositories are evidence producers + stable-reviewer consumers.
- Stable and candidate reviewer roles are separate.
- Promotion requires separately governed evaluation using a new isolated ChatGPT context.
- Learner/candidate cannot change their own evaluation policy.
- Promoted reviewer updates are distributed through auditable consumer PRs rather than silent direct writes to consumer stable branches.
- The user-facing target is one ChatGPT skill invocation: `mimiseek-evolve`.

## Historical data role

The audited reviewer-statistics workbook created before this repository is the bootstrap learning/regression source. It includes historical CAP/UV review outcomes and 84 BUGGY→FIXED cases.

Stage 1 will import those data into canonical machine-readable text datasets under `data/`. Excel remains a human report/import artifact, not the only source of truth.

## What is intentionally not done yet

- Historical workbook data are not yet imported into canonical MimiSeek datasets.
- No CAP/UV `code-review` skill has yet been selected or derived as first MimiSeek stable.
- No collector, outcome store, learner, regression runner, fresh-context executor, promotion registry, or distributor implementation exists yet.
- The `mimiseek-evolve` skill currently defines the required end-to-end contract; later roadmap stages implement every phase behind it.

The existing CAP and UV reviewer policies differ. The first stable baseline must be derived explicitly rather than accidentally copying one consumer's current policy.

## Next canonical action

Complete review/acceptance of PR #1. Then Stage 1 must do two bootstrap jobs together:

1. import/reconcile the existing historical reviewer workbook into canonical MimiSeek data, preserving the 84 BUGGY→FIXED cases and provenance;
2. inventory accepted CAP/UV review policies at exact refs and derive the first reusable stable MimiSeek reviewer while retaining project-specific overlays.

## Open risks

- A naive common baseline could silently lose CAP- or UV-specific obligations.
- Historical outcomes are selection-biased; they are learning/regression evidence, not a neutral leaderboard.
- Automatic fresh evaluator execution requires a proven adapter capable of creating a genuinely new ChatGPT context; same-chat substitution is forbidden.
- Distribution must remain versioned and compatible across future consumers.
