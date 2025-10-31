# 🚀 Jetson 部署完整命令清单

> **重要**: 此文档包含从文件传输到部署运行的所有命令，适用于无 AI 辅助的离线环境

---

## 第一步: 在 Windows 上准备和传输文件

### 1.1 运行准备脚本 (可选)

```powershell
# 进入项目目录
cd c:\Users\19395\Desktop\test

# 运行自动化准备脚本
.\prepare_jetson_deploy.ps1

# 如果提示输入，选择 Y 自动传输，或选择 N 手动传输
```

### 1.2 手动传输文件到 Jetson (如果脚本失败)

```powershell
# Jetson 连接信息
# IP: 192.168.10.135
# 用户: haoyu
# 密码: signify@1234

# 传输核心应用文件
scp c:\Users\19395\Desktop\test\gradio_app_jetson.py haoyu@192.168.10.135:~/luminaire-detection/
scp c:\Users\19395\Desktop\test\pipeline.py haoyu@192.168.10.135:~/luminaire-detection/
scp c:\Users\19395\Desktop\test\config.yaml haoyu@192.168.10.135:~/luminaire-detection/
scp c:\Users\19395\Desktop\test\requirements.txt haoyu@192.168.10.135:~/luminaire-detection/

# 传输 Docker 文件
scp c:\Users\19395\Desktop\test\Dockerfile.jetson haoyu@192.168.10.135:~/luminaire-detection/
scp c:\Users\19395\Desktop\test\docker-compose.jetson.yml haoyu@192.168.10.135:~/luminaire-detection/
scp c:\Users\19395\Desktop\test\deploy_jetson.sh haoyu@192.168.10.135:~/luminaire-detection/
scp c:\Users\19395\Desktop\test\.dockerignore haoyu@192.168.10.135:~/luminaire-detection/

# 传输文档 (可选)
scp c:\Users\19395\Desktop\test\JETSON_DOCKER_GUIDE.md haoyu@192.168.10.135:~/luminaire-detection/
scp c:\Users\19395\Desktop\test\JETSON_DEPLOY_COMMANDS.md haoyu@192.168.10.135:~/luminaire-detection/
```

---

## 第二步: SSH 连接到 Jetson

```bash
# 从 Windows 连接
ssh haoyu@192.168.10.135

# 输入密码: signify@1234
```

---

## 第三步: 在 Jetson 上检查环境

### 3.1 检查文件是否传输成功

```bash
# 进入项目目录
cd ~/luminaire-detection

# 查看文件列表
ls -lh

# 应该看到以下文件:
# gradio_app_jetson.py
# pipeline.py
# config.yaml
# requirements.txt
# Dockerfile.jetson
# docker-compose.jetson.yml
# deploy_jetson.sh
# .dockerignore
```

### 3.2 检查 Docker 是否安装

```bash
# 检查 Docker 版本
docker --version

# 如果未安装，执行以下命令
curl https://get.docker.com | sh
sudo usermod -aG docker $USER
newgrp docker
```

### 3.3 检查 NVIDIA Docker Runtime

```bash
# 检查 NVIDIA runtime
docker info | grep -i nvidia

# 应该看到包含 "nvidia" 的输出

# 如果没有，安装 nvidia-docker2
sudo apt-get update
sudo apt-get install -y nvidia-docker2
sudo systemctl restart docker
```

### 3.4 检查摄像头设备

```bash
# 查看可用的摄像头设备
ls -l /dev/video*

# 应该看到类似:
# /dev/video0
# /dev/video1 (如果有第二个摄像头)

# 测试摄像头 (可选)
v4l2-ctl --list-devices
```

---

## 第四步: 部署应用

### 方法 1: 使用自动化脚本 (推荐)

```bash
# 赋予执行权限
chmod +x deploy_jetson.sh

# 运行部署脚本
./deploy_jetson.sh

# 进入交互式菜单后:
# 输入数字 3，然后按回车
# (选项 3 = 构建并启动)

# 等待构建完成 (首次约 10-20 分钟)
```

### 方法 2: 手动使用 Docker Compose

```bash
# 2.1 构建镜像
docker-compose -f docker-compose.jetson.yml build

# 2.2 启动容器
docker-compose -f docker-compose.jetson.yml up -d

# 2.3 查看日志
docker-compose -f docker-compose.jetson.yml logs -f
```

### 方法 3: 直接使用 Docker 命令

```bash
# 3.1 构建镜像
docker build -f Dockerfile.jetson -t luminaire-detection:jetson-orin .

# 3.2 创建必要的目录
mkdir -p models results cache

# 3.3 启动容器
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

# 3.4 查看日志
docker logs -f luminaire-detection
```

---

## 第五步: 验证部署

### 5.1 检查容器状态

```bash
# 查看运行中的容器
docker ps

# 应该看到名为 "luminaire-detection" 的容器，状态为 "Up"
```

### 5.2 查看应用日志

```bash
# 实时查看日志
docker logs -f luminaire-detection

# 看到以下内容表示启动成功:
# "Running on http://0.0.0.0:7860"
# "✅ 流水线初始化完成!"

# 按 Ctrl+C 退出日志查看
```

### 5.3 访问 Gradio Web UI

在浏览器中打开以下地址之一:

- **从 Jetson 本地**: `http://localhost:7860`
- **从同一网络的其他设备**: `http://192.168.10.135:7860`

### 5.4 测试功能

1. **测试图像检测**:
   - 打开 "📸 图像检测" 标签页
   - 上传一张图片
   - 调整置信度阈值 (建议 0.15)
   - 点击 "🔍 开始检测"

2. **测试摄像头检测**:
   - 打开 "📹 摄像头实时检测" 标签页
   - 点击摄像头图标启动摄像头
   - 系统会自动每 5 秒检测一次

---

## 第六步: 性能优化 (可选)

### 6.1 启用最大性能模式

```bash
# 设置为最大性能模式 (MAXN)
sudo nvpmodel -m 0

# 锁定最大时钟频率
sudo jetson_clocks

# 查看当前模式
sudo nvpmodel -q
```

### 6.2 监控系统性能

```bash
# 方法 1: 使用 tegrastats (实时监控)
sudo tegrastats

# 方法 2: 使用 jtop (更友好的界面)
# 如果未安装，先安装
sudo pip3 install jetson-stats

# 运行 jtop
sudo jtop

# 按 Ctrl+C 退出
```

### 6.3 查看 GPU 使用情况

```bash
# 查看 GPU 状态
sudo /usr/bin/tegrastats --interval 1000

# 或使用 jtop 的实时显示
sudo jtop
```

---

## 常用管理命令

### 容器管理

```bash
# 查看所有容器 (包括停止的)
docker ps -a

# 查看容器日志
docker logs luminaire-detection

# 查看最近 100 行日志
docker logs --tail 100 luminaire-detection

# 实时跟踪日志
docker logs -f luminaire-detection

# 进入容器内部
docker exec -it luminaire-detection bash

# 在容器内执行命令后退出
exit

# 重启容器
docker restart luminaire-detection

# 停止容器
docker stop luminaire-detection

# 启动已停止的容器
docker start luminaire-detection

# 删除容器 (需先停止)
docker rm -f luminaire-detection
```

### Docker Compose 管理

```bash
# 启动服务
docker-compose -f docker-compose.jetson.yml up -d

# 停止服务
docker-compose -f docker-compose.jetson.yml down

# 重启服务
docker-compose -f docker-compose.jetson.yml restart

# 查看日志
docker-compose -f docker-compose.jetson.yml logs -f

# 查看服务状态
docker-compose -f docker-compose.jetson.yml ps
```

### 镜像管理

```bash
# 查看本地镜像
docker images

# 删除镜像
docker rmi luminaire-detection:jetson-orin

# 清理未使用的镜像
docker image prune -a

# 查看镜像占用空间
docker system df
```

---

## 故障排除命令

### 问题 1: 容器无法启动

```bash
# 查看详细错误日志
docker logs luminaire-detection

# 检查容器配置
docker inspect luminaire-detection

# 删除并重新创建容器
docker rm -f luminaire-detection
./deploy_jetson.sh
```

### 问题 2: GPU 不可用

```bash
# 检查 NVIDIA runtime
docker info | grep -i nvidia

# 测试 GPU 访问
docker run --rm --runtime=nvidia --gpus all nvidia/cuda:11.4.0-base-ubuntu20.04 nvidia-smi

# 如果失败，重新安装 nvidia-docker2
sudo apt-get install --reinstall nvidia-docker2
sudo systemctl restart docker
```

### 问题 3: 摄像头无法访问

```bash
# 检查摄像头设备
ls -l /dev/video*

# 检查设备权限
sudo chmod 666 /dev/video0

# 测试摄像头
v4l2-ctl --list-devices
v4l2-ctl -d /dev/video0 --list-formats

# 如果设备路径不同，编辑 docker-compose
nano docker-compose.jetson.yml
# 修改 devices 部分
```

### 问题 4: 端口被占用

```bash
# 查看端口占用
sudo netstat -tlnp | grep 7860

# 或使用 lsof
sudo lsof -i :7860

# 停止占用端口的进程
sudo kill -9 <进程ID>

# 或修改 docker-compose.yml 使用不同端口
# 例如改为 7861:7860
```

### 问题 5: 内存不足

```bash
# 查看内存使用
free -h

# 查看 swap
swapon --show

# 增加 swap (如果没有或太小)
sudo fallocate -l 8G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile

# 永久生效
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab

# 验证
free -h
```

### 问题 6: 模型下载慢或失败

```bash
# 方法 1: 使用国内镜像 (在容器启动前设置)
export HF_ENDPOINT=https://hf-mirror.com

# 然后启动容器
docker-compose -f docker-compose.jetson.yml up -d

# 方法 2: 在运行的容器中设置
docker exec luminaire-detection bash -c "export HF_ENDPOINT=https://hf-mirror.com"

# 方法 3: 编辑 docker-compose.yml 添加环境变量
nano docker-compose.jetson.yml
# 在 environment 部分添加:
# - HF_ENDPOINT=https://hf-mirror.com
```

### 问题 7: 构建镜像失败

```bash
# 清理 Docker 缓存
docker system prune -a

# 重新构建 (不使用缓存)
docker build --no-cache -f Dockerfile.jetson -t luminaire-detection:jetson-orin .

# 或使用 docker-compose
docker-compose -f docker-compose.jetson.yml build --no-cache
```

---

## 系统维护命令

### 磁盘空间管理

```bash
# 查看磁盘使用情况
df -h

# 查看项目目录占用
du -sh ~/luminaire-detection/*

# 清理 Docker 未使用资源
docker system prune -a --volumes

# 清理模型缓存 (谨慎操作)
rm -rf ~/luminaire-detection/cache/*
```

### 日志管理

```bash
# 查看容器日志大小
sudo du -sh /var/lib/docker/containers/*/*-json.log

# 清理日志
sudo truncate -s 0 /var/lib/docker/containers/*/*-json.log

# 或配置日志轮转 (在 docker-compose.yml 中已配置)
```

### 系统更新

```bash
# 更新系统包 (谨慎操作，可能影响 JetPack)
sudo apt-get update
sudo apt-get upgrade

# 仅更新 Docker
sudo apt-get update
sudo apt-get install --only-upgrade docker-ce
```

---

## 完整部署流程总结

```bash
# ===== 在 Jetson 上执行的完整流程 =====

# 1. 连接到 Jetson
ssh haoyu@192.168.10.135
# 密码: signify@1234

# 2. 进入项目目录
cd ~/luminaire-detection

# 3. 检查文件
ls -lh

# 4. 赋予脚本执行权限
chmod +x deploy_jetson.sh

# 5. 运行部署脚本
./deploy_jetson.sh
# 选择: 3 (构建并启动)

# 6. 查看日志 (等待启动完成)
docker logs -f luminaire-detection
# 看到 "Running on http://0.0.0.0:7860" 表示成功
# 按 Ctrl+C 退出

# 7. 启用最大性能 (可选)
sudo nvpmodel -m 0
sudo jetson_clocks

# 8. 访问 Web UI
# 浏览器打开: http://192.168.10.135:7860

# 9. 测试功能
# - 上传图片测试检测
# - 启动摄像头测试实时检测

# 完成!
```

---

## 快速参考

### 重要路径

- **项目目录**: `~/luminaire-detection`
- **模型缓存**: `~/luminaire-detection/cache`
- **检测结果**: `~/luminaire-detection/results`
- **模型文件**: `~/luminaire-detection/models`

### 重要端口

- **Gradio UI**: `7860`

### 重要命令

```bash
# 查看容器状态
docker ps

# 查看日志
docker logs -f luminaire-detection

# 重启容器
docker restart luminaire-detection

# 进入容器
docker exec -it luminaire-detection bash

# 监控性能
sudo jtop
```

---

## 注意事项

1. **首次启动**: 需要下载模型，可能需要 10-30 分钟
2. **网络要求**: 需要访问 HuggingFace (hf.co 或 hf-mirror.com)
3. **显存要求**: 大模型需要约 8-12GB GPU 显存
4. **性能模式**: 建议使用 MAXN 模式获得最佳性能
5. **摄像头**: 确保 USB 摄像头已连接到 /dev/video0

---

**文档版本**: 2024-10-29  
**适用环境**: Jetson AGX Orin 64GB + JetPack 5.x + Docker
