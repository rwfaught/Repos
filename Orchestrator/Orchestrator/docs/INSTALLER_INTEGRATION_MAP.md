# Installer Integration Map

## Purpose

This document maps how the WSL/OpenClaw/Ollama/Discord platform package relates to the Orchestrator product repo.

It is a product-side integration map, not a runtime execution plan.

## Summary

Orchestrator is the product kernel.

The installer/OpenClaw package is the local runtime substrate.

OpenClaw is a potential future reach/action adapter. It must not own Orchestrator state transitions, product phase progression, task lifecycle, case-packet state, recommendation lifecycle, or verification semantics.

## Product Surfaces

The product repo currently contains:

- `orchestrator/` — execution engine and product kernel modules.
- `agents/` — role wrappers and prompts.
- `providers/` — provider contract and provider implementations/stubs.
- `verifiers/` — deterministic verification checks.
- `tests/` — phase-oriented regression coverage.
- `docs/` — product governance, phase ledger, method, context, and strategy docs.
- `data/` — generated/local product runtime state and artifacts.

For orientation, `data/`, `test_logs/`, `__pycache__/`, `.pyc`, and `Zone.Identifier` artifacts are not canonical source surfaces.

## Platform Surfaces

The platform package currently contains root-level platform docs and scripts, including:

- session reentry and relay protocol docs
- worker/model routing protocol docs
- platform memory capsule
- package manifest and runtime ratification handoffs
- Windows WSL init script
- Linux bootstrap script
- config-driven installer runner
- Discord configuration script
- Discord/runtime verifier script

For orientation, `.orchestrator_backups/`, `_package_snapshots/`, `.orchestrator_temp/`, old `REPRO_*` directories, `Run_FIX_*` files, `.bak` files, stale ZIPs, copied path-artifacts, and runtime proof logs should not be treated as canonical unless a later boundary explicitly targets them.

## Integration Contract

The product may reference the platform package for:

- local model runtime availability
- OpenClaw runtime substrate
- Discord remote-control substrate
- future adapter feasibility
- reproduction/provenance context

The product must not silently import platform assumptions as product authority.

Before any future live integration, the coordinator must define a boundary that states:

- purpose
- allowed operations
- excluded operations
- intended files or runtime surfaces
- expected proof
- whether mutation, runtime, export, WSL, model, Discord, bridge, adapter, or installer work is authorized

## Future Adapter Path

A future OpenClaw adapter phase may be considered only after product strategy admits it.

Such a phase would need to preserve:

- product-owned state transitions
- bounded task authority
- explicit operator authorization
- deterministic verification
- clear provider/adapter contracts
- no hidden runtime side effects

## Future Vendoring Criteria

Vendoring should not occur until a later boundary defines:

1. canonical platform release files
2. excluded backup/archive/runtime surfaces
3. manifest/hash expectations
4. update procedure
5. product/platform authority rule
6. rollback or provenance rule
7. proof that vendoring will reduce drift rather than import it

Until then, sibling-package manifest integration is the safer posture.

## Export Separation Rule

Platform export and product export are separate.

`oz` exports the WSL/OpenClaw/Ollama/Discord platform package only.

The product repo is exported by `C:\Users\accou\Desktop\Repos\Powershell Scripts\Zip-OrchestratorProductRepo.ps1`.

Do not overload `oz` to export both artifacts.

