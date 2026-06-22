# Provider Evidence Registry

## Purpose

The provider evidence registry is a deterministic, non-executing source record
for accepted read-only provider/model evidence. It lets coordinator/manual
review reports display known evidence posture without probing providers,
calling models, selecting runtimes, dispatching workers, executing routes, or
claiming production readiness.

## Registered Evidence

Phase 131 provider-surface visibility:

- Provider catalog key: `local_model_candidate`
- Evidence kind: `provider_surface_model_list_visibility`
- Evidence status: `read_only_provider_surface_visible`
- Surface: `http://127.0.0.1:11434/api/tags`
- Method: `GET`
- Status: `200`
- Model count: `9`
- Accepted meaning: read-only provider-surface model-list visibility existed
  at that moment.

Phase 133 model metadata visibility:

- Provider catalog key: `local_model_candidate`
- Evidence kind: `model_metadata_visibility`
- Evidence status: `read_only_metadata_visible`
- Surface: `http://127.0.0.1:11434/api/show`
- Method: `POST`
- Model: `qwen3-30b-24k:latest`
- Status: `200`
- Metadata: GGUF, Qwen3 MoE, 30.5B, Q4_K_M, model-info metadata, template
  presence, parameter presence, and license presence.
- Accepted meaning: read-only model metadata visibility existed for
  `qwen3-30b-24k:latest` at that moment.

Phase 159 Retry 1 generation-smoke marker evidence:

- Provider catalog key: `local_model_candidate`
- Evidence kind: `model_generation_smoke_marker`
- Evidence status: `accepted_generation_smoke_marker_visible`
- Surface: `http://127.0.0.1:11434/api/generate`
- Method: `POST`
- Model: `qwen3.6:27b`
- Status: `200`
- Metadata: `num_predict=96`, JSON parse success, returned model
  `qwen3.6:27b`, response field `ORCH_PROVIDER_SMOKE_OK`, `done=true`, and
  `done_reason=stop`.
- Accepted meaning: bounded generation-smoke marker evidence existed for the
  exact accepted Phase 159 Retry 1 request.
- Preserved caveats: the earlier Phase 159 initial failure was a token-budget/
  probe-shape failure; Phase 155 Retry 3 was a 30b/24k CUDA OOM failure, not a
  27b failure.

Phase 162 qwen3.6 27B model metadata visibility:

- Provider catalog key: `local_model_candidate`
- Evidence kind: `model_metadata_visibility`
- Evidence status: `read_only_metadata_visible`
- Surface: `http://127.0.0.1:11434/api/show`
- Method: `POST`
- Model: `qwen3.6:27b`
- Status: `200`
- Metadata: visible details, license text presence, tensor/model metadata,
  capabilities `completion`, `vision`, `tools`, and `thinking`, and
  `modified_at` presence.
- Unknown fields: family, parameter size, and quantization are
  `unknown_not_recorded`; they are not guessed from the large raw body.
- Accepted meaning: read-only `/api/show` metadata visibility existed for
  `qwen3.6:27b` at that moment.

## Relationship To Router And Reports

The registry is evidence posture only. Router/provider catalog policy remains
conservative: provider execution and provider selection remain false. Manual
review output may render a `Provider Evidence` section, but that section is not
probe authorization, model generation, model correctness, model loadability,
route execution, or production readiness.

Phase 146 feeds the same registry evidence into the router/provider
recommendation envelope as deterministic policy data. A `local_model_candidate`
recommendation may carry provider evidence status, evidence keys, source
phases, model metadata fields, evidence non-proofs, and evidence activity
flags. These fields are evidence posture only and do not grant execution
authority, provider/model selection authority, route execution authority, or
production readiness.

Phase 149 allows registry evidence to feed route-selection readiness posture.
That readiness posture may name the next required proof boundary, but evidence
does not grant provider/model execution authority, model generation authority,
route execution authority, or production readiness.

Phase 160 allows readiness to treat the exact accepted 27b generation-smoke
evidence gate as satisfied. Phase 163 allows readiness to treat the accepted
`qwen3.6:27b` `/api/show` metadata evidence gate as satisfied. Readiness moves
to a conservative future-probe-ready posture for a bounded route-selection
readiness/recommendation-envelope review, while all execution authorities
remain false.

## Non-Proofs

The registry does not prove provider/model/runtime execution, `/api/chat`,
semantic correctness, model loadability for real workloads, VRAM sufficiency
for real workloads, route execution, worker dispatch, RAG/local lookup, web
lookup, scheduler/reminder execution, connector execution, service/API/UI
productization, production execution, or production readiness. The Phase 159
Retry 1 record proves only the exact accepted smoke request.
