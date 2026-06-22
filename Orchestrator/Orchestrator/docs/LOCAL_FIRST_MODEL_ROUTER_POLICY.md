# Local-First Model Router Policy

## Purpose

The local-first model/router policy is a deterministic, non-executing contract
for recommending boundary posture from structured request metadata. It helps
decide whether a request should stay local-first, require frontier/provider
review under a separate boundary, move to a worker/Codex boundary, move to
RAG/local-document lookup, move to scheduler/reminder handling, move to
web/research handling, or block/clarify.

The policy does not execute providers, models, workers, RAG, web lookup,
schedulers, connectors, runtimes, platforms, or production behavior.

Phase 125 adds `docs/LOCAL_FIRST_PROVIDER_CATALOG.md` and
`orchestrator/model_provider_catalog.py` as the provider-tier catalog behind
these posture strings. The catalog makes local-first, frontier, worker, RAG,
scheduler, web, and blocked-provider boundaries inspectable, but it does not
turn the router policy into live provider/model selection or execution.

## Recommendation Fields

Each recommendation records:

- `request_id`
- `recommended_route`
- `provider_posture`
- `confidence`
- `reason`
- `fallback`
- `escalation_posture`
- `required_boundary`
- `blocked_conditions`
- `missing_requirements`
- `non_proofs`
- `activity_flags`

## Route Outcomes

- `local_first_answer`: low-risk answer/report posture may stay local-first
  when direct answer is explicitly allowed and no missing/high-risk/retrieval
  condition blocks it.
- `worker_codex_boundary`: coding and file-mutation routes require a bounded
  worker/Codex boundary; this is not dispatch.
- `rag_local_document_boundary`: local-document lookup routes require a
  RAG/local-document boundary; this is not lookup.
- `scheduler_reminder_boundary`: reminder routes require scheduler/reminder
  confirmation and boundary; this is not scheduling.
- `web_research_boundary`: research routes require explicit web/research
  boundary; this is not browsing.
- `separate_provider_or_platform_boundary_required`: provider/model and
  platform/runtime capabilities require separate authority.
- `block`: production execution is blocked unless a future explicit production
  boundary authorizes it.
- `ask_clarification`: missing or invalid request type, confidence, or
  capability authority must be clarified before routing.

## Escalation Posture

Escalation is posture only. Frontier/provider review may be recommended only
as a separately authorized boundary and never as implicit provider/model
execution. Coding/file work moves to a worker boundary only as a required
boundary recommendation; the policy does not dispatch a worker or invoke Codex.

Provider catalog entries distinguish local-first preference, actual
provider/model execution authority, frontier escalation authority, worker/Codex
dispatch authority, and RAG/web/scheduler boundary authority. All catalog
execution and activity flags remain false.

## Non-Proofs

The policy preserves non-proofs including:

- `router_policy_is_not_provider_execution`
- `router_policy_is_not_model_execution`
- `router_policy_is_not_live_router`
- `router_policy_is_not_worker_dispatch`
- `router_policy_is_not_route_execution`
- `router_policy_is_not_rag_lookup`
- `router_policy_is_not_web_lookup`
- `router_policy_is_not_scheduler_execution`
- `router_policy_is_not_production_readiness`

All no-activity flags remain false.

## Relationship To Intake Routing

This policy sits after structured request intake and route validation doctrine.
It does not infer raw natural-language intent, validate route envelopes, admit
execution, select providers/models/runtimes/platforms, or override capability
registry maturity. It uses structured route/request metadata as evidence for a
recommended next boundary only.

Phase 122 defines the router policy contract, Phase 123 renders it in manual
review reports, Phase 124 repairs the validation-command mismatch, and Phase
125 adds a non-executing provider catalog to make provider-tier posture
auditable before any future provider/runtime proof boundary.

Phase 126 enriches each router recommendation with a provider-catalog-backed
envelope: catalog key, tier, maturity status, allowed boundary, required
authority, execution and selection flags, catalog fallback, catalog escalation
posture, catalog non-proofs, and catalog activity flags. These fields remain
non-executing policy evidence and do not select or run a provider, model,
runtime, platform, worker, route, lookup, scheduler, connector, or production
task.

Phase 127 adds a provider/runtime probe boundary packet draft contract. It can
turn an eligible router/provider recommendation envelope into future-boundary
paperwork that describes authorization, scope, expected evidence, exclusions,
and stop conditions for a later probe. It does not perform provider/runtime
imports, probes, availability checks, execution, route execution, or production
work.

Phase 128 surfaces provider probe packet status in manual review reports. The
status is blocked by default unless explicit deterministic authorization,
scope, and expected evidence are supplied. This visibility does not authorize
or execute a probe.

Phase 129 adds explicit manual review CLI flags for requesting provider probe
packet paperwork. The flags only pass deterministic metadata into manual
review; they do not authorize execution, import providers, check availability,
select models for execution, execute routes, or prove production readiness.

Phase 130 registers accepted operator output for that CLI paperwork path with
an exit-code caveat. Phase 131 registers a separate read-only local Ollama
`/api/tags` availability proof. That proof means provider surface/model-list
visibility only; it does not prove generation, chat, model correctness,
loadability, route execution, or production readiness.

Phase 133 registers an accepted operator proof for read-only local Ollama
`/api/show` metadata visibility for `qwen3-30b-24k:latest`. The visible
metadata included GGUF, Qwen3 MoE, 30.5B, Q4_K_M, model-info metadata,
template, parameters, and license presence. Phase 134 registers that proof in
source docs/ledgers without rerunning it. Metadata visibility remains evidence
only; it is not generation, `/api/generate`, `/api/chat`, semantic correctness,
model loadability, VRAM sufficiency, provider/model execution, route
execution, worker dispatch, RAG/web/scheduler/connector work, or production
readiness.

Phase 143 adds a deterministic provider evidence registry and renders
registered provider evidence in manual review output. This evidence does not
change router recommendations, provider execution authority, provider
selection authority, runtime selection, route execution, or production
readiness.

Phase 146 adds provider evidence posture to the router recommendation envelope
itself. For `local_model_candidate`, the envelope may include read-only
evidence status, evidence keys/source phases, and model metadata fields. This
is not provider/model execution, model generation, live routing, route
execution, provider selection, or production readiness.

Phase 149 adds an evidence-gated route-selection readiness layer that consumes
the recommendation envelope and reports what remains blocked. For
`local_model_candidate` with read-only metadata evidence, readiness is
`blocked_pending_generation_probe_boundary` and `not_ready_for_execution`; the
named next proof boundary is a future bounded generation smoke probe. This
layer does not select a provider/model, execute generation, execute a route, or
prove production readiness.

Phase 152 adds a deterministic future provider generation smoke probe packet
for that readiness boundary. The packet may name `POST /api/generate` as a
future endpoint shape and a local model candidate, but
it does not execute the endpoint, generate output, select a provider/model, or
prove route execution or production readiness.

Phase 156 retargets the active future generation smoke probe packet to
`qwen3.6:27b` after accepted 30b/24k CUDA OOM evidence. Phase 160 registers
accepted Phase 159 Retry 1 `qwen3.6:27b` `/api/generate` marker smoke evidence
for the exact accepted request only. Route-selection readiness can now treat
the generation-smoke gate as satisfied. Phase 163 registers accepted Phase 162
`qwen3.6:27b` `/api/show` metadata visibility, so the prior 27b metadata
blocker is satisfied and readiness moves to a conservative future-probe-ready
posture for a bounded route-selection readiness/recommendation-envelope
review. Provider selection, provider execution, generation-now, route
execution, and production readiness remain false.
