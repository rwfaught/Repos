# Local Topology and Export Rules

## Purpose

This document records the current local repo topology and export convention for the Orchestrator product and the WSL/OpenClaw/Ollama/Discord platform package.

It exists to prevent future coordinator sessions, worker sessions, scripts, or command batches from inferring repo authority from the current shell prompt, backup folders, ZIP artifacts, or historical path names.

## Current Local Topology

### Neutral Operator Dock

Roger may keep PowerShell at:

`C:\Users\accou\Desktop\Repos`

This is the neutral command dock. It is not the product repo root and not the platform repo root.

Command batches should not rely on Roger already being inside a target repo. They should declare explicit paths and either use full paths or call `Set-Location` to the intended target.

### Product Workspace

Current product workspace:

`C:\Users\accou\Desktop\Repos\Orchestrator`

This folder is a workspace/container for the product repo and product ZIP artifacts.

It is not itself the Orchestrator product repo root.

### Product Repo Root

Current Orchestrator product repo root:

`C:\Users\accou\Desktop\Repos\Orchestrator\Orchestrator`

This repo owns product authority, including:

- `docs\PHASE_INDEX.md`
- `docs\ACTION_LOG.md`
- product phase docs
- product method/startup/context docs
- `orchestrator\`
- `agents\`
- `providers\`
- `verifiers\`
- `tests\`

### Platform Repo Root

Current WSL/OpenClaw/Ollama/Discord platform package root:

`C:\Users\accou\Desktop\Repos\Powershell Scripts\orchestrator_wsl_openclaw_v1_7_package`

This repo owns platform infrastructure, including:

- WSL creation/staging scripts
- Linux bootstrap scripts
- Ollama/OpenClaw installation and configuration scripts
- Discord configuration and verifier scripts
- platform proof logs
- platform handoff/reentry docs
- `ORCHESTRATOR_OPENCLAW_MEMORY_CAPSULE.md`

The platform repo does not own product phase authority.

## Export Convention

### Platform Export

`oz` means platform export.

It runs the existing platform zipper script:

`C:\Users\accou\Desktop\Repos\Powershell Scripts\Zip-OrchestratorRepo.ps1`

Default platform ZIP output:

`C:\Users\accou\Desktop\Repos\Powershell Scripts\orchestrator_wsl_openclaw_v1_7_package_latest.zip`

Do not overload `oz` to export the product repo.

### Product Export

The product repo is exported by:

`C:\Users\accou\Desktop\Repos\Powershell Scripts\Zip-OrchestratorProductRepo.ps1`

Default product ZIP output:

`C:\Users\accou\Desktop\Repos\Orchestrator\Orchestrator_product_repo_latest.zip`

The product zipper is intentionally separate from `oz`.

## Command Batch Rule

All future command batches should declare their target paths explicitly.

Preferred path skeleton:

`$ReposRoot = "C:\Users\accou\Desktop\Repos"`

`$ProductWorkspace = Join-Path $ReposRoot "Orchestrator"`

`$ProductRepo = Join-Path $ProductWorkspace "Orchestrator"`

`$ScriptsRoot = Join-Path $ReposRoot "Powershell Scripts"`

`$PlatformRepo = Join-Path $ScriptsRoot "orchestrator_wsl_openclaw_v1_7_package"`

Then the batch should either use full paths or explicitly choose its target with `Set-Location $ProductRepo` or `Set-Location $PlatformRepo`.

No batch should silently assume that the current shell prompt is already the correct repo unless the active boundary explicitly says so.

## Authority Rule

Product docs govern product progression.

Platform docs govern platform interpretation.

The platform memory capsule is supporting platform memory. It may inform history, but it does not override:

- `docs\PHASE_INDEX.md`
- `docs\ACTION_LOG.md`
- product phase docs
- product strategy docs
- current product success criteria

## Non-Goals

This document does not authorize:

- runtime execution
- WSL execution
- installer execution
- model probes
- Discord workflows
- bridge execution
- adapter execution
- vendoring
- cleanup/deletion
- parent-folder renaming
- treating platform history as live runtime truth

