<#
Zip-OrchestratorProductRepo.ps1

Creates a ZIP snapshot of the Orchestrator product repo.

This script is intentionally separate from Zip-OrchestratorRepo.ps1 / oz.

Artifact meaning:
Zip-OrchestratorRepo.ps1 / oz = WSL/OpenClaw/Ollama/Discord platform package.
Zip-OrchestratorProductRepo.ps1 = Orchestrator product repo.

Source-hygiene policy:
- Preserve product docs, source code, tests, fixture/input data, and data/state.
- Exclude .git, Python caches, bytecode, host metadata, and generated workspace/proof payloads.
- Preserve generated workspace directories as .gitkeep placeholders in the ZIP.
#>

[CmdletBinding()]
param(
    [string]$ProductRepoPath = "C:\Users\accou\Desktop\Repos\Orchestrator\Orchestrator",
    [string]$OutputDir = "C:\Users\accou\Desktop\Repos\Orchestrator",
    [bool]$CreateLatestCopy = $true,
    [bool]$FastMode = $true
)

$ErrorActionPreference = "Stop"
$PSNativeCommandUseErrorActionPreference = $false

function Write-Step {
    param([string]$Message)
    Write-Host "[ZIP-ORCH-PRODUCT] $Message"
}

try {
    Add-Type -AssemblyName System.IO.Compression.FileSystem

    if (-not (Test-Path -LiteralPath $ProductRepoPath)) {
        throw "Product repo path not found: $ProductRepoPath"
    }

    if (-not (Test-Path -LiteralPath $OutputDir)) {
        New-Item -ItemType Directory -Path $OutputDir -Force | Out-Null
    }

    $repoItem = Get-Item -LiteralPath $ProductRepoPath
    $repoName = $repoItem.Name
    $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"

    $zipName = "Orchestrator_product_repo_${timestamp}.zip"
    $zipPath = Join-Path $OutputDir $zipName
    $latestPath = Join-Path $OutputDir "Orchestrator_product_repo_latest.zip"

    if (Test-Path -LiteralPath $zipPath) {
        Remove-Item -LiteralPath $zipPath -Force
    }

    $compressionLevel = if ($FastMode) {
        [System.IO.Compression.CompressionLevel]::Fastest
    } else {
        [System.IO.Compression.CompressionLevel]::Optimal
    }

    $start = Get-Date

    Write-Step "Compressing product repo folder..."
    Write-Step "Source: $ProductRepoPath"
    Write-Step "Output: $zipPath"

    $tempRoot = Join-Path ([System.IO.Path]::GetTempPath()) ("orch_product_zip_stage_" + [guid]::NewGuid().ToString("N"))
    $tempRepo = Join-Path $tempRoot $repoName

    try {
        New-Item -ItemType Directory -Path $tempRoot -Force | Out-Null

        Write-Step "Staging product repo with robocopy..."

        $robocopyArgs = @(
            "`"$ProductRepoPath`"",
            "`"$tempRepo`"",
            "/E",
            "/NFL",
            "/NDL",
            "/NJH",
            "/NJS",
            "/NP",
            "/XD",
            ".git",
            "__pycache__",
            ".pytest_cache",
            ".mypy_cache",
            ".ruff_cache",
            "/XF",
            "*.pyc",
            "*.pyo",
            "*.Zone.Identifier",
            "*Zone.Identifier*",
            "*.identifier"
        )

        $robocopyCommand = "robocopy " + ($robocopyArgs -join " ")
        cmd.exe /c $robocopyCommand | Out-Null

        if ($LASTEXITCODE -ge 8) {
            throw "Robocopy failed with exit code $LASTEXITCODE"
        }

        $sourceHygieneGeneratedRels = @(
            "data\tasks",
            "data\runs",
            "data\artifacts",
            "data\verifier_results",
            "data\reviewer_recommendations",
            "data\case_packets",
            # PHASE83_ACCEPTANCE_GENERATED_DATA_EXCLUSION
            "data\acceptance_inputs\",
            "data\acceptance_records\",
            "test_logs"
        )

        foreach ($rel in $sourceHygieneGeneratedRels) {
            $stageDir = Join-Path $tempRepo $rel

            if (-not (Test-Path -LiteralPath $stageDir)) {
                New-Item -ItemType Directory -Path $stageDir -Force | Out-Null
            }

            Get-ChildItem -LiteralPath $stageDir -Force |
                Where-Object { $_.Name -ne ".gitkeep" } |
                Remove-Item -Recurse -Force

            $gitkeep = Join-Path $stageDir ".gitkeep"
            if (-not (Test-Path -LiteralPath $gitkeep)) {
                New-Item -ItemType File -Path $gitkeep -Force | Out-Null
            }
        }

        [System.IO.Compression.ZipFile]::CreateFromDirectory(
            $tempRoot,
            $zipPath,
            $compressionLevel,
            $false
        )
    }
    finally {
        if (Test-Path -LiteralPath $tempRoot) {
            Remove-Item -LiteralPath $tempRoot -Recurse -Force
        }
    }

    if ($CreateLatestCopy) {
        if (Test-Path -LiteralPath $latestPath) {
            Remove-Item -LiteralPath $latestPath -Force
        }
        Copy-Item -LiteralPath $zipPath -Destination $latestPath -Force
        Write-Step "Latest product copy refreshed: $latestPath"
    }

    $zip = [System.IO.Compression.ZipFile]::OpenRead($zipPath)
    try {
        $entries = @($zip.Entries | ForEach-Object { $_.FullName -replace "\\","/" })

        foreach ($needle in @(
            "Orchestrator/docs/STARTUP_BRIEF.md",
            "Orchestrator/docs/PHASE_64.md",
            "Orchestrator/docs/SOURCE_HYGIENE_CLEANUP_REPORT.md",
            "Orchestrator/docs/ARTIFACT_RETENTION_AND_SOURCE_HYGIENE.md",
            "Orchestrator/orchestrator/intake.py",
            "Orchestrator/tests/test_phase_64_intake_handoff.py"
        )) {
            $matches = @($entries | Where-Object { $_ -eq $needle -or $_.EndsWith("/$needle") })
            if ($matches.Count -ne 1) {
                throw "Expected exactly one ZIP entry ending with $needle, found $($matches.Count)"
            }
        }

        $generatedJsonInZip = @($entries | Where-Object {
            $_ -match "/data/(tasks|runs|artifacts|verifier_results|reviewer_recommendations|case_packets)/" -and
            $_ -like "*.json"
        }).Count

        $testLogPayloadInZip = @($entries | Where-Object {
            $_ -match "/test_logs/" -and
            $_ -notmatch "/test_logs/\.gitkeep$"
        }).Count

        $pycInZip = @($entries | Where-Object { $_ -like "*.pyc" -or $_ -like "*.pyo" }).Count

        $hostMetadataInZip = @($entries | Where-Object {
            $_ -like "*Zone.Identifier*" -or
            $_ -like "*.identifier" -or
            $_ -like "*.DS_Store" -or
            $_ -like "*Thumbs.db"
        }).Count

        $fixtureJsonInZip = @($entries | Where-Object {
            $_ -match "/data/(phase53_fixtures|phase54_fixtures|phase57_intake_inputs|phase58_case_packet_inputs|phase59_case_packet_inputs|phase60_case_packet_seeds|phase61_case_packet_inputs|phase62_case_packet_inputs)/" -and
            $_ -like "*.json"
        }).Count

        $generatedGitkeepInZip = @($entries | Where-Object {
            $_ -match "/(data/(tasks|runs|artifacts|verifier_results|reviewer_recommendations|case_packets)|test_logs)/\.gitkeep$"
        }).Count

        if ($generatedJsonInZip -ne 0) {
            throw "Generated JSON still present in product ZIP: $generatedJsonInZip"
        }
        if ($testLogPayloadInZip -ne 0) {
            throw "test_logs payload still present in product ZIP: $testLogPayloadInZip"
        }
        if ($pycInZip -ne 0) {
            throw "Python bytecode still present in product ZIP: $pycInZip"
        }
        if ($hostMetadataInZip -ne 0) {
            throw "Host metadata still present in product ZIP: $hostMetadataInZip"
        }
        if ($fixtureJsonInZip -lt 278) {
            throw "Fixture/input JSON count too low in product ZIP: $fixtureJsonInZip"
        }
        if ($generatedGitkeepInZip -lt 7) {
            throw "Generated placeholder .gitkeep count too low in product ZIP: $generatedGitkeepInZip"
        }

        $entryCount = $entries.Count
        $jsonCount = @($entries | Where-Object { $_ -like "*.json" }).Count
    }
    finally {
        $zip.Dispose()
    }

    $elapsed = New-TimeSpan -Start $start -End (Get-Date)
    $sizeMB = [math]::Round((Get-Item -LiteralPath $zipPath).Length / 1MB, 2)
    $hash = (Get-FileHash -LiteralPath $zipPath -Algorithm SHA256).Hash.ToLowerInvariant()

    Write-Host ""
    Write-Host "ZIP_ORCHESTRATOR_PRODUCT_REPO=PASS"
    Write-Host "ZIP_SOURCE=$ProductRepoPath"
    Write-Host "ZIP_PATH=$zipPath"
    Write-Host "LATEST_PATH=$latestPath"
    Write-Host "SIZE_MB=$sizeMB"
    Write-Host "SHA256=$hash"
    Write-Host ("ELAPSED_SECONDS={0:N1}" -f $elapsed.TotalSeconds)
    Write-Host "ZIP_ENTRY_COUNT=$entryCount"
    Write-Host "ZIP_JSON_COUNT=$jsonCount"
    Write-Host "ZIP_GENERATED_JSON_COUNT=$generatedJsonInZip"
    Write-Host "ZIP_TEST_LOG_PAYLOAD_COUNT=$testLogPayloadInZip"
    Write-Host "ZIP_PYC_COUNT=$pycInZip"
    Write-Host "ZIP_HOST_METADATA_COUNT=$hostMetadataInZip"
    Write-Host "ZIP_FIXTURE_JSON_COUNT=$fixtureJsonInZip"
    Write-Host "ZIP_GENERATED_GITKEEP_COUNT=$generatedGitkeepInZip"
    Write-Host "VERIFY_SOURCE_HYGIENE_ZIP=PASS"
    Write-Host ""

    try {
        Set-Clipboard -Value $latestPath
        Write-Step "Copied latest product ZIP path to clipboard."
    }
    catch {
        Write-Step "Could not copy path to clipboard, but product ZIP was created."
    }

    exit 0
}
catch {
    Write-Host ""
    Write-Host "ZIP_ORCHESTRATOR_PRODUCT_REPO=FAIL"
    Write-Host "ERROR=$($_.Exception.Message)"
    exit 1
}

