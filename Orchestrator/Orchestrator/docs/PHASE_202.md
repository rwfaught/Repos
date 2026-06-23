# Phase 202 - Route Path Proof Packet Contract

## Purpose

Phase 202 creates a deterministic route-path proof packet contract defining
the smallest future proof needed to move from direct captured provider marker
smoke to route-mediated provider marker smoke.

This phase does not execute a route, provider, model, runtime, HTTP endpoint,
worker, WSL, Ollama, Hermes, OpenClaw, Discord, or production behavior.

## Current Accepted Prior Facts

- Phase 190 proved constrained 30B marker-smoke viability only for
  `qwen3:30b-a3b-instruct-2507-q4_K_M`.
- Phase 194 proved captured direct product marker smoke only for
  `ORCH_PROVIDER_SMOKE_OK`.
- Phase 194 Retry 3 is the accepted classifier/proof-artifact backfill.
- Phase 194 classification:
  `captured_marker_smoke_pass_not_route_execution`.
- Phase 194 does not prove route execution.
- Phase 198 clarified that `PHASE_XXX` labels and `docs/PHASE_XXX.md` files
  are not one-to-one.
- Phase 200/201 proved the refreshed product capsule, ending at
  `PHASE_201_SOURCE_CAPSULE_UPLOAD_COORDINATOR_INSPECTION=PASS`.

## Packet Contract

Created source:

- `orchestrator/route_path_proof_packet.py`

Created tests:

- `tests/test_phase_202_route_path_proof_packet_contract.py`

The packet records:

- `phase=PHASE_202`
- `artifact_kind=route_path_proof_packet_contract`
- `prior_direct_marker_proof_phase=PHASE_194`
- `route_proof_target_model=qwen3:30b-a3b-instruct-2507-q4_K_M`
- `disallowed_model=qwen3.6:35b-a3b`
- `fallback_candidate=qwen3.6:27b`
- `prior_direct_marker=ORCH_PROVIDER_SMOKE_OK`
- `future_route_marker=ORCH_ROUTE_PROVIDER_SMOKE_OK`
- `future_boundary=future_route_mediated_provider_marker_smoke_operator_proof`

The future route marker is intentionally distinct from the direct provider
marker.

## Required Future Proof

The future route-mediated proof must include:

- Request intake/harness evidence
- Route recommendation/readiness evidence
- Explicit route execution boundary evidence
- Provider call through route path evidence
- Captured HTTP/status/JSON/model/marker evidence if Ollama remains the
  provider surface
- Persisted artifact path evidence
- Displayed/reviewable outcome evidence

## Current Gap

The product has direct captured provider marker smoke evidence, but not:

request enters harness -> route recommendation/readiness -> route path
execution boundary -> provider call through route path -> captured response ->
persisted/displayed outcome.

Current success criterion is still not met for route-mediated provider
execution.

## Non-Proofs

Phase 202 does not prove:

- Route execution
- Provider execution
- Model execution
- Runtime execution
- `/api/generate`
- `/api/chat`
- `/api/tags`
- `/api/version`
- Worker dispatch
- Semantic correctness
- Real workload sufficiency
- Long-context behavior
- Sustained-load stability
- Hermes/OpenClaw behavior
- Production readiness

The packet contract is not route execution. Route recommendation is not
execution. The provider target string is not model execution. Prior direct
provider smoke is not route-mediated proof.

## Validation

- `python -m pytest tests/test_phase_202_route_path_proof_packet_contract.py`
  - NOT RUN: local Python reported `No module named pytest`
- `python -m unittest discover -s tests -p "test_phase_202_route_path_proof_packet_contract.py" -v`
  - PASS
- `python -m py_compile orchestrator/route_path_proof_packet.py` - PASS
- `git diff --check` - PASS
- `git diff --cached --check` - PASS

`PHASE202_ROUTE_PATH_PROOF_PACKET_CONTRACT_SOURCE_TEST_DOCS_PROVEN=PASS`
