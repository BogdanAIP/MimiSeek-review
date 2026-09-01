# Data

This directory contains MimiSeek Review's canonical machine-readable bootstrap/learning/regression data. Non-authoritative live GitHub intake is stored separately on branch `evidence/github-intake`; it is source evidence, not canonical adjudicated truth.

## Bootstrap source

The audited historical CAP/UV reviewer-statistics workbook used to bootstrap Stage 1 is durably identified by `data/bootstrap-source.json`.

That manifest is the sole owner of the exact access-controlled Library path/version, byte size, SHA-256, recovery contract, and declared BUGGY→FIXED reconciliation target. A fresh authorized chat must recover that exact artifact and verify the manifest before trusting a bootstrap import. Failure to recover/authenticate it is fail-closed.

The workbook remains a bootstrap/provenance artifact, not the ongoing automation store.

## Canonical bootstrap datasets

Stage 1 imports the authenticated workbook into deterministic JSON Lines datasets:

- `review-runs.jsonl` — normalized historical reviewer executions and exact review identity;
- `findings.jsonl` — historical finding observations, disposition/provenance fields, and source identity;
- `regression-cases.jsonl` — historical BUGGY→FIXED target cases and evidence refs.

Their positional field contracts are versioned under `data/schemas/`. `data/bootstrap-import-report.json` records source authentication, counts, hashes, internal reconciliation, and explicitly unfinished provenance work. It is derived verification evidence, not a competing source-identity owner.

For numeric review-run metrics, `null` means the authenticated workbook cell was blank/unknown. Literal `0` means the source explicitly recorded zero. Bootstrap import must not convert a blank metric into numerical evidence.

The Stage-1 bootstrap-v1 prefixes are additionally pinned by fixed source-reconciliation digests in `tests/test_bootstrap_data_integrity.py`. Those anchors are intentionally independent of the mutable import report. Changing an anchored bootstrap prefix or its fixed digest requires an explicit new authenticated source reconciliation/version and fresh semantic acceptance; it must not be updated merely to make altered canonical data pass CI. Later operational records may be appended beyond the anchored bootstrap prefixes without rewriting the historical anchor.

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

The collector is implemented by `tools/collect_github_evidence.py` and scheduled by `.github/workflows/collect-review-evidence.yml`. Reliable scheduled operation requires the dedicated read-only GitHub App credentials described by ADR 0012.

Stage 2 will add the structured consumer evidence-export contract required to make fresh ordinary-ChatGPT terminal results automatically recoverable from consumer GitHub state. Stage 3 will complete normalized operational collector/outcome-store semantics.

## Rules

- Source evidence remains traceable to exact repository/PR/comment/review/reaction/commit identities.
- Imports and collection are idempotent.
- Unknown stays unknown.
- Different HEADs are not silently collapsed into direct reviewer comparisons.
- Generated reports and raw intake snapshots do not become competing truth owners.
- Incomplete/truncated API evidence fails closed.
- A baseline seed may not be derived merely because files exist; Stage 1 provenance/policy/classification requirements must also be satisfied.
