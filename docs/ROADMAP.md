# Roadmap

The roadmap is ordered. A stage is not complete merely because implementation exists; acceptance conditions must be satisfied.

## Stage 0 — Continuous-development foundation — IN REVIEW

Goal: make the repository self-describing so any fresh development chat can continue without previous-chat memory and establish the correct product boundary.

Acceptance:

- canonical product/current-state/roadmap/architecture/protocol owners exist;
- MimiSeek is explicitly a reviewer-improvement/release system, not the owner of consumer PR review loops;
- standalone multi-project ownership is recorded;
- one ChatGPT user entry-point skill contract exists;
- branch/PR workflow is established.

## Stage 1 — Bootstrap data + first stable reviewer baseline — NEXT

Goal: start MimiSeek with both its historical learning memory and an explicit reusable stable reviewer.

Work:

- import the existing reviewer statistics workbook into canonical text-based normalized data;
- preserve the 84 historical BUGGY→FIXED cases as regression/bootstrap evidence;
- retain Excel as a generated/report view, not the only source of truth;
- resolve exact accepted CAP and UV review-policy refs;
- classify rules as generic or project-specific;
- derive the first stable MimiSeek reviewer without weakening either consumer;
- define immutable reviewer version identity.

Acceptance:

- imported counts/identities reconcile with the audited source workbook;
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
- stale/mismatched reviewer identity fails closed.

## Stage 3 — Collector + normalized outcome store

Goal: let MimiSeek automatically gather new accepted review evidence from all registered consumers.

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

Goal: evaluate stable versus candidate on historical and accumulated real cases.

Acceptance:

- BUGGY target detection is measured;
- old target findings must disappear on FIXED;
- false-positive/regression behavior is measured;
- protected capabilities are checked;
- candidate cannot modify the evaluation policy governing the run.

## Stage 7 — Fresh ChatGPT evaluator executor

Goal: let the evolution pipeline automatically create a new isolated ChatGPT evaluation context and obtain an independent `PROMOTE`, `REJECT`, or `ABSTAIN` result.

Acceptance:

- evaluator runs in a new context, separate from learner/candidate development;
- evaluator resolves evidence independently and read-only;
- insufficient evidence yields `ABSTAIN`;
- missing fresh-context capability fails closed without promotion;
- evaluator result is durable and identity-bound.

## Stage 8 — Automatic promotion + distribution

Goal: convert an accepted candidate into new stable and propagate it to registered consumers.

Acceptance:

- only authoritative `PROMOTE` can change stable;
- promotion is atomic/auditable and rollback remains possible;
- compatible consumers receive version-update PRs automatically;
- incompatible consumers remain explicitly pinned rather than silently changed.

## Stage 9 — Full `mimiseek-evolve` ChatGPT skill

Goal: one user invocation runs the complete pipeline:

`collect → learn → candidate → regression → fresh evaluation → promote/reject/abstain → distribute`.

Acceptance:

- no manual technical sequencing is required from the user;
- the skill resumes idempotently after interruption;
- unchanged evidence produces a safe no-op;
- every mutation is traceable to an exact pipeline run;
- failures leave the current stable reviewer unchanged.

## Stage 10 — Continuous autonomous evolution

Goal: optionally trigger the same proven evolution pipeline from new evidence automatically, while retaining the ChatGPT skill as the explicit manual entry point.

Acceptance: reviewer improvement can continue across CAP, UV, and future projects without technical adjudication by the human owner except policy/product choices explicitly reserved to the owner.
