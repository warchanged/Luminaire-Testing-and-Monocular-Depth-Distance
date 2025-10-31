# ✅ Jetson 部署检查清单

## 📋 部署前准备

### Windows 端

- [ ] 项目文件位于: `c:\Users\19395\Desktop\test`
- [ ] 已安装 OpenSSH 客户端 (或 WinSCP)
- [ ] 可以 ping 通 Jetson: `ping 192.168.10.135`

### Jetson 端

- [ ] Jetson AGX Orin 64GB 已开机
- [ ] IP 地址: 192.168.10.135
- [ ] SSH 端口 22 可访问
- [ ] 登录凭据: haoyu / signify@1234

---

## 🚀 部署步骤检查清单

### 第一步: 文件传输

- [ ] 运行 `prepare_jetson_deploy.ps1`
- [ ] 或手动 SCP 传输所有文件
- [ ] 确认以下文件已传输:
  - [ ] gradio_app_jetson.py
  - [ ] pipeline.py
  - [ ] config.yaml
  - [ ] requirements.txt
  - [ ] Dockerfile.jetson
  - [ ] docker-compose.jetson.yml
  - [ ] deploy_jetson.sh
  - [ ] .dockerignore
  - [ ] JETSON_DEPLOY_COMMANDS.md

### 第二步: SSH 连接

- [ ] 成功 SSH 到 Jetson: `ssh haoyu@192.168.10.135`
- [ ] 进入项目目录: `cd ~/luminaire-detection`
- [ ] 确认文件存在: `ls -lh`

### 第三步: 环境检查

- [ ] Docker 已安装: `docker --version`
- [ ] NVIDIA runtime 可用: `docker info | grep -i nvidia`
- [ ] 摄像头已连接: `ls -l /dev/video*`
- [ ] 磁盘空间充足: `df -h` (至少 20GB 可用)

### 第四步: 构建和启动

- [ ] 赋予执行权限: `chmod +x deploy_jetson.sh`
- [ ] 运行部署脚本: `./deploy_jetson.sh`
- [ ] 选择选项 3: "构建并启动"
- [ ] 等待构建完成 (10-20 分钟)

### 第五步: 验证部署

- [ ] 容器正在运行: `docker ps`
- [ ] 日志显示成功: `docker logs luminaire-detection`
- [ ] 看到: "Running on <http://0.0.0.0:7860>"
- [ ] 看到: "✅ 流水线初始化完成!"

### 第六步: 测试功能

- [ ] 浏览器访问: <http://192.168.10.135:7860>
- [ ] Gradio UI 正常加载
- [ ] 图像检测功能测试:
  - [ ] 上传图片
  - [ ] 调整置信度阈值
  - [ ] 点击检测
  - [ ] 查看检测结果
  - [ ] 查看距离估计
  - [ ] 查看深度图 (如启用)
- [ ] 摄像头检测功能测试:
  - [ ] 启动摄像头
  - [ ] 自动检测每 5 秒触发
  - [ ] 查看实时检测结果
  - [ ] FPS 显示正常

---

## 🔧 性能优化检查清单

- [ ] 启用最大性能模式: `sudo nvpmodel -m 0`
- [ ] 锁定最高频率: `sudo jetson_clocks`
- [ ] 确认当前模式: `sudo nvpmodel -q` (应显示 MAXN)
- [ ] 安装性能监控工具: `sudo pip3 install jetson-stats`
- [ ] 运行 jtop 查看性能: `sudo jtop`

---

## 📊 性能基准验证

### 预期指标 (Jetson AGX Orin 64GB)

- [ ] 图像检测时间: 0.5-1.5 秒/帧
- [ ] GPU 显存占用: 8-12 GB
- [ ] GPU 利用率: 70-95%
- [ ] 功耗 (MAXN): 30-50W
- [ ] 容器稳定运行: > 1 小时无错误

---

## 🐛 故障排除检查清单

### 如果容器无法启动

- [ ] 查看详细日志: `docker logs luminaire-detection`
- [ ] 检查端口占用: `sudo netstat -tlnp | grep 7860`
- [ ] 检查磁盘空间: `df -h`
- [ ] 检查内存: `free -h`

### 如果 GPU 不可用

- [ ] 检查 NVIDIA runtime: `docker info | grep -i nvidia`
- [ ] 重新安装: `sudo apt-get install --reinstall nvidia-docker2`
- [ ] 重启 Docker: `sudo systemctl restart docker`
- [ ] 测试 GPU: `docker run --rm --runtime=nvidia --gpus all nvidia/cuda:11.4.0-base-ubuntu20.04 nvidia-smi`

### 如果摄像头不可用

- [ ] 检查设备: `ls -l /dev/video*`
- [ ] 修改权限: `sudo chmod 666 /dev/video0`
- [ ] 测试摄像头: `v4l2-ctl --list-devices`
- [ ] 更新 docker-compose.yml 设备映射

### 如果模型下载失败

- [ ] 检查网络: `ping hf.co` 或 `ping hf-mirror.com`
- [ ] 设置镜像: `export HF_ENDPOINT=https://hf-mirror.com`
- [ ] 查看容器日志中的下载进度

### 如果内存不足

- [ ] 检查 swap: `swapon --show`
- [ ] 创建 swap: `sudo fallocate -l 8G /swapfile`
- [ ] 启用 swap: 参考 JETSON_DEPLOY_COMMANDS.md

---

## 📝 部署后维护检查清单

### 日常监控

- [ ] 每天检查容器状态: `docker ps`
- [ ] 定期查看日志: `docker logs --tail 100 luminaire-detection`
- [ ] 监控性能: `sudo jtop` 或 `sudo tegrastats`
- [ ] 检查磁盘空间: `df -h`

### 每周维护

- [ ] 清理 Docker 缓存: `docker system prune`
- [ ] 检查更新 (谨慎): `sudo apt-get update`
- [ ] 备份配置文件
- [ ] 测试所有功能

### 性能问题排查

- [ ] 检查 GPU 温度: `sudo jtop` (Temperature 标签)
- [ ] 检查功耗模式: `sudo nvpmodel -q`
- [ ] 检查频率锁定: `sudo jetson_clocks --show`
- [ ] 查看 GPU 利用率: `sudo tegrastats`

---

## 🎯 成功部署标准

### 必须满足

- ✅ 容器状态为 "Up"
- ✅ Gradio UI 可访问
- ✅ 图像检测功能正常
- ✅ 摄像头检测功能正常
- ✅ 检测时间 < 2 秒/帧
- ✅ 无错误日志

### 推荐达到

- ✅ 检测时间 < 1.5 秒/帧
- ✅ GPU 显存占用稳定
- ✅ 距离估计准确 (误差 < 0.5m)
- ✅ 深度图生成正常
- ✅ 容器运行 > 24 小时无崩溃

---

## 📞 快速命令参考

```bash
# 查看状态
docker ps
docker logs -f luminaire-detection

# 重启服务
docker restart luminaire-detection

# 性能监控
sudo jtop
sudo tegrastats

# 访问 UI
# http://192.168.10.135:7860
```

---

## 📚 文档参考

- **完整命令**: `JETSON_DEPLOY_COMMANDS.md`
- **快速参考**: `JETSON_QUICK_REFERENCE.md`
- **速查卡**: `JETSON_CHEATSHEET.txt`
- **Docker 指南**: `JETSON_DOCKER_GUIDE.md`

---

**部署日期**: ____________  
**部署人员**: ____________  
**检查人员**: ____________  
**验收状态**: [ ] 通过  [ ] 未通过  
**备注**: ____________________________
