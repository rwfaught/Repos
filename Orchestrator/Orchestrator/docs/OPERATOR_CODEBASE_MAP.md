# Operator Codebase Map

Boundary: `FOUNDER_CONTROL_AND_SOURCE_REALITY_DOCS_ONLY`

Status: founder/operator orientation map.

Marker: `OPERATOR_CODEBASE_MAP_REGISTERED=DOCS_ONLY`

## Executive Summary

The repo has three broad layers Roger should keep distinct:

1. the engine skeleton that handles tasks, state, artifacts, and verification
2. the builder/control machinery used to safely build Orchestrator itself
3. the early product substrate around case-like work

The strongest current user-understandable capability is still the bounded
coding-task packet path. The case-packet substrate is important but early. The
largest black-box zone is the recent product-task packet governance/readback
chain.

## Map of Major Areas

### `docs/`

Role: project control room.

This is where the project records vision, current success criteria, startup
rules, phase history, source manifest, strategy/design direction, open threads,
and proof caveats.

Roger should understand:

- `PROJECT_VISION.md`
- `CURRENT_SUCCESS_CRITERION.md`
- `STARTUP_BRIEF.md`
- `TRACKS_AND_OPEN_THREADS.md`
- `CONTEXT_MAP.md`
- `CAPABILITY_REALITY_MAP.md`
- `DOMAIN_LOCK_IN_AUDIT.md`
- `FIRST_PRODUCT_WEDGE_DECISION.md`

Can remain implementation detail:

- individual historical phase docs unless a current boundary needs them
- low-level test/source manifest details except when proof is disputed

### Core Execution / State Skeleton

Representative files:

- `orchestrator/engine.py`
- `orchestrator/run_manager.py`
- `orchestrator/state.py`
- `orchestrator/artifact_store.py`
- `orchestrator/task_schema.py`
- `orchestrator/paths.py`

Role:

This is the basic machinery for receiving bounded work, preserving state,
storing artifacts, and reporting task outcomes.

Roger should understand:

A task enters the system under a boundary. The system records state and
artifacts. Verification/readback surfaces describe what happened and what was
not proven.

Can remain implementation detail:

Exact Python functions, dataclass shapes, and internal path handling unless a
bug or refactor touches them.

### Operator Coding-Task Packet Path

Representative files:

- `orchestrator/operator_coding_task_packet.py`
- `orchestrator/operator_coding_task_packet_cli.py`
- `orchestrator/operator_packet_result_decision.py`
- `orchestrator/packet_cli_residue_guard.py`

Role:

This is the clearest current work path. A bounded coding task is shaped into a
packet, processed through controlled surfaces, and returned with artifacts,
checks, readbacks, and operator-visible decisions.

Roger should understand:

This is the strongest proven spine. It proves controlled bounded work better
than it proves general product usefulness.

### Patch / Apply / Verification Machinery

Representative files:

- `orchestrator/patch_proposal.py`
- `orchestrator/patch_apply_engine.py`
- `orchestrator/patch_apply_authorization.py`
- `orchestrator/authorized_draft_patch_apply.py`
- `orchestrator/verified_patch_apply_task_*.py`

Role:

This layer governs safe code mutation: proposal, authorization, apply, verify,
finalize.

Roger should understand:

This is build-system safety machinery. It matters because Orchestrator is being
built through AI-assisted code changes, but it is not the final product surface.

### Case-Packet Substrate

Representative files:

- `orchestrator/case_packet.py`
- `orchestrator/case_packet_persistence.py`
- `orchestrator/case_packet_task_candidate_review.py`
- `orchestrator/case_packet_task_creation_authorization.py`
- `orchestrator/case_packet_task_creation_write_gate.py`
- `orchestrator/case_packet_task_execution_authorization.py`
- `orchestrator/case_packet_task_execution_candidate_surface.py`
- `orchestrator/case_packet_task_execution_result_review.py`
- `orchestrator/case_packet_task_execution_result_response_options.py`

Role:

This is the early product substrate for case-like work: objectives, materials,
facts, timelines, open issues, contradictions, drafts, and decisions.

Roger should understand:

The substrate exists, but it is not yet a competent claims/disputes/appeals
worker. It may be reusable as a dossier substrate.

### Product-Task Packet Governance / Readback Chain

Representative files:

- `orchestrator/product_task_packet_operator_report.py`
- `orchestrator/product_task_packet_*_readback.py`
- the Phase 349 through Phase 386 source/test/docs family

Role:

This layer adds deterministic reports and posture checks around product-task
packets, handoffs, escalation, review, blockers, outcomes, closures, and
next-boundary selection.

Roger should understand:

This is the most black-box-prone region. It is mostly control spine, not product
body. It keeps the project safe and auditable, but it can also create a feeling
that the machine is mostly generating paperwork about itself.

### Routing / Capability / Provider Policy

Representative files:

- `orchestrator/capability_registry.py`
- `orchestrator/request_routing.py`
- `orchestrator/route_proposal.py`
- `orchestrator/route_selection_readiness.py`
- `orchestrator/model_router_policy.py`
- provider catalog / provider smoke modules

Role:

This layer describes how future requests may be classified, routed, blocked, or
prepared for provider/model/runtime work.

Roger should understand:

Policy and route-readiness are not live route execution. A route envelope or
provider catalog entry does not prove a model can do the job.

### Backbone / Reusable Loop Abstraction

Representative files:

- `orchestrator/backbone_*.py`
- fake research-claim and PKMS note fixture mapping modules

Role:

This layer tries to describe reusable workflow structure across domains.

Roger should understand:

This is strategically important because it suggests Orchestrator can generalize
beyond coding and beyond claims/disputes. But fixture mappings are not live
domain integrations.

## What Roger Needs To Keep In View

Roger should track these five questions:

1. What can the system actually do today?
2. What is only a deterministic control/readback surface?
3. What product direction is being silently reinforced?
4. What proof exists, and what does it not prove?
5. What decision still needs founder ratification?

## What Can Stay Under The Hood

Roger does not need to personally understand every module, test, or phase. The
following can stay under the hood unless they become active boundaries:

- exact Python implementation of readback dataclasses
- every phase-specific test module
- repeated non-proof strings in individual phase docs
- low-level artifact path formatting
- patch apply internals not relevant to a current mutation boundary

## Most Black-Boxed Areas

Current black-box pressure comes from:

- the volume of product-task packet readback phases
- the dense naming of Phase 349 through Phase 386 modules
- overlap between case packet, product task packet, coding packet, boundary
  packet, and backbone vocabulary
- inherited claims/disputes/appeals strategy that may look ratified because it
  is written down
- deterministic tests that prove contract shape but not human-level usefulness

## Recommended Next Clarity Docs

The current founder clarity set is:

- `docs/FOUNDER_CONTROL_PROTOCOL.md`
- `docs/FOUNDER_COMPREHENSION_SNAPSHOT_TEMPLATE.md`
- `docs/CAPABILITY_REALITY_MAP.md`
- `docs/DOMAIN_LOCK_IN_AUDIT.md`
- `docs/OPERATOR_CODEBASE_MAP.md`
- `docs/FIRST_PRODUCT_WEDGE_DECISION.md`

A later useful addition may be:

- `docs/PRODUCT_SURFACE_GLOSSARY.md`

That glossary should define packet, case packet, dossier packet, boundary,
readback, artifact, deterministic verification, semantic success, product
capability surface, and governance surface.
