# Phase 194 - Supervised Provider Call Tracer 30B Product Marker Operator Proof

## Purpose

Phase 194 records the accepted supervised provider-call tracer 30B product
marker proof for `qwen3:30b-a3b-instruct-2507-q4_K_M`.

Accepted status:

`PHASE194_SUPERVISED_PROVIDER_CALL_TRACER_30B_PRODUCT_MARKER_OPERATOR_PROOF=PASS_WITH_RETRY3_CLASSIFIER_ARTIFACT_BACKFILL`

Current accepted stop point:

`PHASE_194_RETRY3_PRODUCT_MARKER_CLASSIFIER_ARTIFACT_BACKFILL_NO_PROVIDER_CALL=PASS`

## Product Marker Facts

- Product marker: `ORCH_PROVIDER_SMOKE_OK`
- Prompt: `Return exactly: ORCH_PROVIDER_SMOKE_OK`
- Model: `qwen3:30b-a3b-instruct-2507-q4_K_M`
- HTTP status: `200`
- JSON parse success: `true`
- Returned model: `qwen3:30b-a3b-instruct-2507-q4_K_M`
- Response text: `ORCH_PROVIDER_SMOKE_OK`
- Done: `true`
- Done reason: `stop`
- Duration: `448ms`
- Marker present: `true`

## Classifier And Packet Facts

- Retry 3 classifier result:
  `classification=captured_marker_smoke_pass_not_route_execution`
- Accepted: `true`
- Packet phase: `PHASE_191`
- Packet artifact kind: `supervised_provider_call_tracer_packet_contract`
- Packet model: `qwen3:30b-a3b-instruct-2507-q4_K_M`
- Packet disallowed model: `qwen3.6:35b-a3b`
- Packet fallback: `qwen3.6:27b`
- Route execution allowed: `false`
- Production readiness: `false`

Proof artifact path:

`C:\Users\accou\AppData\Local\Temp\orchestrator_phase194_supervised_provider_call_tracer_30b_product_marker\phase_194_retry3_supervised_provider_call_tracer_30b_product_marker_proof.json`

## Retry History

- Initial Phase 194 provider call succeeded, but embedded Python proof artifact
  failed due to syntax error.
- Phase 194 Retry 1 failed because Python ran from the temp directory and
  could not import `orchestrator`.
- Phase 194 Retry 2 fixed `PYTHONPATH` but failed because
  `SupervisedProviderCallTracerReview` was serialized directly instead of via
  `.to_dict()`.
- Phase 194 Retry 3 succeeded by setting `PYTHONPATH`, using
  `review.to_dict()`, and asserting the actual classifier label.

Do not accept final PASS lines from the initial Phase 194 attempt, Retry 1, or
Retry 2 as classifier/proof-artifact acceptance. Only Retry 3 is accepted for
classifier/proof artifact backfill.

## GPU Caveat

Before the product marker call, GPU memory was already
`18302MiB / 24463MiB`, so the model was likely already resident from the
earlier 30B viability probe. Do not overclaim cold-load timing.

## Model Policy

- Active supervised provider-call tracer target:
  `qwen3:30b-a3b-instruct-2507-q4_K_M`
- Disallowed target: `qwen3.6:35b-a3b`
- Disallowed reason: Roger reported it locks up the laptop every time;
  installed inventory is not runtime suitability proof.
- Fallback candidate: `qwen3.6:27b`
- Practical policy: test 30B and below only; treat 35B as off-limits for this
  laptop target.

## Non-Proofs

Phase 194 proves captured product marker smoke only, and the classifier
explicitly says it does not authorize route execution.

Phase 194 does not prove:

- Route execution
- Live routing
- Worker dispatch
- `/api/chat`
- Semantic correctness
- Real workload sufficiency
- Long-context behavior
- Sustained-load stability
- Service/API/UI productization
- Production readiness
- Hermes/OpenClaw behavior from this product track

## Validation

- `git diff --check` - PASS

`PHASE194_SUPERVISED_PROVIDER_CALL_TRACER_30B_PRODUCT_MARKER_OPERATOR_PROOF=PASS_WITH_RETRY3_CLASSIFIER_ARTIFACT_BACKFILL`
