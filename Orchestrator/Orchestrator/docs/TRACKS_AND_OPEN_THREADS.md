# Tracks And Open Threads

## Purpose And Authority

This file is the durable cross-track coordination map for the Orchestrator
product repo. It preserves accepted track state, proof posture, active open
threads, likely next boundaries, source-of-truth documents, and drift warnings
across coordinator sessions.

This ledger does not replace phase documents, `ACTION_LOG.md`,
`SOURCE_MANIFEST.md`, `CURRENT_SUCCESS_CRITERION.md`, `PROJECT_VISION.md`,
`docs/CONTEXT_MAP.md`, or the external platform/OpenClaw memory capsule. Those
sources retain authority for their own detailed claims. This file connects
their active implications without turning conversational memory into proof.

Every future coordinator session must inspect this ledger and apply
`docs/OPEN_THREAD_TRIAGE_PROTOCOL.md` before recommending a next best move
(NBM) or changing tracks. Accepted facts, coordinator inference, worker report,
and artifact proof must remain visibly distinct.

## Open-Thread Triage Statuses

Every visible open thread must be triaged before NBM ranking. Use these status
labels:

- `ACTIVE_NBM_CANDIDATE`: A live candidate for the next bounded move.
- `BLOCKED_AWAITING_PROOF`: Valid thread, but cannot advance until fresh
  proof, operator output, or artifact evidence exists.
- `DEFERRED_VALID`: Valid but intentionally not next.
- `EXTERNAL_TRACK`: Belongs primarily to platform, OpenClaw, Hermes, model,
  RAG, installer, or another non-product track unless an integration boundary
  authorizes it.
- `HISTORICAL_EVIDENCE`: Preserved for audit/history, not active work.
- `RETIRED_OR_RESOLVED`: No longer active. Must not influence NBM ranking
  unless reopened with reason and proof.
- `NEEDS_TRIAGE`: Thread exists but its status is unclear; coordinator must
  classify it before ranking it.

The coordinator should identify which thread, if any, is the highest-leverage
`ACTIVE_NBM_CANDIDATE`. Blocked, deferred, external, historical, retired, and
unclear threads must preserve their caveats without dominating the active NBM
list.

## Current Accepted Product Artifact

Coordinator export/upload verification accepted the Phase 101 product ZIP:

- Accepted uploaded ZIP SHA-256:
  `7305653F4D7BFD7C537E52C5B45DCA63BC23A7DAFD4E4F2491AB5092FA03B769`
- `PHASE101_VERIFIED_PATCH_APPLY_TASK_COMPLETION_FINALIZATION_GATE_LOCAL_SOURCE_TEST_PROVEN=PASS`
- `PHASE101_PRODUCT_ZIP_EXPORT_VERIFY_RESULT=PASS`
- `PHASE101_PRODUCT_ZIP_UPLOAD_VERIFY_RESULT=PASS`

These are accepted external artifact facts supplied to Phase 102. The Phase
101 source documents correctly describe the source state before that later
export/upload proof. If this Phase 102 source state is later exported, the
Phase 101 artifact hash remains external proof of the earlier artifact until
the next export/upload verification reconciles the new source state.

Open Phase 102 artifact-proof conflict: a supplied handoff may claim Phase 102
upload hash
`F5A53C67100F95744E20E25ED5A48A244E4D08C021E848463AAF3BE2A7D23CA6`.
Inspected repo docs preserve Phase 101 as the accepted uploaded artifact and
state Phase 102 was not exported/uploaded. Do not resolve this conflict without
fresh artifact proof.

## Track Table

| Track ID | Purpose | Current accepted state | Proof status | Source-of-truth docs | Open threads | Next likely boundary | Drift warnings |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `PRODUCT_GOVERNANCE_PROTOCOL` | Preserve ranking, approval, role, evidence, handoff, review, closure, and re-entry discipline. | Governance and interaction protocols are documented; Phase 102 adds the durable cross-track map. | Docs/control proven locally by Phase 102; governance quality still requires operational use. | `ORCHESTRATOR_METHOD.md`; `ORCHESTRATOR_INTERACTION_MODEL.md`; `STARTUP_BRIEF.md`; this ledger | Read ledger before NBMs; separate accepted facts, inference, worker report, and artifact proof; preserve role boundaries; re-rank instead of following phase momentum. | Make ledger use explicit in every future coordinator re-entry and update it whenever a track changes. | Governance must not become ceremonial or substitute for useful product proof. |
| `PRODUCT_CURRENT_SUCCESS_CODING_TASK` | Define the present-tense product success bar for bounded coding work. | The current criterion remains coding-task focused and has bounded deterministic-provider proof with caveats. | Current criterion and prior phase records support a narrow accepted bar; no general-product proof. | `CURRENT_SUCCESS_CRITERION.md`; `PROJECT_VISION.md`; Phase 80-82 records; this ledger | Coding-specific criterion is narrower than product vision; do not treat coding as the whole product. | Re-rank against the coding criterion while preserving broader tracks; broaden the criterion only through an explicit future decision. | A proven coding path is not proof of general assistant or orchestration capability. |
| `PRODUCT_PATCH_WORKFLOW_CODING_SPINE` | Govern proposal, authorization, bounded apply, evidence review, and explicit task finalization. | Phase 97-101 components are individually sealed and the Phase 101 artifact is export/upload accepted. | Local source/test markers and external artifact proof exist for component phases; integrated production workflow is unproven. | `PHASE_97.md` through `PHASE_101.md`; `PHASE_INDEX.md`; this ledger | Full end-to-end integration unproven; no broad semantic correctness; no live model-generated proposal; no autonomous writeback; no production task execution proof for the full spine. | Explicit integrated patch-spine proof, if re-ranked above other tracks and separately authorized. | Component PASS markers must not be collapsed into semantic, production, or autonomous-writeback proof. |
| `PRODUCT_DOMAIN_GENERAL_INTAKE_ROUTING` | Make coding one bounded route within a general request intake and capability-routing layer. | Initial route taxonomy and route-envelope validation contract are source/test/docs-proven by Phase 103; Phase 106 adds docs-only task risk routing doctrine; Phase 107 adds docs-only route proposal source and admission lifecycle doctrine; Phase 108 adds docs-only capability registry maturity doctrine; Phase 109 adds a source/test capability registry contract; Phase 110 integrates the registry into route-envelope validation at source/test contract level; Phase 111 adds a non-executing route proposal source/admission pipeline contract; Phase 112 adds docs-only prompt-to-envelope inference boundary and fixture doctrine; Phase 113 adds a deterministic fixture-based prompt-to-envelope source/test contract; Phase 114 adds a deterministic end-to-end non-executing intake-to-admission pipeline contract; Phase 115 adds a deterministic non-executing admission-to-boundary-packet source/test contract; Phase 116 adds a deterministic end-to-end fixture/intake/admission/boundary-packet pipeline source/test contract; Phase 117 adds a deterministic coordinator-facing review report source/test contract; Phase 118 adds a deterministic manual coordinator review runner source/test contract; Phase 119 adds a deterministic manual review CLI-compatible adapter source/test contract; Phase 120 proves manual review CLI module entrypoint smoke after the fix; Phase 121 proves the manual review CLI runbook/golden smoke contract at docs/test level; Phase 122 adds a deterministic local-first model/router policy source/test/docs contract; Phase 123 integrates router policy posture into manual review reports at source/test/docs level; Phase 124 repairs the missing standalone Phase 120 validation module expected by Phase 123. | Local contract plus docs/control proof only; route proposal source implementation is addressed only at deterministic structured-intake contract level; prompt-to-envelope fixture source contract is addressed only at fixture contract level; end-to-end fixture/intake/route/admission pipeline is addressed only at deterministic source/test contract level; boundary packet drafting is addressed only at source/test contract level; fixture-to-boundary-packet pipeline is addressed only at deterministic non-executing source/test contract level; coordinator review report generation is addressed only at deterministic source/test contract level; manual review runner is addressed only at deterministic source/test contract level; manual review CLI-compatible adapter and module entrypoint are addressed only at deterministic source/test/smoke contract level; manual review CLI runbook/golden smoke is addressed only at docs/test level; local-first model/router policy is addressed only at deterministic non-executing source/test/docs contract level; router policy manual review integration is addressed only as non-executing report metadata/rendering; Phase 123 validation-command mismatch is repaired at proof-hygiene test level by Phase 124; Phase 133 metadata visibility is registered as evidence only, not execution authority; no service/API/UI productization, worker dispatch, concrete substrate selection, live raw prompt inference, natural-language intent inference, live router, RAG, reminders, web lookup implementation, provider/model routing or execution, route execution, or production readiness proof. | `PROJECT_VISION.md`; `ORCHESTRATOR_INTERACTION_MODEL.md`; `docs/CONTEXT_MAP.md`; `docs/CAPABILITY_REGISTRY.md`; `docs/PROMPT_TO_ENVELOPE_INFERENCE.md`; `docs/LOCAL_FIRST_MODEL_ROUTER_POLICY.md`; `docs/PHASE_103.md`; `docs/PHASE_107.md`; `docs/PHASE_108.md`; `docs/PHASE_109.md`; `docs/PHASE_110.md`; `docs/PHASE_111.md`; `docs/PHASE_112.md`; `docs/PHASE_113.md`; `docs/PHASE_114.md`; `docs/PHASE_115.md`; `docs/PHASE_116.md`; `docs/PHASE_117.md`; `docs/PHASE_118.md`; `docs/PHASE_119.md`; `docs/PHASE_120.md`; `docs/PHASE_121.md`; `docs/PHASE_122.md`; `docs/PHASE_123.md`; `docs/PHASE_124.md`; `docs/PHASE_133.md`; `docs/MANUAL_REVIEW_CLI_RUNBOOK.md`; `orchestrator/request_routing.py`; `orchestrator/capability_registry.py`; `orchestrator/route_proposal.py`; `orchestrator/prompt_to_envelope.py`; `orchestrator/intake_admission_pipeline.py`; `orchestrator/boundary_packet.py`; `orchestrator/fixture_packet_pipeline.py`; `orchestrator/coordinator_review_report.py`; `orchestrator/manual_review_runner.py`; `orchestrator/manual_review_cli.py`; `orchestrator/model_router_policy.py`; this ledger | Productized coordinator CLI/UI, live worker dispatch, live prompt-to-envelope inference/productized classifier, live model router, RAG, reminders, web lookup implementation, productized answer/lookup/scheduler lanes, provider/model routing, route execution, and production readiness remain open. | Implement productized coordinator CLI/UI, live worker dispatch, live prompt-to-envelope inference/productized classifier, live router, productized answer/lookup/scheduler lanes, or live provider/model routing under separate boundaries before any live routing or execution. | Model output is not proof; route validation is not execution; capability labels are not implementation proof or execution authority; route proposal admission is not execution; router policy and model metadata visibility are not live routing, provider/model execution, worker dispatch, or route execution; Phase 124 proof-hygiene repair is not product behavior. |
| `PRODUCT_LOCAL_FIRST_MODEL_ROUTER_PROVIDER` | Route work local-first with explicit provider contracts, confidence, fallback, and escalation. | Phase 122-129 add deterministic non-executing source/test/docs contracts for router/provider paperwork; Phase 130 operator proof registers the CLI paperwork path with an exit-code caveat; Phase 131 operator proof registers read-only local Ollama `/api/tags` provider-surface visibility with nine model names; Phase 132 registers those accepted proofs in source docs/ledgers; Phase 133 operator proof registers read-only local Ollama `/api/show` metadata visibility for `qwen3-30b-24k:latest`; Phase 134 registers Phase 133 in source docs/ledgers; Phase 135-140 register git checkpoint publication/alignment only; Phase 143 adds a deterministic provider evidence registry and surfaces Phase 131/133 evidence in manual review reports; Phase 146 adds provider evidence fields to router/provider recommendation envelope data; Phase 149 adds deterministic evidence-gated route-selection readiness; Phase 152 adds a future generation smoke probe packet contract; Phase 156 retargets that active packet to `qwen3.6:27b`; Phase 160 registers accepted Phase 159 Retry 1 `qwen3.6:27b` `/api/generate` marker smoke evidence; Phase 163 registers accepted Phase 162 `qwen3.6:27b` `/api/show` metadata visibility evidence; Phase 165 reviews the readiness/recommendation-envelope posture; Phase 169 adds a tiny vertical tracer dry report artifact contract over the safe fixture harness spine; Phase 172 Retry 3 accepts operator proof that the dry artifacts can be generated and inspected from current pushed source into a temp directory. | Deterministic source/test/docs contract proof plus accepted operator-output registration only; Phase 131 proves read-only `/api/tags` visibility at that moment and Phase 133 proves read-only `/api/show` metadata visibility for one model at that moment; Phase 143/146/149/152 make earlier visibility structured report, recommendation-envelope, readiness posture, and future packet evidence only; Phase 156 is source/test/docs retargeting only; Phase 160 registers generation-smoke evidence for the exact accepted request only; Phase 163 registers 27b `/api/show` metadata visibility only; Phase 165 proves the source/report posture only; Phase 169 proves a dry report artifact contract only; no `/api/chat` proof, provider/model execution, route execution, worker dispatch, artifact export/package, or production readiness is proven. | `docs/LOCAL_FIRST_MODEL_ROUTER_POLICY.md`; `docs/LOCAL_FIRST_PROVIDER_CATALOG.md`; `docs/PROVIDER_EVIDENCE_REGISTRY.md`; `docs/PROVIDER_PROBE_BOUNDARY_PACKET.md`; `docs/PROVIDER_GENERATION_SMOKE_PROBE_PACKET.md`; `docs/MANUAL_REVIEW_CLI_RUNBOOK.md`; `docs/PHASE_122.md`; `docs/PHASE_123.md`; `docs/PHASE_124.md`; `docs/PHASE_125.md`; `docs/PHASE_126.md`; `docs/PHASE_127.md`; `docs/PHASE_128.md`; `docs/PHASE_129.md`; `docs/PHASE_130.md`; `docs/PHASE_131.md`; `docs/PHASE_132.md`; `docs/PHASE_133.md`; `docs/PHASE_134.md`; `docs/PHASE_135.md`; `docs/PHASE_136.md`; `docs/PHASE_137.md`; `docs/PHASE_138.md`; `docs/PHASE_139.md`; `docs/PHASE_140.md`; `docs/PHASE_143.md`; `docs/PHASE_146.md`; `docs/PHASE_149.md`; `docs/PHASE_152.md`; `docs/PHASE_156.md`; `docs/PHASE_160.md`; `docs/PHASE_163.md`; `docs/PHASE_165.md`; `docs/PHASE_169.md`; `orchestrator/model_router_policy.py`; `orchestrator/model_provider_catalog.py`; `orchestrator/provider_probe_boundary_packet.py`; `orchestrator/provider_evidence_registry.py`; `orchestrator/route_selection_readiness.py`; `orchestrator/provider_generation_smoke_probe_packet.py`; `orchestrator/coordinator_review_report.py`; `orchestrator/manual_review_cli.py`; `orchestrator/tiny_vertical_tracer.py`; provider docs/code when inspected; this ledger | Provider catalog, router/provider envelope, provider evidence registry, evidence-backed recommendation fields, route-selection readiness, future generation smoke probe packet, probe packet draft, manual review status, CLI probe-packet adapter, and tiny vertical tracer dry artifact remain policy/report metadata; Phase 155 Retry 3 OOM was a 30b/24k failure, not a 27b failure; no model correctness, model loadability, broad VRAM sufficiency, provider/model selection for execution, route execution, provider/runtime execution, mutation-capable provider path, or production artifact path exists. | Next recommended boundary is `PHASE_173_TINY_VERTICAL_TRACER_DRY_ARTIFACT_OPERATOR_PROOF_SOURCE_DOCS`; future live execution still requires explicit coordinator authorization and fresh operator proof. | Provider catalog envelope, provider evidence text, evidence-backed recommendation fields, route-selection readiness, future generation smoke probe packet, retargeting to 27b, probe packet data, manual review status, CLI adapter output, tiny vertical tracer dry report, `/api/tags` visibility, `/api/show` metadata visibility for 30b/24k, 27b `/api/show` metadata visibility, and checkpoint records are not model generation, model correctness, provider/model/runtime/platform execution, route execution, mutation authority, artifact export/package, or production readiness. |
| `PRODUCT_RAG_LOCAL_DOCUMENT_LOOKUP` | Ground answers and work in indexed local documents with inspectable sources. | Intended product track only; no mature RAG subsystem is accepted. | Unproven/unimplemented at mature product level. | `PROJECT_VISION.md`; future RAG phase docs; this ledger | No mature ingestion/indexing, retrieval interface, citation/source artifact contract, grounding verifier, or stale-source policy. | Define document authority, ingestion boundaries, retrieval contract, and citation artifact semantics. | Local files existing on disk are not retrieval, grounding, or freshness proof. |
| `PRODUCT_REMINDER_SCHEDULER_AUTOMATION` | Support persisted reminders and scheduled operator-facing automation. | Intended product track only; no accepted scheduler/reminder service exists. | Unproven/unimplemented. | Future reminder/scheduler phase docs; this ledger | No time parser, persisted reminder model, service loop, notification backend, update/cancel semantics, or restart-survival proof. | Define reminder record, time semantics, lifecycle, and persistence before adding a scheduler loop. | A parsed date or one-shot timer is not a durable reminder system. |
| `PRODUCT_GENERAL_ANSWER_LIGHTWEIGHT_REPORT` | Provide a lightweight report-only lane for simple questions without forcing coding workflow overhead. | Phase 235 adds a deterministic structured low-risk `general_answer` report-only artifact contract. | Local source/test/docs contract proof only; no semantic answer quality, model-backed generation, live router, persistence policy, service/API/UI, or production readiness proof. | `docs/PHASE_235.md`; `orchestrator/lightweight_answer_report.py`; `tests/test_phase_235_general_answer_lightweight_report_only_contract.py`; `PROJECT_VISION.md`; this ledger | Optional persistence policy, local-first answer/fallback policy, service/API/UI surface, and any live answer generation remain open. | Define persistence/default surfacing or local-first answer/fallback policy under a separate boundary. | Report-only must not silently gain execution, persistence, model generation, retrieval, scheduling, connector, worker-dispatch, or production semantics. |
| `PLATFORM_INSTALLER_OPENCLAW` | Maintain the separate installer/runtime/OpenClaw infrastructure track and its evidence. | Platform authority remains in the sibling package and memory capsule; no Phase 102 platform mutation or live claim occurred. | External documentary reference only for Phase 102; current runtime behavior requires fresh operator output. | External `ORCHESTRATOR_OPENCLAW_MEMORY_CAPSULE.md`; platform package docs; this ledger for product-side separation | Keep platform separate unless explicitly integrated; decide standalone installer versus product infrastructure dependency; later document standalone run path. | Under an explicit platform boundary, inspect current authority docs and fresh operator output before deciding integration posture. | Platform installer is not the product repo; historical runtime proof is not current runtime truth. |
| `PRODUCT_EXPORT_ARTIFACT_PROOF` | Produce and verify product artifacts without confusing source state, export, and upload acceptance. | Phase 101 export and upload are externally accepted with the SHA-256 recorded above. | External artifact proof accepted; Phase 102 itself is not exported or uploaded. | `SOURCE_MANIFEST.md`; `ACTION_LOG.md`; phase docs; external operator logs; this ledger | Automate artifact verification eventually; export/upload proof often remains external until next reconciliation. | Add bounded artifact verification automation only after explicit ranking and authorization. | Export PASS is not upload PASS; in-repo text cannot self-prove the hash of a later export. |
| `PRODUCT_PERSISTENCE_ATOMICITY_LOCKING` | Make persisted task/artifact state crash-consistent and concurrency-safe. | Separate persistence writes remain; Phase 101 has best-effort rollback for one finalization path. | Narrow rollback behavior is source/test proven; no general transaction proof. | `PHASE_101.md`; persistence implementation/docs when inspected; this ledger | No full atomicity/locking; task and artifact writes can be separate; need crash consistency, concurrency policy, and migration/versioning strategy. | Define persistence invariants and locking/transaction policy before broadening concurrent or service execution. | One-path rollback is not a general transaction system. |
| `PRODUCT_TESTING_CI_HERMETICITY` | Establish repeatable required tests, isolation, and CI policy by task type. | Targeted phase regression tests exist and have recorded PASS results. | Targeted local proof only; no mature CI or global hermeticity proof. | Phase test records; test modules; future CI policy docs; this ledger | No mature CI, global hermetic isolation guarantee, test matrix, or task-type test policy. | Define required test classes and isolation rules, then add CI under an explicit tooling boundary. | A targeted passing suite is not repository-wide or environment-independent proof. |
| `PRODUCT_SERVICE_API_UI_AUTH` | Expose one stable governing layer through service, API, UI, auth, and deployment surfaces. | No accepted stable service/API, auth layer, dashboard, multi-user model, or deployment story. | Unproven/unimplemented. | `PROJECT_VISION.md`; future service/API/UI phase docs; this ledger | Stable API, auth, dashboard, multi-user semantics, and deployment are all open. | Define a service boundary that reuses existing orchestration semantics before adding UI or auth. | New interfaces must not create alternate control systems or bypass operator gates. |
| `PRODUCT_CODEBASE_STRUCTURE_TECH_DEBT` | Keep product modules legible and separated as capabilities expand. | The product has extracted modules, but `main.py` remains a monolith and the BOM issue remains open. | Existing structure is directly inspectable; no debt-resolution proof. | `SOURCE_MANIFEST.md`; source tree; future refactor phase docs; this ledger | Split `main.py`; address BOM; separate router, providers, RAG, reminders, coding spine, and platform integration; keep governance operational. | Perform a bounded structure assessment before any refactor, then isolate one ownership boundary at a time. | Broad cleanup can obscure behavior changes and exceed phase boundaries. |
| `PRODUCT_DOCS_LANGUAGE_ARCHITECTURE_AND_DDD_CONTEXT_MAP` | Assess whether Orchestrator docs should be reorganized around DDD-style language architecture. | Phase 104 creates `docs/CONTEXT_MAP.md` as the durable language/context architecture map; cleanup and reorganization remain open. | Local docs/control proof only; no cleanup, historical rewrite, export, upload, or runtime proof. | This ledger; `docs/CONTEXT_MAP.md`; `docs/PHASE_104.md` | Preserve all existing open-thread caveats; do not convert context-map existence into cleanup completion; preserve Phase 102 artifact-proof conflict pending fresh proof. | Future documentation architecture cleanup or context-specific docs only under a separate boundary. | Phase 104 clarifies language authority; it must not rewrite history, blur source authority, or close redundancy work by existence alone. |
| `PRODUCT_WORKER_RELAY_OPERATOR_ROUTING` | Preserve distinct owner/operator, coordinator, worker, and relay responsibilities. | Roger is owner/operator; coordinator ranks/scopes/reviews/ratifies; worker inspects/mutates within boundaries; relay constructs command batches only; Phase 106 adds the coding worker boundary contract. | Role model documented; compliance depends on each handoff. | `ORCHESTRATOR_METHOD.md`; `ORCHESTRATOR_INTERACTION_MODEL.md`; `STARTUP_BRIEF.md`; this ledger | Future sessions must not confuse relay tasks with worker assignments or treat worker PASS as coordinator acceptance. | Include actor and delegation state in `RESPONSE_METADATA` and every bounded handoff. | Authorization is not execution; relay construction is not worker execution; worker report is not artifact acceptance. |

## Required Open Thread Register

### Product Governance / Protocol

- Triage status: `ACTIVE_NBM_CANDIDATE` when re-entry discipline itself is the
  ranked problem; otherwise `DEFERRED_VALID`.
- Read this central ledger and `docs/OPEN_THREAD_TRIAGE_PROTOCOL.md` before
  future NBMs.
- Preserve accepted facts versus inference versus worker report versus artifact
  proof.
- Preserve owner/coordinator/relay/worker role boundaries.
- Prevent phase momentum from replacing re-ranking.

### Current Success / Coding Task

- The current success criterion is coding-specific.
- Product vision remains broader than coding.
- Future sessions must not treat coding as the whole product.
- Triage status: `DEFERRED_VALID` unless the current-success bar is the ranked
  blockage for the next boundary.

### Patch Workflow / Coding Spine

- Phase 97-101 components are individually sealed.
- The full end-to-end integrated patch workflow is not yet proven.
- There is no broad semantic correctness proof.
- There is no live model-generated patch proposal proof.
- There is no autonomous writeback.
- There is no production task execution proof for the full patch spine.
- Triage status: `ACTIVE_NBM_CANDIDATE` only if integrated patch-spine proof is
  ranked highest; otherwise `DEFERRED_VALID`.

### Domain-General Intake / Routing

- Initial route taxonomy and route-envelope validation contract are
  source/test/docs-proven by Phase 103.
- Phase 106 adds docs-only task risk routing doctrine in `docs/CONTEXT_MAP.md`.
- Phase 107 adds docs-only route proposal source and admission lifecycle
  doctrine; route proposal source doctrine is addressed at docs/control level
  only.
- Phase 108 adds docs-only capability registry maturity doctrine; capability
  registry maturity is addressed at docs/control level only.
- Phase 109 adds a source/test capability registry contract; source/test
  capability registry implementation is addressed only at contract level.
- Phase 110 integrates the capability registry into route-envelope validation
  at source/test contract level; route-validator integration with registry is
  addressed only at non-executing validation-contract level.
- Phase 111 adds a non-executing route proposal source/admission pipeline
  contract; route proposal source implementation is addressed only at
  deterministic structured-intake contract level.
- Phase 112 adds docs-only prompt-to-envelope inference boundary and fixture
  doctrine; prompt-to-envelope inference is addressed at docs/control doctrine
  level only.
- Phase 113 adds a deterministic fixture-based prompt-to-envelope source/test
  contract; prompt-to-envelope fixture source contract is addressed only at
  fixture contract level.
- Phase 114 adds a deterministic end-to-end non-executing intake-to-admission
  pipeline contract; end-to-end fixture/intake/route/admission pipeline is
  addressed only at deterministic source/test contract level.
- Phase 115 adds a deterministic non-executing admission-to-boundary-packet
  source/test contract; boundary packet drafting is addressed only at
  source/test contract level.
- Phase 116 adds a deterministic end-to-end fixture/intake/admission/
  boundary-packet pipeline source/test contract; fixture-to-boundary-packet
  pipeline is addressed only at deterministic non-executing source/test
  contract level.
- Phase 117 adds a deterministic coordinator-facing review report source/test
  contract; coordinator review report generation is addressed only at
  deterministic source/test contract level.
- Phase 118 adds a deterministic manual coordinator review runner source/test
  contract; manual review runner is addressed only at deterministic
  source/test contract level.
- Phase 119 adds a deterministic manual review CLI-compatible adapter
  source/test contract; manual review CLI-compatible adapter is addressed only
  at deterministic source/test contract level.
- Phase 120 fixes and smoke-proves the manual review CLI module entrypoint;
  module invocation is addressed only at deterministic source/test/smoke
  contract level.
- Phase 121 adds the manual review CLI runbook/golden smoke contract; the
  runbook/golden smoke contract is addressed only at docs/test level.
- Phase 122 adds a deterministic local-first model/router policy contract;
  model/router policy is addressed only at non-executing source/test/docs
  contract level.
- Phase 123 integrates router policy posture into manual review reports;
  integration is addressed only as non-executing report metadata/rendering.
- Phase 124 repairs the missing standalone Phase 120 module-entrypoint
  validation module expected by the Phase 123 validation list; this is
  proof-hygiene test compatibility only.
- Phase 125 adds a deterministic local-first provider catalog and escalation
  matrix; provider catalog posture is addressed only at non-executing
  source/test/docs contract level.
- Phase 126 enriches deterministic router recommendations and manual review
  reports with provider-catalog-backed envelope fields; this remains
  non-executing source/test/docs contract proof only.
- Phase 127 adds provider/runtime probe boundary packet drafting; this is
  future-boundary paperwork only and does not probe providers, models, or
  runtimes.
- Phase 128 integrates provider probe packet status into manual review
  artifacts; this is status visibility only, not authorization or execution.
- Phase 129 adds explicit CLI adapter flags for provider probe packet
  paperwork drafting; this is manual review metadata only, not a probe.
- Phase 130 registers operator evidence that the CLI paperwork path rendered
  expected provider probe packet metadata; exit code was not separately
  captured.
- Phase 131 registers read-only local Ollama `/api/tags` provider-surface
  visibility at one point in time with nine model names.
- Phase 132 registers Phase 130 and Phase 131 accepted operator proofs in
  source docs/ledgers without rerunning them.
- Phase 133 registers read-only local Ollama `/api/show` model metadata
  visibility for `qwen3-30b-24k:latest` at one point in time, including GGUF,
  Qwen3 MoE, 30.5B, Q4_K_M, model-info metadata, template, parameters, and
  license presence.
- Phase 134 registers Phase 133 in source docs/ledgers without rerunning it.
- Phase 135 commits the Phase 130 through Phase 134 provider-proof ledger chain
  locally at `a4c6815` using explicit docs staging only.
- Phase 136 pushes `a4c6815` to `origin/main` with range
  `3e0e9af..a4c6815`.
- Phase 137 registers those git checkpoint proofs without rerunning commit or
  push.
- Phase 138 commits the Phase 135 through Phase 137 checkpoint ledger chain at
  `18da1e7` using explicit docs staging only.
- Phase 139 confirms `origin/main` was already aligned at `18da1e7`;
  `Everything up-to-date` means the command did not newly advance the remote.
- Phase 140 registers those checkpoint proofs without rerunning commit or
  push.
- Phase 143 adds a deterministic provider evidence registry and surfaces
  accepted Phase 131 and Phase 133 read-only visibility evidence in manual
  review reports.
- Phase 146 adds deterministic provider evidence fields to router/provider
  recommendation envelope data without changing execution authority.
- Phase 149 adds deterministic evidence-gated route-selection readiness that
  can name a future proof boundary without executing it.
- Phase 152 adds a deterministic future generation smoke probe packet contract
  without executing the packet.
- Phase 156 retargets the active future smoke probe packet to `qwen3.6:27b`
  at source/test/docs level only.
- Phase 160 registers accepted Phase 159 Retry 1 `qwen3.6:27b`
  `/api/generate` marker smoke evidence in source/docs/tests without rerunning
  the provider proof. The earlier Phase 159 initial failure remains a
  token-budget/probe-shape failure, and Phase 155 Retry 3 remains a 30b/24k
  CUDA OOM failure.
- Phase 163 registers accepted Phase 162 `qwen3.6:27b` `/api/show` metadata
  visibility in source/docs/tests without rerunning the provider proof.
- Phase 141 and Phase 142 transport checkpoints are accepted in coordinator
  metadata, but Phase 143 does not recursively expand them into source phase
  docs.
- Route validation is admission policy only, not route execution.
- Model output is not proof.
- Capability labels are not implementation proof or execution authority.
- Registry lookup is not execution.
- Live prompt-to-envelope inference/productized classifier remains open.
- No live raw prompt inference or natural-language intent inference exists yet.
- No worker dispatch, worker execution, or concrete substrate selection exists
  yet.
- Live router remains open.
- RAG, reminders, web lookup implementation, lightweight answer productization,
  provider/model routing, route execution, and production readiness remain
  open.
- Productized coordinator CLI/UI, service/API/UI productization, and live
  worker dispatch remain open.
- Productized answer, lookup, and scheduler lanes remain open.

### Local-First Model Router / Provider

- Phase 122 defines deterministic router posture only.
- Phase 123 renders router posture in manual review reports only.
- Phase 124 repairs validation-command compatibility only.
- Phase 125 defines provider-tier catalog and escalation matrix policy only.
- Phase 126 enriches the router/provider recommendation envelope with
  provider-catalog facts only.
- Phase 127 drafts provider/runtime probe boundary packets only.
- Phase 128 renders provider probe packet status in manual review only.
- Phase 129 renders explicit CLI-requested provider probe packet paperwork
  metadata only.
- Phase 130 operator proof accepted the CLI paperwork rendering with an
  exit-code caveat.
- Phase 131 operator proof accepted read-only `/api/tags` provider-surface
  visibility only.
- Phase 132 registers those proofs only and does not authorize Phase 133.
- Phase 133 operator proof accepted read-only `/api/show` metadata visibility
  for `qwen3-30b-24k:latest` only.
- Phase 134 registers Phase 133 only and does not authorize generation or
  route execution.
- Phase 135 is a local commit checkpoint for the Phase 130-134 provider-proof
  ledger chain only.
- Phase 136 is a remote push checkpoint for commit `a4c6815` only.
- Phase 137 registers the checkpoint proofs only.
- Phase 138 is a local commit checkpoint for the Phase 135-137 checkpoint
  ledger chain only.
- Phase 139 is a remote-alignment checkpoint for commit `18da1e7` only; it did
  not newly advance `origin/main`.
- Phase 140 registers the checkpoint proofs only.
- Phase 143 provider evidence registry is deterministic evidence posture only.
- Phase 131 and Phase 133 evidence can be surfaced in reports, but it remains
  evidence visibility only.
- Phase 146 evidence-backed recommendation envelope fields are deterministic
  policy data only and are not runtime provider selection.
- Phase 149 route-selection readiness is evidence-gated deterministic posture
  only; provider evidence is not execution authority.
- The generation-smoke evidence gate is satisfied only for the exact accepted
  Phase 159 Retry 1 request.
- Phase 152 future generation smoke probe packet existence is not execution;
  future live execution still requires explicit coordinator authorization.
- Phase 163 satisfies the prior accepted 27b `/api/show` metadata blocker.
- Phase 165 reviews the route-selection readiness/recommendation-envelope
  posture after Phase 163 without adding execution authority.
- Phase 169 adds a tiny vertical tracer dry report artifact contract over the
  safe fixture harness spine without adding execution authority.
- Phase 172 Retry 3 accepts operator proof that the tiny vertical tracer dry
  artifacts can be generated and inspected from current pushed source into a
  temp directory without adding execution authority.
- Phase 176 adds a CLI-compatible adapter over the Phase 169 tiny vertical
  tracer dry report, including caller-supplied JSON dry artifact writing for
  `safe_direct_answer` only, without adding execution authority.
- Phase 179 accepts PowerShell operator smoke proof that the Phase 176 tiny
  vertical tracer CLI adapter works as a dry deterministic command surface
  without adding execution authority.
- Phase 183 defines a supervised provider-call tracer packet contract and pure
  captured-result classifier for a future operator-run marker smoke, without
  adding HTTP/provider/model execution authority.
- Phase 187 reconciles the supervised provider-call tracer target to
  `qwen3.6:35b-a3b` based on Phase 186 Retry 4 current inventory visibility
  only. The prior `qwen3.6:27b` marker-smoke and metadata evidence are not
  transferred to `qwen3.6:35b-a3b`.
- Phase 190 accepts constrained one-call 30B marker-smoke viability for
  `qwen3:30b-a3b-instruct-2507-q4_K_M` only; it does not prove route
  execution, semantic correctness, real workload sufficiency, long-context
  behavior, sustained-load stability, or production readiness.
- Phase 191 disallows `qwen3.6:35b-a3b` for current laptop target selection
  based on Roger's operational lockup evidence and retargets the supervised
  provider-call tracer packet to
  `qwen3:30b-a3b-instruct-2507-q4_K_M`. `qwen3.6:27b` remains the safer
  fallback candidate.
- Phase 194 accepts captured product marker smoke for
  `qwen3:30b-a3b-instruct-2507-q4_K_M` with `ORCH_PROVIDER_SMOKE_OK`; Retry 3
  is the accepted classifier/proof artifact backfill, and earlier final PASS
  lines are not accepted for classifier/proof artifact status.
- Phase 195 registers the Phase 194 proof in docs/ledgers only and does not
  authorize follow-on work.
- Phase 202 adds a deterministic route-path proof packet contract for the
  future move from direct provider marker smoke to route-mediated provider
  marker smoke. It requires request intake/harness, route recommendation/
  readiness, explicit route execution boundary, provider call through route
  path, captured response, persisted artifact path, and displayed/reviewable
  outcome evidence before route-mediated execution can be claimed.
- Phase 206 adds the controlled runner/CLI/artifact seam for a future
  route-mediated provider smoke proof, with dry-run default behavior,
  caller-supplied captured-result review, and explicit rejection of provider
  call flags during this phase.
- Phase 208 adds a guarded execution adapter path for a future operator
  boundary. It can call only an injected provider callable after explicit
  route/provider/execution-mode/model/marker guards pass; fake injected tests
  are not runtime proof.
- Phase 212 adds a guarded live Ollama transport adapter path for a later
  operator boundary. Source/tests use injected transport only; no provider,
  model, Ollama, HTTP, or route runtime execution is performed. Fake injected
  transport validation is not runtime proof, and the runtime classification is
  reserved for later actual live HTTP evidence.
- Phase 228 registers accepted Phase 216 Retry 3 operator proof for exactly
  one route-mediated live Ollama `/api/generate` marker-smoke call through the
  live transport CLI. The accepted artifact classifies as
  `route_mediated_provider_smoke_runtime_marker_pass` for
  `qwen3:30b-a3b-instruct-2507-q4_K_M` and
  `ORCH_ROUTE_PROVIDER_SMOKE_OK` only.
- No live provider/model routing, provider/model execution, runtime/platform
  execution beyond the exact Phase 228 marker-smoke boundary, model
  generation beyond the exact accepted marker response, `/api/chat`, model
  loadability, VRAM sufficiency beyond the exact accepted smoke request,
  provider runtime import, worker dispatch, RAG/web/scheduler execution, route
  execution beyond the exact Phase 228 marker-smoke boundary, or production
  readiness is proven.
- Future deeper provider/runtime/model proof remains a separate explicit
  boundary.
- Coding must remain one route among many, not the product identity.
- Triage status: `ACTIVE_NBM_CANDIDATE` only if prompt-to-envelope inference,
  live router, productized answer/lookup/scheduler lanes, or another routing
  proof gap is ranked highest; otherwise `DEFERRED_VALID`.

### Local-First Model / Router / Provider

- Ollama/provider surfaces exist but not as the first-pass router.
- Qwen/Ollama local-first routing is not accepted or proven.
- There is no strict router JSON contract.
- There is no confidence/fallback/escalation policy.
- Ollama remains report-only, not mutation-capable.
- Triage status: `DEFERRED_VALID` or `EXTERNAL_TRACK` unless an explicit
  product/router integration boundary authorizes it.

### RAG / Local Document Lookup

- There is no mature document ingestion/indexing.
- There is no retrieval interface.
- There is no citation/source artifact contract.
- There is no grounding verifier.
- There is no stale-source policy.
- Triage status: `DEFERRED_VALID` unless a product RAG boundary is ranked;
  platform/package evidence remains `EXTERNAL_TRACK`.

### Reminder / Scheduler

- There is no time parser.
- There is no persisted reminder model.
- There is no scheduler/service loop.
- There is no notification backend.
- There are no update/cancel semantics.
- There is no restart-survival proof.
- Triage status: `DEFERRED_VALID` unless a reminder/scheduler boundary is
  ranked highest.

### General Answer / Lightweight Report-Only

- Phase 235 adds a deterministic lightweight `general_answer` report-only
  contract for structured low-risk requests.
- The lane produces a reviewable artifact with accepted facts, blocked
  conditions, missing requirements, caveats, non-proofs, all-false activity
  flags, and an operator-visible next action.
- Phase 243 surfaces that Phase 235 payload and rendered report section inside
  manual review output for accepted low-risk direct-answer cases while
  preserving router policy posture.
- Phase 235 is not semantic answer quality proof, model-backed generation,
  live router proof, RAG/local lookup, web lookup, scheduler/reminder
  execution, connector execution, worker dispatch, Codex dispatch, or
  production readiness.
- Phase 243 is not semantic answer quality proof, model-backed generation,
  provider/runtime execution, live router proof, RAG/local lookup, web lookup,
  scheduler/reminder execution, connector execution, worker/Codex dispatch,
  service/API/UI productization, or production readiness.
- An optional persistence policy is needed.
- A local-first answer/fallback policy is needed.
- Triage status: `DEFERRED_VALID` unless the lightweight answer lane is ranked
  highest.

### Platform / Installer / OpenClaw

- Keep platform/installer/OpenClaw separate from the product repo unless
  explicitly integrated.
- The platform capsule is detailed authority, not a product doc.
- Do not make live installer/runtime claims without fresh operator output.
- Decide standalone installer versus Orchestrator infrastructure dependency.
- Document the standalone installer run path later under an explicit platform
  boundary.
- Triage status: `EXTERNAL_TRACK` unless an explicit product integration
  boundary authorizes product-side work.

### Export / Artifact Proof

- Native PowerShell direct invocation is the canonical local export lane:
  `& $Exporter -ProductRepoPath $Repo -OutputDir $OutputDir`
- Avoid `cmd.exe`, nested `powershell.exe -File`, WSL wrappers, and string-built
  quote mazes.
- Artifact verification should eventually be automated.
- Phase export/upload proof is often external to exported docs until the next
  reconciliation.
- Triage status: `BLOCKED_AWAITING_PROOF` when a newer local source state needs
  artifact reconciliation; otherwise `DEFERRED_VALID`.

### Persistence / Atomicity / Locking

- There is no full atomic persistence/locking.
- Task and artifact writes can be separate.
- Phase 101 rollback exists for one path but is not a general transaction
  system.
- Crash consistency, concurrency policy, and migration/versioning strategy are
  needed.
- Triage status: `DEFERRED_VALID` unless persistence invariants are ranked
  highest.

### Testing / CI / Hermeticity

- Targeted tests exist.
- There is no mature CI.
- There is no global hermetic isolation guarantee.
- There is no test matrix.
- There is no policy defining tests required by task type.
- Triage status: `DEFERRED_VALID` unless required-test policy or CI is ranked
  highest.

### Service / API / UI / Auth

- There is no stable service/API layer.
- There is no auth layer.
- There is no operator dashboard.
- There is no multi-user model.
- There is no deployment story.
- Triage status: `DEFERRED_VALID` unless a service/API boundary is ranked
  highest.

### Codebase Structure / Technical Debt

- The `main.py` monolith remains open.
- The BOM issue remains open.
- Router, providers, RAG, reminders, coding spine, and platform integration
  must remain cleanly separated.
- Governance docs must not become ceremonial rather than operational.
- Triage status: `DEFERRED_VALID` unless bounded structure assessment is ranked
  highest.

### Documentation / Language Architecture / DDD Context Map

- `PRODUCT_DOCS_LANGUAGE_ARCHITECTURE_AND_DDD_CONTEXT_MAP` now has a durable
  language/context architecture map in `docs/CONTEXT_MAP.md`.
- Purpose: assess whether Orchestrator's docs should be reorganized around
  DDD-style language architecture, including `docs/CONTEXT_MAP.md`, `context.md`
  files, Ubiquitous Language, active-vs-historical doc separation, and
  redundancy reduction.
- Current state: Phase 104 creates the repo-local context map and language
  authority model.
- Required caveat: Phase 103 did not perform this cleanup.
- Required caveat: Phase 104 context-map existence does not complete cleanup,
  reorganization, redundancy reduction, or historical-doc reconciliation.
- Open artifact-proof caveat: a supplied handoff may claim Phase 102 upload
  hash
  `F5A53C67100F95744E20E25ED5A48A244E4D08C021E848463AAF3BE2A7D23CA6`, while
  inspected repo docs preserve Phase 101 as the accepted uploaded artifact and
  state Phase 102 was not exported/uploaded. Do not resolve without fresh
  artifact proof.
- Next boundary: future documentation cleanup or context-specific docs only if
  separately ranked and authorized.
- Triage status: `ACTIVE_NBM_CANDIDATE` only if documentation architecture
  cleanup is ranked highest; otherwise `DEFERRED_VALID`.

### Worker / Relay / Operator Routing

- Roger is owner/operator.
- The coordinator ranks, scopes, reviews, and ratifies.
- The worker agent inspects and mutates files within authorized boundaries.
- The relay coordinator constructs command batches only and does not execute.
- Phase 106 adds the coding worker boundary contract in
  `docs/ORCHESTRATOR_INTERACTION_MODEL.md`.
- Future sessions must not confuse relay tasks with worker assignments.
- Triage status: `DEFERRED_VALID` unless role confusion is the ranked
  blockage.

## Track Update Rules

1. Any phase that changes a track's accepted state, open threads, proof status,
   next boundary, or source-of-truth docs must update this file.
2. Any handoff should include only active relevant open threads and triage
   statuses, while referring to this ledger for the full list.
3. Any new coordinator session must read this ledger and triage visible open
   threads before recommending the next boundary.
4. Any track shift must be explicit in `RESPONSE_METADATA`.
5. Any platform/installer/OpenClaw claim requires platform authority documents
   plus fresh operator output when current runtime behavior is involved.

## Do-Not-Confuse Warnings

- Coding spine is not the entire product.
- Authorization is not execution.
- Export PASS is not upload PASS.
- Worker PASS is not coordinator artifact acceptance.
- Platform installer is not the product repo.
- Model output is not proof.
- Route validation is not execution.
- A Phase 217 live transport failure artifact is failure-shape evidence, not a
  route-mediated runtime marker pass.
- Phase 228 proves only the accepted narrow route-mediated provider
  marker-smoke runtime path; it is not semantic correctness, real workload,
  long-context, sustained-load, production readiness, Hermes/OpenClaw behavior,
  or `qwen3.6:35b-a3b` authorization proof.
- Memory is not proof.
- RAG, local docs, and reminders are intended tracks but are not implemented
  maturely yet.
