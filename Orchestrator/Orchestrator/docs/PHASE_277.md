# Phase 277 - Packet CLI Operator Runbook Golden Smoke

## Boundary

`PRODUCT_PHASE_277_PACKET_CLI_OPERATOR_RUNBOOK_GOLDEN_SMOKE_SOURCE_TEST_DOCS`

## Purpose

Phase 277 adds a durable operator-facing runbook and golden-smoke test for the
Phase 275 packet CLI:

`python -m orchestrator.operator_coding_task_packet_cli --packet-json <path>`

The runbook lets Roger write a minimal valid local JSON packet, invoke the CLI,
and understand the deterministic JSON output fields without reconstructing the
packet schema from tests or coordinator memory.

## Files Changed

Docs:

- `docs/OPERATOR_CODING_TASK_PACKET_CLI_RUNBOOK.md`
- `docs/PHASE_277.md`
- `docs/ACTION_LOG.md`
- `docs/PHASE_INDEX.md`
- `docs/SOURCE_MANIFEST.md`
- `docs/TRACKS_AND_OPEN_THREADS.md`

Tests:

- `tests/test_phase_277_packet_cli_operator_runbook_golden_smoke.py`

Production source:

- None.

## Validation Commands

- `python -m py_compile orchestrator/operator_coding_task_packet.py orchestrator/operator_coding_task_packet_cli.py`
- `python -m unittest tests.test_phase_274_operator_facing_bounded_coding_task_packet`
- `python -m unittest tests.test_phase_275_operator_coding_task_packet_cli_file_input_adapter`
- `python -m unittest tests.test_phase_277_packet_cli_operator_runbook_golden_smoke`
- Search proof for
  `PHASE277_PACKET_CLI_OPERATOR_RUNBOOK_GOLDEN_SMOKE_SOURCE_TEST_DOCS_PROVEN=PASS`
- Search proof for `OPERATOR_CODING_TASK_PACKET_CLI_RUNBOOK.md`
- Git status proof for authorized changed files only

## Proof Marker

`PHASE277_PACKET_CLI_OPERATOR_RUNBOOK_GOLDEN_SMOKE_SOURCE_TEST_DOCS_PROVEN=PASS`

## Proof Scope

This phase proved a source/test/docs-backed operator runbook and golden-smoke
contract for the packet CLI. The golden smoke parses the runbook packet,
writes it to a local temp JSON file, invokes the actual CLI main path with
`--packet-json`, and verifies deterministic parseable JSON, `local_file`
behavior, inspectable persisted artifacts in patched temp directories, false
no-activity flags, and current non-proof caveats.

Phase 279 later corrected the operator-facing posture: the actual packet CLI is
an execution and persistence surface and may create repo-local durable files
under `outputs/`, `data/tasks/`, `data/artifacts/`, and
`data/verifier_results/`. Phase 277 must not be read as a repo-read-only
operator smoke claim.

## Non-Proofs

Phase 277 does not prove semantic correctness, live provider/model execution,
runtime/platform behavior, autonomous AI coding, production readiness,
service/API/UI behavior, scheduler/reminder behavior, connector behavior,
`general_answer` resumption, WSL/Ollama/OpenClaw/Hermes/Discord/installer
behavior, or the full production patch workflow.
