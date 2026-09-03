# Evidence Index

This document indexes accepted stage evidence and review/remediation chronology. It is not a substitute for GitHub, CI logs, review results, immutable commits, or canonical data manifests; it points to them.

## Stage 0 — Continuous-development foundation

Status: DONE

Implementation and acceptance identity:

- PR #1 — `Bootstrap continuous development foundation`
- BASE: `09492f1ec8aeb1dfbfc152505d14574016a72870`
- accepted exact PR HEAD: `1588e196051917bf35483ba05b5f7f36fd00c468`
- bootstrap `review_policy_ref`: `09492f1ec8aeb1dfbfc152505d14574016a72870`
- terminal review artifact: `docs/evidence/stage0-pr1-terminal-review.md`
- terminal review artifact Git blob: `2a6a7d72561e5be67e88cd36fbf81251abf71761`
- durable GitHub PR #1 evidence comment id: `5493224928`
- repository-assigned reviewer instance identity: `ordinary_chat_fresh:pr1:1588e196051917bf35483ba05b5f7f36fd00c468:2026-09-01T13:59:11+03:00`
- reviewer identity/class reported by the terminal result: `ordinary_chat_fresh`
- review mode reported by the terminal result: `read_only`
- final independent review: `CURRENT PASS`
- reported findings: `0`
- rejected candidates: `15`
- review timestamp: `2026-09-01T13:59:11+03:00`
- CI state: `NOT_CONFIGURED`
- squash-merge commit on `main`: `3e482964daaae5aefad2eeaf832836cd340ac5f5`
- accepted-head Git tree: `d2c5ff390312ace75770b626ef62e4343977d8c3`
- merged-commit Git tree: `d2c5ff390312ace75770b626ef62e4343977d8c3`

The terminal review artifact preserves the complete independent `REVIEW_RESULT_V1` verbatim and records the provenance available from the received result. Its repository-assigned reviewer-instance identifier is derived only from fields emitted by that result and does not invent a platform conversation identifier. A fresh chat can resolve the immutable Git blob directly and can also resolve PR #1 comment `5493224928`, which records the same exact review binding and points to that blob. The artifact does not claim cryptographic attestation of the external chat beyond the identity and independence assertions in the terminal result itself.

The accepted exact HEAD and squash-merge commit have the same Git tree, proving that the merged repository contents are the exact contents independently accepted by the terminal review.

Stage 0 established:

- repository-owned cross-chat development state;
- standalone multi-project reviewer-improvement boundary;
- consumer/evidence/distribution responsibility split;
- identity-bound recovery contract for the historical Stage 1 workbook;
- two user-facing ChatGPT roles with repository-owned workflow contracts;
- new independent update chat for every real update invocation;
- separation of global promotion from per-consumer installation;
- fail-closed consumer safe-update semantics and running-run reviewer immutability;
- repository-development review evidence bound to immutable repository/base/head/reviewer/`review_policy_ref`;
- accepted BASE policy governing ordinary future PR acceptance, with HEAD governance target-only for the PR that introduces it;
- the explicit one-time PR #1 bootstrap exception, now exhausted by the accepted merge;
- no bootstrap shortcut for first stable admission or first consumer installation;
- one canonical owner for review chronology and exact Stage 0 acceptance evidence: this evidence index, with source review content stored in the terminal-review artifact above.

### Review/remediation chronology

1. Exact head `cd5090b38e556636bea6c3f6dd4e0e74c2f41dff`
   - fresh independent review: `FINDINGS` (3);
   - confirmed/remediated: historical-source recoverability, unconditional fresh update-chat boundary, README bootstrap single-ownership;
   - result became STALE when HEAD moved.

2. Exact head `354eab1117e60a426fa3b86109b42abb147ac005`
   - fresh independent review: `FINDINGS` (1 P1);
   - prior remediations verified PASS;
   - confirmed/remediated: repository-development acceptance lacked immutable prior `review_policy_ref`;
   - remediation added accepted-BASE policy authority, one-time PR #1 bootstrap exception, and ADR 0010;
   - result became STALE when HEAD moved.

3. Exact head `26ce83e74dea5e5c45645dd3d2f454d5f0e2214f`
   - fresh independent review: `FINDINGS` (3: P1, P1, P2);
   - all earlier remediations verified PASS;
   - confirmed/remediated: missing governed first-stable admission, premature Stage 2 consumer pin requirement, and duplicate review-chronology ownership;
   - remediation created baseline-seed → candidate → normal promotion sequencing, deferred first installation to normal Stage 8 safe distribution, added ADR 0011, and made this file the single review-chronology owner;
   - result became STALE when HEAD moved.

4. Exact head `1588e196051917bf35483ba05b5f7f36fd00c468`
   - durable source result: Git blob `2a6a7d72561e5be67e88cd36fbf81251abf71761`, path `docs/evidence/stage0-pr1-terminal-review.md` in PR #2;
   - durable GitHub pointer: PR #1 comment `5493224928`;
   - reviewer instance identity: `ordinary_chat_fresh:pr1:1588e196051917bf35483ba05b5f7f36fd00c468:2026-09-01T13:59:11+03:00`;
   - fresh independent review: `PASS`;
   - review validity: `CURRENT` at final live re-resolution;
   - reported findings: `0`;
   - rejected candidates: `15`;
   - all requested remediation checks: PASS;
   - historical Library artifact independently recovered and verified against the canonical source manifest;
   - GitHub evidence showed no workflow runs, commit statuses, check runs, required status checks, or rulesets; classification `NOT_CONFIGURED`;
   - accepted for Stage 0 merge under bootstrap `review_policy_ref=09492f1ec8aeb1dfbfc152505d14574016a72870`.

PR #1 was then squash-merged with `expected_head_sha=1588e196051917bf35483ba05b5f7f36fd00c468`, producing `main` commit `3e482964daaae5aefad2eeaf832836cd340ac5f5`. The merged commit and accepted exact head share Git tree `d2c5ff390312ace75770b626ef62e4343977d8c3`.

Earlier Codex usage-limit notices and reviews of earlier heads are not terminal acceptance evidence for the accepted Stage 0 head.

Stage 0 CI remains accurately recorded as `NOT_CONFIGURED`, not PASS.

## Stage 1 — Bootstrap data + reviewer baseline seed

Status: IN PROGRESS

Canonical bootstrap source identity and recovery contract: `data/bootstrap-source.json`.

### Accepted foundation slice — PR #5

PR #5 — `Stage 1: bootstrap review data and continuous evidence intake` established the accepted bootstrap-data projection and bounded non-authoritative GitHub evidence-intake foundation.

Acceptance identity:

- BASE: `05342285d23260c069f13fd123e5dc872648d6ce`
- accepted exact PR HEAD: `fb4449dedc69671b277d8ef3c4ceb6b09fb088e9`
- `review_policy_ref`: `05342285d23260c069f13fd123e5dc872648d6ce`
- changed files: `20`
- reviewer identity/class reported by the terminal result: `ordinary_chat_fresh`
- review mode: `read_only`
- terminal review validity: `CURRENT`
- terminal review status: `PASS`
- reported findings: `0`
- rejected candidates: `22`
- review timestamp: `2026-09-02T12:36:46Z`
- durable GitHub terminal-result comment id: `5510158690`
- exact-head CI run: `33628956383`
- CI state: `PASS`
- accepted live canonical ruleset: `mimiseek-canonical-main`, ruleset id `22076488`
- merge commit on `main`: `bda75c6d1c0b5b56a48728e4ab04aee84c77188b`

The durable PR #5 comment contains the terminal `REVIEW_RESULT_V1` itself rather than merely summarizing it. The result binds repository, PR, BASE, HEAD, reviewer context, read-only mode, immutable `review_policy_ref`, exact-head CI, live ruleset state, bootstrap authentication, and terminal PASS. The comment was persisted before merge without moving the reviewed HEAD.

The merge used `expected_head_sha=fb4449dedc69671b277d8ef3c4ceb6b09fb088e9`, so GitHub would have rejected the operation had the accepted head moved. PR #5 then merged as commit `bda75c6d1c0b5b56a48728e4ab04aee84c77188b`.

Accepted PR #5 foundation includes:

- authenticated workbook-backed bootstrap projections;
- fixed bootstrap-v1 sets of 92 review runs, 139 findings, and 84 regression cases;
- source blank-versus-zero preservation;
- corrected `RC-UV70-*` finding identity mapping with semantic/source-identity validation;
- bootstrap-only schema/provenance contracts and immutable count/byte/SHA anchors;
- explicit workbook-source versus normalized-projection authority boundary;
- bounded read-only CAP/UV evidence polling with immutable GitHub repository/PR identities;
- mixed-head snapshot rejection and fail-closed watermark semantics;
- dedicated non-authoritative `evidence/github-intake` publication design;
- server-enforced canonical-main write boundary validated through effective rules for the actual default branch;
- CI unit coverage plus live canonical-ref-boundary verification.

The accepted foundation did **not** by itself complete Stage 1. At acceptance, complete commit-level BUGGY/FIXED/VERIFIED provenance remained explicitly pending, no durable CAP/UV collector watermark had yet been demonstrated, exact accepted CAP/UV reviewer-policy refs had not yet been resolved into the Stage-1 baseline work, generic-versus-project-specific rule classification remained pending, and no baseline seed existed.

### Accepted state synchronization — PR #7

PR #7 — `Stage 1: record PR #5 acceptance and backfill readiness` synchronized `CURRENT_STATE`/`EVIDENCE_INDEX` after PR #5 without expanding Stage-1 authority.

Acceptance identity:

- BASE: `bda75c6d1c0b5b56a48728e4ab04aee84c77188b`
- accepted exact PR HEAD: `1030f4aa39457837423bea83acd1dfe84982a364`
- reviewer identity/class: `ordinary_chat_fresh`
- review mode: `read_only`
- terminal review validity: `CURRENT`
- terminal review status: `PASS`
- reported findings: `0`
- rejected candidates: `16`
- durable GitHub terminal-result comment id: `5510523944`
- exact-head CI run: `33635510046`
- CI state: `PASS`
- merge commit on `main`: `3fadb539fb83db9f4b8a71f1b22f04ca3a461ea5`

PR #7 did not activate the external collector or claim a durable intake watermark; it only made accepted repository documentation accurately describe the then-pending setup/backfill work.

### Collector activation evidence after PR #7

Collector activation is operational evidence within Stage 1, not a terminal acceptance record for the still-open provenance PR.

The dedicated source GitHub App was configured outside repository contents and installed only on the registered CAP/UV repositories with read-only source permissions. Secret values are intentionally not recorded here. Repository variable `MIMISEEK_COLLECTOR_ENABLED=true` intentionally enabled the accepted collector workflow.

The first authenticated run is durably identifiable as:

- workflow: `Collect review evidence`;
- run id: `33642703700`;
- run attempt: `1`;
- trigger: `workflow_dispatch`;
- source branch: `main`;
- exact workflow source HEAD: `3fadb539fb83db9f4b8a71f1b22f04ca3a461ea5`;
- conclusion: `success`;
- first intake commit: `77303e135a6dacb0c5f068940291c016902725d6`;
- intake commit parent: `3fadb539fb83db9f4b8a71f1b22f04ca3a461ea5`;
- durable scan/watermark: `2026-09-02T14:33:02Z`;
- selected CAP PR snapshots: `16`;
- selected UV PR snapshots: `4`.

The first intake commit created the non-authoritative `evidence/github-intake` data from the accepted `main` workflow and wrote `evidence/github/collector-state.json` beside the PR snapshots. This proves authenticated CAP/UV source access, durable publication, and watermark/state advancement; it does not make the intake branch canonical truth.

Immediate rerun attempts also completed successfully, but they are **not** accepted as the required unchanged-source no-op proof. `uv-studio` PR #89 genuinely changed between those scans. The collector correctly refreshed the moving `uv-studio/89.json`; one resulting evidence commit `8fc7c57d0f5531e73bebd05fb7b2b098535f97c7` changed that snapshot plus `collector-state.json`, while unchanged CAP snapshots were not rewritten. A clean quiet-source no-op/idempotence proof therefore remains pending and must not be inferred from these moving-source reruns.

### Structural bootstrap commit provenance — active PR #8 work

The active Stage-1 provenance slice is intentionally not listed as accepted until its normal PR acceptance completes. Current live verification work covers all 84 regression cases across **9 regression-source PRs**, not the wider 21-PR bootstrap identity scope.

Fail-closed verification discovered one material authenticated-source lineage conflict: seven CAP PR #124 cases (`RC-CAP124-047` through `RC-CAP124-053`) point to Codex-reviewed historical BUGGY head `48d2e89c3b2fee9053b5038c093ad5060124b2ce`, while the workbook's recorded BUGGY BASE belongs to a later rebased lineage. GitHub still preserves the exact detached commit, Codex review submission/comments bound to it, its actual parent, and owner replies recording the rebase/fix transition.

The active implementation preserves bootstrap-v1 projections unchanged and records the conflict in `data/bootstrap-provenance-reconciliation.json`. The live verifier distinguishes 77 ordinary linear-history cases from 7 explicit `reviewed_head_rebased_before_fix` cases. This is structural provenance only: semantic fix correctness, material source-commentary/disposition reconciliation, reviewer-policy refs, generic/project-specific classification, clean collector no-op, and baseline-seed derivation remain separate Stage-1 work.

Stage 1 continues under the normal accepted-BASE repository-development review policy. PR #1's no-policy bootstrap exception is no longer available.

## Later stages

Add entries only when evidence exists. Do not pre-fill imagined CI/review IDs.
