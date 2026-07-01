# CURRENT_SUCCESS_CRITERION.md

## Purpose

This document defines the present-tense success bar for the system at its current maturity level.

It is not:
- a roadmap
- an architecture document
- a phase document
- a fix document

It does not override:
- `BUILD_RULES.md`
- `PHASE_INDEX.md`
- phase documents
- fix documents

Its purpose is narrower:

to define what a successful end-to-end run means today, so the project can evaluate progress against a concrete current bar rather than against general philosophy or future capability.

---

## Why this document exists

The project already defines:
- architectural philosophy
- phase-local success criteria
- bounded implementation rules
- current subsystem behavior

What it has lacked is a single explicit statement of what the current system should be able to do, end to end, in a way a human can inspect and judge honestly.

This document provides that bar.

---

## Current success target

At the current maturity level, a successful end-to-end run is:

a bounded operator-provided coding task executed through the orchestration system such that the run produces a persisted, inspectable, minimally verified result with clear outcome classification and no ambiguity about what happened.

This is a current-state bar, not a future-state aspiration.

---

## Kind of task the system should handle today

The system should currently handle:
- a bounded, well-specified coding task
- one file or a small related file surface
- a clear objective
- explicit success criteria
- files in scope named in advance
- operator-provided task framing

The system does not yet need to prove success on:
- open-ended project planning
- autonomous decomposition
- broad multi-step repair chains
- large uncontrolled repo mutation
- unattended execution loops

---

## What a successful run should produce

A successful run today should produce all of the following.

### 1. Persisted task state

The task should end with a persisted final status that accurately reflects the actual outcome under current routing rules.

### 2. Execution artifact

The run should emit a persisted artifact containing the provider result in a form the operator can inspect later.

### 3. Deterministic verification result

The run should emit a persisted verifier result reflecting the currently implemented deterministic checks.

At the current stage, this means verification should function as a bounded tripwire, not as a broad correctness proof.

### 4. Clear outcome classification

The final task state should distinguish at least among:
- execution failure
- verification failure
- completed / acceptable current-state success
- reviewer task completed with recommendation record persisted

The operator should not need to infer outcome semantics from scattered files or guesswork.

### 5. Review landing when review is involved

If the workflow reaches reviewer handling, reviewer output should land in the currently supported bounded recommendation form, with valid type, persisted traceability, and a readable reason.

### 6. Operator-visible next-step surface

If a recommendation is produced, the system should make it inspectable and operator-actionable through the currently supported control surfaces.

A recommendation is not itself execution.
A recommendation is not itself derived-task approval.
A recommendation is not itself autonomous task creation beyond the currently explicit, bounded, operator-mediated flows.

---

## What verification should prove today

Verification should currently prove only what the implemented deterministic layer can honestly support.

At this maturity level, verification should be treated as proof of:
- named outputs existing where expected
- implemented syntax-level checks passing where applicable
- deterministic checks having actually been run and persisted

Verification should not be treated as proof of:
- semantic correctness
- task adequacy in the strong sense
- test completeness
- production readiness
- architectural soundness of generated code
- correctness of reviewer judgment

Verification is currently a tripwire and observability layer, not a guarantee of good software.

---

## What reviewer output should add today

Reviewer output should add structured judgment, not autonomous control.

At the current stage, reviewer handling should contribute:
- a bounded recommendation in the currently supported recommendation types
- a readable reason
- persisted linkage to the source task / artifact where applicable
- a stable landing point for operator judgment

Reviewer output should not be treated as:
- automatic repair authorization
- automatic follow-up execution
- autonomous planning
- broad policy interpretation
- proof that the underlying work is correct

Its role is to improve inspectability and decision clarity.

---

## What the operator should be able to conclude after a successful run

After a successful run at the current maturity level, the operator should be able to conclude:
- the system executed the task through a real or explicitly selected provider path
- the result was persisted
- deterministic checks were run and recorded
- the task received an outcome classification consistent with current rules
- any review-derived recommendation was landed in a structured, inspectable form
- the run history is understandable without reconstructing the workflow manually from scattered implementation details

The operator should not be forced to guess:
- what ran
- what was produced
- what failed
- why a recommendation appeared
- what the currently supported next action is

---

## What remains out of scope even in a successful run today

Even a successful current-state run does not imply support for:
- planner-generated task decomposition
- autonomous repair chains
- autonomous recommendation resolution
- rich test execution as a default system guarantee
- broad semantic verification
- direct writeback to a live codebase as a trusted completion mechanism
- unattended multi-step orchestration
- broad repo-scale mutation without explicit bounded task framing

These remain future concerns unless and until separately built and ratified.

---

## Failure of this criterion

The current success criterion should be treated as not met if one or more of the following is true:
- the system produces output but the run is not self-explaining
- task state, artifact state, verification state, or recommendation state are ambiguous or inconsistent
- deterministic checks do not run, do not persist, or overclaim what they proved
- reviewer output cannot be cleanly landed in the supported recommendation structure
- recommendation-to-action surfaces create ambiguity about what is merely suggested versus what is already authorized or created
- control-surface density makes the workflow materially harder to understand than the underlying task warrants
- a nominally successful run still leaves the operator unable to judge what happened or what to do next

---

## How this document should be used

This document is not a phase document and does not authorize work. It provides the anchor for Question 0 before any new forward ranking.

Before ranking new forward moves, ask:
1. Does the current system satisfy this success bar on a real bounded task?
2. If not, what concrete gap most prevents that?
3. Is the proposed next move aimed directly at that gap?
4. Does the proposed move improve trustworthy useful work, or only elaborate an already-active subsystem?
5. Would the system become more inspectable, more reliable, or more operator-legible if this move landed?

If those questions cannot be answered clearly, re-rank before drafting further growth.

---

## Guiding interpretation

This document exists to keep the project anchored to present-tense useful work.

The system is not successful merely because its governance is elegant.
It is successful when its current governance, control surfaces, execution flow, verification, and review handling together produce a bounded result a human can inspect and act on honestly.

That is the bar.

## Phase 273 Current Success Satisfaction Status

The previous current success criterion is now satisfied at deterministic
integrated proof level after Phase 272.

The proof basis is Phase 272:

- persisted task state
- deterministic local engine execution
- execution artifact
- verifier result
- current-success review over actual persisted records
- operator-visible response options

This satisfaction is narrow. It does not prove:

- semantic correctness
- live provider/model behavior
- runtime/platform behavior
- autonomous AI coding
- production readiness
- `general_answer` behavior
- OpenClaw/Hermes/Obsidian/LightRAG integration

`PHASE273_CURRENT_SUCCESS_SATISFACTION_AND_NEXT_SUCCESS_BAR_DOCS_ONLY_PROVEN=PASS`

## Next Success Bar

The next product success bar is:

operator-facing bounded coding-task proof through a stable control surface or
repeatable boundary packet.

The next bar should require:

- an operator-provided bounded coding task specification or packet
- named file scope
- explicit success criteria
- persisted task state
- execution artifact
- verifier result
- current-success review/readback
- clear operator-visible next action
- no ambiguity about what was executed, what was only recommended, and what
  remains unproven

The next bar does not yet require:

- live model/provider execution
- autonomous coding
- semantic correctness proof
- production readiness
- runtime/platform/OpenClaw/Hermes work
- `general_answer` resumption

## Phase 212 Route-Mediated Provider Smoke Gap Note

Phase 212 adds a guarded live Ollama transport adapter path for a future
route-mediated provider smoke proof.

This does not change the current success bar and does not prove actual
route-mediated provider execution. Phase 212 source/test validation uses
injected transport only and does not run provider/model/Ollama/HTTP.

Current success remains unmet for the route-mediated provider runtime path
until a later operator boundary produces actual live execution evidence with a
persisted, reviewable artifact and honest classification.

Phase 217 adds structured failure artifacts for live transport exceptions in
the Phase 212 route-mediated provider smoke path. It is source/test/docs only
and does not run provider, model, Ollama, HTTP, route runtime, worker dispatch,
or production behavior.

Phase 216 remains failed and is not accepted as runtime proof. The Phase 217
failure classification
`live_ollama_transport_exception_not_runtime_proof` records failure shape only:
HTTP status is unavailable, JSON parse did not succeed, no returned model or
response text exists, and the route marker is not present in response evidence.

A future retry must still perform the live route-mediated smoke. Current
success remains unmet for this path until an actual live artifact classifies as
`route_mediated_provider_smoke_runtime_marker_pass`.


## Phase 80 Live Proof Update

CURRENT_SUCCESS_CRITERION_LIVE_PROVEN_WITH_DETERMINISTIC_LOCAL_FILE_PROVIDER_CAVEAT

The current success criterion has been live-proven under a deterministic-provider caveat.

Proof document:

`docs/PHASE_80_CURRENT_SUCCESS_DEMO_PROOF.md`

The proof demonstrates task creation, explicit `local_file` provider execution, scoped file materialization, artifact persistence, deterministic verifier execution, verifier-result persistence, completed task classification, and operator response-option surfacing through `current-success-result-review`.

Caveat: this does not prove autonomous AI coding ability or model-backed generation.


## Phase 82 Operator Acceptance Update

PHASE_82_RATIFIED_CURRENT_SUCCESS_ACCEPTANCE_DEMO

The Phase 80 current-success result now has an explicit operator acceptance record produced through the Phase 81 acceptance surface.

Accepted task id:

$TaskId

Acceptance record id:

$AcceptanceRecordId

This means the current success proof has crossed the operator-acceptance membrane: the bounded result was not merely completed and reviewable; it was explicitly accepted with caveats acknowledged.

The caveat remains unchanged.

This acceptance does not prove autonomous AI coding ability.

This acceptance does not prove model-backed generation.

This acceptance does not broaden deterministic verification beyond its current bounded-tripwire role.
## Phase 84 Ollama Provider Contract Update

PHASE84_OLLAMA_PROVIDER_CONTRACT_METADATA_AND_MOCKED_HTTP_UNIT_TESTS

Phase 84 adds product-side Ollama provider contract metadata and mocked HTTP unit tests.

This does not change the current-success caveat.

The current success proof still does not prove autonomous AI coding ability.

The current success proof still does not prove model-backed generation.

Phase 84 proves only that the product-side Ollama provider can construct a bounded mocked /api/generate request, parse the expected mocked response shape, surface metadata, and route through the dispatcher without live model/provider/runtime execution.

PHASE84_OLLAMA_PROVIDER_CONTRACT_METADATA_AND_MOCKED_HTTP_UNIT_TESTS

## Phase 85 Guarded Live Ollama Smoke Harness

PHASE85_GUARDED_LIVE_OLLAMA_SMOKE_HARNESS_AND_GUARD_TESTS

Phase 85 adds a guarded live Ollama smoke harness for a future explicitly authorized live provider proof.

This does not change the current-success caveat.

The current success proof still does not prove autonomous AI coding ability.

The current success proof still does not prove model-backed generation.

Phase 85 proves only that a live Ollama smoke path exists and blocks unless ORCH_PHASE85_ALLOW_LIVE_OLLAMA=YES is explicitly set.

PHASE85_GUARDED_LIVE_OLLAMA_SMOKE_HARNESS_AND_GUARD_TESTS

## Phase 85 Repair Note

PHASE85_REPAIR_GUARDED_SMOKE_IMPORT_PATH_AND_FALSE_PASS_PROOF

The initial Phase 85 run was not ratified because the guard unit test failed before the later export/pass markers.

This repair preserves the current-success caveat.

The current success proof still does not prove autonomous AI coding ability.

The current success proof still does not prove model-backed generation.

Phase 85, after repair, proves only that the live Ollama smoke path is guarded and blocks without ORCH_PHASE85_ALLOW_LIVE_OLLAMA=YES.

PHASE85_REPAIR_GUARDED_SMOKE_IMPORT_PATH_AND_FALSE_PASS_PROOF

## Phase 85 Static Analysis Repair Note

PHASE85_REPAIR_STATIC_ANALYSIS_FALSE_FAILURE

The prior Phase 85 repair failed because a static test compared raw text positions rather than executable import behavior.

This repair preserves the current-success caveat.

The current success proof still does not prove autonomous AI coding ability.

The current success proof still does not prove model-backed generation.

Phase 85 proves only that the live Ollama smoke path exists and blocks without ORCH_PHASE85_ALLOW_LIVE_OLLAMA=YES.

PHASE85_REPAIR_STATIC_ANALYSIS_FALSE_FAILURE

## Phase 85 UTF-8 No-BOM Repair Note

PHASE85_REPAIR_UTF8_NO_BOM_GUARD_TEST

The prior Phase 85 static-analysis repair failed because a UTF-8 BOM caused AST parsing to fail.

This repair preserves the current-success caveat.

The current success proof still does not prove autonomous AI coding ability.

The current success proof still does not prove model-backed generation.

Phase 85 proves only that the live Ollama smoke path exists and blocks without ORCH_PHASE85_ALLOW_LIVE_OLLAMA=YES.

PHASE85_REPAIR_UTF8_NO_BOM_GUARD_TEST


## Phase 86 Direct Live Ollama Smoke Ratification

PHASE86_RATIFIED_DIRECT_LIVE_OLLAMA_SMOKE_MANUAL_TEST_ENVIRONMENT

Phase 86 reduces the model-backed generation caveat only for a direct provider smoke.

It proves that the product-side Ollama provider can complete one real local model-backed /api/generate call against a manually prepared Windows Ollama test environment.

This does not ratify full current-success under Ollama.

The current-success criterion remains ratified only under the Phase 80 deterministic local_file provider caveat until a later boundary proves a full persisted task/artifact/verifier/reviewer/current-success flow under Ollama.

Phase 86 also does not prove autonomous AI coding, semantic correctness, installer-managed model provisioning, platform/OpenClaw behavior, Discord behavior, WSL behavior, bridge/adapter behavior, or broad model reliability.

PHASE86_RATIFIED_DIRECT_LIVE_OLLAMA_SMOKE_MANUAL_TEST_ENVIRONMENT

## Phase 88 Current-Success Update ? 2026-06-12 22:33:20Z

Marker: PRODUCT_PHASE88_LIVE_OLLAMA_ORCHESTRATION_SPINE_CURRENT_SUCCESS_PROOF

Current-success state now includes a live model-backed Ollama orchestration-spine proof through the product engine/dispatcher path.

Accepted scope:

- provider `ollama`;
- model `llama3.2:latest`;
- provider contract `ollama_generate_v1`;
- runtime execution metadata persisted;
- model execution metadata persisted;
- execution artifact persisted;
- deterministic verifier result persisted;
- current-success review surfaced.

Explicit exclusions:

- semantic correctness is not proven;
- no exact bounded-response compliance proof;
- no autonomous file mutation or code writeback proof;
- no installer-managed provisioning proof;
- no WSL/OpenClaw/platform/Discord/bridge/adapter proof.

Output caveat: PRODUCT_PHASE88_ARTIFACT_OUTPUT_PROSPECTIVE_NOISY_NOT_EXACT_BOUNDED_COMPLIANCE

## Phase 89 And Phase 91 Contract-Hardening Update

Markers:

- `PHASE89_STRICT_OLLAMA_JSON_TASK_OUTPUT_CONTRACT_SOURCE_TEST_PROVEN`
- `PHASE91_CORRECTED_LOCAL_PROOF_RESULT=PASS`

Proof-visible current-state summary:

- strict Ollama output contract exists;
- semantic status routing is implemented for `completed`, `blocked`, and `needs_review`;
- unsupported provider status is non-success;
- reviewer/performer schema separation exists;
- this is targeted local unit proof only;
- live model compliance is not proven;
- no code writeback claim is made;
- no verification provenance repair claim is made;
- no Phase 74 synthetic execution repair claim is made;
- production readiness is not claimed;
- export and upload pending.

The current source/test-proven state now includes:

- a strict raw JSON Ollama task output contract;
- exact task envelope fields `task_id`, `status`, `summary`, `evidence`, `files_touched`, and `caveats`;
- deterministic rejection of malformed, wrapped, structurally invalid, mismatched, empty, or prospective task output;
- semantic engine routing for valid Ollama `completed`, `blocked`, and `needs_review` statuses;
- completion only when a `completed` envelope also passes existing verification and adequacy gates;
- `blocked` and `needs_review` routing to task `needs_review`, not task completion;
- non-`success` provider execution routing, including Codex `not_implemented`, to `execution_failed`;
- separate Ollama performer task-output and reviewer recommendation schemas.

This update is targeted, unit-level, and local source/test proof. It does not supersede Phase 88's live-output caveat and does not prove that a live Ollama model consistently follows the hardened contract.

The following remain explicitly open:

- live Ollama contract compliance;
- semantic correctness of model answers;
- model-backed code mutation or writeback;
- verification provenance and no-op verification semantics;
- Phase 74 authorized case-packet synthetic completion semantics;
- reviewer subtype/contract-selector nuance;
- test isolation;
- path containment;
- atomic persistence and locking;
- service/API, authentication, and multi-user support;
- packaging and CI;
- production readiness;
- export and upload of the Phase 89/91 documentation state.

## Phase 92 Causal Verification Provenance Update

Marker:

`PHASE92_CAUSAL_VERIFICATION_CORRECTED_LOCAL_PROOF_RESULT=PASS`

Phase 92 causal verification provenance adds an opt-in causal-change requirement to the normal engine path.

The current locally source/test-proven behavior includes:

- task field `requires_causal_change`, defaulting to false;
- pre/post filesystem snapshots for declared `files_in_scope` targets;
- SHA-256 transition evidence through `existed_before`, `existed_after`, `sha256_before`, and `sha256_after`;
- no-write provider success is rejected when causal change is required;
- same-content rewrite is rejected when causal change is required;
- new-file creation and existing-file hash change can satisfy causal verification;
- verifier record binds causal evidence to `execution_artifact_id`;
- Proof marker: verifier record binds causal evidence to execution_artifact_id.
- full file contents are not stored;
- default state-only verification remains available when causal change is not required;
- provider execution failure retains precedence as `execution_failed`;
- Phase 91 Ollama status routing remains covered.

The Phase 92 repair is opt-in and limited to the normal engine path. Phase 74 synthetic completion is not repaired.

Explicit non-proofs and open caveats:

- live model compliance is not proven;
- semantic correctness is not proven;
- autonomous writeback is not proven;
- no global path-containment repair;
- production readiness is not claimed;
- export/upload pending after Phase 92.

## Phase 93 Synthetic Completion Correction

Phase 93 removes the Phase 74 path that previously treated authorization plus a locally written no-execution artifact as task completion.

Current interpretation:

- authorization is not execution;
- a task cannot be marked completed without a real execution boundary;
- a valid Phase 73 authorization remains queued and returns `needs_operator_decision` at the Phase 74 surface;
- no artifact or execution artifact identity is created by that deferred result.

The accepted uploaded Phase 92 ZIP SHA-256 is `9485206278FDEAC994C92D7990ADFD2AC0D524D2CF3287772E99B0C58CFCB7C8`. Phase 93 local mutation makes the working tree newer than that accepted artifact; no export or upload was performed.

## Phase 94 Path Containment Update

Marker:

`PHASE94_PATH_AND_RECORD_IDENTITY_CONTAINMENT_LOCAL_SOURCE_TEST_PROVEN=PASS`

The current locally source/test-proven state now rejects unsafe filesystem-backed task and artifact identities and rejects task-declared absolute, parent-traversal, or resolved-outside-project file targets in normal verification, causal snapshots, declared checks, and the deterministic `LocalFileProvider`.

Safe relative task targets remain supported. Phase 91 provider routing, Phase 92 causal verification semantics, and Phase 93 synthetic-completion rejection remain intact.

This is bounded containment hardening, not production-readiness proof. It does not add runtime, model, provider, platform, real Phase 74 execution, export, package, cleanup, deletion, or archive behavior.

Coordinator-side uploaded verification accepted Phase 93 with ZIP SHA-256 `B8D761B07C17D55D700B408A8F755204799F1618C937B8D28668DAA0470D73AB`. The hash proof is external to source files later exported; Phase 94 has not been exported or uploaded.

## Phase 95 Task Execution Policy Update

Marker:

`PHASE95_TASK_EXECUTION_POLICY_CLASSIFICATION_LOCAL_SOURCE_TEST_PROVEN=PASS`

The current locally source/test-proven state now distinguishes report-only work from filesystem-mutation work.

- Missing task policy remains backward compatible as `report_only`.
- Report-only tasks retain existing provider, adequacy, deterministic verification, and no-scope skipped-verification behavior.
- Filesystem-mutation tasks require bounded non-empty relative targets and causal filesystem change.
- Mutation tasks cannot complete through state-only verification or provider success with no changed target.
- Unknown policies, empty mutation scope, absolute targets, and parent-traversal targets cannot reach provider dispatch.
- Policy classification is visible in persisted task, artifact, and verifier evidence.

This strengthens the current success bar by making completion semantics match declared task intent. It does not prove semantic correctness, autonomous writeback, real Phase 74 execution, or production readiness.

Coordinator-side Phase 94 upload verification is accepted with marker `PHASE94_PRODUCT_ZIP_UPLOAD_VERIFY_RESULT=PASS` and ZIP SHA-256 `614282E4884F901F07F96487F1D0D71E563A875E881E4E7DCD4BDDBC44AAB88E`. That artifact hash proof is external to source files later exported.

## Phase 96 Canonical Execution Delegation Update

Marker:

`PHASE96_CANONICAL_CASE_PACKET_EXECUTION_DELEGATION_LOCAL_SOURCE_TEST_PROVEN=PASS`

The current locally source/test-proven state now gives valid authorized case-packet work an honest path into the normal task lifecycle.

- Authorization records `queued_for_canonical_execution`; it does not execute the task.
- The task remains queued and can be selected by the existing normal engine path only inside a separate execution boundary.
- No synthetic artifact, completion state, provider dispatch, verification, model call, or runtime claim is produced.
- Task/run identity, execution policy, bounded file scope, causal-change requirement, source case-packet identity, source artifact, and available operator/reviewer decision provenance remain inspectable.
- Report-only compatibility remains intact.
- Filesystem-mutation tasks remain subject to Phase 95 bounded-target and causal-change completion requirements.

This improves honest contact between authorization and execution without adding autonomous writeback or live execution behavior. Semantic correctness and production readiness are not proven.

Coordinator-side Phase 95 export/upload verification is accepted with markers `PHASE95_PRODUCT_ZIP_EXPORT_VERIFY_RESULT=PASS` and `PHASE95_PRODUCT_ZIP_UPLOAD_VERIFY_RESULT=PASS`, and ZIP SHA-256 `260EC3280ACE2F1BB40DDAD07451D7C9648429F8E6FACDEE46647620EF6B41D8`.

The earlier relay FAIL was a ZIP path-normalization helper false negative superseded by coordinator direct inspection, not an artifact failure. That final artifact hash proof is external to source files later exported.

## Phase 97 Model-Backed Patch Proposal Protocol Update

Marker:

`PHASE97_MODEL_BACKED_PATCH_PROPOSAL_PROTOCOL_LOCAL_SOURCE_TEST_PROVEN=PASS`

The current locally source/test-proven state now provides a bounded, non-executing representation for proposed filesystem changes.

- Patch proposals are available only for `filesystem_mutation` tasks.
- Task scope, proposed-change paths, and unified-diff paths use the shared Phase 94 containment policy.
- Proposal artifacts preserve bounded task, policy, change, diff, rationale, risk, validation, source, and creation-time evidence.
- Proposals require later operator apply and remain explicitly unapplied.
- Proposal creation does not mutate target files, task status, or execution artifact identity.
- Proposal artifacts are reviewable evidence, not execution artifacts, completion proof, or Phase 92 causal-change proof.
- Report-only tasks are deterministically rejected as policy-incompatible.
- No provider or engine integration was added.

This is the bridge design between report-only model output and a future mutation-capable workflow. It is not the mutation bridge itself. A later explicit operator apply or separately authorized execution boundary remains necessary.

Coordinator-side Phase 96 export/upload verification is accepted with markers `PHASE96_PRODUCT_ZIP_EXPORT_VERIFY_RESULT=PASS` and `PHASE96_PRODUCT_ZIP_UPLOAD_VERIFY_RESULT=PASS`, and ZIP SHA-256 `15366CE13B66471EA9C4C4860169D85A75729498260B77584A8B958E75A1C728`.

That final artifact hash proof is external to source files later exported. Phase 97 does not prove live model proposal generation, patch applicability, semantic correctness, autonomous writeback, or production readiness.

## Phase 98 Patch Proposal Operator Apply Authorization Gate Update

Marker:

`PHASE98_PATCH_PROPOSAL_OPERATOR_APPLY_AUTHORIZATION_GATE_LOCAL_SOURCE_TEST_PROVEN=PASS`

The current locally source/test-proven state now provides the explicit operator
decision membrane after a stored Phase 97 patch proposal.

- Valid filesystem-mutation proposals can receive `authorize_apply` or
  `reject_apply` operator decision artifacts.
- Authorization preserves proposal, task, optional run, execution policy,
  bounded authorized files, operator identity label, rationale, source, and
  creation-time evidence.
- `authorize_apply` means authorized for a future apply boundary, not yet
  applied.
- Every decision artifact requires a separate apply boundary and remains
  explicitly unapplied.
- Missing, report-only, already-applied, non-operator-gated, absolute-path,
  parent-traversal, outside-project, and outside-proposal-scope cases are
  rejected.
- Authorization does not mutate the proposal, target files, task status, or task
  execution artifact identity.
- Authorization is governance evidence, not execution, completion, verification,
  or causal-change evidence.
- No engine, provider, model, runtime, or patch-application integration was
  added.

This strengthens honest contact between proposal review and future mutation:
operator approval is now durable and inspectable without being misrepresented as
application or completion. A later separately authorized apply boundary remains
required and must produce its own mutation and causal proof.

Coordinator-side Phase 97 export/upload verification is accepted with markers
`PHASE97_PRODUCT_ZIP_EXPORT_VERIFY_RESULT=PASS` and
`PHASE97_PRODUCT_ZIP_UPLOAD_VERIFY_RESULT=PASS`, and ZIP SHA-256
`4F8F0FFE180CA94945F39677319D4578991F25A7654B17C1D1DABEAC01733561`.

That final artifact hash proof is external to source files later exported. Phase
98 does not prove patch applicability, semantic correctness, source mutation,
causal change, autonomous writeback, or production readiness.

## Phase 99 Bounded Patch Apply Engine Update

Marker:

`PHASE99_BOUNDED_PATCH_APPLY_ENGINE_FOR_OPERATOR_AUTHORIZED_PROPOSALS_LOCAL_SOURCE_TEST_PROVEN=PASS`

The current locally source/test-proven state now supports the first explicit
operator-authorized bounded source mutation.

- A valid Phase 98 `authorize_apply` artifact is mandatory.
- It must reference a valid unapplied Phase 97 filesystem-mutation proposal that
  still requires operator apply.
- Exact text operations reject zero or multiple `expected_before` matches.
- All operations are staged before any file write.
- Every path must pass Phase 94 containment and appear in both proposal and
  authorization scope.
- Successful application produces a separate apply-result artifact containing
  changed files, operation identities, and per-file before/after SHA-256.
- Proposal and authorization artifacts remain unchanged.
- Task status and execution artifact identity remain unchanged.
- Apply results require later verification and do not establish full
  verification or task completion.
- No provider, model, runtime, or normal-engine automatic apply behavior was
  added.

This capability requires durable operator authorization, exact deterministic
preconditions, bounded scope, and inspectable causal evidence. It remains
narrower than a general patch engine and does not infer semantic correctness.

Coordinator-side Phase 98 export/upload verification is accepted with markers
`PHASE98_PRODUCT_ZIP_EXPORT_VERIFY_RESULT=PASS` and
`PHASE98_PRODUCT_ZIP_UPLOAD_VERIFY_RESULT=PASS`, and ZIP SHA-256
`354BC287532E3429EF056ABAD850431303139843954710EA1454EE44FBE24A09`.

That final artifact hash proof is external to source files later exported. Phase
99 does not prove full task verification, semantic correctness, general patch
compatibility, autonomous writeback, or production readiness.

## Phase 100 Patch Apply Result Verification And Task Completion Gate Update

Marker:

`PHASE100_PATCH_APPLY_RESULT_VERIFICATION_AND_TASK_COMPLETION_GATE_LOCAL_SOURCE_TEST_PROVEN=PASS`

The current locally source/test-proven state now gives Phase 99 causal apply
evidence an explicit read-only completion-eligibility review.

- Missing apply evidence is classified as `insufficient_evidence`.
- Malformed, identity-mismatched, path-unsafe, no-change, or otherwise
  incomplete evidence is `rejected`.
- Only bounded evidence with non-empty changed files and operations, differing
  per-file hashes, expected task identity, proposal and authorization linkage,
  causal-change truth, and pending-verification truth is
  `eligible_for_completion`.
- Eligibility does not mutate task state or establish completion.
- Review performs no patch application and does not enter the normal engine.

This improves the inspectability of the proposal-to-authorization-to-apply
chain without overstating byte-change evidence as task success. A later explicit
completion boundary must still evaluate all task success criteria before any
task-state mutation.

Coordinator-side Phase 99 export/upload verification is accepted with markers
`PHASE99_PRODUCT_ZIP_EXPORT_VERIFY_RESULT=PASS` and
`PHASE99_PRODUCT_ZIP_UPLOAD_VERIFY_RESULT=PASS`, and ZIP SHA-256
`1D8C04CE30D7F1D947C4DACCCF981A171492220D3DB63AD372D824BE3EB708BF`.

That final artifact hash proof is external to source files later exported.
Phase 100 does not prove semantic correctness, full task verification, task
completion, autonomous writeback, or production readiness.

## Phase 101 Verified Patch Apply Task Completion Finalization Gate Update

Marker:

`PHASE101_VERIFIED_PATCH_APPLY_TASK_COMPLETION_FINALIZATION_GATE_LOCAL_SOURCE_TEST_PROVEN=PASS`

The current locally source/test-proven state now provides the explicit final
task-state boundary after the Phase 97-100 proposal, authorization, apply, and
eligibility chain.

- A supplied Phase 100 eligibility result is revalidated against its referenced
  stored Phase 99 apply result rather than trusted by label.
- Task, apply, proposal, authorization, bounded changed-file, causal-change, and
  verification evidence must align.
- Only queued or in-progress filesystem-mutation tasks can move to `completed`.
- Successful finalization writes a separate immutable evidence artifact.
- Rejected, missing, unsafe, mismatched, incompatible, or duplicate-completion
  attempts leave the task unfinalized and create no finalization artifact.
- Finalization applies no patch and runs no provider, model, runtime, or normal
  engine behavior.

This closes the explicit governed patch lifecycle without making completion
automatic. The operator-facing boundary remains separate from normal engine
execution, and its evidence summary states that semantic correctness is not
independently proven.

Coordinator-side Phase 100 export/upload verification is accepted with markers
`PHASE100_PRODUCT_ZIP_EXPORT_VERIFY_RESULT=PASS` and
`PHASE100_PRODUCT_ZIP_UPLOAD_VERIFY_RESULT=PASS`, and ZIP SHA-256
`62E0F5F8B484FE056B9A75CF9157D718659CC02B9B4E12497BCE95ADB4A553F0`.

That final artifact hash proof is external to source files later exported.
Phase 101 does not prove semantic correctness, broad test adequacy, autonomous
writeback, or production readiness.

## Phase 102 Cross-Track Scope Note

The current success criterion remains intentionally focused on a bounded coding
task. That present-tense bar is narrower than the product vision and must not be
treated as the identity or complete scope of the Orchestrator product.

`docs/TRACKS_AND_OPEN_THREADS.md` preserves the broader active and intended
product tracks, their proof posture, and their open threads. Coordinator
sessions must use that ledger before recommending an NBM or changing tracks so
coding-spine momentum does not erase domain-general intake, local-first
routing, RAG/local document lookup, reminders, lightweight answers,
persistence, testing, service/UI, structure, platform separation, and
role-routing concerns.

This note does not broaden or rewrite the current success criterion.

`PHASE102_CROSS_TRACK_LEDGER_AND_OPEN_THREAD_REGISTER_LOCAL_DOCS_PROVEN=PASS`

## Phase 103 Domain-General Routing Scope Note

Phase 103 adds an initial domain-general request taxonomy and route-envelope
validation contract, but it does not broaden the current success criterion.

The present-tense success bar remains coding-task focused: a bounded
operator-provided coding task should produce persisted, inspectable, minimally
verified outcome evidence with clear classification.

Phase 103 is an intake/routing governance membrane only. It does not prove a
general assistant product, live local-first model routing, RAG/local document
lookup, reminders, scheduling, web lookup, lightweight answer productization,
service/API/UI behavior, production readiness, autonomous writeback, or
production task execution.

`PHASE103_DOMAIN_GENERAL_REQUEST_INTAKE_TAXONOMY_AND_ROUTING_CONTRACT_LOCAL_SOURCE_TEST_DOCS_PROVEN=PASS`

## Phase 104 Documentation Context Map Scope Note

Phase 104 adds `docs/CONTEXT_MAP.md` and clarifies documentation authority,
bounded contexts, owned language, active-vs-historical document separation, and
artifact-proof hygiene.

This phase does not broaden the current success criterion. The present-tense
success bar remains coding-task focused: a bounded operator-provided coding
task should produce persisted, inspectable, minimally verified outcome evidence
with clear classification.

Phase 104 is docs/control only. It does not prove runtime behavior,
provider/model behavior, route execution, RAG/local-document lookup, reminders,
scheduling, web lookup, autonomous writeback, export/upload, production task
execution, or production readiness.

`PHASE104_DOCS_CONTEXT_MAP_AND_LANGUAGE_AUTHORITY_MODEL_LOCAL_DOCS_PROVEN=PASS`

## Phase 105 Open-Thread Triage And Startup-Load Discipline Scope Note

Phase 105 adds docs/control discipline for open-thread triage and startup-load
classes. It requires coordinator re-entry sessions to triage visible open
threads before NBM ranking and clarifies that append-heavy evidence/history
docs are read on demand when a boundary requires proof, phase history, source
registration, or reconciliation.

This phase does not broaden the current success criterion. The present-tense
success bar remains coding-task focused: a bounded operator-provided coding
task should produce persisted, inspectable, minimally verified outcome evidence
with clear classification.

Phase 105 is docs/control only. It does not prove runtime behavior,
provider/model behavior, route execution, RAG/local-document lookup, reminders,
scheduling, web lookup, autonomous writeback, export/upload, production task
execution, or production readiness.

`PHASE105_OPEN_THREAD_TRIAGE_AND_STARTUP_LOAD_DISCIPLINE_LOCAL_DOCS_PROVEN=PASS`

## Phase 228 Route-Mediated Provider Marker-Smoke Runtime Registration

Phase 228 registers the accepted operator proof:

`PHASE_216_RETRY3_ROUTE_MEDIATED_PROVIDER_SMOKE_LIVE_RUNTIME_OPERATOR_PROOF=PASS`

For the provider/model route-mediated marker-smoke path only, the previously
open runtime-marker gap is now closed by a single live local Ollama
`/api/generate` call through the route-mediated live transport CLI. The
accepted artifact is classified as
`route_mediated_provider_smoke_runtime_marker_pass`, with HTTP `200`, JSON
parse success, returned model `qwen3:30b-a3b-instruct-2507-q4_K_M`, response
text `ORCH_ROUTE_PROVIDER_SMOKE_OK`, `done=true`, and marker present.

This does not broaden the current success criterion into production readiness
or general provider competence. It does not prove semantic correctness, real
workload sufficiency, long-context behavior, sustained-load stability, Hermes
behavior, OpenClaw behavior, Discord behavior, WSL behavior, worker dispatch,
or `qwen3.6:35b-a3b` suitability.

`PHASE228_ROUTE_MEDIATED_PROVIDER_SMOKE_LIVE_RUNTIME_PROOF_REGISTRATION_DOCS_PROVEN=PASS`

## Phase 235 General Answer Lightweight Report-Only Scope Note

Phase 235 adds a deterministic lightweight `general_answer` report-only
contract for structured low-risk requests.

This does not broaden the current success criterion into general semantic
answer quality, model-backed generation, live routing, RAG/local lookup, web
lookup, scheduler/reminder execution, connector execution, worker dispatch,
Codex dispatch, service/API/UI productization, or production readiness.

The present-tense success bar remains coding-task focused unless a later
explicit boundary changes it.

`PHASE235_GENERAL_ANSWER_LIGHTWEIGHT_REPORT_ONLY_CONTRACT_SOURCE_TEST_DOCS_PROVEN=PASS`
