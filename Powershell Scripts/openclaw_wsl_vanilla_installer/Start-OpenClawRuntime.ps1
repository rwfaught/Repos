[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$DistroName,
    [string]$LinuxUser = "roger",
    [switch]$RequireDiscord,
    [switch]$KeepAliveLoop,
    [switch]$AnchorWrapper,
    [switch]$Status,
    [switch]$Stop,
    [int]$ReadyAttempts = 30,
    [int]$ReadyDelaySeconds = 2,
    [int]$CheckIntervalSeconds = 20
)

$ErrorActionPreference = "Stop"
$ScriptPath = $MyInvocation.MyCommand.Path
$ScriptDir = Split-Path -Parent $ScriptPath
$RuntimeDir = Join-Path $ScriptDir "runtime"
$SafeDistroName = $DistroName -replace '[^A-Za-z0-9_.-]', '_'
$PidFile = Join-Path $RuntimeDir "openclaw_runtime_${SafeDistroName}.pid"
$StatusFile = Join-Path $RuntimeDir "openclaw_runtime_${SafeDistroName}.status.json"
$LogFile = Join-Path $RuntimeDir "openclaw_runtime_${SafeDistroName}.log"
$AnchorSleepSeconds = "2147483647"

function Get-ProcessById {
    param([int]$ProcessId)
    if ($ProcessId -le 0) { return $null }
    return Get-CimInstance Win32_Process -Filter "ProcessId = $ProcessId" -ErrorAction SilentlyContinue
}

function Get-AllProcesses {
    return @(Get-CimInstance Win32_Process -ErrorAction SilentlyContinue)
}

function Test-SupervisorProcess {
    param($ProcessInfo)
    if ($null -eq $ProcessInfo) { return $false }
    $commandLine = [string]$ProcessInfo.CommandLine
    return (
        ([string]$ProcessInfo.Name).Equals("powershell.exe", [StringComparison]::OrdinalIgnoreCase) -and
        $commandLine.Contains("Start-OpenClawRuntime.ps1") -and
        $commandLine.Contains("-KeepAliveLoop") -and
        $commandLine.Contains($DistroName)
    )
}

function Test-WrapperProcess {
    param($ProcessInfo)
    if ($null -eq $ProcessInfo) { return $false }
    $commandLine = [string]$ProcessInfo.CommandLine
    return (
        ([string]$ProcessInfo.Name).Equals("powershell.exe", [StringComparison]::OrdinalIgnoreCase) -and
        $commandLine.Contains("Start-OpenClawRuntime.ps1") -and
        $commandLine.Contains("-AnchorWrapper") -and
        $commandLine.Contains($DistroName) -and
        $commandLine.Contains($LinuxUser)
    )
}

function Test-AnchorProcess {
    param($ProcessInfo)
    if ($null -eq $ProcessInfo) { return $false }
    $commandLine = [string]$ProcessInfo.CommandLine
    return (
        ([string]$ProcessInfo.Name).Equals("wsl.exe", [StringComparison]::OrdinalIgnoreCase) -and
        $commandLine.Contains("--distribution") -and
        $commandLine.Contains($DistroName) -and
        $commandLine.Contains("--user") -and
        $commandLine.Contains($LinuxUser) -and
        $commandLine.Contains("--exec") -and
        $commandLine.Contains("/bin/sleep") -and
        $commandLine.Contains($AnchorSleepSeconds)
    )
}

function Get-MatchingWrapperProcesses {
    return @(Get-AllProcesses | Where-Object { Test-WrapperProcess -ProcessInfo $_ })
}

function Get-MatchingSupervisorProcesses {
    return @(Get-AllProcesses | Where-Object { Test-SupervisorProcess -ProcessInfo $_ })
}

function Get-MatchingAnchorProcesses {
    return @(Get-AllProcesses | Where-Object { Test-AnchorProcess -ProcessInfo $_ })
}

function Read-SupervisorPid {
    if (-not (Test-Path -LiteralPath $PidFile -PathType Leaf)) { return 0 }
    $raw = (Get-Content -LiteralPath $PidFile -Raw).Trim()
    $value = 0
    if ([int]::TryParse($raw, [ref]$value)) { return $value }
    return 0
}

function Write-RuntimeLog {
    param([string]$Message)
    $line = "{0} {1}" -f ([DateTimeOffset]::Now.ToString("o")), $Message
    Add-Content -LiteralPath $LogFile -Value $line -Encoding UTF8
}

function Write-RuntimeStatus {
    param(
        [string]$State,
        [int]$WrapperPid,
        [int[]]$AnchorPids,
        [bool]$WrapperAlive,
        [bool]$AnchorAlive,
        [bool]$AnchorCommandMatches,
        [bool]$DistroRunning,
        [bool]$GatewayActive,
        [bool]$DiscordReady,
        [long]$CheckNumber,
        [string]$Detail
    )
    $statusObject = [ordered]@{
        state = $State
        supervisorPid = $PID
        wrapperPid = $WrapperPid
        anchorPids = @($AnchorPids)
        wrapperAlive = $WrapperAlive
        anchorAlive = $AnchorAlive
        anchorCommandMatches = $AnchorCommandMatches
        distroName = $DistroName
        linuxUser = $LinuxUser
        requireDiscord = [bool]$RequireDiscord
        distroRunning = $DistroRunning
        gatewayActive = $GatewayActive
        discordReady = $DiscordReady
        checkNumber = $CheckNumber
        detail = $Detail
        updatedAt = [DateTimeOffset]::Now.ToString("o")
    }
    $statusObject | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath $StatusFile -Encoding UTF8
}

function Test-DiscordReady {
    param([string[]]$Lines)
    foreach ($line in $Lines) {
        $lower = ([string]$line).ToLowerInvariant()
        if (
            $lower.Contains("discord") -and
            $lower.Contains("running") -and
            ($lower.Contains("connected") -or $lower.Contains("works"))
        ) {
            return $true
        }
    }
    return $false
}

function Test-DistroRunning {
    $rows = & wsl.exe --list --verbose 2>$null
    if ($LASTEXITCODE -ne 0) { return $false }
    foreach ($row in @($rows)) {
        $normalized = ([string]$row) -replace "`0", ""
        if ($normalized -match [regex]::Escape($DistroName) -and $normalized -match '\bRunning\b') {
            return $true
        }
    }
    return $false
}

function Get-ServiceReadiness {
    param([bool]$DistroRunning)
    if (-not $DistroRunning) {
        return [pscustomobject]@{
            GatewayActive = $false
            DiscordReady = (-not $RequireDiscord)
        }
    }

    $gatewayLines = & wsl.exe --distribution $DistroName --user $LinuxUser -- bash -lc "systemctl --user is-active openclaw-gateway.service 2>/dev/null || true"
    $gatewayActive = (($gatewayLines | Select-Object -First 1) -eq "active")
    $discordReady = -not $RequireDiscord
    if ($RequireDiscord) {
        $probeLines = @(& wsl.exe --distribution $DistroName --user $LinuxUser -- bash -lc "openclaw channels status --probe 2>&1 || true")
        $discordReady = Test-DiscordReady -Lines $probeLines
    }

    return [pscustomobject]@{
        GatewayActive = $gatewayActive
        DiscordReady = $discordReady
    }
}

function Repair-Gateway {
    & wsl.exe --distribution $DistroName --user $LinuxUser -- bash -lc "systemctl --user daemon-reload && systemctl --user enable openclaw-gateway.service >/dev/null 2>&1 || true; systemctl --user restart openclaw-gateway.service" | Out-Null
}

function Start-WrapperProcess {
    $arguments = @(
        "-NoProfile",
        "-ExecutionPolicy", "Bypass",
        "-File", "`"$ScriptPath`"",
        "-DistroName", "`"$DistroName`"",
        "-LinuxUser", "`"$LinuxUser`"",
        "-AnchorWrapper"
    )
    return Start-Process -FilePath "powershell.exe" -ArgumentList $arguments -WindowStyle Hidden -PassThru
}

function Get-LiveRuntimeState {
    param(
        [int]$SupervisorPid,
        [int]$WrapperPid,
        [bool]$ProbeServices
    )

    $supervisorAlive = Test-SupervisorProcess -ProcessInfo (Get-ProcessById -ProcessId $SupervisorPid)
    $wrapperProcess = Get-ProcessById -ProcessId $WrapperPid
    $wrapperAlive = Test-WrapperProcess -ProcessInfo $wrapperProcess
    $anchorProcesses = Get-MatchingAnchorProcesses
    $anchorPids = @($anchorProcesses | ForEach-Object { [int]$_.ProcessId })
    $anchorAlive = $anchorPids.Count -gt 0
    $anchorCommandMatches = $anchorAlive -and (@($anchorProcesses | Where-Object { Test-AnchorProcess -ProcessInfo $_ }).Count -gt 0)
    $distroRunning = Test-DistroRunning
    $gatewayActive = $false
    $discordReady = -not $RequireDiscord

    if ($ProbeServices -and $supervisorAlive -and $wrapperAlive -and $anchorAlive -and $anchorCommandMatches -and $distroRunning) {
        $serviceReadiness = Get-ServiceReadiness -DistroRunning $distroRunning
        $gatewayActive = $serviceReadiness.GatewayActive
        $discordReady = $serviceReadiness.DiscordReady
    }

    return [pscustomobject]@{
        SupervisorAlive = $supervisorAlive
        WrapperAlive = $wrapperAlive
        WrapperPid = $WrapperPid
        AnchorAlive = $anchorAlive
        AnchorCommandMatches = $anchorCommandMatches
        AnchorPids = $anchorPids
        DistroRunning = $distroRunning
        GatewayActive = $gatewayActive
        DiscordReady = $discordReady
    }
}

New-Item -ItemType Directory -Path $RuntimeDir -Force | Out-Null

if ($AnchorWrapper) {
    Write-RuntimeLog "Foreground wrapper started. pid=$PID distro=$DistroName user=$LinuxUser"
    & wsl.exe --distribution $DistroName --user $LinuxUser --exec /bin/sleep 2147483647
    $anchorExitCode = $LASTEXITCODE
    Write-RuntimeLog "Foreground wrapper exited. pid=$PID wslExitCode=$anchorExitCode"
    exit $anchorExitCode
}

if ($Status) {
    $supervisorPid = Read-SupervisorPid
    $savedStatus = $null
    if (Test-Path -LiteralPath $StatusFile -PathType Leaf) {
        try {
            $savedStatus = Get-Content -LiteralPath $StatusFile -Raw | ConvertFrom-Json
        } catch {
            $savedStatus = $null
        }
    }
    $wrapperPid = if ($null -eq $savedStatus) { 0 } else { [int]$savedStatus.wrapperPid }
    $live = Get-LiveRuntimeState -SupervisorPid $supervisorPid -WrapperPid $wrapperPid -ProbeServices $true
    $liveReady = (
        $live.SupervisorAlive -and
        $live.WrapperAlive -and
        $live.AnchorAlive -and
        $live.AnchorCommandMatches -and
        $live.DistroRunning -and
        $live.GatewayActive -and
        $live.DiscordReady
    )

    if (-not $liveReady) {
        Write-Host "OpenClaw runtime keepalive: NOT_READY"
        Write-Host "Supervisor alive: $($live.SupervisorAlive)"
        Write-Host "Wrapper alive: $($live.WrapperAlive)"
        Write-Host "Wrapper PID: $($live.WrapperPid)"
        Write-Host "Anchor alive: $($live.AnchorAlive)"
        Write-Host "Anchor command matches: $($live.AnchorCommandMatches)"
        Write-Host "Anchor PIDs: $($live.AnchorPids -join ',')"
        Write-Host "Distro running: $($live.DistroRunning)"
        Write-Host "Gateway active: $($live.GatewayActive)"
        Write-Host "Discord ready: $($live.DiscordReady)"
        if ($null -ne $savedStatus) {
            Write-Host "Recorded state: $($savedStatus.state)"
            Write-Host "Recorded updatedAt: $($savedStatus.updatedAt)"
            Write-Host "Recorded checkNumber: $($savedStatus.checkNumber)"
        }
        exit 1
    }

    Write-Host "OpenClaw runtime keepalive: READY"
    Write-Host "Supervisor PID: $supervisorPid"
    Write-Host "Wrapper PID: $($live.WrapperPid)"
    Write-Host "Anchor PIDs: $($live.AnchorPids -join ',')"
    Write-Host "Distro running: $($live.DistroRunning)"
    Write-Host "Gateway active: $($live.GatewayActive)"
    Write-Host "Discord ready: $($live.DiscordReady)"
    Write-Host "Recorded updatedAt: $($savedStatus.updatedAt)"
    Write-Host "Recorded checkNumber: $($savedStatus.checkNumber)"
    exit 0
}

if ($Stop) {
    $supervisorPid = Read-SupervisorPid
    $supervisorProcess = Get-ProcessById -ProcessId $supervisorPid
    $matchingSupervisors = Get-MatchingSupervisorProcesses
    $matchingWrappers = Get-MatchingWrapperProcesses
    $matchingAnchors = Get-MatchingAnchorProcesses

    if (Test-SupervisorProcess -ProcessInfo $supervisorProcess) {
        Stop-Process -Id $supervisorPid -Force -ErrorAction SilentlyContinue
    }
    foreach ($matchingSupervisor in $matchingSupervisors) {
        Stop-Process -Id ([int]$matchingSupervisor.ProcessId) -Force -ErrorAction SilentlyContinue
    }
    foreach ($wrapper in $matchingWrappers) {
        Stop-Process -Id ([int]$wrapper.ProcessId) -Force -ErrorAction SilentlyContinue
    }
    foreach ($anchor in $matchingAnchors) {
        Stop-Process -Id ([int]$anchor.ProcessId) -Force -ErrorAction SilentlyContinue
    }

    Remove-Item -LiteralPath $PidFile -Force -ErrorAction SilentlyContinue
    Write-RuntimeStatus -State "STOPPED" -WrapperPid 0 -AnchorPids @() -WrapperAlive $false -AnchorAlive $false -AnchorCommandMatches $false -DistroRunning $false -GatewayActive $false -DiscordReady $false -CheckNumber 0 -Detail "Stopped by operator"
    Write-Host "OpenClaw runtime keepalive stopped for $DistroName."
    exit 0
}

if ($KeepAliveLoop) {
    Set-Content -LiteralPath $PidFile -Value $PID -Encoding ASCII
    Write-RuntimeLog "Supervisor started. pid=$PID distro=$DistroName requireDiscord=$([bool]$RequireDiscord)"
    Write-RuntimeStatus -State "STARTING" -WrapperPid 0 -AnchorPids @() -WrapperAlive $false -AnchorAlive $false -AnchorCommandMatches $false -DistroRunning $false -GatewayActive $false -DiscordReady $false -CheckNumber 0 -Detail "Supervisor initialized"

    $wrapperProcess = $null
    $checkNumber = [long]0
    $lastGatewayRestartAt = [DateTimeOffset]::MinValue
    $gatewayRestartCooldownSeconds = 60

    try {
        while ($true) {
            $checkNumber++
            $wrapperAlive = $null -ne $wrapperProcess -and (Test-WrapperProcess -ProcessInfo (Get-ProcessById -ProcessId $wrapperProcess.Id))
            if (-not $wrapperAlive) {
                $wrapperProcess = Start-WrapperProcess
                Write-RuntimeLog "Foreground wrapper launched. pid=$($wrapperProcess.Id)"
                Write-RuntimeStatus -State "WRAPPER_STARTING" -WrapperPid $wrapperProcess.Id -AnchorPids @() -WrapperAlive $false -AnchorAlive $false -AnchorCommandMatches $false -DistroRunning $false -GatewayActive $false -DiscordReady $false -CheckNumber $checkNumber -Detail "Foreground WSL wrapper recreated"
                Start-Sleep -Seconds $ReadyDelaySeconds
                continue
            }

            $live = Get-LiveRuntimeState -SupervisorPid $PID -WrapperPid $wrapperProcess.Id -ProbeServices $true
            $anchorHeldRunning = $live.SupervisorAlive -and $live.WrapperAlive -and $live.AnchorAlive -and $live.AnchorCommandMatches -and $live.DistroRunning
            $gatewayOrDiscordDegraded = -not ($live.GatewayActive -and $live.DiscordReady)
            $restartCooldownElapsed = (([DateTimeOffset]::Now - $lastGatewayRestartAt).TotalSeconds -ge $gatewayRestartCooldownSeconds)

            if ($anchorHeldRunning -and $gatewayOrDiscordDegraded -and $restartCooldownElapsed) {
                Write-RuntimeLog "Gateway or Discord readiness degraded; restarting gateway."
                Write-RuntimeStatus -State "REPAIRING" -WrapperPid $live.WrapperPid -AnchorPids $live.AnchorPids -WrapperAlive $live.WrapperAlive -AnchorAlive $live.AnchorAlive -AnchorCommandMatches $live.AnchorCommandMatches -DistroRunning $live.DistroRunning -GatewayActive $live.GatewayActive -DiscordReady $live.DiscordReady -CheckNumber $checkNumber -Detail "Restarting gateway after cooldown"
                Repair-Gateway
                $lastGatewayRestartAt = [DateTimeOffset]::Now
                Start-Sleep -Seconds $ReadyDelaySeconds
                continue
            }

            $completeCycleReady = (
                $live.SupervisorAlive -and
                $live.WrapperAlive -and
                $live.AnchorAlive -and
                $live.AnchorCommandMatches -and
                $live.DistroRunning -and
                $live.GatewayActive -and
                $live.DiscordReady
            )
            $state = if ($completeCycleReady) { "READY" } else { "NOT_READY" }
            Write-RuntimeStatus -State $state -WrapperPid $live.WrapperPid -AnchorPids $live.AnchorPids -WrapperAlive $live.WrapperAlive -AnchorAlive $live.AnchorAlive -AnchorCommandMatches $live.AnchorCommandMatches -DistroRunning $live.DistroRunning -GatewayActive $live.GatewayActive -DiscordReady $live.DiscordReady -CheckNumber $checkNumber -Detail "Complete foreground-wrapper validation cycle"
            Start-Sleep -Seconds ([Math]::Max(15, $CheckIntervalSeconds))
        }
    } catch {
        Write-RuntimeLog "Supervisor failure: $($_.Exception.Message)"
        $wrapperPid = if ($null -eq $wrapperProcess) { 0 } else { $wrapperProcess.Id }
        Write-RuntimeStatus -State "FAILED" -WrapperPid $wrapperPid -AnchorPids @() -WrapperAlive $false -AnchorAlive $false -AnchorCommandMatches $false -DistroRunning $false -GatewayActive $false -DiscordReady $false -CheckNumber $checkNumber -Detail $_.Exception.Message
        throw
    } finally {
        if ($null -ne $wrapperProcess -and (Test-WrapperProcess -ProcessInfo (Get-ProcessById -ProcessId $wrapperProcess.Id))) {
            Stop-Process -Id $wrapperProcess.Id -Force -ErrorAction SilentlyContinue
        }
        foreach ($anchor in (Get-MatchingAnchorProcesses)) {
            Stop-Process -Id ([int]$anchor.ProcessId) -Force -ErrorAction SilentlyContinue
        }
        if ((Read-SupervisorPid) -eq $PID) {
            Remove-Item -LiteralPath $PidFile -Force -ErrorAction SilentlyContinue
        }
    }
}

$existingPid = Read-SupervisorPid
$existingProcess = Get-ProcessById -ProcessId $existingPid
if (Test-SupervisorProcess -ProcessInfo $existingProcess) {
    Write-Host "OpenClaw runtime keepalive already running."
    Write-Host "Keepalive process ID: $existingPid"
    exit 0
}

$childArguments = @(
    "-NoProfile",
    "-ExecutionPolicy", "Bypass",
    "-File", "`"$ScriptPath`"",
    "-DistroName", "`"$DistroName`"",
    "-LinuxUser", "`"$LinuxUser`"",
    "-KeepAliveLoop",
    "-ReadyAttempts", "$ReadyAttempts",
    "-ReadyDelaySeconds", "$ReadyDelaySeconds",
    "-CheckIntervalSeconds", "$CheckIntervalSeconds"
)
if ($RequireDiscord) {
    $childArguments += "-RequireDiscord"
}

$supervisorProcess = Start-Process -FilePath "powershell.exe" -ArgumentList $childArguments -WindowStyle Hidden -PassThru
Start-Sleep -Seconds 5
if (-not (Test-SupervisorProcess -ProcessInfo (Get-ProcessById -ProcessId $supervisorProcess.Id))) {
    throw "OpenClaw runtime supervisor exited before verification. See $LogFile"
}

$ready = $false
for ($attempt = 1; $attempt -le $ReadyAttempts; $attempt++) {
    if (-not (Test-SupervisorProcess -ProcessInfo (Get-ProcessById -ProcessId $supervisorProcess.Id))) {
        throw "OpenClaw runtime supervisor exited during readiness verification. See $LogFile"
    }
    if (Test-Path -LiteralPath $StatusFile -PathType Leaf) {
        try {
            $runtimeStatus = Get-Content -LiteralPath $StatusFile -Raw | ConvertFrom-Json
            $live = Get-LiveRuntimeState -SupervisorPid $supervisorProcess.Id -WrapperPid ([int]$runtimeStatus.wrapperPid) -ProbeServices $true
            $ready = (
                $runtimeStatus.state -eq "READY" -and
                $live.SupervisorAlive -and
                $live.WrapperAlive -and
                $live.AnchorAlive -and
                $live.AnchorCommandMatches -and
                $live.DistroRunning -and
                $live.GatewayActive -and
                $live.DiscordReady
            )
            if ($ready) { break }
        } catch {
            $ready = $false
        }
    }
    Start-Sleep -Seconds $ReadyDelaySeconds
}

if (-not $ready) {
    Stop-Process -Id $supervisorProcess.Id -Force -ErrorAction SilentlyContinue
    throw "OpenClaw runtime keepalive did not reach live READY state. See $LogFile"
}

Write-Host "OpenClaw runtime keepalive started and live-verified."
Write-Host "Keepalive process ID: $($supervisorProcess.Id)"
Write-Host "Runtime status file: $StatusFile"
Write-Host "Runtime log file: $LogFile"
