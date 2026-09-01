# Evidence Index

This document indexes accepted stage evidence. It is not a substitute for GitHub, CI logs, review results, or immutable commits; it points to them.

## Stage 0 — Continuous-development foundation

Status: IN REVIEW

Implementation PR:

- PR #1 — `Bootstrap continuous development foundation`
- Base: `09492f1ec8aeb1dfbfc152505d14574016a72870`
- Development branch: `bootstrap/continuous-development-docs`
- Exact active HEAD: resolve live from GitHub; do not duplicate a self-referential moving branch SHA here.

Stage 0 scope now includes:

- repository-owned cross-chat development state;
- standalone multi-project reviewer-improvement boundary;
- consumer/evidence/distribution responsibility split;
- historical-dataset bootstrap role with a repository-recoverable identity-bound source snapshot;
- two user-facing ChatGPT roles with repository-owned workflow contracts;
- repository-driven run behavior that continues bootstrap/development until the operational learning pipeline exists;
- fresh independent update/evaluator authority for every real update invocation, including deferred-distribution reconciliation;
- separation of global reviewer promotion from per-consumer installation;
- fail-closed consumer safe-update semantics and running-run reviewer immutability;
- fail-closed rule when required independent evaluation, identity, or evidence cannot be established.

Current verification state:

- no GitHub Actions workflow is present for the current Stage 0 branch, and the most recent explicit Actions query before this coherence pass returned zero workflow runs for the then-current head;
- repeated Codex review attempts on PR #1 returned usage-limit notices, not semantic review findings or PASS evidence;
- an independent exact-head review of head `cd5090b38e556636bea6c3f6dd4e0e74c2f41dff` returned FINDINGS; those findings are being remediated and that review is stale for any resulting new head;
- therefore no Codex review, CI result, or earlier semantic review is being treated as acceptance evidence for the final post-fix head.

Evidence still required before DONE:

- a fresh independent read-only semantic review of the exact final PR head under the repository's governing development/acceptance protocol;
- if that review reports findings, fixes plus a new independent review of the resulting exact head;
- merge of the accepted exact head;
- merged commit recorded here after acceptance.

Accepted head: not yet established.

## Stage 1 — Bootstrap data + first stable reviewer baseline

Status: NOT STARTED

Pinned bootstrap source:

- workbook: `reports/bootstrap/reviewer_statistics_improvement_dataset.xlsx`
- identity manifest: `data/bootstrap-source.json`
- SHA-256: `6fe79a73a7f10e528a7323adce1fafcc1951955394a0dbece31a5eec73d6391a`
- expected reconciliation target: 84 historical BUGGY→FIXED pairs
- source repositories: `BogdanAIP/chat-agent-platform`, `BogdanAIP/uv-studio`

Stage 1 must verify the workbook digest from the accepted Stage 0 commit and independently reconcile the workbook counts/records and GitHub provenance before creating canonical machine-readable datasets. The expected pair count is not independent ground truth.

Also resolve exact accepted CAP/UV reviewer-policy refs at implementation time.

Do not pre-fill final imported counts or reviewer identities until the import/reconciliation is executed on Stage 1.

## Later stages

Add entries only when evidence exists. Do not pre-fill imagined CI/review IDs.
