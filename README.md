# Luminaire Testing and Monocular Depth Distance

> 基于 **OWLv2 + DINOv3 + Depth Anything V2** 的室内灯具3D定位系统  
> 支持 **Gradio Web UI** + **TensorRT加速** + **实时检测**

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![CUDA 12.1+](https://img.shields.io/badge/CUDA-12.1+-green.svg)](https://developer.nvidia.com/cuda-downloads)

## 📦 应用版本

| 版本 | 文件 | 用途 | 推荐环境 |
|------|------|------|---------|
| **Jetson 生产版** ⭐ | `gradio_app_jetson.py` | 精简优化,直连摄像头 | Jetson AGX Orin 64GB |
| **服务器开发版** | `gradio_app_optimized.py` | 功能完整,包含测试 | AWS/本地服务器 |

**快速部署**: 查看 [FILES_GUIDE.md](FILES_GUIDE.md) 了解文件说明和部署建议

---

## ✨ 最新更新 (2024-10-29)

### 🎉 Jetson 部署优化

- 🐳 **Docker 容器化**: 一键部署到 Jetson AGX Orin
- ⚡ **精简版应用**: `gradio_app_jetson.py` 专为生产环境优化
- 📹 **本地摄像头**: 直接使用 USB/CSI 摄像头,无需网络传输
- 🚀 **NMS 优化**: 使用 `torchvision.ops.nms` 提升检测速度
- 📚 **完整文档**: Jetson Docker 快速部署指南

### 🛠️ 代码优化 (2024-10-24)

- ⚡ **Gradio Web UI**: 可视化界面,支持图像上传和实时检测
- 🚀 **TensorRT加速**: 推理速度提升2-3倍,显存占用降低30-50%
- 🔄 **间隔采样检测**: 可调采样间隔(1-30秒),GPU负载降低90%+
- 🎨 **精美Web客户端**: `webcam_client.html` 本地摄像头实时检测
- 🔐 **DINOv3支持**: 完整配置HuggingFace访问权限

---

## 🚀 核心特性

- **零样本检测**: OWLv2开放世界检测,无需训练
- **33+灯具类别**: 吊灯、吸顶灯、壁灯、台灯、射灯等
- **精确深度估计**: Depth Anything V2 + DINOv3双重保障
- **智能距离计算**: 根据灯具类型和位置自适应调整
- **Web可视化界面**: Gradio UI,支持本地/远程访问
- **高性能推理**: TensorRT加速,FP16混合精度
- **灵活部署**: 支持本地、服务器、Docker等多种部署方式

## 📋 技术架构

| 组件 | 模型 | 用途 | 性能 |
|------|------|------|------|
| **检测器** | OWLv2-Large (1.1B) | 零样本目标检测 | 90%+ 精度 |
| **特征提取** | DINOv3-Large (304M) | 自监督视觉特征 | 2%精度提升 |
| **深度估计** | Depth Anything V2 Large (335M) | 单目深度估计 | ±0.3m精度 |
| **加速引擎** | TensorRT + CUDA | 推理优化 | 2-3x速度提升 |

## 🛠️ 快速开始

## 🛠️ 快速开始

### 方式1: Gradio Web UI (推荐)

**本地使用**:

```bash
# 安装依赖
pip install -r requirements.txt

# 启动Web界面
python gradio_app_optimized.py
```

访问: `http://localhost:7860`

**服务器部署**:

```bash
# SSH到服务器
ssh user@server

# 启动优化版Gradio
cd /path/to/project
chmod +x start_gradio_optimized.sh
./start_gradio_optimized.sh

# 本地通过SSH隧道访问
ssh -L 7860:localhost:7860 user@server
```

访问: `http://localhost:7860`

**Web客户端** (本地摄像头):

1. 双击打开 `webcam_client.html`
2. 输入服务器地址
3. 启动摄像头开始检测

### 方式2: Python脚本

```bash
# 基础检测测试
python pipeline.py

# 评估模型性能
python evaluate.py --samples 20

# 实时摄像头检测
python realtime.py --mode webcam

# 视频处理
python realtime.py --mode video --input video.mp4
```

### 方式3: 代码集成

```python
from pipeline import LightLocalization3D

# 初始化流水线
pipeline = LightLocalization3D(
    detection_model="google/owlv2-large-patch14-ensemble",
    feature_model="facebook/dinov2-large",
    depth_model="depth-anything/Depth-Anything-V2-Large-hf"
)

# 处理图像
import cv2
image = cv2.imread("test.jpg")
results = pipeline.process_image(
    image,
    confidence_threshold=0.15,
    compute_depth=True,
    compute_distance=True
)

# 查看检测结果
for det in results['detections']:
    print(f"灯具: {det['label']}")
    print(f"置信度: {det['confidence']:.2%}")
    print(f"位置: {det['box']}")
    if det.get('distance'):
        print(f"距离: {det['distance']:.2f}m")
```

## 📂 项目结构

```
.
├── gradio_app_optimized.py  # Gradio Web UI (优化版)
├── webcam_client.html       # 本地摄像头客户端
├── pipeline.py              # 核心流水线 (检测+特征+深度)
├── tensorrt_utils.py        # TensorRT加速工具
├── realtime.py              # 实时检测 (摄像头/视频)
├── evaluate.py              # 模型评估脚本
├── start_gradio_optimized.sh# Gradio启动脚本
├── start_ssh_tunnel.bat     # SSH隧道启动脚本 (Windows)
├── config.yaml              # 配置文件
├── requirements.txt         # Python依赖
├── DEPLOYMENT_GUIDE.md      # 完整部署指南
├── OPTIMIZATION_GUIDE.md    # 性能优化指南
├── data/                    # 数据目录
├── models/                  # 模型缓存
└── results/                 # 输出结果
```

## 🎯 使用场景

- **室内场景分析**: 自动识别和定位各类灯具
- **智能家居**: 灯具分布和控制优化
- **装修设计**: 照明方案评估
- **安防监控**: 异常光源检测
- **机器人导航**: 环境理解和定位
- **长期监控**: 间隔采样,24小时持续运行

## 📊 性能指标

### 检测性能

| 指标 | 值 |
|------|-----|
| **检测精度** | 90%+ (室内场景) |
| **处理速度** | 1 FPS (优化前) → 3 FPS (优化后) |
| **深度精度** | ±0.3m (2-5m距离) |
| **支持类别** | 33 种灯具 |

### 优化性能 (TensorRT)

| 优化 | 提升 |
|------|-----|
| **速度** | 2-3x 加速 |
| **显存** | 30-50% 降低 |
| **GPU负载** | 90%+ 降低 (间隔采样) |
| **持续运行** | 24小时+ 无OOM |

## 🔧 配置说明

### 基础配置

编辑 `config.yaml` 自定义参数:

```yaml
DETECTION:
  confidence_threshold: 0.15  # 检测阈值 (降低可检测更多灯具)
  use_nms: true               # NMS去重
  nms_threshold: 0.5          # NMS阈值

DEPTH:
  model_name: "depth-anything/Depth-Anything-V2-Large-hf"
  # 可选: Base (更快) 或 Small (最快)
```

### HuggingFace配置 (DINOv3访问)

```bash
# 登录HuggingFace
huggingface-cli login

# 或设置环境变量
export HF_TOKEN="your_token_here"

# 申请DINOv3访问权限
# 访问: https://huggingface.co/facebook/dinov3-vitl16-pretrain-lvd1689m
```

### TensorRT优化 (可选)

```bash
# 安装torch-tensorrt
pip install torch-tensorrt --extra-index-url https://download.pytorch.org/whl/cu121

# 系统会自动检测并启用TensorRT加速
```

## 📈 模型降级策略

系统内置智能降级,确保在不同环境下都能运行:

**检测模型**: OWLv2-Large → OWLv2-Base  
**特征模型**: DINOv3-Large → DINOv3-Base → DINOv3-Small → DINOv2-Large (备用)  
**深度模型**: Depth Anything V2 Large → Base → Small

## 📖 文档

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 🙏 致谢

- [OWLv2](https://github.com/google-research/scenic/tree/main/scenic/projects/owl_vit) - Google Research
- [DINOv3](https://github.com/facebookresearch/dinov2) - Meta AI Research
- [Depth Anything V2](https://github.com/DepthAnything/Depth-Anything-V2) - Depth Anything Team
- [Transformers](https://github.com/huggingface/transformers) - Hugging Face

## 📧 联系方式

项目链接: [https://github.com/warchanged/Luminaire-Testing-and-Monocular-Depth-Distance](https://github.com/warchanged/Luminaire-Testing-and-Monocular-Depth-Distance)

---

⭐ 如果这个项目对你有帮助,请给个 Star!
