# RAG Metadata Schema And Retrieval Contract

## 1. Purpose

This document records the accepted metadata schema and retrieval policy contract for first local Orchestrator/RAG experiments in the OpenClaw/Hermes project track. It is derived from the accepted RAG Embedding Benchmark V2 findings and is documentation-only.

This contract does not prove full RAG readiness, generation quality, OpenClaw readiness, Hermes readiness, Discord readiness, Qwen3.6 readiness, or production integration readiness.

## 2. Accepted Benchmark Basis

The accepted benchmark basis is recorded in `MODEL_ROSTER_AND_RAG_BENCHMARK_LEDGER.md`.

`RAG_MINIMAL_IMPLEMENTATION_PLAN.md` defines the future minimal implementation shape governed by this metadata and retrieval contract.

Accepted embedding acquisition state:

- `nomic-embed-text-v2-moe:latest` is ACQUIRED / SHOW VERIFIED / PASS.
- `bge-m3:latest` is ACQUIRED / SHOW VERIFIED / PASS.
- `qwen3-embedding:0.6b` is NOT PRESENT / DEFERRED AS INTENDED.
- Red `NativeCommandError`-looking pull output was classified as a capture/logging artifact because final proof showed success and `LASTEXITCODE: 0`.

Accepted Qwen3.6 state:

- `qwen3.6:35b-a3b` acquisition: PASS.
- Isolated runtime smoke: PASS WITH CAVEATS.
- Caveat: high VRAM pressure on 24 GB GPU.
- OpenClaw/Hermes/Discord readiness: NOT TESTED.

Accepted RAG Embedding Benchmark V1 state:

- Execution: PASS.
- Default model: NOT SELECTED.
- `nomic-embed-text-v2-moe:latest`: Top-1 11/18, Top-3 17/18, Protocol Top-3 3/3, dangerous false positives 1, latency Yellow.
- `bge-m3:latest`: Top-1 13/18, Top-3 16/18, Protocol Top-3 3/3, dangerous false positives 2, latency Green.
- V1 key finding: both models showed stale/current retrieval weakness.

Accepted RAG Embedding Benchmark V2 state:

- Execution: PASS.
- Corpus: synthetic/sanitized toy corpus only.
- Docs/chunks: 24.
- Queries: 30.
- Retrieval modes tested: `RAW_VECTOR_TOPK`, `CURRENT_ONLY_FILTER`, and `CURRENT_FIRST_RERANK`.
- V2 key finding: metadata-aware retrieval fixed the Q13-like stale/current failure class.
- Safest mode: `CURRENT_ONLY_FILTER`.
- Stronger model after metadata handling: `bge-m3:latest`.
- Provisional default possible only after metadata handling.
- V2 does not prove full RAG readiness.
- V2 does not test generation quality.
- V2 does not test OpenClaw, Hermes, Discord, Qwen3.6, or production integration.

Current provisional policy:

- Default embedding model for first local Orchestrator/RAG experiments: `bge-m3:latest`.
- Default retrieval policy for current accepted-state questions: `CURRENT_ONLY_FILTER`.
- Use `CURRENT_FIRST_RERANK` for history, evolution, troubleshooting, or prior-attempt questions where historical notes may be useful but must not outrank current canonical notes.
- Do not use raw vector Top-K as the Orchestrator default.

## 3. Core Retrieval Principle

Current accepted-state answers must be grounded in eligible current canonical chunks, not merely in semantically similar chunks. Metadata must control eligibility before ranking is allowed to support a current-state claim.

Semantic similarity is useful for discovery and ranking, but it is not proof that a chunk is current, canonical, accepted, or safe to use as final support.

## 4. Minimal Metadata Schema

Each indexed chunk should carry enough metadata to answer these questions before the chunk is used as proof:

- What source produced this chunk?
- Which project track does it belong to?
- Is it current, stale, superseded, historical, or draft/proposed?
- Is it canonical for the question being answered?
- What proof state supports it?
- When did it become effective and when was it indexed?
- Which schema version shaped the metadata?

The minimum schema is the required field set in this document. Optional fields may be added for better routing, supersession handling, redaction, confidence tracking, and auditability.

## 5. Required Fields

| Field | Requirement |
|---|---|
| `chunk_id` | Stable unique identifier for the indexed chunk. |
| `document_id` | Stable identifier for the parent document. |
| `source_path` | Repo/package path, durable artifact path, or accepted source locator. |
| `source_title` | Human-readable source title. |
| `primary_track` | Main track from the track taxonomy. |
| `status` | Currentness status from the status taxonomy. |
| `canonical` | Boolean indicating whether the chunk is eligible as canonical support within its track and scope. |
| `source_tier` | Source authority tier used by the canonical source policy. |
| `proof_state` | Proof posture, such as accepted, observed, proposed, untested, or superseded. |
| `effective_from` | Date or timestamp when the fact became effective, if known. |
| `indexed_at` | Date or timestamp when the chunk was indexed. |
| `schema_version` | Metadata schema version applied to this chunk. |

## 6. Optional Fields

| Field | Use |
|---|---|
| `secondary_tracks` | Additional track tags that may help routing. |
| `subject_keys` | Stable subject identifiers, model names, phase names, package names, or feature keys. |
| `phase_id` | Phase or milestone identifier when applicable. |
| `boundary_id` | Work boundary or execution boundary identifier when applicable. |
| `supersedes` | Prior chunk, document, or claim replaced by this chunk. |
| `superseded_by` | Later chunk, document, or claim that replaces this chunk. |
| `valid_until` | Date or timestamp after which the chunk should not be treated as current. |
| `confidence` | Confidence marker or score supplied by the indexing process or operator. |
| `contains_secret` | Boolean marker for secret-bearing or sensitive content. |
| `redaction_status` | Redaction state, such as not_needed, redacted, pending_review, or excluded. |
| `document_kind` | Document type, such as ledger, manifest, report, contract, prompt, source, config, or external reference. |
| `notes` | Short operator or indexer notes. |

## 7. Status Taxonomy

Allowed `status` values:

- `current`: Accepted as current for its documented scope.
- `stale`: Known to be outdated or no longer reliable for current-state answers.
- `superseded`: Replaced by a later accepted source or claim.
- `historical`: Retained for history, evolution, audit, or troubleshooting context.
- `draft_proposed`: Proposed, draft, or not yet accepted as durable current policy.

Stale, superseded, historical, and draft/proposed chunks must not be used as current proof.

## 8. Canonical Source Policy

Source authority order for current accepted-state answers:

- Current canonical repo/package docs outrank stale docs.
- Fresh operator output may be temporary observed proof but should be promoted into durable docs when stable.
- Accepted boundary facts may orient but should become durable docs when stable.
- Handoff prompts are session-transfer aids, not permanent canonical proof unless incorporated into durable docs.
- Conversation memory is background only and is never proof.
- External references are non-authoritative unless explicitly accepted for an external research task.

For current accepted-state answers, the retriever must prefer chunks where `status` is `current`, `canonical` is true, and `source_tier` is compatible with durable project proof.

## 9. Track Taxonomy

Allowed `primary_track` values:

- `product`
- `platform`
- `model_roster`
- `workflow`
- `config`
- `benchmark`

Use `secondary_tracks` when a chunk legitimately crosses tracks, but keep `primary_track` to one dominant value for routing.

## 10. Query Intent Classes

Supported query intent classes:

- `current accepted-state`
- `historical/evolution`
- `troubleshooting/debugging`
- `design/research`
- `code/config lookup`

Prior-attempt questions should route with historical/evolution or troubleshooting/debugging behavior, depending on whether the user is asking for timeline context or failure analysis.

## 11. Retrieval Policy Routing

| Query intent | Default retrieval mode | Rule |
|---|---|---|
| `current accepted-state` | `CURRENT_ONLY_FILTER` | Filter to eligible current canonical chunks before ranking. |
| `historical/evolution` | `CURRENT_FIRST_RERANK` | Prefer current canonical chunks, then allow historical context after current state is established. |
| `troubleshooting/debugging` | `CURRENT_FIRST_RERANK` | Prefer current canonical chunks while allowing historical failures, caveats, and prior attempts to assist diagnosis. |
| `design/research` | `CURRENT_FIRST_RERANK` | Prefer current accepted constraints while allowing research notes and alternatives as non-proof context. |
| `code/config lookup` | `CURRENT_FIRST_RERANK` | Prefer current source/config references and allow history only as context. |
| Prior-attempt questions | `CURRENT_FIRST_RERANK` | Historical notes may be useful but must not outrank current canonical notes. |

If no eligible current canonical chunk exists for a current accepted-state question, the system should say the answer is not proven in current canonical sources rather than falling back to stale semantic similarity.

## 12. Raw Vector Retrieval Rule

Raw vector retrieval is not allowed as an Orchestrator default.

Raw vector retrieval is allowed only for:

- Discovery.
- Debugging ranking behavior.
- Exploratory archive search.
- Benchmark comparison.

Raw vector retrieval must never be used as final proof for current accepted-state answers.

## 13. Safety / Caveat Rules

- No secrets, tokens, credentials, private keys, live `.env` values, or sensitive config should be indexed into ordinary RAG.
- Stale, superseded, historical, and draft/proposed chunks must not be used as current proof.
- Benchmark results do not prove full RAG readiness.
- Retrieval-only benchmark results do not prove generation quality.
- V2 does not prove OpenClaw, Hermes, Discord, Qwen3.6, or production integration readiness.
- If no eligible current canonical chunk exists, the system should say the answer is not proven in current canonical sources rather than falling back to stale semantic similarity.

## 14. Non-Proofs

This contract does not prove:

- Full RAG readiness.
- Generation quality.
- Production integration readiness.
- OpenClaw readiness.
- Hermes readiness.
- Discord readiness.
- Qwen3.6 readiness.
- Model serving stability under real workload.
- Corpus quality beyond the synthetic/sanitized toy corpus used in Benchmark V2.
- Secret-safe indexing coverage for future corpora.

## 15. Open Threads

- Define exact accepted values for `source_tier` and `proof_state`.
- Define the first production schema version identifier for `schema_version`.
- Decide whether `contains_secret = true` chunks are excluded from ordinary indexes or routed to a separate restricted index.
- Define promotion rules for fresh operator output into durable docs.
- Validate this contract against a non-toy corpus before claiming broader RAG readiness.
- Test generation quality separately before using retrieval results to claim answer quality.
