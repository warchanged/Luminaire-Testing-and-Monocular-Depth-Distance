@echo off
echo === Luminaire Detection Project Cleanup ===
echo.
echo This will remove:
echo   - Test scripts (test_*.py)
echo   - Old documentation files (multiple MD files)
echo   - Temporary deployment scripts
echo.
set /p confirm="Continue? (y/n): "
if /i not "%confirm%"=="y" (
    echo Cancelled
    exit /b 0
)

echo.
echo Cleaning up...

REM Remove test scripts
del /q test_threshold_fine.py test_quick.py test_multi_lights.py 2>nul
echo [OK] Removed test scripts

REM Remove old evaluation/step scripts
del /q evaluate.py step1_download_data.py step4_setup_depth_anything.py run_all.py realtime.py 2>nul
echo [OK] Removed old development scripts

REM Remove old documentation
del /q COMPLETION_REPORT.md DEPLOYMENT_CHECKLIST.md DEPLOYMENT_GUIDE.md DEPLOY_TO_JETSON_GUIDE.md 2>nul
del /q DOCUMENTATION_SUMMARY.md FILES_GUIDE.md JETSON_DEPLOY_COMMANDS.md JETSON_DOCKER_GUIDE.md 2>nul
del /q JETSON_OPTIMIZATION_SUMMARY.md JETSON_QUICK_REFERENCE.md OPTIMIZATION_GUIDE.md QUICK_START_JETSON.md 2>nul
del /q 如何部署到Jetson.md 网线部署到Jetson-快速指南.md 网线配置指南.md 命令速查表.txt 2>nul
echo [OK] Removed old documentation

REM Remove temporary scripts
del /q deploy_prepare.ps1 deploy_simple.ps1 deploy_quick.ps1 check_jetson_files.ps1 2>nul
del /q setup_network.ps1 test_jetson_connection.ps1 deploy_jetson.sh setup_jetson_network.sh 2>nul
del /q check_jetson_env.sh diagnose_jetson.sh start_ssh_tunnel.bat update_server.bat 2>nul
echo [OK] Removed temporary deployment scripts

REM Remove old docker files
del /q docker-compose.jetson.yml Dockerfile.jetson 2>nul
echo [OK] Removed old docker files

REM Remove HTML test files
del /q webcam_client.html webcam_test_simple.html 2>nul
echo [OK] Removed HTML test files

echo.
echo === Cleanup Complete ====
echo.
echo Remaining CORE files:
echo    - gradio_app_jetson.py (main application)
echo    - pipeline.py (detection pipeline)
echo    - config_multi_lights.py (configuration)
echo    - tensorrt_utils.py (optimization)
echo    - docker-compose.yml, start.sh
echo    - utils/ (helper modules)
echo.
echo Backup versions kept:
echo    - pipeline_owlv2.py
echo    - gradio_app_optimized.py
echo    - gradio_app.py
echo.
pause
