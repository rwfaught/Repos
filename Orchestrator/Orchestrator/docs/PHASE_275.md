# Phase 275 - Operator Coding Task Packet CLI File Input Adapter

## Boundary

`PRODUCT_PHASE_275_OPERATOR_CODING_TASK_PACKET_CLI_FILE_INPUT_ADAPTER_SOURCE_TEST_DOCS`

## Purpose

Phase 275 adds the smallest deterministic standard-library CLI/file-input
adapter over the Phase 274 operator coding-task packet surface.

The adapter reads a local JSON packet file, calls the existing
`run_operator_coding_task_packet(packet)` function, and prints deterministic
JSON output for operator review.

## Files Changed

Source:

- `orchestrator/operator_coding_task_packet_cli.py`

Tests:

- `tests/test_phase_275_operator_coding_task_packet_cli_file_input_adapter.py`

Docs:

- `docs/PHASE_275.md`
- `docs/PHASE_INDEX.md`
- `docs/ACTION_LOG.md`
- `docs/SOURCE_MANIFEST.md`
- `docs/TRACKS_AND_OPEN_THREADS.md`

## Behavior

The Phase 275 CLI adapter:

- exposes `main(argv: list[str] | None = None) -> int`
- supports module execution with
  `python -m orchestrator.operator_coding_task_packet_cli --packet-json <path>`
- accepts only `--packet-json <path>`
- reads UTF-8-sig JSON from a local packet file
- returns deterministic blocked JSON and a nonzero exit code for unreadable
  files, malformed JSON, non-object JSON, or packet validation failure
- calls the existing Phase 274 packet function for valid JSON-object packets
- prints deterministic JSON with `sort_keys=True`, `indent=2`, and a trailing
  newline
- preserves deterministic `local_file`-only behavior

## Validation

Validation passed:

- `python -m py_compile orchestrator/operator_coding_task_packet_cli.py tests/test_phase_275_operator_coding_task_packet_cli_file_input_adapter.py`
- `python -m unittest tests.test_phase_275_operator_coding_task_packet_cli_file_input_adapter -v`
- `python -m unittest tests.test_phase_78_current_success_result_review tests.test_phase_91_provider_status_routing tests.test_phase_92_verification_provenance tests.test_phase_95_task_execution_policy_classification tests.test_phase_97_model_backed_patch_proposal_protocol tests.test_phase_98_patch_proposal_operator_apply_authorization_gate tests.test_phase_99_bounded_patch_apply_engine_for_operator_authorized_proposals tests.test_phase_100_patch_apply_result_verification_and_task_completion_gate tests.test_phase_101_verified_patch_apply_task_completion_finalization_gate tests.test_phase_272_integrated_coding_task_current_spine_proof tests.test_phase_274_operator_facing_bounded_coding_task_packet tests.test_phase_275_operator_coding_task_packet_cli_file_input_adapter -v`
- `git diff --check`

The targeted current-spine regression with Phase 275 ran 105 tests with one
symlink-environment skip and passed.

## Non-Proofs

Phase 275 does not prove or add:

- semantic correctness
- live provider/model behavior
- runtime/platform behavior
- autonomous AI coding behavior
- production readiness
- model-backed generation
- `general_answer` resumption
- service/API/UI behavior
- scheduler/reminder behavior
- connector behavior

## Marker

`PHASE275_OPERATOR_CODING_TASK_PACKET_CLI_FILE_INPUT_ADAPTER_SOURCE_TEST_DOCS_PROVEN=PASS`
