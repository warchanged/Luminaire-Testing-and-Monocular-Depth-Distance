#!/bin/bash

# 更新服务器代码脚本

echo "========================================="
echo "  更新 Gradio 代码到服务器"
echo "========================================="
echo ""

# 服务器信息
SERVER="haoyu@52.18.175.128"
KEY_FILE="C:/Users/19395/Downloads/haoyu.pem"
REMOTE_DIR="/mnt/ai/luminaire-detection"

echo "📤 上传 gradio_app_optimized.py..."
scp -i "$KEY_FILE" gradio_app_optimized.py "$SERVER:$REMOTE_DIR/"

echo ""
echo "✅ 上传完成!"
echo ""
echo "现在请在服务器上重启 Gradio:"
echo "  cd $REMOTE_DIR"
echo "  pkill -f gradio_app"
echo "  source venv/bin/activate"
echo "  export CUDA_VISIBLE_DEVICES=1"
echo "  export HF_HOME=\"/mnt/ai/huggingface_cache\""
echo "  export TRANSFORMERS_CACHE=\"/mnt/ai/huggingface_cache\""
echo "  python gradio_app_optimized.py"
echo ""

pause
