"""
完整流水线运行脚本 - DINO版本
自动执行所有步骤: 数据下载 → DINO检测 → 深度估计 → 3D定位 → 评估
"""

import sys
from pathlib import Path


def run_all_dino():
    """运行完整的DINO流水线"""
    
    print("="*60)
    print("DINO灯具3D定位完整流水线")
    print("="*60)
    
    steps = [
        {
            'name': '步骤1: 下载数据集',
            'module': 'step1_download_data',
            'optional': False
        },
        {
            'name': '步骤2: DINO检测测试',
            'module': 'pipeline',
            'function': 'test_pipeline',
            'optional': False
        },
        {
            'name': '步骤3: 性能评估',
            'module': 'evaluate',
            'optional': True
        },
        {
            'name': '步骤4: 实时检测Demo',
            'module': 'realtime',
            'function': 'main',
            'optional': True
        }
    ]
    
    completed_steps = []
    failed_steps = []
    
    for i, step in enumerate(steps, 1):
        print(f"\n{'='*60}")
        print(f"{step['name']}")
        print(f"{'='*60}")
        
        if step.get('optional', False):
            user_input = input(f"\n是否执行此步骤? [y/N]: ").strip().lower()
            if user_input not in ['y', 'yes']:
                print(f"⊘ 跳过: {step['name']}")
                continue
        
        try:
            # 动态导入模块
            module = __import__(step['module'])
            
            # 执行主函数或指定函数
            if 'function' in step:
                func = getattr(module, step['function'])
                func()
            else:
                if hasattr(module, 'main'):
                    module.main()
                else:
                    print(f"⚠️  模块 {step['module']} 没有main函数")
            
            completed_steps.append(step['name'])
            print(f"\n✓ 完成: {step['name']}")
            
        except KeyboardInterrupt:
            print(f"\n\n⊘ 用户中断")
            break
        
        except Exception as e:
            print(f"\n✗ 错误: {e}")
            failed_steps.append(step['name'])
            
            if not step.get('optional', False):
                print(f"\n关键步骤失败,终止流水线")
                break
            else:
                print(f"\n可选步骤失败,继续执行...")
    
    # 总结
    print("\n" + "="*60)
    print("流水线执行总结")
    print("="*60)
    
    print(f"\n✓ 完成的步骤 ({len(completed_steps)}):")
    for step in completed_steps:
        print(f"  - {step}")
    
    if failed_steps:
        print(f"\n✗ 失败的步骤 ({len(failed_steps)}):")
        for step in failed_steps:
            print(f"  - {step}")
    
    print("\n" + "="*60)
    print("流水线结束")
    print("="*60)


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="DINO灯具3D定位完整流水线")
    parser.add_argument('--auto', action='store_true', help='自动执行所有步骤(不询问)')
    
    args = parser.parse_args()
    
    if args.auto:
        # 修改所有步骤为非可选
        print("自动模式: 将执行所有步骤")
    
    run_all_dino()


if __name__ == "__main__":
    main()
