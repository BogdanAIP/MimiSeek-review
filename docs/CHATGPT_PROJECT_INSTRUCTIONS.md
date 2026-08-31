# ChatGPT Project Instructions — MimiSeek Review

Use these instructions in a dedicated ChatGPT Project named `MimiSeek Review` while Personal Skills are unavailable on the current ChatGPT plan/surface.

## Repository authority

The canonical repository is `BogdanAIP/MimiSeek-review`.

Before acting on any MimiSeek command, resolve the live repository state from GitHub and read the repository-governed instructions. Chat memory is context only; Git/GitHub state and canonical repository documents are authority.

## Command routing

When the user says **«Запусти Мимисик»** or explicitly invokes `mimiseek-run`:

1. Open `BogdanAIP/MimiSeek-review`.
2. Resolve the live governing branch/state according to `AGENTS.md` and `docs/CURRENT_STATE.md`.
3. Read `.agents/skills/mimiseek-run/SKILL.md` from the authoritative ref.
4. Execute that skill exactly as governed there.
5. Do not substitute `mimiseek-update` in the same chat.

When the user says **«Обнови Мимисик»** or explicitly invokes `mimiseek-update`:

1. This must be a new ChatGPT chat that did not create or modify the pending candidate.
2. Open `BogdanAIP/MimiSeek-review`.
3. Resolve the live governing branch/state according to `AGENTS.md` and `docs/CURRENT_STATE.md`.
4. Read `.agents/skills/mimiseek-update/SKILL.md` from the authoritative ref.
5. Execute that skill exactly as governed there.
6. Promotion and per-consumer rollout must remain fail-closed when independence, compatibility, or a safe project update window cannot be proven.

## Independence rule

Never treat two messages in the same chat as the required two-chat workflow. `mimiseek-run` and promotion evaluation through `mimiseek-update` require separate ChatGPT conversations.

## Consumer safety rule

A newly promoted MimiSeek stable reviewer is not automatically installed into CAP, UV, or another consumer. The update skill must independently prove that the consumer's current live project state permits the reviewer change. Active agents/runs, frozen exact-head acceptance gates, protected stages, or unresolved compatibility require deferral.

Already-running work remains bound to the reviewer version with which it started. A later safe reviewer update applies only to future runs.

## Future Personal Skills migration

If ChatGPT Personal Skills later become available on the user's plan/surface, the repository `SKILL.md` files remain canonical. Install/import them as ChatGPT Skills rather than duplicating or rewriting their workflow in product settings. Keep these Project Instructions only as a routing/bootstrap layer or retire them when equivalent native routing is proven.
