# Full Harvest v7.1 Restoration Script (PowerShell)
# Verifies and extracts both source-only and everything packages

param(
    [Parameter(Mandatory=$false)]
    [string]$TargetDir = "WatchLockAI_Sentinel_Restored",
    
    [Parameter(Mandatory=$false)]
    [string]$DistDir = "./dist",
    
    [Parameter(Mandatory=$false)]
    [switch]$SourceOnly = $false,
    
    [Parameter(Mandatory=$false)]
    [switch]$Everything = $false,
    
    [Parameter(Mandatory=$false)]
    [switch]$Verify = $true
)

Write-Host "🔧 Full Harvest v7.1 Restoration Script" -ForegroundColor Cyan
Write-Host "=============================================" -ForegroundColor Cyan

# Function to calculate SHA256
function Get-FileSHA256 {
    param([string]$FilePath)
    $hash = Get-FileHash -Path $FilePath -Algorithm SHA256
    return $hash.Hash.ToLower()
}

# Function to verify SHA256SUMS
function Test-SHA256SUMS {
    param([string]$DistPath)
    
    $sha256sumsFile = Join-Path $DistPath "SHA256SUMS"
    if (-not (Test-Path $sha256sumsFile)) {
        Write-Host "❌ SHA256SUMS file not found: $sha256sumsFile" -ForegroundColor Red
        return $false
    }
    
    Write-Host "🔍 Verifying SHA256SUMS..." -ForegroundColor Yellow
    $checksums = Get-Content $sha256sumsFile
    $allValid = $true
    
    foreach ($line in $checksums) {
        if ($line -match '^([a-f0-9]{64})\s+(.+)$') {
            $expectedHash = $Matches[1]
            $fileName = $Matches[2]
            $filePath = Join-Path $DistPath $fileName
            
            if (Test-Path $filePath) {
                $actualHash = Get-FileSHA256 $filePath
                if ($actualHash -eq $expectedHash) {
                    Write-Host "  ✅ $fileName" -ForegroundColor Green
                } else {
                    Write-Host "  ❌ $fileName (hash mismatch)" -ForegroundColor Red
                    $allValid = $false
                }
            } else {
                Write-Host "  ❌ $fileName (file not found)" -ForegroundColor Red
                $allValid = $false
            }
        }
    }
    
    return $allValid
}

# Function to reassemble parts (if any exist)
function Restore-SplitArchive {
    param([string]$BaseName, [string]$DistPath)
    
    $partsIndexFile = Join-Path $DistPath "$BaseName.parts.json"
    if (-not (Test-Path $partsIndexFile)) {
        # No parts to reassemble
        return $true
    }
    
    Write-Host "🔧 Reassembling split archive: $BaseName" -ForegroundColor Yellow
    
    $partsInfo = Get-Content $partsIndexFile | ConvertFrom-Json
    $outputFile = Join-Path $DistPath $partsInfo.original_file
    
    # Remove existing file if it exists
    if (Test-Path $outputFile) {
        Remove-Item $outputFile -Force
    }
    
    $totalSize = 0
    foreach ($part in $partsInfo.parts) {
        $partPath = Join-Path $DistPath $part.filename
        if (-not (Test-Path $partPath)) {
            Write-Host "  ❌ Part not found: $($part.filename)" -ForegroundColor Red
            return $false
        }
        
        # Verify part hash
        $partHash = Get-FileSHA256 $partPath
        if ($partHash -ne $part.sha256) {
            Write-Host "  ❌ Part hash mismatch: $($part.filename)" -ForegroundColor Red
            return $false
        }
        
        # Append to output file
        $content = [System.IO.File]::ReadAllBytes($partPath)
        [System.IO.File]::WriteAllBytes($outputFile, $content, $totalSize)
        $totalSize += $content.Length
        
        Write-Host "  ✅ Part $($part.part_number): $($part.filename)" -ForegroundColor Green
    }
    
    Write-Host "  ✅ Reassembled: $BaseName ($totalSize bytes)" -ForegroundColor Green
    return $true
}

# Function to extract archive and count contents
function Expand-HarvestArchive {
    param([string]$ArchivePath, [string]$DestinationPath, [string]$PackageType)
    
    Write-Host "📦 Extracting $PackageType package..." -ForegroundColor Yellow
    Write-Host "  Source: $ArchivePath" -ForegroundColor Gray
    Write-Host "  Target: $DestinationPath" -ForegroundColor Gray
    
    if (-not (Test-Path $ArchivePath)) {
        Write-Host "  ❌ Archive not found: $ArchivePath" -ForegroundColor Red
        return @{Success=$false; FileCount=0; TotalBytes=0}
    }
    
    # Create destination directory
    if (Test-Path $DestinationPath) {
        Remove-Item $DestinationPath -Recurse -Force
    }
    New-Item -ItemType Directory -Path $DestinationPath -Force | Out-Null
    
    # Extract archive
    try {
        Expand-Archive -Path $ArchivePath -DestinationPath $DestinationPath -Force
        
        # Count extracted files and calculate total size
        $extractedFiles = Get-ChildItem -Path $DestinationPath -Recurse -File
        $fileCount = $extractedFiles.Count
        $totalBytes = ($extractedFiles | Measure-Object -Property Length -Sum).Sum
        
        Write-Host "  ✅ Extracted $fileCount files ($totalBytes bytes)" -ForegroundColor Green
        
        return @{Success=$true; FileCount=$fileCount; TotalBytes=$totalBytes}
    }
    catch {
        Write-Host "  ❌ Extraction failed: $($_.Exception.Message)" -ForegroundColor Red
        return @{Success=$false; FileCount=0; TotalBytes=0}
    }
}

# Main restoration logic
try {
    # Resolve paths
    $DistPath = Resolve-Path $DistDir -ErrorAction Stop
    Write-Host "📁 Distribution directory: $DistPath" -ForegroundColor Gray
    
    # Verify SHA256SUMS if requested
    if ($Verify) {
        if (-not (Test-SHA256SUMS -DistPath $DistPath)) {
            Write-Host "❌ SHA256 verification failed!" -ForegroundColor Red
            exit 1
        }
        Write-Host "✅ SHA256 verification passed!" -ForegroundColor Green
    }
    
    # Determine which packages to restore
    $restoreSource = $SourceOnly -or (-not $Everything -and -not $SourceOnly)
    $restoreEverything = $Everything -or (-not $Everything -and -not $SourceOnly)
    
    $totalFileCount = 0
    $totalBytes = 0
    
    # Restore source-only package
    if ($restoreSource) {
        $sourceArchive = Join-Path $DistPath "source_only_v7_1.zip"
        $sourceTarget = "${TargetDir}_source_only"
        
        # Check for split archive parts
        Restore-SplitArchive -BaseName "source_only_v7_1.zip" -DistPath $DistPath | Out-Null
        
        $result = Expand-HarvestArchive -ArchivePath $sourceArchive -DestinationPath $sourceTarget -PackageType "source-only"
        if ($result.Success) {
            $totalFileCount += $result.FileCount
            $totalBytes += $result.TotalBytes
        } else {
            throw "Source-only extraction failed"
        }
    }
    
    # Restore everything package  
    if ($restoreEverything) {
        $everythingArchive = Join-Path $DistPath "everything_v7_1.zip"
        $everythingTarget = "${TargetDir}_everything"
        
        # Check for split archive parts
        Restore-SplitArchive -BaseName "everything_v7_1.zip" -DistPath $DistPath | Out-Null
        
        $result = Expand-HarvestArchive -ArchivePath $everythingArchive -DestinationPath $everythingTarget -PackageType "everything"
        if ($result.Success) {
            $totalFileCount += $result.FileCount
            $totalBytes += $result.TotalBytes
        } else {
            throw "Everything extraction failed"
        }
    }
    
    # Success summary
    Write-Host ""
    Write-Host "=============================================" -ForegroundColor Cyan
    Write-Host "✅ RESTORATION COMPLETE" -ForegroundColor Green
    Write-Host "   Files restored: $totalFileCount" -ForegroundColor White
    Write-Host "   Total bytes: $($totalBytes.ToString('N0'))" -ForegroundColor White
    Write-Host "   Target directories created" -ForegroundColor White
    if ($restoreSource) { Write-Host "     - ${TargetDir}_source_only" -ForegroundColor Gray }
    if ($restoreEverything) { Write-Host "     - ${TargetDir}_everything" -ForegroundColor Gray }
    Write-Host "🟢 OK - Full Harvest v7.1 restoration successful!" -ForegroundColor Green
    Write-Host "=============================================" -ForegroundColor Cyan
    
    exit 0
}
catch {
    Write-Host ""
    Write-Host "❌ RESTORATION FAILED: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}