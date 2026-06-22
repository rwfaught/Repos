# Local-First Provider Catalog

## Purpose

The local-first provider catalog is a deterministic, non-executing policy
matrix for provider-tier posture and escalation authority. It supports future
model/router decisions by making local-first, frontier, worker, RAG, scheduler,
web, and blocked-provider boundaries inspectable without executing any
provider, model, runtime, worker, connector, lookup, scheduler, or production
work.

## Catalog Entries

The Phase 125 catalog defines:

- `local_model_candidate`
- `frontier_provider_candidate`
- `worker_codex_boundary`
- `rag_local_document_boundary`
- `scheduler_reminder_boundary`
- `web_research_boundary`
- `provider_blocked_or_unavailable`

Each entry records `provider_key`, `provider_tier`, `maturity_status`,
`allowed_boundary`, `execution_allowed`, `selection_allowed`, `fallback`,
`escalation_posture`, `required_authority`, `non_proofs`, `activity_flags`,
and `provider_posture`.

## Authority Rules

Local-first preference is not provider/model execution authority. A local model
candidate requires a future explicit provider/model boundary before execution.

Frontier escalation is not provider/model execution authority. A frontier
candidate requires an explicit frontier/provider escalation boundary before any
provider can be selected or invoked.

Worker/Codex posture is not dispatch. It only identifies that a bounded worker
boundary would be required before any downstream worker work.

RAG/local-document lookup, scheduler/reminder handling, and web/research each
require their own explicit boundaries and do not execute through this catalog.

Provider blocked/unavailable posture is not evidence that a provider is absent
or present; it is a conservative fallback until a future boundary and fresh
proof authorize more.

## Relationship To Prior Phases

Phase 122 created the deterministic local-first model/router policy contract.
Phase 125 adds an inspectable provider-tier catalog behind that posture without
changing the router into live provider/model selection.

Phase 123 rendered router policy posture in manual review reports. The catalog
can explain those posture strings, but rendered report text remains
coordinator-facing evidence only.

Phase 124 repaired validation-command compatibility for the Phase 120
entrypoint smoke test. Phase 125 preserves that proof-hygiene result and adds
new catalog coverage only.

Future provider/runtime proof must happen under a separate boundary. This
catalog does not import provider runtime modules or prove provider/model,
runtime, platform, worker, RAG, web, scheduler, connector, route, or production
execution.

## Router Recommendation Envelope

Phase 126 derives structured router/provider recommendation fields from the
catalog. The router envelope includes the selected catalog key, tier, maturity
status, allowed boundary, required authority, execution and selection flags,
catalog fallback, catalog escalation posture, catalog non-proofs, and catalog
activity flags.

The selected catalog key is a policy posture key only. It is not concrete
provider/model/runtime/platform selection, availability proof, route execution,
or production readiness.

## Probe Boundary Packet Airlock

Phase 127 adds `docs/PROVIDER_PROBE_BOUNDARY_PACKET.md` and
`orchestrator/provider_probe_boundary_packet.py` as the future probe-boundary
airlock. The packet draft consumes eligible provider-catalog-backed router
recommendations and records what a later explicitly authorized probe boundary
would need to define.

The airlock does not import providers, probe availability, execute models,
dispatch workers, perform RAG/web/scheduler/connector work, execute routes, or
prove production readiness.

Phase 128 exposes this airlock status in manual review artifacts. The report
may show that probe paperwork is blocked, missing requirements, awaiting
authorization, or draftable through an explicit deterministic path. It still
does not prove provider availability, model availability, runtime import,
execution, route execution, or production readiness.

Phase 129 exposes the same paperwork-only path through explicit manual review
CLI flags. CLI visibility does not convert catalog posture into provider
availability, provider/model/runtime selection, route execution, or production
readiness.

Phase 130 registers operator proof that the CLI paperwork path rendered the
expected local model candidate metadata, with the command exit code caveat
preserved. Phase 131 registers read-only `/api/tags` visibility for the local
Ollama provider surface and nine model names. The catalog interpretation
remains conservative: list visibility is not model execution, model
correctness, model loadability, route execution, mutation authority, or
production readiness.

Phase 133 registers read-only `/api/show` metadata visibility for
`qwen3-30b-24k:latest`: GGUF, Qwen3 MoE, 30.5B, Q4_K_M, model-info metadata,
template, parameters, and license presence. Phase 134 registers that accepted
operator proof in source docs/ledgers without rerunning it. Catalog posture
remains conservative: metadata visibility is not generation, chat, semantic
correctness, model loadability, VRAM sufficiency, provider/model/runtime
execution, route execution, mutation authority, or production readiness.

Phase 143 adds a provider evidence registry for accepted Phase 131 and Phase
133 read-only visibility proofs. Catalog posture remains conservative:
evidence visibility does not flip `execution_allowed` or `selection_allowed`
to true and does not prove provider/model/runtime execution, route execution,
or production readiness.

## Non-Proofs

The catalog explicitly does not prove provider/model execution,
runtime/platform execution, worker/Codex dispatch, RAG/local-document lookup,
web lookup, scheduler/reminder execution, connector execution, route execution,
or production readiness. All execution and activity flags remain false.
