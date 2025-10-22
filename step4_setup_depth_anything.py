"""
步骤4: 设置Depth Anything深度估计模型
部署零样本单目深度估计(MMDE)模型
"""

import torch
import cv2
import numpy as np
from pathlib import Path
from transformers import AutoImageProcessor, AutoModelForDepthEstimation
from PIL import Image
import matplotlib.pyplot as plt

class DepthAnythingModel:
    """Depth Anything深度估计模型封装"""
    
    def __init__(self, model_name="LiheYoung/depth-anything-small-hf", device=None):
        """
        初始化Depth Anything模型
        
        Args:
            model_name: 模型名称,可选:
                - "LiheYoung/depth-anything-small-hf" (小模型,快速)
                - "LiheYoung/depth-anything-base-hf" (基础模型)
                - "LiheYoung/depth-anything-large-hf" (大模型,高精度)
            device: 设备 (cuda/cpu)
        """
        if device is None:
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        else:
            self.device = torch.device(device)
        
        print(f"使用设备: {self.device}")
        print(f"加载模型: {model_name}")
        
        # 加载图像处理器和模型
        self.image_processor = AutoImageProcessor.from_pretrained(model_name)
        self.model = AutoModelForDepthEstimation.from_pretrained(model_name)
        self.model.to(self.device)
        self.model.eval()
        
        print("模型加载完成!")
    
    def estimate_depth(self, image):
        """
        估计单张图像的深度
        
        Args:
            image: numpy数组 (H, W, 3) RGB格式 或 PIL Image
        
        Returns:
            depth_map: numpy数组 (H, W) 深度图
        """
        # 转换为PIL Image
        if isinstance(image, np.ndarray):
            if image.dtype != np.uint8:
                image = (image * 255).astype(np.uint8)
            pil_image = Image.fromarray(image)
        else:
            pil_image = image
        
        # 预处理
        inputs = self.image_processor(images=pil_image, return_tensors="pt")
        inputs = {k: v.to(self.device) for k, v in inputs.items()}
        
        # 推理
        with torch.no_grad():
            outputs = self.model(**inputs)
            predicted_depth = outputs.predicted_depth
        
        # 插值到原始图像大小
        prediction = torch.nn.functional.interpolate(
            predicted_depth.unsqueeze(1),
            size=pil_image.size[::-1],
            mode="bicubic",
            align_corners=False,
        )
        
        # 转换为numpy数组
        depth_map = prediction.squeeze().cpu().numpy()
        
        return depth_map
    
    def visualize_depth(self, image, depth_map, save_path=None):
        """可视化深度图"""
        fig, axes = plt.subplots(1, 2, figsize=(12, 5))
        
        # 原始图像
        if isinstance(image, np.ndarray):
            axes[0].imshow(image)
        else:
            axes[0].imshow(np.array(image))
        axes[0].set_title("Original Image")
        axes[0].axis('off')
        
        # 深度图
        im = axes[1].imshow(depth_map, cmap='plasma')
        axes[1].set_title("Depth Map")
        axes[1].axis('off')
        plt.colorbar(im, ax=axes[1], fraction=0.046, pad=0.04)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
            print(f"可视化结果已保存到: {save_path}")
        
        plt.close()
        
        return fig

def test_depth_model():
    """测试深度估计模型"""
    print("="*50)
    print("测试Depth Anything模型")
    print("="*50)
    
    # 初始化模型
    depth_model = DepthAnythingModel(
        model_name="LiheYoung/depth-anything-small-hf"  # 使用小模型
    )
    
    # 查找测试图像
    test_images = list(Path("data/yolo_dataset/images/val").glob("*.jpg"))
    
    if not test_images:
        print("未找到测试图像,创建示例图像...")
        # 创建一个简单的测试图像
        test_img = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
        test_path = Path("results/test_image.jpg")
        test_path.parent.mkdir(exist_ok=True)
        cv2.imwrite(str(test_path), cv2.cvtColor(test_img, cv2.COLOR_RGB2BGR))
        test_images = [test_path]
    
    # 测试前3张图像
    results_dir = Path("results/depth_estimation")
    results_dir.mkdir(parents=True, exist_ok=True)
    
    for i, img_path in enumerate(test_images[:3]):
        print(f"\n处理图像 {i+1}: {img_path.name}")
        
        # 读取图像
        image = cv2.imread(str(img_path))
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # 估计深度
        depth_map = depth_model.estimate_depth(image)
        
        print(f"  深度范围: [{depth_map.min():.2f}, {depth_map.max():.2f}]")
        print(f"  深度图形状: {depth_map.shape}")
        
        # 可视化
        save_path = results_dir / f"depth_{img_path.stem}.png"
        depth_model.visualize_depth(image, depth_map, save_path)
        
        # 保存深度图为numpy文件
        np.save(results_dir / f"depth_{img_path.stem}.npy", depth_map)
    
    print(f"\n深度估计结果已保存到: {results_dir.absolute()}")
    
    return depth_model

def save_model_wrapper(depth_model, save_path="models/depth_anything_wrapper.pth"):
    """保存模型配置(实际模型会自动缓存)"""
    config = {
        'model_name': 'LiheYoung/depth-anything-small-hf',
        'device': str(depth_model.device)
    }
    
    save_path = Path(save_path)
    save_path.parent.mkdir(parents=True, exist_ok=True)
    
    torch.save(config, save_path)
    print(f"\n模型配置已保存到: {save_path.absolute()}")

def main():
    try:
        # 测试深度估计模型
        depth_model = test_depth_model()
        
        # 保存模型配置
        save_model_wrapper(depth_model)
        
        print("\n" + "="*50)
        print("✓ 步骤4完成!")
        print("="*50)
        print("Depth Anything模型已准备就绪")
        print("\n下一步: 运行 step5_integrate_pipeline.py 整合检测和深度估计")
        
    except Exception as e:
        print(f"\n✗ 错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
