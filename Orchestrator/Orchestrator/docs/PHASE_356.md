# Phase 356 - Product Task Packet Routing Contract Readback

Boundary:

`PHASE356_PRODUCT_TASK_PACKET_ROUTING_CONTRACT_READBACK_SOURCE_TEST_DOCS`

## Purpose

Phase 356 adds a narrow deterministic source/test/docs routing-contract readback
surface for product task packets after Phase 349, Phase 351, Phase 352, Phase
354, and Phase 355.

The readback describes routing eligibility, route contracts, route stop
conditions, blocked routes, routing gates, evidence requirements, non-proofs,
and next-safe routing doctrine. It does not implement routing, execute route
selection, dispatch workers, apply patches, execute providers/models, inspect
live tasks, mutate data, create CLI/API/service/UI/dashboard behavior, resume
`general_answer`, or perform live integration behavior.

## Changed Files

- `orchestrator/product_task_packet_routing_contract_readback.py`
- `tests/test_phase_356_product_task_packet_routing_contract_readback.py`
- `docs/PHASE_356.md`
- `docs/PHASE_INDEX.md`
- `docs/ACTION_LOG.md`
- `docs/SOURCE_MANIFEST.md`
- `docs/TRACKS_AND_OPEN_THREADS.md`

## Accepted Facts

- Phase 355 is pushed and remote-ref verified.
- Current verified `origin/main`:
  `5b4ca1f1834a45503e14d353e1377d5a6a648825`.
- Phase 355 push/ref marker:
  `PHASE355_PUSH_AND_POST_COMMIT_REF_VERIFY_RESULT=PASS`
- Phase 355 marker:
  `PHASE355_PRODUCT_TASK_PACKET_LIFECYCLE_STATE_READBACK_SOURCE_TEST_DOCS_PROVEN=PASS`
- Phase 354 marker:
  `PHASE354_PRODUCT_TASK_PACKET_NEXT_SEAM_SELECTION_READBACK_SOURCE_TEST_DOCS_PROVEN=PASS`
- Phase 352 marker:
  `PHASE352_PRODUCT_TASK_PACKET_OPERATOR_DECISION_READBACK_SOURCE_TEST_DOCS_PROVEN=PASS`
- Phase 351 marker:
  `PHASE351_PRODUCT_TASK_PACKET_NEGATIVE_EDGE_CONTRACT_SOURCE_TEST_DOCS_PROVEN=PASS`
- Phase 349 marker:
  `PHASE349_PRODUCT_TASK_PACKET_OPERATOR_REPORT_SURFACE_SOURCE_TEST_DOCS_PROVEN=PASS`
- Source Files refreshes are handoff/source snapshots only unless an explicit
  official capsule-proof boundary supersedes them.
- Phase 335 remains the only accepted official clean capsule proof unless
  explicitly superseded:
  `04cb5a2205bedcef767d8cab6344237e9b4ce1f75f19793a56425ab8b197d49d`.

## Implementation Summary

Phase 356 adds
`read_product_task_packet_routing_contract_readback()` as a pure deterministic
source-level readback. It returns static data only and does not read files, run
subprocesses, inspect Git, access environment variables, access networks,
execute providers/models/runtimes, dispatch workers, apply patches, mutate
files, parse live packets, create CLI behavior, create service/API/UI/dashboard
behavior, or execute routing decisions.

The readback records Phase 349, Phase 351, Phase 352, Phase 354, and Phase 355
source basis; completed packet spine; route contracts; routing gates; blocked
routes; routing doctrine; invalid route claims; stop conditions; false activity
flags; required report caveats; source/capsule/Git truth separation; and a
conservative recommended next boundary.

## Validation Checklist

- `git status --short --branch`
- `python -m py_compile orchestrator/product_task_packet_routing_contract_readback.py`
- `python -m unittest tests.test_phase_356_product_task_packet_routing_contract_readback`
- Marker search for
  `PHASE356_PRODUCT_TASK_PACKET_ROUTING_CONTRACT_READBACK_SOURCE_TEST_DOCS_PROVEN=PASS`
- Non-proof and lockout text search in source, test, and phase doc
- `git diff --check`
- changed-file allowlist audit
- `git status --short --branch`

## Marker

`PHASE356_PRODUCT_TASK_PACKET_ROUTING_CONTRACT_READBACK_SOURCE_TEST_DOCS_PROVEN=PASS`

## Recommended Next Boundary

`PHASE357_PRODUCT_TASK_PACKET_PATCH_WORKFLOW_CONTRACT_READBACK_SOURCE_TEST_DOCS`

Rationale: after routing-contract readback, a patch-workflow contract readback
can define patch eligibility and patch-stop doctrine without applying patches.

## Routing-Contract Doctrine

- Readback precedes route execution.
- Lifecycle state precedes route eligibility.
- Routing contract precedes routing implementation.
- Patch workflow contract precedes patch application.
- Worker dispatch contract precedes worker dispatch.
- Provider policy contract precedes provider/model execution.
- Domain-general intake contract precedes domain-general intake.
- Coordinator review precedes push/ref verification.
- Remote-before check precedes push.
- Pushed commit does not prove production readiness.
- Test PASS does not prove semantic correctness.
- Worker PASS is evidence, not coordinator ratification.
- Source Files refresh is not official capsule proof.
- Phase 335 remains accepted capsule proof unless explicitly superseded.
- Context saturation routes to handoff, not scope expansion.

## Non-Proofs

- No runtime/provider/model/platform execution occurred.
- No service/API/UI/dashboard/auth/deployment work occurred.
- No WSL, Ollama, OpenClaw, Hermes, LightRAG, Discord, installer, service,
  API, UI, dashboard, auth, deployment, scheduler, connector, or production
  behavior occurred.
- No general_answer work occurred.
- No `general_answer` work occurred.
- No Source Files refresh occurred.
- No capsule/export/package refresh occurred.
- No Source Files refresh, capsule refresh, export/package refresh, or official
  capsule proof extension occurred.
- No worker dispatch occurred.
- No patch workflow implementation or patch application occurred.
- No routing implementation, route execution, or route selection execution
  occurred.
- No provider policy implementation or provider/model execution occurred.
- No domain-general intake implementation occurred.
- No lifecycle transition execution occurred.
- No live task creation, live task execution, or live mutation occurred.
- No live business-data, Obsidian, or PKMS access occurred.
- No adapter execution or real domain execution occurred.
- No parser, runner, dispatcher, CLI, service, API, UI, or live harness
  behavior occurred.
- No push occurred in this phase unless a later coordinator/operator boundary
  does it.
- No production readiness claim is made.
- No semantic correctness claim is made.
- No autonomous AI coding authority is implied.
- No official capsule proof beyond Phase 335 is registered.

## Source/Capsule/Git Truth Separation Caveat

Git repo truth remains separate from Source Files handoff snapshots, official
clean product capsule proofs, and full Git repo backups including `.git`.
Phase 356 adds a source/test/docs routing-contract readback only and does not
refresh or supersede the Phase 335 official clean capsule proof.

## Next-Safe-Seam Doctrine

Choose readback before execution, lifecycle before routing, routing contract
before routing implementation, patch contract before patch application, worker
contract before worker dispatch, provider policy before provider/model
execution, and handoff when context saturation appears. Separate push/ref
verification and separate capsule-proof boundaries remain required for those
claims.
