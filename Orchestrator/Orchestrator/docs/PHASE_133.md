# Phase 133 - Read-Only Local Model Metadata Probe Operator Proof

## Status

Operator-output proof accepted for registration.

Marker:

`PHASE133_READ_ONLY_LOCAL_MODEL_METADATA_PROBE_OPERATOR_PROOF=PASS`

## Registered Operator Probe

Roger ran a read-only local model metadata probe against:

`http://127.0.0.1:11434/api/show`

Registered probe facts:

- `PHASE133_BOUNDARY=PHASE133_READ_ONLY_LOCAL_MODEL_METADATA_PROBE_OPERATOR_PROOF`
- `PHASE133_URI=http://127.0.0.1:11434/api/show`
- `PHASE133_METHOD=POST`
- `PHASE133_MODEL_REQUESTED=qwen3-30b-24k:latest`
- `PHASE133_NON_PROOFS=no_generation,no_chat,no_route_execution,no_worker_dispatch,no_rag,no_web,no_scheduler,no_connector,no_hermes,no_openclaw,no_wsl,no_production_readiness`
- `PHASE133_REQUEST_SUCCEEDED=true`
- `PHASE133_STATUS_CODE=200`
- `PHASE133_CONTENT_TYPE=application/json; charset=utf-8`
- `PHASE133_RESPONSE_BYTES=70864`
- `PHASE133_MODIFIED_AT=2026-06-14T07:14:30.490610583-05:00`
- `PHASE133_DETAILS_FORMAT=gguf`
- `PHASE133_DETAILS_FAMILY=qwen3moe`
- `PHASE133_DETAILS_FAMILIES=qwen3moe`
- `PHASE133_DETAILS_PARAMETER_SIZE=30.5B`
- `PHASE133_DETAILS_QUANTIZATION_LEVEL=Q4_K_M`
- `PHASE133_MODEL_INFO_KEY_COUNT=31`
- `PHASE133_TEMPLATE_PRESENT=true`
- `PHASE133_PARAMETERS_PRESENT=true`
- `PHASE133_LICENSE_PRESENT=true`
- `PHASE133_OPERATOR_RESULT=PASS_CANDIDATE_READ_ONLY_METADATA_VISIBLE`

Registered model-info key sample:

`general.architecture,general.basename,general.file_type,general.finetune,general.parameter_count,general.quantization_version,general.size_label,general.type,general.version,qwen3moe.attention.head_count,qwen3moe.attention.head_count_kv,qwen3moe.attention.key_length,qwen3moe.attention.layer_norm_rms_epsilon,qwen3moe.attention.value_length,qwen3moe.block_count,qwen3moe.context_length,qwen3moe.embedding_length,qwen3moe.expert_count,qwen3moe.expert_feed_forward_length,qwen3moe.expert_used_count`

The pre/post git status showed the same existing Phase 132 docs mutation set,
with no new Phase 133 mutation caused by the probe.

## Accepted Meaning

The local Ollama provider surface exposed read-only metadata for
`qwen3-30b-24k:latest` at `/api/show` at that moment.

The visible metadata included GGUF format, Qwen3 MoE family, 30.5B parameter
size, Q4_K_M quantization, model-info metadata, template presence, parameter
presence, and license presence.

## Explicit Non-Proofs

This proof does not prove model generation, `/api/generate`, `/api/chat`,
semantic correctness, model loadability under generation, VRAM sufficiency,
route execution, Hermes behavior, OpenClaw behavior, WSL behavior, worker/Codex
dispatch from product code, RAG/local lookup, web lookup, scheduler/reminder
execution, connector execution, service/API/UI productization, or production
readiness.
