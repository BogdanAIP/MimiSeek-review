# Current State

Last synchronized: 2026-09-02

## Repository state

- Project: MimiSeek Review
- Repository: `BogdanAIP/MimiSeek-review`
- Stable branch: `main`
- Development status: Stage 1 in progress — bootstrap data import + continuous evidence-intake foundation
- Stage 0 implementation foundation: accepted and merged
- Stable reviewer version: **not established yet**
- Bootstrap baseline seed: none
- Candidate reviewer version: none
- Registered initial consumers/evidence producers: `BogdanAIP/chat-agent-platform`, `BogdanAIP/uv-studio`
- Consumer MimiSeek installation: none yet; first installation is governed by Stage 8 safe distribution
- Native ChatGPT skill identities: `mimiseek-review-run` and `mimiseek-review-update`

Exact accepted-stage review/merge identities and chronology belong only in `docs/EVIDENCE_INDEX.md`. This file owns current position and next action.

## Stage 1 implementation reality

The Stage 1 implementation now has a proposed canonical bootstrap projection and an early evidence-intake foundation:

- the pinned historical workbook was recovered and authenticated against `data/bootstrap-source.json`;
- `data/review-runs.jsonl`, `data/findings.jsonl`, and `data/regression-cases.jsonl` contain normalized authenticated bootstrap projections, not column-lossless workbook clones;
- every normalized tuple retains an exact workbook `source_row`; omitted `PR title`/`Notes` fields are explicitly classified by schema, and material source-commentary assertions must be reconciled into governed provenance before baseline derivation rather than silently promoted to truth;
- the bootstrap-v1 datasets are exact anchored sets of 92 review runs, 139 findings, and 84 regression cases; they are not operational append targets;
- the import reconciles those records internally, while complete commit-level BUGGY/FIXED/VERIFIED provenance reconciliation remains unfinished;
- `tools/collect_github_evidence.py` provides deterministic read-only GitHub evidence polling for registered consumers;
- `.github/workflows/collect-review-evidence.yml` schedules hourly collection once the dedicated read-only GitHub App credentials are configured and the required server-side canonical-ref boundary remains active;
- source snapshots are intended to be written only to `evidence/github-intake`, which is **non-authoritative intake evidence** and is not the normalized outcome store;
- the intake backfill deliberately overlaps the bootstrap workbook so later normalization can deduplicate by immutable source identity rather than rely on an assumed perfect cutoff;
- `.github/workflows/ci.yml` provides repository unit-test CI plus a live canonical-ref boundary check.

These changes do not create a baseline seed, candidate, stable reviewer, consumer installation, learning events, or promotion authority.

The full Stage 3 collector/outcome-store stage is **not** claimed complete. The early collector exists only to stop new evidence from being lost while Stage 1 and Stage 2 are implemented.

## Canonical ref boundary

The live repository now has active ruleset `mimiseek-canonical-main` (GitHub ruleset id `22076488`) targeting the default branch. Live GitHub reports:

- enforcement `active`;
- include `~DEFAULT_BRANCH`, exclude none;
- rules `pull_request`, `deletion`, and `non_fast_forward`;
- required approving reviews `0`;
- bypass actors empty and `current_user_can_bypass=never`;
- `main` reports `protected=true`.

This is the server-enforced boundary required because the intake workflow's MimiSeek `GITHUB_TOKEN` has repository-scoped `contents: write` rather than a branch-scoped credential. Workflow shell intent alone is not authority. CI and the collector preflight fail closed if the required live ruleset is absent, inactive, no longer covers the default branch, or loses the required rule types; terminal semantic review must independently re-resolve the full live rule.

The optional GitHub setting `require_extra_approval_for_unattributed_changes=true` is also currently present in the pull-request rule. It is not relied upon by MimiSeek acceptance and is not part of the minimum canonical-ref invariant.

The prior fresh semantic review was bound to HEAD `3fc18bcc4edc47cf2bca341dc092f1f80bb2fa1b` and returned three findings. All three findings were remediated, which moved the PR HEAD and made that result historical remediation evidence only. A new fresh exact-head independent review is required for terminal acceptance.

## Evidence gaps that remain

GitHub-native Codex reviews, PR comments, review comments, commits, and owner adjudication replies can be preserved automatically once the collector source credentials are configured and a successful authenticated intake run records its watermark.

Fresh ordinary-ChatGPT terminal reviews that existed only inside ChatGPT and were never durably exported into the consumer PR cannot be reconstructed from GitHub alone. Stage 2 must define/implement structured consumer evidence export so future fresh terminal results are also captured automatically. Historical chat-only gaps must remain explicit rather than being inferred from absence.

## Next canonical action

Continue Stage 1, in this order:

1. obtain green exact-head CI for the final PR #5 remediation head with the live canonical-ref rule in force;
2. obtain a new fresh independent exact-head semantic review under immutable BASE policy; persist a CURRENT terminal result without moving HEAD and merge the bootstrap-data/evidence-intake foundation only on CURRENT PASS;
3. run authenticated backfill for CAP/UV and verify the durable collector watermark/intake snapshots;
4. complete commit-level provenance reconciliation for imported BUGGY/FIXED/VERIFIED identities, including material assertions currently present only in authenticated source commentary;
5. resolve exact accepted CAP/UV reviewer-policy refs;
6. classify generic versus project-specific rules;
7. only after the evidence set is current and reconciled, derive an immutable reusable **baseline seed** that is explicitly not stable and not distributable.

Stage 2 then adds structured consumer evidence export/binding, including durable fresh ordinary-ChatGPT result export. Stage 3 later completes the normalized operational collector/outcome-store contract and owns operational outcome schemas rather than appending records to bootstrap-v1 files.

All work uses normal post-bootstrap branch/PR acceptance. PR #1's bootstrap exception is no longer available.

## Open risks

- Loss of access to the exact pinned Library artifact must halt historical-source reconciliation until a governed replacement/provenance migration is accepted.
- Missing or weakened canonical-ref protection must leave the write-capable intake workflow disabled/fail-closed.
- Missing collector GitHub App credentials leave automatic intake unconfigured; do not pretend collection is active until a successful authenticated run records a watermark.
- Chat-only review evidence cannot be inferred from GitHub absence.
- Source workbook commentary may contain useful fix/adjudication hints, but those hints are not canonical truth until reconciled against governed provenance.
- A naive common baseline could silently lose CAP- or UV-specific obligations.
- Historical outcomes are selection-biased; they are learning/regression evidence, not a neutral leaderboard.
- First-promotion evaluation must later define fixed absolute requirements without fabricating a nonexistent stable comparison.
- Consumer safe-window detection must not infer safety from silence or absence of visible GitHub activity.
