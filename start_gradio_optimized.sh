#!/bin/bash

# 启动优化版Gradio Web UI
# TensorRT加速 + 间隔采样

cd /mnt/ai/luminaire-detection
source venv/bin/activate

# 设置环境变量
export CUDA_VISIBLE_DEVICES=1
export HF_HOME="/mnt/ai/huggingface_cache"
export TRANSFORMERS_CACHE="/mnt/ai/huggingface_cache"
# export HF_TOKEN="your_huggingface_token_here"  # 如需使用DINOv3,请设置您的token

# TensorRT优化设置
export TORCH_COMPILE_DEBUG=0
export TORCHINDUCTOR_CACHE_DIR="/mnt/ai/torch_cache"

# 获取服务器IP
SERVER_IP=$(curl -s ifconfig.me)

echo ""
echo "⚡ 启动优化版Gradio Web UI..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📍 本地访问: http://localhost:7860"
echo "🌐 远程访问: http://${SERVER_IP}:7860"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "⚡ 性能优化:"
echo "  - TensorRT加速: 自动尝试"
echo "  - 间隔采样: 10秒/帧"
echo "  - DINOv3: ✅ 已配置"
echo "  - GPU: CUDA Device 1"
echo ""
echo "💡 使用提示:"
echo "  - 图像检测: 完整分析单张图片"
echo "  - 间隔检测: 每N秒检测一帧(降低负载)"
echo "  - 按 Ctrl+C 停止服务"
echo ""

# 运行优化版应用
python gradio_app_optimized.py
