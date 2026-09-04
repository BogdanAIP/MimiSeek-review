# Review quality orchestration research

Status: research only; not product, architecture, runtime, review-policy, promotion, or merge authority.

This document records architecture hypotheses for improving the **quality and semantic completeness of independent review** after the current single-job Track R execution path is proven end to end. It does not change accepted ADR 0013, `REVIEW_JOB_V1`, consumer authority, current acceptance policy, or the sequencing requirements that still block live external Track R operation.

## Question

MimiSeek is increasingly able to prove that an independent review was executed with the correct immutable repository/PR/BASE/HEAD/policy identity and that its result was correlated, persisted, recovered, and returned without duplication.

That is necessary, but it is not the same as proving that the semantic review itself was sufficiently deep.

The research question is:

> How can MimiSeek make semantic-review quality more explicit, falsifiable, measurable, and learnable without turning reviewer self-report, majority voting, or uncontrolled multi-agent recursion into new authority?

The distinction to preserve is:

```text
process correctness
    correct target / policy / reviewer / execution / persistence

            is not the same as

semantic review quality
    relevant system properties were actually examined with adequate evidence
```

A complete diff is evidence that the changed bytes were available. It is not evidence that every material semantic risk was examined.

## Boundary to preserve

Accepted ADR 0013 remains authoritative.

The current `REVIEW_JOB_V1` should remain an atomic unit:

```text
one immutable review job
    -> one fresh reviewer execution
    -> one correlated terminal result
```

This research must not silently turn a review job into:

```text
workers[]
results[]
votes[]
```

or give MimiSeek consumer finding-adjudication, remediation, terminal-acceptance, merge, promotion, or distribution authority.

Consumer repositories continue to own project-specific consequences. Reviewer agreement is not ground truth. A MimiSeek review result does not become more authoritative merely because multiple workers repeat it.

## Research thesis

The next quality improvement should come from making four things explicit:

1. **semantic coverage** — which material properties were examined, skipped, inapplicable, or blocked by insufficient evidence;
2. **structured findings** — claims and supporting evidence that can be individually tracked and falsified;
3. **falsification** — deliberate attempts to disprove consequential candidate findings before treating them as robust review evidence;
4. **bounded orchestration strategy** — targeted additional passes only when risk/evidence warrants them, with strict limits and explicit unresolved outcomes.

These are review-quality mechanisms, not execution-transport mechanisms.

## Hypothesis 1 — evidence-backed semantic coverage

A review should be able to distinguish at least:

```text
REVIEWED_NO_FINDING
NOT_APPLICABLE
INSUFFICIENT_EVIDENCE
NOT_REVIEWED
```

for material semantic surfaces.

Examples of surfaces include, when actually relevant to the diff and governing architecture:

- lifecycle/state transitions;
- persistence/durability;
- crash/restart/recovery;
- concurrency/CAS/idempotence;
- authority/ownership;
- credentials/security/privacy;
- provenance/identity;
- external side effects;
- compatibility/migration;
- bounded transport/delivery semantics.

The surface set must **not** be a universal fixed checklist. It should be derived from the exact diff, accepted governing policy, relevant architecture/ADR boundaries, and discovered dependencies.

### Proposed research artifact

A possible future artifact is:

```text
REVIEW_COVERAGE_V1

identity:
  repository
  pr_number
  base_sha
  head_sha
  review_policy_ref
  reviewer_identity

surfaces:
  - surface_id
    status
    invariant_or_question
    evidence_refs[]
    notes
```

### Anti-checkbox requirement

Coverage must not be accepted merely because the reviewer says "checked concurrency".

A positive coverage claim should carry evidence of what was actually examined, for example:

- exact file/symbol/commit refs;
- governing invariant or ADR ref;
- state-transition path;
- test or runtime evidence;
- external API/authority evidence;
- concrete counterexample path that was considered.

The goal is not to certify hidden reasoning. The goal is to make observable review scope and evidence sufficiently explicit that later learning can distinguish different failure modes.

## Hypothesis 2 — structured findings beside the terminal result

A monolithic human-readable report is useful for users but weak as a long-term machine-learning/evaluation substrate.

Do not mutate the accepted `REVIEW_RESULT_V1` contract merely to pursue this idea. A future versioned structured layer can coexist with the existing terminal result.

A possible finding artifact is:

```text
FINDING_V1

finding_id
severity
title
claim
violated_invariant
reasoning_class

evidence:
  source_refs[]
  files[]
  symbols[]
  commits[]
  tests[]
  runtime_evidence[]

uncertainty
falsification_attempt
```

`confidence=95%` is intentionally not the target. Model-generated confidence percentages are not sufficient evidence.

The more useful field is:

> What concrete path or evidence was examined in an attempt to show that this finding is wrong?

Structured findings should make it possible later to answer:

- which invariant a finding claims is violated;
- what exact evidence supports it;
- whether it was later confirmed/rejected/superseded;
- whether two findings are duplicates of one root cause;
- which classes of defects a reviewer tends to miss or over-report.

## Hypothesis 3 — explicit falsification

A consequential candidate finding should sometimes be challenged asymmetrically.

The challenge task is not:

> Review the whole PR again.

It is:

> Try to prove that candidate finding Fxxx is false. Find the strongest valid path under which the claimed invariant is actually preserved.

Possible internal candidate states:

```text
SUPPORTED
REJECTED
UNRESOLVED
```

This state is about a candidate finding inside a review procedure. It does not replace the terminal `PASS / FINDINGS / ABSTAIN` language.

Falsification should initially be targeted rather than universal. Candidate triggers may include:

- HIGH/CRITICAL findings;
- findings that block acceptance;
- findings with incomplete or indirect evidence;
- findings whose consequence depends on subtle recovery/concurrency/authority behavior.

A false-positive finding that fails a strong falsification pass is valuable learning evidence.

## Hypothesis 4 — keep Review Job atomic; add Review Run above it

If multiple semantically different review passes become useful, introduce a higher-level procedure rather than expanding one job into a multi-worker aggregate.

Conceptually:

```text
REVIEW_RUN_V1

review_identity
review_strategy_ref
jobs:
  J1 general semantic review
  J2 targeted recovery/concurrency review
  J3 falsify F001
aggregation_policy
final_procedure_state
```

The intended distinction is:

```text
Review Job
  one independent reviewer execution/result

Review Run
  bounded orchestration of one or more semantically distinct jobs
```

The higher layer must not use majority vote as truth. Additional jobs should have deliberately different responsibilities, for example:

- general reviewer — broad semantic search;
- risk specialist — one difficult surface;
- falsifier — attack an existing candidate finding;
- gap reviewer — examine only an explicitly uncovered surface.

## Hypothesis 5 — bounded adaptive orchestration

Not every PR needs the same number of review passes.

A future strategy may classify **review-procedure risk**, not defect truth. The classifier may decide how much review effort to allocate; it must not decide whether the code is correct.

A research-only candidate scale is:

```text
LOW
  documentation / isolated declarative change
  -> one general pass

NORMAL
  ordinary bounded code change
  -> one general pass
  -> targeted verification only if needed

HIGH
  state machine / persistence / concurrency / security
  -> general pass
  -> targeted specialist or falsification where warranted

CRITICAL
  credentials / authority / irreversible external writes / recovery boundary
  -> multiple distinct semantic paths
  -> explicit coverage closure or unresolved outcome
```

This mapping must not become production policy merely because it is written here. It requires evidence that the chosen triggers improve recall/false-positive behavior at acceptable cost.

## Hypothesis 6 — semantic budget and LoopGuard

Reasoning orchestration needs the same no-blind-retry discipline already being established for execution/publication.

Without a semantic budget, a system can recurse indefinitely:

```text
review
  -> doubt
  -> rereview
  -> challenger
  -> reviewer of challenger
  -> challenger of reviewer
  -> ...
```

A future strategy should be explicitly bounded. Example research limits:

```text
max_general_passes = 1
max_targeted_passes_per_surface = 1
max_falsification_attempts_per_finding = 1
```

If material disagreement remains after the allowed evidence-gathering/falsification path, the procedure should represent it as unresolved rather than spawning unbounded additional workers.

For a release-critical unresolved condition, terminal `ABSTAIN` may be the correct fail-closed consequence under the consumer's governing policy.

## Hypothesis 7 — review strategy identity

Once orchestration choices materially affect review quality, the strategy itself needs immutable identity.

A possible future field is:

```text
review_strategy_ref=<immutable version/content identity>
```

This must remain distinct from:

- reviewer source/version;
- model/provider identity;
- review policy identity;
- worker profile;
- execution identity.

Otherwise later evaluation cannot distinguish whether behavior changed because of:

- reviewer instruction changes;
- model changes;
- evidence preparation changes;
- extra specialist/falsification passes;
- different orchestration thresholds.

Do not add `review_strategy_ref` to current public contracts until more than one meaningful strategy exists and the identity has operational value.

## Hypothesis 8 — Evidence Manifest as an index, never authority

A future MimiSeek review procedure may prepare an evidence index such as:

```text
EVIDENCE_MANIFEST_V1

repository identity
PR / BASE / HEAD identity
changed-file inventory
immutable authority refs
CI refs
relevant accepted ADR refs
required evidence classes
```

The manifest must not become "trust MimiSeek" input.

Where governing policy requires independent reconstruction, the reviewer must still independently read/verify the underlying GitHub/repository source. The manifest is only an index of evidence classes and expected source locations so a reviewer is less likely to omit a required class.

## Hypothesis 9 — distinguish why a review missed

Coverage information would allow the learner to distinguish at least:

```text
COVERAGE_MISS
  relevant surface was never examined

REASONING_MISS
  surface was examined but invariant was misunderstood

EVIDENCE_MISS
  conclusion used missing/wrong/incomplete evidence

FALSIFICATION_FAILURE
  wrong conclusion survived an inadequate challenge
```

These are materially different learning events.

For example, a later confirmed recovery defect should not teach the same lesson when:

- recovery was never inspected;
- recovery was inspected but a second writer was overlooked;
- the reviewer lacked required restart evidence;
- a candidate finding was incorrectly rejected during falsification.

This distinction may improve both reviewer rules and orchestration strategy.

## Hypothesis 10 — learn orchestration separately from reviewer instructions

The slow learning loop should eventually be able to improve two independent things:

1. reviewer mechanics/instructions;
2. review strategy.

Example:

```text
observed history:
  persistent-state + restart changes correlate with missed concurrency defects

possible reviewer improvement:
  enumerate all recovery writers

possible strategy improvement:
  automatically add one targeted recovery pass for this change class
```

The second is not a reviewer-prompt change. It is an orchestration-policy change and should be evaluated separately.

## Evaluation questions for review strategy

Candidate metrics include:

- defect recall;
- critical-defect recall;
- false-positive rate;
- unsupported-finding rate;
- unresolved rate;
- semantic coverage completion;
- median worker/job count;
- review latency;
- review execution cost where measurable.

`unsupported-finding rate` is especially useful: it measures findings stated as real defects that later fail evidence-backed falsification/adjudication.

No metric should treat reviewer agreement or majority vote as ground truth. Ground truth remains governed adjudicated evidence.

## Sequencing recommendation

Do not implement multi-pass review orchestration before the atomic single-job execution path is physically reliable.

Recommended sequence:

```text
1. finish/prove current single REVIEW_JOB_V1 E2E
   origin -> MimiSeek -> generic session substrate -> fresh reviewer
          -> result -> durable MimiSeek state -> origin return

2. physically exercise restart / ambiguity / no-duplicate launch and return

3. perform a bounded review-quality research decision

4. if accepted narrowly, first implementation slice:
   REVIEW_COVERAGE_V1 + structured FINDING_V1 evidence

5. evaluate whether those artifacts actually improve learning/evaluation

6. only then consider REVIEW_RUN_V1, falsifier/specialist passes,
   adaptive orchestration, and review_strategy_ref
```

This ordering avoids building sophisticated multi-pass reasoning on top of unstable execution/delivery semantics.

## Explicit non-goals of this research

- no change to current `REVIEW_JOB_V1` runtime semantics;
- no new CAP/session capability requirement;
- no live reviewer launch or return delivery;
- no consumer repository write authority;
- no consumer adjudication/fix/merge authority;
- no reviewer majority voting;
- no automatic promotion/distribution authority;
- no universal static semantic checklist;
- no claim that reviewer self-reported coverage proves correctness;
- no unbounded review/challenger recursion;
- no immediate production risk classifier;
- no claim that this document changes canonical architecture.

## Research questions before any architecture decision

1. What is the minimum useful evidence-backed shape for semantic coverage?
2. Which coverage states can be verified externally enough to be useful rather than decorative?
3. Should structured findings be a companion artifact or a future version of the terminal result contract?
4. Which finding severities/classes justify a falsification pass?
5. What evidence is required to classify a candidate finding `SUPPORTED`, `REJECTED`, or `UNRESOLVED`?
6. What bounded strategy improves critical-defect recall without unacceptable false-positive/cost growth?
7. Which change-risk signals are reliable enough to drive targeted passes?
8. How should strategy identity be versioned and frozen for evaluation?
9. How should coverage/reasoning/evidence/falsification misses enter the existing learning-event model?
10. Which historical BUGGY/FIXED cases can evaluate strategy changes without leakage?

## Decision gate

This document is intentionally not an ADR.

After the current atomic Track R single-job E2E/restart/ambiguity path is accepted, a separate governed research/architecture change may choose:

```text
ACCEPT_NARROW
DEFER
REJECT
```

for review-quality orchestration.

An `ACCEPT_NARROW` decision should define only the smallest evidence-backed first slice and preserve:

- atomic `REVIEW_JOB_V1` semantics;
- consumer authority;
- independent exact-head review requirements;
- ground truth from adjudicated evidence rather than reviewer agreement;
- bounded/no-blind orchestration;
- separation of reviewer identity, review policy, execution identity, and future strategy identity.

Until such a decision is independently accepted, this file is a research record only.