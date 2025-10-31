# ⚡ Jetson 部署速查卡

## 📋 快速部署 (5 分钟版)

```bash
# 1. SSH 连接
ssh haoyu@192.168.10.135
# 密码: signify@1234

# 2. 进入目录
cd ~/luminaire-detection

# 3. 部署
chmod +x deploy_jetson.sh
./deploy_jetson.sh
# 输入: 3 (构建并启动)

# 4. 查看日志
docker logs -f luminaire-detection

# 5. 访问 UI
# 浏览器: http://192.168.10.135:7860
```

---

## 🔧 常用命令

### 容器管理

```bash
docker ps                              # 查看状态
docker logs -f luminaire-detection     # 查看日志
docker restart luminaire-detection     # 重启
docker stop luminaire-detection        # 停止
docker start luminaire-detection       # 启动
```

### 性能监控

```bash
sudo jtop                # GPU/CPU 监控
sudo tegrastats          # 系统状态
sudo nvpmodel -q         # 查看功耗模式
```

### 性能优化

```bash
sudo nvpmodel -m 0       # 最大性能模式
sudo jetson_clocks       # 锁定最高频率
```

---

## 🐛 故障排除

### GPU 不可用

```bash
docker info | grep -i nvidia
sudo apt-get install --reinstall nvidia-docker2
sudo systemctl restart docker
```

### 摄像头问题

```bash
ls -l /dev/video*
sudo chmod 666 /dev/video0
v4l2-ctl --list-devices
```

### 端口占用

```bash
sudo netstat -tlnp | grep 7860
sudo kill -9 <进程ID>
```

### 内存不足

```bash
free -h
sudo fallocate -l 8G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

### 清理空间

```bash
docker system prune -a
rm -rf ~/luminaire-detection/cache/*
```

---

## 📞 重要信息

- **IP**: 192.168.10.135
- **用户**: haoyu
- **密码**: signify@1234
- **端口**: 7860
- **路径**: ~/luminaire-detection

---

**详细文档**: JETSON_DEPLOY_COMMANDS.md
