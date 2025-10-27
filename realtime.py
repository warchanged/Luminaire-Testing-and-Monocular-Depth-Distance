"""
实时灯具3D定位 - 使用OWLv2 + DINOv3 + Depth Anything V2
已在Colab验证的最优技术栈
"""

import cv2
import numpy as np
import torch
from pathlib import Path
import time
import argparse
from pipeline import LightLocalization3D


class RealtimeLightDetection:
    """实时灯具3D定位 (OWLv2架构)"""
    
    def __init__(self, 
                 detection_model="google/owlv2-large-patch14-ensemble",
                 feature_model="facebook/dinov3-vitl16-pretrain-lvd1689m",
                 depth_model="depth-anything/Depth-Anything-V2-Large-hf",
                 confidence_threshold=0.15):
        """
        初始化实时检测系统
        
        Args:
            detection_model: OWLv2检测模型
            feature_model: DINOv3特征模型
            depth_model: Depth Anything V2深度模型
            confidence_threshold: 检测置信度阈值 (0.15针对室内优化)
        """
        print("="*60)
        print("初始化实时检测系统 (OWLv2 + DINOv3 + Depth Anything V2)")
        print("="*60)
        
        # 加载3D定位流水线
        self.pipeline = LightLocalization3D(
            detection_model=detection_model,
            feature_model=feature_model,
            depth_model=depth_model
        )
        
        self.confidence_threshold = confidence_threshold
        
        # 性能统计
        self.fps_history = []
        self.detection_count = 0
        self.frame_count = 0
        
        print("✓ 实时系统初始化完成!")
        print("="*60)
    
    def process_frame(self, frame, show_stats=True, compute_depth=True):
        """
        处理单帧图像
        
        Args:
            frame: numpy数组 (H, W, 3) BGR格式
            show_stats: 是否显示统计信息
            compute_depth: 是否计算深度和距离
        
        Returns:
            vis_frame: 可视化结果
            results: 检测结果字典
            fps: 当前FPS
        """
        start_time = time.time()
        
        # 执行完整处理流程
        results = self.pipeline.process_image(
            frame,
            confidence_threshold=self.confidence_threshold,
            compute_depth=compute_depth,
            compute_distance=compute_depth
        )
        
        detections = results['detections']
        depth_map = results.get('depth_map')
        
        # 可视化
        vis_frame = self._visualize_frame(frame, detections, depth_map)
        
        # 计算FPS
        elapsed = time.time() - start_time
        fps = 1.0 / elapsed if elapsed > 0 else 0
        
        self.fps_history.append(fps)
        if len(self.fps_history) > 30:
            self.fps_history.pop(0)
        
        self.frame_count += 1
        self.detection_count += len(detections)
        
        # 显示统计信息
        if show_stats:
            avg_fps = np.mean(self.fps_history)
            
            # FPS
            cv2.putText(
                vis_frame,
                f"FPS: {avg_fps:.1f}",
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                1.0,
                (0, 255, 0),
                2
            )
            
            # 检测统计
            cv2.putText(
                vis_frame,
                f"Detections: {len(detections)}",
                (10, 70),
                cv2.FONT_HERSHEY_SIMPLEX,
                1.0,
                (0, 255, 0),
                2
            )
            
            # 总计
            cv2.putText(
                vis_frame,
                f"Total: {self.detection_count} lights in {self.frame_count} frames",
                (10, 110),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (255, 255, 255),
                2
            )
        
        return vis_frame, results, fps
    
    def _visualize_frame(self, frame, detections, depth_map=None):
        """
        可视化检测结果
        
        Args:
            frame: 输入帧
            detections: 检测结果列表
            depth_map: 深度图 (可选)
        
        Returns:
            vis_frame: 可视化后的帧
        """
        vis_frame = frame.copy()
        
        for det in detections:
            x1, y1, x2, y2 = det['box'].astype(int)
            confidence = det['confidence']
            label = det['label']
            
            # 根据置信度选择颜色
            if confidence > 0.5:
                color = (0, 255, 0)  # 绿色 - 高置信度
            elif confidence > 0.3:
                color = (0, 255, 255)  # 黄色 - 中等置信度
            else:
                color = (0, 165, 255)  # 橙色 - 低置信度
            
            thickness = 2 if confidence > 0.3 else 1
            
            # 绘制边界框
            cv2.rectangle(vis_frame, (x1, y1), (x2, y2), color, thickness)
            
            # 准备标签文本
            text_lines = [f"{label}: {confidence:.2f}"]
            if det.get('distance'):
                text_lines.append(f"{det['distance']:.2f}m")
            
            # 绘制标签背景和文本
            y_offset = y1 - 5
            for text in text_lines:
                (w, h), _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
                cv2.rectangle(vis_frame, (x1, y_offset-h-5), (x1+w, y_offset), color, -1)
                cv2.putText(vis_frame, text, (x1, y_offset-5),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                y_offset -= (h + 10)
        
        return vis_frame
    
    def run_webcam(self, camera_id=0, output_path=None):
        """
        运行网络摄像头实时检测
        
        Args:
            camera_id: 摄像头ID (0=默认摄像头)
            output_path: 输出视频路径 (可选)
        """
        print(f"\n启动摄像头 (ID={camera_id})...")
        cap = cv2.VideoCapture(camera_id)
        
        if not cap.isOpened():
            print(f"✗ 无法打开摄像头 {camera_id}")
            return
        
        # 获取视频属性
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps_cam = int(cap.get(cv2.CAP_PROP_FPS))
        
        print(f"摄像头分辨率: {width}x{height} @ {fps_cam}fps")
        
        # 视频写入器
        writer = None
        if output_path:
            output_path = Path(output_path)
            output_path.parent.mkdir(exist_ok=True, parents=True)
            
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            writer = cv2.VideoWriter(
                str(output_path),
                fourcc,
                fps_cam,
                (width, height)
            )
            print(f"录制到: {output_path}")
        
        print("\n开始检测...")
        print("按 'q' 退出, 'p' 暂停, 's' 保存截图")
        
        paused = False
        
        try:
            while True:
                if not paused:
                    ret, frame = cap.read()
                    if not ret:
                        print("\n✗ 无法读取帧")
                        break
                    
                    # 处理帧
                    vis_frame, results, fps = self.process_frame(frame)
                    
                    # 写入视频
                    if writer is not None:
                        writer.write(vis_frame)
                else:
                    # 暂停时显示当前帧
                    cv2.putText(
                        vis_frame,
                        "PAUSED - Press 'p' to resume",
                        (width//2 - 200, height//2),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        1.0,
                        (0, 0, 255),
                        3
                    )
                
                # 显示
                cv2.imshow('DINO Light Detection', vis_frame)
                
                # 按键处理
                key = cv2.waitKey(1) & 0xFF
                
                if key == ord('q'):
                    print("\n用户退出")
                    break
                elif key == ord('p'):
                    paused = not paused
                    status = "暂停" if paused else "继续"
                    print(f"\n{status}检测")
                elif key == ord('s'):
                    # 保存截图
                    screenshot_path = Path("results/screenshots")
                    screenshot_path.mkdir(exist_ok=True, parents=True)
                    
                    timestamp = time.strftime("%Y%m%d_%H%M%S")
                    save_path = screenshot_path / f"screenshot_{timestamp}.jpg"
                    cv2.imwrite(str(save_path), vis_frame)
                    print(f"\n✓ 截图保存: {save_path}")
        
        finally:
            # 清理
            cap.release()
            if writer is not None:
                writer.release()
            cv2.destroyAllWindows()
            
            # 统计
            print("\n" + "="*60)
            print("检测统计:")
            print("="*60)
            print(f"总帧数: {self.frame_count}")
            print(f"总检测数: {self.detection_count}")
            print(f"平均FPS: {np.mean(self.fps_history):.2f}")
            print(f"平均每帧检测: {self.detection_count/max(self.frame_count,1):.2f} 个灯具")
    
    def run_video(self, video_path, output_path=None):
        """
        处理视频文件
        
        Args:
            video_path: 输入视频路径
            output_path: 输出视频路径 (可选)
        """
        video_path = Path(video_path)
        
        if not video_path.exists():
            print(f"✗ 视频文件不存在: {video_path}")
            return
        
        print(f"\n处理视频: {video_path}")
        cap = cv2.VideoCapture(str(video_path))
        
        if not cap.isOpened():
            print(f"✗ 无法打开视频文件")
            return
        
        # 获取视频属性
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps_video = int(cap.get(cv2.CAP_PROP_FPS))
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        print(f"视频属性: {width}x{height} @ {fps_video}fps, {total_frames} 帧")
        
        # 视频写入器
        writer = None
        if output_path:
            output_path = Path(output_path)
            output_path.parent.mkdir(exist_ok=True, parents=True)
            
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            writer = cv2.VideoWriter(
                str(output_path),
                fourcc,
                fps_video,
                (width, height)
            )
            print(f"输出到: {output_path}")
        
        print("\n开始处理...")
        
        frame_idx = 0
        
        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                frame_idx += 1
                
                # 处理帧
                vis_frame, results, fps = self.process_frame(frame, show_stats=True)
                
                # 写入视频
                if writer is not None:
                    writer.write(vis_frame)
                
                # 进度
                if frame_idx % 10 == 0:
                    progress = frame_idx / total_frames * 100
                    print(f"\r进度: {frame_idx}/{total_frames} ({progress:.1f}%) - FPS: {fps:.1f}", end="")
                
                # 显示 (可选,按'q'退出)
                cv2.imshow('Processing Video', vis_frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    print("\n\n用户中断处理")
                    break
        
        finally:
            # 清理
            cap.release()
            if writer is not None:
                writer.release()
            cv2.destroyAllWindows()
            
            # 统计
            print("\n\n" + "="*60)
            print("处理完成!")
            print("="*60)
            print(f"处理帧数: {frame_idx}/{total_frames}")
            print(f"总检测数: {self.detection_count}")
            print(f"平均FPS: {np.mean(self.fps_history):.2f}")
            if output_path:
                print(f"输出视频: {output_path}")

    def _run_demo_mode(self):
        """运行demo模式"""
        # Demo模式: 使用测试数据集的图像
        print("\nDemo模式: 处理测试图像")

        # 找到测试图像
        test_dir = Path("data/yolo_dataset/images/val")
        if not test_dir.exists():
            test_dir = Path("data/yolo_dataset_dino/images/val")

        if not test_dir.exists():
            print("✗ 未找到测试图像目录")
            return

        # 创建伪视频流
        test_images = sorted(test_dir.glob("*.jpg"))[:10]

        if not test_images:
            print("✗ 未找到测试图像")
            return

        print(f"找到 {len(test_images)} 张测试图像")
        print("按 'q' 退出, 'n' 下一张, 'p' 上一张")

        idx = 0

        while True:
            # 读取图像
            img_path = test_images[idx]
            frame = cv2.imread(str(img_path))

            if frame is None:
                idx = (idx + 1) % len(test_images)
                continue

            # 处理
            vis_frame, results, fps = self.process_frame(frame)

            # 显示图像信息
            cv2.putText(
                vis_frame,
                f"Image {idx+1}/{len(test_images)}: {img_path.name}",
                (10, frame.shape[0] - 20),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (255, 255, 255),
                2
            )

            cv2.imshow('DINO Demo', vis_frame)

            # 按键
            key = cv2.waitKey(0) & 0xFF

            if key == ord('q'):
                break
            elif key == ord('n'):
                idx = (idx + 1) % len(test_images)
            elif key == ord('p'):
                idx = (idx - 1) % len(test_images)

        cv2.destroyAllWindows()

        print("\n✓ Demo完成")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="DINO实时灯具检测")
    
    parser.add_argument(
        '--mode',
        choices=['webcam', 'video', 'demo'],
        default='demo',
        help='运行模式'
    )
    
    parser.add_argument(
        '--input',
        type=str,
        help='输入视频路径 (仅video模式)'
    )
    
    parser.add_argument(
        '--output',
        type=str,
        help='输出视频路径'
    )
    
    parser.add_argument(
        '--camera',
        type=int,
        default=0,
        help='摄像头ID (仅webcam模式)'
    )
    
    parser.add_argument(
        '--confidence',
        type=float,
        default=0.22,
        help='检测置信度阈值 (推荐: 0.22平衡模式, 0.10-0.15多灯高召回, 0.25-0.30高精度)'
    )
    
    args = parser.parse_args()
    
    print("="*60)
    print("DINO实时灯具3D定位系统")
    print("="*60)
    
    # 初始化系统
    detector = RealtimeLightDetection(
        confidence_threshold=args.confidence
    )
    
    # 运行
    if args.mode == 'webcam':
        detector.run_webcam(
            camera_id=args.camera,
            output_path=args.output
        )
    
    elif args.mode == 'video':
        if not args.input:
            print("✗ 视频模式需要指定 --input 参数")
            return
        
        detector.run_video(
            video_path=args.input,
            output_path=args.output
        )
    
    elif args.mode == 'demo':
        detector._run_demo_mode()


if __name__ == "__main__":
    main()
