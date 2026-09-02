# Current State

Last synchronized: 2026-09-02

## Repository state

- Project: MimiSeek Review
- Repository: `BogdanAIP/MimiSeek-review`
- Stable branch: `main`
- Development status: Stage 1 in progress — accepted bootstrap-data/evidence-intake foundation, backfill/provenance/baseline work still pending
- Stage 0 implementation foundation: accepted and merged
- Stage 1 bootstrap-data/evidence-intake foundation: accepted and merged
- Stable reviewer version: **not established yet**
- Bootstrap baseline seed: none
- Candidate reviewer version: none
- Registered initial consumers/evidence producers: `BogdanAIP/chat-agent-platform`, `BogdanAIP/uv-studio`
- Consumer MimiSeek installation: none yet; first installation is governed by Stage 8 safe distribution
- Native ChatGPT skill identities: `mimiseek-review-run` and `mimiseek-review-update`

Exact accepted-stage review/merge identities belong only in `docs/EVIDENCE_INDEX.md`. Non-terminal PR review attempts/remediations belong to PR history. This file owns current position and next action.

## Stage 1 implementation reality

The accepted Stage 1 foundation now provides:

- an authenticated pinned historical workbook source identified by `data/bootstrap-source.json`;
- normalized authenticated bootstrap projections in `data/review-runs.jsonl`, `data/findings.jsonl`, and `data/regression-cases.jsonl`;
- exact anchored bootstrap-v1 sets of 92 review runs, 139 findings, and 84 regression cases;
- explicit separation between workbook source authority and normalized JSONL projection semantics;
- deterministic source-row recovery for intentionally omitted descriptive/source-commentary fields;
- permanent semantic/source-identity checks for regression-case links;
- explicit preservation of source blanks as `null` versus recorded numeric zeroes;
- bootstrap-only schemas that reject operational append records with fabricated workbook provenance;
- `tools/collect_github_evidence.py` for bounded read-only GitHub evidence polling of registered consumers;
- immutable GitHub repository/PR identities in snapshots alongside human-readable names and exact BASE/HEAD SHAs;
- a mixed-head identity fence that re-reads PR state after dependent evidence collection and fails before durable watermark advancement if identity/state moved;
- strict boolean handling for consumer `evidence.enabled`;
- `.github/workflows/collect-review-evidence.yml` for hourly/manual intake once the external source credentials and enablement variable are configured;
- `.github/workflows/ci.yml` with unit tests and a live effective-rules check for the canonical-ref authority boundary.

This accepted foundation does **not** complete Stage 1. Complete commit-level BUGGY/FIXED/VERIFIED provenance reconciliation remains unfinished, registered-consumer intake has not yet been proven current to a durable collector watermark, CAP/UV accepted reviewer-policy refs are unresolved here, generic-versus-project-specific classification is unfinished, and no baseline seed exists.

It also does not create learning events, a candidate, a stable reviewer, promotion authority, distribution authority, or consumer installation. The Stage 1 intake foundation remains non-authoritative source preservation, not the completed Stage 3 normalized outcome store.

## Canonical ref boundary

The live repository has ruleset `mimiseek-canonical-main` protecting the default branch. The accepted minimum Stage-1 invariant is:

- the named repository ruleset is active and targets branches;
- GitHub reports `current_user_can_bypass=never` for the actual workflow caller;
- a visible non-empty privileged bypass list fails closed;
- GitHub's effective-rules-for-branch API proves that this exact ruleset contributes `pull_request`, `deletion`, and `non_fast_forward` to the actual default branch;
- the default branch reports `protected=true`.

The collector checks this boundary before collection and again immediately before push. The server ruleset remains the real enforcement boundary because the MimiSeek workflow `GITHUB_TOKEN` has repository-scoped `contents: write`, not a branch-scoped credential.

The optional GitHub setting `require_extra_approval_for_unattributed_changes=true` may be present in the pull-request rule but is not relied upon by MimiSeek acceptance and is not part of the minimum canonical-ref invariant.

## Current evidence-intake state

The registered evidence scope is already configured in `config/consumers.json` for both initial producers with deliberate overlap from `2026-08-30T00:00:00Z`.

A live check immediately after PR #5 merge found no `evidence/github-intake` branch. Therefore **no successful intake publication and durable collector watermark have yet been demonstrated**. Branch absence does not prove which external setup item is missing; source credentials and collector enablement must be verified/configured before the first authenticated run.

The workflow-defined external requirements are:

- dedicated GitHub App credentials capable of creating a read-only installation token for the registered CAP/UV repositories;
- repository variable `MIMISEEK_COLLECTOR_ENABLED=true` when collection is intentionally enabled.

Do not treat the collector as active until a successful authenticated run creates/updates the intake branch and records a durable state/watermark.

## Evidence gaps that remain

GitHub-native Codex reviews, PR comments, review comments, commits, and owner adjudication replies can be preserved automatically after collector activation.

Fresh ordinary-ChatGPT terminal reviews that existed only inside ChatGPT and were never durably exported into the consumer PR cannot be reconstructed from GitHub alone. Stage 2 must define/implement structured consumer evidence export so future fresh terminal results are also captured automatically. Historical chat-only gaps must remain explicit rather than being inferred from absence.

## Next canonical action

Continue Stage 1, in this order:

1. verify/configure the collector's dedicated read-only source GitHub App credentials and intentional enablement variable without weakening the canonical-ref boundary;
2. run the first authenticated CAP/UV backfill from the accepted overlap boundary and verify creation of `evidence/github-intake`, deterministic per-PR snapshots, and a durable collector watermark/state;
3. run a second unchanged-source collection and verify idempotent/no-op behavior rather than duplicate or drifting snapshots;
4. complete commit-level provenance reconciliation for imported BUGGY/FIXED/VERIFIED identities, including material assertions currently present only in authenticated source commentary;
5. resolve exact accepted CAP/UV reviewer-policy refs;
6. classify generic versus project-specific rules;
7. only after the evidence set is current and reconciled, derive an immutable reusable **baseline seed** that is explicitly not stable and not distributable.

Stage 2 then adds structured consumer evidence export/binding, including durable fresh ordinary-ChatGPT result export. Stage 3 later completes the normalized operational collector/outcome-store contract and owns operational outcome schemas rather than appending records to bootstrap-v1 files.

All repository changes continue through normal post-bootstrap branch/PR acceptance under accepted-BASE authority. PR #1's bootstrap exception is no longer available.

## Open risks

- Loss of access to the exact pinned Library artifact must halt historical-source reconciliation until a governed replacement/provenance migration is accepted.
- Missing or weakened canonical-ref protection must leave the write-capable intake workflow disabled/fail-closed.
- Missing or invalid collector GitHub App credentials must leave automatic intake unconfigured; do not infer credential state merely from branch absence.
- A PR changing during sequential evidence collection must fail the scan rather than publish a mixed-head snapshot; later retry/backfill is preferred to ambiguous provenance.
- Repository rename/transfer and deleted-fork cases must preserve immutable IDs/explicit unknowns rather than rely only on mutable owner/name strings.
- Chat-only review evidence cannot be inferred from GitHub absence.
- Source workbook commentary may contain useful fix/adjudication hints, but those hints are not canonical truth until reconciled against governed provenance.
- A naive common baseline could silently lose CAP- or UV-specific obligations.
- Historical outcomes are selection-biased; they are learning/regression evidence, not a neutral leaderboard.
- First-promotion evaluation must later define fixed absolute requirements without fabricating a nonexistent stable comparison.
- Consumer safe-window detection must not infer safety from silence or absence of visible GitHub activity.
