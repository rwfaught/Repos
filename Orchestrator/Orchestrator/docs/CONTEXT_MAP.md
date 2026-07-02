# Context Map

## Purpose And Authority

This file defines the Orchestrator product documentation context map and
language authority model. It exists to make document roles, bounded contexts,
owned language, and proof posture explicit for future coordinator re-entry and
worker handoff.

This file is authoritative for language/context architecture only. It does not
authorize implementation, cleanup, export, package creation, provider/model
execution, runtime behavior, platform behavior, or production task execution.

This file does not replace:

- `docs/TRACKS_AND_OPEN_THREADS.md`
- `docs/OPEN_THREAD_TRIAGE_PROTOCOL.md`
- `docs/PHASE_INDEX.md`
- `docs/ACTION_LOG.md`
- `docs/SOURCE_MANIFEST.md`
- `docs/CURRENT_SUCCESS_CRITERION.md`
- `docs/PROJECT_VISION.md`
- phase docs
- the external platform/OpenClaw memory capsule

Those documents and external authorities retain their own scope-specific
authority. This map explains how their language and contexts should be kept
separate.

## Document Authority Model

| Layer | Primary purpose | Authority docs/files | Notes |
| --- | --- | --- | --- |
| Constitutional direction | Defines what Orchestrator is trying to become and what growth must preserve. | `docs/PROJECT_VISION.md` | Long-range direction, not present capability proof. |
| Present success bar | Defines what a successful run means today. | `docs/CURRENT_SUCCESS_CRITERION.md` | Present-tense product bar, not a roadmap or phase authorization. |
| Coordinator/governance method | Defines ranking, approval, handoff, review, closure, re-entry discipline, open-thread triage, startup-load discipline, and project continuity evidence discipline. | `docs/ORCHESTRATOR_METHOD.md`; `docs/ORCHESTRATOR_INTERACTION_MODEL.md`; `docs/STARTUP_BRIEF.md`; `docs/OPEN_THREAD_TRIAGE_PROTOCOL.md`; `docs/PROJECT_CONTINUITY_EVIDENCE_PROTOCOL.md` | Governs process semantics and evidence vocabulary, not runtime behavior. |
| Active product state/open threads | Preserves accepted track state, open threads, proof posture, triage status, and drift warnings. | `docs/TRACKS_AND_OPEN_THREADS.md`; `docs/OPEN_THREAD_TRIAGE_PROTOCOL.md` | Active coordination ledger and triage protocol; this context map does not complete its open threads. |
| Evidence/history stack | Records ordered phase history, action logs, source identity, artifact caveats, and accepted proof claims. | `docs/PHASE_INDEX.md`; `docs/ACTION_LOG.md`; `docs/SOURCE_MANIFEST.md`; phase docs | Evidence/history authorities; not mandatory full-load startup payloads unless the boundary requires phase history, source registration, proof, or reconciliation. |
| Language/context architecture | Defines bounded contexts, owned terms, and do-not-confuse rules for docs. | `docs/CONTEXT_MAP.md` | Clarifies language authority only; it does not clean up historical docs by itself. |

## Bounded Context Map

### Product Governance Context

Purpose: preserve Orchestrator as the governing layer for AI-assisted work,
including ranking, approval gates, role boundaries, closure, and re-entry.

Owned language: Orchestrator, coordinator, Roger/operator, Relay, worker, NBM,
boundary, open thread, caveat.

Authority docs/files:

- `docs/PROJECT_VISION.md`
- `docs/ORCHESTRATOR_METHOD.md`
- `docs/ORCHESTRATOR_INTERACTION_MODEL.md`
- `docs/STARTUP_BRIEF.md`
- `docs/TRACKS_AND_OPEN_THREADS.md`
- `docs/OPEN_THREAD_TRIAGE_PROTOCOL.md`

Non-authority / do-not-confuse warnings:

- Governance health is not product execution proof.
- Worker PASS is not coordinator artifact acceptance.
- Relay construction is not worker execution.
- Authorization is not execution.
- This context map is not a cleanup-completion record.
- Startup-load discipline keeps append-heavy evidence/history docs on demand
  unless the boundary requires them.

Current proof posture: governance and interaction protocols are documented;
Phase 102 locally proved the durable cross-track ledger; Phase 104 locally
proves only the documentation language/context map.

### Startup Load Classes

- `ALWAYS_READ_CONTROL`: small docs needed for role, protocol, and current
  orientation.
- `CURRENT_STATE`: docs used to understand active product state and open
  threads.
- `ON_DEMAND_EVIDENCE`: append-heavy docs such as `ACTION_LOG.md`,
  `SOURCE_MANIFEST.md`, `PHASE_INDEX.md`, phase docs, and historical design
  docs. Read when the boundary requires evidence, phase history, source
  registration, proof, or reconciliation.
- `EXTERNAL_TRACK_PACKAGE`: platform/OpenClaw/Hermes/model/RAG package docs.
  Read only when that track or an integration boundary is in scope.

### Project Continuity Evidence Context

Purpose: govern portable re-entry proof, command-batch evidence, durable run
artifact placement, evidence capsules, source authority classification,
handoff requirements, redaction, shell parity, and project-boundary runtime
fact separation.

Owned language: repo proof, source capsule proof, uploaded-source proof,
operator terminal proof, worker report, accepted fact, open thread, non-proof,
source authority class, run artifact, source capsule freshness, integration
boundary.

Authority docs/files:

- `docs/PROJECT_CONTINUITY_EVIDENCE_PROTOCOL.md`
- `docs/ORCHESTRATOR_METHOD.md`
- `docs/ORCHESTRATOR_INTERACTION_MODEL.md`
- `docs/STARTUP_BRIEF.md`
- `docs/SOURCE_MANIFEST.md`
- `docs/TRACKS_AND_OPEN_THREADS.md`

Non-authority / do-not-confuse warnings:

- Command logs are evidence records, not permission to mutate or execute.
- Source capsules may lag live repo state and require freshness checks.
- Worker reports are not coordinator acceptance or artifact proof by
  themselves.
- Run artifacts should not be placed under the git worktree unless a boundary
  explicitly makes them source artifacts.
- Project-specific runtime facts do not transfer across Orchestrator,
  Obsidian/LightRAG/Hermes, Blender, OpenClaw, or future project boundaries
  without an explicit integration boundary.

Current proof posture: Phase 269 adds docs-only governance and ledger
registration for the protocol. It does not implement wrapper tooling, run
runtime/provider/model/platform probes, refresh source capsules, export,
package, commit, push, or prove service/API/UI behavior.

### Request Intake / Routing Context

Purpose: classify human objectives into bounded request types and validate
structured route envelopes before downstream capability use is admitted.

Owned language: route membrane, route envelope, route admission, request type,
capability, substrate, provider/model.

Authority docs/files:

- `docs/PROJECT_VISION.md`
- `docs/ORCHESTRATOR_INTERACTION_MODEL.md`
- `docs/CAPABILITY_REGISTRY.md`
- `docs/PROMPT_TO_ENVELOPE_INFERENCE.md`
- `docs/PHASE_103.md`
- `orchestrator/request_routing.py`
- `tests/test_phase_103_domain_general_request_routing_contract.py`
- `docs/TRACKS_AND_OPEN_THREADS.md`

Non-authority / do-not-confuse warnings:

- Route-envelope validation is not request execution.
- Route admission is not live model routing.
- Capability labels are not proof that a capability is implemented.
- Substrate description must not become provider/model selection.
- Coding remains one request route, not the product identity.

Current proof posture: Phase 103 validates structured route envelopes only. It
does not implement live route proposal, model routing, RAG/local-document
lookup, reminders, scheduling, web lookup, autonomous writeback, or production
task execution.

Capability registry maturity belongs to this context. It defines
documentation-level capability names, classes, maturity statuses, permission
burdens, validation burdens, and stop conditions for route admission. It
interacts with Evidence / Artifact Proof Context when capability claims depend
on proof status, but it does not authorize live execution or
provider/model/substrate selection.

Prompt-to-envelope inference belongs to this context. It feeds structured
intake and route proposal, interacts with capability registry maturity and
Evidence / Artifact Proof Context, and does not authorize route admission or
execution.

Local-first model router policy belongs to this context. It recommends
boundary posture from structured request metadata only: local-first answer,
provider/frontier review boundary, worker/Codex boundary, RAG/local-document
boundary, scheduler/reminder boundary, web/research boundary, block, or
clarify. It does not execute providers or models, select runtimes or
platforms, dispatch workers, perform RAG/web/scheduler/connector work, or
authorize production execution.

Local-first provider catalog doctrine belongs to this context as provider-tier
policy evidence. It defines local model candidate, frontier provider candidate,
worker/Codex boundary, RAG/local-document boundary, scheduler/reminder
boundary, web/research boundary, and blocked/unavailable provider posture as
non-executing catalog entries. Catalog posture is not provider/model/runtime
availability, provider selection, worker dispatch, boundary crossing, route
execution, or production readiness.

Provider-catalog-backed router recommendation envelopes also belong to this
context. They expose catalog key, tier, maturity, boundary, authority,
execution/selection flags, catalog fallback, catalog escalation posture,
catalog non-proofs, and catalog activity flags as reviewable policy evidence.
The envelope is not live provider routing, model selection for execution,
runtime import, worker dispatch, route execution, or production readiness.

Provider/runtime probe boundary packet doctrine belongs to this context as an
airlock between provider policy and future runtime proof. It drafts authorized
scope, expected evidence, explicit exclusions, stop conditions, non-proofs, and
coordinator acceptance requirements for a later probe boundary. It does not
perform provider/runtime imports, provider or model availability probes,
execution, dispatch, lookup, scheduling, connector work, route execution, or
production readiness proof.

Manual review integration of provider probe packet status belongs to this
context as coordinator-visible metadata. Default review output is blocked or
awaiting explicit probe-boundary authorization, scope, and evidence. Rendering
that status is not probe authorization, provider/runtime import, execution,
route execution, or production readiness.

Provider probe packet CLI draft adapter language also belongs to this context.
The CLI may pass explicit paperwork metadata into manual review output, but it
does not execute probes, import runtimes, select models for execution, dispatch
workers, perform lookup/scheduling/connector work, execute routes, or prove
production readiness.

Operator provider proof registration belongs to this context only as evidence
language. Phase 130 registers CLI paperwork rendering with an exit-code caveat.
Phase 131 registers read-only local Ollama `/api/tags` provider-surface
visibility and model list visibility at one point in time. Provider
availability proof in this context means read-only provider surface visibility
only; it is not model execution, model correctness, model loadability, route
execution, worker dispatch, RAG/web/scheduler/connector work, or production
readiness.

Model metadata proof registration belongs to this context only as evidence
language. Phase 133 registers read-only local Ollama `/api/show` metadata
visibility for `qwen3-30b-24k:latest` at one point in time, including GGUF,
Qwen3 MoE, 30.5B, Q4_K_M, model-info metadata, template, parameters, and
license presence. Model metadata visibility means candidate metadata
introspection only; it is not generation, chat, semantic correctness, model
loadability, VRAM sufficiency, route execution, provider/model/runtime
execution, worker dispatch, RAG/web/scheduler/connector work, or production
readiness.

Git checkpoint registration belongs to this context only as source publication
language. Phase 135 records a local explicit-docs commit checkpoint for the
Phase 130 through Phase 134 proof ledgers at `a4c6815`; Phase 136 records the
remote push checkpoint to `origin/main`; Phase 137 registers those checkpoint
proofs in source docs/ledgers. Commit/push checkpoint means durable git/source
publication of prior proof ledgers only. It is not provider/model/runtime
execution, route execution, product behavior, or production readiness.

Remote-alignment checkpoint registration belongs to this context only as
source publication confirmation language. Phase 138 records a local
explicit-docs commit checkpoint for the Phase 135 through Phase 137 checkpoint
ledger chain at `18da1e7`; Phase 139 records that `git push origin main`
returned `Everything up-to-date`; Phase 140 registers those checkpoint proofs
in source docs/ledgers. Remote-alignment checkpoint means durable git/source
publication was confirmed. It is not provider/model/runtime execution, route
execution, product behavior, or production readiness.

Provider evidence registry language belongs to this context only as structured
evidence posture. Phase 143 records accepted Phase 131 provider-surface
visibility and Phase 133 model metadata visibility in deterministic source
data so coordinator/manual-review reports can display it. Provider evidence
visibility is structured evidence, not execution authority, provider/model
selection, runtime execution, route execution, or production readiness.

Evidence-backed router recommendation language belongs to this context only as
policy-data posture. Phase 146 threads provider evidence fields into
router/provider recommendation envelopes. Evidence-backed recommendation means
deterministic evidence posture inside policy data, not runtime provider
selection, model selection, provider/model execution, route execution, or
production readiness.

Evidence-gated route-selection readiness language belongs to this context only
as source/report posture. Phase 149 can name the next proof boundary required
before local provider/model route selection or execution, without executing
that boundary or granting provider/model, generation, route-execution, or
production authority.

Future provider generation smoke probe packet language belongs to this context
only as bounded-proof paperwork. Phase 152 means a future proof can be
described without being run; it is not provider/model execution, generation,
route execution, or production readiness.

Local provider target alignment language belongs to this context only as
source/test/docs retargeting. Phase 156 changes the active future smoke probe
packet target to `qwen3.6:27b` based on accepted 30b/24k OOM evidence and prior
27b model-list visibility; it does not add 27b metadata proof, generation
proof, loadability proof, route execution, or production readiness.

Local provider generation-smoke evidence language belongs to this context only
as accepted operator-proof registration. Phase 160 records the accepted Phase
159 Retry 1 `qwen3.6:27b` `/api/generate` marker smoke proof in source data and
docs without rerunning it. This satisfies the generation-smoke evidence gate
for the exact accepted request only; it does not add `/api/chat` proof,
semantic correctness, real workload loadability, route execution, or
production readiness.

Qwen3.6 27B metadata evidence language belongs to this context only as
accepted operator-proof registration. Phase 163 records the accepted Phase 162
`qwen3.6:27b` `/api/show` metadata visibility proof in source data and docs
without rerunning it. This satisfies the prior 27b metadata blocker only; it
does not prove semantic correctness, real workload loadability, broad VRAM
sufficiency, route execution, provider/model execution, or production
readiness.

Route-selection readiness recommendation-envelope review language belongs to
this context only as non-executing report/review posture. Phase 165 confirms
that the recommendation envelope carries registered `qwen3.6:27b` evidence and
that the prior generation-smoke and metadata blockers are no longer present,
without authorizing provider/model selection, route execution, worker dispatch,
or production readiness.

Tiny vertical tracer dry artifact language belongs to this context only as
deterministic in-process report artifact posture. Phase 169 builds a dry
report from the existing `safe_direct_answer` manual-review harness spine and
allows JSON persistence only to a caller-supplied path for test/review use. It
is not provider/model execution, route execution, worker dispatch, artifact
export/package, service/API/UI productization, or production readiness.

Tiny vertical tracer dry artifact operator-proof language belongs to this
context only as accepted proof registration. Phase 172 Retry 3 proves the dry
artifact can be generated and inspected from current pushed source into a temp
directory, preserving the actual `written_path` contract and all non-execution
posture.

Tiny vertical tracer CLI adapter language belongs to this context only as a
deterministic command-surface wrapper over the Phase 169 dry report. Phase 176
adds help, fixture listing, stdout rendering, JSON formatting, and
caller-supplied JSON dry artifact writing for `safe_direct_answer` only. It is
not provider/model execution, route execution, live routing, worker dispatch,
service/API/UI productization, cleanup/delete/archive behavior, or production
readiness.

Tiny vertical tracer CLI operator-smoke language belongs to this context only
as accepted dry command-surface proof registration. Phase 179 proves the Phase
176 CLI adapter commands worked from PowerShell, including conservative
rejection cases and caller-supplied temp JSON persistence. It does not add
provider/model execution, route execution, live routing, API endpoint
execution, product-harness Codex dispatch, worker dispatch, RAG/web/scheduler/
connector behavior, service/API/UI productization, or production readiness.

Supervised provider-call tracer language belongs to this context only as a
future-boundary packet contract until an operator proof is separately accepted.
Phase 183 records the endpoint URL, model name, prompt contract, marker,
request parameters, required future boundary, and pure captured-result
classifier as source/test/docs data only. Endpoint strings are not endpoint
execution; model names are not model execution; prior smoke evidence is not
current loadability proof; and even a future marker-smoke pass would not prove
semantic correctness, real workload sufficiency, route execution, or
production readiness.

Supervised provider-call tracer target reconciliation belongs to this context
only as source/test/docs target alignment. Phase 187 retargets the Phase 183
packet from `qwen3.6:27b` to `qwen3.6:35b-a3b` because Phase 186 Retry 4
current inventory visibility showed `qwen3.6:27b` absent and
`qwen3.6:35b-a3b` present. That inventory visibility is not marker-smoke
proof, does not transfer prior 27b evidence to 35b-a3b, and does not authorize
provider/model execution, route execution, or production readiness.

Phase 191 supersedes that laptop target selection without rewriting the
historical Phase 187 record. `qwen3.6:35b-a3b` is disallowed for current
laptop target selection based on Roger's operational evidence that it locks up
the laptop. Phase 190 proves only constrained 30B marker-smoke viability for
`qwen3:30b-a3b-instruct-2507-q4_K_M`; it does not prove route execution,
semantic correctness, real workload sufficiency, long-context behavior,
sustained-load stability, or production readiness. Phase 191 retargets the
packet to that 30B candidate while preserving `qwen3.6:27b` as the safer
fallback candidate based on prior smoother operation and earlier accepted
marker-smoke and metadata evidence.

Phase 194 belongs to this context as accepted captured product marker smoke
for `qwen3:30b-a3b-instruct-2507-q4_K_M` with
`ORCH_PROVIDER_SMOKE_OK`. The accepted classifier/proof artifact backfill is
Retry 3 only; initial Phase 194, Retry 1, and Retry 2 final PASS lines are not
accepted for classifier/proof artifact status. Phase 194 proves captured
product marker smoke only and does not prove route execution, live routing,
worker dispatch, `/api/chat`, semantic correctness, real workload
sufficiency, long-context behavior, sustained-load stability, service/API/UI
productization, Hermes/OpenClaw behavior, or production readiness.

Phase 202 belongs to this context as a route-path proof packet contract only.
It defines the future evidence required to move from direct provider marker
smoke to route-mediated provider marker smoke: request intake/harness, route
recommendation/readiness, explicit route execution boundary, provider call
through route path, captured response, persisted artifact path, and
displayed/reviewable outcome. Phase 202 does not execute a route, provider,
model, runtime, HTTP endpoint, worker, WSL, Ollama, Hermes, OpenClaw, Discord,
or production behavior. Current success remains unmet for route-mediated
provider execution.

Phase 206 belongs to this context as a controlled route-mediated provider
smoke runner/CLI seam only. It prepares dry artifact shape creation,
caller-supplied captured-result review, caller-supplied artifact writing, and
explicit rejection of provider-call flags. It does not run route/provider/
model/runtime behavior and does not prove route-mediated provider execution.

Phase 208 belongs to this context as a guarded execution adapter seam only. It
adds explicit guard checks and dependency injection for a future operator
route-mediated smoke proof, but fake injected validation is not runtime proof.
The first actual route-mediated runtime proof still requires a later operator
artifact with captured execution evidence.

Phase 212 belongs to this context as a guarded live Ollama transport adapter
path only. It defines the future `/api/generate` request body, URL shape,
operator flags, artifact shape, and reserved runtime classification for a
later route-mediated provider smoke proof. Phase 212 source/test validation
uses injected transport only; it does not run provider/model/Ollama/HTTP,
route runtime, worker dispatch, platform behavior, or production behavior.
Fake injected transport validation is not runtime proof, and current success
remains unmet until actual route-mediated provider execution is proven.

Manual review/report integration may display local-first model router policy
posture as coordinator-facing evidence. Displayed router posture remains
non-executing review metadata; it is not provider/model selection, worker
dispatch, route execution, RAG/web/scheduler/connector work, or production
readiness.

Phase 124 adds the missing standalone Phase 120 module-entrypoint validation
test expected by the Phase 123 validation list. This repairs validation command
compatibility only; it does not add product behavior or erase the historical
Phase 123 failed-command caveat.

## Route Proposal Source And Admission Lifecycle

Route proposal is not execution. A route proposal source is substrate-agnostic
and non-executing; it may supply candidate route evidence, but it may not
perform the requested work or choose the downstream implementation path.

Lifecycle terms:

- Request intake record: the preserved description of the observed operator
  request, visible constraints, missing inputs, and declared boundary.
- Candidate route proposal: a non-authoritative candidate route envelope
  drafted from authorized context.
- Route-envelope validation: structural validation that the candidate envelope
  satisfies the route contract; validation is not execution.
- Risk-doctrine review: comparison against task risk routing doctrine,
  permission burden, stop conditions, and missing authority.
- Coordinator admission decision: coordinator choice to admit, reject, clarify,
  defer, directly answer, or prepare a bounded downstream handoff.
- Downstream boundary emission: explicit worker packet or external/platform
  crossing boundary created only after admission permits downstream work.

Allowed proposal source classes include:

- Operator-declared request details.
- Coordinator-drafted candidate route from visible request context.
- Worker-reported evidence used only as evidence, not acceptance.
- Connector/document-derived facts only when a boundary authorizes those
  sources.
- Model/provider-generated suggestions as non-proof unless separately
  validated.

No proposal source may smuggle in a provider, model, worker substrate, platform
executor, runtime, or implementation path as part of route admission.

## Task Risk Routing Doctrine

Task risk routing is a human-facing control doctrine for deciding what kind of
route, permission, confirmation, substrate, validation, and stop condition a
request requires before any downstream work is admitted.

| Task risk | Route class | Permissions | Confirmation burden | Allowed substrate | Validation burden | Stop conditions |
| --- | --- | --- | --- | --- | --- | --- |
| Simple answer or report-only request | `general_answer` or report-only lane | Answer only; no mutation, scheduling, retrieval, or provider execution claim | Low, unless facts are stale or consequential | Coordinator/report-only surface | Cite or state basis when needed; preserve caveats | Missing facts, high-stakes uncertainty, or requested capability outside report-only scope |
| Local-document lookup or RAG-style lookup | `local_document_lookup` | Read/search declared local document sources only | Confirm source set when ambiguous or sensitive | Document lookup surface only, once implemented | Source-grounded answer with inspectable citations or evidence paths | Missing source authority, stale-source risk, or requested mutation/execution |
| Reminder or scheduler request | `reminder_request` | Schedule only after explicit confirmation | Explicit operator confirmation required before persistence or scheduling | Scheduler/reminder surface only, once implemented | Confirm time, recurrence, target, notification semantics, and persistence | Ambiguous time, missing confirmation, or request to execute non-reminder work |
| Coding task | `coding_task` | Mutation only with explicit boundary and declared file scope | Explicit operator authorization through a bounded worker packet | Coding worker or authorized coding spine; substrate must not be smuggled through route text | Worker validation plus coordinator review; local PASS is not acceptance | Unclear scope, undeclared files, conflicting evidence, or mutation beyond packet |
| File operation | `file_operation` | Read/write/move/delete only if explicitly authorized and scoped | Explicit confirmation proportional to destructive or broad impact | Bounded file-operation surface or worker packet | Path, scope, and effect evidence; no hidden adjacent cleanup | Unsafe paths, broad scope, deletion/archive ambiguity, or missing backup/approval where required |
| Platform, substrate, runtime, provider, or model work | External or platform/substrate track unless product boundary explicitly crosses tracks | No product-side execution by default | Separate boundary with platform authority and fresh operator evidence | Platform package, provider, model, or runtime surface only under explicit crossing boundary | Fresh proof appropriate to the external track; no historical-runtime inference | Boundary lacks crossing authority, current runtime proof is missing, or product/platform authority conflicts |
| Unsupported, requires connector, or needs clarification | `unsupported` or `needs_clarification` | No capability enabled | Clarify or block before downstream work | None until admitted | Explain missing connector, authority, scope, or capability | Connector unavailable, request type unclear, required authority missing, or permissions contradictory |

Standing routing rules:

- Route validation is not execution.
- Authorization is not execution.
- Provider/model availability is not route correctness.
- Capability labels are not implementation proof.
- Mutation requires explicit authorization and declared scope.
- Scheduler/reminder lanes require explicit confirmation.
- Platform/substrate/runtime work remains separate unless a boundary explicitly
  authorizes crossing tracks.

### Coding Spine Context

Purpose: govern bounded coding/file-mutation work through proposal,
authorization, apply evidence, verification review, and explicit finalization.

Owned language: filesystem mutation, report-only, patch proposal, operator
apply authorization, apply result, causal change, finalization, completion
gate.

Authority docs/files:

- `docs/CURRENT_SUCCESS_CRITERION.md`
- `docs/PHASE_95.md` through `docs/PHASE_101.md`
- `docs/PHASE_INDEX.md`
- coding-spine source/test files listed in phase docs
- `docs/TRACKS_AND_OPEN_THREADS.md`

Non-authority / do-not-confuse warnings:

- Component PASS markers are not broad semantic correctness proof.
- Patch proposal is not patch application.
- Apply evidence is not full task success.
- Finalization does not prove production readiness.
- Autonomous writeback remains unproven.

Current proof posture: Phase 97 through Phase 101 components are locally
source/test/docs-proven and the Phase 101 product ZIP is accepted as the last
uploaded artifact in inspected repo docs. Integrated production workflow
readiness is not proven.

### Evidence / Artifact Proof Context

Purpose: preserve the distinction between source state, local proof, export
proof, upload proof, non-proof, and caveated historical records.

Owned language: source state, export proof, upload proof, non-proof, caveat,
artifact proof, SHA-256, accepted artifact, fresh operator output.

Authority docs/files:

- `docs/SOURCE_MANIFEST.md`
- `docs/ACTION_LOG.md`
- `docs/PHASE_INDEX.md`
- phase docs
- external operator export/upload logs when supplied
- `docs/TRACKS_AND_OPEN_THREADS.md`

Non-authority / do-not-confuse warnings:

- In-repo text cannot prove the hash of a later export.
- Export PASS is not upload PASS.
- Local source/test/docs proof is not artifact proof.
- Historical artifact records are not automatically current source truth.
- Memory or handoff text is not proof without reconciliation.

Current proof posture: inspected repo docs preserve Phase 101 as the accepted
uploaded artifact and state Phase 102 was not exported/uploaded. Phase 103 is
locally source/test/docs-proven only and not exported/uploaded.

### Platform / Substrate Context

Purpose: keep platform/runtime/installer/OpenClaw/Ollama/Discord/bridge/adapter
claims separate from product documentation and source-state claims.

Owned language: platform, substrate, provider/model, OpenClaw, Ollama, WSL,
Discord, bridge, adapter, installer, external memory capsule.

Authority docs/files:

- external platform/OpenClaw memory capsule
- platform package docs, when explicitly in scope
- product-side platform references in `docs/SOURCE_MANIFEST.md` and
  `docs/TRACKS_AND_OPEN_THREADS.md`

Non-authority / do-not-confuse warnings:

- The platform installer is not the product repo.
- Historical runtime proof is not current runtime truth.
- Product docs may reference platform separation without making live platform
  claims.
- Provider/model availability is not routing proof or mutation proof.

Current proof posture: Phase 104 performs no platform inspection beyond product
docs and makes no current runtime, installer, provider/model, OpenClaw,
Discord, bridge, adapter, WSL, or platform behavior claim.

## Ubiquitous Language

| Term | Definition |
| --- | --- |
| Orchestrator | The governing layer for AI-assisted work, intended to preserve boundedness, inspectability, explicit state, reviewability, diagnosable failure, and operator judgment. |
| coordinator | The governance role that ranks, scopes, packages, reviews, ratifies, and preserves context; not the worker executor. |
| Roger/operator | The owner/operator authority who approves direction, relays worker packets, and accepts or rejects results. |
| Relay | The human-mediated command or prompt transfer layer; relay construction is not execution proof. |
| worker | A bounded implementation role that inspects and mutates only within an authorized packet, then reports evidence. |
| NBM | Next best move: the coordinator-ranked immediate intervention, justified against the present success bar and constitutional direction. |
| boundary | The explicit in-scope/out-of-scope membrane for a phase, fix, or document mutation. |
| route membrane | The governance boundary that decides whether a structured route proposal is admissible before downstream capability use. |
| route envelope | A structured object containing request type, confidence, capabilities, permissions, caveats, and recommended next action for route validation. |
| route admission | The validation outcome for a route envelope: accepted, needs clarification, or rejected. |
| request type | The domain-general category assigned to a proposed request, such as general answer, local document lookup, reminder request, coding task, file operation, planning request, research request, creative generation, unsupported, or needs clarification. |
| capability | A named ability needed by a route or task; a capability label is not proof that the capability exists or executed. |
| substrate | The underlying execution or support surface, such as worker, provider, model, platform, or connector; substrate naming must not bypass route or operator gates. |
| provider/model | A concrete AI or execution provider/model surface; provider/model existence is not proof of route execution, semantic correctness, or mutation authority. |
| source state | The contents of the product repo at a point in time after local mutation; source state is not the same as an exported or uploaded artifact. |
| export proof | Fresh evidence that a product artifact was created from a source state and has observed path, hash, size, entries, and contents. |
| upload proof | Fresh evidence that an exported artifact was uploaded and verified in the receiving context. |
| non-proof | A claim, marker, note, or memory that does not establish the behavior or artifact identity it might appear to imply. |
| caveat | A preserved limitation that bounds what a proof or source claim actually establishes. |
| open thread | A durable unresolved question, obligation, or risk that must remain visible until a future boundary explicitly resolves it with evidence. |

## Active-Vs-Historical Document Separation

Active governing documents define current direction, current success bar,
current process semantics, active track state, and language architecture.
Historical phase docs and logs preserve what was done, what was proven, and
what was not proven at the time.

Rules:

1. Do not rewrite historical phase records to make later state look cleaner.
2. Do not treat an older phase doc's local proof as current artifact proof.
3. Do not treat the existence of this context map as redundancy cleanup.
4. Do not collapse active open threads into historical caveats.
5. When sources conflict, current repo evidence and fresh artifact/operator
   proof outrank conversational memory and handoff claims.

## Artifact-Proof Hygiene Rules

1. Source-state claims, export proof, and upload proof must remain separate.
2. A ZIP cannot self-prove its own final post-edit hash from inside the same
   source mutation that changes the ZIP contents.
3. Artifact hashes require fresh external observation of the produced artifact.
4. Export PASS must not be reported as upload PASS.
5. Upload acceptance must state the observed artifact identity and verification
   basis.
6. Local docs/control proof must not be described as source/test proof unless
   source/tests were actually changed and validated.
7. Worker-reported PASS markers remain worker proof until coordinator
   ratification or artifact acceptance occurs.

## Phase 102 Artifact-Proof Conflict

This conflict is explicitly preserved as an open reconciliation thread:

- A supplied handoff may claim Phase 102 upload hash
  `F5A53C67100F95744E20E25ED5A48A244E4D08C021E848463AAF3BE2A7D23CA6`.
- Inspected repo docs preserve Phase 101 as the accepted uploaded artifact and
  state Phase 102 was not exported/uploaded.
- Do not resolve this conflict without fresh artifact proof.

Until fresh proof is supplied, product docs should preserve the inspected repo
position: Phase 101 is the accepted uploaded artifact, and Phase 102 is local
docs/control source state only.

## Phase 103 Routing Boundary

Phase 103 validates structured route envelopes only.

It does not implement:

- live route proposal
- model routing
- RAG/local-document lookup
- reminders
- scheduling
- web lookup
- autonomous writeback
- production task execution

The Phase 103 contract may name request types, required route-envelope fields,
permissions, capabilities, caveats, and no-activity flags. It does not execute
those capabilities or prove that any future route is productized.

## Phase Label Taxonomy Context

Marker: PHASE_198_PHASE_LABEL_TAXONOMY_AND_CHECKPOINT_GAP_CLARIFICATION_DOCS

The Orchestrator product track distinguishes accepted phase/checkpoint labels from dedicated phase documentation files.

PHASE_XXX labels are named acceptance boundaries. Dedicated docs/PHASE_XXX.md files are durable source documentation artifacts and are not guaranteed for every accepted boundary.

Future sessions should inspect PHASE_INDEX.md, ACTION_LOG.md, source manifests, commit history, operator proof, capsule metadata, and current handoff before treating a missing phase doc as a missing phase.

## Phase 217 Live Transport Failure Artifact Context

Phase 217 belongs to the provider/model substrate context as source/test/docs
failure-shape handling for the Phase 212 live route-mediated provider smoke
transport path.

It records that transport exceptions after live guards pass should produce a
structured JSON-safe artifact classified as
`live_ollama_transport_exception_not_runtime_proof`. That artifact may record
route-boundary entry and attempted `/api/generate` transport shape, but it is
not provider/model/Ollama/HTTP execution proof without response evidence.

Before the later Phase 228 registration, Phase 216 remained failed and current
success for this path remained unmet until a future live artifact classified as
`route_mediated_provider_smoke_runtime_marker_pass`.

## Phase 228 Route Mediated Provider Smoke Runtime Proof Context

Phase 228 belongs to the provider/model substrate context as documentation
registration of the accepted Phase 216 Retry 3 operator proof:

`PHASE_216_RETRY3_ROUTE_MEDIATED_PROVIDER_SMOKE_LIVE_RUNTIME_OPERATOR_PROOF=PASS`

It records exactly one live local Ollama `/api/generate` call through the
route-mediated live transport CLI for
`qwen3:30b-a3b-instruct-2507-q4_K_M`, marker
`ORCH_ROUTE_PROVIDER_SMOKE_OK`, and the Phase 212 artifact classification
`route_mediated_provider_smoke_runtime_marker_pass`.

The route-mediated provider marker-smoke runtime gap is closed only for that
narrow target/prompt/options/artifact boundary. It is not semantic correctness,
real workload sufficiency, long-context, sustained-load, production readiness,
Hermes/OpenClaw behavior, or `qwen3.6:35b-a3b` authorization proof.

## Phase 316 Backbone Scaffold Context

Phase 316 belongs to the source/test/docs control-loop abstraction context. It
adds a domain-neutral Backbone scaffold beside the existing code-patching
vertical loop.

The code-patching loop remains its own bounded context. Phase 316 only provides
neutral stage vocabulary, stage-record contracts, adapter descriptors, linked
evidence-chain fields, non-proof fields, and deterministic incomplete reason
codes for later mapping work.

Phase 316 does not declare Backbone V0, execute adapters, migrate patch-loop
behavior, prove semantic correctness, prove production readiness, or prove
provider/model/runtime/platform behavior.

## Phase 317 Backbone Code-Patching Mapping Context

Phase 317 belongs to the source/test/docs control-loop abstraction context. It
maps the existing code-patching bounded context to the Phase 316 neutral
Backbone scaffold vocabulary by source/doc/test evidence strings only.

The mapping seam is descriptive. It does not execute adapters, migrate
patch-loop behavior, declare Backbone V0, prove semantic correctness, prove
production readiness, or prove provider/model/runtime/platform behavior.
