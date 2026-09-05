# Current State

Last synchronized: 2026-09-05

## Repository state

- Project: MimiSeek Review
- Repository: `BogdanAIP/MimiSeek-review`
- Stable branch: `main`
- Development status: Stage 1 in progress — authenticated collector active, first backfill durable, structural BUGGY/FIXED/VERIFIED provenance accepted, bounded F050/F051, F052, F053/F054, F058, and F057 multi-review-progression source-commentary reconciliations represented, clean unchanged-source collector no-op and large-PR commit collection accepted; remaining source-commentary reconciliation, reviewer-policy refs, classification, and baseline seed remain pending
- Stage 0 implementation foundation: accepted and merged
- Stage 1 bootstrap-data/evidence-intake foundation: accepted and merged
- Stage 1 structural bootstrap commit provenance: accepted and merged
- Stage 1 first bounded source-commentary reconciliation (F050/F051): accepted and merged
- Stage 1 exact-head clean re-review reconciliation (F052): accepted and merged
- Stage 1 same-PR material-fix evidence reconciliation (F053/F054): accepted and merged
- Stage 1 same-PR material-fix-baseline reconciliation (F058): accepted and merged
- Stage 1 same-PR multi-review progression reconciliation (F057 → distinct F059/F061): represented in this tree; acceptance remains PR-scoped until fresh exact-head review/merge
- Stage 1 collector clean no-op and large-PR support: accepted and merged
- Review-job coordination research: accepted in PR #14
- Review-job coordination architecture: `ACCEPT_NARROW` selected by ADR 0013
- Semantic reviewer architecture research plan: accepted PR #18 consolidates predecessor PR #6, review-quality orchestration research, and later finding/strategy ideas as research only; no production context/orchestration architecture was selected
- Review-job local foundation: accepted PR #16 implements the `REVIEW_JOB_V1` public schema/state-machine/validation boundary
- Review-job durability slice in this tree: MimiSeek-owned GitHub ledger/publication adapter implemented with revision/identity fencing, immutable exact-result blob publication, and explicit ambiguous-publication reconciliation; physical production enablement and external CAP/session integration remain pending acceptance/separate verification
- Track R implementation may proceed in parallel with remaining Stage 1 work, but live external launch/wake remains blocked until separately accepted/verified generic external session capabilities are resolved
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

Accepted PR #10 establishes a distinct F052 evidence shape for CAP PR #129. The authenticated source note says that the P2 was fixed and a final exact-head Codex re-review reported no remaining major issues. `data/bootstrap-commentary-rereview-reconciliation.json` binds that bounded claim to the exact original Codex finding on reviewed head `0dde5aab1725c076ff56e2d2c8662c842e57b8ae`, live merged-PR final head `d6ea5bbd913d8a3ab27d7d1521d389e972602de2`, exact owner reply/re-review request, exact Codex GitHub-App clean-result comment, evidence chronology, final changed-file inventory, and immutable final-head contract-test text.

This F052 evidence does not claim that the final reviewed branch head itself became a canonical-main commit. Live history for PR #129 is divergent after merge mechanics, while the authenticated source claim is specifically about an exact-head review. The relevant identity boundary is therefore the exact live final merged-PR head plus reviewed→fixed descent, immutable fixed-head content, and the clean Codex result bound to that same head. A clean re-review remains evidence about that bounded review run, not universal semantic-correctness authority.

Accepted PR #12 closes the previously pending clean collector no-op gate and the newly exposed large-PR commit-history boundary. For source PRs above GitHub's 250-commit pull-list cap, the collector now reads exact paginated BASE...HEAD comparison commits and fails closed on count, compare identity, duplicate SHAs, source movement, or failure to terminate at the exact PR HEAD. The existing post-read PR identity fence remains authoritative for mixed-head rejection. For unchanged source snapshots, durable per-repository watermark/state no longer advances merely because wall-clock time passed; retaining the prior watermark is conservative because the next scan rechecks at least the same overlap interval. A fresh independent exact-head review accepted a physical two-pass live CAP/UV run in which the first pass converged stale local evidence and a later second pass changed zero snapshots, zero durable state bytes, and zero files while the remote intake branch remained unchanged.

Accepted PR #11 establishes the bounded same-PR material-fix evidence shape for UV PR #71 findings F053/F054. Each entry binds the exact original Codex review/finding, exact owner reply naming the full same-PR fix commit, reviewed→fix descent, source-PR membership, exact fix-commit changed-file inventory, and immutable implementation/regression content materially corresponding to the authenticated source Note. GitHub may relocate an old inline review comment's mutable current `commit_id`; the accepted identity model binds historical authority through the exact review submission plus `original_commit_id` and allows a current relocation only to the original reviewed head or live final PR head. Later reviewer silence is not used as proof of repair, and `SUPPORTED_SAME_PR_MATERIAL_FIX_EVIDENCE` remains narrower than universal semantic correctness.

Accepted PR #13 establishes the bounded same-PR material-fix-baseline evidence shape for UV PR #71 finding F058 from reviewed head `aafddd3b37476a65558d56755edd2ae440648b74`. Its authenticated Note says `Fixed with exact harness/store/planner authority checks.` The exact owner reply names code-bearing baseline `9af22cdcbb60501dca968fd10f12dc1d40ee6482`, which is the end of a four-commit reviewed→baseline range rather than one implementation commit. `SUPPORTED_SAME_PR_MATERIAL_FIX_BASELINE_EVIDENCE` therefore binds the exact original Codex finding/thread, exact owner reply and baseline SHA, exact ordered reviewed→baseline commit sequence, exact range changed-file inventory, source-PR membership/ancestry, and immutable baseline-head implementation/regression content. It deliberately does not pretend the named baseline commit itself is the implementation commit and does not infer universal semantic correctness from owner prose, ancestry, tests, CI, or later reviewer silence.

This tree adds the bounded same-PR multi-review progression evidence shape for UV PR #71 finding F057 from reviewed head `aafddd3b37476a65558d56755edd2ae440648b74`. Its authenticated Note says `Fixed by complete typed delegation matching and later stronger namespace reservation.` The progression preserves three distinct normalized findings and reviewed heads rather than collapsing them: F057 binds its exact owner response head `9af22cdcbb60501dca968fd10f12dc1d40ee6482` and complete-typed matching evidence; later F059 on reviewed head `10643bd160c65b8d8df690266390725d5d0dd6eb` binds the stronger existing-identity namespace collision and response head `7c8280721d96e7822d3c56e08e00ff6cb3868349`; later F061 on that `7c828072...` reviewed head binds the further proposal-created namespace collision and response code/docs head `1467bd3c97511f8349b574d00a6029e8e98b3fe7`. `SUPPORTED_SAME_PR_MULTI_REVIEW_PROGRESSION_EVIDENCE` records only that bounded source-note progression with exact review/comment/reply, ancestry, source-PR membership, and immutable response-head content. The relation labels are Stage-1 evidence descriptors only: they do not instantiate future `FINDING_V1` lifecycle authority, do not turn F057/F059/F061 into one defect identity, and do not infer universal semantic correctness from owner prose, tests, CI, ancestry, or later reviewer silence.

All accepted commentary slices explicitly report that global source-commentary reconciliation is incomplete. Other material source-commentary/disposition assertions still require governed reconciliation before baseline derivation.

Stage 1 is therefore still incomplete. Material source-commentary/disposition reconciliation is only partially covered, CAP/UV accepted reviewer-policy refs are unresolved here, generic-versus-project-specific classification is unfinished, and no baseline seed exists.

It also does not create learning events, a candidate, a stable reviewer, promotion authority, distribution authority, or consumer installation. The Stage 1 intake foundation remains non-authoritative source preservation, not the completed Stage 3 normalized outcome store.

## Review-job coordination boundary

Accepted research PR #14 established that the desired automated review flow can be separated from consumer development authority if the split is narrow and explicit. ADR 0013 selects `ACCEPT_NARROW` for that architecture.

The authorized fast loop is:

```text
originating project chat
    ↓ explicit exact-identity review request
MimiSeek review-job control plane
    ↓ generic execution request
CAP / generic session substrate
    ↓
fresh Temporary Chat reviewer
    ↓ REVIEW_RESULT_V1
MimiSeek live identity recheck + durable GitHub result
    ↓ generic return/wake delivery
originating project chat continues
```

Consumer/project authority remains outside MimiSeek: the origin decides readiness, local policy, finding adjudication, remediation, re-review, terminal acceptance, and merge consequences.

The first accepted MimiSeek-local Track R foundation consists of `schemas/review-job-v1.schema.json` plus the supported `tools/review_job_state.py` boundary. It defines the exact public record shape, deterministic immutable job identity, revision/CAS-style mutation checks, exact `REVIEW_RESULT_V1` and external-execution correlation, explicit `STALE`/`ABSTAIN`/`FAILED` outcomes, result-content digests, and launch/publication/return claim states including `*_UNKNOWN` reconciliation states that forbid blind duplicate retry. This is a local coordination foundation, not a live external executor.

The public record contains only durable GitHub-safe identity/state. Raw external execution/session references are not persisted; when an external execution reference must be correlated, the local state stores only its SHA-256 fingerprint. The schema rejects undeclared fields, and public durable locators are constrained to GitHub-owned references. A usable ChatGPT/browser/session capability must remain outside the public record.

This tree adds the next MimiSeek-owned durability layer: `tools/review_job_github_ledger.py` is the supported repository-scoped facade over the private ledger implementation. It only accepts `BogdanAIP/MimiSeek-review` as the authoritative ledger repository. The adapter uses an isolated `mimiseek-review-jobs-v1` branch marker, persists canonical per-job `REVIEW_JOB_V1` snapshots with exact one-revision progression, stores exact reviewer-result bytes as immutable Git blobs, and commits the result artifact plus resulting `RESULT_PERSISTED` job snapshot atomically in one tree commit. Result-less pre-launch `STALE`/`FAILED` publication uses bounded `REVIEW_JOB_OUTCOME_V1` rather than fabricating reviewer bytes.

Ledger ref movement is non-force. Definite concurrent branch movement is treated as a CAS conflict and re-read before any retry. A mutating ref request whose outcome is ambiguous is never treated as success by assumption: exact observed state may prove an ordinary snapshot write applied; result publication either proves the exact result commit visible or durably fences the claim as `PUBLICATION_UNKNOWN`. The unknown fence and the original candidate publication are sibling commits, so only one can remain a fast-forward successor. Reconciliation must then prove the exact result already persisted or prove the fenced artifact absent before returning to `RESULT_VALIDATED` and permitting a new explicit publication claim.

The adapter does not initialize a live production ledger branch merely because the code exists, does not create an external reviewer execution, and does not perform return/wake delivery. Physical MimiSeek-owned ledger enablement/recovery evidence and external CAP/session integration remain separate acceptance work.

External execution remains a separately governed dependency. Before live launch/return integration, MimiSeek must independently verify exact accepted generic external capabilities for:

- fresh qualified worker launch + correlated result;
- opaque existing-session return delivery;
- restart/recovery and one-shot/no-blind-resend semantics;
- no project-specific routing tables or PR/PASS/FINDINGS interpretation inside transport.

The existing CAP/UV source GitHub App stays read-only. The supported ledger backend is scoped to MimiSeek's own repository and must not be redirected to a consumer/source repository. Private ChatGPT/browser/session capabilities and GitHub authentication tokens must not be written to public job records or ledger artifacts.

Track R does not create a stable reviewer, does not install MimiSeek in consumers, and does not make a review `PASS` merge or promotion authority.

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

Immediate repeat collections correctly refreshed genuinely moving source evidence, but could not prove the unchanged-source case. A later quiet-source control exposed both GitHub's 250-commit PR-list cap on UV PR #89 and the old collector's wall-clock-only state churn. Accepted PR #12 repaired both boundaries and supplied the required physical clean no-op proof: after one convergence pass, a later second live CAP/UV scan changed no snapshots, did not advance either repository watermark, left durable state byte-identical, produced no file diff, and observed the remote `evidence/github-intake` ref unchanged for the check interval. The clean no-op/idempotence gate is therefore accepted rather than pending.

## Evidence gaps that remain

GitHub-native Codex reviews, PR comments, review comments, commits, and owner adjudication replies can now be preserved automatically for collector-selected PRs.

Fresh ordinary-ChatGPT terminal reviews that existed only inside ChatGPT and were never durably exported into the consumer PR cannot be reconstructed from GitHub alone. Stage 2 must define/implement structured consumer evidence export so future fresh terminal results are also captured automatically. Historical chat-only gaps must remain explicit rather than being inferred from absence.

Once this ledger/publication adapter is accepted and physically enabled, Track R durable review-job results can reduce future chat-only result loss. Those results are still source review evidence, not automatically adjudicated learning outcomes, and they do not replace Stage 2/3 evidence/export/normalization requirements.

Authenticated workbook commentary can contain material fix/adjudication hints. Structural commit reconciliation is not enough to promote those hints. Accepted F050/F051, F052, F053/F054, and F058 slices plus the F057 multi-review progression represented in this tree demonstrate bounded patterns for preserving explicit unknowns, binding positive follow-up claims, binding exact-head clean re-review chains, binding exact same-PR fix commits, binding owner-declared multi-commit code-bearing baselines, and preserving stronger later findings without collapsing distinct reviewed heads. None of those shapes silently converts source commentary into universal semantic correctness. The rest of the material commentary corpus still needs the same treatment.

## Next canonical action

Two workstreams may proceed in parallel without changing each other's authority.

### Stage 1 reviewer-evolution foundation

Continue in this order where dependencies allow parallel preparation:

1. continue material source-commentary/disposition reconciliation on top of the accepted structural BUGGY/FIXED/VERIFIED provenance layer, preserving explicit unknowns where evidence is insufficient and never converting remediation or clean-review evidence into semantic correctness by implication;
2. resolve exact accepted CAP/UV reviewer-policy refs;
3. classify generic versus project-specific rules;
4. only after the evidence set is current and reconciled, derive an immutable reusable **baseline seed** that is explicitly not stable and not distributable.

### Track R independent-review coordination

With the MimiSeek-owned ledger/publication slice accepted:

1. enable and verify the isolated MimiSeek-owned ledger path under separately governed MimiSeek write authority, including physical exact-result publication, concurrent-CAS behavior, restart recovery, and ambiguous-applied/absent reconciliation without touching a consumer repository;
2. independently resolve the exact accepted generic session/execution capability identities for fresh qualified worker launch/result correlation and existing-session return delivery;
3. only then add the external launch/result adapter and the private-route return/wake adapter against those immutable external capability identities;
4. keep private return/session authority outside the public ledger and keep CAP/UV source GitHub access read-only;
5. run the required cross-origin physical E2E/restart/ambiguous-delivery experiments before treating Track R as routine review infrastructure.

The accepted local state foundation plus accepted durability adapter do not satisfy those later external/physical acceptance gates by themselves.

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
- Review-job retries/recovery must not create duplicate reviewer launches or duplicate origin wakes.
- A public review-job ledger must never leak a usable private ChatGPT/browser/session capability or GitHub authentication token.
- The supported durable ledger path must remain MimiSeek-owned; redirecting publication into a consumer/source repository is outside Track R authority.
- Before routine use, physical ledger branch/ref behavior must be verified under MimiSeek-owned credentials; code-level CAS tests alone are not external durability evidence.
- MimiSeek must not silently depend on an unaccepted or moving external CAP/session runtime contract.
- Track R must not grow into consumer-specific development orchestration or treat reviewer PASS as merge/promotion authority.
