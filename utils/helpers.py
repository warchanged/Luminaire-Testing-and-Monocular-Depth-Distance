"""
工具函数 - 常用功能封装
"""

import cv2
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import json
import yaml

def load_config(config_path="config.yaml"):
    """加载配置文件"""
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    return config

def save_json(data, filepath):
    """保存JSON文件"""
    filepath = Path(filepath)
    filepath.parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2)

def load_json(filepath):
    """加载JSON文件"""
    with open(filepath, 'r') as f:
        return json.load(f)

def visualize_detection_results(image, detections, save_path=None):
    """
    可视化检测结果
    
    Args:
        image: numpy array (H, W, 3)
        detections: list of dicts with 'bbox' and 'confidence'
        save_path: 保存路径
    """
    img_vis = image.copy()
    
    for det in detections:
        x1, y1, x2, y2 = [int(v) for v in det['bbox']]
        conf = det['confidence']
        
        # 绘制边界框
        cv2.rectangle(img_vis, (x1, y1), (x2, y2), (0, 255, 0), 2)
        
        # 显示置信度
        text = f"{conf:.2f}"
        cv2.putText(img_vis, text, (x1, y1-10),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
    
    if save_path:
        save_path = Path(save_path)
        save_path.parent.mkdir(parents=True, exist_ok=True)
        cv2.imwrite(str(save_path), cv2.cvtColor(img_vis, cv2.COLOR_RGB2BGR))
    
    return img_vis

def visualize_depth_map(depth_map, save_path=None, cmap='plasma'):
    """
    可视化深度图
    
    Args:
        depth_map: numpy array (H, W)
        save_path: 保存路径
        cmap: 颜色映射
    """
    plt.figure(figsize=(10, 8))
    plt.imshow(depth_map, cmap=cmap)
    plt.colorbar(label='Depth')
    plt.title('Depth Map')
    plt.axis('off')
    
    if save_path:
        save_path = Path(save_path)
        save_path.parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
    
    plt.close()

def compute_iou(box1, box2):
    """
    计算两个边界框的IoU
    
    Args:
        box1, box2: [x1, y1, x2, y2]
    
    Returns:
        iou: float
    """
    x1_1, y1_1, x2_1, y2_1 = box1
    x1_2, y1_2, x2_2, y2_2 = box2
    
    # 计算交集
    x1_i = max(x1_1, x1_2)
    y1_i = max(y1_1, y1_2)
    x2_i = min(x2_1, x2_2)
    y2_i = min(y2_1, y2_2)
    
    if x2_i < x1_i or y2_i < y1_i:
        return 0.0
    
    area_i = (x2_i - x1_i) * (y2_i - y1_i)
    
    # 计算并集
    area_1 = (x2_1 - x1_1) * (y2_1 - y1_1)
    area_2 = (x2_2 - x1_2) * (y2_2 - y1_2)
    area_u = area_1 + area_2 - area_i
    
    iou = area_i / area_u if area_u > 0 else 0.0
    
    return iou

def normalize_depth(depth_map):
    """归一化深度图到[0, 1]"""
    depth_min = depth_map.min()
    depth_max = depth_map.max()
    
    if depth_max - depth_min < 1e-8:
        return np.zeros_like(depth_map)
    
    depth_normalized = (depth_map - depth_min) / (depth_max - depth_min)
    return depth_normalized

def pixel_to_camera_coords(u, v, depth, fx, fy, cx, cy):
    """
    将像素坐标转换为相机坐标系3D坐标
    
    Args:
        u, v: 像素坐标
        depth: 深度值
        fx, fy: 焦距
        cx, cy: 主点
    
    Returns:
        x, y, z: 相机坐标系下的3D坐标
    """
    x = (u - cx) * depth / fx
    y = (v - cy) * depth / fy
    z = depth
    
    return x, y, z

def camera_to_pixel_coords(x, y, z, fx, fy, cx, cy):
    """
    将相机坐标系3D坐标转换为像素坐标
    
    Args:
        x, y, z: 相机坐标系下的3D坐标
        fx, fy: 焦距
        cx, cy: 主点
    
    Returns:
        u, v: 像素坐标
    """
    u = fx * x / z + cx
    v = fy * y / z + cy
    
    return u, v

def compute_depth_metrics(pred, gt, valid_mask=None):
    """
    计算深度估计指标
    
    Args:
        pred: 预测深度图
        gt: 真值深度图
        valid_mask: 有效像素掩码
    
    Returns:
        metrics: dict
    """
    if valid_mask is None:
        valid_mask = (gt > 0) & (gt < 10)
    
    pred_valid = pred[valid_mask]
    gt_valid = gt[valid_mask]
    
    # 归一化
    pred_norm = (pred_valid - pred_valid.min()) / (pred_valid.max() - pred_valid.min() + 1e-8)
    gt_norm = (gt_valid - gt_valid.min()) / (gt_valid.max() - gt_valid.min() + 1e-8)
    
    # 计算指标
    abs_diff = np.abs(pred_norm - gt_norm)
    
    metrics = {
        'mae': float(np.mean(abs_diff)),
        'rmse': float(np.sqrt(np.mean(abs_diff ** 2))),
        'abs_rel': float(np.mean(abs_diff / (gt_norm + 1e-8))),
    }
    
    # Delta准确率
    thresh = np.maximum((gt_norm / (pred_norm + 1e-8)),
                       (pred_norm / (gt_norm + 1e-8)))
    
    metrics['delta1'] = float(np.mean(thresh < 1.25))
    metrics['delta2'] = float(np.mean(thresh < 1.25 ** 2))
    metrics['delta3'] = float(np.mean(thresh < 1.25 ** 3))
    
    return metrics

def create_summary_report(results, save_path="results/summary_report.txt"):
    """
    创建总结报告
    
    Args:
        results: dict, 包含各种结果
        save_path: 保存路径
    """
    save_path = Path(save_path)
    save_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(save_path, 'w', encoding='utf-8') as f:
        f.write("="*60 + "\n")
        f.write("  灯具3D定位系统 - 性能评估报告\n")
        f.write("="*60 + "\n\n")
        
        # 检测性能
        if 'detection' in results:
            f.write("## 检测性能\n")
            f.write("-"*40 + "\n")
            det = results['detection']
            f.write(f"mAP@0.5:    {det.get('map50', 0):.4f}\n")
            f.write(f"Precision:  {det.get('precision', 0):.4f}\n")
            f.write(f"Recall:     {det.get('recall', 0):.4f}\n")
            f.write("\n")
        
        # 深度估计性能
        if 'depth' in results:
            f.write("## 深度估计性能\n")
            f.write("-"*40 + "\n")
            depth = results['depth']
            f.write(f"MAE:        {depth.get('mae', 0):.4f}\n")
            f.write(f"RMSE:       {depth.get('rmse', 0):.4f}\n")
            f.write(f"δ1 (< 1.25): {depth.get('delta1', 0):.4f}\n")
            f.write(f"δ2:         {depth.get('delta2', 0):.4f}\n")
            f.write(f"δ3:         {depth.get('delta3', 0):.4f}\n")
            f.write("\n")
        
        # 3D定位性能
        if 'localization' in results:
            f.write("## 3D定位性能\n")
            f.write("-"*40 + "\n")
            loc = results['localization']
            f.write(f"平均误差:   {loc.get('mean_error', 0):.4f} 米\n")
            f.write(f"Precision:  {loc.get('precision', 0):.4f}\n")
            f.write(f"Recall:     {loc.get('recall', 0):.4f}\n")
            f.write(f"F1 Score:   {loc.get('f1', 0):.4f}\n")
            f.write("\n")
        
        f.write("="*60 + "\n")
        f.write("报告生成完成\n")
    
    print(f"报告已保存到: {save_path}")

def check_system_requirements():
    """检查系统要求"""
    import torch
    import sys
    
    print("="*60)
    print("系统环境检查")
    print("="*60)
    
    # Python版本
    print(f"\nPython版本: {sys.version}")
    
    # PyTorch版本
    print(f"PyTorch版本: {torch.__version__}")
    
    # CUDA可用性
    cuda_available = torch.cuda.is_available()
    print(f"CUDA可用: {cuda_available}")
    
    if cuda_available:
        print(f"  设备数量: {torch.cuda.device_count()}")
        print(f"  当前设备: {torch.cuda.current_device()}")
        print(f"  设备名称: {torch.cuda.get_device_name(0)}")
        print(f"  显存容量: {torch.cuda.get_device_properties(0).total_memory / 1e9:.2f} GB")
    
    print("\n" + "="*60)

if __name__ == "__main__":
    # 测试工具函数
    print("测试工具函数...")
    
    # 测试IoU计算
    box1 = [100, 100, 200, 200]
    box2 = [150, 150, 250, 250]
    iou = compute_iou(box1, box2)
    print(f"IoU: {iou:.4f}")
    
    # 测试坐标转换
    x, y, z = pixel_to_camera_coords(320, 240, 2.0, 525, 525, 320, 240)
    print(f"3D坐标: ({x:.2f}, {y:.2f}, {z:.2f})")
    
    u, v = camera_to_pixel_coords(x, y, z, 525, 525, 320, 240)
    print(f"像素坐标: ({u:.2f}, {v:.2f})")
    
    # 检查系统
    check_system_requirements()
