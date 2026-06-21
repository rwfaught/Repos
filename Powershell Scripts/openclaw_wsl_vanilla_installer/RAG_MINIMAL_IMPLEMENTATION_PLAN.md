# RAG Minimal Implementation Plan

## 1. Goal

Define the future minimal RAG implementation shape for the local-first Orchestrator/OpenClaw/Hermes track without performing implementation, indexing, model execution, or integration work.

The first implementation should be a standalone CLI-style RAG harness that produces retrieval-only evidence packets. It should prove whether metadata-governed retrieval can find and rank acceptable evidence before any generated answer path exists.

## 2. Non-Goals

- Do not integrate with OpenClaw, Hermes, or Discord yet.
- Do not use a generator model yet.
- Do not claim full RAG readiness.
- Do not claim generation quality.
- Do not claim production integration readiness.
- Do not claim OpenClaw readiness.
- Do not claim Hermes readiness.
- Do not claim Discord readiness.
- Do not index secrets, tokens, credentials, live `.env` values, private keys, or sensitive config.
- Do not create or require a vector database in this documentation-only boundary.

No indexing has been performed.

## 3. First Implementation Shape

The future MVP should be a standalone CLI-style RAG harness with explicit inputs, local corpus discovery, metadata assignment, embedding, local storage, retrieval, and evidence-packet output.

The harness should remain outside OpenClaw, Hermes, and Discord runtime flows until a later boundary explicitly authorizes integration.

The first CLI surface should support:

- selecting a docs-only corpus root;
- assigning required metadata to each accepted source or chunk;
- embedding eligible chunks only after metadata handling is validated;
- running retrieval-only queries;
- writing evidence packets that cite source paths, chunk identifiers, metadata, scores, and retrieval mode;
- failing closed when current canonical evidence is absent.

## 4. Recommended Storage Choice

Prefer SQLite plus simple local vector storage and brute-force cosine for the MVP unless a later boundary decides otherwise.

This keeps the first implementation auditable, dependency-light, and easy to inspect. Dedicated vector stores such as Chroma, Qdrant, FAISS, LanceDB, or DuckDB-backed layouts should remain deferred until the minimal retrieval contract is proven useful.

## 5. Minimal Corpus Policy

Start with a docs-only corpus.

Initial eligible sources should be durable project markdown documents that do not contain secrets or sensitive runtime configuration. Source selection should begin with package docs, ledgers, manifests, contracts, and accepted status reports.

The first corpus must exclude:

- secrets;
- tokens;
- credentials;
- live `.env` values;
- private keys;
- sensitive config;
- generated runtime logs unless explicitly approved by a later boundary.

## 6. Required Metadata Behavior

The implementation must be governed by `RAG_METADATA_SCHEMA_AND_RETRIEVAL_CONTRACT.md`.

Every indexed chunk must have enough metadata to decide whether it is eligible as current proof before semantic ranking is used. Current accepted-state answers must be grounded in eligible current canonical chunks, not merely high-similarity chunks.

Required metadata behavior includes:

- apply `status` before final proof selection;
- require `canonical = true` for current accepted-state proof;
- preserve `source_path`, `document_id`, `chunk_id`, `source_title`, `primary_track`, `source_tier`, `proof_state`, `effective_from`, `indexed_at`, and `schema_version`;
- exclude or separately quarantine chunks marked as secret-bearing or sensitive;
- fail closed when metadata cannot establish current canonical eligibility.

## 7. Initial Metadata Assignment Recommendations

Initial assignment should be conservative.

- Current durable package docs may be assigned `status = current` only for their documented scope.
- Benchmark ledgers should use `primary_track = benchmark` or `model_roster` depending on the dominant claim.
- Manifests should use `primary_track = config` or `platform` depending on the entry.
- Historical or superseded notes should not be marked current.
- Draft, proposed, or relay-only material should not be marked canonical current proof.
- Operator output should remain observed context until promoted into durable docs.

## 8. Query Intent Router

The first router should classify queries before retrieval mode selection.

Supported initial intents:

- `current accepted-state`;
- `historical/evolution`;
- `troubleshooting/debugging`;
- `design/research`;
- `code/config lookup`;
- prior-attempt questions.

The router should prefer explicit user wording first, then fallback to conservative current-state handling when ambiguous.

## 9. Retrieval Modes

Use `CURRENT_ONLY_FILTER` for current accepted-state questions.

Use `CURRENT_FIRST_RERANK` for history, evolution, troubleshooting, design, and prior-attempt questions.

`RAW_VECTOR_TOPK` is not the default and is never final proof for current accepted-state answers. It may be used only for discovery, ranking debugging, exploratory archive search, or benchmark comparison.

Use `bge-m3:latest` as the provisional embedding default only after metadata handling is validated.

## 10. Evidence Packet Output

The first output should be retrieval-only evidence packets, not generated answers.

Each evidence packet should include:

- query text;
- inferred query intent;
- selected retrieval mode;
- embedding model;
- corpus identifier;
- schema version;
- ranked evidence chunks;
- source paths and titles;
- chunk identifiers;
- metadata used for eligibility;
- similarity scores;
- rejection or exclusion reasons for stale, non-canonical, secret-bearing, or ineligible chunks;
- final retrieval-only verdict.

The packet should state whether current canonical evidence was found. It should not synthesize a final model-generated answer.

## 11. First Retrieval-Only Test Set

The first test set should be small and documentation-only.

It should include:

- current accepted-state questions;
- stale/current conflict questions;
- historical/evolution questions;
- troubleshooting questions;
- design or policy questions;
- prior-attempt questions;
- negative controls where no current canonical answer exists;
- secret-safety controls using synthetic placeholder names only.

The test set should verify retrieval behavior and caveat preservation, not generation quality.

## 12. Minimum Success Criterion

Minimum success requires the future harness to produce deterministic retrieval-only evidence packets showing that:

- current accepted-state questions use `CURRENT_ONLY_FILTER`;
- historical, evolution, troubleshooting, design, and prior-attempt questions use `CURRENT_FIRST_RERANK`;
- `RAW_VECTOR_TOPK` is not used as default or final proof for current accepted-state answers;
- stale or superseded chunks do not outrank current canonical chunks as proof;
- absence of current canonical evidence is reported explicitly;
- no secret-bearing or sensitive content is indexed into the ordinary corpus.

## 13. Failure Conditions

The future harness should fail the MVP if it:

- indexes secrets, tokens, credentials, live `.env` values, private keys, or sensitive config;
- uses raw vector similarity as final proof for current accepted-state answers;
- produces generated answers instead of retrieval-only evidence packets;
- treats historical, stale, superseded, draft, or proposed chunks as current proof;
- claims full RAG readiness;
- claims generation quality;
- claims production integration readiness;
- claims OpenClaw readiness;
- claims Hermes readiness;
- claims Discord readiness;
- integrates with OpenClaw, Hermes, or Discord before a later boundary authorizes it.

## 14. Recommended Future File Surface

A later implementation boundary may choose exact paths. A minimal future file surface could include:

- `rag_harness/cli.py` or equivalent standalone CLI entrypoint;
- `rag_harness/metadata.py` for schema validation and assignment;
- `rag_harness/chunking.py` for document chunking;
- `rag_harness/embed.py` for embedding calls;
- `rag_harness/store.py` for SQLite plus local vector storage;
- `rag_harness/retrieve.py` for retrieval modes;
- `rag_harness/evidence_packet.py` for structured packet output;
- `rag_harness/tests/` for retrieval-only test fixtures.

This list is advisory only and does not authorize code creation in this boundary.

## 15. Open Threads And Caveats

- No indexing has been performed.
- Existing RAG evidence is docs/policy-only.
- No actual RAG implementation exists.
- No generation quality has been tested.
- No OpenClaw/Hermes/Discord/RAG integration has been tested.
- No full RAG readiness is claimed.
- No production integration readiness is claimed.
- Storage choice remains provisional until a later implementation boundary.
- Corpus promotion rules still need an accepted durable policy.
- Secret-safe indexing behavior must be proven before any non-toy corpus is used.
- The first non-toy retrieval test set still needs to be defined.
