[CmdletBinding()]
param(
    [ValidateSet("start", "stop", "status")]
    [string]$Action,
    [string]$DistroName,
    [string]$LinuxUser = "roger",
    [switch]$NoDiscordRequirement,
    [string]$InstallerRoot
)

$ErrorActionPreference = "Stop"
$prefix = "OpenClaw-Ubuntu-22.04-"
if ([string]::IsNullOrWhiteSpace($InstallerRoot)) {
    $InstallerRoot = Join-Path (Split-Path -Parent $PSScriptRoot) "openclaw_wsl_vanilla_installer"
}

if ([string]::IsNullOrWhiteSpace($Action)) {
    $Action = (Read-Host "Action: start, stop, or status").Trim().ToLowerInvariant()
}
if ($Action -notin @("start", "stop", "status")) {
    throw "Action must be start, stop, or status."
}
if ([string]::IsNullOrWhiteSpace($DistroName)) {
    $DistroName = Read-Host "Registered OpenClaw distro name or suffix"
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

$runtimeScript = Join-Path $InstallerRoot "Start-OpenClawRuntime.ps1"
if (-not (Test-Path -LiteralPath $runtimeScript -PathType Leaf)) {
    throw "Missing runtime script: $runtimeScript"
}

$runtimeArgs = @(
    "-DistroName", $resolvedDistroName,
    "-LinuxUser", $LinuxUser
)
if (-not $NoDiscordRequirement) { $runtimeArgs += "-RequireDiscord" }
switch ($Action) {
    "stop" { $runtimeArgs += "-Stop" }
    "status" { $runtimeArgs += "-Status" }
}

Write-Host "OpenClaw runtime $Action for $resolvedDistroName"
& powershell.exe -NoProfile -ExecutionPolicy Bypass -File $runtimeScript @runtimeArgs
exit $LASTEXITCODE
