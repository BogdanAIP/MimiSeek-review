# Current State

Last synchronized: 2026-09-03

## Repository state

- Project: MimiSeek Review
- Repository: `BogdanAIP/MimiSeek-review`
- Stable branch: `main`
- Development status: Stage 1 in progress — authenticated collector active, first backfill durable, structural BUGGY/FIXED/VERIFIED provenance accepted, and the first bounded source-commentary slice accepted; clean unchanged-source no-op, remaining source-commentary reconciliation, reviewer-policy refs, classification, and baseline seed remain pending
- Stage 0 implementation foundation: accepted and merged
- Stage 1 bootstrap-data/evidence-intake foundation: accepted and merged
- Stage 1 structural bootstrap commit provenance: accepted and merged
- Stage 1 first bounded source-commentary reconciliation (F050/F051): accepted and merged
- Stable reviewer version: **not established yet**
- Bootstrap baseline seed: none
- Candidate reviewer version: none
- Registered initial consumers/evidence producers: `BogdanAIP/chat-agent-platform`, `BogdanAIP/uv-studio`
- Consumer MimiSeek installation: none yet; first installation is governed by Stage 8 safe distribution
- Native ChatGPT skill identities: `mimiseek-review-run` and `mimiseek-review-update`

Exact accepted-stage review/merge identities belong only in `docs/EVIDENCE_INDEX.md`. Non-terminal PR review attempts/remediations belong to PR history. This file owns current position and next action.

## Stage 1 implementation reality

The accepted Stage 1 foundation provides:

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
- `.github/workflows/collect-review-evidence.yml` for hourly/manual intake through a dedicated read-only source GitHub App;
- `.github/workflows/ci.yml` with unit tests and a live effective-rules check for the canonical-ref authority boundary.

Accepted PR #8 adds structural live verification of all 84 imported BUGGY/FIXED/VERIFIED cases across 9 regression-source PRs. The normal path requires exact case/finding identity, exact source PR identity, commit membership, and ancestry. A discovered CAP PR #124 historical rebase conflict is preserved separately in `data/bootstrap-provenance-reconciliation.json`: the authenticated bootstrap projection is not rewritten, the exact Codex-reviewed detached BUGGY head remains bound to its historical GitHub review evidence and actual parent, and the later rebased FIXED lineage is independently bound to the exact owner-review submissions that identify the rebased response anchor. This structural reconciliation does **not** infer semantic fix correctness from ancestry, thread replies, owner prose, or a passing test and does not promote workbook commentary into canonical truth.

Accepted PR #9 establishes the first bounded source-commentary reconciliation for CAP PR #121 findings F050/F051. `data/bootstrap-commentary-reconciliation.json` is a separate governed layer tied to the authenticated workbook digest and normalized finding/source-row identities. F050 remains explicit `UNKNOWN`; the layer binds its original Codex finding but makes no claim that later evidence is absent. For F051, the layer verifies only the material workbook Notes assertion that follow-up PR #123 added the hostile-caller output-ownership implementation/regression evidence, using exact source/follow-up identities, Git/result provenance, changed-file inventory, and immutable-head content. Even when that evidence is present, semantic fix correctness is still not inferred.

The current proposed bounded continuation adds a distinct F052 evidence shape for CAP PR #129. The authenticated source note says that the P2 was fixed and a final exact-head Codex re-review reported no remaining major issues. `data/bootstrap-commentary-rereview-reconciliation.json` binds that claim to the exact original Codex finding on reviewed head `0dde5aab1725c076ff56e2d2c8662c842e57b8ae`, live merged-PR final head `d6ea5bbd913d8a3ab27d7d1521d389e972602de2`, exact owner reply/re-review request, exact Codex GitHub-App clean-result comment, evidence chronology, final changed-file inventory, and immutable final-head contract-test text.

This F052 evidence does not claim that the final reviewed branch head itself became a canonical-main commit. Live PR #129 history is divergent after merge mechanics, while the authenticated source claim is specifically about an exact-head review. The relevant identity boundary is therefore the exact live final merged-PR head plus reviewed→fixed descent, immutable fixed-head content, and the clean Codex result bound to that same head. A clean re-review remains evidence about that bounded review run, not universal semantic-correctness authority.

Both commentary slices explicitly report that global source-commentary reconciliation is incomplete. Other material source-commentary/disposition assertions still require governed reconciliation before baseline derivation.

Stage 1 is therefore still incomplete. A clean live unchanged-source collector no-op has not yet been demonstrated, material source-commentary/disposition reconciliation is only partially covered, CAP/UV accepted reviewer-policy refs are unresolved here, generic-versus-project-specific classification is unfinished, and no baseline seed exists.

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

The registered evidence scope is configured in `config/consumers.json` for both initial producers with deliberate overlap from `2026-08-30T00:00:00Z`.

The dedicated source GitHub App is now installed only on the registered CAP/UV repositories with read-only Contents, Issues, Pull requests, and required Metadata access. Repository Actions secrets hold the App Client ID/private key and `MIMISEEK_COLLECTOR_ENABLED=true` intentionally enables collection. Credentials remain external secret state and are never repository data.

The first authenticated collection from accepted `main` completed successfully. It created `evidence/github-intake`, wrote deterministic source snapshots for 16 selected CAP PRs and 4 selected UV PRs, and durably recorded a collector watermark/state at `2026-09-02T14:33:02Z`. Exact run/commit evidence belongs in `docs/EVIDENCE_INDEX.md`.

Immediate repeat collections also completed successfully, but they are **not** counted as the required unchanged-source no-op proof because `uv-studio` PR #89 genuinely changed between scans. Those runs correctly refreshed the moving UV snapshot while unchanged CAP snapshot files were not rewritten. A later quiet-source run must still demonstrate the clean no-op/idempotence case before this gate is closed.

## Evidence gaps that remain

GitHub-native Codex reviews, PR comments, review comments, commits, and owner adjudication replies can now be preserved automatically for collector-selected PRs.

Fresh ordinary-ChatGPT terminal reviews that existed only inside ChatGPT and were never durably exported into the consumer PR cannot be reconstructed from GitHub alone. Stage 2 must define/implement structured consumer evidence export so future fresh terminal results are also captured automatically. Historical chat-only gaps must remain explicit rather than being inferred from absence.

Authenticated workbook commentary can contain material fix/adjudication hints. Structural commit reconciliation is not enough to promote those hints. Accepted F050/F051 and the proposed F052 slice demonstrate two bounded patterns: preserve explicit unknowns, bind positive follow-up claims to governed identities/content, and bind exact-head clean re-review claims to the exact review chain without silently turning any of them into universal semantic correctness. The rest of the material commentary corpus still needs the same treatment.

## Next canonical action

Continue Stage 1, in this order where dependencies allow parallel preparation:

1. when a genuinely quiet source window is available, obtain one clean live unchanged-source collector run and verify true no-op/idempotent snapshot behavior; do not substitute runs that overlap real source movement;
2. meanwhile continue material source-commentary/disposition reconciliation on top of the accepted structural BUGGY/FIXED/VERIFIED provenance layer, preserving explicit unknowns where evidence is insufficient and never converting remediation or clean-review evidence into semantic correctness by implication;
3. resolve exact accepted CAP/UV reviewer-policy refs;
4. classify generic versus project-specific rules;
5. only after the evidence set is current and reconciled, derive an immutable reusable **baseline seed** that is explicitly not stable and not distributable.

Stage 2 then adds structured consumer evidence export/binding, including durable fresh ordinary-ChatGPT result export. Stage 3 later completes the normalized operational collector/outcome-store contract and owns operational outcome schemas rather than appending records to bootstrap-v1 files.

All repository changes continue through normal post-bootstrap branch/PR acceptance under accepted-BASE authority. PR #1's bootstrap exception is no longer available.

## Open risks

- Loss of access to the exact pinned Library artifact must halt historical-source reconciliation until a governed replacement/provenance migration is accepted.
- Missing or weakened canonical-ref protection must leave the write-capable intake workflow disabled/fail-closed.
- Revoked, rotated, or invalid source GitHub App credentials must make collection fail closed; source access must never be widened to recover from an authentication failure.
- A PR changing during sequential evidence collection must fail the scan rather than publish a mixed-head snapshot; later retry/backfill is preferred to ambiguous provenance.
- Repository rename/transfer and deleted-fork cases must preserve immutable IDs/explicit unknowns rather than rely only on mutable owner/name strings.
- Historical rebases/force-pushes can make a reviewed head disappear from the final PR commit list; such cases require explicit PR-bound historical evidence and must not be silently treated as linear ancestry.
- Chat-only review evidence cannot be inferred from GitHub absence.
- Source workbook commentary may contain useful fix/adjudication hints, but those hints are not canonical truth until reconciled against governed provenance.
- A bounded commentary slice must never be misreported as complete corpus reconciliation.
- A clean exact-head reviewer result must remain bound to its exact reviewed head and must not be generalized into a claim about later history or universal correctness.
- A naive common baseline could silently lose CAP- or UV-specific obligations.
- Historical outcomes are selection-biased; they are learning/regression evidence, not a neutral leaderboard.
- First-promotion evaluation must later define fixed absolute requirements without fabricating a nonexistent stable comparison.
- Consumer safe-window detection must not infer safety from silence or absence of visible GitHub activity.
