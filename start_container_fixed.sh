#!/bin/bash

echo "=== 启动Luminaire Detection容器 (已修复版本) ==="

# 停止旧容器
docker stop luminaire-detection 2>/dev/null
docker rm luminaire-detection 2>/dev/null

# 启动新容器并应用所有修复
docker run -d \
  --name luminaire-detection \
  --runtime nvidia \
  --gpus all \
  -p 7860:7860 \
  -v $(pwd)/models:/app/models \
  -v $(pwd)/results:/app/results \
  -v $(pwd)/cache:/app/.cache \
  --device /dev/video0:/dev/video0 \
  --device /dev/video1:/dev/video1 \
  --group-add video \
  --privileged \
  -e CUDA_VISIBLE_DEVICES=0 \
  -e HF_HOME=/app/.cache/huggingface \
  -e TRANSFORMERS_CACHE=/app/.cache/huggingface \
  -e GRADIO_SERVER_NAME=0.0.0.0 \
  -e GRADIO_SERVER_PORT=7860 \
  -e LD_LIBRARY_PATH=/usr/local/lib/python3.8/dist-packages/opencv_python_headless.libs \
  --restart unless-stopped \
  luminaire-detection:jetson-orin-fixed \
  bash -c '
    wget -q http://ports.ubuntu.com/pool/main/libf/libffi/libffi8_3.4.2-4_arm64.deb && \
    dpkg -i libffi8_3.4.2-4_arm64.deb && \
    pip3 uninstall -y opencv-python opencv-python-headless opencv-contrib-python 2>/dev/null || true && \
    rm -rf /usr/local/lib/python3.8/dist-packages/cv2* && \
    pip3 cache purge && \
    pip3 install --no-cache-dir -i https://pypi.tuna.tsinghua.edu.cn/simple opencv-python-headless==4.5.3.56 && \
    sed -i "s/stream_every=/every=/g" /app/gradio_app_jetson.py && \
    export LD_LIBRARY_PATH=/usr/local/lib/python3.8/dist-packages/opencv_python_headless.libs:$LD_LIBRARY_PATH && \
    cd /app && \
    python3 gradio_app_jetson.py
  '

echo ""
echo "容器已启动！等待应用加载..."
sleep 10

echo ""
echo "=== 容器状态 ==="
docker ps | grep luminaire

echo ""
echo "=== 应用日志 (最后30行) ==="
docker logs --tail 30 luminaire-detection

echo ""
echo "==============================================="
echo "访问地址: http://192.168.10.135:7860"
echo "查看实时日志: docker logs -f luminaire-detection"
echo "停止服务: docker stop luminaire-detection"
echo "重启服务: docker restart luminaire-detection"
echo "==============================================="
