# Luminaire Testing and Monocular Depth Distance

> 基于 **OWLv2 + DINOv3 + Depth Anything V2** 的室内灯具3D定位系统

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 🚀 核心特性

- **零样本检测**: OWLv2开放世界检测,无需训练
- **30+灯具类别**: 吊灯、吸顶灯、壁灯、台灯、射灯等
- **精确深度估计**: Depth Anything V2 + DINOv3双重保障
- **智能距离计算**: 根据灯具类型和位置自适应调整
- **实时处理**: 优化架构,支持摄像头实时检测

## 📋 技术栈

| 组件 | 模型 | 用途 |
|------|------|------|
| **检测器** | OWLv2-Large | 零样本目标检测 |
| **特征提取** | DINOv3-Large (304M) | 自监督视觉特征 |
| **深度估计** | Depth Anything V2 Large | 单目深度估计 |

## 🛠️ 快速开始

### 1. 安装依赖

```bash
# 使用pip安装
pip install -r requirements.txt

# 或使用uv (推荐,更快)
uv sync
```

### 2. 运行测试

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

### 3. 使用流水线

```python
from pipeline import LightLocalization3D

# 初始化流水线
pipeline = LightLocalization3D()

# 处理图像
import cv2
image = cv2.imread("test.jpg")
results = pipeline.process_image(image)

# 查看检测结果
for det in results['detections']:
    print(f"灯具: {det['label']}")
    print(f"置信度: {det['confidence']:.2%}")
    print(f"距离: {det['distance']:.2f}m")
```

## 📂 项目结构

```
.
├── pipeline.py              # 核心流水线 (检测+特征+深度)
├── realtime.py              # 实时检测 (摄像头/视频)
├── evaluate.py              # 模型评估脚本
├── pipeline_owlv2.py        # 向后兼容包装器
├── config.yaml              # 配置文件
├── config_multi_lights.py   # 多灯场景优化配置
├── requirements.txt         # Python依赖
├── data/                    # 数据目录
├── models/                  # 模型缓存
├── results/                 # 输出结果
├── docs/                    # 文档
└── utils/                   # 工具函数
```

## 🎯 使用场景

- **室内场景分析**: 自动识别和定位各类灯具
- **智能家居**: 灯具分布和控制优化
- **装修设计**: 照明方案评估
- **安防监控**: 异常光源检测
- **机器人导航**: 环境理解和定位

## 📊 性能指标

| 指标 | 值 |
|------|-----|
| **检测精度** | 90%+ (室内场景) |
| **处理速度** | 1-3 FPS (GPU) |
| **深度精度** | ±0.3m (2-5m距离) |
| **支持类别** | 30+ 种灯具 |

## 🔧 配置说明

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

## 📈 模型降级策略

系统内置智能降级,确保在不同环境下都能运行:

**检测模型**: OWLv2-Large → OWLv2-Base  
**特征模型**: DINOv3-Large → DINOv3-Base → DINOv3-Small  
**深度模型**: Depth Anything V2 Large → Base → Small → DINOv3特征方法

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request!

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
