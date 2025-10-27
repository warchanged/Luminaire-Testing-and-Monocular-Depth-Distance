"""
TensorRT优化工具
为模型添加TensorRT加速支持
"""

import torch
import torch.nn as nn
import platform
from calibration import get_calibration_loader

try:
    import torch_tensorrt
    from torch_tensorrt.ptq import INT8Calibrator, DataLoaderCalibrator
except ImportError:
    pass

def is_jetson():
    """检查是否在Jetson平台上运行"""
    return "aarch64" in platform.machine()

def enable_tensorrt_optimization(model, input_shape=(1, 3, 224, 224), use_int8=False):
    """
    为PyTorch模型启用TensorRT优化
    
    参数:
        model: PyTorch模型
        input_shape: 输入形状 (batch, channels, height, width)
    
    返回:
        优化后的模型
    """
    try:
        # 检查是否支持TensorRT
        if not torch.cuda.is_available():
            print("⚠️ CUDA不可用,跳过TensorRT优化")
            return model
        
        # 方法1: 使用torch.compile (PyTorch 2.0+)
        if hasattr(torch, 'compile'):
            try:
                print("尝试使用 torch.compile 优化...")
                model = torch.compile(model, backend="inductor", mode="max-autotune")
                print("✅ torch.compile 优化成功")
                return model
            except Exception as e:
                print(f"⚠️ torch.compile 失败: {e}")
        
        # 方法2: 使用torch_tensorrt (需要安装)
        try:
            import torch_tensorrt
            print("尝试使用 torch_tensorrt 优化...")
            
            model.eval()
            with torch.no_grad():
                dummy_input = torch.randn(input_shape).cuda()
                
                # Configure INT8 calibration
                calibrator = None
                enabled_precisions = {torch.float16}
                if use_int8:
                    print("Performing INT8 calibration...")
                    calibration_loader = get_calibration_loader()
                    calibrator = DataLoaderCalibrator(
                        calibration_loader,
                        cache_file="./calibration.cache",
                        use_cache=False,
                        algo_type=torch_tensorrt.ptq.CalibrationAlgo.ENTROPY_CALIBRATION_2,
                        device=torch.device("cuda:0"),
                    )
                    enabled_precisions = {torch.int8}

                # 编译为TensorRT
                trt_model = torch_tensorrt.compile(
                    model,
                    inputs=[dummy_input],
                    enabled_precisions=enabled_precisions,
                    workspace_size=1 << 30,  # 1GB
                    calibrator=calibrator,
                )
                
                print("✅ TensorRT优化成功")
                return trt_model
                
        except ImportError:
            print("⚠️ torch_tensorrt未安装,跳过TensorRT优化")
            print("   安装命令: pip install torch-tensorrt")
        except Exception as e:
            print(f"⚠️ TensorRT优化失败: {e}")
        
        # 方法3: 基础优化 - 使用FP16
        try:
            print("应用基础优化 (FP16)...")
            model = model.half()  # 转换为FP16
            print("✅ FP16优化成功")
        except Exception as e:
            print(f"⚠️ FP16优化失败: {e}")
        
        return model
        
    except Exception as e:
        print(f"❌ 优化过程出错: {e}")
        return model


def optimize_for_inference(model):
    """
    为推理优化模型
    
    包括:
    - 切换到eval模式
    - 禁用梯度计算
    - 融合BatchNorm
    - JIT编译
    """
    try:
        # 1. Eval模式
        model.eval()
        
        # 2. 禁用梯度
        for param in model.parameters():
            param.requires_grad = False
        
        # 3. 融合BatchNorm (如果有)
        try:
            model = torch.jit.optimize_for_inference(
                torch.jit.script(model)
            )
            print("✅ JIT优化成功")
        except:
            pass
        
        return model
        
    except Exception as e:
        print(f"⚠️ 推理优化失败: {e}")
        return model


class OptimizedInference:
    """
    优化的推理包装器
    
    特性:
    - 批处理
    - 混合精度
    - 异步推理
    """
    
    def __init__(self, model, use_fp16=True):
        self.model = model
        self.use_fp16 = use_fp16
        self.device = next(model.parameters()).device
        
        if use_fp16:
            self.model = self.model.half()
    
    @torch.no_grad()
    def __call__(self, x):
        """执行优化的推理"""
        if self.use_fp16:
            x = x.half()
        
        # 使用CUDA流加速
        with torch.cuda.stream(torch.cuda.Stream()):
            output = self.model(x)
        
        return output
