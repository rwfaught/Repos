# OpenClaw WSL Vanilla Installer

This package creates a custom-named Ubuntu 22.04 WSL2 distro and installs a selectable OpenClaw package with optional Ollama models, verification stages, dashboard support, and optional Discord configuration.

## Requirements

- Windows with WSL2 available
- Windows PowerShell 5.1 or later
- Internet access during an actual install
- Sufficient disk space for Ubuntu, OpenClaw, Ollama, and selected models
- Administrator access where Windows or WSL configuration requires it

Supply either a full distro name such as `OpenClaw-Ubuntu-22.04-MyBot` or a suffix such as `MyBot`. When omitted, the installer prompts. Suffixes are normalized to `OpenClaw-Ubuntu-22.04-<suffix>`.

`-OpenClawPackageSpec` defaults to the latest ratified package, `openclaw@2026.6.6`. Explicit pins such as `openclaw@2026.6.6` preserve reproducibility. `openclaw@latest` validates that the command and installed package metadata are usable and reports the resolved version without enforcing a stale build string. Use `-OpenClawExpectedIdentity "OpenClaw <version> (<build>)"` when an exact identity must be enforced.

## Safety

`-ForceRecreate` can unregister the selected WSL distro and remove its install directory. Verify the exact `-DistroName` before using that switch.

The migration was validated statically only. No installer, WSL, Ollama, model, Discord, or network action was run during package creation.

## Host Preflight

```powershell
Set-Location "C:\Users\accou\Desktop\Repos\Powershell Scripts\openclaw_wsl_vanilla_installer"
powershell -ExecutionPolicy Bypass -File .\init_openclaw_wsl.ps1 -DistroName "MyBot" -OpenClawPackageSpec "openclaw@2026.6.6" -RunHostPreflightOnly -AllowWslShutdown
```

## Install Without Discord

```powershell
Set-Location "C:\Users\accou\Desktop\Repos\Powershell Scripts\openclaw_wsl_vanilla_installer"
powershell -ExecutionPolicy Bypass -File .\init_openclaw_wsl.ps1 -DistroName "MyBot" -OpenClawPackageSpec "openclaw@2026.6.6" -RunSupervisedWire -AllowWslShutdown -MinimalWireModel
```

During supervised wire mode, the Windows installer monitors the active operator state. When the dashboard verifier requests input, PowerShell copies and opens the authenticated dashboard URL without printing its token. Complete the dashboard chat proof and press ENTER in the installer; the Discord stage follows only after that gate passes.

If authenticated dashboard auto-open fails, run:

```powershell
powershell -ExecutionPolicy Bypass -File .\watch_openclaw_wire.ps1 -DistroName "<distro>" -CopyDashboardUrl -OpenDashboard
```

## Install With Discord

Store the token in a local file and pass its path. Do not put the token directly on the command line.

```powershell
Set-Location "C:\Users\accou\Desktop\Repos\Powershell Scripts\openclaw_wsl_vanilla_installer"
powershell -ExecutionPolicy Bypass -File .\init_openclaw_wsl.ps1 -DistroName "MyBot" -OpenClawPackageSpec "openclaw@2026.6.6" -RunSupervisedWire -AllowWslShutdown -MinimalWireModel -ConfigureDiscord -DiscordOwnerId "<DISCORD_USER_ID>" -DiscordBotTokenFile "C:\secure\discord_bot_token.txt" -RunDiscordVerifier
```

With `-RunDiscordVerifier`, completion requires all of these results: dashboard proof PASS, Discord configuration PASS, Discord transport PASS, manual Discord message proof PASS, and post-install runtime readiness PASS. At the Discord gate, DM the configured bot exactly `Reply with DISCORD_SMOKE_OK only.`, then type `DISCORD_SMOKE_OK` in the installer only after the bot replies.

## Runtime Lifecycle

Before printing `Done.`, the installer restarts `openclaw-gateway.service`, waits for the gateway to become active and Discord to report running/connected/works, then starts `Start-OpenClawRuntime.ps1`. The helper launches a hidden PowerShell supervisor plus a hidden foreground wrapper. The wrapper remains blocked on:

```powershell
wsl.exe --distribution "<distro>" --user "<user>" --exec /bin/sleep 2147483647
```

The supervisor checks the wrapper, matching WSL anchor processes, WSL Running state, gateway, and optional Discord readiness every 20 seconds. It only restarts the gateway while the verified wrapper/anchor is holding WSL Running.

Runtime files are written inside this package under `runtime\`:

- `openclaw_runtime_<distro>.pid`
- `openclaw_runtime_<distro>.status.json`
- `openclaw_runtime_<distro>.log`

`-Status` performs fresh supervisor, wrapper, matching WSL anchor, WSL, gateway, and optional Discord checks. It reports `NOT_READY` when recorded JSON is stale or disagrees with current state. A `READY` JSON value by itself is not treated as proof.

The Windows supervisor and foreground wrapper must remain alive to keep WSL resident. They do not survive a Windows reboot, so start the runtime again after signing in. If the wrapper or matching anchor exits, the supervisor recreates the wrapper. The same start command is safe to run manually:

```powershell
powershell -ExecutionPolicy Bypass -File .\Start-OpenClawRuntime.ps1 -DistroName "<distro>" -RequireDiscord
```

Check status:

```powershell
powershell -ExecutionPolicy Bypass -File .\Start-OpenClawRuntime.ps1 -DistroName "<distro>" -RequireDiscord -Status
```

Stop the keepalive. This terminates the matching supervisor, wrapper, and all matching WSL sleep anchors for that distro/user payload without targeting unrelated WSL processes:

```powershell
powershell -ExecutionPolicy Bypass -File .\Start-OpenClawRuntime.ps1 -DistroName "<distro>" -RequireDiscord -Stop
```

## Post-Install Verification

```powershell
wsl.exe --distribution "OpenClaw-Ubuntu-22.04-MyBot" --user roger -- bash -lc "openclaw --version"
wsl.exe --distribution "OpenClaw-Ubuntu-22.04-MyBot" --user roger -- bash -lc "systemctl --user status openclaw-gateway.service --no-pager"
wsl.exe --distribution "OpenClaw-Ubuntu-22.04-MyBot" --user roger -- bash -lc "ollama list"

Global wrappers in `C:\Users\accou\Desktop\Repos\Powershell Scripts\tools` provide `openclaw-install` and `openclaw-bot`. They can be run from any folder when that tools directory is on `PATH`. Both accept a full distro name or suffix and prompt when omitted.
```

See `QUICK_START.md` for the shortest command sequence and `MIGRATION_REPORT.md` for migration scope and caveats.
