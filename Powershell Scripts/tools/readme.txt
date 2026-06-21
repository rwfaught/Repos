OpenClaw operator tools
=======================

Add this directory to PATH to run the command wrappers from any folder.

Install:
  openclaw-install
  openclaw-install -DistroName MyBot -OpenClawPackageSpec openclaw@2026.6.6 -MinimalWireModel
  openclaw-install -DistroName OpenClaw-Ubuntu-22.04-MyBot -OpenClawPackageSpec openclaw@latest

The install wrapper prompts for a distro name or suffix and package spec when omitted.
The package default is openclaw@2026.6.6. Discord configuration and destructive
recreation are opt-in switches:

  openclaw-install -DistroName MyBot -ConfigureDiscord -DiscordOwnerId <ID> -RunDiscordVerifier
  openclaw-install -DistroName MyBot -ForceRecreate

Runtime:
  openclaw-bot start -DistroName MyBot
  openclaw-bot status -DistroName MyBot
  openclaw-bot stop -DistroName MyBot

The runtime wrapper resolves suffixes against registered OpenClaw-Ubuntu-22.04-*
distros before calling Start-OpenClawRuntime.ps1.

Hermes runtime:
  hermes-bot status
  hermes-bot health
  hermes-bot logs
  hermes-bot stop
  hermes-bot start
  hermes-bot restart

The Hermes wrapper defaults to OpenClaw-Ubuntu-22.04-ROC-AI, user roger,
hermes.service, and http://127.0.0.1:8765. It controls only the Hermes user
systemd service and runs health checks from inside the target WSL distro.

Bootstrap log watcher:
  powershell -File watch_bootstrap.ps1 -DistroName OpenClaw-Ubuntu-22.04-MyBot -RunTimestamp <timestamp>
  bash watch_bootstrap.sh OpenClaw-Ubuntu-22.04-MyBot <timestamp>
