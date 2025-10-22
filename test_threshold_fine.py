"""
精细阈值测试工具 - 测试特定阈值范围的检测效果
"""
import argparse
from pathlib import Path
import cv2
import numpy as np
from pipeline import LightLocalization3D
import time

def test_threshold(image_path, threshold, use_nms=True):
    """测试单个阈值的检测效果"""
    detector = LightLocalization3D()
    
    # 读取图像
    image = cv2.imread(str(image_path))
    if image is None:
        raise ValueError(f"无法读取图像: {image_path}")
    
    # 执行检测
    start_time = time.time()
    results = detector.localize_3d(
        image,
        confidence_threshold=threshold,
        use_nms=use_nms
    )
    elapsed = time.time() - start_time
    
    # 统计结果 - results是一个list,每个元素包含bbox_2d, position_3d, confidence, label
    num_detections = len(results)
    confidences = [r['confidence'] for r in results]
    boxes = [r['bbox_2d'] for r in results]
    
    return {
        'threshold': threshold,
        'num_detections': num_detections,
        'confidences': confidences,
        'boxes': boxes,
        'elapsed': elapsed,
        'results': results
    }

def visualize_results(image_path, result, output_path=None):
    """可视化检测结果"""
    image = cv2.imread(str(image_path))
    
    boxes = result['boxes']
    confidences = result['confidences']
    
    # 绘制检测框
    for box, conf in zip(boxes, confidences):
        x1, y1, x2, y2 = box
        color = (0, 255, 0) if conf >= 0.2 else (0, 165, 255)  # 绿色高置信度,橙色低置信度
        
        cv2.rectangle(image, (int(x1), int(y1)), (int(x2), int(y2)), color, 2)
        
        # 添加置信度标签
        label = f"{conf:.2f}"
        cv2.putText(image, label, (int(x1), int(y1)-5), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
    
    # 添加标题
    title = f"Threshold: {result['threshold']:.2f} | Detections: {result['num_detections']}"
    cv2.putText(image, title, (10, 30), 
               cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    
    if output_path:
        cv2.imwrite(str(output_path), image)
    
    return image

def batch_test_thresholds(image_paths, thresholds, use_nms=True):
    """批量测试多个阈值"""
    results = []
    
    for threshold in thresholds:
        print(f"\n{'='*60}")
        print(f"测试阈值: {threshold:.2f}")
        print(f"{'='*60}")
        
        threshold_results = []
        total_detections = 0
        total_time = 0
        
        for img_path in image_paths:
            print(f"  处理: {img_path.name}...", end=" ")
            result = test_threshold(img_path, threshold, use_nms)
            threshold_results.append(result)
            total_detections += result['num_detections']
            total_time += result['elapsed']
            print(f"{result['num_detections']} 个检测")
        
        avg_detections = total_detections / len(image_paths)
        avg_time = total_time / len(image_paths)
        
        # 统计置信度分布
        all_confidences = []
        for r in threshold_results:
            all_confidences.extend(r['confidences'])
        
        if all_confidences:
            min_conf = min(all_confidences)
            max_conf = max(all_confidences)
            avg_conf = np.mean(all_confidences)
            std_conf = np.std(all_confidences)
        else:
            min_conf = max_conf = avg_conf = std_conf = 0
        
        summary = {
            'threshold': threshold,
            'total_detections': total_detections,
            'avg_detections': avg_detections,
            'avg_time': avg_time,
            'min_confidence': min_conf,
            'max_confidence': max_conf,
            'avg_confidence': avg_conf,
            'std_confidence': std_conf,
            'results': threshold_results
        }
        results.append(summary)
        
        print(f"\n  总计: {total_detections} 个检测")
        print(f"  平均: {avg_detections:.1f} 个/图")
        print(f"  置信度: {avg_conf:.3f} ± {std_conf:.3f} (范围: {min_conf:.3f}-{max_conf:.3f})")
        print(f"  处理时间: {avg_time:.2f}s/图")
    
    return results

def print_comparison(results):
    """打印对比结果"""
    print(f"\n{'='*80}")
    print("阈值对比总结")
    print(f"{'='*80}")
    print(f"{'阈值':<10} {'总检测数':<12} {'平均/图':<12} {'平均置信度':<15} {'置信度标准差':<15}")
    print(f"{'-'*80}")
    
    for r in results:
        print(f"{r['threshold']:.2f}      "
              f"{r['total_detections']:<12} "
              f"{r['avg_detections']:<12.1f} "
              f"{r['avg_confidence']:<15.3f} "
              f"{r['std_confidence']:<15.3f}")
    
    # 计算相对变化
    print(f"\n{'='*80}")
    print("相对变化 (相对于最低阈值)")
    print(f"{'='*80}")
    
    base = results[0]
    for r in results[1:]:
        detection_change = ((r['total_detections'] - base['total_detections']) / 
                          base['total_detections'] * 100) if base['total_detections'] > 0 else 0
        conf_change = r['avg_confidence'] - base['avg_confidence']
        
        print(f"阈值 {r['threshold']:.2f} vs {base['threshold']:.2f}:")
        print(f"  检测数变化: {detection_change:+.1f}%")
        print(f"  平均置信度变化: {conf_change:+.3f}")
        print()

def main():
    parser = argparse.ArgumentParser(description="精细阈值测试工具")
    parser.add_argument("--image", type=str, help="单张测试图像路径")
    parser.add_argument("--batch", action="store_true", help="批量测试模式")
    parser.add_argument("--samples", type=int, default=10, help="批量测试时的样本数量")
    parser.add_argument("--thresholds", type=float, nargs="+", 
                       default=[0.12, 0.13, 0.14, 0.15],
                       help="要测试的阈值列表 (默认: 0.12 0.13 0.14 0.15)")
    parser.add_argument("--no-nms", action="store_true", help="禁用NMS")
    parser.add_argument("--output-dir", type=str, default="results/threshold_test",
                       help="可视化结果输出目录")
    
    args = parser.parse_args()
    
    use_nms = not args.no_nms
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"{'='*80}")
    print("精细阈值测试")
    print(f"{'='*80}")
    print(f"测试阈值: {args.thresholds}")
    print(f"使用NMS: {use_nms}")
    print()
    
    if args.image:
        # 单图像测试
        image_path = Path(args.image)
        print(f"测试图像: {image_path}\n")
        
        results = []
        for threshold in args.thresholds:
            result = test_threshold(image_path, threshold, use_nms)
            results.append(result)
            
            # 保存可视化
            output_path = output_dir / f"thresh_{threshold:.2f}_{image_path.name}"
            visualize_results(image_path, result, output_path)
            
            print(f"阈值 {threshold:.2f}: {result['num_detections']} 个检测, "
                  f"平均置信度: {np.mean(result['confidences']) if result['confidences'] else 0:.3f}")
        
        print(f"\n可视化结果已保存到: {output_dir}")
        
    elif args.batch:
        # 批量测试
        test_dir = Path("data/nyu_data/data/nyu2_test")
        if not test_dir.exists():
            print(f"错误: 测试目录不存在: {test_dir}")
            return
        
        image_files = sorted(list(test_dir.glob("*.jpg")) + list(test_dir.glob("*.png")))
        if not image_files:
            print(f"错误: 在 {test_dir} 中未找到图像")
            return
        
        image_files = image_files[:args.samples]
        print(f"找到 {len(image_files)} 张测试图像\n")
        
        results = batch_test_thresholds(image_files, args.thresholds, use_nms)
        print_comparison(results)
        
    else:
        print("错误: 请指定 --image 或 --batch 模式")
        parser.print_help()

if __name__ == "__main__":
    main()
