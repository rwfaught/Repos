# init_openclaw_wsl.ps1
#
# PowerShell-led, config-file-driven OpenClaw WSL installer.
# v1.7 supervised wire append.

[CmdletBinding()]
param(
    [switch]$Help,
    [switch]$ShowHelp,
    [switch]$Usage,
    [string]$DistroName = "",
    [string]$LinuxUser = "roger",
    [string]$OpenClawPackageSpec = "openclaw@2026.6.6",
    [string]$OpenClawExpectedIdentity = "",
    [string]$InstallBase = "$env:LOCALAPPDATA\WSL\OpenClaw",
    [string]$CacheDir = "$env:USERPROFILE\Downloads\openclaw-wsl-cache",
    [switch]$ForceRecreate,
    [switch]$RunInstall,
    [switch]$SkipWslUpdate,
    [switch]$RunWslUpdate,
    [switch]$KeepRootfsArchive,
    [switch]$RunHostPreflight,
    [switch]$RunHostPreflightOnly,
    [switch]$ResumeHostPreflight,
    [switch]$AllowWslShutdown,
    [switch]$SkipHostPreflight,
    [switch]$RunMinimalSystemdProbe,
    [string]$MinimalProbeDistroName = "",

    [switch]$IncludeReasoningModel,
    [switch]$IncludeCoderModel,
    [switch]$PromoteReasoningModel,
    [switch]$PromoteCoderModel,
    [switch]$IncludeRiskyModels,
    [switch]$MinimalWireModel,

    [switch]$RunBaselineVerifier,
    [switch]$SkipDashboardVerifier,
    [switch]$RunOptionalModelVerifier,

    [switch]$ConfigureDiscord,
    [string]$DiscordOwnerId = "",
    [string]$DiscordBotTokenFile = "",
    [switch]$DiscordRefreshToken,
    [switch]$RunDiscordVerifier,
    [switch]$SkipDiscordPluginInstall,

    [switch]$RunSupervisedWire,
    [switch]$RunDashboardVerifier,
    [switch]$CopyDashboardAuthUrl,
    [switch]$OpenDashboard,
    [switch]$SkipDashboardAutoOpen,
    [switch]$ResetGatewayToken,
    [switch]$RunWireRatificationReport,

    [string[]]$BootstrapArgs = @()
)

$ErrorActionPreference = "Stop"
$DistroNamePrefix = "OpenClaw-Ubuntu-22.04-"
$OpenClawExpectedIdentityExplicit = $PSBoundParameters.ContainsKey("OpenClawExpectedIdentity")

if (-not ($Help -or $ShowHelp -or $Usage)) {
    if ([string]::IsNullOrWhiteSpace($DistroName)) {
        $DistroName = Read-Host "OpenClaw distro name or suffix"
    }
    $DistroName = $DistroName.Trim()
    if (-not $DistroName.StartsWith($DistroNamePrefix, [StringComparison]::OrdinalIgnoreCase)) {
        $DistroName = "$DistroNamePrefix$DistroName"
    }
    if ($DistroName -notmatch '^OpenClaw-Ubuntu-22\.04-[A-Za-z0-9][A-Za-z0-9._-]*$') {
        throw "DistroName must be a full OpenClaw-Ubuntu-22.04-* name or a suffix containing letters, numbers, dot, underscore, or hyphen."
    }
}

$OpenClawPackageSpec = $OpenClawPackageSpec.Trim()
if ($OpenClawPackageSpec -notmatch '^openclaw@[A-Za-z0-9][A-Za-z0-9._-]*$') {
    throw "OpenClawPackageSpec must look like openclaw@latest or openclaw@2026.6.6."
}

$OpenClawPackageVersion = $OpenClawPackageSpec.Substring("openclaw@".Length)
$OpenClawExpectedBuildId = ""
$OpenClawIdentityPolicy = "package-version"
if ($OpenClawPackageSpec -eq "openclaw@latest" -and -not $OpenClawExpectedIdentityExplicit) {
    $OpenClawExpectedIdentity = ""
    $OpenClawIdentityPolicy = "version-command"
} elseif (-not [string]::IsNullOrWhiteSpace($OpenClawExpectedIdentity)) {
    $OpenClawExpectedIdentity = $OpenClawExpectedIdentity.Trim()
    if ($OpenClawExpectedIdentity -match '\(([A-Za-z0-9]+)\)\s*$') {
        $OpenClawExpectedBuildId = $Matches[1]
    }
    $OpenClawIdentityPolicy = "observed-build-string"
} elseif ($OpenClawPackageSpec -eq "openclaw@2026.6.6") {
    $OpenClawExpectedIdentity = "OpenClaw 2026.6.6 (8c802aa)"
    $OpenClawExpectedBuildId = "8c802aa"
    $OpenClawIdentityPolicy = "observed-build-string"
}

$RootfsUrl = "https://cloud-images.ubuntu.com/wsl/jammy/current/ubuntu-jammy-wsl-amd64-ubuntu22.04lts.rootfs.tar.gz"
$Sha256Url = "https://cloud-images.ubuntu.com/wsl/jammy/current/SHA256SUMS"
$RootfsFile = Join-Path $CacheDir "ubuntu-jammy-wsl-amd64-ubuntu22.04lts.rootfs.tar.gz"
$Sha256File = Join-Path $CacheDir "SHA256SUMS"
$InstallLocation = Join-Path $InstallBase $DistroName
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RunnerScript = Join-Path $ScriptDir "run_openclaw_supervised_wire.sh"
$WatcherScript = Join-Path $ScriptDir "watch_openclaw_wire.ps1"
$RuntimeLauncherScript = Join-Path $ScriptDir "Start-OpenClawRuntime.ps1"
$RoutingScaffoldPayload = @(
    [pscustomobject]@{ Name = "local_worker_routing_v1.json"; Sha256 = "65dc436abeba0dea7fb3ea15366cb1ce52005133d9037fe50fff3770741bbc20" },
    [pscustomobject]@{ Name = "Get-LocalWorkerRoutingConfig_v1.ps1"; Sha256 = "8326d71f3b48b29b605864292655231c5d1eb13d6c904b635e2e86f6c467cb71" },
    [pscustomobject]@{ Name = "Invoke-LocalWorkerRouting_v1.ps1"; Sha256 = "b9a25c0d177471919319b2dd6e814770185b04292d02aa781c33f82c6d53628c" },
    [pscustomobject]@{ Name = "Invoke-LocalWorkerRoutingRuntimeBridge_v1.ps1"; Sha256 = "af864a89fadaf250e5ab397f3ddaa772458ee891e850ebd0f79813b465e4f3f8" }
)
$DistroImportOrRecreateAttempted = $false
$DistroImportOrRecreateResult = "NOT_RUN"
$UserSystemdReadinessAttempted = $false
$UserSystemdReadinessResult = "UNKNOWN"
$UserSystemdReadinessAttempts = 0
$UserSystemdSubstrateProbeAttempted = $false
$UserSystemdSubstrateResult = "NOT_RUN"
$UserSystemdFailureClass = "NONE"
$UserSystemdFailureEvidence = "NONE"
$UserSystemdRecoveryAttempted = "NO"
$UserSystemdLingerState = "UNKNOWN"
$UserSystemdRuntimeDirState = "UNKNOWN"
$UserSystemdBusState = "UNKNOWN"
$InteropAppendWindowsPathPolicy = "appendWindowsPath=false"
$HostPreflightMarkerPath = Join-Path $ScriptDir "host_preflight_marker_v1_7.json"
$ResumeHostPreflightMarker = "NO"
$TargetDistroExistsForResumeMarker = "NO"
$DistroCreateSkippedForResumeMarker = "NO"
$ForceRecreateRequiredMarker = "YES"
$ResumeExistingDistroAllowedMarker = "NO"
$ResumeExistingDistroFlow = $false
$DiscordBotTokenFileResolved = ""
$DiscordBotTokenFileConfigured = $false
$DiscordBotTokenFileWsl = ""
$HostPreflight = [ordered]@{
    hostPreflightAttempted = "false"
    hostPreflightResult = "UNKNOWN"
    hostPreflightTimestamp = "UNKNOWN"
    wslVersionCaptured = "UNKNOWN"
    wslStatusCaptured = "UNKNOWN"
    wslListCaptured = "UNKNOWN"
    hostDistroCountBefore = "UNKNOWN"
    targetDistroExistedBefore = "UNKNOWN"
    runningDistrosDetected = "UNKNOWN"
    forceRecreateRequested = "false"
    allowWslShutdownRequested = "false"
    wslShutdownAttempted = "false"
    wslShutdownResult = "NOT_REQUESTED"
    wslUpdateRequested = "false"
    wslUpdateAttempted = "false"
    wslUpdateResult = "NOT_REQUESTED"
    windowsRebootRecommended = "false"
    resumeSuggested = "false"
    resumeCommand = "UNKNOWN"
    minimalSystemdProbeAttempted = "false"
    minimalSystemdProbeResult = "NOT_REQUESTED"
    minimalUserSystemdProbeAttempted = "false"
    minimalUserSystemdProbeResult = "NOT_REQUESTED"
}

function Write-Step {
    param([string]$Message)
    Write-Host ""
    Write-Host "[openclaw-wsl-init-v1.7] $Message" -ForegroundColor Cyan
}

function Fail {
    param([string]$Message)
    throw "[openclaw-wsl-init-v1.7] ERROR: $Message"
}

function Assert-RoutingScaffoldSourcePayload {
    foreach ($payload in $RoutingScaffoldPayload) {
        $payloadPath = Join-Path $ScriptDir $payload.Name
        if (-not (Test-Path -LiteralPath $payloadPath -PathType Leaf)) {
            Fail "Missing local worker routing scaffold payload beside installer: $($payload.Name)"
        }

        $actualHash = (Get-FileHash -LiteralPath $payloadPath -Algorithm SHA256).Hash.ToLowerInvariant()
        if ($actualHash -ne $payload.Sha256) {
            Fail "Local worker routing scaffold payload hash mismatch: $($payload.Name)"
        }
    }

    $routingConfigPath = Join-Path $ScriptDir "local_worker_routing_v1.json"
    try {
        $routingConfig = Get-Content -LiteralPath $routingConfigPath -Raw | ConvertFrom-Json
    } catch {
        Fail "Local worker routing scaffold config is not valid JSON."
    }

    if ($routingConfig.localWorkerSurface.runtimeIntegrationEnabled -ne $true) {
        Fail "Local worker routing scaffold requires runtimeIntegrationEnabled=true."
    }
    if ($routingConfig.futureIntegration.runtimeConsumptionEnabled -ne $false) {
        Fail "Local worker routing scaffold must keep runtimeConsumptionEnabled=false."
    }
    if ($routingConfig.futureIntegration.routingScriptMutationAllowedHere -ne $false) {
        Fail "Local worker routing scaffold must keep routingScriptMutationAllowedHere=false."
    }

    Write-Host "C45H_ROUTING_SCAFFOLD_SOURCE_VALIDATION=PASS"
    Write-Host "C45H_ROUTING_SCAFFOLD_RUNTIME_INTEGRATION_ENABLED=YES"
    Write-Host "C45H_ROUTING_SCAFFOLD_RUNTIME_CONSUMPTION_ENABLED=NO"
    Write-Host "C45H_ROUTING_SCAFFOLD_SCRIPT_MUTATION_ALLOWED=NO"
}

function Invoke-External {
    param(
        [Parameter(Mandatory=$true)]
        [string]$FilePath,
        [Parameter(ValueFromRemainingArguments=$true)]
        [string[]]$Arguments
    )
    & $FilePath @Arguments
    if ($LASTEXITCODE -ne 0) {
        Fail "Command failed: $FilePath $($Arguments -join ' ')"
    }
}

function Invoke-SupervisedWireInstall {
    param(
        [Parameter(Mandatory=$true)][string]$DistroNameValue,
        [Parameter(Mandatory=$true)][string]$LinuxUserValue
    )

    $monitorProcess = $null
    $fallbackCommand = "powershell -ExecutionPolicy Bypass -File .\watch_openclaw_wire.ps1 -DistroName `"$DistroNameValue`" -CopyDashboardUrl -OpenDashboard"

    if (-not $SkipDashboardAutoOpen) {
        if (-not (Test-Path -LiteralPath $WatcherScript -PathType Leaf)) {
            Fail "Dashboard watcher is missing: $WatcherScript"
        }

        $monitorStartedAt = [DateTimeOffset]::UtcNow.ToString("o")
        $monitorArgs = @(
            "-NoProfile",
            "-ExecutionPolicy", "Bypass",
            "-File", "`"$WatcherScript`"",
            "-DistroName", "`"$DistroNameValue`"",
            "-LinuxUser", "`"$LinuxUserValue`"",
            "-AutoOpenAtDashboard",
            "-NotBeforeUtc", "`"$monitorStartedAt`"",
            "-ParentProcessId", "$PID"
        )

        Write-Host "Windows dashboard auto-open monitor enabled."
        Write-Host "If authenticated dashboard auto-open fails, run:"
        Write-Host "  $fallbackCommand"
        $monitorProcess = Start-Process -FilePath "powershell.exe" -ArgumentList $monitorArgs -WindowStyle Hidden -PassThru
    } else {
        Write-Host "Dashboard auto-open skipped by request."
        Write-Host "Manual authenticated dashboard command:"
        Write-Host "  $fallbackCommand"
    }

    $installerExitCode = 1
    try {
        & wsl.exe --distribution $DistroNameValue --user $LinuxUserValue -- bash -lc "cd /home/$LinuxUserValue/openclaw_install/package && bash ./run_openclaw_supervised_wire.sh --config /home/$LinuxUserValue/openclaw_install/config/install_config.json"
        $installerExitCode = $LASTEXITCODE
    } finally {
        if ($null -ne $monitorProcess -and -not $monitorProcess.HasExited) {
            Stop-Process -Id $monitorProcess.Id -ErrorAction SilentlyContinue
        }
    }

    if ($installerExitCode -ne 0) {
        Fail "Supervised installer failed with exit code $installerExitCode. Post-install checks were not run."
    }

    if (-not (Test-Path -LiteralPath $RuntimeLauncherScript -PathType Leaf)) {
        Fail "Runtime launcher is missing: $RuntimeLauncherScript"
    }

    Write-Step "Starting persistent Windows-side OpenClaw runtime keepalive"
    $runtimeLauncherArgs = @(
        "-NoProfile",
        "-ExecutionPolicy", "Bypass",
        "-File", $RuntimeLauncherScript,
        "-DistroName", $DistroNameValue,
        "-LinuxUser", $LinuxUserValue
    )
    if ($RunDiscordVerifier) {
        $runtimeLauncherArgs += "-RequireDiscord"
    }
    & powershell.exe @runtimeLauncherArgs
    if ($LASTEXITCODE -ne 0) {
        Fail "OpenClaw runtime keepalive/readiness failed. Installer completion was not declared."
    }

    $safeRuntimeDistroName = $DistroNameValue -replace '[^A-Za-z0-9_.-]', '_'
    $runtimePidPath = Join-Path (Join-Path $ScriptDir "runtime") "openclaw_runtime_${safeRuntimeDistroName}.pid"
    if (-not (Test-Path -LiteralPath $runtimePidPath -PathType Leaf)) {
        Fail "OpenClaw runtime keepalive PID file was not created. Installer completion was not declared."
    }
    $runtimePidRaw = (Get-Content -LiteralPath $runtimePidPath -Raw).Trim()
    $runtimePid = 0
    if (-not [int]::TryParse($runtimePidRaw, [ref]$runtimePid)) {
        Fail "OpenClaw runtime keepalive PID file is invalid. Installer completion was not declared."
    }
    Start-Sleep -Seconds 5
    $runtimeProcess = Get-CimInstance Win32_Process -Filter "ProcessId = $runtimePid" -ErrorAction SilentlyContinue
    $runtimeCommandLine = if ($null -eq $runtimeProcess) { "" } else { [string]$runtimeProcess.CommandLine }
    $runtimeProcessMatches = (
        $null -ne $runtimeProcess -and
        $runtimeCommandLine.Contains("Start-OpenClawRuntime.ps1") -and
        $runtimeCommandLine.Contains("-KeepAliveLoop") -and
        $runtimeCommandLine.Contains($DistroNameValue)
    )
    if (-not $runtimeProcessMatches) {
        Fail "OpenClaw runtime keepalive PID $runtimePid did not survive delayed verification. Installer completion was not declared."
    }
    Write-Host "OpenClaw runtime keepalive Windows process verified: PID $runtimePid"

    $runtimeStatusArgs = @(
        "-NoProfile",
        "-ExecutionPolicy", "Bypass",
        "-File", $RuntimeLauncherScript,
        "-DistroName", $DistroNameValue,
        "-LinuxUser", $LinuxUserValue,
        "-Status"
    )
    if ($RunDiscordVerifier) {
        $runtimeStatusArgs += "-RequireDiscord"
    }
    & powershell.exe @runtimeStatusArgs
    if ($LASTEXITCODE -ne 0) {
        Fail "OpenClaw runtime live status validation failed after delayed PID verification. Installer completion was not declared."
    }
    Write-Host "OpenClaw runtime wrapper, WSL anchor, distro, gateway, and channel readiness verified."
}

function Write-HostPreflightMarker {
    param([object]$MarkerData)
    $MarkerData.hostPreflightTimestamp = [DateTimeOffset]::UtcNow.ToString("o")
    $markerJson = $MarkerData | ConvertTo-Json -Depth 8
    Set-Content -Path $HostPreflightMarkerPath -Value $markerJson -Encoding UTF8
}

function Write-ResumeProofMarkers {
    Write-Host "RESUME_HOST_PREFLIGHT=$ResumeHostPreflightMarker"
    Write-Host "TARGET_DISTRO_EXISTS_FOR_RESUME=$TargetDistroExistsForResumeMarker"
    Write-Host "DISTRO_CREATE_SKIPPED_FOR_RESUME=$DistroCreateSkippedForResumeMarker"
    Write-Host "FORCE_RECREATE_REQUIRED=$ForceRecreateRequiredMarker"
    Write-Host "RESUME_EXISTING_DISTRO_ALLOWED=$ResumeExistingDistroAllowedMarker"
}

function Read-HostPreflightMarker {
    if (Test-Path $HostPreflightMarkerPath) {
        try {
            $raw = Get-Content -Raw -Path $HostPreflightMarkerPath | ConvertFrom-Json
            foreach ($prop in $raw.PSObject.Properties.Name) {
                $HostPreflight[$prop] = [string]$raw.$prop
            }
        } catch {
            Write-Warning "Existing host preflight marker is not valid JSON. Continuing with new marker data."
        }
    }
}

function Get-ResumeCommand {
    $resumeArgs = @("-ExecutionPolicy","Bypass","-File",".\init_openclaw_wsl.ps1")
    foreach ($k in $PSBoundParameters.Keys) {
        if ($k -in @("RunHostPreflightOnly","RunHostPreflight","SkipHostPreflight","AllowWslShutdown","RunWslUpdate")) { continue }
        $v = $PSBoundParameters[$k]
        if ($v -is [switch]) {
            if ($v.IsPresent) { $resumeArgs += "-$k" }
        } elseif ($null -ne $v -and "$v" -ne "") {
            $resumeArgs += "-$k"
            $resumeArgs += "`"$v`""
        }
    }
    if ($resumeArgs -notcontains "-ResumeHostPreflight") { $resumeArgs += "-ResumeHostPreflight" }
    return "powershell " + ($resumeArgs -join " ")
}

function Try-StageHostPreflightMarkerToWsl {
    param(
        [string]$DistroNameValue,
        [string]$LinuxUserValue
    )
    if (-not (Test-Path $HostPreflightMarkerPath)) { return }
    $distros = Get-WslDistros
    if (-not ($distros -contains $DistroNameValue)) { return }
    $markerJson = Get-Content -Raw -Path $HostPreflightMarkerPath
    $encoded = [Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes($markerJson))
    $cmd = "install -d -m 0755 /home/$LinuxUserValue/openclaw_install/config && echo $encoded | base64 -d > /home/$LinuxUserValue/openclaw_install/config/host_preflight_marker_v1_7.json && chown ${LinuxUserValue}:${LinuxUserValue} /home/$LinuxUserValue/openclaw_install/config/host_preflight_marker_v1_7.json && chmod 0644 /home/$LinuxUserValue/openclaw_install/config/host_preflight_marker_v1_7.json"
    Invoke-External wsl.exe --distribution $DistroNameValue --user root -- bash -lc $cmd
}

function Invoke-MinimalSystemdProbe {
    param(
        [string]$ProbeDistroName,
        [string]$ProbeLinuxUser
    )
    $HostPreflight.minimalSystemdProbeAttempted = "true"
    $HostPreflight.minimalUserSystemdProbeAttempted = "true"
    $distros = Get-WslDistros
    if (-not ($distros -contains $ProbeDistroName)) {
        $HostPreflight.minimalSystemdProbeResult = "DISTRO_NOT_FOUND"
        $HostPreflight.minimalUserSystemdProbeResult = "DISTRO_NOT_FOUND"
        return
    }
    $probeScript = @'
set -euo pipefail
pid1=$(ps -p 1 -o comm= | tr -d '[:space:]')
if [[ "$pid1" != "systemd" ]]; then
  echo "PID1_NOT_SYSTEMD"
  exit 101
fi
grep -q '^\[boot\]' /etc/wsl.conf && grep -q '^systemd=true' /etc/wsl.conf || { echo "WSL_CONF_SYSTEMD_MISSING"; exit 102; }
systemctl is-system-running >/tmp/orch_systemd_state.out 2>&1 || true
id -u "__LINUX_USER__" >/dev/null 2>&1 || { echo "USER_MISSING"; exit 103; }
if command -v loginctl >/dev/null 2>&1; then loginctl enable-linger "__LINUX_USER__" >/dev/null 2>&1 || true; fi
runuser -u "__LINUX_USER__" -- systemctl --user show-environment >/dev/null 2>&1 || { echo "USER_SYSTEMD_UNREACHABLE"; exit 104; }
echo "PROBE_PASS"
'@
    $probeScript = $probeScript.Replace("__LINUX_USER__", $ProbeLinuxUser)
    $encoded = [Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes($probeScript))
    & wsl.exe --distribution $ProbeDistroName --user root -- bash -lc "echo $encoded | base64 -d | bash"
    if ($LASTEXITCODE -eq 0) {
        $HostPreflight.minimalSystemdProbeResult = "PASS"
        $HostPreflight.minimalUserSystemdProbeResult = "PASS"
    } else {
        $HostPreflight.minimalSystemdProbeResult = "FAIL"
        $HostPreflight.minimalUserSystemdProbeResult = "HOST_WSL_USER_SYSTEMD_UNHEALTHY"
    }
}

function Invoke-HostPreflight {
    param(
        [string]$TargetDistroName,
        [string]$TargetLinuxUser
    )
    $HostPreflight.hostPreflightAttempted = "true"
    $HostPreflight.forceRecreateRequested = ([bool]$ForceRecreate).ToString().ToLower()
    $HostPreflight.allowWslShutdownRequested = ([bool]$AllowWslShutdown).ToString().ToLower()
    $HostPreflight.wslUpdateRequested = ([bool]$RunWslUpdate).ToString().ToLower()
    $HostPreflight.resumeCommand = Get-ResumeCommand
    $HostPreflight.resumeSuggested = "false"
    $HostPreflight.windowsRebootRecommended = "false"
    $HostPreflight.hostPreflightResult = "IN_PROGRESS"

    $wslVersionRaw = (& wsl.exe --version 2>&1) -join "`n"
    if ($LASTEXITCODE -eq 0 -and -not [string]::IsNullOrWhiteSpace($wslVersionRaw)) { $HostPreflight.wslVersionCaptured = "true" }
    $wslStatusRaw = (& wsl.exe --status 2>&1) -join "`n"
    if ($LASTEXITCODE -eq 0 -and -not [string]::IsNullOrWhiteSpace($wslStatusRaw)) { $HostPreflight.wslStatusCaptured = "true" }
    $wslListRaw = (& wsl.exe --list --verbose 2>&1) -join "`n"
    if ($LASTEXITCODE -eq 0 -and -not [string]::IsNullOrWhiteSpace($wslListRaw)) { $HostPreflight.wslListCaptured = "true" }

    $existingDistros = Get-WslDistros
    $HostPreflight.hostDistroCountBefore = "$($existingDistros.Count)"
    $HostPreflight.targetDistroExistedBefore = ($existingDistros -contains $TargetDistroName).ToString().ToLower()
    $runningDetected = [bool]($wslListRaw -match 'Running')
    $HostPreflight.runningDistrosDetected = $runningDetected.ToString().ToLower()

    if ($RunWslUpdate) {
        $HostPreflight.wslUpdateAttempted = "true"
        & wsl.exe --update | Out-Null
        if ($LASTEXITCODE -eq 0) { $HostPreflight.wslUpdateResult = "PASS" } else { $HostPreflight.wslUpdateResult = "FAIL" }
    }

    if ($runningDetected) {
        if ($AllowWslShutdown) {
            $HostPreflight.wslShutdownAttempted = "true"
            & wsl.exe --shutdown | Out-Null
            if ($LASTEXITCODE -eq 0) { $HostPreflight.wslShutdownResult = "PASS" } else { $HostPreflight.wslShutdownResult = "FAIL" }
            Start-Sleep -Seconds 3
        } else {
            $HostPreflight.wslShutdownAttempted = "false"
            $HostPreflight.wslShutdownResult = "NOT_AUTHORIZED"
            $HostPreflight.resumeSuggested = "true"
        }
    }

    if ($RunMinimalSystemdProbe) {
        $probeDistro = if ([string]::IsNullOrWhiteSpace($MinimalProbeDistroName)) { $TargetDistroName } else { $MinimalProbeDistroName }
        Invoke-MinimalSystemdProbe -ProbeDistroName $probeDistro -ProbeLinuxUser $TargetLinuxUser
    }

    $needsStop = $false
    if ($HostPreflight.wslShutdownResult -eq "NOT_AUTHORIZED" -or $HostPreflight.wslShutdownResult -eq "FAIL") {
        $HostPreflight.windowsRebootRecommended = "true"
        $HostPreflight.resumeSuggested = "true"
        $HostPreflight.hostPreflightResult = "REBOOT_REQUIRED"
        $needsStop = $true
    }
    if ($HostPreflight.minimalUserSystemdProbeResult -eq "HOST_WSL_USER_SYSTEMD_UNHEALTHY") {
        $HostPreflight.windowsRebootRecommended = "true"
        $HostPreflight.resumeSuggested = "true"
        $HostPreflight.hostPreflightResult = "HOST_WSL_USER_SYSTEMD_UNHEALTHY"
        $needsStop = $true
    }
    if (-not $needsStop) {
        $HostPreflight.hostPreflightResult = "PASS"
    }
    Write-HostPreflightMarker -MarkerData $HostPreflight
    if ($needsStop) {
        Write-Host ""
        Write-Host "WSL host preflight indicates recovery is required before continuing." -ForegroundColor Yellow
        Write-Host "Recommended command: wsl --shutdown"
        Write-Host "If issue persists, perform a full Windows reboot."
        Write-Host "Resume with:"
        Write-Host "  $($HostPreflight.resumeCommand)"
        if ($RunHostPreflightOnly -or $RunHostPreflight -or $RunSupervisedWire) {
            Fail "HOST_PREFLIGHT_RECOVERY_REQUIRED"
        }
    }
}

function Write-ConductorMarker {
    param(
        [string]$DistroNameValue,
        [string]$LinuxUserValue,
        [bool]$RunSupervisedWireValue,
        [bool]$ForceRecreateValue,
        [bool]$DistroImportAttemptedValue,
        [string]$DistroImportResultValue,
        [bool]$UserSystemdReadinessAttemptedValue,
        [string]$UserSystemdReadinessResultValue,
        [int]$UserSystemdReadinessAttemptsValue,
        [bool]$UserSystemdSubstrateProbeAttemptedValue,
        [string]$UserSystemdSubstrateResultValue,
        [string]$UserSystemdFailureClassValue,
        [string]$UserSystemdFailureEvidenceValue,
        [string]$UserSystemdRecoveryAttemptedValue,
        [string]$UserSystemdLingerStateValue,
        [string]$UserSystemdRuntimeDirStateValue,
        [string]$UserSystemdBusStateValue,
        [string]$InteropAppendWindowsPathPolicyValue,
        [string]$ResumeHostPreflightValue,
        [string]$TargetDistroExistsForResumeValue,
        [string]$DistroCreateSkippedForResumeValue,
        [string]$ForceRecreateRequiredValue,
        [string]$ResumeExistingDistroAllowedValue
    )

    $markerObject = [ordered]@{
        distroName = $DistroNameValue
        linuxUser = $LinuxUserValue
        packageVersion = "v1.7"
        runSupervisedWire = $RunSupervisedWireValue
        forceRecreate = $ForceRecreateValue
        distroImportOrRecreateAttempted = $DistroImportAttemptedValue
        distroImportOrRecreateResult = $DistroImportResultValue
        userSystemdReadinessAttempted = $UserSystemdReadinessAttemptedValue
        userSystemdReadinessResult = $UserSystemdReadinessResultValue
        userSystemdReadinessAttempts = $UserSystemdReadinessAttemptsValue
        userSystemdSubstrateProbeAttempted = $UserSystemdSubstrateProbeAttemptedValue
        userSystemdSubstrateResult = $UserSystemdSubstrateResultValue
        userSystemdFailureClass = $UserSystemdFailureClassValue
        userSystemdFailureEvidence = $UserSystemdFailureEvidenceValue
        userSystemdRecoveryAttempted = $UserSystemdRecoveryAttemptedValue
        userSystemdLingerState = $UserSystemdLingerStateValue
        userSystemdRuntimeDirState = $UserSystemdRuntimeDirStateValue
        userSystemdBusState = $UserSystemdBusStateValue
        interopAppendWindowsPathPolicy = $InteropAppendWindowsPathPolicyValue
        resumeHostPreflight = $ResumeHostPreflightValue
        targetDistroExistsForResume = $TargetDistroExistsForResumeValue
        distroCreateSkippedForResume = $DistroCreateSkippedForResumeValue
        forceRecreateRequired = $ForceRecreateRequiredValue
        resumeExistingDistroAllowed = $ResumeExistingDistroAllowedValue
        timestamp = [DateTimeOffset]::UtcNow.ToString("o")
    }
    $markerJson = $markerObject | ConvertTo-Json -Depth 6
    $encodedMarker = [Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes($markerJson))
    $markerCmd = "echo $encodedMarker | base64 -d > /home/$LinuxUserValue/openclaw_install/config/conductor_marker_v1_7.json && chown ${LinuxUserValue}:${LinuxUserValue} /home/$LinuxUserValue/openclaw_install/config/conductor_marker_v1_7.json && chmod 0644 /home/$LinuxUserValue/openclaw_install/config/conductor_marker_v1_7.json"
    Invoke-External wsl.exe --distribution $DistroNameValue --user root -- bash -lc $markerCmd
}

function Get-UserSystemdProbeResult {
    param(
        [Parameter(Mandatory=$true)][string]$DistroNameValue,
        [Parameter(Mandatory=$true)][string]$LinuxUserValue
    )

    $probeScript = @'
set -uo pipefail
linux_user="__LINUX_USER__"
uid="$(id -u "$linux_user" 2>/dev/null || echo 1000)"
runtime_dir="/run/user/${uid}"
bus_path="${runtime_dir}/bus"
pid1_comm="$(ps -p 1 -o comm= 2>/dev/null || true)"
systemd_state="$(systemctl is-system-running 2>&1 || true)"
linger_state="UNKNOWN"
loginctl_state="UNKNOWN"
loginctl_runtime_path="UNKNOWN"
if command -v loginctl >/dev/null 2>&1; then
  linger_state="$(loginctl show-user "$linux_user" -p Linger --value 2>/dev/null || true)"
  loginctl_state="$(loginctl show-user "$linux_user" -p State --value 2>/dev/null || true)"
  loginctl_runtime_path="$(loginctl show-user "$linux_user" -p RuntimePath --value 2>/dev/null || true)"
fi
runtime_dir_state="MISSING"
[[ -d "$runtime_dir" ]] && runtime_dir_state="PRESENT"
bus_state="MISSING"
[[ -S "$bus_path" ]] && bus_state="PRESENT"
set +e
user_output="$(
  runuser -u "$linux_user" -- env \
    HOME="/home/$linux_user" \
    USER="$linux_user" \
    LOGNAME="$linux_user" \
    PATH="/usr/lib/wsl/lib:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin" \
    XDG_RUNTIME_DIR="$runtime_dir" \
    DBUS_SESSION_BUS_ADDRESS="unix:path=$bus_path" \
    bash -lc 'systemctl --user show-environment 2>&1'
)"
user_rc=$?
set -e
unit_state="$(systemctl is-active "user@${uid}.service" 2>&1 || true)"
unit_status="$(systemctl status "user@${uid}.service" --no-pager 2>&1 || true)"
unit_journal="$(journalctl -u "user@${uid}.service" -n 80 --no-pager 2>&1 || true)"
failure_blob="$user_output
$unit_state
$unit_status
$unit_journal"
classification="PASS"
evidence="none"
if [[ "$user_rc" -ne 0 ]]; then
  classification="USER_SYSTEMD_NOT_READY"
  evidence="systemctl-user-show-environment-nonzero"
  if printf '%s' "$failure_blob" | grep -Eq '219/CGROUP|Device or resource busy|Failed to attach to cgroup'; then
    classification="HOST_WSL_USER_SYSTEMD_CGROUP_BUSY"
    evidence="219/CGROUP-or-Device-or-resource-busy"
  elif printf '%s' "$failure_blob" | grep -Eq 'Failed to connect to bus|No medium found'; then
    classification="USER_SYSTEMD_BUS_UNAVAILABLE"
    evidence="failed-to-connect-to-bus"
  elif [[ "$runtime_dir_state" != "PRESENT" ]]; then
    classification="USER_SYSTEMD_RUNTIME_DIR_MISSING"
    evidence="runtime-dir-missing"
  elif [[ "$bus_state" != "PRESENT" ]]; then
    classification="USER_SYSTEMD_BUS_SOCKET_MISSING"
    evidence="bus-socket-missing"
  elif printf '%s' "$failure_blob" | grep -Eq 'not logged in or lingering'; then
    classification="USER_SYSTEMD_LINGER_OR_LOGIN_SESSION_MISSING"
    evidence="not-logged-in-or-lingering"
  fi
fi
echo "PID1_COMM=${pid1_comm:-UNKNOWN}"
echo "SYSTEMD_STATE=${systemd_state:-UNKNOWN}"
echo "USER_SHOW_ENV_RC=${user_rc}"
echo "LOGINCTL_LINGER=${linger_state:-UNKNOWN}"
echo "LOGINCTL_STATE=${loginctl_state:-UNKNOWN}"
echo "LOGINCTL_RUNTIME_PATH=${loginctl_runtime_path:-UNKNOWN}"
echo "RUNTIME_DIR_STATE=${runtime_dir_state}"
echo "BUS_STATE=${bus_state}"
echo "CLASSIFICATION=${classification}"
echo "EVIDENCE=${evidence}"
'@
    $probeScript = $probeScript.Replace("__LINUX_USER__", $LinuxUserValue)
    $probeCmd = "echo " + [Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes($probeScript)) + " | base64 -d | bash"
    $probeOutput = & wsl.exe --distribution $DistroNameValue --user root -- bash -lc $probeCmd
    if ($LASTEXITCODE -ne 0) {
        throw "User-systemd probe failed to execute for distro '$DistroNameValue'."
    }

    $result = [ordered]@{
        pid1_comm = "UNKNOWN"
        systemd_state = "UNKNOWN"
        user_show_env_rc = "1"
        loginctl_linger = "UNKNOWN"
        loginctl_state = "UNKNOWN"
        loginctl_runtime_path = "UNKNOWN"
        runtime_dir_state = "UNKNOWN"
        bus_state = "UNKNOWN"
        classification = "USER_SYSTEMD_PROBE_FAILED"
        evidence = "probe-output-missing"
    }
    foreach ($line in $probeOutput) {
        if ($line -match '^(?<key>[A-Z0-9_]+)=(?<value>.*)$') {
            $result[$matches['key'].ToLower()] = $matches['value']
        }
    }
    return $result
}

function Get-WslDistros {
    $raw = & wsl.exe --list --quiet 2>$null
    if ($LASTEXITCODE -ne 0) {
        return @()
    }
    return @($raw | ForEach-Object { ($_ -replace "`0","").Trim() } | Where-Object { $_ })
}

function Convert-WindowsPathToWslPath {
    param([Parameter(Mandatory=$true)][string]$Path)
    $full = (Resolve-Path $Path).Path
    $drive = $full.Substring(0,1).ToLower()
    $rest = $full.Substring(2).Replace("\","/")
    return "/mnt/$drive$rest"
}

function ShellQuote {
    param([string]$s)
    return "'" + ($s -replace "'", "'\''") + "'"
}

function Resolve-DiscordBotTokenFile {
    param([string]$Path)
    if ([string]::IsNullOrWhiteSpace($Path)) {
        return $null
    }
    $resolved = (Resolve-Path -LiteralPath $Path).Path
    $content = [System.IO.File]::ReadAllText($resolved)
    $trimmed = $content.Trim()
    if ([string]::IsNullOrWhiteSpace($trimmed)) {
        Fail "Discord bot token file is empty: $resolved"
    }
    return [ordered]@{
        ResolvedPath = $resolved
        TokenValue = $trimmed
    }
}

function Stage-DiscordBotTokenIntoWsl {
    param(
        [Parameter(Mandatory=$true)][string]$DistroNameValue,
        [Parameter(Mandatory=$true)][string]$LinuxUserValue,
        [Parameter(Mandatory=$true)][string]$TokenValue,
        [Parameter(Mandatory=$true)][string]$TargetPath
    )

    function Get-PosixParentPath {
        param([Parameter(Mandatory=$true)][string]$PathValue)

        $p = $PathValue.Trim()
        if ([string]::IsNullOrWhiteSpace($p)) {
            Fail "Empty POSIX path"
        }
        if ($p -notmatch '^/') {
            Fail "Expected absolute POSIX path"
        }
        if ($p -match '\\') {
            Fail "Unexpected backslash in POSIX path"
        }

        $trimmed = $p.TrimEnd('/')
        if ($trimmed -eq "" -or $trimmed -eq "/") {
            Fail "Cannot derive parent for POSIX root"
        }

        $idx = $trimmed.LastIndexOf('/')
        if ($idx -le 0) {
            return "/"
        }
        return $trimmed.Substring(0, $idx)
    }

    $targetDir = Get-PosixParentPath -PathValue $TargetPath
    $openclawDir = Get-PosixParentPath -PathValue $targetDir

    function Invoke-TokenStageWslPhase {
        param(
            [Parameter(Mandatory=$true)][string]$PhaseName,
            [Parameter(Mandatory=$true)][string[]]$CommandArgs,
            [string]$InputText
        )

        $wslArgs = @("--distribution", $DistroNameValue, "--user", "root", "--") + $CommandArgs

        try {
            if ($PSBoundParameters.ContainsKey("InputText")) {
                $phaseOutput = $InputText | & wsl.exe @wslArgs 2>&1
            } else {
                $phaseOutput = & wsl.exe @wslArgs 2>&1
            }
            $phaseRc = $LASTEXITCODE
        } catch {
            Fail "Failed to launch wsl.exe for Discord token staging during ${PhaseName}: $($_.Exception.Message)"
        }

        if ($phaseRc -ne 0) {
            $detail = ($phaseOutput | Out-String).Trim()
            if ([string]::IsNullOrWhiteSpace($detail)) {
                $detail = "exit code $phaseRc"
            }
            Fail "Failed to stage Discord bot token file into WSL during ${PhaseName}: $detail"
        }
    }

    Invoke-TokenStageWslPhase -PhaseName "prep-directories" -CommandArgs @("install", "-d", "-m", "0700", $openclawDir, $targetDir)
    Invoke-TokenStageWslPhase -PhaseName "prep-directory-owner" -CommandArgs @("chown", "${LinuxUserValue}:${LinuxUserValue}", $openclawDir, $targetDir)
    Invoke-TokenStageWslPhase -PhaseName "prep-directory-permissions" -CommandArgs @("chmod", "700", $openclawDir, $targetDir)

    $writeCode = 'import sys;open(sys.argv[1],chr(119)+chr(98)).write(sys.stdin.buffer.read().rstrip(bytes([13,10])))'
    Invoke-TokenStageWslPhase -PhaseName "write-token-stdin" -CommandArgs @("python3", "-c", $writeCode, $TargetPath) -InputText $TokenValue

    Invoke-TokenStageWslPhase -PhaseName "finalize-file-owner" -CommandArgs @("chown", "${LinuxUserValue}:${LinuxUserValue}", $TargetPath)
    Invoke-TokenStageWslPhase -PhaseName "finalize-file-permissions" -CommandArgs @("chmod", "600", $TargetPath)
    Invoke-TokenStageWslPhase -PhaseName "finalize-nonempty-check" -CommandArgs @("test", "-s", $TargetPath)
}

function Download-FileWithRetry {
    param(
        [Parameter(Mandatory=$true)][string]$Uri,
        [Parameter(Mandatory=$true)][string]$OutFile,
        [int]$Retries = 3
    )

    for ($i = 1; $i -le $Retries; $i++) {
        try {
            Invoke-WebRequest -Uri $Uri -OutFile $OutFile
            return
        } catch {
            if ($i -eq $Retries) { throw }
            Write-Warning "Download failed on attempt $i/$Retries. Retrying..."
            Start-Sleep -Seconds 3
        }
    }
}

function Show-UsageText {
    $cmdMinimal = @'
powershell -ExecutionPolicy Bypass -File .\init_openclaw_wsl.ps1 `
  -DistroName "<name-or-suffix>" `
  -OpenClawPackageSpec "openclaw@2026.6.6" `
  -ForceRecreate `
  -RunSupervisedWire `
  -AllowWslShutdown `
  -MinimalWireModel `
  -DiscordOwnerId "<your_discord_user_id>" `
  -DiscordBotTokenFile "$env:USERPROFILE\.config\openclaw\secrets\discord_bot_token.txt"
'@
    $cmdFull = @'
powershell -ExecutionPolicy Bypass -File .\init_openclaw_wsl.ps1 `
  -DistroName "<name-or-suffix>" `
  -OpenClawPackageSpec "openclaw@2026.6.6" `
  -ForceRecreate `
  -RunSupervisedWire `
  -AllowWslShutdown `
  -DiscordOwnerId "<your_discord_user_id>" `
  -DiscordBotTokenFile "$env:USERPROFILE\.config\openclaw\secrets\discord_bot_token.txt"
'@
    $cmdPreflight = @'
powershell -ExecutionPolicy Bypass -File .\init_openclaw_wsl.ps1 `
  -DistroName "<name-or-suffix>" `
  -RunHostPreflightOnly `
  -RunWslUpdate `
  -AllowWslShutdown
'@
    $cmdResume = @'
powershell -ExecutionPolicy Bypass -File .\init_openclaw_wsl.ps1 `
  -DistroName "<name-or-suffix>" `
  -ResumeHostPreflight `
  -RunSupervisedWire `
  -AllowWslShutdown
'@
    $watchStatus = @'
powershell -ExecutionPolicy Bypass -File .\watch_openclaw_wire.ps1 `
  -DistroName "OpenClaw-Ubuntu-22.04-<name>" `
  -Status
'@
    $watchLive = @'
powershell -ExecutionPolicy Bypass -File .\watch_openclaw_wire.ps1 `
  -DistroName "OpenClaw-Ubuntu-22.04-<name>" `
  -Watch
'@
    $watchCanonical = @'
wsl.exe --distribution OpenClaw-Ubuntu-22.04-<name> --user roger -- bash -lc "tail -n 80 -F /home/roger/openclaw_install/logs/<run_timestamp>/runner.log /home/roger/openclaw_install/logs/<run_timestamp>/bootstrap.log /home/roger/openclaw_install/logs/<run_timestamp>/openclaw_npm_install.log 2>/dev/null"
'@
    $watchPattern = @'
$Current_log_number = "<run_timestamp>"
wsl.exe --distribution OpenClaw-Ubuntu-22.04-<name> --user roger -- bash -lc "tail -n 80 -F /home/roger/openclaw_install/logs/$Current_log_number/runner.log /home/roger/openclaw_install/logs/$Current_log_number/bootstrap.log /home/roger/openclaw_install/logs/$Current_log_number/openclaw_npm_install.log 2>/dev/null"
'@
    Write-Host ""
    Write-Host "OpenClaw WSL/OpenClaw v1.7 Usage" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Minimal wire command (transport proof tier):"
    Write-Host $cmdMinimal
    Write-Host "Full safe command (default safe_full tier):"
    Write-Host $cmdFull
    Write-Host "Preflight-only command:"
    Write-Host $cmdPreflight
    Write-Host "Resume-host-preflight command:"
    Write-Host $cmdResume
    Write-Host ""
    Write-Host "-MinimalWireModel means:"
    Write-Host "  Uses only qwen3:0.6b with its non-4K context for essential wire proof."
    Write-Host "  It does not claim full safe-model ratification."
    Write-Host ""
    Write-Host "Human gates you should expect:"
    Write-Host "  1) Dashboard auth URL/token handoff"
    Write-Host "  2) Dashboard proof prompt"
    Write-Host "  3) Discord bot token entry or staged local token file"
    Write-Host "  4) Discord pairing approval (if prompted)"
    Write-Host "  5) Discord manual message proof"
    Write-Host ""
    Write-Host "Watcher/status commands:"
    Write-Host $watchStatus
    Write-Host $watchLive
    Write-Host "Canonical watcher tail command:"
    Write-Host $watchCanonical
    Write-Host "Practical PowerShell watcher pattern:"
    Write-Host $watchPattern
    Write-Host "Dashboard auth helper (copy/open):"
    Write-Host "  powershell -ExecutionPolicy Bypass -File .\watch_openclaw_wire.ps1 -DistroName ""OpenClaw-Ubuntu-22.04-<name>"" -CopyDashboardUrl -OpenDashboard"
    Write-Host ""
    Write-Host "If installer appears silent:"
    Write-Host "  Do not stop installer immediately; check watcher/status output and operator_state_v1_7.json."
    Write-Host "  Stop watcher windows with Ctrl+C; this does not stop the installer."
    Write-Host ""
    Write-Host "Secret safety:"
    Write-Host "  Never paste secrets into watcher windows or logs."
    Write-Host "  Prefer -DiscordBotTokenFile for local secret-file input."
    Write-Host "  If no token file is supplied, paste Discord token only into the foreground installer human-gate prompt."
    Write-Host "  Discord token input is hidden and should not be printed."
    Write-Host "  Tokens should not appear in markers/reports/operator state."
    Write-Host ""
}

if ($Help -or $ShowHelp -or $Usage) {
    Show-UsageText
    exit 0
}
if ($ConfigureDiscord -and [string]::IsNullOrWhiteSpace($DiscordOwnerId)) {
    Fail "-ConfigureDiscord requires -DiscordOwnerId <your Discord user id>."
}
if ($RunDiscordVerifier -and [string]::IsNullOrWhiteSpace($DiscordOwnerId)) {
    Fail "-RunDiscordVerifier requires -DiscordOwnerId <your Discord user id>."
}
if ($RunSupervisedWire) {
    $RunInstall = $true
    $RunBaselineVerifier = $true
    $RunDashboardVerifier = $true
    $RunWireRatificationReport = $true
    if (-not $SkipDashboardAutoOpen) {
        $CopyDashboardAuthUrl = $true
        $OpenDashboard = $true
    }
    $SkipDashboardVerifier = $false
    if (-not [string]::IsNullOrWhiteSpace($DiscordOwnerId)) {
        $ConfigureDiscord = $true
        $RunDiscordVerifier = $true
    }
    if (-not $SkipHostPreflight) {
        $RunHostPreflight = $true
    }
}

if ($RunWslUpdate -and $SkipWslUpdate) {
    Fail "Use either -RunWslUpdate or -SkipWslUpdate, not both."
}

if (-not [string]::IsNullOrWhiteSpace($DiscordBotTokenFile)) {
    $resolvedDiscordTokenFile = Resolve-DiscordBotTokenFile -Path $DiscordBotTokenFile
    $DiscordBotTokenFileResolved = [string]$resolvedDiscordTokenFile.ResolvedPath
    $DiscordBotTokenFileConfigured = $true
}

if ($ResumeHostPreflight) {
    Read-HostPreflightMarker
}

if (-not (Test-Path $RunnerScript)) {
    Fail "Missing package runner beside PS1: $RunnerScript"
}

Write-Step "Validating local worker routing scaffold source payload"
Assert-RoutingScaffoldSourcePayload

Write-Step "Checking WSL availability"
& wsl.exe --version
if ($LASTEXITCODE -ne 0) {
    Fail "wsl.exe is not available or WSL is not installed."
}

if ($RunHostPreflight -or $RunHostPreflightOnly -or $ResumeHostPreflight) {
    Write-Step "Running Stage 0 WSL host preflight"
    Invoke-HostPreflight -TargetDistroName $DistroName -TargetLinuxUser $LinuxUser
    if ($RunHostPreflightOnly) {
        Write-Step "RunHostPreflightOnly requested. Exiting after preflight."
        Write-Host "Host preflight marker: $HostPreflightMarkerPath"
        exit 0
    }
}

if ($RunWslUpdate) {
    Write-Step "WSL update explicitly requested"
    & wsl.exe --update
    if ($LASTEXITCODE -ne 0) {
        Write-Warning "wsl --update failed or requires elevation."
    }
} elseif (-not $SkipWslUpdate) {
    Write-Step "Skipping WSL update by default. Use -RunWslUpdate to request it."
}

Write-Step "Setting default WSL version to 2"
& wsl.exe --set-default-version 2 | Out-Null

$existing = Get-WslDistros
if ($ResumeHostPreflight) {
    $ResumeHostPreflightMarker = "YES"
    $ForceRecreateRequiredMarker = "NO"
    if (-not ($existing -contains $DistroName)) {
        $TargetDistroExistsForResumeMarker = "NO"
        $DistroCreateSkippedForResumeMarker = "NO"
        $ResumeExistingDistroAllowedMarker = "NO"
        Write-ResumeProofMarkers
        Fail "ResumeHostPreflight requires an existing target distro. Distro '$DistroName' was not found."
    }

    $TargetDistroExistsForResumeMarker = "YES"
    $DistroCreateSkippedForResumeMarker = "YES"
    $ResumeExistingDistroAllowedMarker = "YES"
    $ResumeExistingDistroFlow = $true
    $DistroImportOrRecreateAttempted = $false
    $DistroImportOrRecreateResult = "SKIPPED_FOR_RESUME"
    Write-Step "ResumeHostPreflight accepted existing target distro: $DistroName"
    Write-ResumeProofMarkers
}

if ($existing -contains $DistroName) {
    if ($ResumeExistingDistroFlow) {
        Write-Step "Skipping existing-distro recreate guard because resume flow targets the existing distro."
    } elseif (-not $ForceRecreate) {
        Fail "Distro '$DistroName' already exists. Use -ForceRecreate to unregister only that test distro."
    }

    if (-not $ResumeExistingDistroFlow) {
        Write-Step "ForceRecreate enabled. Terminating and unregistering existing test distro: $DistroName"
        & wsl.exe --terminate $DistroName 2>$null | Out-Null
        & wsl.exe --unregister $DistroName
        if ($LASTEXITCODE -ne 0) {
            Fail "Failed to unregister existing test distro: $DistroName"
        }
    }
}

if (-not $ResumeExistingDistroFlow) {
    Write-Step "Creating cache/install folders"
    New-Item -ItemType Directory -Force -Path $CacheDir | Out-Null
    New-Item -ItemType Directory -Force -Path $InstallBase | Out-Null

    Write-Step "Downloading SHA256SUMS"
    Download-FileWithRetry -Uri $Sha256Url -OutFile $Sha256File

    function Test-RootfsHash {
        param([string]$FilePath)

        if (-not (Test-Path $FilePath)) {
            return $false
        }

        $rootfsName = Split-Path -Leaf $FilePath
        $shaLine = Get-Content $Sha256File | Where-Object { $_ -match [regex]::Escape($rootfsName) } | Select-Object -First 1
        if (-not $shaLine) {
            Fail "Could not find SHA256 entry for $rootfsName in $Sha256File"
        }

        $script:ExpectedRootfsHash = ($shaLine -split "\s+")[0].ToLower()
        $script:ActualRootfsHash = (Get-FileHash -Algorithm SHA256 $FilePath).Hash.ToLower()
        return ($script:ExpectedRootfsHash -eq $script:ActualRootfsHash)
    }

    Write-Step "Checking cached Ubuntu 22.04 WSL rootfs"
    if (Test-Path $RootfsFile) {
        if (Test-RootfsHash -FilePath $RootfsFile) {
            Write-Host "Using verified cached rootfs: $RootfsFile"
            Write-Host "SHA256 verified: $ActualRootfsHash"
        } else {
            Write-Warning "Cached rootfs SHA256 mismatch. Deleting and redownloading."
            Remove-Item -Force $RootfsFile
        }
    }

    if (-not (Test-Path $RootfsFile)) {
        Write-Step "Downloading Ubuntu 22.04 WSL rootfs"
        Download-FileWithRetry -Uri $RootfsUrl -OutFile $RootfsFile
    }

    Write-Step "Verifying rootfs SHA256"
    if (-not (Test-RootfsHash -FilePath $RootfsFile)) {
        Fail "SHA256 mismatch after fresh download. Expected $ExpectedRootfsHash but got $ActualRootfsHash"
    }
    Write-Host "SHA256 verified: $ActualRootfsHash"

    if (Test-Path $InstallLocation) {
        if ($ForceRecreate) {
            Write-Step "Removing old install directory: $InstallLocation"
            Remove-Item -Recurse -Force $InstallLocation
        } else {
            Fail "Install location already exists: $InstallLocation. Use -ForceRecreate or remove it manually."
        }
    }
    New-Item -ItemType Directory -Force -Path $InstallLocation | Out-Null

    Write-Step "Importing custom-named WSL2 distro: $DistroName"
    $DistroImportOrRecreateAttempted = $true
    Invoke-External wsl.exe --import $DistroName $InstallLocation $RootfsFile --version 2
    $DistroImportOrRecreateResult = "PASS"

    Write-Step "Bootstrapping Linux user, sudo, systemd, and python3"
    $setupLinux = @"
set -euo pipefail
apt-get update
DEBIAN_FRONTEND=noninteractive apt-get install -y sudo ca-certificates curl locales python3
locale-gen en_US.UTF-8 >/dev/null 2>&1 || true

if ! id -u "$LinuxUser" >/dev/null 2>&1; then
  useradd -m -s /bin/bash "$LinuxUser"
fi

usermod -aG sudo "$LinuxUser"

install -d -m 0755 /etc/sudoers.d
cat >/etc/sudoers.d/90-openclaw-bootstrap <<'EOS'
$LinuxUser ALL=(ALL) NOPASSWD:ALL
EOS
chmod 0440 /etc/sudoers.d/90-openclaw-bootstrap
visudo -cf /etc/sudoers.d/90-openclaw-bootstrap

cat >/etc/wsl.conf <<'EOS'
[boot]
systemd=true

[user]
default=$LinuxUser

[interop]
appendWindowsPath=false
EOS

mkdir -p /home/$LinuxUser
chown -R ${LinuxUser}:${LinuxUser} /home/$LinuxUser

if command -v loginctl >/dev/null 2>&1; then
  loginctl enable-linger "$LinuxUser" >/dev/null 2>&1 || echo "loginctl enable-linger failed during initial setup"
else
  echo "loginctl not available during initial setup"
fi
"@

    $encodedSetup = [Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes($setupLinux))
    Invoke-External wsl.exe --distribution $DistroName --user root -- bash -lc "echo $encodedSetup | base64 -d | bash"

    Write-Step "Terminating distro once so systemd/default user settings apply"
    & wsl.exe --terminate $DistroName | Out-Null
    Start-Sleep -Seconds 3
} else {
    Write-Step "Resume flow will reuse the existing distro and skip create/import/bootstrap-only stages."
}

Write-Step "Staging full package into distro"
$wslScriptDir = Convert-WindowsPathToWslPath $ScriptDir
$stageCmd = @"
set -euo pipefail
install -d -m 0755 /home/$LinuxUser/openclaw_install/package
install -d -m 0755 /home/$LinuxUser/openclaw_install/config
install -d -m 0755 /home/$LinuxUser/openclaw_install/logs
cp -a $(ShellQuote "$wslScriptDir/.") /home/$LinuxUser/openclaw_install/package/
find /home/$LinuxUser/openclaw_install/package -name '*.sh' -exec chmod +x {} \;
printf '%s  %s\n' \
  '65dc436abeba0dea7fb3ea15366cb1ce52005133d9037fe50fff3770741bbc20' '/home/$LinuxUser/openclaw_install/package/local_worker_routing_v1.json' \
  '8326d71f3b48b29b605864292655231c5d1eb13d6c904b635e2e86f6c467cb71' '/home/$LinuxUser/openclaw_install/package/Get-LocalWorkerRoutingConfig_v1.ps1' \
  'b9a25c0d177471919319b2dd6e814770185b04292d02aa781c33f82c6d53628c' '/home/$LinuxUser/openclaw_install/package/Invoke-LocalWorkerRouting_v1.ps1' \
  'af864a89fadaf250e5ab397f3ddaa772458ee891e850ebd0f79813b465e4f3f8' '/home/$LinuxUser/openclaw_install/package/Invoke-LocalWorkerRoutingRuntimeBridge_v1.ps1' \
  | sha256sum -c -
install -d -m 0755 /home/$LinuxUser/.config/openclaw/local_worker_routing
install -m 0644 \
  /home/$LinuxUser/openclaw_install/package/local_worker_routing_v1.json \
  /home/$LinuxUser/openclaw_install/package/Get-LocalWorkerRoutingConfig_v1.ps1 \
  /home/$LinuxUser/openclaw_install/package/Invoke-LocalWorkerRouting_v1.ps1 \
  /home/$LinuxUser/openclaw_install/package/Invoke-LocalWorkerRoutingRuntimeBridge_v1.ps1 \
  /home/$LinuxUser/.config/openclaw/local_worker_routing/
printf '%s  %s\n' \
  '65dc436abeba0dea7fb3ea15366cb1ce52005133d9037fe50fff3770741bbc20' '/home/$LinuxUser/.config/openclaw/local_worker_routing/local_worker_routing_v1.json' \
  '8326d71f3b48b29b605864292655231c5d1eb13d6c904b635e2e86f6c467cb71' '/home/$LinuxUser/.config/openclaw/local_worker_routing/Get-LocalWorkerRoutingConfig_v1.ps1' \
  'b9a25c0d177471919319b2dd6e814770185b04292d02aa781c33f82c6d53628c' '/home/$LinuxUser/.config/openclaw/local_worker_routing/Invoke-LocalWorkerRouting_v1.ps1' \
  'af864a89fadaf250e5ab397f3ddaa772458ee891e850ebd0f79813b465e4f3f8' '/home/$LinuxUser/.config/openclaw/local_worker_routing/Invoke-LocalWorkerRoutingRuntimeBridge_v1.ps1' \
  | sha256sum -c -
printf '%s' 'aW1wb3J0IGpzb24KaW1wb3J0IG9zCmltcG9ydCBzeXMKCnBhdGggPSBvcy5lbnZpcm9uWyJST1VUSU5HX0NPTkZJR19QQVRIIl0KCndpdGggb3BlbihwYXRoLCAiciIsIGVuY29kaW5nPSJ1dGYtOC1zaWciKSBhcyBmOgogICAgY29uZmlnID0ganNvbi5sb2FkKGYpCgpjaGVja3MgPSB7CiAgICAicnVudGltZUludGVncmF0aW9uRW5hYmxlZCI6IGNvbmZpZ1sibG9jYWxXb3JrZXJTdXJmYWNlIl1bInJ1bnRpbWVJbnRlZ3JhdGlvbkVuYWJsZWQiXSBpcyBUcnVlLAogICAgInJ1bnRpbWVDb25zdW1wdGlvbkVuYWJsZWQiOiBjb25maWdbImZ1dHVyZUludGVncmF0aW9uIl1bInJ1bnRpbWVDb25zdW1wdGlvbkVuYWJsZWQiXSBpcyBGYWxzZSwKICAgICJyb3V0aW5nU2NyaXB0TXV0YXRpb25BbGxvd2VkSGVyZSI6IGNvbmZpZ1siZnV0dXJlSW50ZWdyYXRpb24iXVsicm91dGluZ1NjcmlwdE11dGF0aW9uQWxsb3dlZEhlcmUiXSBpcyBGYWxzZSwKfQoKZmFpbGVkID0gW25hbWUgZm9yIG5hbWUsIHBhc3NlZCBpbiBjaGVja3MuaXRlbXMoKSBpZiBub3QgcGFzc2VkXQoKaWYgZmFpbGVkOgogICAgcmFpc2UgU3lzdGVtRXhpdCgicm91dGluZyBzY2FmZm9sZCBzdGFnaW5nIHBvbGljeSB2YWxpZGF0aW9uIGZhaWxlZDogIiArICIsIi5qb2luKGZhaWxlZCkp' | base64 -d > /tmp/openclaw_validate_routing_policy_v1.py
ROUTING_CONFIG_PATH="/home/$LinuxUser/.config/openclaw/local_worker_routing/local_worker_routing_v1.json" python3 /tmp/openclaw_validate_routing_policy_v1.py
rm -f /tmp/openclaw_validate_routing_policy_v1.py
echo 'C45P_ROUTING_DEST_STAGE_VALIDATION=PASS'
chown -R ${LinuxUser}:${LinuxUser} /home/$LinuxUser/openclaw_install
chown -R ${LinuxUser}:${LinuxUser} /home/$LinuxUser/.config/openclaw
"@
$stageRetryMax = 4
$stageSucceeded = $false
$stageLastRc = $null
$stageLastOutputText = ""

for ($stageAttempt = 1; $stageAttempt -le $stageRetryMax; $stageAttempt++) {
    Write-Step "Running package staging command in distro (attempt $stageAttempt/$stageRetryMax)"

    $oldStageEap = $ErrorActionPreference
    try {
        $ErrorActionPreference = "Continue"
        $stageOutput = & wsl.exe --distribution $DistroName --user root -- bash -lc $stageCmd 2>&1
        $stageLastRc = $LASTEXITCODE
    } finally {
        $ErrorActionPreference = $oldStageEap
    }

    $stageOutputLines = @($stageOutput | ForEach-Object { [string]$_ })
    $stageLastOutputText = ($stageOutputLines -join "`n")

    foreach ($stageLine in $stageOutputLines) {
        if ($stageLine -match "(?i)(secret|password|authorization|bearer|token=|bot token|discord.*token)") {
            Write-Host "[stage-output-redacted-secretish-line]"
        } else {
            Write-Host $stageLine
        }
    }

    if ($stageLastRc -eq 0) {
        $stageSucceeded = $true
        break
    }

    $rootSessionWarning = ($stageLastOutputText -match "Failed to start the systemd user session for 'root'")
    if ($rootSessionWarning -and $stageAttempt -lt $stageRetryMax) {
        Write-Warning "Transient WSL root user-session startup warning during package staging; terminating target distro and retrying bounded staging attempt."
        & wsl.exe --terminate $DistroName 2>$null | Out-Null
        Start-Sleep -Seconds (2 + $stageAttempt)
        continue
    }

    break
}

if (-not $stageSucceeded) {
    $safeStageOutputTail = if ($stageLastOutputText.Length -gt 1200) {
        $stageLastOutputText.Substring($stageLastOutputText.Length - 1200)
    } else {
        $stageLastOutputText
    }

    Fail "Package staging into distro failed after bounded retry. rc=$stageLastRc; output_tail=$safeStageOutputTail"
}
Try-StageHostPreflightMarkerToWsl -DistroNameValue $DistroName -LinuxUserValue $LinuxUser

if ($DiscordBotTokenFileConfigured) {
    Write-Step "Staging local Discord credential file into distro"
    $DiscordBotTokenFileWsl = "/home/$LinuxUser/.config/openclaw/secrets/discord_bot_token"
    $discordTokenFileData = Resolve-DiscordBotTokenFile -Path $DiscordBotTokenFileResolved
    Stage-DiscordBotTokenIntoWsl `
        -DistroNameValue $DistroName `
        -LinuxUserValue $LinuxUser `
        -TokenValue ([string]$discordTokenFileData.TokenValue) `
        -TargetPath $DiscordBotTokenFileWsl
}

Write-Step "Writing install_config.json handoff"
$configObject = [ordered]@{
    packageVersion = "v1.7"
    distroName = $DistroName
    linuxUser = $LinuxUser
    modelPolicy = [ordered]@{
        baselineDefault = "ollama/qwen3.5:9b-4k"
        includeReasoningModel = [bool]$IncludeReasoningModel
        includeCoderModel = [bool]$IncludeCoderModel
        promoteReasoningModel = [bool]$PromoteReasoningModel
        promoteCoderModel = [bool]$PromoteCoderModel
        includeRiskyModels = [bool]$IncludeRiskyModels
        minimalWireModel = [bool]$MinimalWireModel
    }
    bootstrap = [ordered]@{
        extraArgs = @($BootstrapArgs)
    }
    openclaw = [ordered]@{
        packageSpec = $OpenClawPackageSpec
        expectedIdentity = $OpenClawExpectedIdentity
        expectedBuildId = $OpenClawExpectedBuildId
        expectedPackageVersion = $OpenClawPackageVersion
        identityPolicy = $OpenClawIdentityPolicy
        compatibilityStage = [ordered]@{
            enabled = $true
            validationGate = "static-final-post-hash"
        }
    }
    verification = [ordered]@{
        runBaselineVerifier = [bool]$RunBaselineVerifier
        runDashboardVerifier = [bool]$RunDashboardVerifier
        skipDashboardVerifier = [bool]$SkipDashboardVerifier
        runOptionalModelVerifier = [bool]$RunOptionalModelVerifier
    }
    discord = [ordered]@{
        configure = [bool]$ConfigureDiscord
        ownerId = $DiscordOwnerId
        tokenInputMode = $(if ($DiscordBotTokenFileConfigured) { "file-reference" } else { "prompt-or-env" })
        tokenFilePath = $DiscordBotTokenFileWsl
        tokenValueStored = $false
        refreshToken = [bool]$DiscordRefreshToken
        runVerifier = [bool]$RunDiscordVerifier
        skipPluginInstall = [bool]$SkipDiscordPluginInstall
    }
    supervisedWire = [ordered]@{
        enabled = [bool]$RunSupervisedWire
    }
    dashboardAuth = [ordered]@{
        copyAuthUrl = [bool]$CopyDashboardAuthUrl
        openDashboard = [bool]$OpenDashboard
        resetGatewayToken = [bool]$ResetGatewayToken
    }
    reportPolicy = [ordered]@{
        runWireRatificationReport = [bool]$RunWireRatificationReport
    }
}

$configJson = $configObject | ConvertTo-Json -Depth 10
$encodedConfig = [Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes($configJson))
$configCmd = "echo $encodedConfig | base64 -d > /home/$LinuxUser/openclaw_install/config/install_config.json && chown ${LinuxUser}:${LinuxUser} /home/$LinuxUser/openclaw_install/config/install_config.json && chmod 0644 /home/$LinuxUser/openclaw_install/config/install_config.json"
Invoke-External wsl.exe --distribution $DistroName --user root -- bash -lc $configCmd

Write-Step "Writing conductor marker"
Write-ConductorMarker `
    -DistroNameValue $DistroName `
    -LinuxUserValue $LinuxUser `
    -RunSupervisedWireValue ([bool]$RunSupervisedWire) `
    -ForceRecreateValue ([bool]$ForceRecreate) `
    -DistroImportAttemptedValue ([bool]$DistroImportOrRecreateAttempted) `
    -DistroImportResultValue $DistroImportOrRecreateResult `
    -UserSystemdReadinessAttemptedValue ([bool]$UserSystemdReadinessAttempted) `
    -UserSystemdReadinessResultValue $UserSystemdReadinessResult `
    -UserSystemdReadinessAttemptsValue $UserSystemdReadinessAttempts `
    -UserSystemdSubstrateProbeAttemptedValue ([bool]$UserSystemdSubstrateProbeAttempted) `
    -UserSystemdSubstrateResultValue $UserSystemdSubstrateResult `
    -UserSystemdFailureClassValue $UserSystemdFailureClass `
    -UserSystemdFailureEvidenceValue $UserSystemdFailureEvidence `
    -UserSystemdRecoveryAttemptedValue $UserSystemdRecoveryAttempted `
    -UserSystemdLingerStateValue $UserSystemdLingerState `
    -UserSystemdRuntimeDirStateValue $UserSystemdRuntimeDirState `
    -UserSystemdBusStateValue $UserSystemdBusState `
    -InteropAppendWindowsPathPolicyValue $InteropAppendWindowsPathPolicy `
    -ResumeHostPreflightValue $ResumeHostPreflightMarker `
    -TargetDistroExistsForResumeValue $TargetDistroExistsForResumeMarker `
    -DistroCreateSkippedForResumeValue $DistroCreateSkippedForResumeMarker `
    -ForceRecreateRequiredValue $ForceRecreateRequiredMarker `
    -ResumeExistingDistroAllowedValue $ResumeExistingDistroAllowedMarker

Write-Step "Verifying new distro identity"
Invoke-External wsl.exe --distribution $DistroName --user $LinuxUser -- bash -lc "whoami && cat /etc/os-release | grep PRETTY_NAME && ps -p 1 -o comm= && python3 --version"

Write-Step "Verifying passwordless sudo for bootstrap user"
Invoke-External wsl.exe --distribution $DistroName --user root -- bash -lc "visudo -cf /etc/sudoers.d/90-openclaw-bootstrap && runuser -u $LinuxUser -- sudo -n true && echo NOPASSWD_SUDO_OK"

if ($RunInstall) {
    Write-Step "Checking user-systemd manager readiness before bootstrap"
    $UserSystemdReadinessAttempted = $true
    $UserSystemdSubstrateProbeAttempted = $true
    $maxAttempts = 3
    $ready = $false

    for ($attempt = 1; $attempt -le $maxAttempts; $attempt++) {
        $UserSystemdReadinessAttempts = $attempt
        $probe = Get-UserSystemdProbeResult -DistroNameValue $DistroName -LinuxUserValue $LinuxUser
        $UserSystemdSubstrateResult = [string]$probe['classification']
        $UserSystemdFailureClass = [string]$probe['classification']
        $UserSystemdFailureEvidence = [string]$probe['evidence']
        $UserSystemdLingerState = [string]$probe['loginctl_linger']
        $UserSystemdRuntimeDirState = [string]$probe['runtime_dir_state']
        $UserSystemdBusState = [string]$probe['bus_state']
        if ($UserSystemdSubstrateResult -eq "PASS") {
            $ready = $true
            break
        }

        Write-Warning "user-systemd manager not reachable on attempt $attempt/$maxAttempts; applying bounded recovery."
        $UserSystemdRecoveryAttempted = "YES"
        & wsl.exe --terminate $DistroName 2>$null | Out-Null
        Start-Sleep -Seconds 2
        & wsl.exe --distribution $DistroName --user root -- bash -lc "if command -v loginctl >/dev/null 2>&1; then loginctl enable-linger $LinuxUser || true; else echo 'loginctl unavailable during recovery'; fi"
        & wsl.exe --terminate $DistroName 2>$null | Out-Null
        Start-Sleep -Seconds 2
    }

    if ($ready) {
        $UserSystemdReadinessResult = "PASS"
        $UserSystemdSubstrateResult = "PASS"
        $UserSystemdFailureClass = "NONE"
        $UserSystemdFailureEvidence = "NONE"
    } else {
        $UserSystemdReadinessResult = "FAIL"
    }

    Write-ConductorMarker `
        -DistroNameValue $DistroName `
        -LinuxUserValue $LinuxUser `
        -RunSupervisedWireValue ([bool]$RunSupervisedWire) `
        -ForceRecreateValue ([bool]$ForceRecreate) `
        -DistroImportAttemptedValue ([bool]$DistroImportOrRecreateAttempted) `
        -DistroImportResultValue $DistroImportOrRecreateResult `
        -UserSystemdReadinessAttemptedValue ([bool]$UserSystemdReadinessAttempted) `
        -UserSystemdReadinessResultValue $UserSystemdReadinessResult `
        -UserSystemdReadinessAttemptsValue $UserSystemdReadinessAttempts `
        -UserSystemdSubstrateProbeAttemptedValue ([bool]$UserSystemdSubstrateProbeAttempted) `
        -UserSystemdSubstrateResultValue $UserSystemdSubstrateResult `
        -UserSystemdFailureClassValue $UserSystemdFailureClass `
        -UserSystemdFailureEvidenceValue $UserSystemdFailureEvidence `
        -UserSystemdRecoveryAttemptedValue $UserSystemdRecoveryAttempted `
        -UserSystemdLingerStateValue $UserSystemdLingerState `
        -UserSystemdRuntimeDirStateValue $UserSystemdRuntimeDirState `
        -UserSystemdBusStateValue $UserSystemdBusState `
        -InteropAppendWindowsPathPolicyValue $InteropAppendWindowsPathPolicy `
        -ResumeHostPreflightValue $ResumeHostPreflightMarker `
        -TargetDistroExistsForResumeValue $TargetDistroExistsForResumeMarker `
        -DistroCreateSkippedForResumeValue $DistroCreateSkippedForResumeMarker `
        -ForceRecreateRequiredValue $ForceRecreateRequiredMarker `
        -ResumeExistingDistroAllowedValue $ResumeExistingDistroAllowedMarker

    if (-not $ready) {
        if ($UserSystemdFailureClass -eq "HOST_WSL_USER_SYSTEMD_CGROUP_BUSY") {
            $UserSystemdReadinessResult = "HOST_WSL_USER_SYSTEMD_UNHEALTHY"
            $UserSystemdSubstrateResult = "HOST_WSL_USER_SYSTEMD_UNHEALTHY"
            Write-ConductorMarker `
                -DistroNameValue $DistroName `
                -LinuxUserValue $LinuxUser `
                -RunSupervisedWireValue ([bool]$RunSupervisedWire) `
                -ForceRecreateValue ([bool]$ForceRecreate) `
                -DistroImportAttemptedValue ([bool]$DistroImportOrRecreateAttempted) `
                -DistroImportResultValue $DistroImportOrRecreateResult `
                -UserSystemdReadinessAttemptedValue ([bool]$UserSystemdReadinessAttempted) `
                -UserSystemdReadinessResultValue $UserSystemdReadinessResult `
                -UserSystemdReadinessAttemptsValue $UserSystemdReadinessAttempts `
                -UserSystemdSubstrateProbeAttemptedValue ([bool]$UserSystemdSubstrateProbeAttempted) `
                -UserSystemdSubstrateResultValue $UserSystemdSubstrateResult `
                -UserSystemdFailureClassValue $UserSystemdFailureClass `
                -UserSystemdFailureEvidenceValue $UserSystemdFailureEvidence `
                -UserSystemdRecoveryAttemptedValue $UserSystemdRecoveryAttempted `
                -UserSystemdLingerStateValue $UserSystemdLingerState `
                -UserSystemdRuntimeDirStateValue $UserSystemdRuntimeDirState `
                -UserSystemdBusStateValue $UserSystemdBusState `
                -InteropAppendWindowsPathPolicyValue $InteropAppendWindowsPathPolicy `
                -ResumeHostPreflightValue $ResumeHostPreflightMarker `
                -TargetDistroExistsForResumeValue $TargetDistroExistsForResumeMarker `
                -DistroCreateSkippedForResumeValue $DistroCreateSkippedForResumeMarker `
                -ForceRecreateRequiredValue $ForceRecreateRequiredMarker `
                -ResumeExistingDistroAllowedValue $ResumeExistingDistroAllowedMarker
            Fail "HOST_WSL_USER_SYSTEMD_UNHEALTHY: target distro user manager is failing with cgroup-busy symptoms. Run 'wsl --shutdown', reboot Windows if needed, then resume with -ResumeHostPreflight."
        }
        Fail "USER_SYSTEMD_NOT_READY: target distro user manager is not ready (class=$UserSystemdFailureClass; evidence=$UserSystemdFailureEvidence; linger=$UserSystemdLingerState; runtimeDir=$UserSystemdRuntimeDirState; bus=$UserSystemdBusState). OpenClaw gateway installation requires a healthy systemctl --user substrate."
    }
}

if ($RunInstall) {
    Write-Step "Running config-driven package install inside $DistroName."
    if ($RunSupervisedWire) {
        Invoke-SupervisedWireInstall -DistroNameValue $DistroName -LinuxUserValue $LinuxUser
    } else {
        Invoke-External wsl.exe --distribution $DistroName --user $LinuxUser -- bash -lc "cd /home/$LinuxUser/openclaw_install/package && bash ./run_openclaw_supervised_wire.sh --config /home/$LinuxUser/openclaw_install/config/install_config.json"
    }
} else {
    Write-Step "Package staged but install not run."
    Write-Host ""
    Write-Host "To run it manually:"
    Write-Host "  wsl -d $DistroName"
    Write-Host "  cd ~/openclaw_install/package"
    Write-Host "  bash ./run_openclaw_supervised_wire.sh --config ~/openclaw_install/config/install_config.json"
}

Write-Step "Current WSL distros"
& wsl.exe --list --verbose

if (-not $KeepRootfsArchive) {
    Write-Step "Rootfs archive kept in cache for reuse: $RootfsFile"
}

Write-Host ""
Write-Host "Done."
Write-Host "Test distro name: $DistroName"
Write-Host "Install location: $InstallLocation"
Write-Host "Package path in WSL: /home/$LinuxUser/openclaw_install/package"
Write-Host "Config path in WSL:  /home/$LinuxUser/openclaw_install/config/install_config.json"
Write-Host ""
Write-Host "To enter:"
Write-Host "  wsl -d $DistroName"







