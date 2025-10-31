# AI Models Downloader - OWLv2 and Depth Anything
# Downloads all required models and prepares for Jetson transfer

Write-Host "=== AI Models Downloader ===" -ForegroundColor Green
Write-Host ""

# Define models to download
$models = @(
    @{
        Name = "google/owlv2-large-patch14-ensemble"
        Description = "OWLv2 Large - Object Detection"
        Size = "~3GB"
        Output = "owlv2_large.zip"
    },
    @{
        Name = "LiheYoung/depth-anything-large-hf"
        Description = "Depth Anything Large - Depth Estimation"
        Size = "~1.5GB"
        Output = "depth_anything_large.zip"
    },
    @{
        Name = "LiheYoung/depth-anything-small-hf"
        Description = "Depth Anything Small - Depth Estimation (Backup)"
        Size = "~100MB"
        Output = "depth_anything_small.zip"
    }
)

Write-Host "This script will download the following models:" -ForegroundColor Cyan
Write-Host ""
foreach ($model in $models) {
    Write-Host "  [$($model.Size)] $($model.Name)" -ForegroundColor White
    Write-Host "    -> $($model.Description)" -ForegroundColor Gray
}
Write-Host ""
Write-Host "Total download size: ~4.5GB" -ForegroundColor Yellow
Write-Host ""

$continue = Read-Host "Continue with download? (Y/N)"
if ($continue -ne "Y" -and $continue -ne "y") {
    Write-Host "Cancelled." -ForegroundColor Yellow
    exit 0
}

# Install huggingface-cli
Write-Host ""
Write-Host "Installing huggingface-hub..." -ForegroundColor Cyan
pip install -q huggingface-hub[cli] 2>$null

Write-Host ""
Write-Host "Starting downloads..." -ForegroundColor Green
Write-Host "This may take 20-60 minutes depending on your connection." -ForegroundColor Yellow
Write-Host ""

$downloadedFiles = @()
$failedModels = @()

foreach ($model in $models) {
    Write-Host "======================================" -ForegroundColor DarkGray
    Write-Host "Downloading: $($model.Name)" -ForegroundColor Cyan
    Write-Host "Description: $($model.Description)" -ForegroundColor Gray
    Write-Host "Size: $($model.Size)" -ForegroundColor Gray
    Write-Host ""
    
    $modelDir = Join-Path $PSScriptRoot "model_downloads\$($model.Name.Replace('/', '--'))"
    $outputZip = Join-Path $PSScriptRoot $model.Output
    
    # Create directory
    New-Item -ItemType Directory -Force -Path $modelDir | Out-Null
    
    # Download
    $env:HF_HUB_CACHE = $modelDir
    huggingface-cli download $model.Name --local-dir $modelDir --local-dir-use-symlinks False
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Download complete! Compressing..." -ForegroundColor Green
        
        # Remove old zip
        if (Test-Path $outputZip) {
            Remove-Item $outputZip -Force
        }
        
        # Compress
        Compress-Archive -Path "$modelDir\*" -DestinationPath $outputZip -CompressionLevel Optimal
        
        $zipSize = [math]::Round((Get-Item $outputZip).Length / 1MB, 2)
        Write-Host "Compressed: $outputZip ($zipSize MB)" -ForegroundColor Green
        
        $downloadedFiles += @{
            Model = $model.Name
            File = $outputZip
            Size = $zipSize
        }
    } else {
        Write-Host "Failed to download $($model.Name)" -ForegroundColor Red
        $failedModels += $model.Name
    }
    
    Write-Host ""
}

# Summary
Write-Host "======================================" -ForegroundColor DarkGray
Write-Host "=== Download Summary ===" -ForegroundColor Green
Write-Host ""

if ($downloadedFiles.Count -gt 0) {
    Write-Host "Successfully downloaded:" -ForegroundColor Green
    foreach ($file in $downloadedFiles) {
        Write-Host "  ✓ $($file.Model)" -ForegroundColor White
        Write-Host "    File: $($file.File) ($($file.Size) MB)" -ForegroundColor Gray
    }
    Write-Host ""
    
    Write-Host "Transfer all to Jetson:" -ForegroundColor Yellow
    foreach ($file in $downloadedFiles) {
        $fileName = Split-Path $file.File -Leaf
        Write-Host "  scp $fileName haoyu@192.168.10.135:~/luminaire-detection/" -ForegroundColor White
    }
    Write-Host ""
    
    Write-Host "On Jetson, extract and copy to container:" -ForegroundColor Yellow
    Write-Host "  cd ~/luminaire-detection" -ForegroundColor White
    Write-Host "  # Extract each model:" -ForegroundColor Gray
    foreach ($file in $downloadedFiles) {
        $fileName = Split-Path $file.File -Leaf
        $modelName = $file.Model.Replace('/', '--')
        Write-Host "  unzip $fileName -d models_temp/$modelName" -ForegroundColor White
        Write-Host "  docker cp models_temp/$modelName luminaire-detection:/app/.cache/huggingface/models--$modelName" -ForegroundColor White
    }
    Write-Host "  docker restart luminaire-detection" -ForegroundColor White
    Write-Host ""
}

if ($failedModels.Count -gt 0) {
    Write-Host "Failed downloads:" -ForegroundColor Red
    foreach ($failed in $failedModels) {
        Write-Host "  ✗ $failed" -ForegroundColor Red
    }
    Write-Host ""
}

Write-Host "=== Download Complete ===" -ForegroundColor Green
