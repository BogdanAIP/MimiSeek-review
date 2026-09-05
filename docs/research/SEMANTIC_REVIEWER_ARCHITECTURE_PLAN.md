# MimiSeek semantic reviewer architecture research plan

Status: **research only / non-authoritative / no production architecture selected**

Research baseline: 2026-09-05.

This document is the unified research plan for MimiSeek's future semantic-review architecture. It consolidates three previously separate bodies of work:

1. reviewer-context and capability research from predecessor PR #6;
2. semantic coverage, structured findings, falsification, and orchestration research developed in PR #18;
3. later ideas around review planning, evidence quality, finding lifecycle/correlation, defect-pattern memory, authority extraction, replay, reviewer/strategy profiles, adaptive depth, strategy evaluation, and cost accounting.

The purpose of consolidation is to give these ideas one research owner, one dependency order, and explicit decision gates. It does **not** accept the whole stack for production.

This document intentionally does **not** change current product/runtime/acceptance authority, accepted ADR 0013, current `REVIEW_JOB_V1` or `REVIEW_RESULT_V1` semantics, the MimiSeek-owned durable GitHub ledger/publication boundary, consumer authority, reviewer-promotion authority, distribution authority, or merge semantics.

## 1. Accepted boundary this research must preserve

Accepted architecture already provides the lower review-execution/control-plane model:

```text
consumer project
    -> explicit exact-identity review request
    -> MimiSeek REVIEW_JOB_V1 coordination
    -> generic external fresh-worker/session capability
    -> one fresh review execution
    -> one correlated REVIEW_RESULT_V1
    -> durable MimiSeek-owned result state
    -> generic return/wake delivery
    -> consumer workflow continues
```

This research begins **above** that atomic execution boundary.

The following remain accepted constraints rather than open research questions:

- one `REVIEW_JOB_V1` represents one immutable review target and one fresh review execution/result;
- current `REVIEW_RESULT_V1` keeps its accepted terminal review semantics; this research does not silently reinterpret them;
- generic transport/session infrastructure remains project-neutral and must not interpret project-specific GitHub PR or `PASS/FINDINGS` semantics;
- consumer repositories own review readiness, project-local policy/architecture truth, finding adjudication, remediation, re-review decisions, terminal acceptance, and merge consequences;
- a review-job `PASS` is neither consumer merge authority nor MimiSeek reviewer-promotion/distribution authority;
- reviewer agreement or majority vote is not ground truth;
- ground truth comes from governed adjudicated evidence, reproducible behavior, accepted fixes, and other accepted evidence;
- private browser/session capability must not leak into public GitHub coordination state;
- ambiguous identity, launch, publication, delivery, evidence, or policy fails closed;
- a reviewer-quality change cannot weaken the repository-development acceptance authority that governs that same change.

## 2. Why one unified plan is needed

The earlier research addressed three questions.

### PR #6 — context and capabilities

> What can one strong reviewer see and do?

It explored immutable repository context, deterministic snapshot versus agentic repository exploration, unchanged callers, structural navigation, bounded validation, context completeness, and experimental controls.

### PR #18 — review observability and orchestration

> How can MimiSeek show what was actually reviewed and challenge important findings?

It introduced evidence-backed coverage, structured findings, targeted falsification, bounded multi-pass concepts, LoopGuard, and strategy identity.

### Later ideas — review memory and strategy evolution

> How can findings persist across cycles, recurring defects become reusable knowledge, and review strategies themselves be measured and improved?

These questions depend on one another. Coverage is weak if relevant repository evidence is unreachable. Finding lifecycle is weak if findings are unstructured. Multi-pass review is premature before a strong single-reviewer baseline is measured. Strategy learning is unsafe if evidence leakage, strategy identity, ground truth, and evaluation authority are unclear.

The intended research dependency chain is therefore:

```text
RELIABLE ATOMIC EXECUTION
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
TYPED FALSIFICATION + BOUNDED ORCHESTRATION
    ↓
STRATEGY EVALUATION + EVOLUTION
```

## 3. Layer 0 — reliable atomic review execution

Owner: accepted Track R architecture.

Question:

> Can MimiSeek reliably execute exactly one independent review for one immutable target and durably return its exact result?

Existing concepts include:

- `REVIEW_JOB_V1`;
- immutable repository/PR/BASE/HEAD/`review_policy_ref` identity;
- exact reviewer/execution correlation;
- durable result bytes/digest;
- launch/publication/return claim states;
- explicit `*_UNKNOWN` reconciliation states;
- restart/recovery/no-blind-retry behavior;
- source-currentness recheck;
- MimiSeek-owned GitHub ledger/publication state.

This plan does not redefine Layer 0.

### Gate E0 — atomic execution readiness

Before production multi-pass orchestration is considered, one atomic Track R job should be physically proven across:

- exact launch;
- exact result correlation;
- durable publication;
- source-currentness recheck;
- exact return/wake;
- restart/recovery;
- ambiguous launch/publication/delivery reconciliation;
- no blind duplicate launch or wake.

Until E0 passes, multi-pass remains research only.

## 4. Layer 1 — reviewer context and capabilities

Primary predecessor: PR #6.

Question:

> Can one reviewer independently reach enough evidence to perform strong semantic review?

### 4.1 Immutable provider/Git authority

For provider-backed review, repository truth must be bound to exact provider and immutable Git identities rather than an arbitrary local working tree.

Candidate sequence:

```text
live provider PR identity
 -> exact BASE_SHA / HEAD_SHA
 -> exact commit/tree/blob identity
 -> reviewer context bound to those immutable objects
 -> local checkout parity recorded only as separate evidence
```

Useful local parity classes may include:

```text
MATCH
LOCAL_AHEAD
REMOTE_AHEAD
DIVERGED
DIRTY
LOCAL_ONLY
REMOTE_UNAVAILABLE
```

A local match does not replace remote PR authority. Remote PR correctness does not prove a local workspace is clean.

### 4.2 Explicit context completeness

Silent omission is incompatible with authoritative `PASS`.

The context layer must be able to represent material incompleteness such as:

- binary/non-UTF8 content;
- LFS pointers;
- submodules/symlinks;
- unsupported language/index coverage;
- oversized snapshots;
- unavailable external evidence;
- bounded tool-session limitations.

Material unresolved incompleteness should produce `INSUFFICIENT_EVIDENCE`, `ABSTAIN`, or another policy-compatible fail-closed consequence rather than silent truncation.

### 4.3 Candidate core context envelope

Research-only candidate:

```text
REVIEW_CONTEXT_CORE_V1

repository/provider identity
PR identity
BASE commit/tree
HEAD commit/tree
review_policy_ref
applicable accepted policy/instruction refs
changed-file inventory
exact diff
relevant CI/check identity
context/capability identity
explicit completeness/omission declarations
```

The core envelope is not expected to contain the whole repository.

### 4.4 Primitive read-only exploration

Candidate capability family:

```text
list_tree(ref, path)
read_file(ref, path/range)
search_text(ref, query/path scope)
show_diff(base, head, path)
show_history(path/symbol/range)
```

The reviewer must retain the ability to choose and inspect unchanged evidence. CAP or another transport layer should not preselect the only files the reviewer is allowed to consider semantically relevant.

### 4.5 Structural navigation

Optional capabilities to evaluate:

```text
find_symbol
find_definition
find_references
find_implementations
find_callers
find_importers
find_dependents
```

Results should identify retrieval/provenance class when possible:

- compiler/index-derived;
- parser-derived;
- search/heuristic;
- incomplete/unsupported.

Critical research principle:

> `not found in graph/index` must not mean `does not exist` or `is irrelevant` unless the concrete index contract proves completeness for that mechanism.

This preserves dynamic registration, reflection, generated code, configuration coupling, plugin systems, and unsupported-language cases.

### 4.6 Bounded validation

Candidate read/validation capabilities:

- repository-governed focused tests;
- predefined static analyzers/lints/type checks;
- inspection of existing CI logs/artifacts;
- bounded reproduction harnesses where governing policy permits execution.

A test failure can be evidence. A test pass does not prove every untested invariant.

### 4.7 Context experiment matrix

Do not select production context architecture by intuition alone.

```text
A — public provider reconstruction baseline
B — deterministic whole-repository snapshot
C — agentic primitive read-only repository session
D — C + structural definitions/references/callers/dependency hints
E — D + bounded test/static/reproduction validation
```

Research gates:

- **C1:** B versus C — snapshot sufficiency versus agentic exploration;
- **C2:** C versus D — structural-navigation value;
- **C3:** D versus E — bounded-validation value.

Possible C1 outcomes may include `ACCEPT_SNAPSHOT`, `ACCEPT_AGENTIC`, `HYBRID`, or `DEFER`. C2/C3 should use bounded `ACCEPT_NARROW / DEFER / REJECT`-style decisions.

Only after a strong single-reviewer baseline exists should multi-pass variants be measured.

## 5. Layer 2 — review planning and evidence indexing

Question:

> Can the review procedure make required authority, evidence classes, and semantic surfaces explicit without leaking expected answers or becoming a closed checklist?

### 5.1 `AUTHORITY_MANIFEST_V1`

A future authority manifest may index the authority chain for one exact target:

```text
AUTHORITY_MANIFEST_V1

repository
BASE_SHA
HEAD_SHA
review_policy_ref

accepted_authority_refs[]
head_target_semantics_refs[]
live_state_refs[]
```

It may help distinguish:

- accepted immutable BASE authority;
- proposed HEAD target semantics;
- current live GitHub/source state;
- accepted external capability evidence.

It is an index, **not** a new authority source. Where policy requires independent reconstruction, the reviewer must still verify the underlying refs.

### 5.2 `EVIDENCE_MANIFEST_V1`

A future evidence manifest may index evidence classes expected for the target:

```text
E001 PR identity
E002 BASE identity
E003 HEAD identity
E004 changed-file inventory
E005 immutable authority refs
E006 exact diff
E007 exact-head CI
E008 relevant runtime/test artifacts
E009 relevant external capability evidence
...
```

The reviewer verifies underlying sources rather than trusting the manifest because MimiSeek listed them.

### 5.3 Evidence quality metadata

Avoid a single magical quality flag.

Candidate dimensions:

```text
source_kind
verification_state
identity_binding
freshness
derivation
```

Example:

```text
PR body says CI passed
source_kind = human_claim
verification_state = CLAIMED
identity_binding = unresolved
```

versus:

```text
live provider workflow
source_kind = provider_workflow
verification_state = VERIFIED_DIRECT
identity_binding = exact_head
freshness = current
```

Metadata describes evidence quality; it does not prove semantic correctness by itself.

### 5.4 `REVIEW_PLAN_V1`

A future review plan should be dynamically derived from:

- exact diff and changed concepts;
- accepted architecture/policy invariants;
- changed and unchanged dependency paths;
- explainable risk features;
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

The plan must not expose expected finding text, expected finding count, later fix knowledge, adjudicated answer keys, or other evaluation ground truth.

### 5.5 Open-ended review remains required

A plan can create blind spots if treated as exhaustive authority.

Any future procedure should retain an explicit open-ended semantic pass after planned surfaces are examined.

The plan is a coverage scaffold, not a finite proof that no other material risk exists.

## 6. Layer 3 — semantic coverage and structured findings

Question:

> Can MimiSeek distinguish "reviewed and no finding" from "not reviewed" and represent each material finding as an evidence-backed machine object?

### 6.1 Coverage states

Candidate states for material semantic surfaces:

```text
REVIEWED_NO_FINDING
FINDING
NOT_APPLICABLE
INSUFFICIENT_EVIDENCE
NOT_REVIEWED
```

A zero-finding result is not equivalent to complete coverage.

### 6.2 Evidence-backed coverage

Coverage must not become reviewer self-certification such as:

```text
concurrency_checked = true
```

A positive coverage record should reference observable evidence of what was examined, for example:

- exact files/symbols/commits;
- governing invariant/ADR refs;
- state-transition paths;
- callers/dependencies;
- tests/runtime evidence;
- concrete adversarial scenarios considered.

The goal is not to expose private chain-of-thought. The goal is to preserve bounded scope/evidence sufficient for later diagnosis and learning.

### 6.3 Candidate `REVIEW_COVERAGE_V1`

```text
REVIEW_COVERAGE_V1

review_identity

surfaces[]:
  surface_id
  status
  invariant_or_question
  evidence_refs[]
  notes
```

The surface set must be derived from the concrete target rather than a universal static checklist.

### 6.4 Candidate `FINDING_V1`

A finding must be namespaced by immutable review identity. A bare local token such as `F001` is not globally unique and must never be used alone as canonical machine identity.

Research-only candidate:

```text
FINDING_V1

review_identity
finding_ref
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

Identity rules for later schema work:

- `review_identity` binds the finding to one immutable review execution/result identity;
- `finding_id` may remain a short local display identifier such as `F001`, but is unique only within that immutable review identity;
- `finding_ref` is the globally unambiguous immutable reference used by ingestion, adjudication links, remediation links, correlation, falsification, and orchestration;
- an implementation may derive `finding_ref` from a governed composite such as `(review_identity, finding_id)` or use another globally unique immutable representation, but the exact encoding is future schema work;
- historical IDs in canonical learning data and local IDs emitted by other review runs must never alias merely because their short labels match.

Do not store private chain-of-thought. Store bounded rationale and evidence sufficient to reconstruct the claim.

Do not treat model-generated numeric confidence as proof.

### 6.5 Keep current `REVIEW_RESULT_V1` small

Richer semantic artifacts do not automatically justify changing the accepted terminal result contract.

Initial research preference:

```text
REVIEW_RESULT_V1
    |
    +-- REVIEW_COVERAGE_V1
    +-- FINDING_V1[]
    +-- EVIDENCE_MANIFEST_V1
```

The rich objects may later be companion/digest-bound artifacts.

A future `REVIEW_RESULT_V2` should be considered only after these semantics stabilize and a versioned replacement provides demonstrated operational value.

### Gate Q1 — semantic observability

Question:

> Do review planning, authority/evidence indexing, evidence-backed coverage, and structured findings materially improve review completeness diagnosis and learning without becoming checklist self-attestation?

Decision: `ACCEPT_NARROW | DEFER | REJECT`.

## 7. Layer 4 — finding lifecycle and outcome knowledge

Question:

> What happened to each finding across adjudication, remediation, new HEADs, and re-review?

### 7.1 Separate authorities and namespaces

Do not collapse reviewer assertion, falsification/challenge outcome, consumer adjudication, and remediation evidence into one state machine or one shared enum namespace.

Primary-review assertion state and candidate challenge state are distinct concepts. A future machine schema should use explicit state type/authority and preferably namespaced enum values.

Illustrative challenge outcomes:

```text
CHALLENGE_SUPPORTED
CHALLENGE_REFUTED
CHALLENGE_UNRESOLVED
```

Consumer-governed disposition may include:

```text
UNKNOWN
CONFIRMED
REJECTED
SUPERSEDED
```

Remediation/re-review relation may include:

```text
NONE
REMEDIATION_EVIDENCE
REREVIEW_REQUIRED
NO_LONGER_REPRODUCED
```

A challenge outcome must not be confused with consumer adjudication merely because both describe disagreement. MimiSeek must not declare a consumer-owned semantic defect `FIXED` merely because implementation changed or a reviewer stopped reproducing it.

### 7.2 Finding history across heads

The system should be able to preserve chains such as:

```text
review A / HEAD A
  finding_ref = <review-A>::F001
  local finding_id = F001
  consumer disposition = CONFIRMED

HEAD B
  remediation evidence exists
  prior exact-head review is stale for acceptance

review B / HEAD B
  prior finding_ref no longer reproduced
```

Review of HEAD A never accepts HEAD B. Reusing local token `F001` in another review does not imply identity or same root cause.

### 7.3 Finding correlation

Long-lived PRs need help recognizing potentially related findings across cycles.

Correlation operates on immutable `finding_ref` values, not bare local IDs.

A future `finding_fingerprint` may use normalized hints such as:

- category;
- affected semantic object;
- violated authority/invariant;
- normalized claim shape.

The fingerprint is a **correlation hint**, not immutable identity and not automatic root-cause truth.

Possible relation states:

```text
POSSIBLE_SAME_ROOT_CAUSE
CONFIRMED_SAME_ROOT_CAUSE
DISTINCT_FINDING
UNRESOLVED_RELATION
```

Authoritative cross-cycle conclusions must remain evidence-backed.

### 7.4 False-positive tracking

Rejected findings are valuable learning evidence. A normalized record should eventually capture both disposition and cause, for example:

- misunderstood CAS semantics;
- wrong authority precedence;
- stale evidence;
- incomplete caller analysis;
- heuristic graph result treated as complete;
- speculative consequence without reproducible path.

This extends existing false-positive learning concepts with causal structure.

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

Do not collapse domain and failure cause into one label.

Different-head, timing, visibility, and leakage conditions must support the inference before an earlier run is labeled a miss.

### Gate Q2 — finding lifecycle value

Question:

> Do structured assertion/disposition/remediation/re-review relations improve learning and long-PR continuity without taking consumer adjudication authority?

Decision: `ACCEPT_NARROW | DEFER | REJECT`.

## 8. Layer 5 — reusable defect patterns and counterexamples

Question:

> Which recurring engineering failure mechanics should become transferable reviewer knowledge?

### 8.1 Candidate `DEFECT_PATTERN_V1`

MimiSeek should learn generic mechanics rather than historical SHA/file answers.

Example:

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
  does restart preserve unresolved claim state?
```

Other pattern families may include:

- stale authority selection;
- uncorrelated external result;
- multiple durable writers outside one serialization boundary;
- incomplete recovery fencing;
- optimistic currentness after source movement;
- project-specific semantics hidden in generic transport;
- unsafe migration/compatibility assumptions;
- graph-only false completeness.

### 8.2 Counterexample/adversarial library

Patterns may carry reusable scenarios that ask the reviewer to prove correctness under stress without revealing that a defect exists.

Example for ambiguous external effects:

```text
action succeeds / acknowledgement lost
restart immediately after claim
concurrent retry from another worker
duplicate callback
remote state visible before local state
local fence visible before remote state
```

Example for session lifecycle:

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

Historical evidence may justify adding targeted review surfaces when a change matches a known pattern.

Example:

```text
observed history:
  persistence + restart changes correlate with missed multi-writer defects

reviewer-method candidate:
  enumerate every independently reachable writer

strategy candidate:
  add one targeted recovery/concurrency pass for this risk class
```

Reviewer methodology and orchestration strategy must remain separately identifiable and evaluable.

### Gate K1 — pattern/counterexample value

Question:

> Do transferable patterns/scenarios improve recall or reduce misses without leaking historical answers into evaluation cases?

Decision: `ACCEPT_NARROW | DEFER | REJECT`.

## 9. Layer 6 — falsification and bounded orchestration

Question:

> After a strong single-reviewer baseline exists and pattern/counterexample research has been evaluated, can targeted challenges and additional asymmetric passes improve quality without changing atomic V1 semantics, using voting, or creating unbounded recursion?

### 9.1 Finding falsification concept

A consequential candidate finding identified by immutable `finding_ref` may receive an adversarial challenge:

> Try to prove this exact finding false. Find the strongest valid path under which the claimed invariant is actually preserved.

Illustrative candidate-level challenge outcomes:

```text
CHALLENGE_SUPPORTED
CHALLENGE_REFUTED
CHALLENGE_UNRESOLVED
```

The falsifier is **not** asked to review the entire PR again and is not asked to agree with the primary reviewer.

Initial trigger candidates:

- HIGH/CRITICAL findings;
- acceptance-blocking findings;
- incomplete/indirect evidence;
- subtle recovery/concurrency/authority consequences;
- historically high false-positive categories.

Universal falsification of every low-severity observation is not an initial requirement.

### 9.2 Preserve atomic `REVIEW_JOB_V1` and current `REVIEW_RESULT_V1`

Do not expand one `REVIEW_JOB_V1` into:

```text
workers[]
results[]
votes[]
```

One current `REVIEW_JOB_V1` remains one fresh **whole-review** execution with one correlated current `REVIEW_RESULT_V1`.

Under the accepted V1 contract, the terminal review outcomes remain the accepted values such as:

```text
PASS
FINDINGS
ABSTAIN
```

This research does **not** reinterpret those values as candidate-finding challenge outcomes.

A falsifier has a narrower semantic task. Therefore `CHALLENGE_SUPPORTED`, `CHALLENGE_REFUTED`, and `CHALLENGE_UNRESOLVED` are not valid substitutes for current `REVIEW_RESULT_V1` terminal semantics.

Likewise, putting an orchestration-critical falsification outcome only into free-form `report` text would not provide a typed machine-verifiable result contract for future aggregation.

### 9.3 Typed falsification execution/result contract is unresolved

This is an explicit research prerequisite exposed by review of this plan.

Before a future `REVIEW_RUN_V1` may launch an independent falsifier as a subordinate execution, a separately governed architecture decision must define a compatible typed execution/result contract.

This plan intentionally does **not** choose the contract.

Research options include, for example:

1. a distinct future `FALSIFICATION_JOB_V1` / `FALSIFICATION_RESULT_V1` beside current review-job V1; or
2. a later versioned review job/result family in which role and typed result variant are explicit, without retroactively changing V1 semantics.

Names above are illustrative, not selected architecture.

Any accepted design must preserve at least:

- immutable review-target identity;
- immutable candidate-finding `finding_ref` identity;
- immutable strategy/role identity where applicable;
- one subordinate execution -> one typed correlated result;
- durable/recoverable result identity where required;
- fail-closed malformed, stale, wrong-finding, wrong-target, or conflicting results;
- challenge state remaining separate from consumer adjudication;
- no silent reinterpretation of current `REVIEW_JOB_V1` / `REVIEW_RESULT_V1`.

Until that contract is separately accepted and implemented:

- an independent falsifier must **not** be modeled or launched as an ordinary `REVIEW_JOB_V1`;
- production `REVIEW_RUN_V1` must not depend on such a falsification execution;
- research experiments may study falsification value with explicitly non-production artifacts, but those artifacts grant no current review-job, acceptance, merge, promotion, or consumer authority.

### 9.4 Future `REVIEW_RUN_V1` above compatible atomic executions

If multi-pass review proves useful **and every subordinate execution role has an accepted compatible typed result contract**, a higher procedure layer may be considered.

Research-only conceptual shape:

```text
REVIEW_RUN_V1

review_identity
review_strategy_ref

review_jobs:
  J1 general semantic review
  J2 targeted whole-review specialist
  J3 gap/coverage whole-review pass

optional_typed_challenges:
  C1 falsify <finding_ref>

aggregation_policy
final_procedure_state
```

The example does **not** claim that `C1` is a `REVIEW_JOB_V1`. Typed correlation and aggregation for heterogeneous subordinate execution kinds remain future architecture.

Even J2/J3 may only use `REVIEW_JOB_V1` if their tasks and terminal outputs remain semantically compatible with the accepted whole-review V1 contract. A future role that is not compatible requires its own accepted typed contract rather than semantic overloading.

The run must not treat majority vote as truth.

Possible asymmetric roles include:

- general reviewer;
- risk specialist where compatible with its typed contract;
- falsifier through a separately accepted typed challenge contract;
- gap/coverage reviewer where compatible with its typed contract.

### 9.5 Semantic budget / LoopGuard

Review orchestration needs bounded/no-blind discipline.

Research limits might begin with:

```text
max_general_passes = 1
max_targeted_passes_per_surface = 1
max_falsification_attempts_per_finding = 1
```

Persistent material disagreement becomes an explicitly typed unresolved state rather than recursive worker spawning.

If unresolved uncertainty is release-critical, consumer governing policy may require a terminal `ABSTAIN` from the applicable whole-review acceptance path. The orchestrator itself does not invent consumer acceptance consequences.

### 9.6 Strategy identity

Once multiple meaningful orchestration strategies exist, research proposes immutable:

```text
review_strategy_ref
```

It should remain distinct from:

- reviewer source/version;
- model/provider;
- review policy;
- worker profile;
- context/capability profile;
- execution identity.

Without this separation, later evaluation cannot tell whether quality changed because of model, reviewer methodology, context capability, or orchestration.

### Gate Q3 — falsification value and typed-result feasibility

Question:

> Does targeted falsification reduce unsupported HIGH/CRITICAL findings enough to justify cost/latency, and can an independent falsifier receive a typed execution/result contract without reinterpreting current V1 review semantics?

Passing Q3 for production use requires **both**:

1. demonstrated semantic value; and
2. a separately governed compatible falsification execution/result contract.

Research-only falsification experiments may precede that contract but cannot be treated as production `REVIEW_JOB_V1` executions.

Decision: `ACCEPT_NARROW | DEFER | REJECT`.

### Gate S1 — multi-pass value

Question:

> After a strong single-reviewer baseline exists, K1 has established the role of reusable adversarial knowledge, and subordinate result contracts are valid, does a higher `REVIEW_RUN_V1` with asymmetric roles materially improve quality per unit cost/latency?

Decision: `ACCEPT_NARROW | DEFER | REJECT`.

## 10. Layer 7 — risk, profiles, replay, and strategy evolution

Question:

> Which reviewer/context/orchestration strategy performs better on governed evidence, and how can a better strategy become default without self-certification?

### 10.1 Risk features before risk scores

Do not begin with invented weights such as `+5 concurrency`.

Start with explainable features:

```text
concurrency = true
persistent_state = true
external_side_effect = true
authority_change = true
retry = true
credential_boundary = false
migration = false
```

Later governed outcome data may justify weights or classification thresholds.

Risk classification allocates review effort. It never decides defect truth.

### 10.2 Adaptive depth

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
  targeted compatible specialist and/or typed falsification if available

CRITICAL
  multiple distinct bounded semantic paths
  explicit coverage closure or unresolved outcome
```

These categories are semantic-risk categories, not file-type categories. An authority/security change cannot become `LOW` merely because it is documentation-only.

This must be measured rather than accepted because the categories sound reasonable.

### 10.3 Reviewer/strategy profiles

Do not collapse performance into one global model score.

Performance identity should distinguish at least:

```text
reviewer source/version
model/provider
context/capability profile
review_strategy_ref
review policy class
```

Candidate metrics:

- review count;
- critical-defect recall;
- supported-finding rate;
- false-positive rate;
- miss rate;
- coverage completion;
- authority errors;
- stale-identity failures;
- unresolved rate;
- domain-specific performance for concurrency/security/lifecycle/docs/etc.

Sparse observations must not become leaderboard truth. Use sample size and statistical caution where appropriate.

### 10.4 Replay/regression corpus

Historical real PR evidence is a core asset.

A governed replay case may contain:

```text
immutable PR snapshot
known BUGGY target defect
corresponding FIXED state
adjudicated accepted/rejected finding evidence
known remediation relation
```

New reviewer/context/strategy candidates can be evaluated blind:

- does the target defect reappear on BUGGY?
- does the old finding disappear on FIXED?
- are new false positives emitted?
- what coverage is achieved?
- what tools/context were required?

### 10.5 Leakage controls

Evaluation must separate:

```text
learning/training evidence
!= fixed evaluation corpus
!= later holdout/shadow evidence
```

Expected finding text/category/count and later fix/disposition must remain hidden from candidate reviewer context unless an experiment explicitly tests that condition.

Historical public comments/fixes can invalidate a case for blind evaluation and should be recorded as leakage risk.

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
- worker/execution count;
- tool/context usage;
- latency;
- execution cost where measurable.

Do not optimize cost before establishing an acceptable semantic-quality region.

### 10.7 Strategy promotion research

If strategy changes later become consequence-bearing defaults, do not make every experimental strategy default immediately.

Candidate progression:

```text
strategy candidate
    ↓
offline replay
    ↓
shadow review
    ↓
limited production evidence
    ↓
fresh independent evaluation
    ↓
PROMOTE / REJECT / ABSTAIN
```

This may reuse existing MimiSeek principles such as fixed exam before candidate, no self-defined evaluation, and independent promotion authority.

However, **the current reviewer-promotion lifecycle does not automatically authorize strategy promotion**. Exact strategy-promotion semantics require a separate accepted architecture decision.

### Gate S2 — adaptive strategy value

Question:

> Can explainable risk features allocate review depth better than a fixed strategy without hiding critical misses or creating unstable authority behavior?

Decision: `ACCEPT_NARROW | DEFER | REJECT`.

## 11. Experimental controls inherited from PR #6

PR #6 remains valuable predecessor research and provenance. Its strongest experimental controls should remain part of this unified program.

### 11.1 Positive, stale, hidden-defect, and false-positive controls

A useful experiment suite includes materially different cases:

- accepted exact target where `PASS` is possible;
- superseded target that must fail currentness rather than be accepted merely because old objects remain fetchable;
- known defective immutable target where expected findings/count are hidden;
- rejected/false-positive historical cases.

A PASS-shaped response alone is not reviewer-quality evidence.

### 11.2 Answer-leakage control

Expected findings, categories, counts, later fixes, and adjudicated dispositions must be stored outside candidate-reviewer-visible input when measuring blind review quality.

### 11.3 Unchanged-caller control

Changed producer/API semantics while an unchanged caller still relies on old behavior.

Purpose: distinguish local diff inspection from repository impact exploration.

### 11.4 Similar-name false-reference control

Multiple plausible same/similar symbols.

Purpose: compare heuristic search with precise navigation and prevent false completeness.

### 11.5 Dynamic registration/configuration control

Behavior connected through registry/plugin/configuration rather than an obvious static call graph.

Purpose: falsify graph-only completeness assumptions.

### 11.6 Large-repository/context-pressure control

Relevant unchanged evidence lies outside obvious context/shard/ranking boundaries.

Purpose: compare deterministic packing with agentic search and explicit oversize behavior.

### 11.7 Validation-value control

Static reading yields a plausible candidate issue that focused validation confirms or disproves.

Purpose: measure precision gain from bounded validation.

### 11.8 FIXED false-positive control

Reviewer sees the materially fixed state without being told it is fixed.

Purpose: prevent a stronger reviewer from merely repeating memorized historical findings.

### 11.9 Governance self-change control

PR changes reviewer/governance instructions in HEAD.

Purpose: prove accepted BASE-derived authority still governs rather than allowing proposed HEAD policy to grade itself.

### 11.10 Fair comparison

When comparing context or strategy variants where technically possible:

- freeze repository/BASE/HEAD/policy identities;
- freeze reviewer/model/reasoning budget where possible;
- hide expected findings;
- preserve raw result artifacts;
- use governed adjudication rather than majority vote;
- compare BUGGY and corresponding FIXED cases;
- record materially different evidence exposure between variants rather than pretending the experiment is perfectly controlled.

## 12. Recommended dependency-ordered sequence

The architecture plan is unified, but implementation should remain narrow and separately governed.

### Phase 0 — finish Track R atomic execution

Pass E0 first.

### Phase 1 — context baseline

Run A/B/C on a small governed hidden corpus and decide C1.

### Phase 2 — capability expansion only if justified

Evaluate D structural navigation and E bounded validation sequentially through C2/C3.

Do not assume graph or execution is required until data show value.

### Phase 3 — semantic observability

If Q1 is accepted narrowly, prefer an initial production slice around:

```text
AUTHORITY/EVIDENCE indexing
REVIEW_PLAN
REVIEW_COVERAGE
FINDING_V1 companion artifacts
```

Do not begin with multi-agent orchestration.

### Phase 4 — finding knowledge

If Q2 is accepted:

- finding lifecycle;
- consumer disposition links;
- remediation/re-review relations;
- globally unambiguous `finding_ref` plus local finding IDs;
- correlation hints;
- false-positive/miss causal classification.

### Phase 5 — defect-pattern and counterexample memory

If K1 is accepted:

- derive generic patterns from adjudicated evidence;
- attach adversarial scenarios without expected-answer leakage;
- evaluate on replay/holdout evidence.

### Phase 6 — falsification research and contract

After Phase 5 establishes the reusable adversarial-knowledge layer, measure falsification value on research-only typed artifacts where appropriate.

For production use, Q3 also requires a separately accepted typed falsification execution/result contract.

Do not encode challenge states as current whole-review terminal states, and do not launch a falsifier as ordinary current `REVIEW_JOB_V1` merely to reuse existing transport.

### Phase 7 — review-run orchestration

Only after:

- E0 passes;
- a strong single-reviewer path is established;
- the relevant semantic-observability layers are accepted where needed;
- K1 has resolved the reusable pattern/counterexample layer as required by this dependency order; and
- every subordinate execution role has an accepted compatible typed result contract.

Then S1 may evaluate:

- `REVIEW_RUN_V1`;
- `review_strategy_ref`;
- bounded asymmetric roles;
- typed falsification where separately accepted;
- gap/coverage passes;
- explicit unresolved outcomes;
- LoopGuard.

### Phase 8 — adaptive strategy evolution

Only after enough outcome data exist:

- use explainable risk features;
- compare fixed and adaptive strategies;
- build reviewer/strategy profiles;
- measure cost/latency;
- define separately governed strategy-evaluation/promotion semantics if justified.

## 13. Relationship to current MimiSeek stages

This research does not replace the accepted Stage 1–11 reviewer-evolution roadmap.

It clarifies what future reviewer capabilities, semantic artifacts, and orchestration strategy may later be learned, evaluated, and released.

Expected relationships:

- Stage 1 historical reconciliation provides initial governed BUGGY/FIXED/false-positive evidence;
- Stage 2 structured evidence export should preserve exact identities/findings/dispositions sufficient for later lifecycle/replay work;
- Stage 3 normalized outcome store becomes the canonical learning/evaluation input rather than raw review-job ledger state;
- Stage 4 learning events may later distinguish coverage/reasoning/evidence/authority/falsification misses;
- before Stage 5 creates a promotion-eligible reviewer candidate, accepted reviewer capability architecture and fixed evaluation policy must be sufficiently resolved for that candidate;
- Stage 6 regression/protected-capability evaluation may later test reviewer methodology and accepted context/exploration capabilities;
- Stage 7 promotion remains independent and policy-bound;
- Stage 8 consumer distribution remains separate and safety-gated;
- Track R remains bounded operational review execution and does not imply reviewer promotion or consumer installation.

## 14. Strong principles versus open questions

### 14.1 Strong candidate principles already supported

- exact immutable review identity;
- accepted policy/authority identity;
- repository-wide evidence must be reachable somehow;
- unchanged code can be material review evidence;
- silent context truncation is incompatible with authoritative PASS;
- graph/search/index results are retrieval mechanisms, not source truth;
- candidate findings should be evidence-backed and falsifiable;
- machine finding identity must be globally unambiguous through immutable review scoping rather than bare local IDs;
- false positives are first-class quality failures;
- reviewer quality and execution-transport reliability must be measured separately;
- one current review job remains one fresh whole-review execution/result;
- current `REVIEW_RESULT_V1` semantics are not repurposed for narrower challenge roles;
- challenge-state and consumer-adjudication namespaces remain distinct;
- reviewer agreement is not ground truth;
- context strategy, reviewer methodology, and orchestration strategy should be independently identifiable.

### 14.2 Open research questions

- deterministic snapshot versus agentic repository session;
- exact primitive repository tool set;
- value/need of structural graph/index;
- value/need of bounded runnable tests/static tools;
- exact `REVIEW_PLAN`, `REVIEW_COVERAGE`, and `FINDING_V1` schemas;
- exact encoding/derivation of globally unique `finding_ref`;
- exact finding correlation/fingerprint algorithm;
- falsification trigger policy;
- exact typed falsification execution/result contract and its relationship to current `REVIEW_JOB_V1` / `REVIEW_RESULT_V1`;
- exact defect-pattern representation;
- whether/when `REVIEW_RUN_V1` materially improves quality;
- which subordinate roles are compatible with current review-job semantics and which require separate typed contracts;
- risk-model inputs/thresholds;
- exact strategy-promotion lifecycle;
- acceptable latency/compute after semantic-quality floors exist.

## 15. Explicit non-goals

This research plan does not authorize:

- changing current `REVIEW_JOB_V1` semantics;
- changing current `REVIEW_RESULT_V1` terminal semantics;
- turning one review job into a worker/result/voting pool;
- using a bare local `finding_id` such as `F001` as global machine identity across independent reviews;
- encoding candidate-level challenge states as current `REVIEW_RESULT_V1` `PASS / FINDINGS / ABSTAIN`;
- hiding an orchestration-critical falsification result only in free-form report text;
- launching an independent falsifier as ordinary `REVIEW_JOB_V1` before a compatible typed challenge contract is separately accepted;
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

## 16. PR #6 and PR #18 consolidation policy

This document is intended to become the single research owner for the semantic-review architecture question if independently accepted.

PR #6 remains valuable predecessor research containing detailed reviewer-context experiments and external-practice notes. It should not be merged in its old architectural context merely to preserve those ideas.

PR #18 is the consolidation vehicle because it is based on the modern accepted architecture after ADR 0013, the accepted atomic review-job foundation, and the MimiSeek-owned durable ledger/publication slice.

If this unified plan is accepted:

- PR #6 may be closed as superseded while retaining its Git/PR history as research provenance;
- older narrower research drafts should not remain competing semantic-architecture owners;
- later decisions should cite this plan but accept/reject individual gates rather than treating every hypothesis here as an all-or-nothing production decision.

Closing PR #6 after this plan is accepted would be repository housekeeping. It would **not** mean that snapshot, agentic exploration, structural navigation, bounded execution, multi-pass review, or any other #6 hypothesis was accepted for production.

## 17. Decision boundary

This document is intentionally **not** an ADR.

It defines one coherent research program and dependency order.

Each consequence-bearing architecture choice should later use a separately governed evidence-based decision with bounded outcomes such as:

```text
ACCEPT_NARROW
DEFER
REJECT
```

The immediate research/implementation order remains:

```text
reliable atomic REVIEW_JOB_V1 E2E
    ↓
measure strong single-reviewer context/capability architecture
    ↓
add planning / evidence indexing / coverage / structured findings
    ↓
add finding lifecycle + outcome memory
    ↓
measure defect-pattern/counterexample value
    ↓
measure falsification and separately resolve its typed result contract
    ↓
only then measure compatible multi-pass orchestration
    ↓
only after sufficient data measure adaptive strategy/evolution
```

Until the relevant gates are independently accepted, every candidate schema, tool, profile, pattern library, challenge contract, risk model, multi-pass procedure, and strategy lifecycle described here remains a research hypothesis only.
