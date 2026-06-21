[CmdletBinding()]
param(
    [switch]$Quiet
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$ReposRoot = "C:\Users\accou\Desktop\Repos"
$SourceFilesDir = Join-Path $ReposRoot "Source Files"

$Jobs = @(
    @{
        SourcePath = "C:\Users\accou\Desktop\Repos\Orchestrator\Orchestrator"
        ZipName    = "Orchestrator_product_repo_latest.zip"
    },
    @{
        SourcePath = "C:\Users\accou\Desktop\Repos\Powershell Scripts\openclaw_wsl_vanilla_installer"
        ZipName    = "openclaw_wsl_vanilla_installer_latest.zip"
    }
)

function Write-Info {
    param([string]$Message)
    if (-not $Quiet) {
        Write-Host $Message
    }
}

function Get-ArchiveBackupPath {
    param(
        [Parameter(Mandatory)][string]$ExistingZipPath
    )

    $dir = Split-Path -Parent $ExistingZipPath
    $base = [System.IO.Path]::GetFileNameWithoutExtension($ExistingZipPath)
    $ext = [System.IO.Path]::GetExtension($ExistingZipPath)

    $created = (Get-Item -LiteralPath $ExistingZipPath).CreationTime
    $stamp = $created.ToString("yyyyMMdd_HHmmss")

    $candidate = Join-Path $dir "$base`_$stamp$ext"
    $i = 1

    while (Test-Path -LiteralPath $candidate) {
        $candidate = Join-Path $dir "$base`_$stamp`_$i$ext"
        $i++
    }

    return $candidate
}

function New-ZipFromDirectoryIncludingRoot {
    param(
        [Parameter(Mandatory)][string]$SourcePath,
        [Parameter(Mandatory)][string]$DestinationZipPath
    )

    Add-Type -AssemblyName System.IO.Compression
    Add-Type -AssemblyName System.IO.Compression.FileSystem

    $sourceItem = Get-Item -LiteralPath $SourcePath
    $sourceRootName = $sourceItem.Name
    $sourceFullName = $sourceItem.FullName.TrimEnd('\')

    $zipStream = [System.IO.File]::Open(
        $DestinationZipPath,
        [System.IO.FileMode]::CreateNew,
        [System.IO.FileAccess]::ReadWrite,
        [System.IO.FileShare]::None
    )

    try {
        $archive = New-Object System.IO.Compression.ZipArchive(
            $zipStream,
            [System.IO.Compression.ZipArchiveMode]::Create,
            $false
        )

        try {
            $files = Get-ChildItem -LiteralPath $sourceFullName -Recurse -File -Force

            foreach ($file in $files) {
                $relative = $file.FullName.Substring($sourceFullName.Length).TrimStart('\')
                $entryName = "$sourceRootName/$($relative -replace '\\','/')"

                [System.IO.Compression.ZipFileExtensions]::CreateEntryFromFile(
                    $archive,
                    $file.FullName,
                    $entryName,
                    [System.IO.Compression.CompressionLevel]::Optimal
                ) | Out-Null
            }
        }
        finally {
            $archive.Dispose()
        }
    }
    catch {
        if (Test-Path -LiteralPath $DestinationZipPath) {
            Remove-Item -LiteralPath $DestinationZipPath -Force
        }
        throw
    }
    finally {
        $zipStream.Dispose()
    }
}

New-Item -ItemType Directory -Force -Path $SourceFilesDir | Out-Null

foreach ($job in $Jobs) {
    $sourcePath = $job.SourcePath
    $zipPath = Join-Path $SourceFilesDir $job.ZipName

    if (-not (Test-Path -LiteralPath $sourcePath -PathType Container)) {
        throw "Source folder not found: $sourcePath"
    }

    if (Test-Path -LiteralPath $zipPath) {
        $backupPath = Get-ArchiveBackupPath -ExistingZipPath $zipPath
        Rename-Item -LiteralPath $zipPath -NewName (Split-Path -Leaf $backupPath)
        Write-Info "Archived existing zip: $backupPath"
    }

    Write-Info "Creating: $zipPath"
    New-ZipFromDirectoryIncludingRoot -SourcePath $sourcePath -DestinationZipPath $zipPath

    $created = Get-Item -LiteralPath $zipPath
    Write-Info "Created: $($created.FullName) [$([math]::Round($created.Length / 1MB, 2)) MB]"
}

Write-Info "Source files updated successfully."
