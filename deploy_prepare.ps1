# Jetson Deployment File Preparation Script
# Copy production files to deployment directory

$sourceDir = "c:\Users\19395\Desktop\test"
$deployDir = "c:\Users\19395\Desktop\jetson_deploy"
$jetsonIP = "192.168.10.135"
$jetsonUser = "haoyu"
$jetsonPath = "~/luminaire-detection"

Write-Host "[START] Preparing Jetson deployment files..." -ForegroundColor Green
Write-Host ""

# Create deployment directory
if (Test-Path $deployDir) {
    Write-Host "[CLEAN] Removing old deployment directory..." -ForegroundColor Yellow
    Remove-Item -Path $deployDir -Recurse -Force
}

New-Item -Path $deployDir -ItemType Directory -Force | Out-Null
Write-Host "[OK] Created deployment directory: $deployDir" -ForegroundColor Green

# Core application files
Write-Host ""
Write-Host "[CORE] Copying core application files..." -ForegroundColor Cyan

$coreFiles = @(
    "gradio_app_jetson.py",
    "pipeline.py",
    "config.yaml",
    "requirements.txt"
)

foreach ($file in $coreFiles) {
    $source = Join-Path $sourceDir $file
    if (Test-Path $source) {
        Copy-Item -Path $source -Destination $deployDir -Force
        Write-Host "  [OK] $file" -ForegroundColor Green
    } else {
        Write-Host "  [WARN] $file (not found)" -ForegroundColor Yellow
    }
}

# Docker files
Write-Host ""
Write-Host "[DOCKER] Copying Docker deployment files..." -ForegroundColor Cyan

$dockerFiles = @(
    "Dockerfile.jetson",
    "docker-compose.jetson.yml",
    "deploy_jetson.sh",
    ".dockerignore"
)

foreach ($file in $dockerFiles) {
    $source = Join-Path $sourceDir $file
    if (Test-Path $source) {
        Copy-Item -Path $source -Destination $deployDir -Force
        Write-Host "  [OK] $file" -ForegroundColor Green
    } else {
        Write-Host "  [WARN] $file (not found)" -ForegroundColor Yellow
    }
}

# Documentation files
Write-Host ""
Write-Host "[DOCS] Copying documentation files..." -ForegroundColor Cyan

$docFiles = @(
    "JETSON_DOCKER_GUIDE.md",
    "JETSON_DEPLOY_COMMANDS.md",
    "JETSON_QUICK_REFERENCE.md",
    "JETSON_CHEATSHEET.txt",
    "FILES_GUIDE.md",
    "README.md"
)

foreach ($file in $docFiles) {
    $source = Join-Path $sourceDir $file
    if (Test-Path $source) {
        Copy-Item -Path $source -Destination $deployDir -Force
        Write-Host "  [OK] $file" -ForegroundColor Green
    } else {
        Write-Host "  [WARN] $file (not found)" -ForegroundColor Yellow
    }
}

# Display file list
Write-Host ""
Write-Host "[LIST] Deployment file list:" -ForegroundColor Cyan
Get-ChildItem -Path $deployDir | ForEach-Object {
    $size = if ($_.Length -gt 1MB) {
        "{0:N2} MB" -f ($_.Length / 1MB)
    } elseif ($_.Length -gt 1KB) {
        "{0:N2} KB" -f ($_.Length / 1KB)
    } else {
        "$($_.Length) B"
    }
    Write-Host ("  {0,-35} {1,10}" -f $_.Name, $size) -ForegroundColor White
}

# Display transfer commands
Write-Host ""
Write-Host ("=" * 70) -ForegroundColor DarkGray
Write-Host ""
Write-Host "[TRANSFER] Transfer files to Jetson:" -ForegroundColor Green
Write-Host ""
Write-Host "Method 1: SCP all files" -ForegroundColor Yellow
Write-Host ("=" * 55) -ForegroundColor DarkGray
Write-Host "scp -r $deployDir\* ${jetsonUser}@${jetsonIP}:${jetsonPath}/" -ForegroundColor White
Write-Host ""

Write-Host "Method 2: Use WinSCP GUI" -ForegroundColor Yellow
Write-Host ("=" * 55) -ForegroundColor DarkGray
Write-Host "1. Open WinSCP" -ForegroundColor White
Write-Host "2. Connect to: ${jetsonUser}@${jetsonIP}" -ForegroundColor White
Write-Host "3. Upload directory: $deployDir" -ForegroundColor White
Write-Host "4. Target path: ${jetsonPath}" -ForegroundColor White
Write-Host ""

Write-Host "Method 3: Step-by-step transfer (Recommended)" -ForegroundColor Yellow
Write-Host ("=" * 55) -ForegroundColor DarkGray
Write-Host "# Core application files" -ForegroundColor Cyan
Write-Host "scp $deployDir\gradio_app_jetson.py ${jetsonUser}@${jetsonIP}:${jetsonPath}/" -ForegroundColor White
Write-Host "scp $deployDir\pipeline.py ${jetsonUser}@${jetsonIP}:${jetsonPath}/" -ForegroundColor White
Write-Host "scp $deployDir\config.yaml ${jetsonUser}@${jetsonIP}:${jetsonPath}/" -ForegroundColor White
Write-Host "scp $deployDir\requirements.txt ${jetsonUser}@${jetsonIP}:${jetsonPath}/" -ForegroundColor White
Write-Host ""
Write-Host "# Docker files" -ForegroundColor Cyan
Write-Host "scp $deployDir\Dockerfile.jetson ${jetsonUser}@${jetsonIP}:${jetsonPath}/" -ForegroundColor White
Write-Host "scp $deployDir\docker-compose.jetson.yml ${jetsonUser}@${jetsonIP}:${jetsonPath}/" -ForegroundColor White
Write-Host "scp $deployDir\deploy_jetson.sh ${jetsonUser}@${jetsonIP}:${jetsonPath}/" -ForegroundColor White
Write-Host "scp $deployDir\.dockerignore ${jetsonUser}@${jetsonIP}:${jetsonPath}/" -ForegroundColor White
Write-Host ""
Write-Host "# Documentation files" -ForegroundColor Cyan
Write-Host "scp $deployDir\JETSON_DEPLOY_COMMANDS.md ${jetsonUser}@${jetsonIP}:${jetsonPath}/" -ForegroundColor White
Write-Host "scp $deployDir\JETSON_CHEATSHEET.txt ${jetsonUser}@${jetsonIP}:${jetsonPath}/" -ForegroundColor White
Write-Host ""

Write-Host ("=" * 70) -ForegroundColor DarkGray
Write-Host ""
Write-Host "[NEXT] Next steps:" -ForegroundColor Green
Write-Host "1. Transfer files to Jetson (use commands above)" -ForegroundColor White
Write-Host "2. SSH login: ssh ${jetsonUser}@${jetsonIP}" -ForegroundColor White
Write-Host "3. Change directory: cd ${jetsonPath}" -ForegroundColor White
Write-Host "4. Run deployment: ./deploy_jetson.sh" -ForegroundColor White
Write-Host ""

# Ask if user wants to transfer immediately
Write-Host "Transfer files to Jetson via SCP now? (Y/N): " -ForegroundColor Yellow -NoNewline
$response = Read-Host

if ($response -eq "Y" -or $response -eq "y") {
    Write-Host ""
    Write-Host "[TRANSFER] Starting file transfer..." -ForegroundColor Green
    Write-Host "Password: signify@1234" -ForegroundColor Yellow
    Write-Host ""
    
    # Check if scp is available
    $scpPath = Get-Command scp -ErrorAction SilentlyContinue
    if ($scpPath) {
        # Transfer files
        scp -r "$deployDir\*" "${jetsonUser}@${jetsonIP}:${jetsonPath}/"
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host ""
            Write-Host "[SUCCESS] Files transferred successfully!" -ForegroundColor Green
            Write-Host ""
            Write-Host "[CONNECT] SSH to Jetson:" -ForegroundColor Cyan
            Write-Host "ssh ${jetsonUser}@${jetsonIP}" -ForegroundColor White
        } else {
            Write-Host ""
            Write-Host "[FAILED] Transfer failed. Check network and credentials." -ForegroundColor Red
        }
    } else {
        Write-Host ""
        Write-Host "[ERROR] scp command not found" -ForegroundColor Red
        Write-Host "Please install OpenSSH Client or use WinSCP" -ForegroundColor Yellow
    }
} else {
    Write-Host ""
    Write-Host "[SKIP] Files are ready at: $deployDir" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "[DONE] Deployment preparation complete!" -ForegroundColor Green
