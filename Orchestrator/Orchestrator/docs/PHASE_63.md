# Phase 63 — OpenClaw/Ollama/Discord Runtime Platform Integration

## Status

Admitted as a documentation-first integration contract.

## Purpose

Phase 63 establishes the product-side authority boundary between the Orchestrator product repo and the WSL/OpenClaw/Ollama/Discord runtime platform package.

This phase does not implement runtime integration. It prevents drift by defining what belongs to the Orchestrator kernel, what belongs to the platform layer, how the platform package is referenced, and what must be true before any future vendoring, bridge execution, adapter execution, WSL work, model probe, Discord action, or cleanup boundary is allowed.

## Accepted Context

The Orchestrator repo is the product authority.

The WSL/OpenClaw/Ollama/Discord installer package is runtime/platform infrastructure. It creates and configures the local runtime substrate but does not own Orchestrator product governance, product phase progression, task state, case-packet state, recommendation lifecycle, or bounded execution semantics.

The platform memory capsule is supporting platform history. It may inform platform interpretation, but it does not override the product phase ledger, product strategy documents, current success criterion, or current OpenClaw posture.

The current product-side OpenClaw posture remains governed by `docs/OPENCLAW_FIT_ASSESSMENT_01.md`: OpenClaw is a possible future adapter / reach-action layer, and immediate live integration is not authorized by this phase.

## Deliverables

Phase 63 creates or updates the following product-side documents:

- `docs/PHASE_63.md`
- `docs/PLATFORM_RUNTIME_BASELINE.md`
- `docs/INSTALLER_INTEGRATION_MAP.md`
- `docs/PHASE_INDEX.md`
- `docs/ACTION_LOG.md`

## Product / Platform Responsibility Map

### Orchestrator Product Repo Owns

- Product phase ledger and action log.
- Bounded task/run/artifact state.
- Case-packet state and orientation surfaces.
- Provider dispatch contracts.
- Deterministic verification contracts.
- Recommendation lifecycle and operator-controlled follow-up surfaces.
- Product strategy, current success criterion, and product governance docs.
- Future admission or rejection of OpenClaw as an adapter.

### Runtime Platform Package Owns

- Windows/WSL distro creation and staging.
- Linux bootstrap logic.
- Ollama installation/configuration/model baseline.
- OpenClaw installation/configuration.
- Discord setup and guarded verifier surfaces.
- Runtime proof logs and reproduction evidence.
- Platform memory capsule and platform-specific handoff/reentry docs.

## Integration Posture

The integration posture for Phase 63 is:

Manifest first; vendor later only if separately authorized.

The installer package should be treated as a sibling platform package with a formal product-side baseline and integration map. It should not be copied wholesale into the product repo during this phase.

Future vendoring may be considered only after a separate cleanup/export-baseline boundary identifies a compact canonical platform release surface and excludes backups, package snapshots, runtime logs, stale proofs, and duplicate protocol copies.

## Non-Goals

Phase 63 does not authorize:

- Runtime execution.
- WSL execution.
- Installer execution.
- Model probes.
- OpenClaw gateway execution.
- Discord workflows.
- Bridge execution.
- Adapter execution.
- A18CF continuation.
- Vendoring the installer package.
- Deleting, moving, archiving, or cleaning backup/noise files.
- Renaming parent folders.
- Treating the platform memory capsule as product phase authority.

## Completion Criteria

Phase 63 is complete when:

1. `docs/PLATFORM_RUNTIME_BASELINE.md` exists and defines the platform package as a sibling runtime substrate.
2. `docs/INSTALLER_INTEGRATION_MAP.md` exists and maps product/platform responsibilities.
3. `docs/PHASE_63.md` exists and defines the phase boundary.
4. `docs/PHASE_INDEX.md` records Phase 63.
5. `docs/ACTION_LOG.md` records Phase 63 completion.
6. No product code behavior is changed.
7. No runtime, WSL, installer, model, Discord, bridge, adapter, vendoring, cleanup, or parent-folder rename work is performed.

## Local Topology and Export Convention

The local topology and export convention for the product repo and platform repo is recorded in `docs/LOCAL_TOPOLOGY_AND_EXPORTS.md`.

That document records the neutral operator dock, product workspace, product repo root, platform repo root, product ZIP output, platform ZIP output, `oz` platform-export meaning, and separate product zipper rule.

