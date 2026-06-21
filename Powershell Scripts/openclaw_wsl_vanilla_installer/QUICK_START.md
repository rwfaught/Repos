# Quick Start

Use a full distro name or a suffix. The default OpenClaw package is `openclaw@2026.6.6`.

## Host Preflight Only

```powershell
Set-Location "C:\Users\accou\Desktop\Repos\Powershell Scripts\openclaw_wsl_vanilla_installer"
powershell -ExecutionPolicy Bypass -File .\init_openclaw_wsl.ps1 -DistroName "MyBot" -OpenClawPackageSpec "openclaw@2026.6.6" -RunHostPreflightOnly -AllowWslShutdown
```

## Install Without Discord

```powershell
Set-Location "C:\Users\accou\Desktop\Repos\Powershell Scripts\openclaw_wsl_vanilla_installer"
powershell -ExecutionPolicy Bypass -File .\init_openclaw_wsl.ps1 -DistroName "MyBot" -OpenClawPackageSpec "openclaw@2026.6.6" -RunSupervisedWire -AllowWslShutdown -MinimalWireModel
```

The authenticated dashboard opens automatically from Windows when the dashboard human gate is ready. Send `Reply with OK only.`, wait for the fresh response, return to the installer, and press ENTER.

Fallback:

```powershell
powershell -ExecutionPolicy Bypass -File .\watch_openclaw_wire.ps1 -DistroName "<distro>" -CopyDashboardUrl -OpenDashboard
```

## Install With Discord

```powershell
Set-Location "C:\Users\accou\Desktop\Repos\Powershell Scripts\openclaw_wsl_vanilla_installer"
powershell -ExecutionPolicy Bypass -File .\init_openclaw_wsl.ps1 -DistroName "MyBot" -OpenClawPackageSpec "openclaw@2026.6.6" -RunSupervisedWire -AllowWslShutdown -MinimalWireModel -ConfigureDiscord -DiscordOwnerId "<DISCORD_USER_ID>" -DiscordBotTokenFile "C:\secure\discord_bot_token.txt" -RunDiscordVerifier
```

The Discord token must remain in the referenced file and must not be inlined.

The installer waits for Discord readiness, then requires this real DM proof:

```text
Reply with DISCORD_SMOKE_OK only.
```

Type `DISCORD_SMOKE_OK` in the installer only after the configured bot replies. The installer then restarts and rechecks the gateway and starts the Windows-side runtime keepalive before printing `Done.`

From any folder, the global wrappers can prompt for the missing values:

```powershell
openclaw-install -DistroName MyBot -OpenClawPackageSpec openclaw@2026.6.6 -MinimalWireModel
openclaw-bot status -DistroName MyBot
```

After a Windows reboot, restart the documented keepalive. Its hidden foreground wrapper runs `wsl.exe --exec /bin/sleep 2147483647`; the Windows supervisor and wrapper must remain alive to keep WSL resident. The start command is safe to rerun:

```powershell
powershell -ExecutionPolicy Bypass -File .\Start-OpenClawRuntime.ps1 -DistroName "<distro>" -RequireDiscord
```

Check or stop it:

```powershell
powershell -ExecutionPolicy Bypass -File .\Start-OpenClawRuntime.ps1 -DistroName "<distro>" -RequireDiscord -Status
powershell -ExecutionPolicy Bypass -File .\Start-OpenClawRuntime.ps1 -DistroName "<distro>" -RequireDiscord -Stop
```

PID, status, and secret-free logs are stored under `runtime\` in this installer folder.

`-Status` performs live supervisor, wrapper, matching anchor, WSL, gateway, and optional Discord checks. It reports `NOT_READY` if saved JSON is stale or live state disagrees. `-Stop` kills matching supervisor, wrapper, and anchor processes only.
