[CmdletBinding()]
param(
    [string]$DistroName = "OpenClaw-Ubuntu-22.04",
    [string]$LinuxUser = "roger",
    [string]$RunDir = "",
    [switch]$Status,
    [switch]$Watch,
    [switch]$Markers,
    [switch]$OpenDashboard,
    [switch]$CopyDashboardUrl,
    [switch]$AutoOpenAtDashboard,
    [string]$NotBeforeUtc = "",
    [int]$ParentProcessId = 0,
    [int]$PollSeconds = 2,
    [int]$TimeoutSeconds = 21600
)

$ErrorActionPreference = "Stop"

function Invoke-Wsl {
    param([string]$Command)
    & wsl.exe --distribution $DistroName --user $LinuxUser -- bash -lc $Command
    return $LASTEXITCODE
}

function Get-LatestRunDir {
    $base = "/home/$LinuxUser/openclaw_install/logs"
    $cmd = "if [ -d '$base' ]; then ls -1dt '$base'/* 2>/dev/null | head -n 1; fi"
    $out = & wsl.exe --distribution $DistroName --user $LinuxUser -- bash -lc $cmd
    if ($LASTEXITCODE -ne 0) { return "" }
    return ($out | Select-Object -First 1).Trim()
}

function Resolve-RunDir {
    if (-not [string]::IsNullOrWhiteSpace($RunDir)) { return $RunDir }
    return Get-LatestRunDir
}

function Read-OperatorState {
    param([string]$RunDirPath)
    $statePath = "$RunDirPath/operator_state_v1_7.json"
    $raw = & wsl.exe --distribution $DistroName --user $LinuxUser -- bash -lc "cat '$statePath' 2>/dev/null || true"
    if ([string]::IsNullOrWhiteSpace(($raw -join "`n"))) { return $null }
    try { return (($raw -join "`n") | ConvertFrom-Json) } catch { return $null }
}

function Test-ParentProcessAlive {
    if ($ParentProcessId -le 0) { return $true }
    return $null -ne (Get-Process -Id $ParentProcessId -ErrorAction SilentlyContinue)
}

function Wait-ForDashboardVerifier {
    $notBefore = [DateTimeOffset]::MinValue
    if (-not [string]::IsNullOrWhiteSpace($NotBeforeUtc)) {
        $notBefore = [DateTimeOffset]::Parse($NotBeforeUtc)
    }

    $deadline = [DateTimeOffset]::UtcNow.AddSeconds($TimeoutSeconds)
    while ([DateTimeOffset]::UtcNow -lt $deadline) {
        if (-not (Test-ParentProcessAlive)) {
            throw "Installer process exited before dashboard auto-open completed."
        }

        $candidateRunDir = Get-LatestRunDir
        if (-not [string]::IsNullOrWhiteSpace($candidateRunDir)) {
            $state = Read-OperatorState -RunDirPath $candidateRunDir
            if ($null -ne $state) {
                $stateTimestamp = [DateTimeOffset]::MinValue
                [DateTimeOffset]::TryParse([string]$state.timestamp, [ref]$stateTimestamp) | Out-Null
                $inputRequired = [string]$state.inputRequired
                if (
                    $stateTimestamp -ge $notBefore -and
                    [string]$state.stage -eq "dashboard_verifier" -and
                    $inputRequired.ToLowerInvariant() -eq "true"
                ) {
                    return $candidateRunDir
                }
            }
        }

        Start-Sleep -Seconds ([Math]::Max(1, $PollSeconds))
    }

    throw "Timed out waiting for dashboard_verifier operator state."
}

function Show-Status {
    param([string]$RunDirPath)
    Write-Host "Run dir: $RunDirPath"
    $stamp = Split-Path -Leaf $RunDirPath
    $canonical = "wsl.exe --distribution $DistroName --user $LinuxUser -- bash -lc ""tail -n 80 -F $RunDirPath/runner.log $RunDirPath/bootstrap.log $RunDirPath/openclaw_npm_install.log 2>/dev/null"""
    $pattern = "`$Current_log_number = `"$stamp`"`nwsl.exe --distribution $DistroName --user $LinuxUser -- bash -lc `"tail -n 80 -F /home/$LinuxUser/openclaw_install/logs/`$Current_log_number/runner.log /home/$LinuxUser/openclaw_install/logs/`$Current_log_number/bootstrap.log /home/$LinuxUser/openclaw_install/logs/`$Current_log_number/openclaw_npm_install.log 2>/dev/null`""
    Write-Host "Canonical watcher:"
    Write-Host $canonical
    Write-Host "PowerShell pattern:"
    Write-Host $pattern
    Write-Host "Stop watcher with Ctrl+C; do not stop installer."
    Write-Host "Do not paste secrets into watcher windows."
    Write-Host "Paste Discord token only into the foreground installer prompt."
    $state = Read-OperatorState -RunDirPath $RunDirPath
    if ($null -ne $state) {
        Write-Host "Stage: $($state.stage)"
        Write-Host "Phase: $($state.phase)"
        Write-Host "Input required: $($state.inputRequired)"
        Write-Host "Input type: $($state.inputType)"
        Write-Host "Instruction: $($state.instruction)"
        Write-Host "Secret expected: $($state.secretExpected)"
        Write-Host "Recommended window: $($state.recommendedWindow)"
        Write-Host "Watch command: $($state.watchCommand)"
        Write-Host "Continue: $($state.continueInstruction)"
        Write-Host "Abort: $($state.abortInstruction)"
        Write-Host "Timestamp: $($state.timestamp)"
    } else {
        Write-Host "Operator state: unavailable"
    }
}

function Show-Markers {
    param([string]$RunDirPath)
    $markerCmd = @"
if [ -d '$RunDirPath/wire_markers' ]; then
  for f in '$RunDirPath'/wire_markers/*.marker; do
    [ -f "\$f" ] || continue
    echo "--- \$f"
    sed -n 's/^key=//p;s/^value=//p;s/^timestamp=//p' "\$f"
  done
fi
"@
    & wsl.exe --distribution $DistroName --user $LinuxUser -- bash -lc $markerCmd
}

function Set-DashboardAuthUrl {
    param([switch]$Open)
    $openclawPath = "/home/$LinuxUser/.openclaw/openclaw.json"
    $jsonRaw = & wsl.exe --distribution $DistroName --user $LinuxUser -- bash -lc "cat '$openclawPath' 2>/dev/null || true"
    if ([string]::IsNullOrWhiteSpace(($jsonRaw -join "`n"))) {
        throw "openclaw.json not found at $openclawPath"
    }
    $obj = ($jsonRaw -join "`n") | ConvertFrom-Json
    $token = "$($obj.gateway.auth.token)"
    if ([string]::IsNullOrWhiteSpace($token)) {
        throw "gateway.auth.token missing in openclaw.json"
    }
    $url = "http://127.0.0.1:18789/#token=$token"
    Set-Clipboard -Value $url
    Write-Host "Dashboard auth URL copied to clipboard (token hidden)."
    if ($Open) {
        Start-Process -FilePath $url | Out-Null
        Write-Host "Dashboard opened in browser."
    }
}

if ($AutoOpenAtDashboard) {
    $resolvedRunDir = Wait-ForDashboardVerifier
    Set-DashboardAuthUrl -Open
    exit 0
}

$resolvedRunDir = Resolve-RunDir
if ([string]::IsNullOrWhiteSpace($resolvedRunDir)) {
    throw "Could not resolve run dir for distro $DistroName"
}

if ($CopyDashboardUrl -or $OpenDashboard) {
    Set-DashboardAuthUrl -Open:$OpenDashboard
}

if ($Status -or (-not $Watch -and -not $Markers)) {
    Show-Status -RunDirPath $resolvedRunDir
}
if ($Markers) {
    Show-Markers -RunDirPath $resolvedRunDir
}
if ($Watch) {
    Show-Status -RunDirPath $resolvedRunDir
    Write-Host "Starting live watch. Stop with Ctrl+C."
    & wsl.exe --distribution $DistroName --user $LinuxUser -- bash -lc "tail -n 80 -F '$resolvedRunDir/runner.log' '$resolvedRunDir/bootstrap.log' '$resolvedRunDir/openclaw_npm_install.log' 2>/dev/null"
}
