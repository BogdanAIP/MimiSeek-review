# ADR 0012 — Preserve continuous GitHub evidence before baseline derivation

## Context

Stage 1 began from a finite historical workbook, while CAP and UV continued producing new Codex reviews, fresh ordinary-ChatGPT reviews, adjudication replies, fixes, and exact-head history. Deriving the first baseline seed from a static bootstrap snapshot while evidence continued to accumulate would make the baseline stale by construction and would force recurring manual spreadsheet rebuilds.

The target architecture already contains a collector in Stage 3. The immediate problem is narrower: preserve new source evidence now, without claiming that the full Stage 3 normalized outcome store or learning pipeline already exists.

## Decision

Stage 1 may establish and operate a **bounded evidence-intake foundation** before the Stage 3 collector is accepted.

The foundation:

- polls only repositories registered in `config/consumers.json`;
- authenticates to consumer repositories with a dedicated GitHub App installation token whose consumer permissions are read-only;
- never writes to CAP, UV, or another consumer;
- writes source snapshots only to the dedicated MimiSeek branch `evidence/github-intake`;
- uses MimiSeek's own workflow `GITHUB_TOKEN` only to update that intake branch;
- treats the intake branch as non-authoritative source evidence, not as adjudicated truth, normalized learning data, reviewer policy, candidate state, or promotion authority;
- preserves issue comments, PR reviews, inline review comments, exact PR BASE/HEAD identity, and PR commit history needed for later reconstruction;
- is idempotent by deterministic snapshot paths/content and uses an overlap window when advancing source watermarks;
- deliberately backfills from a date that overlaps the historical workbook. Later normalization deduplicates by immutable GitHub/source identities rather than assuming the workbook cutoff was perfect;
- fails closed on incomplete API evidence instead of silently truncating it.

This early intake foundation does **not** satisfy Stage 3. Stage 2 must still establish the structured consumer evidence-export/binding contract, including durable export of fresh ordinary-ChatGPT terminal results. Stage 3 must still complete governed normalization, disposition handling, identity reconciliation, and operational collector/outcome-store acceptance.

The first Stage 1 baseline seed must not be derived until the historical workbook is reconciled and the registered consumer intake has been brought current to a durable collector watermark.

## Consequences

- New GitHub-native review evidence stops depending on manual workbook maintenance.
- Existing public GitHub review/adjudication history can be backfilled automatically.
- Chat-only fresh review results that were never exported to GitHub remain a known gap until Stage 2 export is implemented; absence is preserved as unknown.
- The collector cannot mutate consumer repositories or decide whether a finding is true.
- A one-time GitHub App setup is required for reliable authenticated polling. The app should be installed only on intended evidence-producing repositories with minimum read permissions.
- Webhooks remain optional future optimization; hourly polling is sufficient for the first implementation and avoids a separate always-on service.
