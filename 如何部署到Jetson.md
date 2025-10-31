# 🚀 如何将项目部署到Jetson（通过网线连接）

## 📚 文档导航

根据你的需求选择合适的文档：

### 🎯 推荐阅读顺序

1. **[网线部署到Jetson-快速指南.md](网线部署到Jetson-快速指南.md)** ⭐
   - 最简洁的3步部署指南
   - 适合快速开始
   - 预计时间：30-40分钟

2. **[DEPLOY_TO_JETSON_GUIDE.md](DEPLOY_TO_JETSON_GUIDE.md)** 📖
   - 完整详细的部署文档
   - 包含所有可能遇到的问题和解决方案
   - 适合深入了解

3. **[命令速查表.txt](命令速查表.txt)** 📝
   - 所有常用命令集合
   - 方便快速查询
   - 建议打印或保存

### 📑 其他相关文档

- **[QUICK_START_JETSON.md](QUICK_START_JETSON.md)** - 快速开始指南
- **[JETSON_DOCKER_GUIDE.md](JETSON_DOCKER_GUIDE.md)** - Docker部署详细说明
- **[DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)** - 通用部署指南（服务器/Jetson）

---

## ⚡ 超快速开始（TL;DR）

### 1️⃣ 在Windows电脑上

```powershell
cd c:\Users\670358474\Downloads\Luminaire-Testing-and-Monocular-Depth-Distance
.\deploy_prepare.ps1
# 输入Jetson的IP和用户名，然后选择Y传输
```

### 2️⃣ SSH到Jetson

```powershell
ssh <用户名>@<IP地址>
```

### 3️⃣ 在Jetson上

```bash
cd ~/luminaire-detection
chmod +x deploy_jetson.sh
./deploy_jetson.sh
# 选择：3) 构建并启动
```

### 4️⃣ 访问应用

浏览器打开：`http://<Jetson IP>:7860`

---

## 🛠️ 辅助工具

### Windows端工具

1. **网络测试脚本**
   ```powershell
   .\test_jetson_connection.ps1 -JetsonIP <IP地址>
   ```
   - 测试网络连接
   - 检查SSH端口
   - 检查Gradio端口

2. **部署准备脚本**
   ```powershell
   .\deploy_prepare.ps1
   ```
   - 自动准备所有部署文件
   - 自动传输到Jetson
   - 提供详细的后续步骤说明

### Jetson端工具

1. **环境检查脚本**
   ```bash
   chmod +x check_jetson_env.sh
   ./check_jetson_env.sh
   ```
   - 检查系统环境
   - 验证Docker安装
   - 检查GPU状态
   - 测试网络连接

2. **部署脚本**
   ```bash
   ./deploy_jetson.sh
   ```
   - 一键构建和启动
   - 查看日志
   - 管理容器

---

## 📋 部署前检查清单

在开始部署前，确保：

- [ ] Windows电脑和Jetson通过网线连接
- [ ] 可以ping通Jetson的IP地址
- [ ] 知道Jetson的用户名和密码
- [ ] Jetson有至少20GB可用磁盘空间
- [ ] Jetson已安装JetPack 5.x
- [ ] Jetson可以访问互联网（用于下载模型）

---

## 🎯 部署流程图

```
┌─────────────────────────────────────────────────────────────┐
│                    Windows 电脑                              │
│                                                              │
│  1. 运行 deploy_prepare.ps1                                 │
│     ├─ 输入 Jetson IP                                       │
│     ├─ 输入 Jetson 用户名                                   │
│     └─ 自动传输文件                                         │
│                                                              │
│  2. SSH 连接到 Jetson                                       │
│     ssh <用户名>@<IP>                                       │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────┐
│                    Jetson 设备                               │
│                                                              │
│  3. 检查环境（可选）                                         │
│     ./check_jetson_env.sh                                   │
│                                                              │
│  4. 运行部署脚本                                             │
│     ./deploy_jetson.sh                                      │
│     选择：3) 构建并启动                                      │
│                                                              │
│  5. 等待构建完成 (10-30分钟)                                │
│     docker logs -f luminaire-detection                      │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────┐
│                部署完成 ✅                                   │
│                                                              │
│  访问：http://<Jetson IP>:7860                              │
│                                                              │
│  功能：                                                      │
│  - 📸 图像检测                                              │
│  - 🎥 实时检测                                              │
│  - 📊 3D距离估计                                            │
└─────────────────────────────────────────────────────────────┘
```

---

## ❓ 常见问题

### Q: 无法连接到Jetson怎么办？

**A:** 运行网络测试脚本：
```powershell
.\test_jetson_connection.ps1 -JetsonIP <IP地址>
```

### Q: 文件传输很慢怎么办？

**A:** 
- 检查网线质量
- 确保使用千兆网线
- 尝试使用WinSCP图形界面工具

### Q: Docker构建失败怎么办？

**A:** 查看详细错误信息：
```bash
docker logs luminaire-detection
```
参考 [DEPLOY_TO_JETSON_GUIDE.md](DEPLOY_TO_JETSON_GUIDE.md) 的故障排除章节

### Q: 应用运行后无法访问Web界面？

**A:** 
1. 检查容器是否运行：`docker ps`
2. 检查端口是否监听：`sudo netstat -tulnp | grep 7860`
3. 检查防火墙：`sudo ufw status`

---

## 📞 获取帮助

如果遇到本文档未涵盖的问题：

1. 查看 [DEPLOY_TO_JETSON_GUIDE.md](DEPLOY_TO_JETSON_GUIDE.md) 的详细故障排除章节
2. 查看 [命令速查表.txt](命令速查表.txt) 寻找相关命令
3. 查看容器日志：`docker logs luminaire-detection`
4. 在GitHub提交Issue

---

## 📊 预期性能

### Jetson AGX Orin 64GB

| 指标 | 值 |
|------|---|
| 推理速度 | 0.5-1.5秒/帧 |
| 实时FPS | 1-2 FPS |
| 显存占用 | 8-12 GB |
| 功耗 | 30-50W（MAXN模式）|

---

## 🎉 部署成功标志

当你看到以下现象时，说明部署成功：

✅ 容器状态显示为 `Up`（`docker ps`）  
✅ 日志显示 `Running on local URL: http://0.0.0.0:7860`  
✅ 浏览器可以访问 `http://<Jetson IP>:7860`  
✅ 可以上传图片进行检测  
✅ GPU被正确使用（`nvidia-smi` 显示进程）

---

## 📝 更新日志

- 2025-10-31: 创建网线部署完整文档
- 添加网络测试工具
- 添加环境检查脚本
- 添加中文命令速查表

---

**祝你部署顺利！** 🚀

如有问题，欢迎查阅详细文档或提交Issue。
