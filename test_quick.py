"""
快速测试DINO流程
验证环境配置和基本功能

NOTE: This is a functional test script (not a unittest-based test).
It provides interactive testing and validation of the DINO pipeline,
dependencies, and sample image detection. Run directly with: python test_quick.py

For automated unit tests, see test_api.py and test_realtime.py instead.
"""

def test_imports():
    """测试依赖导入"""
    print("测试依赖导入...")
    
    try:
        import torch
        print(f"  ✓ PyTorch {torch.__version__}")
        print(f"    CUDA可用: {torch.cuda.is_available()}")
    except ImportError as e:
        print(f"  ✗ PyTorch导入失败: {e}")
        return False
    
    try:
        import transformers
        print(f"  ✓ Transformers {transformers.__version__}")
    except ImportError as e:
        print(f"  ✗ Transformers导入失败: {e}")
        return False
    
    try:
        import cv2
        print(f"  ✓ OpenCV {cv2.__version__}")
    except ImportError as e:
        print(f"  ✗ OpenCV导入失败: {e}")
        return False
    
    try:
        import numpy
        print(f"  ✓ NumPy {numpy.__version__}")
    except ImportError as e:
        print(f"  ✗ NumPy导入失败: {e}")
        return False
    
    return True


def test_dino_pipeline():
    """测试DINO流水线"""
    print("\n测试DINO流水线...")
    
    try:
        from pipeline import LightLocalization3D
        print("  ✓ 导入LightLocalization3D成功")
    except ImportError as e:
        print(f"  ✗ 导入失败: {e}")
        return False
    
    try:
        print("  初始化流水线(这会下载模型,可能需要几分钟)...")
        pipeline = LightLocalization3D()
        print("  ✓ 流水线初始化成功")
        return True
    except Exception as e:
        print(f"  ✗ 初始化失败: {e}")
        return False


def test_sample_image():
    """测试样本图像检测"""
    print("\n测试样本图像检测...")
    
    from pathlib import Path
    import cv2
    import numpy as np
    
    # 查找测试图像
    test_dirs = [
        "data/yolo_dataset/images/val",
        "data/yolo_dataset_dino/images/val",
        "data/nyu_data/data"
    ]
    
    test_image = None
    for test_dir in test_dirs:
        test_dir = Path(test_dir)
        if test_dir.exists():
            images = list(test_dir.glob("*.jpg")) + list(test_dir.glob("*.png"))
            if images:
                test_image = images[0]
                break
    
    if test_image is None:
        print("  ⚠️  未找到测试图像,跳过此测试")
        return True
    
    print(f"  使用测试图像: {test_image}")
    
    try:
        from pipeline import LightLocalization3D
        
        # 读取图像
        img = cv2.imread(str(test_image))
        if img is None:
            print(f"  ✗ 无法读取图像")
            return False
        
        print(f"  图像尺寸: {img.shape}")
        
        # 初始化流水线
        pipeline = LightLocalization3D()
        
        # 执行检测 (使用平衡配置)
        print("  执行3D定位...")
        results = pipeline.localize_3d(
            img, 
            confidence_threshold=0.22,  # 平衡模式: 降低误检,保持较好召回率
            use_nms=True  # 启用NMS去重
        )
        
        print(f"  ✓ 检测完成,找到 {len(results)} 个灯具")
        
        if results:
            for i, res in enumerate(results[:3], 1):  # 只显示前3个
                print(f"    #{i}: {res['label']} (置信度: {res['confidence']:.3f})")
                print(f"        3D位置: {res['position_3d']}")
        
        # 保存可视化
        output_path = Path("results/quick_test_result.jpg")
        output_path.parent.mkdir(exist_ok=True, parents=True)
        
        vis_img = pipeline.visualize(img, results, output_path)
        print(f"  ✓ 结果已保存: {output_path}")
        
        return True
        
    except Exception as e:
        print(f"  ✗ 检测失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """主测试流程"""
    print("="*60)
    print("DINO流程快速测试")
    print("="*60)
    
    tests = [
        ("依赖导入", test_imports),
        ("DINO流水线", test_dino_pipeline),
        ("样本图像检测", test_sample_image)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{'='*60}")
        print(f"测试: {test_name}")
        print(f"{'='*60}")
        
        try:
            success = test_func()
            results.append((test_name, success))
        except KeyboardInterrupt:
            print("\n\n用户中断测试")
            break
        except Exception as e:
            print(f"\n✗ 测试异常: {e}")
            results.append((test_name, False))
    
    # 总结
    print("\n" + "="*60)
    print("测试总结")
    print("="*60)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    print(f"\n通过: {passed}/{total}")
    
    for test_name, success in results:
        status = "✓" if success else "✗"
        print(f"  {status} {test_name}")
    
    if passed == total:
        print("\n🎉 所有测试通过!系统已就绪")
        print("\n下一步:")
        print("  1. 运行完整流水线: uv run python run_all.py")
        print("  2. 实时检测Demo: uv run python realtime.py --mode demo")
        print("  3. 性能评估: uv run python evaluate.py")
    else:
        print(f"\n⚠️  {total - passed} 个测试失败,请检查错误信息")


if __name__ == "__main__":
    main()
