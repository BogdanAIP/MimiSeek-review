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

Collector activation is operational evidence within Stage 1, not terminal acceptance of Stage 1 itself.

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

Immediate rerun attempts also completed successfully, but they are **not** accepted as the required unchanged-source no-op proof. `uv-studio` PR #89 genuinely changed between those scans. The collector correctly refreshed the moving `uv-studio/89.json`; one resulting evidence commit `8fc7c57d0f5531e73bebd05fb7b2b098535f97c7` changed that snapshot plus `collector-state.json`, while unchanged CAP snapshots were not rewritten. A clean quiet-source no-op/idempotence proof therefore remained pending until the later accepted PR #12 control described below.

### Accepted structural bootstrap commit provenance — PR #8

PR #8 — `Stage 1: verify bootstrap commit provenance live` established accepted structural BUGGY/FIXED/VERIFIED provenance verification for the 84 regression cases across 9 regression-source PRs.

Acceptance identity:

- BASE: `3fadb539fb83db9f4b8a71f1b22f04ca3a461ea5`
- accepted exact PR HEAD: `c9326633380efd2a991d99e1f8e0328e33353c78`
- `review_policy_ref`: `3fadb539fb83db9f4b8a71f1b22f04ca3a461ea5`
- changed files: `7`
- reviewer identity/class: `ordinary_chat_fresh`
- review mode: `read_only`
- terminal review validity: `CURRENT`
- terminal review status: `PASS`
- reported findings: `0`
- rejected candidates: `18`
- review timestamp: `2026-09-03T08:57:40+03:00`
- durable GitHub terminal-result comment id: `5521259867`
- exact-head CI run: `33719367707`
- CI state: `PASS`
- merge commit on `main`: `1250f54a39578d85f28ad7938edd8845eb6d096b`

The terminal result was persisted as top-level PR comment `5521259867` before merge without changing the reviewed HEAD. The merge then used `expected_head_sha=c9326633380efd2a991d99e1f8e0328e33353c78`; the resulting merge commit records both the accepted HEAD and the durable terminal-result pointer.

Accepted PR #8 establishes:

- live structural verification of all 84 regression cases across 9 regression-source PRs;
- 77 ordinary `linear_pr_history` cases requiring exact source identity, commit membership, ordered BUGGY→FIXED→VERIFIED ancestry, and VERIFIED ancestry into the live/final PR head;
- 7 CAP PR #124 `reviewed_head_rebased_before_fix` cases preserved without rewriting authenticated bootstrap-v1 projections;
- exact binding of the detached historical Codex-reviewed BUGGY head to its actual parent, exact Codex review/comment identities, and the later rebased response anchor to seven distinct owner review submissions;
- fail-closed rejection of alternate same-lineage anchors, wrong historical parent, wrong review/comment identity, missing/non-descendant commits, malformed identities, and incomplete/mixed-head source evidence;
- a live read-only source-App CI check alongside unit and canonical-ref-boundary checks.

PR #8 remains structural provenance only. It does not establish semantic correctness of historical fixes, does not adjudicate workbook Notes by itself, and does not complete source-commentary/disposition reconciliation, clean collector no-op proof, reviewer-policy refs, generic/project-specific classification, or baseline-seed derivation.

#### PR #8 review/remediation chronology

1. Exact head `a676f48c69c20f0f9b055eddad3c53a490148ee3`
   - fresh independent review: `CURRENT FINDINGS` (1 HIGH);
   - defect: the CAP #124 rebased lineage anchor was constrained by ancestry but was not bound to the exact owner review submissions that identify that response commit;
   - concrete alternate same-lineage commit `3d89e5c9d811b0077fd54969811cd6cbc57d3ec5` could have substituted under the old predicates;
   - result became STALE when HEAD moved.

2. Remediation on final head `c9326633380efd2a991d99e1f8e0328e33353c78`
   - exact seven owner reply identities were recorded;
   - each reply must bind to its exact original Codex thread and resolve to a distinct owner review submission;
   - every such owner review must have `commit_id=a2f22b3adcadc2fe23796a926871aae29bca3226`;
   - negative tests cover alternate same-lineage anchor, tampered owner-review commit binding, and exact owner-reply identity;
   - exact-head CI `33719367707`: PASS;
   - fresh independent terminal review: `CURRENT PASS`, 0 findings, 18 rejected candidates.

### Accepted first bounded source-commentary reconciliation — PR #9

PR #9 — `Stage 1: reconcile CAP #121 source commentary` established the first accepted governed reconciliation of material authenticated-workbook commentary without changing bootstrap-v1 source projections.

Acceptance identity:

- BASE: `1250f54a39578d85f28ad7938edd8845eb6d096b`
- accepted exact PR HEAD: `2fd1254d915363d6eb4720adacfebbce555e5ef9`
- `review_policy_ref`: `1250f54a39578d85f28ad7938edd8845eb6d096b`
- changed files: `8`
- reviewer identity/class: `ordinary_chat_fresh`
- review mode: `read_only`
- terminal review validity: `CURRENT`
- terminal review status: `PASS`
- reported findings: `0`
- rejected candidates: `24`
- review timestamp: `2026-09-03T12:39:06+03:00`
- durable GitHub terminal-result comment id: `5523796231`
- exact-head CI run: `33736633164`
- CI state: `PASS`
- merge commit on `main`: `3ac7a3281808db95d2db47dae8bed53395b62d8c`

The terminal result was persisted as top-level PR comment `5523796231` before merge without changing the reviewed HEAD. The merge then used `expected_head_sha=2fd1254d915363d6eb4720adacfebbce555e5ef9`; the resulting merge commit records the accepted exact head and terminal-result pointer.

Accepted PR #9 establishes:

- `data/bootstrap-commentary-reconciliation.json` as a separate governed layer rather than a rewrite of authenticated workbook/JSONL source projections;
- exact preservation of F050 as source `UNKNOWN`, without negative inference from absence;
- bounded F051 `SUPPORTED_MATERIAL_ADDRESS_EVIDENCE` for the workbook Notes claim that CAP follow-up PR #123 added hostile-caller output-ownership implementation/regression evidence;
- exact source/follow-up PR, commit, tree/parent, commit→PR and fixed-content bindings for that F051 claim;
- explicit separation between material follow-up evidence and universal semantic fix correctness;
- continued `global_commentary_reconciliation_complete=false`.

#### PR #9 review/remediation chronology

1. Exact head `64ee3a99c7bc9bf78115f4d7ab774c659a010cf4`
   - fresh independent review: `CURRENT FINDINGS` (1 P1);
   - defect: the declared PR #123 resulting commit was not uniquely bound; actual PR HEAD `09c58c4bc286a639662cd77432a54c3f08438ad7` could satisfy the old result predicates in place of intended result `e8bda851e9d810d0e007826693540ec1d4c71053`;
   - result became STALE when HEAD moved.

2. Remediation on final head `2fd1254d915363d6eb4720adacfebbce555e5ef9`
   - added an independent canonical default-branch ancestry discriminator for the declared result commits in this F051 evidence shape;
   - exact result `e8bda851e9d810d0e007826693540ec1d4c71053` is accepted only with the full conjunction of exact SHA/tree/parent/PR association plus canonical ancestry;
   - real alternate PR HEAD `09c58c4bc286a639662cd77432a54c3f08438ad7` is rejected as divergent;
   - adversarial test preserves the old predicates while substituting that real alternate head;
   - exact-head CI `33736633164`: PASS;
   - fresh independent terminal review: `CURRENT PASS`, 0 findings, 24 rejected candidates.

### Accepted exact-head clean re-review reconciliation — PR #10

PR #10 — `Stage 1: reconcile CAP #129 clean re-review evidence` established the accepted F052 evidence shape for an original finding, material final-head change, and exact-head clean Codex re-review without promoting that chain to universal semantic correctness.

Acceptance identity:

- BASE: `3ac7a3281808db95d2db47dae8bed53395b62d8c`
- accepted exact PR HEAD: `6569c6641574bc0d2d871a24e2d94faf6cb2bda4`
- `review_policy_ref`: `3ac7a3281808db95d2db47dae8bed53395b62d8c`
- changed files: `7`
- reviewer identity/class: `ordinary_chat_fresh`
- review mode: `read_only`
- terminal review validity: `CURRENT`
- terminal review status: `PASS`
- reported findings: `0`
- rejected candidates: `36`
- review timestamp: `2026-09-03T17:04:04+02:00`
- durable GitHub terminal-result comment id: `5527850500`
- exact-head CI run: `33763496281`
- CI state: `PASS`
- merge commit on `main`: `2b182584018e46aa90043cfc84d4a72ca7a9b2be`

The terminal result was persisted as top-level PR comment `5527850500` before merge without moving the reviewed HEAD. The merge used `expected_head_sha=6569c6641574bc0d2d871a24e2d94faf6cb2bda4`; the resulting merge commit records both the exact accepted HEAD and the durable terminal-result pointer.

Accepted PR #10 establishes:

- `data/bootstrap-commentary-rereview-reconciliation.json` as a separate bounded F052 layer tied to the authenticated workbook digest and normalized source identity;
- exact binding of original CAP PR #129 Codex review/finding on reviewed head `0dde5aab1725c076ff56e2d2c8662c842e57b8ae`;
- live final PR head `d6ea5bbd913d8a3ab27d7d1521d389e972602de2`, exact reviewed→fixed ancestry, immutable fixed-head contract-test evidence, exact owner reply/re-review request, exact Codex GitHub-App clean result and finality chronology;
- deliberate non-requirement that the reviewed branch head itself be on today's canonical-main ancestry, because the authenticated F052 claim is about the exact reviewed head rather than a resulting merge commit;
- explicit separation between a clean exact-head review result and universal semantic correctness;
- continued `global_commentary_reconciliation_complete=false`.

#### PR #10 review/remediation chronology

1. Exact head `c6e9896a01c0e4c258a78ad12789dedc1c14af1e`
   - fresh independent review: `CURRENT FINDINGS` (1 P2);
   - defect: the finality scan skipped an additional Codex-authored artifact when its relevant timestamp was missing/empty because timestamp parsing was guarded by truthiness;
   - result became STALE when HEAD moved.

2. Remediation on final head `6569c6641574bc0d2d871a24e2d94faf6cb2bda4`
   - timestamp validation became unconditional after an artifact is identified as Codex-authored and is not the declared clean-result comment;
   - missing/empty/malformed/timezone-naive chronology evidence now fails closed;
   - adversarial tests cover missing review `submitted_at`, inline-comment `created_at`, and issue-comment `created_at`;
   - exact-head CI `33763496281`: PASS;
   - fresh independent terminal review: `CURRENT PASS`, 0 findings, 36 rejected candidates.

### Accepted collector clean no-op and large-PR support — PR #12

PR #12 — `Stage 1: make collector clean no-op and support large PRs` closed the previously pending unchanged-source idempotence gate and the GitHub >250-commit source-collection boundary without changing bootstrap authority or consumer write permissions.

Acceptance identity:

- BASE: `2b182584018e46aa90043cfc84d4a72ca7a9b2be`
- accepted exact PR HEAD: `11b7166deed4c5dbb25a9bbe9bf0128bf5558dc7`
- `review_policy_ref`: `2b182584018e46aa90043cfc84d4a72ca7a9b2be`
- changed files: `3`
- reviewer identity/class: `ordinary_chat_fresh`
- review mode: `read_only`
- terminal review validity: `CURRENT`
- terminal review status: `PASS`
- reported findings: `0`
- rejected candidates: `10`
- review timestamp: `2026-09-03T18:55:46+02:00`
- durable GitHub terminal-result comment id: `5529178600`
- exact-head CI run: `33780251151`
- exact-head physical live no-op run: `33780251291`
- CI state: `PASS`
- merge commit on `main`: `8f31ddae0b5bc36dbd62b9e3c07eaae7d212c125`

The terminal result was persisted as top-level PR comment `5529178600` before merge without moving the reviewed HEAD. The merge then used `expected_head_sha=11b7166deed4c5dbb25a9bbe9bf0128bf5558dc7`; the resulting merge commit records the accepted exact head and terminal-result pointer.

Accepted PR #12 establishes:

- fail-closed complete commit collection for source PRs whose declared commit count exceeds GitHub's 250-commit pull-list cap, using exact paginated BASE...HEAD compare evidence bound to the validated PR identity;
- required agreement between the PR declared commit count, compare `total_commits`/`ahead_by`, stable compare identity across pages, unique valid commit SHAs, and exact final PR HEAD;
- preservation of the existing post-read PR identity fence, including equal-count force-push/movement rejection;
- no durable per-repository watermark/state advancement merely because wall-clock time passed when all selected source snapshots are byte-identical; the older watermark is retained conservatively so the next scan rechecks at least the same overlap interval;
- a read-only exact-head physical two-pass CAP/UV check in run `33780251291`: the first pass converged stale local evidence, while the later second pass returned `changed_files=0`, `state_changed=false`, zero CAP/UV changed snapshots, no watermark advancement, and an empty recursive byte diff;
- an explicit evidence-branch movement fence proving remote `evidence/github-intake` remained unchanged during the physical check, plus canonical-main verification before and after;
- continued read-only CAP/UV source-App permissions and no source-repository write authority.

The quiet-window attempt that motivated this PR first failed closed on live UV PR #89 with `declared=274 collected=250` and published nothing. The accepted repair then physically exercised that real 274-commit topology. The physical proof remains bounded evidence of the observed no-op interval and does not make the intake branch canonical adjudicated truth or claim universal completeness for every future GitHub topology.

### Accepted same-PR material-fix evidence reconciliation — PR #11

PR #11 — `Stage 1: reconcile UV #71 material fix evidence` established the accepted bounded F053/F054 same-PR material-fix evidence shape without turning owner prose, ancestry, tests, or later reviewer silence into universal semantic correctness.

Acceptance identity:

- BASE: `8f31ddae0b5bc36dbd62b9e3c07eaae7d212c125`
- accepted exact PR HEAD: `ced90521b6551b7a2f1f9d2c91e995fa289b722e`
- `review_policy_ref`: `8f31ddae0b5bc36dbd62b9e3c07eaae7d212c125`
- changed files: `7`
- reviewer identity/class: `ordinary_chat_fresh`
- review mode: `read_only`
- terminal review validity: `CURRENT`
- terminal review status: `PASS`
- reported findings: `0`
- rejected candidates: `14`
- review timestamp: `2026-09-03T20:19:52+02:00`
- durable GitHub terminal-result comment id: `5530313338`
- exact-head/current-base CI run: `33785860217`
- CI state: `PASS`
- accepted literal-head / PR-merge Git tree: `884b851f18fe29c01827508de8e579d7c8b5b211`
- merge commit on `main`: `552641edb5f76720d176dca67d347b51963aca65`

The terminal result was persisted as top-level PR comment `5530313338` before merge without moving the reviewed HEAD. The merge used `expected_head_sha=ced90521b6551b7a2f1f9d2c91e995fa289b722e`; the resulting merge commit records the accepted exact head and terminal-result pointer.

Accepted PR #11 establishes:

- `data/bootstrap-commentary-fix-evidence-reconciliation.json` as a separate F053/F054 governed layer tied to the authenticated workbook digest and normalized source rows;
- exact original Codex review/finding identity for each entry and historical-head binding through the exact review submission plus `original_commit_id`;
- bounded acceptance of GitHub's mutable historical inline-comment relocation only when current `commit_id` equals the original reviewed head or live final PR head;
- exact owner reply/thread/actor/PR/full-SHA binding;
- exact same-PR fix-commit membership and reviewed→fix ancestry;
- exact fix-commit changed-file inventory and immutable fix-head implementation/regression assertions;
- explicit `SUPPORTED_SAME_PR_MATERIAL_FIX_EVIDENCE` semantics narrower than universal semantic correctness;
- continued `global_commentary_reconciliation_complete=false`.

#### PR #11 review/remediation chronology

1. Exact head `d0bdffccfaa6a39dc588006aaf0507115c0b2910`
   - fresh independent review: `CURRENT FINDINGS` (1 acceptance blocker);
   - semantic F053/F054 evidence model otherwise passed;
   - blocker: after PR #12 moved accepted `main`, the PR branch remained divergent, so pull-request CI exercised a synthetic merge tree different from literal accepted HEAD and exact-head CI was not proven;
   - result became STALE when HEAD moved.

2. Remediation on final head `ced90521b6551b7a2f1f9d2c91e995fa289b722e`
   - accepted `main=8f31ddae0b5bc36dbd62b9e3c07eaae7d212c125` was merged into the PR branch without changing the seven-file BASE..HEAD content scope;
   - BASE became the exact merge base, compare status `ahead`, and `behind_by=0`;
   - literal HEAD Git tree and GitHub PR synthetic merge-ref tree both resolved exactly to `884b851f18fe29c01827508de8e579d7c8b5b211`;
   - exact-head/current-base CI `33785860217`: PASS;
   - fresh independent terminal review: `CURRENT PASS`, 0 findings, 14 rejected candidates.

### Accepted same-PR material-fix-baseline reconciliation — PR #13

PR #13 — `Stage 1: reconcile UV #71 F058 fix baseline evidence` established the accepted bounded F058 same-PR material-fix-baseline evidence shape.

Acceptance identity:

- BASE: `552641edb5f76720d176dca67d347b51963aca65`
- accepted exact PR HEAD: `6de0ba27b80be5760bce1cbf126a8061425caf34`
- `review_policy_ref`: `552641edb5f76720d176dca67d347b51963aca65`
- changed files: `7`
- reviewer identity/class: `ordinary_chat_fresh`
- review mode: `read_only`
- terminal review validity: `CURRENT`
- terminal review status: `PASS`
- reported findings: `0`
- durable GitHub terminal-result comment id: `5538687060`
- exact-head/current-base CI run: `33857606647`
- CI state: `PASS`
- accepted literal-head / PR-merge Git tree: `45aab0e917e666ab65c82d952b5e93ac1afba749`
- merge commit on `main`: `9197cde51c3b9ddd4004ce62f09f38c8b79589c1`

The terminal result was persisted as top-level PR comment `5538687060` before merge without moving the reviewed HEAD. The merge used `expected_head_sha=6de0ba27b80be5760bce1cbf126a8061425caf34`; the resulting merge commit records the accepted exact head and terminal-result pointer.

Accepted PR #13 establishes:

- `data/bootstrap-commentary-fix-baseline-reconciliation.json` as a separate F058 governed layer;
- exact original UV PR #71 Codex review/finding and owner-reply identities;
- exact reviewed head `aafddd3b37476a65558d56755edd2ae440648b74` and owner-declared code-bearing baseline `9af22cdcbb60501dca968fd10f12dc1d40ee6482`;
- exact contiguous four-commit reviewed→baseline sequence and exact four-file range inventory;
- immutable baseline implementation/regression evidence for exact harness/Project Store/planner authority matching, including rejection of a foreign store with the same project ID;
- explicit `SUPPORTED_SAME_PR_MATERIAL_FIX_BASELINE_EVIDENCE` semantics narrower than universal semantic correctness;
- continued `global_commentary_reconciliation_complete=false` and explicit F057 pending status.

#### PR #13 review/remediation chronology

1. Exact head `0e912451ef728f65d585f0911058c5cfb913f011`
   - fresh independent review: `CURRENT FINDINGS` (1);
   - defect: `data/README.md` named the already-accepted F053/F054 verifier using a nonexistent hyphenated path rather than `tools/verify_bootstrap_commentary_fix_evidence_reconciliation.py`;
   - substantive F058 evidence model otherwise passed;
   - result became STALE when HEAD moved.

2. Remediation on final head `6de0ba27b80be5760bce1cbf126a8061425caf34`
   - net content delta from the previously reviewed head was exactly the one documentation-path correction;
   - exact-head/current-base CI `33857606647`: PASS;
   - literal HEAD and PR merge-ref tree both resolved to `45aab0e917e666ab65c82d952b5e93ac1afba749`;
   - fresh independent terminal review: `CURRENT PASS`, 0 findings.

Stage 1 continues under the normal accepted-BASE repository-development review policy. PR #1's no-policy bootstrap exception is no longer available. Material source commentary remains only partially reconciled; F057 and other material commentary remain pending, reviewer-policy refs and generic/project-specific classification remain unresolved, and no baseline seed exists.

## Track R — Independent review-job coordination

### Accepted coordination-boundary research — PR #14

PR #14 — `Research: define generic review-job coordination boundary` established an accepted non-authoritative research basis for deciding whether MimiSeek can coordinate independent review execution without taking ownership of consumer development/fix/merge workflows.

Acceptance identity:

- BASE: `9197cde51c3b9ddd4004ce62f09f38c8b79589c1`
- accepted exact PR HEAD: `21f82632c835e21fa1ce28ad846111c1f7f61c56`
- `review_policy_ref`: `9197cde51c3b9ddd4004ce62f09f38c8b79589c1`
- changed files: `1`
- reviewer identity/class: `ordinary_chat_fresh`
- review mode: `read_only`
- terminal review validity: `CURRENT`
- terminal review status: `PASS`
- reported findings: `0`
- durable GitHub terminal-result comment id: `5540017840`
- exact-head/current-base CI run: `33863052423`
- CI state: `PASS`
- accepted literal-head / PR-merge Git tree: `8346d7f4b84636936b9d5986e0f656fe28ad4424`
- merge commit on `main`: `eb5c53dec64dbe169623c061afe05a19bdb15410`

The terminal result was persisted as top-level PR comment `5540017840` before merge without moving the reviewed HEAD. The merge used `expected_head_sha=21f82632c835e21fa1ce28ad846111c1f7f61c56`; the resulting merge commit records the accepted exact head and terminal-result pointer.

Accepted PR #14 establishes only research evidence:

- the proposed narrow split keeps consumer readiness, local policy, finding adjudication, remediation, re-review and merge consequences with the consumer;
- MimiSeek is only a candidate generic review-job coordinator;
- CAP/session execution remains generic and must not acquire UV/MimiSeek/CAP project semantics, GitHub PR semantics, or PASS/FINDINGS meaning;
- a fresh Temporary Chat remains the independent reviewer;
- GitHub is proposed as durable review-job/result handoff while private session authority remains outside public job state;
- exact job/result correlation, stale-head handling, idempotence, and no-blind-duplicate launch/wake are required;
- the fast review-job loop remains separate from slow reviewer evolution/promotion;
- the research itself changed no production authority and required a later governed `ACCEPT_NARROW | REJECT | DEFER` architecture decision.

The architecture decision that follows this research is recorded separately by ADR 0013 and its own repository-development PR/acceptance evidence; PR #14 by itself is not that authority.

### Accepted narrow review-job coordination architecture — PR #15

PR #15 — `Architecture: accept narrow independent review-job coordination` selected `ACCEPT_NARROW` and synchronized the canonical MimiSeek product/architecture/integration/development/roadmap boundary without implementing the review-job runtime or changing any consumer repository.

Acceptance identity:

- BASE: `eb5c53dec64dbe169623c061afe05a19bdb15410`
- accepted exact PR HEAD: `1cea12430d2eb19b08ab6f53a00ecccc036e0982`
- `review_policy_ref`: `eb5c53dec64dbe169623c061afe05a19bdb15410`
- changed files: `12`
- reviewer identity/class: `ordinary_chat_fresh`
- review mode: `read_only`
- terminal review validity: `CURRENT`
- terminal review status: `PASS`
- reported findings: `0`
- durable GitHub terminal-result comment id: `5541238884`
- exact-head/current-base CI run: `33870791675`
- CI state: `PASS`
- accepted literal-head / PR-merge Git tree: `fa408fd9adc6bb7d46dd8e455783d58cf7644fdd`
- merge commit on `main`: `ca16428e66d2f9e4d5de2e359e0e369a4f334fce`

The terminal result was persisted as top-level PR comment `5541238884` before merge without moving the reviewed HEAD. The merge used `expected_head_sha=1cea12430d2eb19b08ab6f53a00ecccc036e0982`; the resulting merge commit records the accepted exact head and terminal-result pointer.

Accepted PR #15 establishes:

- ADR 0013 `ACCEPT_NARROW` as the canonical authority permitting explicitly requested, immutable, project-neutral independent-review job coordination;
- continued consumer ownership of review readiness, project-local policy, finding adjudication, remediation, re-review, terminal acceptance, and merge consequences;
- a generic CAP/session boundary that must not acquire UV/CAP/MimiSeek project routing, GitHub PR, or `PASS`/`FINDINGS` semantics;
- public/private return-route separation and continued read-only CAP/UV source-App permissions;
- Track R as a cross-cutting implementation path distinct from reviewer evolution/promotion/distribution;
- no claim that generic external fresh-worker or existing-session return-delivery capabilities are already accepted, and no live external launch/wake authority before those exact prerequisites are independently resolved.

Post-merge development of PR #16 discovered that `tests/test_review_job_coordination_boundary.py` in the accepted #15 HEAD used pytest-style free functions while repository CI invokes `python -m unittest discover`, so that newly added file was not executed by the #15 unit job. This index does not retroactively claim otherwise. The exact #15 architecture was still independently reviewed semantically and accepted under its BASE-governed process; PR #16 converts that boundary test to real `unittest.TestCase` discovery and exercises it as new development evidence.

## Later stages

Add entries only when evidence exists. Do not pre-fill imagined CI/review IDs.
