"""
多灯场景检测测试
对比不同配置下的检测效果
"""

import cv2
import numpy as np
from pathlib import Path
from pipeline import LightLocalization3D
from config_multi_lights import get_optimized_config, PROMPT_STRATEGIES
import json
from tqdm import tqdm


def test_detection_configs(image_path, save_dir="results/multi_lights_test"):
    """
    测试不同配置的检测效果
    
    Args:
        image_path: 测试图像路径
        save_dir: 结果保存目录
    """
    save_dir = Path(save_dir)
    save_dir.mkdir(parents=True, exist_ok=True)
    
    # 读取图像
    image = cv2.imread(str(image_path))
    if image is None:
        print(f"❌ 无法读取图像: {image_path}")
        return
    
    print(f"测试图像: {image_path}")
    print(f"图像尺寸: {image.shape}")
    print("=" * 60)
    
    # 初始化检测器
    print("初始化DINO检测器...")
    detector = LightLocalization3D()
    
    # 测试配置
    test_configs = [
        {
            'name': '默认配置',
            'confidence': 0.25,
            'use_nms': True,
            'nms_threshold': 0.5
        },
        {
            'name': '降低阈值 (0.20)',
            'confidence': 0.20,
            'use_nms': True,
            'nms_threshold': 0.5
        },
        {
            'name': '进一步降低 (0.15)',
            'confidence': 0.15,
            'use_nms': True,
            'nms_threshold': 0.5
        },
        {
            'name': '激进模式 (0.12)',
            'confidence': 0.12,
            'use_nms': True,
            'nms_threshold': 0.45
        },
        {
            'name': '无NMS (0.15)',
            'confidence': 0.15,
            'use_nms': False,
            'nms_threshold': 0.5
        }
    ]
    
    results_summary = []
    
    # 测试每个配置
    for i, config in enumerate(test_configs):
        print(f"\n测试 {i+1}/{len(test_configs)}: {config['name']}")
        print(f"  置信度: {config['confidence']}")
        print(f"  NMS: {config['use_nms']} (阈值: {config['nms_threshold']})")
        
        # 执行检测
        detections = detector.detect_lights(
            image,
            confidence_threshold=config['confidence'],
            use_nms=config['use_nms'],
            nms_threshold=config['nms_threshold']
        )
        
        print(f"  检测到 {len(detections)} 个灯具")
        
        # 可视化
        vis_image = image.copy()
        for j, det in enumerate(detections):
            x1, y1, x2, y2 = [int(v) for v in det['bbox']]
            conf = det['confidence']
            
            # 绘制边界框
            cv2.rectangle(vis_image, (x1, y1), (x2, y2), (0, 255, 0), 2)
            
            # 绘制标签
            label = f"#{j+1} {conf:.2f}"
            cv2.putText(
                vis_image, label, (x1, y1-10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2
            )
        
        # 添加配置信息
        info_text = [
            f"Config: {config['name']}",
            f"Detected: {len(detections)} lights",
            f"Confidence: {config['confidence']}",
            f"NMS: {config['use_nms']}"
        ]
        
        y_offset = 30
        for text in info_text:
            cv2.putText(
                vis_image, text, (10, y_offset),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2
            )
            y_offset += 25
        
        # 保存结果
        output_path = save_dir / f"test_{i+1}_{config['name'].replace(' ', '_')}.jpg"
        cv2.imwrite(str(output_path), vis_image)
        print(f"  保存: {output_path}")
        
        # 记录结果
        results_summary.append({
            'config': config,
            'num_detections': len(detections),
            'detections': [
                {
                    'bbox': det['bbox'],
                    'confidence': float(det['confidence']),
                    'label': det['label']
                }
                for det in detections
            ]
        })
    
    # 保存JSON结果
    json_path = save_dir / "comparison_results.json"
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(results_summary, f, indent=2, ensure_ascii=False)
    
    print("\n" + "=" * 60)
    print("对比总结:")
    print("=" * 60)
    for i, result in enumerate(results_summary):
        print(f"{i+1}. {result['config']['name']:20s} -> {result['num_detections']:2d} 个灯具")
    
    print(f"\n详细结果已保存: {json_path}")
    print(f"可视化图像已保存: {save_dir}/")
    
    # 推荐配置
    best_config = max(results_summary, key=lambda x: x['num_detections'])
    print("\n" + "=" * 60)
    print("推荐配置 (检测数最多):")
    print("=" * 60)
    print(f"名称: {best_config['config']['name']}")
    print(f"检测数: {best_config['num_detections']} 个灯具")
    print(f"置信度阈值: {best_config['config']['confidence']}")
    print(f"使用NMS: {best_config['config']['use_nms']}")
    
    return results_summary


def batch_test(image_dir="data/yolo_dataset/images/val", num_samples=5):
    """
    批量测试多张图像
    
    Args:
        image_dir: 图像目录
        num_samples: 测试样本数
    """
    image_dir = Path(image_dir)
    image_files = sorted(image_dir.glob("*.jpg"))[:num_samples]
    
    if not image_files:
        print(f"❌ 未找到图像: {image_dir}")
        return
    
    print("=" * 60)
    print(f"批量测试: {len(image_files)} 张图像")
    print("=" * 60)
    
    # 初始化检测器
    detector = LightLocalization3D()
    
    # 测试配置
    configs = [
        ('默认', 0.25, True),
        ('优化', 0.15, True),
        ('激进', 0.12, True),
    ]
    
    results = {name: [] for name, _, _ in configs}
    
    for img_path in tqdm(image_files, desc="处理图像"):
        image = cv2.imread(str(img_path))
        if image is None:
            continue
        
        for name, conf, use_nms in configs:
            detections = detector.detect_lights(
                image,
                confidence_threshold=conf,
                use_nms=use_nms
            )
            results[name].append(len(detections))
    
    # 统计结果
    print("\n" + "=" * 60)
    print("批量测试结果:")
    print("=" * 60)
    
    for name, counts in results.items():
        avg = np.mean(counts)
        std = np.std(counts)
        total = sum(counts)
        print(f"{name:10s}: 平均 {avg:.1f}±{std:.1f} 个/图, 总计 {total} 个")
    
    # 提升比例
    baseline = results['默认']
    for name in ['优化', '激进']:
        improvement = (sum(results[name]) - sum(baseline)) / sum(baseline) * 100
        print(f"\n{name}配置 vs 默认: {improvement:+.1f}% 检测数提升")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="多灯场景检测测试")
    parser.add_argument('--image', type=str, 
                       default='data/yolo_dataset/images/val/val_00000.jpg',
                       help='测试图像路径')
    parser.add_argument('--batch', action='store_true',
                       help='批量测试模式')
    parser.add_argument('--samples', type=int, default=5,
                       help='批量测试样本数')
    
    args = parser.parse_args()
    
    if args.batch:
        batch_test(num_samples=args.samples)
    else:
        test_detection_configs(args.image)
