# Reviewer-context research handoff from CAP

Status: **research input only / non-authoritative / no architecture selected**

This document preserves reviewer-specific research and experiment evidence produced while `BogdanAIP/chat-agent-platform` was developing automatic independent-review orchestration. It does not change MimiSeek Stage 1 state, does not create a baseline/candidate/stable reviewer, and does not authorize consumer installation.

The handoff is intentionally separate from the active Stage 1 PR. It exists so reviewer-specific work is not lost or further developed inside CAP merely because CAP needs review during its own development.

## 1. Product-boundary conclusion

The handoff follows accepted MimiSeek ADR 0001 and ADR 0006:

- CAP/UV/future consumers own their ordinary development/review/fix workflows and project-local acceptance policy;
- MimiSeek owns the reusable reviewer methodology, learning, evaluation, versioning and release lifecycle;
- CAP may own generic multi-chat/worker orchestration, but CAP should not become the long-term owner of reviewer-specific repository-context methodology.

### Keep in CAP as generic agent infrastructure

The following mechanics are useful to reviewers but are not reviewer-specific and should remain candidates for CAP/general worker orchestration:

- launch a genuinely fresh bounded worker chat;
- prove worker context/capability isolation;
- correlate parent operation to child run;
- durable exactly-once/one-Send ownership;
- browser lifecycle, crash/restart and stale-run handling;
- deliver bounded task inputs/files to a worker;
- capture a structured terminal result and return it durably to the parent;
- generic privilege separation and fail-closed dispatch/result handling.

### Move to MimiSeek reviewer research/methodology

The following concerns are reviewer-specific and belong here as research/candidate/evaluation inputs rather than CAP product architecture:

- how a reviewer obtains trustworthy BASE/HEAD repository truth;
- whole-repository versus diff-only context;
- changed/unchanged cross-file impact;
- source/config/test relationship discovery;
- snapshot/shard/archive/retrieval strategies;
- code maps/graphs, definitions/references, blast radius and retrieval ranking;
- reviewer-specific prompt/evidence contracts;
- known-finding, cross-file and large-repository review controls;
- false-positive/recall evaluation of context strategies;
- reviewer confidentiality risks when private repository content and external web research coexist.

## 2. Durable CAP experiment sources

### PR #145 — automatic Temporary Chat reviewer experiment

Repository: `BogdanAIP/chat-agent-platform`

PR: `#145 Experiment: automate Temporary Chat reviewer probe`

Current research head at handoff: `df0aa462ade7d36172347adfcbc292dd1c6f95da`

Accepted CAP baseline used by the experiment: `90a8e16e6a1badecd3315968339ca691634b7ee4`

Useful physical evidence already obtained before this handoff:

1. **PASS control** — accepted CAP PR #142: an automatically opened non-personalized Temporary Chat independently reconstructed public GitHub evidence and returned exact-head `PASS`.
2. **STALE control** — an obsolete intermediate PR #140 identity was correctly rejected as `STALE / STALE_MATERIAL_CHANGE` instead of being reviewed as current.
3. **Known-finding negative control** — experiment PR #146 reproduced historical defective range:
   - BASE `b10a5fa3122bb6c76c12d37d67911b88e5e1ce28`
   - HEAD `7077ecb8496ee89530cbe5efaa1b2112e7be330f`

   Without being told the expected answer, the Temporary Chat reviewer returned `CURRENT FINDINGS` and recovered the same four historical P1 defect categories later recorded as confirmed/fixed in CAP PR #140:
   - mutation-capable GitHub actions remained reachable when merely unselected;
   - ambiguous GitHub result publication could race manual fallback;
   - required direct filesystem/IndexedDB/service-worker engineering evidence was missing;
   - architecture-lineage decisions were compound/non-canonical.

This is evidence that the fresh Temporary Chat approach can perform non-trivial semantic review. It is **not** proof that its repository-context strategy is sufficient across private/large/cross-file repositories.

Important experiment paths at exact CAP head above include:

- `experiments/chatgpt-temporary-reviewer/`
- `scripts/launch-temporary-reviewer-probe.ps1`
- `tests/test_temporary_reviewer_physical_experiment.py`
- `experiments/chatgpt-snapshot-reviewer/build_snapshot.py`

The loopback/browser harness is experiment transport, not a MimiSeek production design.

### PR #147 — reviewer context transport research

Repository: `BogdanAIP/chat-agent-platform`

PR: `#147 Research: automatic reviewer context transport`

Research head at handoff: `d732ef190160891b60c953bb584a273b10be0a7e`

State at handoff: **DEFER**. The earlier attempt to select a bounded private evidence package was explicitly superseded because a reviewer-selected/developer-selected small package had not proven sufficient whole-codebase context.

The useful research conclusions to preserve are below.

## 3. Repository source authority

For a final provider-backed PR review, a developer working tree must not be silently trusted as current.

Preferred source-truth sequence under research:

```text
live provider PR identity
 -> exact BASE_SHA / HEAD_SHA
 -> isolated reviewer-side or consumer-side Git mirror/cache
 -> fresh fetch of exact remote objects
 -> verify commit/tree/blob identity
 -> build deterministic review representation from those Git objects
 -> independently compare the developer checkout with remote
```

Local parity should be explicit, for example:

`MATCH | LOCAL_AHEAD | REMOTE_AHEAD | DIVERGED | DIRTY | LOCAL_ONLY | REMOTE_UNAVAILABLE`

A GitHub-generated source ZIP may be tested as a transport format, but should not replace Git objects as repository truth.

For committed local-only development, a pre-PR review may bind to exact local commits. Dirty/local-only work requires a frozen byte snapshot/digest. If the same work is later pushed, a new provider-backed exact review is required; the local preview must not silently become remote acceptance.

## 4. Whole-repository context hypothesis

Research against professional/repository-aware tools suggests that strong review should not be modeled as `diff + a few manually preselected files`.

Patterns investigated include:

- full/sandboxed repository availability plus agentic exploration;
- full-project context gathering;
- repository indexing/RAG;
- code graph across files/functions/dependencies;
- definition/reference/symbol search with graph fallback;
- Tree-sitter definitions/references plus ranked repo maps under token budgets;
- impact/blast-radius traversal from changed code.

The reusable conclusion is not that any one implementation is already selected. It is:

> the reviewer should have a path to evidence across the repository, and context ranking/graphs are retrieval hints rather than repository truth.

A graph can miss dynamic calls, reflection, generated code, unusual configuration coupling, runtime registration and unsupported languages. Therefore `not present in graph` must never mean `not relevant`.

## 5. Direct snapshot/attachment candidates

For a private repository, one investigated path is a deterministic representation built from exact Git objects and directly attached to a fresh Temporary Chat rather than persisted in ChatGPT Library.

Library is not required for this design and creates separate retention/cleanup concerns. ZIP/TAR support must not be assumed unless physically verified.

A stronger text-based candidate under research was deterministic whole-repository source/TXT shards with explicit manifests and no silent truncation.

Snapshot semantics considered useful:

- exact repository/BASE/HEAD commit and tree identity;
- ordered path/mode/blob inventory and snapshot digest;
- BASE governing review policy/instructions;
- applicable HEAD reviewer/project skills;
- exact changed-file inventory and BASE..HEAD diff;
- all reviewable HEAD text/source/config/test files;
- BASE versions of changed/renamed/deleted files;
- explicit binary/non-UTF8/LFS/symlink/submodule declarations;
- deterministic per-file/per-shard digests;
- `OVERSIZE/ABSTAIN` rather than silent omission when a transport limit is exceeded.

This remains a candidate to evaluate, not a selected MimiSeek architecture.

## 6. Cross-file control

CAP experiment PR #148 was created specifically to test whether a reviewer can discover a defect that requires an **unchanged related file**.

Repository: `BogdanAIP/chat-agent-platform`

PR: `#148 Experiment control: cross-file reviewer context`

BASE: `8f019b47d0a49ba343a6a90ea761e55b9b364227`

HEAD: `b7ce6366170cc7e8768929e6a12c457a3672d28d`

Structural property: GitHub reports exactly one changed source file. The semantically relevant caller remains unchanged and is available only if the reviewer actually examines wider repository context. The expected semantic defect is intentionally not stated in the control PR.

This is a useful future regression/context-recall case. It should be imported only through normal MimiSeek evidence/provenance rules rather than copied as ground truth merely because this document references it.

## 7. Suggested future evaluation ladder

When MimiSeek reaches the stage that owns reviewer candidate/evaluation mechanics, compare context strategies on the **same cases** rather than selecting by convenience:

1. public repository + independent web/GitHub reconstruction;
2. exact remote-fetched whole-repository text/source snapshot;
3. snapshot plus structural repo map/index;
4. large-repository / shard-boundary controls;
5. archive transport only after actual platform support is proven;
6. narrow read-only repository context engine if static snapshot approaches are insufficient.

Measure at least:

- recall of adjudicated known defects;
- cross-file recall where required evidence is in unchanged code;
- false-positive rate / rejected candidates;
- stale/exact-identity behavior;
- silent omission detection;
- repository bytes/files supplied;
- model turns and elapsed review time;
- behavior when repository exceeds transport/context limits;
- public/private evidence separation and leakage risk;
- reproducibility of the exact evidence identity used by the reviewer.

## 8. What this handoff does not decide

This document does **not** decide:

- that Temporary Chat is the permanent MimiSeek execution environment;
- that snapshots beat a read-only context engine;
- that code graphs are mandatory;
- that TXT shards are the final transport;
- that ZIP is supported;
- that CAP should stop owning generic multi-chat worker transport;
- that MimiSeek should orchestrate consumer PR/fix loops;
- that historical CAP experiment outcomes are automatically canonical MimiSeek ground truth.

All promotion, learning, regression import and consumer-installation authority remains governed by MimiSeek's existing lifecycle, evaluation policy and roadmap.

## 9. Stage placement

Do not merge this research into current Stage 1 claims as if implementation exists.

Current Stage 1 should continue historical-data/provenance reconciliation and baseline-seed work. The material here is expected to become relevant when MimiSeek defines/evaluates actual reviewer candidate capabilities and protected/regression coverage (primarily later candidate/evaluation stages), and when consumer integration needs an explicit reviewer execution/context contract.

Until then this file is a durable research input only.