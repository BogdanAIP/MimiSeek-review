# ADR 0012 — Preserve continuous GitHub evidence before baseline derivation

## Context

Stage 1 began from a finite historical workbook, while CAP and UV continued producing new Codex reviews, fresh ordinary-ChatGPT reviews, adjudication replies, fixes, exact-head history, and PR reactions. Deriving the first baseline seed from a static bootstrap snapshot while evidence continued to accumulate would make the baseline stale by construction and would force recurring manual spreadsheet rebuilds.

The target architecture already contains a collector in Stage 3. The immediate problem is narrower: preserve new source evidence now, without claiming that the full Stage 3 normalized outcome store or learning pipeline already exists.

GitHub reactions require special handling because adding a reaction does not reliably advance the PR/issue `updated_at` timestamp. A clean Codex review may be represented only by a PR `+1` reaction. Therefore an `updated_at`-only polling strategy can silently lose useful evidence.

The first implementation also exposed an authority issue: GitHub Actions `GITHUB_TOKEN` `contents: write` permission is repository-scoped, not branch-scoped. Merely writing `git push ... evidence/github-intake` in shell does not prevent a defective or compromised workflow step from targeting the canonical branch when the repository has no server-side protection.

## Decision

Stage 1 may establish and operate a **bounded evidence-intake foundation** before the Stage 3 collector is accepted.

The foundation:

- polls only repositories registered in `config/consumers.json`;
- authenticates to consumer repositories with a dedicated GitHub App installation token whose consumer permissions are read-only;
- never writes to CAP, UV, or another consumer;
- writes source snapshots only to the dedicated MimiSeek branch `evidence/github-intake`;
- uses MimiSeek's own workflow `GITHUB_TOKEN` only for the intake-branch push, but treats that token as repository-scoped write capability rather than pretending the credential itself is branch-scoped;
- requires an **independent server-enforced canonical-ref boundary** before the write-capable workflow may run: an active repository ruleset named `mimiseek-canonical-main` must target the default branch, have no bypass actor, require pull requests, and block branch deletion and non-fast-forward updates;
- fails closed before source collection/push when that required live ruleset is absent, inactive, bypassable, excludes the default branch, or lacks any required rule;
- requires terminal repository-development acceptance to independently re-resolve the live ruleset instead of treating the workflow preflight as proof of its own authority boundary;
- treats the intake branch as non-authoritative source evidence, not as adjudicated truth, normalized learning data, reviewer policy, candidate state, or promotion authority;
- preserves issue comments, PR-level reactions, PR reviews, inline review comments/reaction summaries, exact PR BASE/HEAD identity, and PR commit history needed for later reconstruction;
- re-reads every open PR on every scheduled intake run so reaction-only changes cannot be lost merely because `updated_at` was unchanged;
- is idempotent by deterministic snapshot paths/content and uses an overlap window when advancing source watermarks for closed/recently changed evidence;
- deliberately backfills from a date that overlaps the historical workbook. Later normalization deduplicates by immutable GitHub/source identities rather than assuming the workbook cutoff was perfect;
- fails closed on incomplete API evidence instead of silently truncating it.

The ruleset is intentionally outside workflow-controlled state. The same credential that writes intake data must not be able to remove or weaken the server rule that protects canonical `main`. If the rule cannot be independently established, the correct state is collector-disabled, not an optimistic assumption that shell intent is enough.

A GitHub reaction is evidence only. A `+1` must not become PASS unless later governed normalization proves reviewer identity, timing, and the applicable reviewed HEAD/semantics. Absence of a reaction is not a finding or miss.

This early intake foundation does **not** satisfy Stage 3. Stage 2 must still establish the structured consumer evidence-export/binding contract, including durable export of fresh ordinary-ChatGPT terminal results. Stage 3 must still complete governed normalization, disposition handling, identity reconciliation, operational source-kind schemas, and operational collector/outcome-store acceptance.

The Stage 1 reaction guarantee is deliberately bounded to open PRs plus the normal closed-PR watermark/overlap window. Long-after-close reaction-only completeness is not claimed by this foundation; Stage 3 or a later webhook path may extend that evidence surface without changing the non-authoritative rule.

The first Stage 1 baseline seed must not be derived until the historical workbook is reconciled and the registered consumer intake has been brought current to a durable collector watermark.

## Consequences

- New GitHub-native review evidence can stop depending on manual workbook maintenance once the external canonical-ref rule and source credentials are configured.
- Existing public GitHub review/adjudication history can be backfilled automatically.
- Reaction-only clean-review signals on open PRs are preserved without a second reaction-specific collector.
- Chat-only fresh review results that were never exported to GitHub remain a known gap until Stage 2 export is implemented; absence is preserved as unknown.
- The collector cannot mutate consumer repositories or decide whether a finding is true.
- The workflow's MimiSeek write credential remains repository-scoped, but server-side GitHub rules independently prevent direct canonical-main updates; workflow code re-checks this invariant on every run.
- Removing or weakening the required ruleset must make later intake runs fail closed until the boundary is restored.
- A one-time GitHub App setup is required for reliable authenticated polling. The app should be installed only on intended evidence-producing repositories with minimum read permissions.
- Webhooks remain optional future optimization; hourly polling is sufficient for the first implementation and avoids a separate always-on service.
