"""
模型评估 - OWLv2 + DINOv3 + Depth Anything V2
评估新架构在测试集上的性能
"""

import cv2
import numpy as np
from pathlib import Path
import pandas as pd
from tqdm import tqdm
import matplotlib.pyplot as plt
from matplotlib import rcParams
import json

from pipeline import LightLocalization3D

# 设置中文字体
rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei']
rcParams['axes.unicode_minus'] = False


class LightDetectionEvaluator:
    """OWLv2灯具检测评估器"""
    
    def __init__(self, 
                 data_dir="data/nyu_data/data",
                 detection_model="google/owlv2-large-patch14-ensemble",
                 feature_model="facebook/dinov3-vitl16-pretrain-lvd1689m",
                 depth_model="depth-anything/Depth-Anything-V2-Large-hf",
                 use_int8=False):
        """
        初始化评估器
        
        Args:
            data_dir: 数据目录
            detection_model: OWLv2检测模型
            feature_model: DINOv3特征模型
            depth_model: Depth Anything V2深度模型
            use_int8: 是否使用INT8量化
        """
        self.data_dir = Path(data_dir)
        
        # 初始化流水线 (OWLv2架构)
        print("初始化 OWLv2 + DINOv3 + Depth Anything V2 流水线...")
        self.pipeline = LightLocalization3D(
            detection_model=detection_model,
            feature_model=feature_model,
            depth_model=depth_model
        )
        
        if torch.cuda.is_available():
            from tensorrt_utils import enable_tensorrt_optimization
            self.pipeline.detection_model = enable_tensorrt_optimization(
                self.pipeline.detection_model, use_int8=use_int8
            )

        print("✓ 评估器初始化完成")
    
    def evaluate(self, 
                 max_samples=50,
                 confidence_threshold=0.25,
                 output_dir="results/dino_evaluation"):
        """
        评估DINO性能
        
        Args:
            max_samples: 最大测试样本数
            confidence_threshold: 检测置信度阈值
            output_dir: 输出目录
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(exist_ok=True, parents=True)
        
        print("\n" + "="*60)
        print("DINO检测评估")
        print("="*60)
        
        # 读取测试集
        test_csv = self.data_dir / "nyu2_test.csv"
        if not test_csv.exists():
            print(f"✗ 测试集CSV不存在: {test_csv}")
            return None
        
        df = pd.read_csv(test_csv, names=["rgb", "depth"])
        
        # 限制样本数
        test_samples = df.head(max_samples)
        print(f"\n测试样本数: {len(test_samples)}")
        
        # 评估结果
        results = []
        inference_times = []
        
        # 处理每个样本
        print("\n开始评估...")
        for idx, row in tqdm(list(test_samples.iterrows()), desc="评估进度"):
            rgb_rel_path = row['rgb'].replace("data/", "", 1)
            img_path = self.data_dir / rgb_rel_path
            
            if not img_path.exists():
                continue
            
            img = cv2.imread(str(img_path))
            if img is None:
                continue
            
            # 执行3D定位
            import time
            start_time = time.time()
            detections_3d = self.pipeline.localize_3d(
                img,
                confidence_threshold=confidence_threshold
            )
            inference_time = time.time() - start_time
            
            inference_times.append(inference_time)
            
            # 记录结果
            results.append({
                'image_idx': idx,
                'image_path': str(img_path),
                'num_detections': len(detections_3d),
                'inference_time': inference_time,
                'detections': detections_3d
            })
            
            # 保存可视化 (前10张)
            if idx < 10:
                vis_img = self.pipeline.visualize(
                    img,
                    detections_3d,
                    output_path=output_dir / f"result_{idx:03d}.jpg"
                )
        
        # 计算统计
        stats = self._compute_statistics(results, inference_times)
        
        # 保存结果
        self._save_results(results, stats, output_dir)
        
        # 打印报告
        self._print_report(stats)
        
        # 生成图表
        self._generate_plots(results, stats, output_dir)
        
        return stats
    
    def _compute_statistics(self, results, inference_times):
        """计算统计数据"""
        total_samples = len(results)
        total_detections = sum(r['num_detections'] for r in results)
        samples_with_detections = sum(1 for r in results if r['num_detections'] > 0)
        
        # 检测数分布
        detection_counts = [r['num_detections'] for r in results]
        
        # 置信度分布
        all_confidences = []
        for r in results:
            for det in r['detections']:
                all_confidences.append(det['confidence'])
        
        stats = {
            'total_samples': total_samples,
            'total_detections': total_detections,
            'samples_with_detections': samples_with_detections,
            'detection_rate': samples_with_detections / total_samples * 100,
            'avg_detections_per_image': total_detections / total_samples,
            'avg_inference_time': np.mean(inference_times),
            'std_inference_time': np.std(inference_times),
            'min_inference_time': np.min(inference_times),
            'max_inference_time': np.max(inference_times),
            'fps': 1.0 / np.mean(inference_times),
            'detection_counts': detection_counts,
            'confidences': all_confidences,
            'avg_confidence': np.mean(all_confidences) if all_confidences else 0,
            'min_confidence': np.min(all_confidences) if all_confidences else 0,
            'max_confidence': np.max(all_confidences) if all_confidences else 0
        }
        
        return stats
    
    def _save_results(self, results, stats, output_dir):
        """保存评估结果"""
        # 保存详细结果
        results_simple = []
        for r in results:
            results_simple.append({
                'image_idx': r['image_idx'],
                'image_path': r['image_path'],
                'num_detections': r['num_detections'],
                'inference_time': r['inference_time']
            })
        
        results_json = output_dir / "results.json"
        with open(results_json, 'w', encoding='utf-8') as f:
            json.dump(results_simple, f, indent=2, ensure_ascii=False)
        
        # 保存统计
        stats_simple = {k: v for k, v in stats.items() 
                       if not isinstance(v, (list, np.ndarray))}
        
        stats_json = output_dir / "statistics.json"
        with open(stats_json, 'w', encoding='utf-8') as f:
            json.dump(stats_simple, f, indent=2, ensure_ascii=False)
        
        print(f"\n✓ 结果已保存:")
        print(f"  - {results_json}")
        print(f"  - {stats_json}")
    
    def _print_report(self, stats):
        """打印评估报告"""
        print("\n" + "="*60)
        print("评估报告")
        print("="*60)
        
        print(f"\n检测统计:")
        print(f"  测试样本数: {stats['total_samples']}")
        print(f"  总检测数: {stats['total_detections']}")
        print(f"  检测率: {stats['detection_rate']:.1f}% (有检测结果的图像占比)")
        print(f"  平均每图: {stats['avg_detections_per_image']:.2f} 个灯具")
        
        print(f"\n置信度统计:")
        print(f"  平均置信度: {stats['avg_confidence']:.3f}")
        print(f"  置信度范围: [{stats['min_confidence']:.3f}, {stats['max_confidence']:.3f}]")
        
        print(f"\n性能统计:")
        print(f"  平均推理时间: {stats['avg_inference_time']*1000:.2f} ms")
        print(f"  标准差: {stats['std_inference_time']*1000:.2f} ms")
        print(f"  范围: [{stats['min_inference_time']*1000:.2f}, {stats['max_inference_time']*1000:.2f}] ms")
        print(f"  FPS: {stats['fps']:.2f}")
    
    def _generate_plots(self, results, stats, output_dir):
        """生成可视化图表"""
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        
        # 1. 检测数分布
        ax = axes[0, 0]
        detection_counts = stats['detection_counts']
        ax.hist(detection_counts, bins=range(max(detection_counts)+2), 
                edgecolor='black', alpha=0.7)
        ax.set_xlabel('每图检测数', fontsize=12)
        ax.set_ylabel('图像数量', fontsize=12)
        ax.set_title(f'检测数分布 (平均: {stats["avg_detections_per_image"]:.2f})', fontsize=14)
        ax.grid(alpha=0.3)
        
        # 2. 置信度分布
        ax = axes[0, 1]
        if stats['confidences']:
            ax.hist(stats['confidences'], bins=20, edgecolor='black', alpha=0.7)
            ax.set_xlabel('置信度', fontsize=12)
            ax.set_ylabel('检测数量', fontsize=12)
            ax.set_title(f'置信度分布 (平均: {stats["avg_confidence"]:.3f})', fontsize=14)
            ax.grid(alpha=0.3)
        else:
            ax.text(0.5, 0.5, '无检测结果', ha='center', va='center', fontsize=14)
        
        # 3. 推理时间分布
        ax = axes[1, 0]
        inference_times = [r['inference_time']*1000 for r in results]
        ax.hist(inference_times, bins=20, edgecolor='black', alpha=0.7)
        ax.set_xlabel('推理时间 (ms)', fontsize=12)
        ax.set_ylabel('图像数量', fontsize=12)
        ax.set_title(f'推理时间分布 (平均: {stats["avg_inference_time"]*1000:.2f}ms)', fontsize=14)
        ax.grid(alpha=0.3)
        
        # 4. 性能摘要
        ax = axes[1, 1]
        ax.axis('off')
        
        summary_text = f"""
DINO检测性能摘要

检测统计:
  测试样本: {stats['total_samples']}
  总检测数: {stats['total_detections']}
  检测率: {stats['detection_rate']:.1f}%
  平均/图: {stats['avg_detections_per_image']:.2f}

置信度:
  平均: {stats['avg_confidence']:.3f}
  范围: [{stats['min_confidence']:.3f}, {stats['max_confidence']:.3f}]

性能:
  推理时间: {stats['avg_inference_time']*1000:.2f} ms
  FPS: {stats['fps']:.2f}
"""
        ax.text(0.1, 0.5, summary_text, fontsize=11, family='monospace',
                verticalalignment='center')
        
        plt.tight_layout()
        
        plot_path = output_dir / "evaluation_plots.png"
        plt.savefig(plot_path, dpi=150, bbox_inches='tight')
        plt.close()
        
        print(f"  - {plot_path}")


def main():
    """主评估流程"""
    import argparse
    
    parser = argparse.ArgumentParser(description="OWLv2灯具检测评估")
    parser.add_argument('--samples', type=int, default=50, help='测试样本数')
    parser.add_argument('--confidence', type=float, default=0.15, help='检测置信度阈值 (OWLv2优化)')
    parser.add_argument('--output', type=str, default='results/owlv2_evaluation', help='输出目录')
    parser.add_argument('--int8', action='store_true', help='运行INT8量化模型评估')
    
    args = parser.parse_args()
    
    if args.int8:
        print("Running INT8 evaluation...")
        evaluator_int8 = LightDetectionEvaluator(use_int8=True)
        stats_int8 = evaluator_int8.evaluate(
            max_samples=args.samples,
            confidence_threshold=args.confidence,
            output_dir=Path(args.output) / "int8"
        )
    
    print("Running FP16 evaluation...")
    evaluator_fp16 = LightDetectionEvaluator(use_int8=False)
    stats_fp16 = evaluator_fp16.evaluate(
        max_samples=args.samples,
        confidence_threshold=args.confidence,
        output_dir=Path(args.output) / "fp16"
    )

    if args.int8:
        print("\n" + "="*60)
        print("Comparison Report")
        print("="*60)
        print(f"| Metric | FP16 | INT8 |")
        print(f"|---|---|---|")
        print(f"| Avg. Inference Time (ms) | {stats_fp16['avg_inference_time']*1000:.2f} | {stats_int8['avg_inference_time']*1000:.2f} |")
        print(f"| FPS | {stats_fp16['fps']:.2f} | {stats_int8['fps']:.2f} |")
        print(f"| Avg. Detections | {stats_fp16['avg_detections_per_image']:.2f} | {stats_int8['avg_detections_per_image']:.2f} |")
        print(f"| Avg. Confidence | {stats_fp16['avg_confidence']:.3f} | {stats_int8['avg_confidence']:.3f} |")

    print("\n" + "="*60)
    print("✓ 评估完成!")
    print("="*60)
    print(f"结果保存在: {args.output}/")


if __name__ == "__main__":
    main()
