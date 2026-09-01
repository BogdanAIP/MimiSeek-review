# Roadmap

The roadmap is ordered. A stage is not complete merely because implementation exists; acceptance conditions must be satisfied.

## Stage 0 — Continuous-development foundation — IN REVIEW

Goal: make the repository self-describing so any fresh development chat can continue without previous-chat memory and establish the correct product boundary.

Acceptance:

- canonical product/current-state/roadmap/architecture/protocol owners exist and are mutually coherent;
- MimiSeek is explicitly a reviewer-improvement/release system, not the owner of consumer PR review loops;
- standalone multi-project ownership is recorded;
- the two ChatGPT workflow contracts exist in `.agents/skills/mimiseek-run/SKILL.md` and `.agents/skills/mimiseek-update/SKILL.md`;
- the run workflow is repository-driven and continues bootstrap/development until later operational stages actually exist;
- every real update workflow invocation uses a new independent ChatGPT chat, including deferred-distribution reconciliation;
- global promotion and per-consumer installation are separate, with fail-closed safe-update semantics;
- the historical Stage 1 bootstrap source has a repository-owned stable locator, exact version, byte size/digest, and fail-closed recovery contract;
- repository-development terminal review evidence is bound to repository/base/head/reviewer/immutable `review_policy_ref`;
- after bootstrap, accepted BASE policy governs a PR's terminal acceptance while proposed HEAD governance is target semantics only and cannot govern its own acceptance;
- the one-time PR #1 no-policy bootstrap exception is explicit and cannot be reused by ordinary later PRs;
- the repository is the durable handoff between chats;
- branch/PR workflow and fresh exact-head acceptance review are established.

Stage 0 is not DONE until an independent read-only review returns PASS for the exact final PR head under the explicit bootstrap `review_policy_ref` authority and that accepted head is merged.

## Stage 1 — Bootstrap data + first stable reviewer baseline — NEXT

Goal: start MimiSeek with both its historical learning memory and an explicit reusable stable reviewer.

Work:

- recover and authenticate the exact workbook identified by `data/bootstrap-source.json`;
- import the reviewer statistics workbook into canonical text-based normalized data;
- preserve supported historical BUGGY→FIXED cases as regression/bootstrap evidence after reconciliation;
- retain Excel as a bootstrap/report artifact, not the canonical automation source of truth;
- resolve exact accepted CAP and UV review-policy refs;
- classify rules as generic or project-specific;
- derive the first stable MimiSeek reviewer without weakening either consumer;
- define immutable reviewer version identity.

Acceptance:

- source path/version/size/digest are verified before import;
- imported counts/identities reconcile with the audited source workbook and underlying provenance;
- regression cases are machine-readable and traceable to evidence;
- first stable reviewer identity is immutable and reproducible;
- project-specific rules remain project-local.

## Stage 2 — Consumer binding + evidence export

Goal: make CAP and UV true consumers and evidence producers.

Acceptance:

- both repositories pin an exact stable MimiSeek reviewer identity;
- both can export/import structured review runs and finding dispositions;
- updates are explicit and auditable;
- project-local policy remains authoritative;
- stale/mismatched reviewer identity fails closed;
- already-running runs remain bound to the reviewer version with which they started.

## Stage 3 — Collector + normalized outcome store

Goal: let the run workflow automatically gather new accepted review evidence from all registered consumers.

Acceptance:

- collection is idempotent;
- exact identities and provenance are preserved;
- missing adjudication stays unknown;
- a closed PR can be reconstructed into normalized review outcomes without chat history.

## Stage 4 — Learning events

Goal: automatically derive trustworthy OUR/Codex/development success, miss, and false-positive events.

Acceptance:

- event derivation respects exact-head and leakage/timing requirements;
- different-head fixes are not mislabeled as reviewer misses;
- events link back to source evidence.

## Stage 5 — Learner + candidate generation

Goal: convert repeated evidence into transferable reviewer improvements.

Acceptance:

- proposals are generic mechanics, not SHA/file memorization;
- each proposal cites learning events;
- learner creates candidate but cannot promote it;
- potentially affected protected capabilities are declared.

## Stage 6 — Automated regression / protected-capability evaluation

Goal: let the run workflow evaluate stable versus candidate on historical and accumulated real cases before independent update evaluation.

Acceptance:

- BUGGY target detection is measured;
- old target findings must disappear on FIXED;
- false-positive/regression behavior is measured;
- protected capabilities are checked;
- candidate cannot modify the evaluation policy governing the run;
- passing candidate is frozen into exactly one durable independent-update package/state.

## Stage 7 — Independent update workflow

Goal: make `mimiseek-review-update` fully functional in a new ChatGPT chat.

The user opens a new chat and invokes the update workflow. No technical prompt is copied from the run chat.

Acceptance:

- second chat reconstructs the frozen pending package independently from Git/GitHub;
- evaluator is separate from learner/candidate development context;
- insufficient evidence yields `ABSTAIN`;
- failed independence or identity checks fail closed;
- only authoritative `PROMOTE` may advance global MimiSeek stable;
- result is durable and identity-bound.

## Stage 8 — Safe consumer distribution

Goal: after a MimiSeek promotion, update each registered consumer only when its current live project state proves the update safe.

Acceptance:

- global MimiSeek promotion and consumer installation are separate transactions;
- every real distribution/reconciliation run uses a new independent update chat;
- a rollout target is accepted only when durable state proves it is the exact current authoritatively promoted stable;
- the update workflow resolves each consumer independently;
- active runs/gates/stages remain on their existing reviewer identity;
- `SAFE_TO_UPDATE` permits an auditable update PR/change;
- `DEFER_*` leaves the consumer unchanged and records `PENDING_DISTRIBUTION`;
- deferred consumers can be re-checked by a later fresh update invocation without creating or re-promoting a reviewer candidate.

## Stage 9 — Complete two-chat workflow

Goal: the practical user workflow is fully operational:

```text
Chat A: run workflow
collect → learn → candidate → regression → independent-update state

new Chat B: update workflow
independent evaluation → PROMOTE/REJECT/ABSTAIN → safe distribution
```

Acceptance:

- no manual technical sequencing or prompt copying is required;
- both workflows resume idempotently after interruption;
- unchanged evidence produces safe `NO_CHANGE` or equivalent governed no-op state;
- every mutation is traceable to an exact pipeline/update run;
- failures leave current stable and unsafe consumers unchanged.

## Stage 10 — Optional automatic fresh-chat handoff

Goal: later remove even the user's manual action of opening the second chat by adding a proven executor that launches the update role in a genuinely fresh ChatGPT context.

This is an optimization, not a prerequisite for a working self-improvement system.

Acceptance:

- automatic handoff preserves the exact same two-role authority separation;
- freshness is provable;
- failure to create/verify the fresh context leaves stable unchanged.

## Stage 11 — Continuous autonomous evolution

Goal: optionally trigger the proven learning pipeline from new evidence automatically while keeping the two-role evaluation boundary intact.

Acceptance: reviewer improvement can continue across CAP, UV, and future projects without technical adjudication by the human owner except policy/product choices explicitly reserved to the owner.
