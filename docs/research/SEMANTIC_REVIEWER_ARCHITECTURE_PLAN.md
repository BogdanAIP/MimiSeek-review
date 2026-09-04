# MimiSeek semantic reviewer architecture research plan

Status: **research only / non-authoritative / no production architecture selected**

Research baseline: 2026-09-04.

This document is the unified research plan for MimiSeek's future semantic reviewer architecture. It synthesizes the reviewer-context research from PR #6, the review-quality/orchestration research from PR #18, and the later architecture ideas around finding lifecycle, review planning, evidence quality, defect-pattern memory, authority extraction, strategy evaluation, and cost-aware orchestration.

It intentionally does **not** change current product/runtime/acceptance authority, accepted ADR 0013, `REVIEW_JOB_V1`, the current durable GitHub ledger/publication boundary, consumer repository authority, reviewer promotion authority, distribution authority, or merge semantics.

The purpose of this plan is to stop treating context architecture, review observability, finding memory, falsification, and orchestration as unrelated ideas. They are different layers of one reviewer system and should be researched, measured, and accepted in dependency order.

## 1. Accepted boundary that this research must preserve

Accepted architecture already establishes a lower execution/control-plane layer:

```text
consumer project chat
    -> explicit exact-identity review request
    -> MimiSeek REVIEW_JOB_V1 coordination
    -> generic external fresh-worker/session capability
    -> one fresh reviewer execution
    -> one correlated REVIEW_RESULT_V1
    -> durable MimiSeek-owned result state
    -> generic return/wake delivery
    -> consumer workflow continues
```

This research starts **above** that atomic execution boundary.

The following remain accepted constraints rather than research questions:

- one `REVIEW_JOB_V1` represents one immutable review target and one fresh reviewer execution/result;
- generic transport/session infrastructure must remain project-neutral and must not interpret GitHub PR semantics or `PASS/FINDINGS` semantics;
- consumer repositories own review readiness, project-local policy, finding adjudication, remediation, re-review decisions, terminal acceptance, and merge consequences;
- MimiSeek may coordinate review execution and may later improve reviewer methodology, but a review-job `PASS` is not consumer merge authority and not MimiSeek reviewer-promotion authority;
- reviewer agreement or majority vote is not ground truth;
- ground truth comes from governed adjudicated evidence, reproducible behavior, accepted fixes, and other accepted evidence;
- private session/browser authority must not leak into public GitHub review-job state;
- ambiguous launch, publication, delivery, identity, evidence, or policy must fail closed rather than guess through;
- a change to reviewer quality architecture must not weaken the repository-development acceptance policy governing that same change.

## 2. Why one unified plan is needed

The earlier research naturally separated into three questions:

1. **PR #6 — reviewer context/capabilities:** what can one reviewer see and do?
2. **PR #18 — review quality/orchestration:** how can review coverage, findings, falsification, and additional passes be made explicit and measurable?
3. **Later architecture ideas — review knowledge/evolution:** how can findings persist across review cycles, recurring defect patterns become reusable reviewer knowledge, and review strategies themselves be evaluated and improved?

These are not independent products.

A reviewer cannot produce trustworthy semantic coverage if it cannot reach the relevant unchanged repository evidence. A finding lifecycle is not useful if findings are not structured. Adaptive multi-pass review is premature if one well-equipped reviewer has not first been measured. A strategy learner is not trustworthy if strategy identity, evidence leakage boundaries, and replay ground truth are not explicit.

The resulting dependency chain is:

```text
RELIABLE EXECUTION
    ↓
CONTEXT + CAPABILITIES
    ↓
PLANNING + EVIDENCE INDEXING
    ↓
SEMANTIC COVERAGE + STRUCTURED FINDINGS
    ↓
FINDING LIFECYCLE + OUTCOME MEMORY
    ↓
DEFECT PATTERNS + COUNTEREXAMPLES
    ↓
BOUNDED ORCHESTRATION
    ↓
STRATEGY EVALUATION + EVOLUTION
```

## 3. Architectural overview

### Layer 0 — reliable review execution

Owner: accepted Track R architecture.

Question:

> Can MimiSeek reliably execute exactly one independent review for one exact immutable target and durably return its result?

Existing concepts include:

- `REVIEW_JOB_V1`;
- immutable repository/PR/BASE/HEAD/`review_policy_ref` identity;
- exact reviewer/execution correlation;
- durable result bytes/digest;
- launch/publication/return claim states;
- `*_UNKNOWN` reconciliation states;
- restart/recovery/no-blind-retry behavior;
- source-currentness recheck;
- MimiSeek-owned GitHub ledger/publication state.

This unified semantic-review plan does not redefine Layer 0.

### Layer 1 — reviewer context and capabilities

Primary predecessor: PR #6.

Question:

> Can one reviewer independently reach enough repository evidence to perform strong semantic review?

Candidate capability stack:

```text
REVIEW_CONTEXT_CORE
    ↓
immutable repository / BASE / HEAD / policy identity
    ↓
primitive read-only repository exploration
    ↓
optional structural navigation
    ↓
optional bounded validation/execution
```

The reviewer, not CAP or another transport layer, should decide which unchanged repository evidence is semantically relevant.

### Layer 2 — review planning and evidence indexing

Question:

> Before semantic conclusions are produced, can the review procedure explicitly identify the authority, evidence classes, and semantic surfaces that need examination without leaking expected answers?

Candidate research artifacts:

- `AUTHORITY_MANIFEST_V1`;
- `EVIDENCE_MANIFEST_V1`;
- `REVIEW_PLAN_V1`.

These are indexes/planning artifacts, not truth authorities.

### Layer 3 — semantic observability and structured findings

Question:

> Can MimiSeek distinguish "reviewed and no defect found" from "not reviewed" and represent each finding as an evidence-backed machine object?

Candidate research artifacts:

- `REVIEW_COVERAGE_V1`;
- `FINDING_V1`;
- current `REVIEW_RESULT_V1` retained as the small terminal envelope unless evidence later justifies a versioned replacement.

### Layer 4 — finding lifecycle and review knowledge

Question:

> What happened to each finding across adjudication, remediation, new heads, and re-review?

Candidate concepts:

- reviewer assertion state;
- consumer disposition state;
- remediation relation;
- re-review relation;
- finding correlation/fingerprint hints;
- false-positive cause;
- miss classification.

### Layer 5 — reusable review intelligence

Question:

> Which recurring engineering failure mechanics and adversarial scenarios should MimiSeek learn as transferable review knowledge?

Candidate artifacts:

- `DEFECT_PATTERN_V1`;
- counterexample/adversarial scenario library;
- reusable authority/recovery/concurrency/security mechanics;
- pattern-triggered review-plan hints.

### Layer 6 — bounded review orchestration

Question:

> After one strong reviewer baseline exists, when does a second distinct pass improve review quality enough to justify cost/complexity?

Candidate artifacts:

- `REVIEW_RUN_V1` above atomic jobs;
- `review_strategy_ref`;
- targeted specialist jobs;
- finding falsification jobs;
- gap/coverage-audit jobs;
- semantic budget / LoopGuard;
- explicit unresolved outcomes rather than recursive worker spawning.

### Layer 7 — strategy evaluation and evolution

Question:

> Which reviewer/context/orchestration strategy actually performs better on governed evidence, and how should improved strategies become default without self-certification?

Candidate mechanisms:

- historical replay corpus;
- shadow review;
- reviewer/strategy performance profiles;
- semantic risk features;
- adaptive review depth;
- cost/latency accounting;
- fixed evaluation gate for strategy candidates;
- independent `PROMOTE / REJECT / ABSTAIN` style decision for default-strategy changes if later architecture accepts that lifecycle.

## 4. Layer 1 — reviewer context and capability research

### 4.1 Immutable provider/Git authority

For provider-backed review, repository truth must come from exact remote/provider identities and immutable Git objects rather than an arbitrary local working tree.

Candidate control sequence:

```text
live PR identity
 -> exact BASE_SHA / HEAD_SHA
 -> exact commit/tree/blob identity
 -> reviewer context/session bound to those immutable objects
 -> explicit local parity only as separate evidence
```

Useful local parity states may include:

`MATCH | LOCAL_AHEAD | REMOTE_AHEAD | DIVERGED | DIRTY | LOCAL_ONLY | REMOTE_UNAVAILABLE`.

A local match does not replace remote PR authority. A remote PR does not prove a local workspace is clean.

### 4.2 Explicit context incompleteness

Silent omission is incompatible with authoritative `PASS`.

The reviewer/context layer must be able to represent relevant incompleteness such as:

- binary/non-UTF8 content;
- LFS pointers;
- submodules/symlinks;
- unsupported language/index coverage;
- oversized snapshots;
- unavailable external evidence;
- bounded tool-session limitations.

The correct response to unresolved material context may be `INSUFFICIENT_EVIDENCE`, `ABSTAIN`, or another fail-closed state rather than silent truncation.

### 4.3 Core context envelope

A research-only candidate:

```text
REVIEW_CONTEXT_CORE_V1

repository identity
PR identity
BASE commit/tree
HEAD commit/tree
review_policy_ref
applicable accepted instructions/policy refs
changed-file inventory
exact diff
relevant CI/check identity
context/session capability identity
explicit completeness/omission declarations
```

The core envelope is not expected to contain all repository source.

### 4.4 Primitive read-only repository exploration

Candidate capability family:

```text
list_tree(ref, path)
read_file(ref, path/range)
search_text(ref, query/path scope)
show_diff(base, head, path)
show_history(path/symbol/range)
```

No arbitrary repository mutation is required for normal semantic review.

The reviewer must retain the ability to inspect unchanged code selected by its own reasoning.

### 4.5 Structural navigation

Optional higher-level capabilities to evaluate:

```text
find_symbol
find_definition
find_references
find_implementations
find_callers
find_importers
find_dependents
```

Each result should expose retrieval/provenance class where possible:

- precise compiler/index-derived;
- parser-derived;
- search/heuristic;
- incomplete/unsupported.

Critical rule candidate:

> `not found in graph/index` must not mean `does not exist` or `is irrelevant` unless the concrete indexing contract proves completeness for that mechanism.

This preserves dynamic registration, configuration, reflection, generated code, plugins, and unsupported-language cases.

### 4.6 Bounded validation/execution

Candidate read/validation capabilities:

- run repository-governed focused tests;
- run predefined static analyzers/lints/type checks;
- inspect already-produced CI logs/artifacts;
- run a bounded reproduction harness when governing policy permits it.

A test failure can be direct evidence. A test pass is not proof that an untested invariant is correct.

### 4.7 Context architecture experiment matrix

Do not select a production context architecture by intuition alone.

Research variants:

```text
A — public provider reconstruction baseline
B — deterministic whole-repository snapshot
C — agentic primitive read-only repository session
D — C + structural definitions/references/callers/dependency hints
E — D + bounded test/static/reproduction validation
```

Research gates:

- B vs C — snapshot sufficiency versus agentic exploration;
- C vs D — structural navigation value;
- D vs E — bounded validation value.

Only after a strong E-like single-reviewer baseline exists should multi-pass variants be measured.

## 5. Layer 2 — authority, evidence, and review planning

### 5.1 Authority manifest

A future `AUTHORITY_MANIFEST_V1` may index the authority chain applicable to one exact review target.

Example:

```text
AUTHORITY_MANIFEST_V1

repository
BASE_SHA
HEAD_SHA
review_policy_ref

accepted_authority_refs:
  BASE AGENTS.md
  BASE DEVELOPMENT_PROTOCOL
  delegated accepted review skill/policy
  applicable accepted ADRs

head_target_semantics_refs:
  proposed HEAD policy/architecture files

live_state_refs:
  current PR identity
  exact-head CI
  external accepted capability refs where applicable
```

The manifest is **not** a replacement for independent authority reconstruction when policy requires it. It is an index designed to reduce omission and precedence errors.

### 5.2 Evidence manifest

A future `EVIDENCE_MANIFEST_V1` may index evidence classes expected for the review:

```text
E001 PR identity
E002 BASE identity
E003 HEAD identity
E004 changed-file inventory
E005 immutable authority refs
E006 exact diff
E007 exact-head CI
E008 relevant runtime/test artifacts
E009 relevant accepted external capability evidence
...
```

The reviewer must verify underlying sources rather than trust the manifest because MimiSeek listed them.

### 5.3 Evidence quality metadata

The research should avoid a single magical `DIRECT` flag.

A stronger evidence description may separate:

```text
source_kind
verification_state
identity_binding
freshness
derivation
```

Examples:

```text
PR body says CI passed
source_kind = human_claim
verification_state = CLAIMED
identity_binding = unresolved
```

versus:

```text
live GitHub workflow run
source_kind = provider_workflow
verification_state = VERIFIED_DIRECT
identity_binding = exact_head
freshness = current
```

The reviewer should prefer stronger evidence without pretending that any one metadata label proves correctness.

### 5.4 Review plan

A candidate `REVIEW_PLAN_V1` should be derived dynamically from:

- exact diff and changed concepts;
- accepted architecture/policy invariants;
- changed and unchanged dependency paths;
- risk features;
- historical defect patterns;
- required evidence classes;
- known context omissions.

Example:

```text
REVIEW_PLAN_V1

changed_concepts:
  persistent review-job state
  external publication retry

semantic_surfaces:
  lifecycle
  persistence
  crash/restart
  concurrency/CAS
  ambiguous external side effect
  authority
  credential/privacy boundary

required_evidence_classes:
  full BASE..HEAD diff
  durable state transitions
  restart tests
  exact-head CI
  accepted authority refs
```

The plan must not leak expected defects, finding count, post-fix knowledge, or ground truth.

### 5.5 Open-ended review remains mandatory

A review plan can itself create blind spots if treated as exhaustive authority.

Therefore a future procedure should preserve an explicit open-ended semantic pass:

> After planned surfaces are examined, search for material defects outside the precomputed plan.

The plan is a coverage scaffold, not a finite proof that no other semantic risk exists.

## 6. Layer 3 — semantic coverage and structured findings

### 6.1 Coverage states

A review should distinguish at least:

```text
REVIEWED_NO_FINDING
FINDING
NOT_APPLICABLE
INSUFFICIENT_EVIDENCE
NOT_REVIEWED
```

for material semantic surfaces.

A zero-finding result is not equivalent to complete review coverage.

### 6.2 Evidence-backed coverage

Coverage must not become reviewer self-attestation such as:

> concurrency checked = yes

A positive coverage record should reference observable evidence of what was examined, for example:

- exact files/symbols/commits;
- governing invariant/ADR refs;
- state-transition paths;
- callers/dependencies;
- tests/runtime evidence;
- concrete adversarial/counterexample paths considered.

The goal is not to expose hidden chain-of-thought. The goal is to record review scope/evidence sufficiently for later diagnosis and learning.

### 6.3 Candidate `REVIEW_COVERAGE_V1`

```text
REVIEW_COVERAGE_V1

review identity

surfaces[]:
  surface_id
  status
  invariant_or_question
  evidence_refs[]
  notes
```

The surface set must be derived from the concrete target rather than a universal static checklist.

### 6.4 Structured finding object

A candidate `FINDING_V1`:

```text
FINDING_V1

finding_id
severity
category
claim
affected_scope
violated_invariant
reasoning_class

authority_refs[]
evidence_refs[]
files[]
symbols[]
commits[]
tests[]
runtime_evidence[]

uncertainty
falsification_summary
```

Avoid model-generated numeric confidence as a substitute for evidence.

Do not store private chain-of-thought. Store bounded rationale/evidence sufficient to reconstruct the claim.

### 6.5 Keep `REVIEW_RESULT_V1` small for now

Do not replace the accepted terminal result contract merely because richer semantics are useful.

Initial research preference:

```text
REVIEW_RESULT_V1
    |
    +-- REVIEW_COVERAGE_V1
    +-- FINDING_V1[]
    +-- EVIDENCE_MANIFEST_V1
```

These may be companion/digest-bound artifacts.

A future `REVIEW_RESULT_V2` should be considered only after the structured semantics have stabilized and a versioned replacement provides clear operational value.

## 7. Layer 4 — finding lifecycle and review knowledge

### 7.1 Do not collapse reviewer assertion and consumer adjudication

A finding has multiple authorities over time.

Reviewer-internal assertion state may use concepts such as:

```text
SUPPORTED
REJECTED
UNRESOLVED
```

Consumer-governed disposition may use concepts such as:

```text
UNKNOWN
CONFIRMED
REJECTED
SUPERSEDED
```

Remediation/re-review relation may use concepts such as:

```text
NONE
REMEDIATION_EVIDENCE
REREVIEW_REQUIRED
NO_LONGER_REPRODUCED
```

MimiSeek must not declare a consumer defect `FIXED` merely because an implementation changed or a reviewer stopped reproducing the finding. Consumer policy/adjudication remains authoritative.

### 7.2 Finding history across heads

The system should be able to preserve chains such as:

```text
HEAD A
  F001 reported
  consumer disposition = CONFIRMED

HEAD B
  remediation evidence exists
  prior exact-head result is stale for acceptance

fresh review of HEAD B
  F001 no longer reproduced
```

The history must not imply that review of HEAD A accepted HEAD B.

### 7.3 Finding correlation

Long-lived PRs need help recognizing when similar findings across review cycles may represent the same root cause.

A candidate `finding_fingerprint` may use normalized hints such as:

- category;
- affected semantic object;
- violated authority/invariant;
- normalized claim shape.

The fingerprint must be a **correlation hint**, not immutable identity and not automatic root-cause truth.

Possible relation states:

```text
POSSIBLE_SAME_ROOT_CAUSE
CONFIRMED_SAME_ROOT_CAUSE
DISTINCT_FINDING
UNRESOLVED_RELATION
```

where any authoritative cross-cycle conclusion must be evidence-backed.

### 7.4 False-positive tracking

Rejected findings are valuable learning evidence.

A later normalized learning record should be able to capture why a finding failed, for example:

- misunderstood CAS semantics;
- wrong authority precedence;
- stale evidence;
- incomplete caller analysis;
- heuristic graph result treated as complete;
- speculative consequence without reproducible path.

This extends the existing `OUR_FALSE_POSITIVE` concept with causal structure rather than only outcome label.

### 7.5 Miss tracking

Later-confirmed defects missed by a suitable earlier review should be classified carefully.

Candidate causal classes:

```text
COVERAGE_MISS
REASONING_MISS
EVIDENCE_MISS
AUTHORITY_MISS
FALSIFICATION_FAILURE
```

Semantic domain is a separate dimension, for example:

```text
concurrency
persistence
security
authority
lifecycle
compatibility
runtime
```

Do not collapse `CONCURRENCY_MISS` into the same axis as `EVIDENCE_MISS`: one describes domain, the other describes why the review failed.

Different-head/timing/leakage conditions must still support the inference before a run is labeled a miss.

## 8. Layer 5 — reusable defect patterns and counterexamples

### 8.1 `DEFECT_PATTERN_V1`

MimiSeek should eventually learn transferable mechanics rather than historical SHA/file answers.

Candidate example:

```text
DEFECT_PATTERN_V1
id = AMBIGUOUS_EXTERNAL_SIDE_EFFECT

preconditions:
  external mutation
  acknowledgement/timeout ambiguity possible
  retry/recovery path exists

review_questions:
  was consequence claimed durably before mutation?
  can applied-versus-absent state be reconciled?
  is blind resend forbidden?
  does restart preserve the unresolved claim?
```

Other pattern families may include:

- stale authority selection;
- uncorrelated external result;
- multiple durable writers outside one serialization boundary;
- incomplete recovery fencing;
- optimistic currentness after source movement;
- hidden project-specific semantics in generic transport;
- unsafe migration/compatibility assumptions;
- graph-only false completeness.

### 8.2 Counterexample/adversarial library

Each defect pattern may have reusable scenarios that ask the reviewer to prove correctness under stress without telling it that a defect exists.

Example for ambiguous external effects:

```text
action succeeds / acknowledgement lost
restart immediately after claim
concurrent retry from another worker
duplicate callback
remote state visible before local state
local fence visible before remote state
```

Example for session/launch lifecycle:

```text
crash before claim
crash after claim
ack loss
stale tab
browser restore
same URL / new runtime
```

The reviewer receives scenarios/questions, not expected findings.

### 8.3 Pattern-triggered planning

Historical evidence may later justify adding one targeted review surface when a change matches a known pattern.

Example:

```text
observed history:
  persistent state + restart changes correlate with missed multi-writer defects

reviewer-method change:
  enumerate every independently reachable writer

strategy change:
  add one targeted recovery/concurrency pass for this risk class
```

Reviewer methodology and orchestration strategy must remain independently identifiable and evaluable.

## 9. Layer 6 — falsification and bounded orchestration

### 9.1 Finding falsification

A consequential candidate finding may receive an explicit adversarial challenge:

> Try to prove that F001 is false. Find the strongest valid path under which the claimed invariant is actually preserved.

Candidate internal outcome:

```text
SUPPORTED
REJECTED
UNRESOLVED
```

The falsifier is not asked to review the entire PR again and is not asked to agree with the primary reviewer.

Initial trigger candidates:

- HIGH/CRITICAL findings;
- acceptance-blocking findings;
- incomplete/indirect evidence;
- subtle recovery/concurrency/authority consequences;
- findings with high historical false-positive risk.

Universal falsification of every low-severity observation is not an initial requirement.

### 9.2 Preserve atomic `REVIEW_JOB_V1`

Do not expand one job into:

```text
workers[]
results[]
votes[]
```

One job remains one fresh execution/result.

### 9.3 `REVIEW_RUN_V1` above jobs

If multi-pass review proves useful, add a higher procedure layer:

```text
REVIEW_RUN_V1

review_identity
review_strategy_ref

jobs:
  J1 general semantic review
  J2 targeted recovery/concurrency review
  J3 falsify F001
  J4 gap review for uncovered surface

aggregation_policy
final_procedure_state
```

The run must not treat majority vote as truth.

Distinct job roles should be asymmetrical:

- general reviewer;
- risk specialist;
- falsifier;
- gap/coverage reviewer.

### 9.4 Semantic budget / LoopGuard

Review orchestration needs the same bounded/no-blind discipline as transport.

Research limits may start with something like:

```text
max_general_passes = 1
max_targeted_passes_per_surface = 1
max_falsification_attempts_per_finding = 1
```

Persistent material disagreement becomes `UNRESOLVED` rather than recursive worker spawning.

For release-critical unresolved uncertainty, consumer governing policy may require terminal `ABSTAIN`.

### 9.5 Strategy identity

Once more than one meaningful orchestration strategy exists, introduce immutable:

```text
review_strategy_ref
```

Keep it distinct from:

- reviewer source/version;
- model/provider;
- review policy;
- worker profile;
- context-capability profile;
- execution identity.

Without this separation, later evaluation cannot tell whether quality changed because of model, reviewer instruction, context capability, or orchestration.

## 10. Layer 7 — risk, profiles, evaluation, and strategy evolution

### 10.1 Risk features before risk scores

Do not start with invented weights such as `+5 concurrency`.

First represent explainable features:

```text
concurrency = true
persistent_state = true
external_side_effect = true
authority_change = true
retry = true
credential_boundary = false
migration = false
```

Later governed outcome data may justify weights/classification thresholds.

Risk classification allocates review effort. It must not decide defect truth.

### 10.2 Adaptive review depth

A future strategy may use risk/evidence to choose bounded depth.

Research-only shape:

```text
LOW
  one general pass

NORMAL
  one general pass
  targeted follow-up only if needed

HIGH
  general pass
  targeted specialist and/or falsification

CRITICAL
  multiple distinct semantic paths
  explicit coverage closure or unresolved outcome
```

This must be measured rather than accepted merely because the categories sound reasonable.

### 10.3 Reviewer/strategy performance profiles

A future profile must not collapse all behavior into one model score.

Performance identity should separate at least:

```text
reviewer source/version
model/provider
context-capability profile
review_strategy_ref
review policy class
```

Possible metrics:

- reviews total;
- critical finding recall;
- supported-finding rate;
- false-positive rate;
- miss rate;
- coverage completion;
- authority errors;
- stale-identity failures;
- unresolved rate;
- domain-specific performance for concurrency/security/lifecycle/docs/etc.

Use sample sizes and confidence intervals/statistical caution where appropriate; do not turn sparse observations into a leaderboard truth.

### 10.4 Replay/regression corpus

Historical real PR evidence is a core evaluation asset.

A governed replay case may contain:

```text
immutable PR snapshot
known BUGGY target defect
corresponding FIXED state
adjudicated accepted/rejected finding evidence
known remediation relation
```

New reviewer/context/strategy candidates can be tested blind:

- does the target defect reappear on BUGGY?
- does the old finding disappear on FIXED?
- are new false positives emitted?
- what semantic coverage is achieved?
- what tools/context were required?

### 10.5 Leakage controls

Evaluation must separate:

```text
learning/training evidence
!= fixed evaluation corpus
!= later holdout/shadow evidence
```

Expected finding text/category/count and later fix/disposition must remain hidden from candidate reviewer context unless the experiment explicitly tests that condition.

Historical public comments/fixes can invalidate a case for blind evaluation and must be recorded as leakage risk.

### 10.6 Strategy evaluation

Compare strategies on the same governed cases where possible:

```text
same model
same reviewer version
same policy
same immutable PR snapshot

different review_strategy_ref
```

Candidate metrics:

- defect recall;
- critical-defect recall;
- false-positive rate;
- unsupported-finding rate;
- unresolved rate;
- semantic coverage completion;
- worker/job count;
- tool/context usage;
- latency;
- execution cost where measurable.

Do not optimize cost before establishing an acceptable semantic-quality region.

### 10.7 Strategy promotion lifecycle

If strategy changes later become consequence-bearing defaults, do not make every experimental strategy default immediately.

Candidate progression:

```text
strategy candidate
    ↓
offline replay corpus
    ↓
shadow review
    ↓
limited production evidence
    ↓
fresh independent evaluation
    ↓
PROMOTE / REJECT / ABSTAIN
```

This should reuse existing MimiSeek principles — fixed exam before candidate, no self-defined evaluation, independent promotion authority — rather than create an unrelated weaker governance system.

The exact strategy-promotion contract is future architecture, not selected by this research document.

## 11. Experiment controls inherited from PR #6

The earlier PR #6 research remains valuable as experimental evidence and method.

Important controls to preserve include:

### 11.1 Positive / stale / hidden-defect controls

A useful experiment suite includes materially different cases:

- accepted exact target where `PASS` is possible;
- superseded target that must become `STALE`;
- known defective immutable target where expected findings/count are hidden;
- later rejected/false-positive cases.

A PASS-shaped response alone is not reviewer-quality evidence.

### 11.2 Unchanged-caller control

Changed producer/API semantics while an unchanged caller still relies on old behavior.

Purpose: distinguish local diff review from repository impact exploration.

### 11.3 Similar-name false-reference control

Multiple plausible same/similar symbols.

Purpose: measure heuristic search versus precise navigation and prevent false completeness.

### 11.4 Dynamic registration/configuration control

Behavior connected through plugin/registry/config string rather than obvious static call graph.

Purpose: falsify graph-only completeness assumptions.

### 11.5 Large-repository/context-pressure control

Relevant unchanged evidence outside the obvious context/shard/ranking boundary.

Purpose: compare deterministic snapshot/context packing with agentic search and explicit oversize behavior.

### 11.6 Validation-value control

Static reading yields a plausible candidate issue that a focused test/reproduction either confirms or disproves.

Purpose: measure precision gain from bounded validation.

### 11.7 FIXED false-positive control

Reviewer sees materially fixed state without being told it is fixed.

Purpose: prevent "stronger" review from merely repeating remembered historical findings.

### 11.8 Governance self-change control

PR changes reviewer/governance instructions in HEAD.

Purpose: prove accepted BASE-derived authority still governs rather than allowing proposed HEAD policy to grade itself.

## 12. Unified research decision gates

The plan should progress through explicit gates rather than accept the whole stack at once.

### Gate E0 — atomic execution readiness

Question:

> Is one Track R review job physically reliable across launch/result/publication/return, restart, ambiguity, and no-duplicate reconciliation?

Until yes, do not make multi-pass orchestration routine infrastructure.

### Gate C1 — snapshot versus agentic exploration

Question:

> Does deterministic snapshot context B match or exceed primitive agentic repository session C on governed real cases within acceptable completeness/size bounds?

Possible decisions:

`ACCEPT_SNAPSHOT | ACCEPT_AGENTIC | HYBRID | DEFER`

### Gate C2 — structural navigation value

Question:

> Does D materially improve quality/efficiency over C without unacceptable false confidence from index incompleteness?

Decision:

`ACCEPT_NARROW | DEFER | REJECT`

### Gate C3 — bounded validation value

Question:

> Does E materially improve precision/recall/severity calibration enough to justify sandbox/test complexity?

Decision:

`ACCEPT_NARROW | DEFER | REJECT`

### Gate Q1 — structured semantic observability

Question:

> Do `REVIEW_PLAN`, evidence-backed `REVIEW_COVERAGE`, and structured `FINDING_V1` materially improve review completeness diagnosis and later learning without becoming checkbox self-attestation?

Decision:

`ACCEPT_NARROW | DEFER | REJECT`

### Gate Q2 — finding lifecycle value

Question:

> Can structured finding/disposition/remediation/re-review relations improve learning and long-PR review continuity without taking consumer adjudication authority?

Decision:

`ACCEPT_NARROW | DEFER | REJECT`

### Gate Q3 — falsification value

Question:

> Does targeted falsification reduce unsupported HIGH/CRITICAL findings enough to justify its cost and latency?

Decision:

`ACCEPT_NARROW | DEFER | REJECT`

### Gate K1 — defect-pattern/counterexample value

Question:

> Do transferable pattern/scenario libraries improve recall or reduce misses without leaking historical answers into evaluation cases?

Decision:

`ACCEPT_NARROW | DEFER | REJECT`

### Gate S1 — multi-pass orchestration value

Question:

> After a strong single-reviewer baseline exists, does `REVIEW_RUN_V1` with asymmetric roles materially improve quality per unit cost/latency?

Decision:

`ACCEPT_NARROW | DEFER | REJECT`

### Gate S2 — adaptive strategy value

Question:

> Can explainable risk features allocate review depth better than a fixed strategy without hiding critical misses or creating unstable policy behavior?

Decision:

`ACCEPT_NARROW | DEFER | REJECT`

## 13. Recommended implementation/research sequence

The architecture plan is unified, but implementation should remain narrow and staged.

### Phase 0 — finish Track R atomic execution

Prove:

- one exact launch;
- exact correlated result;
- durable publication;
- source-currentness recheck;
- exact return/wake;
- restart recovery;
- ambiguous launch/publication/delivery reconciliation;
- no blind duplicate launch/wake.

### Phase 1 — context baseline experiments

Run A/B/C on a small governed hidden corpus.

Decide C1 before building a large repository-context subsystem.

### Phase 2 — capability expansion only if justified

Evaluate D structural navigation and E bounded validation sequentially.

Do not assume graph or execution is required until data show value.

### Phase 3 — semantic observability first implementation slice

If Q1 is accepted narrowly, prefer the first production slice to be:

```text
AUTHORITY/EVIDENCE indexing
REVIEW_PLAN
REVIEW_COVERAGE
FINDING_V1 companion artifacts
```

Do not start with multi-agent orchestration.

### Phase 4 — finding knowledge

If Q2 is accepted:

- finding lifecycle;
- consumer disposition links;
- remediation/re-review relations;
- correlation hints;
- false-positive/miss causal classification.

### Phase 5 — targeted falsification

If Q3 is accepted:

- HIGH/CRITICAL/uncertain candidate findings first;
- one bounded falsification attempt;
- explicit `UNRESOLVED` rather than recursion.

### Phase 6 — defect-pattern and counterexample memory

If K1 is accepted:

- derive generic patterns from adjudicated evidence;
- add adversarial scenarios without expected-answer leakage;
- evaluate patterns on holdout/replay cases.

### Phase 7 — review-run orchestration

Only after the strong single-reviewer path is proven:

- introduce `REVIEW_RUN_V1`;
- add `review_strategy_ref`;
- measure asymmetric specialist/falsifier/gap passes;
- preserve one-job/one-execution semantics below.

### Phase 8 — adaptive depth and strategy evolution

Only after enough outcome data exist:

- use explainable risk features;
- compare fixed versus adaptive strategies;
- build reviewer/strategy profiles;
- account for cost/latency;
- establish governed strategy-evaluation/promotion semantics if justified.

## 14. Relationship to existing MimiSeek stages

This research does not replace the current Stage 1–11 reviewer-evolution roadmap.

Instead, it clarifies what reviewer artifact/capability/strategy may later be learned, evaluated, and released.

Expected relationships:

- Stage 1 historical reconciliation provides initial governed BUGGY/FIXED/false-positive evidence;
- Stage 2 structured evidence export should preserve enough exact identities/findings/dispositions to support future finding lifecycle and replay;
- Stage 3 normalized outcome store becomes the canonical machine learning/evaluation input rather than raw review-job ledger state;
- Stage 4 learning events can later distinguish coverage/reasoning/evidence/falsification misses;
- before Stage 5 creates a promotion-eligible reviewer candidate, accepted reviewer capability architecture and fixed evaluation policy must be sufficiently resolved for that candidate;
- Stage 6 regression/protected-capability evaluation can later test both reviewer methodology and accepted context/exploration capabilities;
- Stage 7 promotion remains independent and policy-bound;
- Stage 8 consumer distribution remains separate and safety-gated;
- Track R remains the bounded operational review execution path and does not itself imply reviewer promotion or consumer installation.

## 15. What should become canonical later versus remain research

### Strong candidate principles already well supported

- exact immutable review identity;
- accepted policy/authority identity;
- repository-wide evidence must be reachable somehow;
- unchanged code can be material review evidence;
- silent context truncation is incompatible with authoritative PASS;
- graphs/search/indexes are retrieval mechanisms rather than source truth;
- candidate findings should be evidence-backed and falsifiable;
- false positives are first-class quality failures;
- reviewer quality and execution-transport reliability must be measured separately;
- one review job should remain one fresh execution/result;
- reviewer agreement is not ground truth;
- context strategy, reviewer methodology, and orchestration strategy should be independently identifiable.

### Still open research questions

- deterministic snapshot versus agentic repository session;
- exact primitive repository tool set;
- need/value of structural graph/index;
- need/value of bounded runnable tests/static tools;
- exact `REVIEW_PLAN/COVERAGE/FINDING` schemas;
- exact finding correlation/fingerprint algorithm;
- falsification trigger policy;
- exact defect-pattern representation;
- whether/when `REVIEW_RUN_V1` materially improves quality;
- risk-model inputs and thresholds;
- exact strategy-promotion lifecycle;
- acceptable latency/compute after semantic-quality floors exist.

## 16. Explicit non-goals

This research plan does not authorize:

- changing current `REVIEW_JOB_V1` semantics;
- turning one review job into a voting pool;
- a universal fixed semantic checklist;
- trusting model self-reported coverage without evidence;
- using model confidence percentages as correctness proof;
- making graph/index absence authoritative;
- consumer finding adjudication by MimiSeek;
- consumer remediation/merge authority by MimiSeek;
- majority voting between reviewers;
- unbounded reviewer/challenger recursion;
- immediate production risk scoring with invented weights;
- automatic promotion/distribution based on review consensus;
- strategy promotion without a separately accepted fixed evaluation boundary;
- treating this research document itself as canonical production architecture.

## 17. PR #6 and PR #18 consolidation policy

This document is intended to become the single research owner for the semantic reviewer architecture question if independently accepted.

PR #6 remains a valuable predecessor research branch containing detailed reviewer-context experiments and external-practice notes. It should not be merged in its old architectural context merely to preserve those ideas.

PR #18 is the current consolidation vehicle because it is based on the modern accepted architecture after ADR 0013, `REVIEW_JOB_V1`, and the MimiSeek-owned durable ledger/publication slice.

If this unified plan is accepted:

- PR #6 may be closed as superseded by the accepted unified research plan while retaining its Git/PR history as research provenance;
- the older `REVIEW_QUALITY_ORCHESTRATION.md` research draft is replaced by this broader plan rather than maintained as a competing owner;
- later architecture decisions should cite this plan but accept/reject specific gates rather than treating all hypotheses here as one all-or-nothing production decision.

## 18. Decision boundary

This document is intentionally **not** an ADR.

It defines one coherent research program and dependency order.

Each consequence-bearing architecture choice should later use a separate governed decision based on measured evidence, with bounded outcomes such as:

```text
ACCEPT_NARROW
DEFER
REJECT
```

The immediate architectural priority remains:

```text
reliable atomic REVIEW_JOB_V1 E2E
    ↓
measure strong single-reviewer context/capability architecture
    ↓
add semantic planning/coverage/structured findings
    ↓
learn finding lifecycle + defect patterns
    ↓
targeted falsification
    ↓
only then measure multi-pass/adaptive strategy value
```

Until the relevant gates are independently accepted, the candidate schemas, tools, profiles, risk model, multi-pass procedure, and strategy lifecycle in this document remain research hypotheses only.
