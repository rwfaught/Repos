# Phase 187 - Supervised Provider Call Tracer Target Reconciliation

## Purpose

Reconcile the supervised provider-call tracer packet target with the current
Ollama inventory facts proven in Phase 186 Retry 4.

Phase 183 created the packet with target `qwen3.6:27b`. Phase 186 Retry 4
proved current Ollama service availability and inventory visibility only:

- `/api/version` returned HTTP 200 with version `0.30.10`.
- `/api/tags` returned HTTP 200.
- `qwen3.6:27b` was not present.
- `qwen3.6:35b-a3b` was present.
- No `/api/generate` was run.
- No model execution occurred.

## Changed Files

- `orchestrator/supervised_provider_call_tracer.py`
- `tests/test_phase_183_supervised_provider_call_tracer_packet_contract.py`
- `docs/PHASE_187.md`
- `docs/SUPERVISED_PROVIDER_CALL_TRACER_RUNBOOK.md`
- `docs/TRACKS_AND_OPEN_THREADS.md`
- `docs/PHASE_INDEX.md`
- `docs/ACTION_LOG.md`
- `docs/SOURCE_MANIFEST.md`
- `docs/CONTEXT_MAP.md`

## Implementation Summary

The packet target changed from `qwen3.6:27b` to `qwen3.6:35b-a3b` and now
carries explicit Phase 187 reconciliation metadata over the original Phase 183
packet contract.

The packet records the Phase 186 Retry 4 inventory visibility key for
`qwen3.6:35b-a3b` only. It does not carry or transfer the prior
`qwen3.6:27b` marker-smoke or metadata evidence keys to `qwen3.6:35b-a3b`.

The classifier PASS fixture now requires returned model `qwen3.6:35b-a3b`,
HTTP 200, JSON parse success, response text containing
`ORCH_PROVIDER_SMOKE_OK`, and `done=True`. A returned model of `qwen3.6:27b`
now classifies as wrong model for this packet.

## Validation Commands And Results

- `python -m compileall orchestrator` - PASS
- `python -m unittest discover -s tests -p "test_phase_183_supervised_provider_call_tracer_packet_contract.py" -v` - PASS
- `python -m unittest discover -s tests -p "test_phase_176_tiny_vertical_tracer_cli_adapter_contract.py" -v` - PASS
- `python -m unittest discover -s tests -p "test_phase_169_tiny_vertical_tracer_bullet_dry_report_artifact_contract.py" -v` - PASS
- `git diff --check` - PASS
- `git status --short --branch` - PASS

## Accepted Facts

- The packet now carries `phase="PHASE_187"` and
  `artifact_kind="supervised_provider_call_tracer_packet_contract"`.
- The packet records `original_packet_phase="PHASE_183"`,
  `target_reconciliation_phase="PHASE_187"`, and
  `inventory_evidence_phase="PHASE_186_RETRY4"`.
- The packet carries `provider_catalog_key="local_model_candidate"` and
  `model_name="qwen3.6:35b-a3b"`.
- The packet records `endpoint_shape="POST local_ollama_http/api/generate"`
  and `endpoint_url="http://127.0.0.1:11434/api/generate"` as data only.
- The packet records `prompt_contract="Return exactly: ORCH_PROVIDER_SMOKE_OK"`
  and `expected_marker="ORCH_PROVIDER_SMOKE_OK"`.
- The packet records request parameters `stream=false`, `num_predict=96`, and
  `temperature=0`.
- Phase 186 Retry 4 inventory visibility is recorded as inventory evidence
  only for `qwen3.6:35b-a3b`.
- `qwen3.6:27b` is retired for the current packet because it was absent from
  the current Phase 186 Retry 4 inventory.
- Provider selection, provider execution, route execution, generation, and
  production readiness authority remain false.

## Non-Proofs

Phase 187 does not prove a `qwen3.6:35b-a3b` marker-smoke pass,
provider/model execution, route execution, live routing, HTTP/API endpoint
execution, Ollama generation, product-harness Codex dispatch, worker dispatch,
semantic correctness, real workload proof, service/API/UI productization,
production behavior, or production readiness.

Phase 186 Retry 4 inventory visibility is not marker-smoke proof. The endpoint
URL is data only. The model name is data only. Prior `qwen3.6:27b` evidence is
not proof for `qwen3.6:35b-a3b`.

## Caveats

- This is a packet target reconciliation only.
- `qwen3.6:35b-a3b` still needs a future supervised marker-smoke proof.
- A future PASS classification would remain marker-smoke review only and would
  preserve `route_execution_allowed=false` and `production_readiness=false`.

## Next Boundary Recommendation

`PHASE_188_SUPERVISED_PROVIDER_CALL_TRACER_35B_A3B_OPERATOR_PROOF`

`PHASE187_SUPERVISED_PROVIDER_CALL_TRACER_TARGET_RECONCILIATION_SOURCE_TEST_DOCS_PROVEN=PASS`
