# Platform Runtime Baseline

## Purpose

This document records the product-side baseline relationship between Orchestrator and its local runtime platform package.

It exists to prevent repo-topology drift. The Orchestrator product repo remains the product authority. The WSL/OpenClaw/Ollama/Discord installer package is the official local runtime platform substrate, but it is not the product phase ledger and does not own product governance.

## Current Platform Package

Current platform package identity:

- Package role: WSL/OpenClaw/Ollama/Discord runtime platform.
- Package posture: sibling package, not vendored into the product repo during Phase 63.
- Known package family: `orchestrator_wsl_openclaw_v1_7_package`.
- Known Windows package path from prior sessions: `C:\Users\accou\Desktop\Repos\Powershell Scripts\orchestrator_wsl_openclaw_v1_7_package`.

The parent folder name `Powershell Scripts` is historical and should not be renamed inside this phase.

## Authority Rule

The product repo owns:

- `docs/PHASE_INDEX.md`
- `docs/ACTION_LOG.md`
- product phase files
- product method/startup/context docs
- product code and tests
- admission of future product phases

The platform package owns:

- WSL creation and bootstrap scripts
- Ollama/OpenClaw setup scripts
- Discord configuration/verifier scripts
- runtime proof logs
- platform memory capsule
- platform handoff/reentry docs

If platform docs and product docs appear to conflict, product phase docs govern product progression. Platform docs govern only platform interpretation unless explicitly admitted into the product repo by a product phase.

## Memory Capsule Status

`ORCHESTRATOR_OPENCLAW_MEMORY_CAPSULE.md` is platform institutional memory.

It may be used to understand historical OpenClaw/Ollama/Discord work, runtime proof history, and platform handoff context.

It must not be treated as:

- the product phase ledger
- a replacement for `PHASE_INDEX.md`
- a product strategy override
- current live runtime proof
- authorization to run WSL, installers, models, Discord, bridge, or adapter work

## Current Integration Posture

The current posture is manifest-first / vendor-later.

This means the product repo recognizes the runtime platform package as a sibling package and records the integration contract. It does not copy the package into the product tree during Phase 63.

Vendoring can only be considered after a later boundary defines a clean canonical release surface and explicitly excludes backups, package snapshots, runtime logs, stale proof directories, duplicate handoff copies, and other archive noise.

## Current Runtime Truth Rule

Historical runtime proofs may establish that earlier runtime states passed specific checks at specific times.

They do not establish current live runtime truth.

Any future claim about current runtime state requires a fresh, explicitly authorized runtime/probe/model/Discord boundary.

## Local Topology Reference

The current local operator dock, product workspace, product repo root, platform repo root, and export conventions are recorded in `docs/LOCAL_TOPOLOGY_AND_EXPORTS.md`.

That topology document is the product-side reference for local path and ZIP-export conventions.

