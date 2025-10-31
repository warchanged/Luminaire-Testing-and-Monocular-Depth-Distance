# 🗂️ 项目文件说明

## 📦 生产环境文件 (Jetson 部署)

### 核心应用

- **`gradio_app_jetson.py`** ⭐ - Jetson 优化版 Gradio 应用
  - 精简代码,移除测试功能
  - 直接使用本地摄像头 (USB/CSI)
  - 专注于生产环境部署
  - **推荐在 Jetson 上使用**

- **`pipeline.py`** - 核心检测流水线
  - OWLv2 + DINOv3 + Depth Anything V2
  - 已优化 NMS (使用 torchvision.ops.nms)
  - TensorRT 加速支持

### Docker 部署

- **`Dockerfile.jetson`** - Jetson Docker 镜像定义
- **`docker-compose.jetson.yml`** - Docker Compose 配置
- **`deploy_jetson.sh`** - 自动化部署脚本
- **`.dockerignore`** - 构建优化

### 配置文件

- **`config.yaml`** - 基础配置
- **`requirements.txt`** - Python 依赖

### 文档

- **`README.md`** - 项目总文档
- **`JETSON_DOCKER_GUIDE.md`** - Jetson Docker 快速部署指南
- **`DEPLOYMENT_GUIDE.md`** - 完整部署指南

---

## 🧪 测试和开发文件 (可选)

### 原始开发版本

- **`gradio_app_optimized.py`** - AWS 服务器版本 (功能完整,包含所有测试功能)
- **`gradio_app.py`** - 早期版本

### 测试脚本

- **`test_quick.py`** - 快速功能测试
- **`test_threshold_fine.py`** - 阈值微调测试
- **`test_multi_lights.py`** - 多灯具场景测试
- **`evaluate.py`** - 性能评估

### 实用工具

- **`realtime.py`** - 命令行实时检测工具
- **`pipeline_owlv2.py`** - OWLv2 独立测试
- **`tensorrt_utils.py`** - TensorRT 优化工具
- **`run_all.py`** - 批量测试脚本

### 初始化脚本

- **`step1_download_data.py`** - 下载测试数据
- **`step4_setup_depth_anything.py`** - 深度模型设置

### Web 客户端 (高级用户)

- **`webcam_client.html`** - 独立网页摄像头客户端
- **`webcam_test_simple.html`** - 简化测试版本

---

## 🚀 Jetson 部署推荐

### 最小部署 (仅生产环境)

传输以下文件到 Jetson:

```bash
# 核心应用
gradio_app_jetson.py          # ⭐ Jetson 优化版
pipeline.py                     # 检测流水线

# Docker 部署
Dockerfile.jetson
docker-compose.jetson.yml
deploy_jetson.sh
.dockerignore

# 配置
config.yaml
requirements.txt

# 文档 (可选)
JETSON_DOCKER_GUIDE.md
```

### 使用 SCP 传输 (Windows → Jetson)

```powershell
# 创建临时目录
New-Item -Path "c:\Users\19395\Desktop\jetson_deploy" -ItemType Directory -Force

# 复制生产文件
Copy-Item "c:\Users\19395\Desktop\test\gradio_app_jetson.py" "c:\Users\19395\Desktop\jetson_deploy\"
Copy-Item "c:\Users\19395\Desktop\test\pipeline.py" "c:\Users\19395\Desktop\jetson_deploy\"
Copy-Item "c:\Users\19395\Desktop\test\Dockerfile.jetson" "c:\Users\19395\Desktop\jetson_deploy\"
Copy-Item "c:\Users\19395\Desktop\test\docker-compose.jetson.yml" "c:\Users\19395\Desktop\jetson_deploy\"
Copy-Item "c:\Users\19395\Desktop\test\deploy_jetson.sh" "c:\Users\19395\Desktop\jetson_deploy\"
Copy-Item "c:\Users\19395\Desktop\test\.dockerignore" "c:\Users\19395\Desktop\jetson_deploy\"
Copy-Item "c:\Users\19395\Desktop\test\config.yaml" "c:\Users\19395\Desktop\jetson_deploy\"
Copy-Item "c:\Users\19395\Desktop\test\requirements.txt" "c:\Users\19395\Desktop\jetson_deploy\"
Copy-Item "c:\Users\19395\Desktop\test\JETSON_DOCKER_GUIDE.md" "c:\Users\19395\Desktop\jetson_deploy\"

# 传输到 Jetson
scp -r c:\Users\19395\Desktop\jetson_deploy\* haoyu@192.168.10.135:~/luminaire-detection/
```

---

## 📋 文件对比

| 文件 | 用途 | 推荐环境 | 大小 |
|------|------|---------|------|
| `gradio_app_jetson.py` | Jetson 优化版 | Jetson 生产 | ~10KB |
| `gradio_app_optimized.py` | AWS 完整版 | 服务器开发 | ~20KB |
| `gradio_app.py` | 早期版本 | 已废弃 | ~15KB |

---

## 🗑️ 可删除的测试文件 (Jetson 上)

如果磁盘空间紧张,可以删除:

```bash
# 在 Jetson 上执行
cd ~/luminaire-detection

# 删除测试文件
rm -f test_*.py
rm -f step*.py
rm -f evaluate.py
rm -f run_all.py
rm -f realtime.py
rm -f pipeline_owlv2.py
rm -f tensorrt_utils.py
rm -f webcam_*.html
rm -f gradio_app.py
rm -f gradio_app_optimized.py  # 保留 gradio_app_jetson.py

# 删除测试数据
rm -rf data/
rm -rf docs/
rm -rf custom_images/
```

**保留的核心文件**:

- `gradio_app_jetson.py` (应用)
- `pipeline.py` (流水线)
- `config.yaml` (配置)
- `requirements.txt` (依赖)
- Docker 相关文件

---

## ✅ 总结

- **Jetson 生产环境**: 使用 `gradio_app_jetson.py`
- **AWS 服务器开发**: 使用 `gradio_app_optimized.py`
- **测试文件**: 仅用于开发调试,生产环境可删除
- **Docker 部署**: 已配置为使用 `gradio_app_jetson.py`
