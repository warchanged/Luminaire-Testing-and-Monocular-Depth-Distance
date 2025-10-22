"""
步骤1: 下载NYU-Depth-v2数据集
使用kagglehub下载数据集并探索其结构
"""

import kagglehub
import os
import h5py
import numpy as np
from pathlib import Path
import shutil

def download_nyu_depth_v2():
    """下载NYU-Depth-v2数据集"""
    print("开始下载NYU-Depth-v2数据集...")
    path = kagglehub.dataset_download("soumikrakshit/nyu-depth-v2")
    print(f"数据集已下载到: {path}")
    return path

def explore_dataset(dataset_path):
    """探索数据集结构"""
    print("\n" + "="*50)
    print("探索数据集结构...")
    print("="*50)
    
    dataset_path = Path(dataset_path)
    
    # 列出所有文件
    print("\n数据集文件:")
    for file in dataset_path.rglob("*"):
        if file.is_file():
            size_mb = file.stat().st_size / (1024 * 1024)
            print(f"  {file.name} ({size_mb:.2f} MB)")
    
    # 检查是否存在HDF5文件
    h5_files = list(dataset_path.rglob("*.h5"))
    if h5_files:
        print(f"\n找到 {len(h5_files)} 个HDF5文件")
        for h5_file in h5_files:
            print(f"\n分析 {h5_file.name}:")
            try:
                with h5py.File(h5_file, 'r') as f:
                    print(f"  包含的数据集:")
                    def print_structure(name, obj):
                        if isinstance(obj, h5py.Dataset):
                            print(f"    - {name}: shape={obj.shape}, dtype={obj.dtype}")
                    f.visititems(print_structure)
            except Exception as e:
                print(f"  无法读取文件: {e}")
    
    # 检查图像文件
    image_exts = ['.jpg', '.jpeg', '.png', '.bmp']
    image_files = [f for f in dataset_path.rglob("*") if f.suffix.lower() in image_exts]
    if image_files:
        print(f"\n找到 {len(image_files)} 个图像文件")
        print(f"  示例: {image_files[0].name if image_files else 'None'}")

def copy_dataset_to_project(dataset_path, project_dir="data"):
    """将数据集复制到项目目录"""
    print("\n" + "="*50)
    print("复制数据集到项目目录...")
    print("="*50)
    
    project_data_dir = Path(project_dir)
    project_data_dir.mkdir(parents=True, exist_ok=True)
    
    dataset_path = Path(dataset_path)
    
    # 复制所有文件
    for file in dataset_path.rglob("*"):
        if file.is_file():
            relative_path = file.relative_to(dataset_path)
            dest_file = project_data_dir / relative_path
            dest_file.parent.mkdir(parents=True, exist_ok=True)
            
            if not dest_file.exists():
                print(f"  复制: {relative_path}")
                shutil.copy2(file, dest_file)
            else:
                print(f"  跳过(已存在): {relative_path}")
    
    print(f"\n数据集已复制到: {project_data_dir.absolute()}")
    return project_data_dir

def main():
    try:
        # 下载数据集
        dataset_path = download_nyu_depth_v2()
        
        # 探索数据集
        explore_dataset(dataset_path)
        
        # 复制到项目目录
        project_data_dir = copy_dataset_to_project(dataset_path)
        
        print("\n" + "="*50)
        print("✓ 步骤1完成!")
        print("="*50)
        print(f"数据集位置: {project_data_dir.absolute()}")
        print("\n下一步: 运行 step2_prepare_yolo_data.py 准备YOLO训练数据")
        
    except Exception as e:
        print(f"\n✗ 错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
