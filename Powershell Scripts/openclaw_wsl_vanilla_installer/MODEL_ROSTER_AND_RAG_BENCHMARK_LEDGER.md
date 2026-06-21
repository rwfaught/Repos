# Model Roster And RAG Benchmark Ledger

## Scope

This ledger records accepted model acquisition and RAG embedding benchmark state for the local-first Orchestrator/OpenClaw/Hermes track. It is documentation-only and does not prove full runtime, integration, generation, OpenClaw, Hermes, or Discord readiness.

## Accepted Status

### Embedding Acquisition

| Model | Status | Proof State | Result |
|---|---|---|---|
| `nomic-embed-text-v2-moe:latest` | Acquired | Show verified | PASS |
| `bge-m3:latest` | Acquired | Show verified | PASS |
| `qwen3-embedding:0.6b` | Not present | Deferred as intended | Deferred |

Red `NativeCommandError`-looking output during pull was classified as a capture/logging artifact because final proof showed success and `LASTEXITCODE: 0`.

### Qwen3.6

| Item | Status |
|---|---|
| `qwen3.6:35b-a3b` acquisition | PASS |
| Isolated runtime smoke | PASS WITH CAVEATS |
| Caveat | High VRAM pressure on a 24 GB GPU |
| OpenClaw/Hermes/Discord readiness | NOT TESTED |

### RAG Embedding Benchmark V1

Execution: PASS.

Default model: NOT SELECTED.

| Model | Top-1 | Top-3 | Protocol Top-3 | Dangerous false positives | Latency |
|---|---:|---:|---:|---:|---|
| `nomic-embed-text-v2-moe:latest` | 11/18 | 17/18 | 3/3 | 1 | Yellow |
| `bge-m3:latest` | 13/18 | 16/18 | 3/3 | 2 | Green |

Key finding: both models showed stale/current retrieval weakness.

### RAG Embedding Benchmark V2

Execution: PASS.

Corpus: synthetic/sanitized toy corpus only.

Docs/chunks: 24.

Queries: 30.

Modes tested:

- `RAW_VECTOR_TOPK`
- `CURRENT_ONLY_FILTER`
- `CURRENT_FIRST_RERANK`

Key finding: metadata-aware retrieval fixed the Q13-like stale/current failure class.

Safest mode: `CURRENT_ONLY_FILTER`.

Stronger model after metadata handling: `bge-m3:latest`.

Provisional default is possible only after metadata handling.

V2 does not prove full RAG readiness, does not test generation quality, and does not test OpenClaw, Hermes, Discord, Qwen3.6, or production integration.

## Provisional Policy

- Default embedding model for first local Orchestrator/RAG experiments: `bge-m3:latest`.
- Default retrieval policy for current accepted-state questions: `CURRENT_ONLY_FILTER`.
- Use `CURRENT_FIRST_RERANK` for history, evolution, or prior-attempt questions where historical notes may be useful but must not outrank current canonical notes.
- Do not use raw vector Top-K as the Orchestrator default.

Retrieval policy and metadata schema are governed by `RAG_METADATA_SCHEMA_AND_RETRIEVAL_CONTRACT.md`.

## Open Threads

- Full RAG readiness remains unproven.
- Generation quality remains untested.
- OpenClaw, Hermes, Discord, Qwen3.6, and production integration remain untested for this benchmark policy.
- `qwen3-embedding:0.6b` remains intentionally deferred and not present.
