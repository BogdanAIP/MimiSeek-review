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

This distinction is intentional: source commentary must not silently become ground truth, but it also must not become unreachable. The immutable workbook identity plus `source_row` preserves deterministic recovery while commit-level/source provenance reconciliation remains explicitly unfinished.

`data/bootstrap-import-report.json` records source authentication, counts, hashes, internal reconciliation, and explicitly unfinished provenance work. It is derived verification evidence, not a competing source-identity owner.

For numeric review-run metrics, `null` means the authenticated workbook cell was blank/unknown. Literal `0` means the source explicitly recorded zero. Bootstrap import must not convert a blank metric into numerical evidence.

The three bootstrap-v1 files are additionally pinned by fixed source-reconciliation record counts, byte lengths, and SHA-256 digests in `tests/test_bootstrap_data_integrity.py`. Those anchors are intentionally independent of the mutable import report. Changing an anchored bootstrap dataset requires an explicit new authenticated source reconciliation/version and fresh semantic acceptance; operational records must use a separate schema/store rather than being appended after the anchored rows.

`learning-events.jsonl` does not exist yet. Learning events belong to Stage 4 and must not be fabricated during bootstrap.

## Continuous GitHub evidence intake

The bounded Stage 1 intake foundation polls repositories registered in `config/consumers.json` and stores deterministic per-PR source snapshots on branch:

`evidence/github-intake`

Typical path:

`evidence/github/<owner>/<repo>/pulls/<pr-number>.json`

Each snapshot preserves PR identity/BASE/HEAD, issue comments, PR-level reactions, PR reviews, inline review comments with GitHub reaction summaries, and PR commit history. Collector state/watermarks live alongside those snapshots on the intake branch.

Every open PR is refreshed on each scheduled run because GitHub reactions do not reliably advance the PR/issue `updated_at` timestamp. Closed-PR refresh uses the configured backfill/watermark overlap; the initial collector is source preservation infrastructure, not yet the complete Stage 3 normalized outcome store.

The intake branch is deliberately **non-authoritative**:

- it preserves source GitHub facts/comments/reviews/reactions/commits;
- it does not decide that a finding is confirmed merely because text says so;
- it does not interpret a `+1` reaction as PASS without later governed reviewer-identity/timing normalization;
- it does not convert absence into a reviewer miss;
- it does not create learning events, candidate state, stable state, or promotion authority;
- it may overlap the bootstrap workbook and later normalization must deduplicate by immutable GitHub/source identity.

The collector is implemented by `tools/collect_github_evidence.py` and scheduled by `.github/workflows/collect-review-evidence.yml`. Reliable scheduled operation requires both the dedicated read-only CAP/UV GitHub App credentials **and** server-enforced protection of MimiSeek's canonical `main` ref. The repository write token used by the intake workflow is repository-scoped, so the workflow must remain disabled unless an active ruleset named `mimiseek-canonical-main` protects the default branch with no bypass actor and requires pull requests while blocking deletion and non-fast-forward updates. The workflow verifies that boundary before collection/push; terminal acceptance must independently re-resolve the live GitHub rule rather than trusting workflow shell intent.

Stage 2 will add the structured consumer evidence-export contract required to make fresh ordinary-ChatGPT terminal results automatically recoverable from consumer GitHub state. Stage 3 will complete normalized operational collector/outcome-store semantics.

## Rules

- Source evidence remains traceable to exact repository/PR/comment/review/reaction/commit identities.
- Bootstrap imports and evidence collection are idempotent.
- Unknown stays unknown.
- Different HEADs are not silently collapsed into direct reviewer comparisons.
- Generated reports and raw intake snapshots do not become competing truth owners.
- Incomplete/truncated API evidence fails closed.
- Bootstrap-v1 datasets are immutable authenticated-source projections, not append targets for operational records.
- Source commentary omitted from normalized tuples remains recoverable by manifest + `source_row`; material assertions from it must be provenance-reconciled before baseline derivation.
- A baseline seed may not be derived merely because files exist; Stage 1 provenance/policy/classification/current-intake requirements must also be satisfied.
