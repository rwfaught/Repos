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

## Non-Proofs

The catalog explicitly does not prove provider/model execution,
runtime/platform execution, worker/Codex dispatch, RAG/local-document lookup,
web lookup, scheduler/reminder execution, connector execution, route execution,
or production readiness. All execution and activity flags remain false.
