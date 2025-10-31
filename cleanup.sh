#!/bin/bash
# Cleanup Script - Remove unnecessary files

echo "=== Luminaire Detection Project Cleanup ==="
echo ""
echo "This will remove:"
echo "  - Test scripts (test_*.py)"
echo "  - Old documentation files (multiple MD files)"
echo "  - Temporary deployment scripts"
echo ""
read -p "Continue? (y/n) " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Cancelled"
    exit 0
fi

echo "Cleaning up..."

# Remove old documentation (keep only README.md)
rm -f COMPLETION_REPORT.md
rm -f DEPLOYMENT_CHECKLIST.md
rm -f DEPLOYMENT_GUIDE.md
rm -f DEPLOY_TO_JETSON_GUIDE.md
rm -f DOCUMENTATION_SUMMARY.md
rm -f FILES_GUIDE.md
rm -f JETSON_CHEATSHEET.txt
rm -f JETSON_DEPLOY_COMMANDS.md
rm -f JETSON_DOCKER_GUIDE.md
rm -f JETSON_OPTIMIZATION_SUMMARY.md
rm -f JETSON_QUICK_REFERENCE.md
rm -f OPTIMIZATION_GUIDE.md
rm -f QUICK_START_JETSON.md
rm -f 如何部署到Jetson.md
rm -f 网线部署到Jetson-快速指南.md
rm -f 网线配置指南.md
rm -f 命令速查表.txt
echo "✓ Removed old documentation"

# Remove temporary scripts
rm -f deploy_prepare.ps1
rm -f deploy_simple.ps1
rm -f deploy_quick.ps1
rm -f check_jetson_files.ps1
rm -f setup_network.ps1
rm -f test_jetson_connection.ps1
rm -f deploy_jetson.sh
rm -f setup_jetson_network.sh
rm -f check_jetson_env.sh
rm -f diagnose_jetson.sh
rm -f start_ssh_tunnel.bat
rm -f update_server.bat
echo "✓ Removed temporary deployment scripts"

# Remove old docker files
rm -f docker-compose.jetson.yml
rm -f Dockerfile.jetson
echo "✓ Removed old docker files"

# Remove HTML test files
rm -f webcam_client.html
rm -f webcam_test_simple.html
echo "✓ Removed HTML test files"

# Remove test scripts only (keep core pipeline and backup versions)
rm -f test_threshold_fine.py
rm -f test_quick.py
rm -f test_multi_lights.py
echo "✓ Removed test scripts"

# Remove old evaluation/step scripts
rm -f evaluate.py
rm -f step1_download_data.py
rm -f step4_setup_depth_anything.py
rm -f run_all.py
rm -f realtime.py
echo "✓ Removed old development scripts"

echo ""
echo "=== Cleanup Complete ===="
echo ""
echo "✅ Remaining CORE files:"
echo "   - gradio_app_jetson.py (main application)"
echo "   - pipeline.py (detection pipeline)"
echo "   - config_multi_lights.py (configuration)"
echo "   - tensorrt_utils.py (optimization)"
echo "   - docker-compose.yml, start.sh"
echo "   - utils/ (helper modules)"
echo ""
echo "📦 Backup versions kept:"
echo "   - pipeline_owlv2.py"
echo "   - gradio_app_optimized.py"
echo "   - gradio_app.py"
echo ""
