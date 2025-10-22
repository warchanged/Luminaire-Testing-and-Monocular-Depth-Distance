"""
OWLv2 + DINOv3 + Depth Anything V2 灯具3D定位流水线
已在Colab验证的最优技术栈

技术架构:
- OWLv2-Large: Google开放世界零样本检测 (主检测器)
- DINOv3-Large: Meta自监督视觉特征提取
- Depth Anything V2: 使用DINOv3骨干网络的精确深度估计

特点:
- 零样本检测,无需训练
- 30+室内灯具类别支持
- 智能距离估计(根据灯具类型)
- NMS后处理,去除重复检测
"""

import torch
import numpy as np
import cv2
from PIL import Image
from pathlib import Path
from transformers import (
    AutoModel,
    AutoImageProcessor,
    AutoProcessor,
    AutoModelForZeroShotObjectDetection,
    AutoModelForDepthEstimation,
    DPTImageProcessor
)
import time
from typing import List, Dict, Tuple, Optional


__all__ = ["LightLocalization3D"]


def main():
    """Run the canonical pipeline test (delegates to pipeline.main)."""
    # Import inside function to avoid top-level import side-effects when module is imported
    from pipeline import main as pipeline_main
    pipeline_main()


if __name__ == "__main__":
    main()
