# 🚀 网线部署到Jetson - 快速指南（3步完成）

## ⚡ 快速开始

### 第1步：在Windows电脑上准备文件（3分钟）

```powershell
# 进入项目目录
cd c:\Users\670358474\Downloads\Luminaire-Testing-and-Monocular-Depth-Distance

# 运行部署准备脚本
.\deploy_prepare.ps1
```

**按提示输入：**
- Jetson的IP地址（例如：`192.168.1.100`）
- Jetson的用户名（例如：`nvidia`）

**选择传输方式：**
- 提示 `Transfer files to Jetson via SCP now? (Y/N):` 时输入 `Y`

---

### 第2步：SSH连接到Jetson（1分钟）

```powershell
ssh <用户名>@<IP地址>
# 例如: ssh nvidia@192.168.1.100
```

输入Jetson的密码

---

### 第3步：在Jetson上部署（20-30分钟首次）

```bash
# 进入项目目录
cd ~/luminaire-detection

# 运行部署脚本
chmod +x deploy_jetson.sh
./deploy_jetson.sh

# 选择: 3) 构建并启动
```

---

## ✅ 验证部署成功

### 1. 查看日志
```bash
docker logs -f luminaire-detection
```

看到 `Running on local URL: http://0.0.0.0:7860` 表示成功！

### 2. 访问Web界面

在Windows浏览器中打开：
```
http://<Jetson IP地址>:7860
```

例如：`http://192.168.1.100:7860`

---

## 🔧 常用命令

```bash
# 查看容器状态
docker ps

# 重启容器
docker restart luminaire-detection

# 停止容器
docker stop luminaire-detection

# 查看GPU使用
nvidia-smi
```

---

## ❓ 遇到问题？

### 无法连接Jetson
```powershell
# 测试网络连接
ping <Jetson IP地址>
```

### SSH连接被拒绝
```bash
# 在Jetson上启动SSH服务
sudo systemctl start ssh
```

### Docker构建失败
```bash
# 检查Docker状态
sudo systemctl status docker

# 重启Docker
sudo systemctl restart docker
```

---

## 📖 详细文档

完整部署指南：[DEPLOY_TO_JETSON_GUIDE.md](DEPLOY_TO_JETSON_GUIDE.md)

---

**预计总时间：**
- 首次部署：30-40分钟
- 后续更新：5-10分钟
