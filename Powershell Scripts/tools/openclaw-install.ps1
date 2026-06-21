[CmdletBinding()]
param(
    [string]$DistroName,
    [string]$OpenClawPackageSpec,
    [string]$OpenClawExpectedIdentity,
    [switch]$ConfigureDiscord,
    [string]$DiscordOwnerId,
    [switch]$RunDiscordVerifier,
    [switch]$MinimalWireModel,
    [switch]$ForceRecreate,
    [string]$LinuxUser = "roger",
    [string]$InstallerRoot
)

$ErrorActionPreference = "Stop"
$prefix = "OpenClaw-Ubuntu-22.04-"
if ([string]::IsNullOrWhiteSpace($InstallerRoot)) {
    $InstallerRoot = Join-Path (Split-Path -Parent $PSScriptRoot) "openclaw_wsl_vanilla_installer"
}

if ([string]::IsNullOrWhiteSpace($DistroName)) {
    $DistroName = Read-Host "OpenClaw distro name or suffix"
}
$DistroName = $DistroName.Trim()
if (-not $DistroName.StartsWith($prefix, [StringComparison]::OrdinalIgnoreCase)) {
    $DistroName = "$prefix$DistroName"
}
if ($DistroName -notmatch '^OpenClaw-Ubuntu-22\.04-[A-Za-z0-9][A-Za-z0-9._-]*$') {
    throw "Invalid distro name. Supply a suffix or a full OpenClaw-Ubuntu-22.04-* name."
}

if ([string]::IsNullOrWhiteSpace($OpenClawPackageSpec)) {
    $enteredPackageSpec = Read-Host "OpenClaw package spec [openclaw@2026.6.6]"
    $OpenClawPackageSpec = if ([string]::IsNullOrWhiteSpace($enteredPackageSpec)) {
        "openclaw@2026.6.6"
    } else {
        $enteredPackageSpec.Trim()
    }
}

if ($RunDiscordVerifier) {
    $ConfigureDiscord = $true
}
if ($ConfigureDiscord -and [string]::IsNullOrWhiteSpace($DiscordOwnerId)) {
    $DiscordOwnerId = Read-Host "Discord owner ID"
}

$initScript = Join-Path $InstallerRoot "init_openclaw_wsl.ps1"
if (-not (Test-Path -LiteralPath $initScript -PathType Leaf)) {
    throw "Missing installer script: $initScript"
}

$installerArgs = @(
    "-DistroName", $DistroName,
    "-LinuxUser", $LinuxUser,
    "-OpenClawPackageSpec", $OpenClawPackageSpec,
    "-RunSupervisedWire",
    "-AllowWslShutdown"
)
if ($PSBoundParameters.ContainsKey("OpenClawExpectedIdentity")) {
    $installerArgs += @("-OpenClawExpectedIdentity", $OpenClawExpectedIdentity)
}
if ($MinimalWireModel) { $installerArgs += "-MinimalWireModel" }
if ($ForceRecreate) { $installerArgs += "-ForceRecreate" }
if ($ConfigureDiscord) {
    $installerArgs += @("-ConfigureDiscord", "-DiscordOwnerId", $DiscordOwnerId)
}
if ($RunDiscordVerifier) { $installerArgs += "-RunDiscordVerifier" }

Write-Host "Distro: $DistroName"
Write-Host "OpenClaw package: $OpenClawPackageSpec"
Write-Host "Installer: $initScript"
if ($ConfigureDiscord) {
    Write-Host "Discord token input remains inside the installer's hidden prompt."
}

& powershell.exe -NoProfile -ExecutionPolicy Bypass -File $initScript @installerArgs
exit $LASTEXITCODE
