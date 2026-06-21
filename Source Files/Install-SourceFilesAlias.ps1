Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$TargetScript = "C:\Users\accou\Desktop\Repos\Source Files\Update-SourceFiles.ps1"

if (-not (Test-Path -LiteralPath $TargetScript)) {
    throw "Missing target script: $TargetScript"
}

$profileDir = Split-Path -Parent $PROFILE
New-Item -ItemType Directory -Force -Path $profileDir | Out-Null

$start = "# >>> ORCHESTRATOR SOURCE FILE ZIP ALIAS >>>"
$end   = "# <<< ORCHESTRATOR SOURCE FILE ZIP ALIAS <<<"

$block = @"
$start
function Update-SourceFiles {
    & "$TargetScript" @args
}
Set-Alias -Name srczip -Value Update-SourceFiles
$end
"@

if (Test-Path -LiteralPath $PROFILE) {
    $existing = Get-Content -LiteralPath $PROFILE -Raw

    $pattern = [regex]::Escape($start) + ".*?" + [regex]::Escape($end)

    if ($existing -match $pattern) {
        $updated = [regex]::Replace($existing, $pattern, [System.Text.RegularExpressions.MatchEvaluator]{ param($m) $block }, "Singleline")
        Set-Content -LiteralPath $PROFILE -Value $updated -Encoding UTF8
    }
    else {
        Add-Content -LiteralPath $PROFILE -Value "`n$block"
    }
}
else {
    Set-Content -LiteralPath $PROFILE -Value $block -Encoding UTF8
}

. $PROFILE

Write-Host "Installed:"
Write-Host "  Update-SourceFiles"
Write-Host "  srczip"
Write-Host ""
Write-Host "Profile:"
Write-Host "  $PROFILE"
