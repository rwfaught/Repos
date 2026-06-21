[CmdletBinding()]
param(
    [ValidateSet("start", "stop", "restart", "status", "logs", "health")]
    [string]$Action,
    [string]$DistroName = "OpenClaw-Ubuntu-22.04-ROC-AI",
    [string]$LinuxUser = "roger",
    [string]$ServiceName = "hermes.service",
    [string]$WebUiServiceName = "hermes-webui.service",
    [string]$ApiBase = "http://127.0.0.1:8765",
    [string]$WebUiBase = "http://127.0.0.1:8787"
)

$ErrorActionPreference = "Stop"
$prefix = "OpenClaw-Ubuntu-22.04-"

if ([string]::IsNullOrWhiteSpace($Action)) {
    $Action = (Read-Host "Action: start, stop, restart, status, logs, or health").Trim().ToLowerInvariant()
}
if ($Action -notin @("start", "stop", "restart", "status", "logs", "health")) {
    throw "Action must be start, stop, restart, status, logs, or health."
}
if ([string]::IsNullOrWhiteSpace($DistroName)) {
    $DistroName = Read-Host "Registered Hermes/OpenClaw distro name or suffix"
}
$requestedName = $DistroName.Trim()

$registeredDistros = @(
    & wsl.exe --list --quiet |
        ForEach-Object { ([string]$_).Replace([string][char]0, "").Trim() } |
        Where-Object { $_ }
)
if ($LASTEXITCODE -ne 0) {
    throw "Unable to list registered WSL distros."
}

if ($requestedName.StartsWith($prefix, [StringComparison]::OrdinalIgnoreCase)) {
    $matches = @($registeredDistros | Where-Object { $_ -eq $requestedName })
} else {
    $fullName = "$prefix$requestedName"
    $matches = @($registeredDistros | Where-Object { $_ -eq $fullName })
}
if ($matches.Count -eq 0) {
    throw "No registered distro matches '$requestedName'."
}
if ($matches.Count -gt 1) {
    throw "Distro suffix '$requestedName' is ambiguous: $($matches -join ', ')"
}
$resolvedDistroName = $matches[0]
$safeDistroName = $resolvedDistroName -replace '[^A-Za-z0-9_.-]', '_'
$runtimeDir = Join-Path $PSScriptRoot "runtime"
$keepAlivePidFile = Join-Path $runtimeDir "hermes_keepalive_${safeDistroName}.pid"
$keepAliveMarker = "hermes-keepalive-$safeDistroName"

function Invoke-HermesWsl {
    param([Parameter(Mandatory = $true)][string]$Command)

    & wsl.exe --distribution $resolvedDistroName --user $LinuxUser -- bash -lc $Command
    $script:HermesLastExitCode = $LASTEXITCODE
}

function Get-HermesKeepAliveProcess {
    if (-not (Test-Path -LiteralPath $keepAlivePidFile -PathType Leaf)) {
        return $null
    }

    $rawPid = (Get-Content -LiteralPath $keepAlivePidFile -Raw).Trim()
    $pidValue = 0
    if (-not [int]::TryParse($rawPid, [ref]$pidValue)) {
        Remove-Item -LiteralPath $keepAlivePidFile -Force -ErrorAction SilentlyContinue
        return $null
    }

    $process = Get-CimInstance Win32_Process -Filter "ProcessId = $pidValue" -ErrorAction SilentlyContinue
    if ($null -eq $process) {
        Remove-Item -LiteralPath $keepAlivePidFile -Force -ErrorAction SilentlyContinue
        return $null
    }

    $commandLine = [string]$process.CommandLine
    if (
        (
            ([string]$process.Name).Equals("powershell.exe", [StringComparison]::OrdinalIgnoreCase) -or
            ([string]$process.Name).Equals("pwsh.exe", [StringComparison]::OrdinalIgnoreCase)
        ) -and
        $commandLine.IndexOf("-EncodedCommand", [StringComparison]::OrdinalIgnoreCase) -ge 0
    ) {
        return $process
    }

    Remove-Item -LiteralPath $keepAlivePidFile -Force -ErrorAction SilentlyContinue
    return $null
}

function Start-HermesKeepAlive {
    $existing = Get-HermesKeepAliveProcess
    if ($null -ne $existing) {
        Write-Host "Hermes keepalive already running: PID $($existing.ProcessId)"
        return
    }

    New-Item -ItemType Directory -Path $runtimeDir -Force | Out-Null
    $keepAliveCommand = "while :; do sleep 3600; done # $keepAliveMarker"
    $supervisorCommand = "& wsl.exe -d $resolvedDistroName -u $LinuxUser bash -lc '$keepAliveCommand'"
    $encodedCommand = [Convert]::ToBase64String([Text.Encoding]::Unicode.GetBytes($supervisorCommand))
    $args = @("-NoProfile", "-ExecutionPolicy", "Bypass", "-EncodedCommand", $encodedCommand)
    $process = Start-Process -FilePath "powershell.exe" -ArgumentList $args -WindowStyle Hidden -PassThru
    Start-Sleep -Seconds 1
    $keeper = Get-CimInstance Win32_Process -Filter "ProcessId = $($process.Id)" -ErrorAction SilentlyContinue
    if ($null -eq $keeper) {
        throw "Hermes keepalive process exited immediately."
    }
    Set-Content -LiteralPath $keepAlivePidFile -Value ([string]$process.Id) -Encoding ASCII
    Write-Host "Hermes keepalive started: PID $($keeper.ProcessId)"
}

function Stop-HermesKeepAlive {
    $existing = Get-HermesKeepAliveProcess
    if ($null -eq $existing) {
        Remove-Item -LiteralPath $keepAlivePidFile -Force -ErrorAction SilentlyContinue
        return
    }

    Stop-Process -Id ([int]$existing.ProcessId) -Force -ErrorAction SilentlyContinue
    Remove-Item -LiteralPath $keepAlivePidFile -Force -ErrorAction SilentlyContinue
    Write-Host "Hermes keepalive stopped: PID $($existing.ProcessId)"
}

function Write-HermesKeepAliveStatus {
    $existing = Get-HermesKeepAliveProcess
    if ($null -eq $existing) {
        Remove-Item -LiteralPath $keepAlivePidFile -Force -ErrorAction SilentlyContinue
        Write-Host "Hermes keepalive: inactive"
    } else {
        Write-Host "Hermes keepalive: active (PID $($existing.ProcessId))"
    }
}

$healthUrl = "$($ApiBase.TrimEnd('/'))/health"
$webUiStatusUrl = "$($WebUiBase.TrimEnd('/'))/api/gateway/status"
Write-Host "Hermes $Action for $resolvedDistroName"

function Wait-HermesReady {
    $script:HermesReadyExitCode = 1
    for ($attempt = 1; $attempt -le 10; $attempt++) {
        Invoke-HermesWsl "systemctl --user is-active $ServiceName >/dev/null 2>&1 && curl -fsS $healthUrl >/dev/null 2>&1"
        if ($script:HermesLastExitCode -eq 0) {
            Invoke-HermesWsl "systemctl --user is-active $ServiceName"
            Invoke-HermesWsl "curl -fsS $healthUrl"
            if ($script:HermesLastExitCode -eq 0) { Write-Host "" }
            $script:HermesReadyExitCode = 0
            return
        }
        Start-Sleep -Seconds 1
    }

    Write-Host "Hermes did not become healthy within 10 seconds. Recent service state follows."
    Invoke-HermesWsl "systemctl --user status $ServiceName --no-pager || true"
    Invoke-HermesWsl "journalctl --user -u $ServiceName --no-pager -n 40 | sed -E 's/([Tt][Oo][Kk][Ee][Nn]|[Ss][Ee][Cc][Rr][Ee][Tt]|[Pp][Aa][Ss][Ss][Ww][Oo][Rr][Dd]|[Kk][Ee][Yy])=[^[:space:]]+/\1=<REDACTED>/g'"
    $script:HermesReadyExitCode = 1
}

function Wait-HermesWebUiReady {
    $script:HermesWebUiReadyExitCode = 1
    for ($attempt = 1; $attempt -le 10; $attempt++) {
        Invoke-HermesWsl "systemctl --user is-active $WebUiServiceName >/dev/null 2>&1 && curl -fsS $webUiStatusUrl >/dev/null 2>&1"
        if ($script:HermesLastExitCode -eq 0) {
            Invoke-HermesWsl "systemctl --user is-active $WebUiServiceName"
            Invoke-HermesWsl "curl -fsS $webUiStatusUrl"
            if ($script:HermesLastExitCode -eq 0) { Write-Host "" }
            $script:HermesWebUiReadyExitCode = 0
            return
        }
        Start-Sleep -Seconds 1
    }

    Write-Host "Hermes WebUI did not become healthy within 10 seconds. Recent service state follows."
    Invoke-HermesWsl "systemctl --user status $WebUiServiceName --no-pager || true"
    Invoke-HermesWsl "journalctl --user -u $WebUiServiceName --no-pager -n 40 | sed -E 's/([Tt][Oo][Kk][Ee][Nn]|[Ss][Ee][Cc][Rr][Ee][Tt]|[Pp][Aa][Ss][Ss][Ww][Oo][Rr][Dd]|[Kk][Ee][Yy])=[^[:space:]]+/\1=<REDACTED>/g'"
    $script:HermesWebUiReadyExitCode = 1
}

switch ($Action) {
    "start" {
        Invoke-HermesWsl "systemctl --user start $ServiceName"
        if ($script:HermesLastExitCode -ne 0) { exit $script:HermesLastExitCode }
        Wait-HermesReady
        if ($script:HermesReadyExitCode -ne 0) { exit $script:HermesReadyExitCode }
        Invoke-HermesWsl "systemctl --user start $WebUiServiceName"
        if ($script:HermesLastExitCode -ne 0) { exit $script:HermesLastExitCode }
        Wait-HermesWebUiReady
        if ($script:HermesWebUiReadyExitCode -eq 0) { Start-HermesKeepAlive }
        exit $script:HermesWebUiReadyExitCode
    }
    "stop" {
        Invoke-HermesWsl "systemctl --user stop $WebUiServiceName"
        if ($script:HermesLastExitCode -ne 0) { exit $script:HermesLastExitCode }
        Invoke-HermesWsl "systemctl --user stop $ServiceName"
        if ($script:HermesLastExitCode -ne 0) { exit $script:HermesLastExitCode }
        Stop-HermesKeepAlive
        Invoke-HermesWsl "systemctl --user is-active $WebUiServiceName || true"
        Invoke-HermesWsl "systemctl --user is-active $ServiceName || true"
        exit 0
    }
    "restart" {
        Stop-HermesKeepAlive
        Invoke-HermesWsl "systemctl --user restart $ServiceName $WebUiServiceName"
        if ($script:HermesLastExitCode -ne 0) { exit $script:HermesLastExitCode }
        Wait-HermesReady
        if ($script:HermesReadyExitCode -ne 0) { exit $script:HermesReadyExitCode }
        Wait-HermesWebUiReady
        if ($script:HermesWebUiReadyExitCode -eq 0) { Start-HermesKeepAlive }
        exit $script:HermesWebUiReadyExitCode
    }
    "status" {
        Write-HermesKeepAliveStatus
        Invoke-HermesWsl "systemctl --user status $WebUiServiceName --no-pager"
        if ($script:HermesLastExitCode -ne 0) { exit $script:HermesLastExitCode }
        Invoke-HermesWsl "systemctl --user status $ServiceName --no-pager"
        exit $script:HermesLastExitCode
    }
    "logs" {
        Invoke-HermesWsl "journalctl --user -u $WebUiServiceName --no-pager -n 80 | sed -E 's/([Tt][Oo][Kk][Ee][Nn]|[Ss][Ee][Cc][Rr][Ee][Tt]|[Pp][Aa][Ss][Ss][Ww][Oo][Rr][Dd]|[Kk][Ee][Yy])=[^[:space:]]+/\1=<REDACTED>/g'"
        if ($script:HermesLastExitCode -ne 0) { exit $script:HermesLastExitCode }
        Invoke-HermesWsl "journalctl --user -u $ServiceName --no-pager -n 80 | sed -E 's/([Tt][Oo][Kk][Ee][Nn]|[Ss][Ee][Cc][Rr][Ee][Tt]|[Pp][Aa][Ss][Ss][Ww][Oo][Rr][Dd]|[Kk][Ee][Yy])=[^[:space:]]+/\1=<REDACTED>/g'"
        exit $script:HermesLastExitCode
    }
    "health" {
        Invoke-HermesWsl "curl -fsS $healthUrl"
        if ($script:HermesLastExitCode -ne 0) { exit $script:HermesLastExitCode }
        if ($script:HermesLastExitCode -eq 0) { Write-Host "" }
        Invoke-HermesWsl "curl -fsS $webUiStatusUrl"
        if ($script:HermesLastExitCode -eq 0) { Write-Host "" }
        exit $script:HermesLastExitCode
    }
}
