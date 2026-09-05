# Data

This directory contains MimiSeek Review's canonical machine-readable **bootstrap** datasets plus their versioned contracts. Later operational learning/outcome data will use separate governed Stage-3/Stage-4 stores and schemas; it must not be appended to the authenticated bootstrap-v1 files.

Non-authoritative live GitHub intake is stored separately on branch `evidence/github-intake`; it is source evidence, not canonical adjudicated truth.

## Bootstrap source

The audited historical CAP/UV reviewer-statistics workbook used to bootstrap Stage 1 is durably identified by `data/bootstrap-source.json`.

That manifest is the sole owner of the exact access-controlled Library path/version, byte size, SHA-256, recovery contract, and declared BUGGY→FIXED reconciliation target. A fresh authorized chat must recover that exact artifact and verify the manifest before trusting a bootstrap import. Failure to recover/authenticate it is fail-closed.

The workbook remains the authenticated lossless source/provenance artifact for Stage 1, not the ongoing automation store.

## Canonical normalized bootstrap datasets

Stage 1 projects the authenticated workbook into deterministic JSON Lines datasets used for governed bootstrap analysis:

- `review-runs.jsonl` — normalized historical reviewer executions and exact review identity;
- `findings.jsonl` — normalized historical finding observations, disposition fields, and source identity;
- `regression-cases.jsonl` — historical BUGGY→FIXED target cases and evidence refs.

These JSONL files are **normalized semantic projections, not column-lossless workbook clones**. Their positional field contracts and explicit source-projection rules are versioned under `data/schemas/`.

For `Review Runs`, workbook `PR title` is descriptive GitHub metadata recoverable from the exact source PR. Workbook `Notes` is non-authoritative analyst/source commentary. For `Findings`, workbook `Notes` has the same non-authoritative commentary role. Those omitted columns are deliberately not promoted into canonical evidence merely because they were populated. Every normalized tuple retains `source_row`, so the exact authenticated workbook row is recoverable through `data/bootstrap-source.json + source_row`. Any material adjudication/fix/provenance assertion that exists only in source commentary must be reconciled against governed GitHub evidence and represented in the later canonical provenance model **before the Stage-1 baseline seed may be derived**.

This distinction is intentional: source commentary must not silently become ground truth, but it also must not become unreachable. The immutable workbook identity plus `source_row` preserves deterministic recovery while provenance reconciliation proceeds.

`data/bootstrap-import-report.json` records source authentication, counts, hashes, internal reconciliation, and explicitly unfinished provenance work. It is derived verification evidence, not a competing source-identity owner.

For numeric review-run metrics, `null` means the authenticated workbook cell was blank/unknown. Literal `0` means the source explicitly recorded zero. Bootstrap import must not convert a blank metric into numerical evidence.

The three bootstrap-v1 files are additionally pinned by fixed source-reconciliation record counts, byte lengths, and SHA-256 digests in `tests/test_bootstrap_data_integrity.py`. Those anchors are intentionally independent of the mutable import report. Changing an anchored bootstrap dataset requires an explicit new authenticated source reconciliation/version and fresh semantic acceptance; operational records must use a separate schema/store rather than being appended after the anchored rows.

`learning-events.jsonl` does not exist yet. Learning events belong to Stage 4 and must not be fabricated during bootstrap.

## Structural commit provenance reconciliation

`tools/verify_bootstrap_commit_provenance.py` checks the 84 imported regression cases against live read-only GitHub evidence. The regression corpus currently spans **9 source PRs**: six CAP PRs and three UV PRs. This is narrower than the wider PR identity scope present elsewhere in the authenticated bootstrap import and must not be described as 21 regression-source PRs.

The normal provenance path requires:

- exact regression-case ↔ finding identity and source-URL agreement;
- immutable repository/PR identity agreement with the live source snapshot;
- BUGGY, FIXED, and VERIFIED heads to occur in the final source PR commit history;
- ancestry `BUGGY BASE → BUGGY HEAD → FIX HEAD → VERIFIED HEAD`;
- VERIFIED HEAD to remain in the ancestry of the live/final PR head.

A fail-closed live run exposed one authenticated-source lineage conflict rather than silently normalizing it away: seven cases `RC-CAP124-047` through `RC-CAP124-053` refer to the exact Codex-reviewed historical CAP PR #124 head `48d2e89c3b2fee9053b5038c093ad5060124b2ce`, while the workbook's `BUGGY BASE` belongs to the later rebased lineage. GitHub preserves the detached reviewed commit, its actual parent, the exact Codex review submission/comments bound to that commit, and owner replies recording the rebase/fix transition.

The governed exception is recorded in `data/bootstrap-provenance-reconciliation.json`. It does **not** rewrite `regression-cases.jsonl` or `findings.jsonl`: those remain immutable authenticated-source projections. The exception must match the exact seven case IDs, repository/PR identity, source values, historical reviewed head and parent, rebased lineage anchor, review request, Codex review identity, original review-comment identities, and the exact owner-review submissions that bind the rebased response anchor. Unlisted or mismatched lineage conflicts fail closed.

The structural verifier therefore has two explicit modes:

- `linear_pr_history` — 77 cases;
- `reviewed_head_rebased_before_fix` — 7 CAP PR #124 cases.

The accepted implementation target is structural provenance only. A PASS means that imported commit identities, exact PR-bound review evidence, and declared ancestry/rebase structure are supported by live GitHub evidence. It **does not** prove that a fix is semantically correct merely because a later commit descends from an earlier one or because an owner reply says “fixed”. Material source-commentary/disposition claims still require separate governed reconciliation before baseline derivation.

CI runs the verifier with the same dedicated source GitHub App restricted to read-only CAP/UV access. The verification path writes nothing to either consumer repository.

## Bounded source-commentary reconciliation

`data/bootstrap-commentary-reconciliation.json` is a separate governed reconciliation layer for material assertions recovered from authenticated workbook commentary. It is not a replacement for the workbook and does not modify or supersede `review-runs.jsonl`, `findings.jsonl`, or `regression-cases.jsonl`.

The first bounded slice covers only CAP PR #121 findings `F050` and `F051` from the workbook `Findings` sheet:

- `F050` remains source `UNKNOWN`. The reconciliation binds its exact normalized source row, reviewed HEAD, Codex review, and original inline finding, but intentionally asserts no follow-up. `PRESERVED_UNKNOWN` means no positive/negative absence inference is made.
- `F051` retains the authenticated source disposition while reconciling only its material Notes claim that follow-up PR #123 added the hostile-caller output-ownership implementation/regression evidence. The reconciliation binds exact source/follow-up repository and PR identities, source reviewed HEAD, PR #121 merge commit as PR #123 BASE, exact PR #123 HEAD/merge commit, exact changed-file inventory, and immutable-head file-content assertions for the fake-caller verifier and owned Playwright-output path.

`tools/verify_bootstrap_commentary_reconciliation.py` verifies those bindings against live GitHub through the same read-only source App used for structural provenance. It also binds the reconciliation document to the exact bootstrap workbook SHA-256 from `data/bootstrap-source.json` and binds each entry to the normalized finding/source-row identity.

For these historical PR reads, the scoped source GitHub App exposes `base`, `head`, and `merged_at` but redacts `pull.merge_commit_sha` to `null`. The verifier therefore does not treat that unavailable field as either evidence or absence. Instead it proves the declared resulting commits through four independent GitHub/Git constraints: exact Git object identity, the expected tree/parent structure, exact commit→PR association, and membership on the repository's current canonical default-branch ancestry. For #121, the declared resulting commit must match the exact reviewed #121 HEAD tree, be associated with PR #121, and be an ancestor of the current default branch. For #123, the declared resulting commit must have the declared #121 result as its sole parent, match the exact #123 HEAD tree, be associated with PR #123, and be an ancestor of the current default branch. A PR HEAD with equivalent content that is not on canonical default-branch ancestry is rejected.

The status `SUPPORTED_MATERIAL_ADDRESS_EVIDENCE` is intentionally narrower than “fixed” or “semantically correct”. It means the exact material source-note claim about the existence/content of the follow-up implementation/regression is supported by immutable GitHub evidence. It does **not** infer semantic repair from owner prose, merge state, ancestry, or test success alone.

The accepted F050/F051 reconciliation document declares `global_commentary_reconciliation_complete=false`. That bounded slice must not be used to claim that all material workbook commentary/disposition assertions are reconciled.

### Bounded fixed-head + clean re-review reconciliation

`data/bootstrap-commentary-rereview-reconciliation.json` uses a separate strict schema for a different evidence shape: an original finding is materially changed on the live final PR head and a later exact-head Codex re-review reports no remaining major issues.

The first such slice covers only `F052` from CAP PR #129. The authenticated source note says `Fixed; final exact-head Codex re-review reported no remaining major issues.` The verifier binds that bounded claim to:

- exact normalized F052/source-row identity and the original Codex review/inline P2 on reviewed head `0dde5aab1725c076ff56e2d2c8662c842e57b8ae`;
- live merged PR #129 final head `d6ea5bbd913d8a3ab27d7d1521d389e972602de2` as an exact descendant of the reviewed head;
- exact owner reply to the original finding and exact owner re-review request naming the full final head;
- the exact Codex GitHub-App clean-result comment whose `Reviewed commit` prefix matches that final head;
- evidence chronology and absence of any later Codex-authored review evidence before merge;
- exact final three-file PR inventory and immutable final-head contract-test text that checks the complete screenshot-after-every-action negation rather than only a keyword.

This evidence shape deliberately does **not** require the final reviewed PR head itself to be an ancestor of today's canonical `main`. Live history for PR #129 is divergent after the PR's merge mechanics, and the authenticated source claim is about an exact-head review result, not about the reviewed branch SHA becoming the canonical merge/result commit. The fixed-head identity is instead bound directly to the live final merged-PR head, exact reviewed→fixed ancestry, immutable fixed-head content, and the clean Codex result for that same head.

`SUPPORTED_FIXED_AND_CLEAN_REREVIEW_EVIDENCE` is still narrower than universal semantic correctness. It establishes that the exact authenticated source-note claim about the fixed-head material change and clean exact-head Codex re-review is supported by live evidence. It does not turn owner prose, merge state, or a clean reviewer result into a general proof that no defect exists.

This F052 slice also declares `global_commentary_reconciliation_complete=false`; remaining material commentary stays pending before baseline derivation.

### Bounded same-PR material-fix evidence reconciliation

`data/bootstrap-commentary-fix-evidence-reconciliation.json` introduces a third bounded commentary evidence shape for authenticated Notes that point to a material fix inside the same source PR without relying on later reviewer silence as proof of repair.

The accepted slice is exactly UV PR #71 findings `F053` and `F054`, both originally reviewed on `238870958fb88a291cdfa3e2345d8c5d84821534`. For each entry, `tools/verify_bootstrap_commentary_fix_evidence_reconciliation.py` requires:

- exact normalized finding/source-row identity and exact Codex review submission;
- exact original inline finding with immutable `original_commit_id` binding to the reviewed head;
- an exact owner reply to that original thread naming the full declared same-PR fix commit;
- the declared fix commit to be present in the exact PR commit history and to descend exactly from the reviewed head;
- exact fix-commit changed-file inventory;
- immutable fix-head implementation/regression text materially corresponding to the source Note.

GitHub may relocate an old inline comment's current `commit_id` onto the merged PR's later final head. This mutable relocation is not treated as the historical reviewed-head authority: the exact review submission plus `original_commit_id` provide that binding. The verifier still rejects an arbitrary relocated commit by allowing the current `commit_id` only when it is either the original reviewed head or the live final PR head.

`SUPPORTED_SAME_PR_MATERIAL_FIX_EVIDENCE` means that the exact owner-declared fix commit contains implementation/regression evidence materially corresponding to the authenticated source Note. It does not mean that ancestry, owner prose, tests, or absence of a repeated finding proves universal semantic correctness. The F053/F054 document also keeps `global_commentary_reconciliation_complete=false`.

### Bounded same-PR material-fix baseline reconciliation

`data/bootstrap-commentary-fix-baseline-reconciliation.json` introduces a separate strict shape for a source Note whose exact owner reply names a **code-bearing baseline head** rather than one exact implementation commit. This distinction is important: a baseline can span several commits, so the verifier must not pretend that the final named baseline commit itself owns all implementation/test changes.

The accepted first slice covers only UV PR #71 finding `F058`, originally reviewed on `aafddd3b37476a65558d56755edd2ae440648b74`. The authenticated Note is `Fixed with exact harness/store/planner authority checks.` The exact owner reply names baseline `9af22cdcbb60501dca968fd10f12dc1d40ee6482`.

`tools/verify_bootstrap_commentary_fix_baseline_reconciliation.py` therefore requires:

- exact normalized F058/source-row identity and exact Codex review/inline finding;
- immutable historical reviewed-head binding through the exact review submission and `original_commit_id`, with any mutable current `commit_id` limited to the reviewed head or live final PR head;
- exact owner reply to the exact original finding, exact PR owner/PR binding, and the full declared baseline SHA in the reply body;
- the baseline head to be a commit of the exact source PR and an exact descendant of the reviewed head;
- the exact ordered reviewed→baseline commit sequence, not merely endpoint ancestry;
- the exact changed-file inventory across that complete compare range;
- immutable baseline-head implementation/regression content materially corresponding to F058.

`SUPPORTED_SAME_PR_MATERIAL_FIX_BASELINE_EVIDENCE` means only that the exact owner-declared same-PR baseline contains materially corresponding implementation/regression evidence over the exact governed range. It does not infer universal semantic correctness from owner prose, ancestry, tests, CI, or later reviewer silence. The F058 document keeps `global_commentary_reconciliation_complete=false`.

### Bounded same-PR multi-review progression reconciliation

`data/bootstrap-commentary-multi-review-progression-reconciliation.json` introduces a separate strict shape for an authenticated source Note that spans an initial bounded fix and later stronger findings on newer reviewed heads in the **same source PR**.

The first slice covers only root finding `F057` from UV PR #71. Its authenticated Note is `Fixed by complete typed delegation matching and later stronger namespace reservation.` The verifier preserves three distinct normalized findings rather than collapsing them:

- `F057` on reviewed head `aafddd3b37476a65558d56755edd2ae440648b74` binds the original prefix-only classification finding, the exact owner reply naming response head `9af22cdcbb60501dca968fd10f12dc1d40ee6482`, reviewed→response ancestry, and immutable response-head code/test evidence for complete typed matching and the prefix-like canonical-ID regression;
- later distinct `F059` on reviewed head `10643bd160c65b8d8df690266390725d5d0dd6eb` binds the stronger complete-typed namespace-collision finding and exact owner response head `7c8280721d96e7822d3c56e08e00ff6cb3868349`, including immutable reservation code/test evidence;
- later distinct `F061` on reviewed head `7c8280721d96e7822d3c56e08e00ff6cb3868349` binds the further proposal-created namespace-collision finding and exact owner response code/docs head `1467bd3c97511f8349b574d00a6029e8e98b3fe7`, including immutable proposal-output validation and regression evidence.

`tools/verify_bootstrap_commentary_multi_review_progression_reconciliation.py` requires exact normalized source rows, exact Codex review/comment identities, exact owner replies to the corresponding original comments, exact response heads in source-PR history, reviewed→response ancestry/termination, bounded compare evidence, and immutable response-head content. Its cross-stage ordering check separately re-reads and validates the exact GitHub source-PR commit sequence rather than using the timestamp-sorted compact snapshot as ordering authority.

`SUPPORTED_SAME_PR_MULTI_REVIEW_PROGRESSION_EVIDENCE` means only that the authenticated F057 note's two-part progression is supported while `F057`, `F059`, and `F061` remain separate findings bound to separate reviewed heads. Later stronger findings broaden the observed namespace-risk progression; they are not automatically the same defect identity and do not retroactively erase the bounded evidence for the earlier response. The relation labels in this Stage-1 document are evidence descriptors only and do not instantiate the future `FINDING_V1` lifecycle research plan. Owner prose, ancestry, tests, CI, and later reviewer silence remain insufficient for universal semantic correctness.

The F057 progression document also keeps `global_commentary_reconciliation_complete=false`; remaining material commentary stays pending before baseline derivation.

### Bounded historical authority + exact-head CI reconciliation

`data/bootstrap-commentary-authority-ci-reconciliation.json` introduces a separate strict shape for two distinct authenticated findings on the same historical reviewed head where one source Note concerns synchronization of historical current-authority documents and the other concerns refreshed exact-head CI evidence.

The first slice covers distinct UV PR #71 findings `F055` and `F056`, both originally reviewed on `aafddd3b37476a65558d56755edd2ae440648b74` under Codex review `5043917353`:

- `F055` binds exact inline finding `3874358302` and owner reply `3874609972`, the exact four-commit reviewed→code/docs range ending at `9af22cdcbb60501dca968fd10f12dc1d40ee6482`, exact range inventory, immutable `CURRENT_ARCHITECTURE.md` / `UV_STUDIO_V2_ARCHITECTURE_MAP.md` text that changes the historical Stage-17 classification from `NEXT`/idle to `ACTIVE REVIEW`, and the one-commit metadata update to `10643bd160c65b8d8df690266390725d5d0dd6eb`;
- `F056` independently binds exact inline finding `3874358316` and owner reply `3874610894`, the exact code→metadata range, and historical PR CI #3488/run `33101350599` on code head `9af22cdc...` plus PR CI #3490/run `33102045907` on metadata head `10643bd...`.

`tools/verify_bootstrap_commentary_authority_ci_reconciliation.py` keeps the source GitHub App limited to its existing read-only Contents/Issues/Pull-requests scope. It resolves historical public UV Actions runs through a separate unauthenticated public GitHub client and requires exact repository, workflow, PR event, run number, head SHA, completed-success state, and the exact five unique successful permanent jobs for each declared run. Historical inline-comment `original_commit_id` plus the exact review submission remain the immutable reviewed-head binding; mutable current `commit_id` relocation is accepted only when that relocated commit is a member of the exact source PR.

`SUPPORTED_SAME_PR_AUTHORITY_SYNC_EVIDENCE` means only that the authenticated F055 Note's historical synchronization claim is supported by the exact bounded Git/review/content evidence. It does not make those historical `CURRENT` documents present-day authority. `SUPPORTED_EXACT_HEAD_CI_REFRESH_EVIDENCE` means only that the authenticated F056 Note's two exact historical CI runs and metadata record are supported. CI is execution evidence, not semantic correctness proof. F055 and F056 remain separate finding identities, and the document keeps `global_commentary_reconciliation_complete=false`.

## Continuous GitHub evidence intake

The bounded Stage 1 intake foundation polls repositories registered in `config/consumers.json` and stores deterministic per-PR source snapshots on branch:

`evidence/github-intake`

Typical path:

`evidence/github/<owner>/<repo>/pulls/<pr-number>.json`

Each snapshot preserves PR identity/BASE/HEAD, issue comments, PR-level reactions, PR reviews, inline review comments with GitHub reaction summaries, and PR commit history. Collector state/watermarks live alongside those snapshots on the intake branch. For a PR whose declared commit count exceeds GitHub's 250-commit pull-list cap, the accepted collector obtains the exact commit sequence through paginated BASE...HEAD comparison and fails closed on inconsistent count, compare identity, duplicate SHAs, source movement, or failure to terminate at the exact PR HEAD.

Every open PR is refreshed on each scheduled run because GitHub reactions do not reliably advance the PR/issue `updated_at` timestamp. Closed-PR refresh uses the configured backfill/watermark overlap; the initial collector is source preservation infrastructure, not yet the complete Stage 3 normalized outcome store.

The intake branch is deliberately **non-authoritative**:

- it preserves source GitHub facts/comments/reviews/reactions/commits;
- it does not decide that a finding is confirmed merely because text says so;
- it does not interpret a `+1` reaction as PASS without later governed reviewer-identity/timing normalization;
- it does not convert absence into a reviewer miss;
- it does not create learning events, candidate state, stable state, or promotion authority;
- it may overlap the bootstrap workbook and later normalization must deduplicate by immutable GitHub/source identity.

The collector is implemented by `tools/collect_github_evidence.py` and scheduled by `.github/workflows/collect-review-evidence.yml`. Reliable scheduled operation requires both the dedicated read-only CAP/UV GitHub App credentials **and** server-enforced protection of MimiSeek's canonical `main` ref. The repository write token used by the intake workflow is repository-scoped, so the workflow must remain disabled unless an active ruleset named `mimiseek-canonical-main` protects the default branch with no bypass actor and requires pull requests while blocking deletion and non-fast-forward updates. The workflow verifies that boundary before collection/push; terminal acceptance must independently re-resolve the live GitHub rule rather than trusting workflow shell intent.

The first authenticated backfill is durable on `evidence/github-intake`. Accepted PR #12 subsequently closed two collector boundaries exposed by a quiet-source control: UV PR #89 exceeded GitHub's 250-commit pull-list cap, and the prior implementation advanced durable collector-state timestamps even when all selected snapshots were byte-identical. The accepted implementation uses paginated exact BASE...HEAD comparison for >250-commit PRs and leaves per-repository durable watermark/state unchanged on a real no-op. Its exact-head physical two-pass CAP/UV run first converged stale local evidence and then, after wall-clock time advanced, produced `changed_files=0`, `state_changed=false`, zero changed snapshots, no watermark advancement, an empty recursive byte diff, and an unchanged remote intake ref. This is the accepted clean unchanged-source no-op/idempotence proof; it does not promote the intake branch into canonical adjudicated truth.

Stage 2 will add the structured consumer evidence-export contract required to make fresh ordinary-ChatGPT terminal results automatically recoverable from consumer GitHub state. Stage 3 will complete normalized operational collector/outcome-store semantics.

## Rules

- Source evidence remains traceable to exact repository/PR/comment/review/reaction/commit identities.
- Bootstrap imports and evidence collection are idempotent.
- Unknown stays unknown.
- Different HEADs are not silently collapsed into direct reviewer comparisons.
- Generated reports and raw intake snapshots do not become competing truth owners.
- Incomplete/truncated API evidence fails closed.
- Bootstrap-v1 datasets are immutable authenticated-source projections, not append targets for operational records.
- A discovered source-lineage conflict is represented in a separate governed reconciliation layer; it is not silently repaired by mutating the source projection.
- Source commentary omitted from normalized tuples remains recoverable by manifest + `source_row`; material assertions from it must be provenance-reconciled before baseline derivation.
- Bounded source-commentary reconciliation must explicitly state its coverage and may not claim global completion.
- A multi-review progression must preserve each distinct finding identity and reviewed head; stronger later findings are not silently collapsed into the earlier finding.
- Historical authority synchronization and exact-head CI refresh evidence must remain separate finding claims; CI success and historical `CURRENT` document labels are not present-day semantic authority.
- Preserved source `UNKNOWN` is not evidence that later proof does or does not exist.
- Structural commit provenance, material follow-up evidence, clean exact-head re-review evidence, same-PR material-fix evidence, same-PR material-fix baseline evidence, same-PR multi-review progression evidence, historical authority synchronization, and exact-head CI evidence do not by themselves equal universal semantic fix correctness.
- A baseline seed may not be derived merely because files exist; Stage 1 provenance/policy/classification/current-intake requirements must also be satisfied.