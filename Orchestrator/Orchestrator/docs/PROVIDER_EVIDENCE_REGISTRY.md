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

## Non-Proofs

The registry does not prove provider/model/runtime execution, model
generation, `/api/generate`, `/api/chat`, semantic correctness, model
loadability, VRAM sufficiency, route execution, worker dispatch, RAG/local
lookup, web lookup, scheduler/reminder execution, connector execution,
service/API/UI productization, production execution, or production readiness.
