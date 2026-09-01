# ChatGPT Project Instructions — MimiSeek Review

These instructions are a fallback routing/bootstrap layer for a ChatGPT surface where the native MimiSeek Review skills are not available. When native skills are available, prefer their installed identities and keep this file only as repository documentation.

## Repository authority

The canonical repository is `BogdanAIP/MimiSeek-review`.

Before acting on any MimiSeek Review command, resolve the live repository state from GitHub and read the repository-governed instructions. Chat memory is context only; Git/GitHub state and canonical repository documents are authority.

## Command routing

### Run / continue

Native identity: `mimiseek-review-run`.

Canonical repository workflow: `.agents/skills/mimiseek-run/SKILL.md`.

When the user invokes the run role:

1. Open `BogdanAIP/MimiSeek-review`.
2. Resolve the live governing branch/state according to `AGENTS.md` and `docs/CURRENT_STATE.md`.
3. Read `.agents/skills/mimiseek-run/SKILL.md` from the authoritative ref.
4. Execute that repository-driven workflow exactly as governed there.
5. During bootstrap, continue the current canonical repository-development action; do not fabricate later operational learning stages.
6. Do not substitute the independent update role in the same chat.

### Independent update

Native identity: `mimiseek-review-update`.

Canonical repository workflow: `.agents/skills/mimiseek-update/SKILL.md`.

When the user invokes the update role:

1. This must be a new independent ChatGPT conversation, separate from the run/development chat and from any earlier consequence-bearing MimiSeek update decision. This also applies when the only work is deferred-distribution reconciliation.
2. Open `BogdanAIP/MimiSeek-review`.
3. Resolve the live governing branch/state according to `AGENTS.md` and `docs/CURRENT_STATE.md`.
4. Read `.agents/skills/mimiseek-update/SKILL.md` from the authoritative ref.
5. Execute that workflow exactly as governed there.
6. Promotion and per-consumer rollout remain fail-closed when independence, compatibility, identity, or a safe project update window cannot be proven.

## Independence rule

Never treat two messages in the same conversation as the required two-chat workflow. Every real `mimiseek-review-update` invocation uses a new independent ChatGPT conversation; repository state is the durable handoff.

## Consumer safety rule

A newly promoted MimiSeek stable reviewer is not automatically installed into CAP, UV, or another consumer. The update role must independently prove that the consumer's current live project state permits the reviewer change. Active agents/runs, frozen exact-head acceptance gates, protected stages, or unresolved compatibility require deferral.

Already-running work remains bound to the reviewer version with which it started. A later safe reviewer update applies only to future runs.
