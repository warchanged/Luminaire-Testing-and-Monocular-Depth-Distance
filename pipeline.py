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


class LightLocalization3D:
    """基于OWLv2 + DINOv3 + Depth Anything V2的灯具3D定位系统"""
    
    def __init__(
        self,
        detection_model="google/owlv2-large-patch14-ensemble",
        feature_model="facebook/dinov3-vitl16-pretrain-lvd1689m",
        depth_model="depth-anything/Depth-Anything-V2-Large-hf",
        device=None,
        enable_fallback=True
    ):
        """
        初始化3D定位流水线
        
        Args:
            detection_model: OWLv2检测模型
            feature_model: DINOv3特征提取模型
            depth_model: Depth Anything V2深度估计模型
            device: 运行设备 ('cuda', 'cpu', 或 None自动选择)
            enable_fallback: 是否启用降级策略
        """
        if device is None:
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
        else:
            self.device = device
            
        print(f"{'='*60}")
        print(f"初始化 OWLv2 + DINOv3 + Depth Anything V2 流水线")
        print(f"{'='*60}")
        print(f"使用设备: {self.device}")
        
        # 1. 加载OWLv2检测模型
        self.enable_fallback = enable_fallback
        self._load_detection_model(detection_model)
        
        # 2. 加载DINOv3特征提取模型
        self._load_feature_model(feature_model)
        
        # 3. 加载Depth Anything V2深度估计模型
        self._load_depth_model(depth_model)
        
        # 4. 灯具检测提示词 (针对室内场景优化)
        self.light_prompts = [
            # 吊灯类
            "chandelier", "pendant light", "hanging lamp", "drop light",
            # 吸顶灯类
            "ceiling light", "ceiling lamp", "flush mount light", "recessed light", "downlight",
            # 壁灯类
            "wall lamp", "wall sconce", "wall light", "wall mounted light",
            # 台灯/落地灯类
            "table lamp", "desk lamp", "floor lamp", "standing lamp",
            # 筒灯/射灯类
            "spotlight", "track light", "can light", "pot light",
            # LED灯类
            "LED panel", "LED light", "LED strip", "LED bulb",
            # 装饰灯类
            "decorative light", "ambient light", "mood light",
            # 通用
            "light fixture", "lighting", "lamp", "bulb", "light"
        ]
        
        print(f"\n{'='*60}")
        print(f"✓ 流水线初始化完成!")
        print(f"  检测模型: {self.detection_model_name}")
        print(f"  特征模型: {self.feature_model_name}")
        print(f"  深度模型: {self.depth_model_name}")
        print(f"  灯具类别: {len(self.light_prompts)} 种")
        print(f"{'='*60}\n")

    def _to_pil(self, image):
        """Convert an image (numpy BGR or PIL) to a PIL Image in RGB.

        This centralizes conversion logic and reduces duplicated code.
        """
        if isinstance(image, np.ndarray):
            # Support HxWx3 BGR uint8 images and other numpy arrays
            if image.ndim == 3 and image.shape[2] == 3:
                image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                return Image.fromarray(image_rgb)
            else:
                return Image.fromarray(image)
        return image
    
    def _load_detection_model(self, model_name):
        """加载OWLv2检测模型 (支持降级)"""
        print(f"\n1. 加载OWLv2检测模型...")
        
        # 模型选择顺序: Large → Base
        model_configs = [
            ("google/owlv2-large-patch14-ensemble", "OWLv2-Large"),
            ("google/owlv2-base-patch16-ensemble", "OWLv2-Base")
        ]
        
        if model_name not in [m[0] for m in model_configs]:
            model_configs.insert(0, (model_name, "OWLv2-Custom"))
        
        for model_path, model_desc in model_configs:
            try:
                print(f"   尝试加载: {model_desc}")
                self.detection_processor = AutoProcessor.from_pretrained(model_path)
                self.detection_model = AutoModelForZeroShotObjectDetection.from_pretrained(
                    model_path
                )
                self.detection_model.to(self.device)
                self.detection_model.eval()
                
                self.detection_model_name = model_desc
                print(f"   ✓ {model_desc} 加载成功!")
                self.use_detection = True
                break
                
            except Exception as e:
                print(f"   ✗ {model_desc} 加载失败: {e}")
                if not self.enable_fallback:
                    raise
                continue
        else:
            print("   ✗ 所有检测模型加载失败!")
            self.use_detection = False
            self.detection_model_name = "None"
    
    def _load_feature_model(self, model_name):
        """加载DINOv3特征提取模型 (支持降级)"""
        print(f"\n2. 加载DINOv3特征模型...")
        
        # 模型选择顺序: Large → Base → Small → DINOv2
        model_configs = [
            ("facebook/dinov3-vitl16-pretrain-lvd1689m", "DINOv3-Large (304M参数)"),
            ("facebook/dinov3-vitb16-pretrain-lvd1689m", "DINOv3-Base (86M参数)"),
            ("facebook/dinov3-vits16-pretrain-lvd1689m", "DINOv3-Small (22M参数)"),
            ("facebook/dinov2-large", "DINOv2-Large (备用)")
        ]
        
        if model_name not in [m[0] for m in model_configs]:
            model_configs.insert(0, (model_name, "DINOv3-Custom"))
        
        for model_path, model_desc in model_configs:
            try:
                print(f"   尝试加载: {model_desc}")
                self.feature_processor = AutoImageProcessor.from_pretrained(model_path)
                self.feature_model = AutoModel.from_pretrained(model_path)
                self.feature_model.to(self.device)
                self.feature_model.eval()
                
                self.feature_model_name = model_desc
                print(f"   ✓ {model_desc} 加载成功!")
                self.use_features = True
                break
                
            except Exception as e:
                print(f"   ✗ {model_desc} 加载失败: {e}")
                if not self.enable_fallback:
                    raise
                continue
        else:
            print("   ✗ 所有特征模型加载失败!")
            self.use_features = False
            self.feature_model_name = "None"
    
    def _load_depth_model(self, model_name):
        """加载Depth Anything V2深度估计模型 (支持降级)"""
        print(f"\n3. 加载Depth Anything V2深度模型...")
        
        # 模型选择顺序: Large → Base → Small → DINOv3特征方法
        model_configs = [
            ("depth-anything/Depth-Anything-V2-Large-hf", "Depth Anything V2 Large"),
            ("depth-anything/Depth-Anything-V2-Base-hf", "Depth Anything V2 Base"),
            ("depth-anything/Depth-Anything-V2-Small-hf", "Depth Anything V2 Small")
        ]
        
        if model_name not in [m[0] for m in model_configs]:
            model_configs.insert(0, (model_name, "Depth Anything V2 Custom"))
        
        for model_path, model_desc in model_configs:
            try:
                print(f"   尝试加载: {model_desc}")
                self.depth_processor = DPTImageProcessor.from_pretrained(model_path)
                self.depth_model = AutoModelForDepthEstimation.from_pretrained(model_path)
                self.depth_model.to(self.device)
                self.depth_model.eval()
                
                self.depth_model_name = model_desc
                print(f"   ✓ {model_desc} 加载成功!")
                self.use_depth_anything_v2 = True
                break
                
            except Exception as e:
                print(f"   ✗ {model_desc} 加载失败: {e}")
                if not self.enable_fallback:
                    raise
                continue
        else:
            print("   ⚠️ Depth Anything V2加载失败,将使用DINOv3特征方法")
            self.use_depth_anything_v2 = False
            self.depth_model_name = "DINOv3 Feature-based"
    
    def detect_lights(
        self,
        image,
        confidence_threshold=0.15,
        use_nms=True,
        nms_threshold=0.5,
        min_area_ratio=0.001
    ):
        """
        使用OWLv2检测灯具 (针对室内场景优化)
        
        Args:
            image: numpy数组 (H, W, 3) BGR格式, 或PIL Image
            confidence_threshold: 置信度阈值 (降低以检测更多灯具)
            use_nms: 是否使用NMS去除重复检测
            nms_threshold: NMS的IoU阈值
            min_area_ratio: 最小检测框面积比例 (相对于图像)
        
        Returns:
            detections: list of dict with keys: box, confidence, label
        """
        if not self.use_detection:
            print("⚠️ 检测模型未加载")
            return []
        
        # Convert to PIL Image (centralized)
        pil_image = self._to_pil(image)
        
        try:
            # 准备输入
            text_queries = self.light_prompts
            inputs = self.detection_processor(
                images=pil_image,
                text=text_queries,
                return_tensors="pt"
            )
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            # 推理
            with torch.no_grad():
                outputs = self.detection_model(**inputs)
            
            # 后处理
            target_sizes = torch.tensor([pil_image.size[::-1]]).to(self.device)
            results = self.detection_processor.post_process_object_detection(
                outputs=outputs,
                target_sizes=target_sizes,
                threshold=confidence_threshold
            )[0]
            
            # 提取检测结果
            detections = []
            seen_boxes = []  # 用于NMS
            image_area = pil_image.size[0] * pil_image.size[1]
            
            for box, score, label_id in zip(
                results["boxes"],
                results["scores"],
                results["labels"]
            ):
                box_np = box.cpu().numpy()
                
                # 检查面积
                width = box_np[2] - box_np[0]
                height = box_np[3] - box_np[1]
                area = width * height
                
                if area < image_area * min_area_ratio:
                    continue
                
                # NMS去重
                if use_nms:
                    is_duplicate = False
                    for seen_box in seen_boxes:
                        iou = self._calculate_iou(box_np, seen_box)
                        if iou > nms_threshold:
                            is_duplicate = True
                            break
                    
                    if is_duplicate:
                        continue
                
                detections.append({
                    'box': box_np,
                    'confidence': float(score),
                    'label': text_queries[label_id] if label_id < len(text_queries) else 'light'
                })
                seen_boxes.append(box_np)
            
            # 按置信度排序
            detections = sorted(detections, key=lambda x: x['confidence'], reverse=True)
            
            return detections
            
        except Exception as e:
            print(f"⚠️ 检测失败: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def extract_features(self, image):
        """
        使用DINOv3提取图像特征
        
        Args:
            image: PIL Image或numpy数组
        
        Returns:
            features_dict: dict with keys: cls_features, patch_features
        """
        if not self.use_features:
            print("⚠️ 特征模型未加载")
            return None
        
        # Convert to PIL Image (centralized)
        pil_image = self._to_pil(image)
        
        try:
            # 预处理
            inputs = self.feature_processor(images=pil_image, return_tensors="pt")
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            # 提取特征
            with torch.no_grad():
                outputs = self.feature_model(**inputs)
                features = outputs.last_hidden_state
                cls_features = features[:, 0, :]  # CLS token
                patch_features = features[:, 1:, :]  # Patch tokens
            
            return {
                'cls_features': cls_features,
                'patch_features': patch_features,
                'full_features': features
            }
        except Exception as e:
            print(f"⚠️ 特征提取失败: {e}")
            return None
    
    def estimate_depth(self, image, features_dict=None):
        """
        估计深度图 (使用Depth Anything V2或DINOv3特征)
        
        Args:
            image: PIL Image或numpy数组
            features_dict: DINOv3特征字典 (用于降级)
        
        Returns:
            depth_map: numpy array (H, W), 归一化深度值 [0, 1]
        """
        # Convert to PIL Image (centralized)
        pil_image = self._to_pil(image)
        
        # 优先使用Depth Anything V2
        if self.use_depth_anything_v2:
            try:
                inputs = self.depth_processor(images=pil_image, return_tensors="pt")
                inputs = {k: v.to(self.device) for k, v in inputs.items()}
                
                with torch.no_grad():
                    outputs = self.depth_model(**inputs)
                    predicted_depth = outputs.predicted_depth
                
                # 插值到原图大小
                depth_map = torch.nn.functional.interpolate(
                    predicted_depth.unsqueeze(1),
                    size=(pil_image.size[1], pil_image.size[0]),
                    mode="bicubic",
                    align_corners=False,
                ).squeeze().cpu().numpy()
                
                # 归一化到[0, 1]
                depth_map = (depth_map - depth_map.min()) / (depth_map.max() - depth_map.min() + 1e-8)
                
                return depth_map
                
            except Exception as e:
                print(f"⚠️ Depth Anything V2失败,回退到DINOv3方法: {e}")
        
        # 降级方案: 使用DINOv3特征估计深度
        if not self.use_features:
            print("⚠️ 特征模型未加载,无法估计深度")
            return None
        
        try:
            # 如果没有提供特征,则提取特征
            if features_dict is None:
                features_dict = self.extract_features(pil_image)
            
            if features_dict is None:
                return None
            
            patch_features = features_dict['patch_features']
            
            # 计算patch特征范数作为深度线索
            patch_norms = torch.norm(patch_features, dim=-1).squeeze(0)
            
            # 重塑为2D网格
            num_patches = patch_norms.shape[0]
            grid_size = int(np.sqrt(num_patches))
            depth_features = patch_norms[:grid_size**2].reshape(grid_size, grid_size)
            
            # 转换并归一化
            depth_map = depth_features.cpu().numpy()
            depth_map = 1.0 - depth_map  # 反转
            depth_map = (depth_map - depth_map.min()) / (depth_map.max() - depth_map.min() + 1e-8)
            
            # 上采样到原图大小
            depth_map_resized = cv2.resize(
                depth_map,
                (pil_image.size[0], pil_image.size[1]),
                interpolation=cv2.INTER_CUBIC
            )
            
            # 高斯平滑
            depth_map_smooth = cv2.GaussianBlur(depth_map_resized, (15, 15), 0)
            
            return depth_map_smooth
            
        except Exception as e:
            print(f"⚠️ 深度估计失败: {e}")
            return None
    
    def depth_to_distance(
        self,
        depth_map,
        detections,
        camera_params=None,
        image_size=None
    ):
        """
        将归一化深度值转换为实际距离 (针对室内灯具优化)
        
        Args:
            depth_map: 归一化深度图 [0, 1]
            detections: 检测结果列表
            camera_params: 相机参数字典 (可选)
            image_size: 图像尺寸 (width, height)
        
        Returns:
            detections_with_distance: 添加了'distance'字段的检测结果
        """
        if depth_map is None or not detections:
            return detections
        
        if camera_params is None:
            camera_params = {}
        
        results = []
        
        for det in detections:
            x1, y1, x2, y2 = det['box'].astype(int)
            
            # 计算检测框中心点的相对位置
            center_y = (y1 + y2) / 2
            if image_size:
                rel_y = center_y / image_size[1]
            else:
                rel_y = center_y / depth_map.shape[0]
            
            # 根据灯具类型和位置智能调整距离范围
            label = det['label'].lower()
            
            # 吸顶灯/吊灯 (通常在上方)
            if any(kw in label for kw in ['ceiling', 'chandelier', 'pendant', 'hanging', 'recessed', 'downlight']):
                if rel_y < 0.4:
                    min_distance = 2.0
                    max_distance = 4.5
                else:
                    min_distance = 1.5
                    max_distance = 4.0
            
            # 壁灯 (中等高度)
            elif any(kw in label for kw in ['wall', 'sconce']):
                min_distance = 1.0
                max_distance = 3.5
            
            # 台灯/落地灯 (较低位置)
            elif any(kw in label for kw in ['table', 'desk', 'floor', 'standing']):
                if rel_y > 0.6:
                    min_distance = 0.5
                    max_distance = 2.5
                else:
                    min_distance = 1.0
                    max_distance = 3.0
            
            # 射灯/筒灯
            elif any(kw in label for kw in ['spotlight', 'track', 'can', 'pot']):
                min_distance = 1.5
                max_distance = 4.0
            
            # 其他通用灯具
            else:
                min_distance = 0.8
                max_distance = 4.5
            
            # 允许用户覆盖
            min_distance = camera_params.get('min_distance', min_distance)
            max_distance = camera_params.get('max_distance', max_distance)
            
            # 获取ROI深度值
            x1_clip = max(0, x1)
            y1_clip = max(0, y1)
            x2_clip = min(depth_map.shape[1], x2)
            y2_clip = min(depth_map.shape[0], y2)
            
            if x2_clip > x1_clip and y2_clip > y1_clip:
                roi_depth = depth_map[y1_clip:y2_clip, x1_clip:x2_clip]
                
                # 多指标深度
                median_depth = np.median(roi_depth)
                mean_depth = np.mean(roi_depth)
                combined_depth = 0.7 * median_depth + 0.3 * mean_depth
                
                # 非线性映射
                if combined_depth < 0.3:
                    distance = min_distance + combined_depth * (max_distance - min_distance) / 0.3
                else:
                    normalized_depth = (combined_depth - 0.3) / 0.7
                    distance = min_distance + (max_distance - min_distance) * 0.3 + \
                              (max_distance - min_distance) * 0.7 * (np.log1p(normalized_depth * 2) / np.log1p(2))
                
                # 根据检测框大小微调
                box_area = (x2 - x1) * (y2 - y1)
                image_area = depth_map.shape[0] * depth_map.shape[1]
                area_ratio = box_area / image_area
                
                if area_ratio > 0.15:
                    distance *= 0.85
                elif area_ratio < 0.02:
                    distance *= 1.15
                
                distance = np.clip(distance, min_distance, max_distance)
                
                det_copy = det.copy()
                det_copy['distance'] = distance
                det_copy['depth_value'] = combined_depth
                det_copy['distance_range'] = (min_distance, max_distance)
                det_copy['position_hint'] = 'upper' if rel_y < 0.4 else 'middle' if rel_y < 0.6 else 'lower'
                results.append(det_copy)
            else:
                det_copy = det.copy()
                det_copy['distance'] = None
                results.append(det_copy)
        
        return results
    
    def process_image(
        self,
        image,
        confidence_threshold=0.15,
        compute_depth=True,
        compute_distance=True
    ):
        """
        完整处理流程: 检测 + 特征提取 + 深度估计 + 距离计算
        
        Args:
            image: 输入图像 (numpy或PIL)
            confidence_threshold: 检测置信度阈值
            compute_depth: 是否计算深度图
            compute_distance: 是否计算距离
        
        Returns:
            result_dict: 包含所有结果的字典
        """
        start_time = time.time()
        
        # 1. 检测灯具
        detections = self.detect_lights(image, confidence_threshold)
        detection_time = time.time() - start_time
        
        # 2. 提取特征
        features_dict = None
        if compute_depth or self.use_features:
            features_dict = self.extract_features(image)
        feature_time = time.time() - start_time - detection_time
        
        # 3. 估计深度
        depth_map = None
        if compute_depth:
            depth_map = self.estimate_depth(image, features_dict)
        depth_time = time.time() - start_time - detection_time - feature_time
        
        # 4. 计算距离
        if compute_distance and depth_map is not None:
            if isinstance(image, np.ndarray):
                image_size = (image.shape[1], image.shape[0])
            else:
                image_size = image.size
            detections = self.depth_to_distance(depth_map, detections, image_size=image_size)
        distance_time = time.time() - start_time - detection_time - feature_time - depth_time
        
        total_time = time.time() - start_time
        
        return {
            'detections': detections,
            'features': features_dict,
            'depth_map': depth_map,
            'timing': {
                'detection': detection_time,
                'features': feature_time,
                'depth': depth_time,
                'distance': distance_time,
                'total': total_time
            }
        }
    
    @staticmethod
    def _calculate_iou(box1, box2):
        """计算两个边界框的IOU"""
        x1_min, y1_min, x1_max, y1_max = box1
        x2_min, y2_min, x2_max, y2_max = box2
        
        inter_x_min = max(x1_min, x2_min)
        inter_y_min = max(y1_min, y2_min)
        inter_x_max = min(x1_max, x2_max)
        inter_y_max = min(y1_max, y2_max)
        
        if inter_x_max < inter_x_min or inter_y_max < inter_y_min:
            return 0.0
        
        inter_area = (inter_x_max - inter_x_min) * (inter_y_max - inter_y_min)
        box1_area = (x1_max - x1_min) * (y1_max - y1_min)
        box2_area = (x2_max - x2_min) * (y2_max - y2_min)
        union_area = box1_area + box2_area - inter_area
        
        return inter_area / union_area if union_area > 0 else 0.0


def main():
    """测试流水线"""
    print("="*60)
    print("OWLv2 + DINOv3 + Depth Anything V2 测试")
    print("="*60)
    
    # 初始化流水线
    pipeline = LightLocalization3D()
    
    # 查找测试图像
    test_dirs = [
        "data/yolo_dataset/images/val",
        "data/custom_images",
        "data/test"
    ]
    
    test_image_path = None
    for test_dir in test_dirs:
        test_dir_path = Path(test_dir)
        if test_dir_path.exists():
            images = list(test_dir_path.glob("*.jpg")) + list(test_dir_path.glob("*.png"))
            if images:
                test_image_path = images[0]
                break
    
    if test_image_path is None or not test_image_path.exists():
        print("⚠️ 未找到测试图像")
        return
    
    print(f"\n测试图像: {test_image_path}")
    
    # 读取图像
    image = cv2.imread(str(test_image_path))
    if image is None:
        print("❌ 无法读取图像")
        return
    
    # 处理
    result = pipeline.process_image(image, confidence_threshold=0.15)
    
    # 显示结果
    print(f"\n{'='*60}")
    print("检测结果:")
    print(f"{'='*60}")
    print(f"检测到 {len(result['detections'])} 个灯具")
    
    for i, det in enumerate(result['detections'], 1):
        print(f"\n  #{i} {det['label']}")
        print(f"      置信度: {det['confidence']:.2%}")
        if det.get('distance'):
            print(f"      距离: {det['distance']:.2f}m")
            print(f"      位置: {det.get('position_hint', 'unknown')}")
    
    print(f"\n{'='*60}")
    print("性能统计:")
    print(f"{'='*60}")
    timing = result['timing']
    print(f"  检测: {timing['detection']:.3f}s")
    print(f"  特征提取: {timing['features']:.3f}s")
    print(f"  深度估计: {timing['depth']:.3f}s")
    print(f"  距离计算: {timing['distance']:.3f}s")
    print(f"  总计: {timing['total']:.3f}s")
    print(f"  FPS: {1/timing['total']:.2f}")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
