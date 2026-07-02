# Phase 285 - Packet Schema Negative Edge Contract

## Boundary

`PHASE285_PACKET_SCHEMA_NEGATIVE_EDGE_CONTRACT_SOURCE_TEST_DOCS`

## Purpose

Phase 285 hardens packet schema negative edge cases and deterministic blocked
JSON shapes for the packet CLI and direct packet function path. It does not
broaden execution capability.

## Files Changed

- `orchestrator/operator_coding_task_packet.py`
- `tests/test_phase_285_packet_schema_negative_edge_contract.py`
- `docs/PHASE_285.md`
- `docs/PHASE_INDEX.md`
- `docs/ACTION_LOG.md`
- `docs/SOURCE_MANIFEST.md`
- `docs/TRACKS_AND_OPEN_THREADS.md`

## Validation Commands

- `python -m py_compile orchestrator/operator_coding_task_packet.py tests/test_phase_285_packet_schema_negative_edge_contract.py`
- `python -m unittest tests.test_phase_285_packet_schema_negative_edge_contract -v`
- `python -m unittest tests.test_phase_274_operator_facing_bounded_coding_task_packet`
- `python -m unittest tests.test_phase_275_operator_coding_task_packet_cli_file_input_adapter`
- `python -m unittest tests.test_phase_277_packet_cli_operator_runbook_golden_smoke`
- `python -m unittest tests.test_phase_279_packet_cli_runbook_execution_persistence_honesty`
- `python -m unittest tests.test_phase_283_packet_cli_operator_acceptance_record`
- `python -m unittest tests.test_phase_284_packet_cli_pre_run_residue_guard`
- `git diff --check`
- Search proof marker:
  `PHASE285_PACKET_SCHEMA_NEGATIVE_EDGE_CONTRACT_SOURCE_TEST_DOCS_PROVEN=PASS`
- Changed-file allowlist audit

## Proof Marker

`PHASE285_PACKET_SCHEMA_NEGATIVE_EDGE_CONTRACT_SOURCE_TEST_DOCS_PROVEN=PASS`

## Proof Scope

Phase 285 proves deterministic blocked/error JSON shapes for malformed packet
JSON, non-object JSON, direct non-object packet input, missing required fields,
empty `expected_output`, reused task ids, Windows backslash declared paths,
POSIX absolute paths, parent traversal, provider/model/runtime/platform
smuggling, unsupported execution policy, unsupported provider name, no-proof
and no-activity flag preservation, and matching blocked conditions from CLI and
direct function paths for invalid packet ids.

## Non-Proofs

Phase 285 does not prove semantic correctness, live provider/model execution,
runtime/platform behavior, autonomous AI coding, model-backed generation,
production readiness, service/API/UI/dashboard/auth/deployment behavior,
scheduler/reminder behavior, connector behavior, `general_answer` resumption,
platform/OpenClaw/Hermes/LightRAG behavior, cleanup/delete/archive authority,
or integrated production patch workflow readiness.

## Caveats

- Windows backslash paths are blocked for packet `files_in_scope`; packet paths
  remain project-relative forward-slash paths.
- Reused task ids are blocked before persistence to avoid overwriting existing
  task records.
- This phase only hardens negative contracts. It does not add providers,
  runtimes, platforms, services, APIs, UI, dashboard, auth, deployment, or
  patch-apply behavior.

## Generated Artifact And Residue Posture

The Phase 285 tests use temporary project stores and do not require repo-local
generated packet residue.
