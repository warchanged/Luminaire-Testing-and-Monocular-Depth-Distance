# 🚀 Jetson 快速部署 - 3 步完成

## 步骤 1: 准备文件 (Windows 上执行)

```powershell
# 进入项目目录
cd c:\Users\19395\Desktop\test

# 运行自动化脚本
.\prepare_jetson_deploy.ps1

# 提示时输入 Y 自动传输,或手动复制命令传输
```

**密码**: `signify@1234`

---

## 步骤 2: SSH 到 Jetson

```bash
ssh haoyu@192.168.10.135
# 密码: signify@1234

# 进入项目目录
cd ~/luminaire-detection

# 查看文件
ls -lh
```

---

## 步骤 3: 启动 Docker 容器

```bash
# 赋予执行权限
chmod +x deploy_jetson.sh

# 运行部署脚本
./deploy_jetson.sh

# 交互菜单中选择: 3) 构建并启动
```

**等待时间**: 首次构建约 10-20 分钟

---

## ✅ 验证部署

### 1. 查看日志

```bash
docker logs -f luminaire-detection
```

看到 "Running on <http://0.0.0.0:7860>" 表示成功!

### 2. 访问 Gradio UI

- 本地: <http://localhost:7860>
- 网络: <http://192.168.10.135:7860>

### 3. 测试功能

1. **图像检测**: 上传图片测试
2. **摄像头检测**: 启动摄像头测试 (自动每5秒检测)

---

## 🔧 常用命令

```bash
# 查看容器状态
docker ps

# 查看日志
docker logs luminaire-detection

# 重启容器
docker restart luminaire-detection

# 停止容器
docker stop luminaire-detection

# 进入容器
docker exec -it luminaire-detection bash

# 监控性能
sudo jtop  # 或 sudo tegrastats
```

---

## 📊 性能优化 (可选)

### 最大性能模式

```bash
sudo nvpmodel -m 0
sudo jetson_clocks
```

### 查看当前模式

```bash
sudo nvpmodel -q
```

---

## 🐛 故障排除

### 问题 1: 摄像头不可用

```bash
# 检查摄像头设备
ls -l /dev/video*

# 如果没有 video0,更新 docker-compose.jetson.yml
# devices 部分添加正确的设备路径
```

### 问题 2: GPU 不可用

```bash
# 检查 NVIDIA runtime
docker info | grep -i nvidia

# 如果没有,安装 nvidia-docker2
sudo apt-get install nvidia-docker2
sudo systemctl restart docker
```

### 问题 3: 内存不足

```bash
# 检查内存和 swap
free -h

# 如果需要,增加 swap
sudo fallocate -l 8G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

---

## 📚 更多信息

- [完整部署指南](JETSON_DOCKER_GUIDE.md)
- [文件说明](FILES_GUIDE.md)
- [优化总结](JETSON_OPTIMIZATION_SUMMARY.md)

---

**预计总耗时**: 30-40 分钟 (含首次构建)

**成功标志**:

- ✅ Gradio UI 可访问
- ✅ 图像检测正常
- ✅ 摄像头检测正常
- ✅ 距离估计准确
