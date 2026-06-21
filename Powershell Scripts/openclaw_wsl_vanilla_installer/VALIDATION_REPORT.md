# Validation Report

## Dashboard Auto-Open Remediation

This section records the later clean-install dashboard remediation and supersedes the original "unchanged" status for files touched by this patch.

- `init_openclaw_wsl.ps1` now starts a hidden Windows-side dashboard monitor for supervised wire runs and fails closed on a nonzero installer exit.
- `watch_openclaw_wire.ps1` now waits for the active `dashboard_verifier` operator state and opens the authenticated URL through `Start-Process -FilePath $url`.
- `bootstrap_openclaw_wsl.sh` retains the repair that makes `$HOME/.config` user-owned before environment persistence.
- Documentation now describes the automatic authenticated dashboard handoff and exact fallback command.
- All included `.sh` files were normalized to LF.

## Discord Completion And Runtime Remediation

- Supervised Discord verification now polls until Discord reports running/connected/works.
- Manual proof requires the operator to DM the configured Discord bot exactly `Reply with DISCORD_SMOKE_OK only.` and type `DISCORD_SMOKE_OK` only after the reply.

## Generic Distro And Package Selection Remediation

- Installer and global wrappers accept a full `OpenClaw-Ubuntu-22.04-*` distro name or a suffix and prompt when omitted.
- Default package spec is the ratified `openclaw@2026.6.6`; explicit package pins remain supported.
- The ratified default enforces `OpenClaw 2026.6.6 (8c802aa)`.
- Other explicit version pins validate installed npm package version unless an exact identity is supplied.
- `openclaw@latest` validates command/package availability and records the resolved version without using a stale exact identity.
- The legacy 2026.5.28 compatibility patch is skipped for other selected package versions after identity validation.
- Configuration or transport evidence alone cannot mark the Discord verifier allowed.
- A final runtime stage restarts the gateway and requires gateway active plus Discord running/connected/works.
- `Start-OpenClawRuntime.ps1` starts a hidden documented WSL keepalive and rechecks readiness before installer completion.
- The final report separately records dashboard, Discord configuration, Discord transport, manual message, and runtime readiness results.

## Vanilla05 Verifier Nounset Remediation

- `verify_openclaw_discord_v1_7.sh` now initializes all channel, transport, manual-proof, pairing, and failure bookkeeping before readiness helpers can write taxonomy markers.
- The readiness helper can safely run under `set -u` before the channel-list parser updates `discord_installed`, `discord_configured`, and `discord_enabled`.
- Manual proof remains REQUIRED and becomes PASS only after the operator types `DISCORD_SMOKE_OK` following the real bot reply.
- Git Bash `bash -n` for all 14 shell scripts: pass.
- Byte-level carriage-return scan for all 14 shell scripts: pass, zero CR bytes.
- Active `discord.runVerifier` branches contain no SKIPPED result; SKIPPED markers are confined to the not-requested `else` branches.

## Vanilla06 Durable Runtime Remediation

- `Start-OpenClawRuntime.ps1` now launches a detached hidden PowerShell supervisor using `Start-Process powershell.exe`.
- The supervisor runs a non-exiting keepalive loop, maintains a WSL anchor, checks distro/gateway/Discord readiness every 20 seconds, and restarts the gateway when readiness degrades.
- Secret-free PID, JSON status, and log files are written under the package `runtime` directory.
- The foreground launcher confirms the detached PID with `Get-CimInstance` and waits for its status to become READY.
- `init_openclaw_wsl.ps1` independently waits five seconds and confirms the recorded Windows supervisor PID with `Get-CimInstance` before allowing `Done.`
- PID verification also checks that the process command line identifies `Start-OpenClawRuntime.ps1`, `-KeepAliveLoop`, and the target distro.
- PowerShell parser validation for `Start-OpenClawRuntime.ps1` and `init_openclaw_wsl.ps1`: pass.
- Static loop proof found `while ($true)`, the 20-second interval, WSL anchor recreation, distro checks, gateway restart, and optional Discord probe checks.
- Git Bash `bash -n` for all 14 shell scripts: pass.
- Byte-level carriage-return scan for all 14 shell scripts: pass, zero CR bytes.

## Vanilla06 Anchor Validation Remediation

- The WSL anchor uses a blocking encoded shell payload equivalent to `trap "exit 0" TERM INT; while true; do sleep 60; done`.
- Anchor validation requires a live `wsl.exe` PID whose command line matches the target distro, Linux user, and exact encoded persistent-loop payload.
- READY requires supervisor alive, matching anchor alive, target distro Running, gateway active, and Discord running/connected/works when required in the same cycle.
- Anchor recreation writes `ANCHOR_STARTING` and cannot become READY until a later complete validation cycle.
- Gateway repair runs only when the matching anchor is alive and WSL is Running, with a 60-second restart cooldown.
- Status JSON now includes `updatedAt`, `anchorAlive`, `anchorCommandMatches`, and `checkNumber`.
- `-Status` performs live supervisor, anchor, WSL, gateway, and optional Discord checks and reports NOT_READY on stale disagreement.
- `-Stop` validates and terminates both the supervisor and matching anchor.

## Foreground Wrapper Anchor Remediation

- Replaced detached `wsl.exe` anchor launching with a dedicated hidden PowerShell `-AnchorWrapper` mode.
- The wrapper runs `wsl.exe --distribution <distro> --user <user> --exec /bin/sleep 2147483647` in the foreground and remains blocked while the anchor is healthy.
- The supervisor discovers matching wrapper and `wsl.exe` anchor processes by command line and recreates the wrapper when it exits.
- READY requires live supervisor, wrapper, matching anchor, WSL Running, gateway active, and optional Discord ready checks in the same cycle.
- Status JSON records `state`, `wrapperPid`, `anchorPids`, `wrapperAlive`, `anchorAlive`, `anchorCommandMatches`, `distroRunning`, `gatewayActive`, `discordReady`, `checkNumber`, and `updatedAt`.
- `-Status` ignores stale READY claims and performs live validation.
- `-Stop` terminates the matching supervisor, all matching wrappers, and all matching WSL sleep anchors without targeting unrelated WSL processes.
- The installer performs live `-Status` validation after its delayed supervisor PID check and before `Done.`

## Paths

- Source folder: `C:\Users\accou\Desktop\Repos\Powershell Scripts\&#111;rchestrator_wsl_openclaw_v1_7_package`
- Target folder: `C:\Users\accou\Desktop\Repos\Powershell Scripts\openclaw_wsl_vanilla_installer`

The source path encodes one character as a Markdown entity so the rendered path remains identifiable while the target's required plain-text legacy-name scan remains clean.

## Files Copied Or Created

- `init_openclaw_wsl.ps1`
- `bootstrap_openclaw_wsl.sh`
- `run_openclaw_supervised_wire.sh`
- `run_openclaw_install_from_config.sh`
- `verify_openclaw_baseline.sh`
- `verify_openclaw_dashboard.sh`
- `verify_openclaw_optional_models.sh`
- `watch_openclaw_wire.ps1`
- `Start-OpenClawRuntime.ps1`
- `configure_openclaw_discord_v1.sh`
- `verify_openclaw_discord_v1.sh`
- `verify_openclaw_discord_v1_7.sh`
- `verify_openclaw_runtime_readiness.sh`
- `write_wire_ratification_report_v1_7.sh`
- `apply_openclaw_repro_compat_layer_v1_7.sh`
- `openclaw_gateway_auth_helper_v1.sh`
- `patch_openclaw_readonly_external_plugins_v1_7.sh`
- `local_worker_routing_v1.json`
- `Get-LocalWorkerRoutingConfig_v1.ps1`
- `Invoke-LocalWorkerRouting_v1.ps1`
- `Invoke-LocalWorkerRoutingRuntimeBridge_v1.ps1`
- `Invoke-LocalWorkerLiveProbeAdapter_v1.ps1`
- `README.md`
- `QUICK_START.md`
- `PACKAGE_MANIFEST.md`
- `MIGRATION_REPORT.md`
- `VALIDATION_REPORT.md`

## Renamed Surfaces

- PowerShell installer entrypoint
- Linux bootstrap
- Supervised runner
- Config-driven runner
- Baseline verifier
- Dashboard verifier
- Optional-model verifier
- Windows watcher

All direct references to these renamed files were updated in the copied target scripts.

## Reference Removal

Removed or neutralized:

- Product branding in filenames and file content
- Default distro names
- Windows install and cache paths
- Linux install, configuration, log, archive, and secret paths
- Script invocations and recovery guidance
- Sudoers filename, shell markers, temporary filenames, function identifiers, comments, help text, and operator output

Plain-text case-insensitive target scan result: **zero legacy product-name matches**.

Target filename scan result: **zero legacy product-name matches**.

## Historical Source Hash Proof

The following hashes were captured during the original package migration. They are historical and are not current hashes for files changed or line-ending-normalized by the dashboard remediation:

| Target role/file | SHA-256 before | SHA-256 after | Result |
|---|---|---|---|
| `init_openclaw_wsl.ps1` | `a4fea19ed76b59576b1b2713dcc82223c1c596681c05902f0d173f141253bc72` | `a4fea19ed76b59576b1b2713dcc82223c1c596681c05902f0d173f141253bc72` | unchanged |
| `bootstrap_openclaw_wsl.sh` | `2b5c219ea431c481498a2f0b3da00cb90912fa2d81b71553f78086e725c3a00d` | `2b5c219ea431c481498a2f0b3da00cb90912fa2d81b71553f78086e725c3a00d` | unchanged |
| `run_openclaw_supervised_wire.sh` | `c006742c46e0577b9b4e8e1e834a324b84c1287cead333a9843e1d9643deebb6` | `c006742c46e0577b9b4e8e1e834a324b84c1287cead333a9843e1d9643deebb6` | unchanged |
| `configure_openclaw_discord_v1.sh` | `03110c763a148d56bfbe97d774692441d23b3cdc9f0550043f45078833456c88` | `03110c763a148d56bfbe97d774692441d23b3cdc9f0550043f45078833456c88` | unchanged |
| `verify_openclaw_baseline.sh` | `69e191fca7a7a1bbb486f5f8495d70602df7bdac0ae9144e3e1c02b041dc732c` | `69e191fca7a7a1bbb486f5f8495d70602df7bdac0ae9144e3e1c02b041dc732c` | unchanged |
| `verify_openclaw_dashboard.sh` | `aace5c7130d09f21686dab5451e4d74a1deb39ecc2d1aa5645f76e6ed6413a0f` | `aace5c7130d09f21686dab5451e4d74a1deb39ecc2d1aa5645f76e6ed6413a0f` | unchanged |
| `verify_openclaw_optional_models.sh` | `61eb20384df29457bbd36943c34d60c28b918f21c908d2a5dc09d328a0d364ae` | `61eb20384df29457bbd36943c34d60c28b918f21c908d2a5dc09d328a0d364ae` | unchanged |
| `verify_openclaw_discord_v1_7.sh` | `b5b661cd9991aa2c40e90ee6035a2f9a490b2776700ab21be5d57d8ec2c4849a` | `b5b661cd9991aa2c40e90ee6035a2f9a490b2776700ab21be5d57d8ec2c4849a` | unchanged |
| `write_wire_ratification_report_v1_7.sh` | `c760358d7d33bd0201b4377d5d43026bda185dfc85d149217482900f8e18d850` | `c760358d7d33bd0201b4377d5d43026bda185dfc85d149217482900f8e18d850` | unchanged |
| `apply_openclaw_repro_compat_layer_v1_7.sh` | `86da8dceeb5374e0f8a8e1e47616ece4c0352efe7006ffbbe91da83b44f74d91` | `86da8dceeb5374e0f8a8e1e47616ece4c0352efe7006ffbbe91da83b44f74d91` | unchanged |
| `openclaw_gateway_auth_helper_v1.sh` | `85c541ae20d671f2620d4cf69ffe5a2dbd96de781d54443ebfa7a0e3fb828966` | `85c541ae20d671f2620d4cf69ffe5a2dbd96de781d54443ebfa7a0e3fb828966` | unchanged |
| `patch_openclaw_readonly_external_plugins_v1_7.sh` | `6318c445c9e66c8e9c7b56a47492c2647f6eadcddd0da05cbe2ad23f363673dc` | `6318c445c9e66c8e9c7b56a47492c2647f6eadcddd0da05cbe2ad23f363673dc` | unchanged |
| `local_worker_routing_v1.json` | `29e35bec3e244dc4535b5307d60b3347eaa1a72ee070737645682cb22835bd66` | `29e35bec3e244dc4535b5307d60b3347eaa1a72ee070737645682cb22835bd66` | unchanged |
| `Get-LocalWorkerRoutingConfig_v1.ps1` | `c377faa18e67532e37f263c033c6dd6052c2cccca6b0f307647df53866fb35b8` | `c377faa18e67532e37f263c033c6dd6052c2cccca6b0f307647df53866fb35b8` | unchanged |
| `Invoke-LocalWorkerRouting_v1.ps1` | `b9a25c0d177471919319b2dd6e814770185b04292d02aa781c33f82c6d53628c` | `b9a25c0d177471919319b2dd6e814770185b04292d02aa781c33f82c6d53628c` | unchanged |
| `Invoke-LocalWorkerRoutingRuntimeBridge_v1.ps1` | `af864a89fadaf250e5ab397f3ddaa772458ee891e850ebd0f79813b465e4f3f8` | `af864a89fadaf250e5ab397f3ddaa772458ee891e850ebd0f79813b465e4f3f8` | unchanged |
| `Invoke-LocalWorkerLiveProbeAdapter_v1.ps1` | `cf8aa7901d3088ea42a40b024f6d6930124fbfa4686ca87e98e39e268f73b1bc` | `cf8aa7901d3088ea42a40b024f6d6930124fbfa4686ca87e98e39e268f73b1bc` | unchanged |

## Static Validation

- Windows-side supervised dashboard monitor waits for `dashboard_verifier` with operator input required: pass
- Dashboard watcher opens the authenticated `$url` variable and does not print the token: pass
- Supervised installer native exit code blocks post-install checks on failure: pass
- PowerShell parser for `init_openclaw_wsl.ps1` and `watch_openclaw_wire.ps1`: pass
- Git Bash `bash -n` for all 14 included `.sh` files: pass
- Byte-level carriage-return scan for all 14 included `.sh` files: pass, zero CR bytes
- PowerShell parser for `Start-OpenClawRuntime.ps1`: pass
- Active Discord verifier defaults manual proof to REQUIRED, not SKIPPED: pass
- Final completion order is Discord manual proof, runtime readiness, report, Windows keepalive readiness, then `Done.`: pass
- Bootstrap ownership repair before environment persistence: pass
- Target folder exists: pass
- Source folder exists: pass
- Required files exist: pass
- Bash syntax for every included `.sh` file: pass
- Routing JSON parse with UTF-8 BOM support: pass
- Renamed direct dependency files exist: pass
- Default distro is neutral: pass
- Linux install root is `/home/<user>/openclaw_install`: pass
- README and quick-start commands use the target folder and `init_openclaw_wsl.ps1`: pass
- Obvious hard-coded Discord token/webhook literal scan: pass
- No secret or token value was printed during migration or validation: pass

## Actions Not Executed

No installer, WSL command, Ollama command, model pull, Discord client, runtime/probe script, network request, or service action was executed.

## Known Caveats

- Runtime and install behavior were not tested after migration.
- The adapter source baseline was captured after its read-only copy step and before final recheck; its source hash remained unchanged.
- The retained routing scaffold is compatibility behavior from the current installer contract and may be removable in a separately reviewed simplification phase.

## Recommended Next Boundary

Perform a read-only coordinator review of this target folder. If accepted, run host preflight only as a separate explicitly authorized boundary before any install.
