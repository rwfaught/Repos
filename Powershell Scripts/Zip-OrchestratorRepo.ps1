<#
Zip-OrchestratorRepo.ps1

Context-aware ZIP snapshot tool for Roger's Orchestrator work.

Default behavior:
- If invoked from the product repo, exports the product repo:
    C:\Users\accou\Desktop\Repos\Orchestrator\Orchestrator
  to:
    C:\Users\accou\Desktop\Repos\Orchestrator\Orchestrator_product_repo_latest.zip

- If invoked from the platform/OpenClaw package, exports the platform package:
    C:\Users\accou\Desktop\Repos\Powershell Scripts\orchestrator_wsl_openclaw_v1_7_package
  to:
    C:\Users\accou\Desktop\Repos\Powershell Scripts\orchestrator_wsl_openclaw_v1_7_package_latest.zip

Product export preserves product ZIP hygiene:
- excludes generated data/acceptance_inputs/*.json
- excludes generated data/acceptance_records/*.json
- excludes cache/build/transient folders

Run:
  oz
  oz -PreviewOnly
  oz -Mode Product
  oz -Mode Platform
#>

[CmdletBinding()]
param(
    [ValidateSet("Auto", "Product", "Platform", "Custom")]
    [string]$Mode = "Auto",

    [string]$RepoPath = "",
    [string]$OutputDir = "",
    [string]$LatestName = "",

    [bool]$CreateLatestCopy = $true,
    [bool]$FastMode = $true,

    [switch]$PreviewOnly
)

$ErrorActionPreference = "Stop"

$KnownProductRepo = "C:\Users\accou\Desktop\Repos\Orchestrator\Orchestrator"
$KnownProductOutputDir = "C:\Users\accou\Desktop\Repos\Orchestrator"
$KnownProductLatestName = "Orchestrator_product_repo_latest.zip"
$KnownProductTimestampPrefix = "Orchestrator_product_repo"

$KnownPlatformRepo = "C:\Users\accou\Desktop\Repos\Powershell Scripts\orchestrator_wsl_openclaw_v1_7_package"
$KnownPlatformOutputDir = "C:\Users\accou\Desktop\Repos\Powershell Scripts"

function Write-Step {
    param([string]$Message)
    Write-Host "[ZIP-ORCH] $Message"
}

function Normalize-ExistingPath {
    param([string]$Path)

    $Resolved = Resolve-Path -LiteralPath $Path -ErrorAction Stop
    return $Resolved.ProviderPath.TrimEnd("\", "/")
}

function Test-SameOrChildPath {
    param(
        [string]$Path,
        [string]$Root
    )

    $NormalizedPath = Normalize-ExistingPath -Path $Path
    $NormalizedRoot = Normalize-ExistingPath -Path $Root

    if ($NormalizedPath.Equals($NormalizedRoot, [System.StringComparison]::OrdinalIgnoreCase)) {
        return $true
    }

    $Prefix = $NormalizedRoot + "\"
    return $NormalizedPath.StartsWith($Prefix, [System.StringComparison]::OrdinalIgnoreCase)
}

function Should-IncludeProductFile {
    param([string]$RelativePath)

    $Rel = $RelativePath.Replace("\", "/")

    if ($Rel -like ".git/*") { return $false }
    if ($Rel -like "__pycache__/*") { return $false }
    if ($Rel -like "*/__pycache__/*") { return $false }
    if ($Rel -like ".pytest_cache/*") { return $false }
    if ($Rel -like ".mypy_cache/*") { return $false }
    if ($Rel -like ".ruff_cache/*") { return $false }
    if ($Rel -like ".venv/*") { return $false }
    if ($Rel -like "venv/*") { return $false }
    if ($Rel -like "node_modules/*") { return $false }
    if ($Rel -like "*.pyc") { return $false }
    if ($Rel -like "*.pyo") { return $false }

    if ($Rel -like "data/acceptance_inputs/*.json") { return $false }
    if ($Rel -like "data/acceptance_records/*.json") { return $false }

    return $true
}

function New-ProductZip {
    param(
        [string]$SourceRepo,
        [string]$DestinationZip,
        [System.IO.Compression.CompressionLevel]$CompressionLevel
    )

    $RepoItem = Get-Item -LiteralPath $SourceRepo
    $RepoName = $RepoItem.Name

    $FileStream = [System.IO.File]::Open($DestinationZip, [System.IO.FileMode]::Create, [System.IO.FileAccess]::ReadWrite, [System.IO.FileShare]::None)

    try {
        $Archive = [System.IO.Compression.ZipArchive]::new($FileStream, [System.IO.Compression.ZipArchiveMode]::Create)

        try {
            $Files = Get-ChildItem -Path $SourceRepo -Recurse -File | Sort-Object FullName

            foreach ($File in $Files) {
                $Rel = $File.FullName.Substring($SourceRepo.Length).TrimStart("\", "/")
                $Rel = $Rel.Replace("\", "/")

                if (-not (Should-IncludeProductFile -RelativePath $Rel)) {
                    continue
                }

                $EntryName = "$RepoName/$Rel"
                $Entry = $Archive.CreateEntry($EntryName, $CompressionLevel)

                $EntryStream = $Entry.Open()
                $InputStream = [System.IO.File]::OpenRead($File.FullName)

                try {
                    $InputStream.CopyTo($EntryStream)
                }
                finally {
                    $InputStream.Dispose()
                    $EntryStream.Dispose()
                }
            }
        }
        finally {
            $Archive.Dispose()
        }
    }
    finally {
        $FileStream.Dispose()
    }
}

function New-StagedDirectoryZip {
    param(
        [string]$SourceRepo,
        [string]$DestinationZip,
        [System.IO.Compression.CompressionLevel]$CompressionLevel
    )

    $RepoItem = Get-Item -LiteralPath $SourceRepo
    $RepoName = $RepoItem.Name

    $TempRoot = Join-Path ([System.IO.Path]::GetTempPath()) ("orch_zip_stage_" + [guid]::NewGuid().ToString("N"))
    $TempRepo = Join-Path $TempRoot $RepoName

    New-Item -ItemType Directory -Path $TempRoot -Force | Out-Null

    try {
        Write-Step "Staging repo with robocopy..."

        $RobocopyArgs = @(
            "`"$SourceRepo`"",
            "`"$TempRepo`"",
            "/MIR",
            "/R:1",
            "/W:1",
            "/NFL",
            "/NDL",
            "/NJH",
            "/NJS",
            "/NP"
        )

        $RobocopyCommand = "robocopy " + ($RobocopyArgs -join " ")
        cmd.exe /c $RobocopyCommand | Out-Null

        if ($LASTEXITCODE -ge 8) {
            throw "Robocopy failed with exit code $LASTEXITCODE"
        }

        [System.IO.Compression.ZipFile]::CreateFromDirectory(
            $TempRoot,
            $DestinationZip,
            $CompressionLevel,
            $false
        )
    }
    finally {
        if (Test-Path -LiteralPath $TempRoot) {
            Remove-Item -LiteralPath $TempRoot -Recurse -Force -ErrorAction SilentlyContinue
        }
    }
}

try {
    $InvocationCwd = (Get-Location).Path
    $ResolvedMode = $Mode

    if ($ResolvedMode -eq "Auto") {
        if (Test-SameOrChildPath -Path $InvocationCwd -Root $KnownProductRepo) {
            $ResolvedMode = "Product"
        }
        elseif (Test-SameOrChildPath -Path $InvocationCwd -Root $KnownPlatformRepo) {
            $ResolvedMode = "Platform"
        }
        elseif (-not [string]::IsNullOrWhiteSpace($RepoPath)) {
            $ResolvedMode = "Custom"
        }
        else {
            throw "Auto mode could not resolve routing from current directory: $InvocationCwd. Run from a known repo or pass -Mode Product, -Mode Platform, or -RepoPath."
        }
    }

    if ($ResolvedMode -eq "Product") {
        if ([string]::IsNullOrWhiteSpace($RepoPath)) {
            $RepoPath = $KnownProductRepo
        }

        if ([string]::IsNullOrWhiteSpace($OutputDir)) {
            $OutputDir = $KnownProductOutputDir
        }

        if ([string]::IsNullOrWhiteSpace($LatestName)) {
            $LatestName = $KnownProductLatestName
        }
    }

    if ($ResolvedMode -eq "Platform") {
        if ([string]::IsNullOrWhiteSpace($RepoPath)) {
            $RepoPath = $KnownPlatformRepo
        }

        if ([string]::IsNullOrWhiteSpace($OutputDir)) {
            $OutputDir = $KnownPlatformOutputDir
        }
    }

    if ($ResolvedMode -eq "Custom") {
        if ([string]::IsNullOrWhiteSpace($RepoPath)) {
            throw "Custom mode requires -RepoPath."
        }

        if ([string]::IsNullOrWhiteSpace($OutputDir)) {
            $OutputDir = Split-Path -Parent $RepoPath
        }
    }

    if (-not (Test-Path -LiteralPath $RepoPath -PathType Container)) {
        throw "RepoPath not found: $RepoPath"
    }

    $RepoItem = Get-Item -LiteralPath $RepoPath
    $RepoName = $RepoItem.Name
    $Timestamp = Get-Date -Format "yyyyMMdd_HHmmss"

    if ($ResolvedMode -eq "Product") {
        $ZipName = "${KnownProductTimestampPrefix}_${Timestamp}.zip"
    }
    else {
        $ZipName = "${RepoName}_${Timestamp}.zip"
    }

    if ([string]::IsNullOrWhiteSpace($LatestName)) {
        $LatestName = "${RepoName}_latest.zip"
    }

    $ZipPath = Join-Path $OutputDir $ZipName
    $LatestPath = Join-Path $OutputDir $LatestName
    $ProductExcludesApplied = ($ResolvedMode -eq "Product")

    Write-Host "ZIP_ORCHESTRATOR_REPO_PREVIEW=$($PreviewOnly.IsPresent)"
    Write-Host "INVOCATION_CWD=$InvocationCwd"
    Write-Host "REQUESTED_MODE=$Mode"
    Write-Host "RESOLVED_MODE=$ResolvedMode"
    Write-Host "REPO_PATH=$RepoPath"
    Write-Host "OUTPUT_DIR=$OutputDir"
    Write-Host "ZIP_PATH=$ZipPath"
    Write-Host "LATEST_PATH=$LatestPath"
    Write-Host "PRODUCT_EXCLUDES_APPLIED=$ProductExcludesApplied"
    Write-Host "CREATE_LATEST_COPY=$CreateLatestCopy"

    if ($PreviewOnly) {
        Write-Host "ZIP_ORCHESTRATOR_REPO=PREVIEW_ONLY"
        exit 0
    }

    if (-not (Test-Path -LiteralPath $OutputDir -PathType Container)) {
        New-Item -ItemType Directory -Path $OutputDir -Force | Out-Null
    }

    Add-Type -AssemblyName System.IO.Compression
    Add-Type -AssemblyName System.IO.Compression.FileSystem

    if (Test-Path -LiteralPath $ZipPath) {
        Remove-Item -LiteralPath $ZipPath -Force
    }

    $CompressionLevel = if ($FastMode) {
        [System.IO.Compression.CompressionLevel]::Fastest
    }
    else {
        [System.IO.Compression.CompressionLevel]::Optimal
    }

    $Start = Get-Date
    Write-Step "Compressing repo folder..."
    Write-Step "Mode: $ResolvedMode"
    Write-Step "Source: $RepoPath"
    Write-Step "Output: $ZipPath"

    if ($ResolvedMode -eq "Product") {
        New-ProductZip -SourceRepo $RepoPath -DestinationZip $ZipPath -CompressionLevel $CompressionLevel
    }
    else {
        New-StagedDirectoryZip -SourceRepo $RepoPath -DestinationZip $ZipPath -CompressionLevel $CompressionLevel
    }

    if ($CreateLatestCopy) {
        if (Test-Path -LiteralPath $LatestPath) {
            Remove-Item -LiteralPath $LatestPath -Force
        }

        Copy-Item -LiteralPath $ZipPath -Destination $LatestPath -Force
        Write-Step "Latest copy refreshed: $LatestPath"
    }

    $Elapsed = New-TimeSpan -Start $Start -End (Get-Date)
    $SizeMB = [math]::Round((Get-Item -LiteralPath $ZipPath).Length / 1MB, 2)

    Write-Host ""
    Write-Host "ZIP_ORCHESTRATOR_REPO=PASS"
    Write-Host "RESOLVED_MODE=$ResolvedMode"
    Write-Host "ZIP_PATH=$ZipPath"
    Write-Host "LATEST_PATH=$LatestPath"
    Write-Host "SIZE_MB=$SizeMB"
    Write-Host ("ELAPSED_SECONDS={0:N1}" -f $Elapsed.TotalSeconds)
    Write-Host ""

    try {
        Set-Clipboard -Value $LatestPath
        Write-Step "Copied latest ZIP path to clipboard."
    }
    catch {
        Write-Step "Could not copy path to clipboard, but ZIP was created."
    }
}
catch {
    Write-Host ""
    Write-Host "ZIP_ORCHESTRATOR_REPO=FAIL"
    Write-Host "ERROR=$($_.Exception.Message)"
    exit 1
}