# 🚀 Jetson AGX Orin Docker 快速部署指南

## 📋 前提条件

### 1. 硬件要求

- Jetson AGX Orin 64GB
- USB 摄像头 (可选)
- 至少 20GB 可用存储空间

### 2. 软件要求

- JetPack 5.x
- Docker
- NVIDIA Container Runtime

## 🔧 安装 Docker 和 NVIDIA Runtime

### 安装 Docker

```bash
# 安装 Docker
curl https://get.docker.com | sh

# 添加用户到 docker 组
sudo usermod -aG docker $USER

# 重新登录或执行
newgrp docker

# 验证安装
docker --version
```

### 安装 NVIDIA Container Runtime

```bash
# JetPack 5.x 已预装,检查
docker info | grep -i nvidia

# 如果没有,安装
sudo apt-get update
sudo apt-get install -y nvidia-docker2
sudo systemctl restart docker
```

## 📦 部署步骤

### 方法 1: 自动部署 (推荐)

```bash
# 1. 传输项目文件到 Jetson
# 在 Windows 电脑上执行:
scp -r c:\Users\19395\Desktop\test\* haoyu@192.168.10.135:~/luminaire-detection/

# 2. SSH 到 Jetson
ssh haoyu@192.168.10.135

# 3. 进入项目目录
cd ~/luminaire-detection

# 4. 赋予执行权限
chmod +x deploy_jetson.sh

# 5. 运行部署脚本
./deploy_jetson.sh

# 选择选项 3 (构建并启动)
```

### 方法 2: 手动部署

```bash
# 1. 构建镜像
docker build -f Dockerfile.jetson -t luminaire-detection:jetson-orin .

# 2. 启动容器
docker run -d \
  --name luminaire-detection \
  --runtime=nvidia \
  --gpus all \
  -p 7860:7860 \
  -v $(pwd)/models:/app/models \
  -v $(pwd)/results:/app/results \
  -v $(pwd)/cache:/app/.cache \
  --device /dev/video0:/dev/video0 \
  --restart unless-stopped \
  luminaire-detection:jetson-orin

# 3. 查看日志
docker logs -f luminaire-detection
```

### 方法 3: Docker Compose

```bash
# 启动
docker-compose -f docker-compose.jetson.yml up -d

# 停止
docker-compose -f docker-compose.jetson.yml down

# 查看日志
docker-compose -f docker-compose.jetson.yml logs -f
```

## 🎯 访问应用

### Gradio Web UI

- 本地访问: `http://localhost:7860`
- 网络访问: `http://192.168.10.135:7860`

## 📊 性能优化

### 最大性能模式

```bash
# 设置为最大性能模式
sudo nvpmodel -m 0
sudo jetson_clocks

# 查看当前模式
sudo nvpmodel -q
```

### 监控性能

```bash
# 实时监控
sudo tegrastats

# 或使用 jtop (更友好)
sudo pip install jetson-stats
sudo jtop
```

## 🔧 容器管理

### 查看容器状态

```bash
docker ps -a
```

### 进入容器

```bash
docker exec -it luminaire-detection bash
```

### 查看日志

```bash
# 实时日志
docker logs -f luminaire-detection

# 最近 100 行
docker logs --tail 100 luminaire-detection
```

### 重启容器

```bash
docker restart luminaire-detection
```

### 停止容器

```bash
docker stop luminaire-detection
```

### 删除容器

```bash
docker rm -f luminaire-detection
```

### 清理镜像

```bash
# 删除镜像
docker rmi luminaire-detection:jetson-orin

# 清理未使用的镜像
docker image prune -a
```

## 🐛 故障排除

### 问题 1: GPU 不可用

```bash
# 检查 NVIDIA runtime
docker info | grep -i nvidia

# 重新安装 nvidia-docker2
sudo apt-get install --reinstall nvidia-docker2
sudo systemctl restart docker
```

### 问题 2: 内存不足

```bash
# 增加 swap
sudo fallocate -l 8G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile

# 永久生效
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

### 问题 3: 模型下载慢

```bash
# 使用国内镜像
docker run ... -e HF_ENDPOINT=https://hf-mirror.com ...
```

### 问题 4: 摄像头不可用

```bash
# 检查摄像头设备
ls -l /dev/video*

# 测试摄像头
v4l2-ctl --list-devices

# 添加摄像头设备到容器
docker run ... --device /dev/video0:/dev/video0 ...
```

## 🔄 更新应用

### 方法 1: 重新构建

```bash
# 停止并删除旧容器
docker stop luminaire-detection
docker rm luminaire-detection

# 重新构建镜像
docker build -f Dockerfile.jetson -t luminaire-detection:jetson-orin .

# 启动新容器
docker run ...
```

### 方法 2: 挂载代码目录 (开发模式)

```bash
docker run ... -v $(pwd):/app ...
```

## 📈 性能基准

### 预期性能 (Jetson AGX Orin 64GB)

- **OWLv2-Large + DINOv3-Large + Depth Anything V2 Large**
- **精度**: FP16
- **推理时间**: 0.5-1.5 秒/帧
- **FPS**: 0.7-2 FPS
- **显存占用**: 8-12 GB
- **功耗**: 30-50W (MAXN 模式)

## 📝 注意事项

1. **首次运行**: 需要下载模型,可能需要 10-20 分钟
2. **缓存目录**: 模型会缓存在 `./cache` 目录
3. **持久化**: 挂载卷确保数据持久化
4. **网络**: 确保 Jetson 可以访问 HuggingFace

## 🆘 获取帮助

查看完整文档: [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)

## 📜 许可证

[项目许可证信息]
