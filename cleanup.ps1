# Cleanup Script - Remove unnecessary files (Windows PowerShell)

Write-Host "=== Luminaire Detection Project Cleanup ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "This will remove:" -ForegroundColor Yellow
Write-Host "  - Test scripts (test_*.py)" -ForegroundColor Gray
Write-Host "  - Old documentation files (multiple MD files)" -ForegroundColor Gray
Write-Host "  - Temporary deployment scripts" -ForegroundColor Gray
Write-Host ""

$response = Read-Host "Continue? (y/n)"
if ($response -ne "y" -and $response -ne "Y") {
    Write-Host "Cancelled" -ForegroundColor Red
    exit 0
}

Write-Host ""
Write-Host "Cleaning up..." -ForegroundColor Green

# Remove test scripts
Remove-Item -Path "test_threshold_fine.py", "test_quick.py", "test_multi_lights.py" -ErrorAction SilentlyContinue
Write-Host "✓ Removed test scripts" -ForegroundColor Green

# Remove old evaluation/step scripts
Remove-Item -Path "evaluate.py", "step1_download_data.py", "step4_setup_depth_anything.py", "run_all.py", "realtime.py" -ErrorAction SilentlyContinue
Write-Host "✓ Removed old development scripts" -ForegroundColor Green

# Remove old documentation (keep only README.md)
$docsToRemove = @(
    "COMPLETION_REPORT.md",
    "DEPLOYMENT_CHECKLIST.md",
    "DEPLOYMENT_GUIDE.md",
    "DEPLOY_TO_JETSON_GUIDE.md",
    "DOCUMENTATION_SUMMARY.md",
    "FILES_GUIDE.md",
    "JETSON_DEPLOY_COMMANDS.md",
    "JETSON_DOCKER_GUIDE.md",
    "JETSON_OPTIMIZATION_SUMMARY.md",
    "JETSON_QUICK_REFERENCE.md",
    "OPTIMIZATION_GUIDE.md",
    "QUICK_START_JETSON.md",
    "如何部署到Jetson.md",
    "网线部署到Jetson-快速指南.md",
    "网线配置指南.md",
    "命令速查表.txt"
)
foreach ($doc in $docsToRemove) {
    Remove-Item -Path $doc -ErrorAction SilentlyContinue
}
Write-Host "✓ Removed old documentation" -ForegroundColor Green

# Remove temporary scripts
$scriptsToRemove = @(
    "deploy_prepare.ps1",
    "deploy_simple.ps1",
    "deploy_quick.ps1",
    "check_jetson_files.ps1",
    "setup_network.ps1",
    "test_jetson_connection.ps1",
    "deploy_jetson.sh",
    "setup_jetson_network.sh",
    "check_jetson_env.sh",
    "diagnose_jetson.sh",
    "start_ssh_tunnel.bat",
    "update_server.bat"
)
foreach ($script in $scriptsToRemove) {
    Remove-Item -Path $script -ErrorAction SilentlyContinue
}
Write-Host "✓ Removed temporary deployment scripts" -ForegroundColor Green

# Remove old docker files
Remove-Item -Path "docker-compose.jetson.yml", "Dockerfile.jetson" -ErrorAction SilentlyContinue
Write-Host "✓ Removed old docker files" -ForegroundColor Green

# Remove HTML test files
Remove-Item -Path "webcam_client.html", "webcam_test_simple.html" -ErrorAction SilentlyContinue
Write-Host "✓ Removed HTML test files" -ForegroundColor Green

Write-Host ""
Write-Host "=== Cleanup Complete ====" -ForegroundColor Cyan
Write-Host ""
Write-Host "✅ Remaining CORE files:" -ForegroundColor Green
Write-Host "   - gradio_app_jetson.py (main application)" -ForegroundColor White
Write-Host "   - pipeline.py (detection pipeline)" -ForegroundColor White
Write-Host "   - config_multi_lights.py (configuration)" -ForegroundColor White
Write-Host "   - tensorrt_utils.py (optimization)" -ForegroundColor White
Write-Host "   - docker-compose.yml, start.sh" -ForegroundColor White
Write-Host "   - utils/ (helper modules)" -ForegroundColor White
Write-Host ""
Write-Host "📦 Backup versions kept:" -ForegroundColor Yellow
Write-Host "   - pipeline_owlv2.py" -ForegroundColor White
Write-Host "   - gradio_app_optimized.py" -ForegroundColor White
Write-Host "   - gradio_app.py" -ForegroundColor White
Write-Host ""
