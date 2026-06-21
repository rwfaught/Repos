# Migration Report

## Purpose

This folder provides a standalone, generic OpenClaw WSL installer with neutral distro names, install paths, script names, logs, comments, configuration paths, and operator output.

## Included

The current PowerShell entrypoint, supervised Bash pipeline, bootstrap, verification scripts, dashboard helper, optional Discord scripts, compatibility helpers, reporting helper, and routing payload required by the current staging contract were included.

## Excluded

Historical proof logs, backups, snapshots, archived packages, patch-test scripts, handoff packets, design records, runtime captures, and superseded installer entrypoints were intentionally excluded.

## Renamed

- Host entrypoint to `init_openclaw_wsl.ps1`
- Bootstrap to `bootstrap_openclaw_wsl.sh`
- Supervised runner to `run_openclaw_supervised_wire.sh`
- Config runner to `run_openclaw_install_from_config.sh`
- Baseline, dashboard, optional-model, and watcher files to neutral names

All dependent references were updated consistently.

## Preserved Behavior

The WSL import flow, host preflight, systemd setup, package staging, pinned OpenClaw setup, Ollama/model behavior, supervised stages, verification logic, dashboard support, optional Discord flow, token-file staging, and generated reporting are intended to remain equivalent.

## Intentional Changes

- Default distro: `OpenClaw-Ubuntu-22.04-Vanilla01`
- Linux install root: `/home/<user>/openclaw_install`
- Windows install base: `%LOCALAPPDATA%\WSL\OpenClaw`
- Cache and log names use OpenClaw-neutral naming
- Package filenames, comments, help text, service support paths, and operator output use neutral naming

## Commands

Host preflight only:

```powershell
powershell -ExecutionPolicy Bypass -File .\init_openclaw_wsl.ps1 -DistroName "OpenClaw-Ubuntu-22.04-Vanilla01" -RunHostPreflightOnly -AllowWslShutdown
```

Install without Discord:

```powershell
powershell -ExecutionPolicy Bypass -File .\init_openclaw_wsl.ps1 -DistroName "OpenClaw-Ubuntu-22.04-Vanilla01" -RunSupervisedWire -AllowWslShutdown -MinimalWireModel
```

Install with Discord:

```powershell
powershell -ExecutionPolicy Bypass -File .\init_openclaw_wsl.ps1 -DistroName "OpenClaw-Ubuntu-22.04-Vanilla01" -RunSupervisedWire -AllowWslShutdown -MinimalWireModel -ConfigureDiscord -DiscordOwnerId "<DISCORD_USER_ID>" -DiscordBotTokenFile "C:\secure\discord_bot_token.txt" -RunDiscordVerifier
```

Create and stage a distro without running the Linux install:

```powershell
powershell -ExecutionPolicy Bypass -File .\init_openclaw_wsl.ps1 -DistroName "OpenClaw-Ubuntu-22.04-Vanilla01" -AllowWslShutdown
```

## Runtime Status

No runtime, installer, WSL, Ollama, model, Discord, or network action was executed during migration. Runtime equivalence remains unproven.
