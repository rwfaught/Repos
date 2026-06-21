# Phase 103 - Domain-General Request Intake Taxonomy And Routing Contract

Status: LOCALLY SOURCE/TEST/DOCS-PROVEN; EXPORT/UPLOAD NOT PERFORMED

Marker:
`PHASE103_DOMAIN_GENERAL_REQUEST_INTAKE_TAXONOMY_AND_ROUTING_CONTRACT_LOCAL_SOURCE_TEST_DOCS_PROVEN=PASS`

## Purpose

Phase 103 defines a domain-general request taxonomy and strict route-envelope
validation contract.

The purpose is not request execution. The purpose is to create a deterministic
governance membrane that can validate future structured route proposals before
any downstream local-first model routing, connector use, scheduling, document
lookup, mutation, or answer path is admitted.

Core rule preserved:

Orchestrator must not become a coding-agent harness. Orchestrator may
coordinate coding-agent harnesses.

## Changed Behavior

- Added `orchestrator.request_routing` as a standalone importable contract
  module.
- Defined the allowed top-level request types:
  `general_answer`, `local_document_lookup`, `reminder_request`,
  `coding_task`, `file_operation`, `planning_request`, `research_request`,
  `creative_generation`, `unsupported_or_requires_connector`, and
  `needs_clarification`.
- Defined the required route-envelope fields through
  `ROUTE_ENVELOPE_REQUIRED_FIELDS`.
- Added deterministic `validate_route_envelope(envelope)` behavior that
  validates only proposed structured envelopes.
- Validation does not infer route type from raw natural-language prompts.
- Validation returns explicit `route_admission`, `accepted`, `request_type`,
  `missing_requirements`, `blocked_conditions`, and accepted
  `normalized_envelope` fields.
- Validation enforces boolean permission fields as real booleans and confidence
  as numeric `0.0` through `1.0`.
- Validation blocks contradictory permissions, direct-answer overreach,
  unsupported connector routes, invalid web/local-document use, scheduling
  without reminder route and operator confirmation, and mutation without coding
  or file-operation route plus operator confirmation.
- Validation is substrate-agnostic and rejects coding/file-operation route
  envelopes that name a provider/model/worker substrate as executor.
- Every validation result records no mutation, execution, provider, model,
  runtime, WSL, installer, Discord, bridge, adapter, platform, export, package,
  cleanup, deletion, or archive activity.

## Changed Files

- `orchestrator/request_routing.py`
- `tests/test_phase_103_domain_general_request_routing_contract.py`
- `docs/PHASE_103.md`
- `docs/PHASE_INDEX.md`
- `docs/ACTION_LOG.md`
- `docs/SOURCE_MANIFEST.md`
- `docs/CURRENT_SUCCESS_CRITERION.md`
- `docs/TRACKS_AND_OPEN_THREADS.md`

## Tests

- `tests/test_phase_103_domain_general_request_routing_contract.py`

## Proof Commands

From repo root:

`python -m py_compile .\orchestrator\request_routing.py .\tests\test_phase_103_domain_general_request_routing_contract.py`

`python -m unittest tests.test_phase_103_domain_general_request_routing_contract`

Recorded result:

`Ran 24 tests`

`OK`

## Explicit Non-Proofs

Phase 103 does not execute requests, tasks, providers, models, runtime, WSL,
installer, OpenClaw, Discord, bridge, adapter, platform, RAG, reminders,
scheduling, web lookup, local document lookup, export, package creation,
cleanup, deletion, archive, or production task behavior.

Phase 103 does not implement a live provider router, model router, scheduler,
RAG system, web lookup system, connector integration, autonomous writeback, or
coding-agent harness.

Phase 103 does not prove semantic correctness, model-output correctness,
production readiness, export verification, or upload verification.

## Caveats

- The validator accepts or rejects structured route envelopes only. A later
  boundary must define how route candidates are proposed.
- `research_request` may carry `allowed_to_use_web=true` only with an explicit
  `web_lookup_not_implemented` caveat; Phase 103 still implements no web lookup.
- `local_document_lookup` may carry `allowed_to_use_local_documents=true`, but
  Phase 103 implements no retrieval, indexing, grounding, citation, or RAG
  behavior.
- `reminder_request` may carry `allowed_to_schedule=true` only with operator
  confirmation, but Phase 103 implements no scheduler or reminder persistence.
- `coding_task` and `file_operation` may carry mutation permission constraints,
  but Phase 103 does not turn Orchestrator into a coding-agent harness and does
  not select any worker substrate.
- No Phase 103 export or upload was performed.

`PHASE103_DOMAIN_GENERAL_REQUEST_INTAKE_TAXONOMY_AND_ROUTING_CONTRACT_LOCAL_SOURCE_TEST_DOCS_PROVEN=PASS`
