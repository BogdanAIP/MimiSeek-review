# Data

This directory will contain MimiSeek Review's canonical machine-readable learning and regression data.

## Bootstrap source

The audited historical CAP/UV reviewer-statistics workbook used to bootstrap Stage 1 is durably identified by the repository-owned manifest:

`data/bootstrap-source.json`

The manifest pins the exact access-controlled ChatGPT File Library artifact by stable Library path + `version_id`, together with its expected byte size and SHA-256:

`/MimiSeek Review/bootstrap/reviewer_statistics_improvement_dataset.xlsx`

SHA-256:

`6fe79a73a7f10e528a7323adce1fafcc1951955394a0dbece31a5eec73d6391a`

This locator is external storage, but it is not chat memory: a fresh MimiSeek chat must resolve the exact manifest path/version, materialize that Library artifact, verify the digest, and only then use it as Stage 1 input. If the exact version cannot be recovered or the digest differs, Stage 1 fails closed rather than substituting another workbook with the same name.

The manifest records 84 BUGGY→FIXED cases as an expected reconciliation target. Stage 1 must independently reconcile the workbook contents/counts and underlying GitHub evidence before importing them.

The workbook is **not** intended to remain the canonical automation store because binary spreadsheets are difficult to diff, merge, validate, and consume safely from automation. Its role is the bootstrap import/provenance artifact; Stage 1 converts verified content into repository-owned machine-readable datasets.

## Planned canonical datasets

At minimum:

- `review-runs.jsonl` — normalized reviewer executions and immutable review identity;
- `findings.jsonl` — finding observations and adjudicated disposition/provenance;
- `regression-cases.jsonl` — BUGGY→FIXED target cases and evidence refs;
- `learning-events.jsonl` — derived OUR/Codex/development success/miss/false-positive events;
- versioned schemas for each dataset.

Exact schema is a Stage 1 deliverable.

## Rules

- Source evidence must remain traceable.
- Imports are idempotent.
- Unknown is preserved as unknown.
- Different HEADs are not silently collapsed into direct reviewer comparisons.
- Generated reports must not become competing truth owners.
- The exact Library path/version, byte size and workbook digest must be verified before Stage 1 import/reconciliation.
- Inability to recover the exact pinned source is a hard stop, not permission to use a similar file.
