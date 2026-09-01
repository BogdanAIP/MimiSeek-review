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
- historical-dataset bootstrap role;
- two user-facing ChatGPT roles with repository-owned workflow contracts;
- repository-driven run behavior that continues bootstrap/development until the operational learning pipeline exists;
- fresh independent update/evaluator authority for candidate promotion;
- separation of global reviewer promotion from per-consumer installation;
- fail-closed consumer safe-update semantics and running-run reviewer immutability;
- fail-closed rule when required independent evaluation, identity, or evidence cannot be established.

Current verification state:

- no GitHub Actions workflow is present for the current Stage 0 branch, and the most recent explicit Actions query before this coherence pass returned zero workflow runs for the then-current head;
- repeated Codex review attempts on PR #1 returned usage-limit notices, not semantic review findings or PASS evidence;
- therefore no Codex review or CI result is being treated as Stage 0 acceptance evidence.

Evidence still required before DONE:

- a fresh independent read-only semantic review of the exact final PR head under the repository's governing development/acceptance protocol;
- if that review reports findings, fixes plus a new independent review of the resulting exact head;
- merge of the accepted exact head;
- merged commit recorded here after acceptance.

Accepted head: not yet established.

## Stage 1 — Bootstrap data + first stable reviewer baseline

Status: NOT STARTED

Expected source data:

- audited historical reviewer-statistics workbook assembled from CAP/UV history;
- 84 existing BUGGY→FIXED regression pairs;
- exact accepted CAP/UV reviewer-policy refs resolved at implementation time.

Do not pre-fill final imported counts or reviewer identities until the import/reconciliation is executed on Stage 1.

## Later stages

Add entries only when evidence exists. Do not pre-fill imagined CI/review IDs.
