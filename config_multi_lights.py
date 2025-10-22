"""
多灯场景优化配置 - OWLv2 架构
用于改善密集灯具场景的检测召回率

注意: 已从 Grounding DINO 迁移到 OWLv2
最后更新: 2025-10-22
"""

# OWLv2 检测配置
DETECTION_CONFIG = {
    # OWLv2 针对室内场景优化的置信度阈值
    'confidence_threshold': 0.15,  # OWLv2推荐0.15 (比Grounding DINO更低)
    
    # NMS配置
    'use_nms': True,
    'nms_threshold': 0.5,  # IoU阈值,越小去重越激进
    
    # 面积过滤
    'min_area_ratio': 0.001,  # 最小检测框面积比例
    
    # 多尺度检测 (可选,会增加计算时间)
    'multi_scale': False,  # OWLv2单尺度已足够准确
    'scales': [0.8, 1.0, 1.2],  # 如启用多尺度
    
    # 滑动窗口检测 (针对超多灯场景,可选)
    'use_sliding_window': False,
    'window_size': (640, 480),
    'stride': 320,
}

# 提示词策略
PROMPT_STRATEGIES = {
    # 策略1: 通用灯具 (默认)
    'general': [
        "light", "lamp", "chandelier", "ceiling light",
        "pendant light", "wall lamp", "bulb", "lighting fixture",
        "LED light", "tube light", "spotlight", "downlight",
        "light source", "illumination", "bright light"
    ],
    
    # 策略2: 室内灯具专用
    'indoor': [
        "ceiling lamp", "ceiling light", "overhead light",
        "recessed light", "track light", "pendant lamp",
        "chandelier", "wall sconce", "table lamp",
        "floor lamp", "desk lamp", "LED panel"
    ],
    
    # 策略3: 工业/商业灯具
    'industrial': [
        "industrial light", "warehouse light", "high bay light",
        "LED strip", "tube light", "fluorescent light",
        "spotlight", "floodlight", "panel light"
    ],
    
    # 策略4: 简化版 (速度优先)
    'simple': [
        "light", "lamp", "lighting"
    ]
}

# 后处理配置
POST_PROCESS_CONFIG = {
    # 最小框尺寸 (像素)
    'min_box_area': 100,
    
    # 最大框尺寸 (相对图像)
    'max_box_ratio': 0.5,
    
    # 去除边缘检测
    'remove_edge_detections': True,
    'edge_margin': 10,  # 像素
    
    # 置信度加权融合
    'confidence_boost': {
        'bright_region': 0.05,  # 亮度区域加权
        'center_region': 0.03,  # 中心区域加权
    }
}

# 性能优化
PERFORMANCE_CONFIG = {
    # 图像预处理
    'resize_before_detection': True,
    'max_size': 1280,  # 长边最大尺寸
    
    # 批处理
    'batch_size': 1,
    
    # 缓存
    'cache_model': True,
}


def get_optimized_config(scenario='general'):
    """
    获取优化配置
    
    Args:
        scenario: 场景类型 ('general', 'indoor', 'industrial', 'dense')
    
    Returns:
        config: dict
    """
    config = {
        'detection': DETECTION_CONFIG.copy(),
        'post_process': POST_PROCESS_CONFIG.copy(),
        'performance': PERFORMANCE_CONFIG.copy(),
    }
    
    # 根据场景调整
    if scenario == 'dense':
        # 超密集场景
        config['detection']['confidence_threshold'] = 0.12
        config['detection']['nms_threshold'] = 0.40
        config['detection']['use_sliding_window'] = True
        
    elif scenario == 'indoor':
        config['detection']['confidence_threshold'] = 0.18
        
    elif scenario == 'industrial':
        config['detection']['confidence_threshold'] = 0.20
    
    return config


# 使用示例
if __name__ == "__main__":
    print("=" * 60)
    print("多灯场景优化配置")
    print("=" * 60)
    
    scenarios = ['general', 'indoor', 'industrial', 'dense']
    
    for scenario in scenarios:
        config = get_optimized_config(scenario)
        print(f"\n场景: {scenario}")
        print(f"  置信度阈值: {config['detection']['confidence_threshold']}")
        print(f"  NMS阈值: {config['detection']['nms_threshold']}")
        print(f"  滑动窗口: {config['detection']['use_sliding_window']}")
    
    print("\n" + "=" * 60)
    print("提示词策略:")
    print("=" * 60)
    for strategy, prompts in PROMPT_STRATEGIES.items():
        print(f"\n{strategy}: {len(prompts)} 个提示词")
        print(f"  {', '.join(prompts[:5])}...")
