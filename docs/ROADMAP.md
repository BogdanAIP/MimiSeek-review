# Roadmap

The reviewer-evolution stages are ordered. A stage is not complete merely because implementation exists; acceptance conditions must be satisfied.

A separate cross-cutting **Track R — independent review-job coordination** may proceed in parallel with the ordered reviewer-evolution stages once its own prerequisites are accepted. Track R does not make any reviewer-evolution stage complete and cannot bypass candidate promotion or consumer distribution authority.

## Stage 0 — Continuous-development foundation — DONE

Goal: make the repository self-describing so any fresh development chat can continue without previous-chat memory and establish the correct product boundary.

Acceptance:

- canonical product/current-state/roadmap/architecture/protocol owners exist and are mutually coherent;
- MimiSeek is explicitly a reviewer-improvement/release system, not the owner of consumer PR development/review/fix/merge loops;
- standalone multi-project ownership is recorded;
- the two ChatGPT workflow contracts exist in `.agents/skills/mimiseek-run/SKILL.md` and `.agents/skills/mimiseek-update/SKILL.md`;
- the run workflow is repository-driven and continues bootstrap/development until later operational stages actually exist;
- every real update workflow invocation uses a new independent ChatGPT chat, including deferred-distribution reconciliation;
- global promotion and per-consumer installation are separate, with fail-closed safe-update semantics;
- the historical Stage 1 bootstrap source has a repository-owned stable locator, exact version, byte size/digest, and fail-closed recovery contract;
- repository-development terminal review evidence is bound to repository/base/head/reviewer/immutable `review_policy_ref`;
- after bootstrap, accepted BASE policy governs a PR's terminal acceptance while proposed HEAD governance is target semantics only and cannot govern its own acceptance;
- the one-time PR #1 no-policy bootstrap exception is explicit and cannot be reused by ordinary later PRs;
- no bootstrap shortcut may create the first stable reviewer or install it in a consumer outside the same governed promotion/distribution paths used later;
- the repository is the durable handoff between chats;
- branch/PR workflow and fresh exact-head acceptance review are established.

Stage 0 acceptance and merge evidence are owned by `docs/EVIDENCE_INDEX.md`; this roadmap records only stage status, sequencing, and acceptance conditions.

## Stage 1 — Bootstrap data + reviewer baseline seed — IN PROGRESS

Goal: reconstruct MimiSeek's historical learning memory, prevent new review evidence from being lost while bootstrap continues, and derive a reusable **unreleased baseline seed** for later candidate generation without inventing a stable version.

Work:

- recover and authenticate the exact workbook identified by `data/bootstrap-source.json`;
- import the reviewer statistics workbook into canonical text-based normalized bootstrap data while preserving an exact source-row recovery path for intentionally omitted non-authoritative commentary/descriptive fields;
- preserve supported historical BUGGY→FIXED cases as regression/bootstrap evidence after reconciliation;
- retain Excel as the authenticated source/provenance artifact, not the ongoing canonical automation store;
- keep bootstrap-v1 JSONL files immutable and separate from later operational outcome schemas/stores;
- establish a bounded **non-authoritative GitHub evidence-intake foundation** so CAP/UV reviews produced during Stage 1 are automatically preserved instead of waiting for a later manual workbook rebuild;
- enforce a server-side canonical-ref boundary before any repository-scoped write token is allowed to publish intake snapshots;
- backfill intake with deliberate overlap against the bootstrap workbook and preserve immutable GitHub identities so later normalization can deduplicate safely;
- keep the early intake foundation separate from Stage 3 acceptance: it stores source snapshots only and cannot infer adjudication, create learning events, or become promotion authority;
- resolve exact accepted CAP and UV review-policy refs;
- classify rules as generic or project-specific;
- derive a reusable reviewer baseline seed without weakening either consumer;
- define immutable identity for the baseline seed.

The Stage 1 baseline seed is **not** stable, is not consumer-authoritative, and cannot be distributed. It is an evidence-backed bootstrap input for the first governed candidate created at Stage 5.

Acceptance:

- source path/version/size/digest are verified before import;
- imported normalized counts/identities reconcile with the audited source workbook and underlying provenance;
- intentionally omitted workbook fields are explicitly classified and remain deterministically recoverable by authenticated source identity + source row; material assertions from source commentary are reconciled before baseline derivation;
- bootstrap-v1 datasets are immutable exact anchored sets and do not accept operational append records;
- regression cases are machine-readable and traceable to evidence;
- before durable intake publishing is enabled, the live repository has an active server-enforced canonical-main rule with no workflow bypass, PR-required updates, deletion protection, and non-fast-forward protection;
- the intake workflow fails closed if that live canonical-ref boundary is absent or weakened;
- registered-consumer GitHub intake is brought current to a durable collector watermark before the baseline seed is derived;
- raw intake remains explicitly non-authoritative and missing adjudication remains unknown;
- baseline-seed identity is immutable and reproducible;
- baseline seed is explicitly non-stable/non-distributable;
- project-specific rules remain project-local.

The early collector foundation is authorized only to stop evidence loss during bootstrap. It does **not** mean Stage 3 is complete.

## Track R — Independent review-job coordination — IN PROGRESS

Goal: remove routine manual prompt/result shuttling for an explicitly requested independent review while preserving consumer project authority and keeping the session/execution substrate generic.

Track R is a cross-cutting operational capability, not a reviewer-evolution stage. It may proceed in parallel with the remaining Stage 1 evidence work after the architecture decision is accepted.

Accepted PR #16 established the first MimiSeek-local `REVIEW_JOB_V1` state-machine/result-correlation foundation. The durability slice proposed in the current development tree adds the MimiSeek-owned GitHub ledger/publication adapter. Neither implementation alone authorizes live external CAP/session launch or return delivery, and code-level ledger tests are not a substitute for later physical GitHub durability evidence.

Target flow:

```text
originating project chat
    ↓ explicit exact-identity review request
MimiSeek REVIEW_JOB_V1 control plane
    ↓
generic CAP/session fresh-worker capability
    ↓
fresh Temporary Chat reviewer
    ↓ REVIEW_RESULT_V1
MimiSeek durable result + live identity recheck
    ↓
generic CAP/session return delivery
    ↓
originating project chat continues under its own policy
```

MimiSeek-side work:

- define versioned immutable `REVIEW_JOB_V1` identity/state/result schemas;
- implement a durable job ledger/publication path owned by MimiSeek;
- keep raw/private ChatGPT/browser/session authority out of public GitHub records;
- validate source repository/PR/BASE/HEAD/`review_policy_ref` before launch and again after result capture;
- bind reviewer profile/source and exact external execution correlation;
- represent explicit `STALE`, `ABSTAIN`, and failure outcomes rather than treating them as generic retryable errors;
- guarantee idempotent launch/result/publication/return coordination at the MimiSeek layer;
- persist the exact result without moving the reviewed consumer HEAD;
- treat the consumer workflow as owner of adjudication, fixes, re-review decisions, terminal acceptance, and merge consequences;
- keep review-job evidence distinct from adjudicated learning events until the normal evidence/outcome contract promotes it into the learning store.

Current Track R implementation boundary:

- accepted: immutable local job/state/result boundary from PR #16;
- proposed in the current ledger slice: MimiSeek-repository-scoped durable job snapshots, immutable exact-result Git blob publication, revision/CAS fencing, bounded result-less outcome publication, and explicit ambiguous-publication reconciliation;
- still pending after this slice: physical production ledger enablement/recovery evidence, exact accepted generic external capability identities, launch/result adapter, private-route return/wake adapter, and cross-origin physical E2E/restart/ambiguous-delivery evidence.

External prerequisites, verified rather than assumed:

- a separately accepted generic fresh-worker/result capability from CAP or another session/execution substrate;
- a separately accepted generic existing-session return-delivery capability with opaque route, restart recovery, one-shot/no-blind-resend semantics, and no project-specific routing tables;
- exact capability/version identity so MimiSeek does not silently depend on moving external behavior.

Track R acceptance:

- canonical product/architecture/integration authority explicitly permits the narrow coordination boundary while preserving consumer ownership;
- one immutable review job cannot be launched twice by crash/retry/concurrent claims;
- wrong repository/PR/BASE/HEAD/policy/job/result correlation fails closed;
- source HEAD movement is classified `STALE` after a live post-result recheck;
- conflicting repeated results or ambiguous publication fail closed;
- public GitHub state contains no usable private session capability;
- the existing CAP/UV source GitHub App remains read-only; review-job/result publication does not require widening consumer source permissions;
- a repeated reconciliation of an already-completed job is a no-op rather than a second review or second wake;
- the generic transport contains no UV/CAP/MimiSeek project semantics and does not interpret PR/PASS/FINDINGS semantics;
- one real end-to-end job is proven from each origin class used in routine development (UV, CAP, MimiSeek) after the external generic capabilities are accepted;
- browser/runtime restart and ambiguous-delivery paths are physically exercised before the mechanism becomes routine acceptance infrastructure;
- a review-job `PASS` grants neither consumer merge authority nor MimiSeek reviewer-promotion/distribution authority.

Track R may operate before the first MimiSeek stable exists, but each job must explicitly bind the actual reviewer profile/source and the consumer's accepted policy authority. It must never invent a stable reviewer identity.

## Stage 2 — Consumer binding schema + evidence export contract

Goal: make CAP and UV structurally ready to become consumers/evidence producers **without installing a MimiSeek reviewer yet**.

Acceptance:

- both repositories have or can consume an explicit machine-readable binding schema that can represent `consumer_installed = none` before first rollout;
- both can export/import structured review runs and finding dispositions without pretending they already use MimiSeek stable;
- fresh ordinary-ChatGPT terminal results can be durably exported with exact repository/base/head/reviewer/policy identity so collection no longer depends on chat history;
- future reviewer updates are defined as explicit and auditable;
- project-local policy remains authoritative;
- stale/mismatched reviewer identity fails closed when a binding exists;
- already-running runs will remain bound to the reviewer version with which they started once MimiSeek is installed;
- Stage 2 does not create or modify a CAP/UV MimiSeek pin merely to satisfy its acceptance criteria.

Track R durable review-job results may later become one structured evidence source for Stage 2/3, but Track R implementation by itself does not satisfy Stage 2 acceptance because adjudication/export/binding requirements remain separate.

## Stage 3 — Collector + normalized outcome store

Goal: turn the Stage 1 intake foundation plus Stage 2 structured exports into the complete operational collector/outcome store used by the run workflow.

Acceptance:

- collection is idempotent;
- exact identities and provenance are preserved;
- missing adjudication stays unknown;
- a closed PR can be reconstructed into normalized review outcomes without chat history;
- reviewer source/version remains explicit rather than assuming every imported run used MimiSeek;
- bootstrap workbook records, overlapping raw GitHub intake, Track R review-job evidence where applicable, and structured consumer exports deduplicate without collapsing different exact HEADs;
- operational records use their own versioned source-kind/source-identity contract instead of fabricating workbook `source_row` provenance;
- the operational normalized outcome store, not the raw intake branch, review-job ledger, or bootstrap-v1 files, is the canonical learning input.

## Stage 4 — Learning events

Goal: automatically derive trustworthy OUR/Codex/development success, miss, and false-positive events.

Acceptance:

- event derivation respects exact-head and leakage/timing requirements;
- different-head fixes are not mislabeled as same-head misses;
- events link back to source evidence.

## Stage 5 — Fixed evaluation gate + learner + candidate generation

Goal: fix the candidate's exam first, then convert accumulated evidence into the first or next transferable reviewer candidate.

Before candidate creation, the quantitative/absolute evaluation policy that will govern that candidate must already be accepted as a separate repository-development change under `docs/EVALUATION_POLICY.md`. The candidate identity binds that immutable evaluation-policy identity; learner/candidate work cannot alter it for the same promotion attempt.

Before any stable exists, the Stage 1 baseline seed plus governed learning evidence may then be used to create the **first candidate**. After a stable exists, later candidates evolve from accepted stable/evidence according to lifecycle policy.

Acceptance:

- governing evaluation-policy identity was accepted before candidate creation;
- proposals are generic mechanics, not SHA/file memorization;
- each proposal cites learning events;
- candidate identity is immutable and distinct from both baseline seed and stable;
- candidate identity binds the preaccepted evaluation-policy identity;
- learner creates candidate but cannot promote it or change its governing evaluation policy;
- potentially affected protected capabilities are declared.

## Stage 6 — Automated regression / protected-capability evaluation

Goal: let the run workflow evaluate an eligible candidate on appropriate historical cases and protected capabilities before independent update evaluation.

Acceptance:

- BUGGY target detection is measured;
- old target findings must disappear on FIXED;
- false-positive/regression behavior is measured;
- protected capabilities are checked;
- candidate cannot modify the evaluation policy governing the run;
- candidate evaluation uses the immutable policy identity bound before candidate creation;
- when a stable exists, stable-versus-candidate comparison is included where required;
- when no stable exists yet, the first candidate is still evaluated against the fixed corpus/protected capabilities and may use the non-authoritative baseline seed only as comparison evidence, never as promotion authority;
- a passing candidate is frozen into exactly one durable independent-update package/state.

## Stage 7 — Independent update workflow + first/next stable promotion

Goal: make `mimiseek-review-update` fully functional in a new ChatGPT chat and use the same authority path for the **first stable** and every later stable.

The user opens a new chat and invokes the update workflow. No technical prompt is copied from the run chat.

Acceptance:

- second chat reconstructs the frozen pending package independently from Git/GitHub;
- evaluator is separate from learner/candidate development context;
- candidate/policy identities match the immutable package created before evaluation;
- insufficient evidence yields `ABSTAIN`;
- failed independence or identity checks fail closed;
- only authoritative `PROMOTE` may advance global MimiSeek stable;
- if no stable exists before the decision, authoritative `PROMOTE` establishes the first stable and `REJECT`/`ABSTAIN` leave stable unset;
- no separate bootstrap-stable admission path exists;
- result is durable and identity-bound.

## Stage 8 — Safe consumer distribution + first installation

Goal: after a MimiSeek stable has been authoritatively promoted, install/update it in each registered consumer only when that consumer's current live project state proves the update safe.

This stage is the first point at which CAP/UV reviewer pins may be changed solely to install MimiSeek.

Acceptance:

- global MimiSeek promotion and consumer installation are separate transactions;
- every real distribution/reconciliation run uses a new independent update chat;
- a rollout target is accepted only when durable state proves it is the exact current authoritatively promoted stable;
- the update workflow resolves each consumer independently;
- active runs/gates/stages remain on their existing reviewer identity;
- `SAFE_TO_UPDATE` permits an auditable first-install/update PR/change;
- `DEFER_*` leaves the consumer unchanged and records `PENDING_DISTRIBUTION`;
- deferred consumers can be re-checked by a later fresh update invocation without creating or re-promoting a reviewer candidate;
- no earlier stage or Track R review job is allowed to bypass this safe-distribution authority merely to create an initial consumer pin.

## Stage 9 — Complete two-chat workflow

Goal: the practical reviewer-evolution user workflow is fully operational:

```text
Chat A: run workflow
collect → learn → candidate → regression → independent-update state

new Chat B: update workflow
independent evaluation → PROMOTE/REJECT/ABSTAIN → safe distribution
```

Acceptance:

- no manual technical sequencing or prompt copying is required inside the reviewer-evolution workflow except the deliberate new-chat boundary still governed here;
- both workflows resume idempotently after interruption;
- unchanged evidence produces safe `NO_CHANGE` or equivalent governed no-op state;
- every mutation is traceable to an exact pipeline/update run;
- failures leave current stable (or the intentional no-stable bootstrap state) and unsafe consumers unchanged.

Track R is separate: its purpose is automatic execution/return of ordinary independent review jobs, not promotion of a reviewer candidate.

## Stage 10 — Optional automatic fresh-chat handoff for reviewer promotion/update

Goal: later remove even the user's manual action of opening the **independent promotion/update chat** by adding a proven executor that launches `mimiseek-review-update` in a genuinely fresh ChatGPT context.

This stage is about the reviewer-evolution promotion/update authority boundary. It is distinct from Track R, which may use a generic fresh reviewer worker earlier for ordinary exact-head review jobs.

Acceptance:

- automatic handoff preserves the exact same two-role authority separation;
- freshness is provable;
- failure to create/verify the fresh context leaves stable unchanged.

## Stage 11 — Continuous autonomous evolution

Goal: optionally trigger the proven learning pipeline from new evidence automatically while keeping the two-role evaluation boundary intact.

Acceptance: reviewer improvement can continue across CAP, UV, and future projects without technical adjudication by the human owner except policy/product choices explicitly reserved to the owner.
