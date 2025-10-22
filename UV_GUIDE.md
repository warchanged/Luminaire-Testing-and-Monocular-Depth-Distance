# UV虚拟环境管理指南

## ✅ 环境已创建完成

当前已使用 `uv` 创建并激活虚拟环境,所有依赖已安装完成。

## 🔧 虚拟环境管理命令

### 激活虚拟环境

```powershell
.venv\Scripts\activate
```

### 停用虚拟环境

```powershell
deactivate
```

### 查看已安装的包

```powershell
uv pip list
```

### 安装新包

```powershell
uv pip install <package-name>
```

### 更新包

```powershell
uv pip install --upgrade <package-name>
```

### 同步依赖(根据requirements.txt)

```powershell
uv pip sync requirements.txt
```

## 🚀 运行项目

### 测试环境

```powershell
python test_environment.py
```

### 运行完整流程

```powershell
python run_all.py
```

### 分步运行

```powershell
# 步骤1: 下载数据集
python step1_download_data.py

# 步骤2: 准备YOLO数据
python step2_prepare_yolo_data.py

# 步骤3: 训练YOLO模型
python step3_train_yolo.py

# 步骤4: 设置深度估计
python step4_setup_depth_anything.py

# 步骤5: 整合管线
python step5_integrate_pipeline.py

# 步骤6: 评估精度
python step6_evaluate.py

# 步骤7: 实时检测
python step7_realtime_detection.py
```

### 运行使用示例

```powershell
python examples.py
```

## 📦 项目信息

- **Python版本**: 3.12.10
- **虚拟环境**: .venv/
- **包管理器**: uv (快速Python包管理器)
- **已安装包**: 53个

## ⚠️ 注意事项

### GPU支持

当前安装的是CPU版本的PyTorch。如需GPU加速:

```powershell
# 先卸载CPU版本
uv pip uninstall torch torchvision

# 安装CUDA版本(根据你的CUDA版本选择)
uv pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
```

### Kaggle配置

在运行步骤1之前,需要配置Kaggle凭证:

1. 访问: <https://www.kaggle.com/settings>
2. 点击 "Create New Token"
3. 下载 `kaggle.json`
4. 放到: `C:\Users\19395\.kaggle\kaggle.json`

## 🎯 环境测试结果

✅ **所有测试通过!**

- ✓ 导入测试 - 11/11 包成功
- ✓ PyTorch测试 - 张量操作正常
- ✓ YOLO测试 - Ultralytics已安装
- ✓ Transformers测试 - 深度估计模型可用
- ✓ OpenCV测试 - 图像处理正常
- ✓ 项目结构 - 所有文件完整

## 📝 下一步

### 1. 快速测试(推荐)

```powershell
# 先用少量数据快速测试
# 编辑 step3_train_yolo.py, 设置 epochs=5
# 编辑 step6_evaluate.py, 设置 num_samples=5
python run_all.py --quick
```

### 2. 完整运行

```powershell
# 配置好Kaggle后
python run_all.py
```

### 3. 查看结果

```powershell
# 训练结果
ls models/light_detection/weights/

# 3D定位结果
ls results/3d_localization/

# 评估报告
cat results/evaluation/evaluation_results.json
```

## 💡 提示

- 使用 `uv` 比 `pip` 快10-100倍
- 虚拟环境隔离了项目依赖,不影响系统Python
- 首次运行会下载约3GB数据和模型,请确保网络畅通
- CPU训练较慢,建议使用GPU或减少训练轮数

## 🔗 相关文档

- `README.md` - 完整技术文档
- `QUICKSTART.md` - 快速开始指南
- `PROJECT_COMPLETE.md` - 项目完成说明
- `config.yaml` - 配置参数

---

**环境状态**: ✅ 已就绪
**最后测试**: 2025年10月21日
**Python**: 3.12.10
**虚拟环境**: .venv (uv)
