# 🔦 灯具3D定位检测系统 - 完整部署指南

> 基于 OWLv2 + DINOv2 + Depth Anything V2 的智能灯具检测与3D定位系统

---

## 📋 目录

1. [系统架构](#系统架构)
2. [快速启动](#快速启动)
3. [服务器部署](#服务器部署)
4. [Gradio Web UI](#gradio-web-ui)
5. [使用说明](#使用说明)
6. [性能优化](#性能优化)
7. [常见问题](#常见问题)
8. [技术支持](#技术支持)

---

## 🏗️ 系统架构

```
┌─────────────────┐          ┌──────────────────────────┐
│  本地电脑        │          │   远程服务器 (4x A10G)    │
│                 │          │                          │
│  摄像头 📹      │  HTTP    │   Gradio Web UI          │
│  浏览器 🌐      │◄────────►│   ├─ OWLv2 检测          │
│                 │  7860    │   ├─ DINOv2 特征         │
│  webcam_client  │          │   └─ DepthAnything 深度  │
│  .html          │          │                          │
└─────────────────┘          │   GPU 1 (23GB)           │
                             └──────────────────────────┘
```

### 技术栈

| 组件 | 模型 | 参数量 | 用途 |
|------|------|--------|------|
| **检测器** | OWLv2-Large | 1.1B | 零样本目标检测 |
| **特征提取** | DINOv2-Large | 304M | 自监督视觉特征 |
| **深度估计** | Depth Anything V2 | 335M | 单目深度估计 |

### 硬件要求

- **GPU**: NVIDIA A10G (23GB) 或同等算力
- **显存**: 最低10GB,推荐16GB+
- **磁盘**: 10GB+ (模型缓存)
- **网络**: 稳定网络连接(首次下载模型)

---

## 🚀 快速启动

### 方法1: 一键启动脚本

在服务器上执行:

```bash
# SSH连接服务器
ssh -i haoyu.pem haoyu@52.18.175.128

# 进入项目目录
cd /mnt/ai/luminaire-detection

# 一键启动Gradio服务
chmod +x start_gradio.sh && ./start_gradio.sh
```

### 方法2: 手动启动

```bash
# 1. 进入项目目录
cd /mnt/ai/luminaire-detection

# 2. 激活虚拟环境
source venv/bin/activate

# 3. 设置环境变量
export CUDA_VISIBLE_DEVICES=1
export HF_HOME="/mnt/ai/huggingface_cache"
export TRANSFORMERS_CACHE="/mnt/ai/huggingface_cache"

# 4. 安装Gradio依赖
pip install gradio matplotlib

# 5. 启动应用
python gradio_app.py
```

### 启动成功标志

```
🚀 启动Gradio Web UI...
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📍 本地访问: http://localhost:7860
🌐 远程访问: http://52.18.175.128:7860
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Running on local URL:  http://0.0.0.0:7860
```

---

## 🖥️ 服务器部署

### 步骤1: 克隆项目

```bash
# 使用HTTPS克隆(推荐)
cd /mnt/ai
git clone https://github.com/warchanged/Luminaire-Testing-and-Monocular-Depth-Distance.git
cd Luminaire-Testing-and-Monocular-Depth-Distance
```

### 步骤2: 创建Python环境

```bash
# 使用Python 3.10(重要!)
python3.10 -m venv venv
source venv/bin/activate

# 验证Python版本
python --version  # 应该显示 Python 3.10.x
```

### 步骤3: 安装依赖

```bash
# 升级pip
pip install --upgrade pip

# 安装PyTorch (CUDA 12.1)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# 安装其他依赖
pip install transformers opencv-python pillow numpy pandas matplotlib tqdm pyyaml gradio
```

### 步骤4: 配置HuggingFace

```bash
# 设置缓存路径(避免占用根分区)
export HF_HOME="/mnt/ai/huggingface_cache"
export TRANSFORMERS_CACHE="/mnt/ai/huggingface_cache"

# 写入.bashrc永久生效
echo 'export HF_HOME="/mnt/ai/huggingface_cache"' >> ~/.bashrc
echo 'export TRANSFORMERS_CACHE="/mnt/ai/huggingface_cache"' >> ~/.bashrc
```

### 步骤5: 配置DINOv2访问令牌

DINOv2模型需要HuggingFace访问令牌:

```bash
# 安装huggingface-cli
pip install huggingface-hub

# 登录(需要从 https://huggingface.co/settings/tokens 获取令牌)
huggingface-cli login

# 或直接设置环境变量
export HF_TOKEN="your_token_here"
echo 'export HF_TOKEN="your_token_here"' >> ~/.bashrc
```

---

## 🌐 Gradio Web UI

### 界面功能

#### 1. 📸 图像检测模式

**特点**:

- 上传单张图片进行完整分析
- 显示深度图可视化
- 计算每个灯具的3D距离
- 详细检测统计和结果

**使用场景**:

- 离线图片分析
- 详细报告生成
- 深度信息需求

**性能**: 1-2秒/张

#### 2. 🎥 实时检测模式

**特点**:

- 摄像头流式处理
- 实时边界框绘制
- FPS实时显示
- 检测数量统计

**使用场景**:

- 现场勘查
- 动态监控
- 实时演示

**性能**: 1-3 FPS

#### 3. ℹ️ 系统信息

查看:

- 技术架构说明
- 支持的灯具类型(30+种)
- 性能指标
- 项目链接

### 访问方式

#### 选项A: 直接使用Gradio界面 (推荐)

1. 打开浏览器: `http://52.18.175.128:7860`
2. 选择"🎥 实时检测"标签
3. 点击"启动摄像头"
4. 授权浏览器使用摄像头
5. 实时检测开始!

#### 选项B: 使用自定义HTML客户端

1. 双击打开 `webcam_client.html`
2. 确认服务器地址: `http://52.18.175.128:7860`
3. 点击"📹 启动摄像头"
4. 查看实时统计(FPS、延迟、检测数)

---

## 📖 使用说明

### 支持的灯具类型

```
✅ 吊灯类: chandelier, pendant light, hanging lamp
✅ 吸顶灯: ceiling light, flush mount, recessed light
✅ 壁灯: wall lamp, wall sconce, picture light
✅ 台灯: table lamp, desk lamp, reading lamp
✅ 落地灯: floor lamp, standing lamp
✅ 射灯: spotlight, track light, accent light
✅ 筒灯: downlight, can light, pot light
✅ LED灯: LED panel, LED strip, LED bulb
✅ 荧光灯: fluorescent light, tube light
✅ 灯串: string lights, fairy lights
... 共30+种类型
```

### 参数调整

#### 置信度阈值 (Confidence Threshold)

- **范围**: 0.05 - 0.5
- **推荐值**: 0.15
- **效果**:
  - 低值(0.05-0.10): 检测更多目标,可能有误报
  - 中值(0.15-0.20): 平衡精度和召回率 ✅
  - 高值(0.25-0.50): 只保留高置信度检测,减少误报

#### 深度图显示

- **图像模式**: 可开启(显示完整深度图)
- **实时模式**: 默认关闭(提高帧率)
- **用途**: 可视化场景深度信息

### 操作流程

#### 图像检测流程

1. 点击"📸 图像检测"标签
2. 上传图片(支持JPG/PNG)
3. 调整置信度阈值(可选)
4. 勾选"显示深度图"(可选)
5. 点击"🔍 开始检测"
6. 查看结果:
   - 左侧: 检测框标注
   - 右侧: 深度图可视化
   - 下方: 详细统计信息

#### 实时检测流程

1. 点击"🎥 实时检测"标签
2. 点击"启动摄像头"
3. 授权浏览器摄像头权限
4. 调整置信度阈值(实时生效)
5. 查看实时检测结果
6. 监控FPS和检测数量

---

## ⚡ 性能优化

### 服务器端优化

#### 1. 降低分辨率

编辑 `gradio_app.py`:

```python
# 调整输入图像大小
input_image = gr.Image(
    label="上传图像", 
    type="numpy",
    height=480  # 降低到480p
)
```

#### 2. 禁用深度估计

```python
# 在 process_video_frame 函数中
result = pipe.process_image(
    frame,
    confidence_threshold=confidence_threshold,
    compute_depth=False,      # 关闭深度计算
    compute_distance=False    # 关闭距离计算
)
```

#### 3. 使用更小的模型

编辑 `pipeline.py`:

```python
# 使用Base模型代替Large
pipeline = LightLocalization3D(
    detection_model="google/owlv2-base-patch16-ensemble",  # Large → Base
    feature_model="facebook/dinov2-base",                  # Large → Base
    depth_model="depth-anything/Depth-Anything-V2-Base-hf" # Large → Base
)
```

### 客户端优化

#### 降低摄像头分辨率

编辑 `webcam_client.html`:

```javascript
const stream = await navigator.mediaDevices.getUserMedia({ 
    video: { 
        width: 640,   // 1280 → 640
        height: 480,  // 720 → 480
        facingMode: 'user'
    } 
});
```

#### 降低发送频率

```javascript
// 添加帧跳过逻辑
let frameSkip = 2;  // 每2帧处理1帧
let frameCount = 0;

async function detectLoop() {
    frameCount++;
    if (frameCount % frameSkip !== 0) {
        animationId = requestAnimationFrame(detectLoop);
        return;
    }
    // ... 处理逻辑
}
```

### 性能对比

| 配置 | 分辨率 | 模型大小 | FPS | 显存占用 |
|------|--------|----------|-----|----------|
| 高质量 | 1280x720 | Large | 1-2 | 12GB |
| 标准 | 640x480 | Large | 2-3 | 10GB |
| 快速 | 640x480 | Base | 3-5 | 6GB |

---

## 🔧 常见问题

### Q1: 无法访问7860端口

**症状**: 浏览器无法连接到 `http://52.18.175.128:7860`

**解决方案**:

```bash
# 方案1: 检查防火墙
sudo ufw status
sudo ufw allow 7860

# 方案2: 使用SSH隧道
ssh -i haoyu.pem -L 7860:localhost:7860 haoyu@52.18.175.128
# 然后访问 http://localhost:7860

# 方案3: 检查Gradio是否运行
ps aux | grep gradio
netstat -tulnp | grep 7860
```

### Q2: 摄像头权限被拒绝

**症状**: 浏览器显示"摄像头权限被拒绝"

**解决方案**:

- **Chrome/Edge**:
  1. 点击地址栏左侧的锁/摄像头图标
  2. 网站设置 → 摄像头 → 允许
  3. 刷新页面

- **Firefox**:
  1. 点击地址栏左侧的锁图标
  2. 连接安全 → 更多信息
  3. 权限 → 摄像头 → 允许

- **Safari**:
  1. Safari → 网站设置 → 摄像头
  2. 允许该网站访问摄像头

### Q3: FPS太低 (< 1)

**症状**: 实时检测帧率非常低

**诊断**:

```bash
# 检查GPU使用情况
nvidia-smi

# 检查GPU 1是否被占用
nvidia-smi | grep "GPU 1"

# 查看进程
ps aux | grep python
```

**解决方案**:

1. 确保使用GPU 1: `export CUDA_VISIBLE_DEVICES=1`
2. 降低分辨率到640x480
3. 关闭深度估计
4. 提高置信度阈值(减少检测数量)
5. 使用Base模型

### Q4: 内存不足 (CUDA out of memory)

**症状**:

```
RuntimeError: CUDA out of memory. Tried to allocate XX GB
```

**解决方案**:

```bash
# 1. 清理GPU显存
pkill -9 python
nvidia-smi

# 2. 使用更小的模型
# 编辑 pipeline.py, 使用 Base 模型

# 3. 减小批处理大小
# 编辑 gradio_app.py, 降低输入分辨率
```

### Q5: 模型下载失败

**症状**:

```
HTTPError: 401 Client Error: Unauthorized
OSError: Can't load model
```

**解决方案**:

```bash
# 1. 检查网络连接
ping huggingface.co

# 2. 配置HuggingFace令牌(DINOv2需要)
huggingface-cli login

# 3. 使用镜像站(国内)
export HF_ENDPOINT=https://hf-mirror.com

# 4. 手动下载模型
# 访问 https://huggingface.co 下载模型文件
# 放置到 /mnt/ai/huggingface_cache
```

### Q6: Python _lzma 模块错误

**症状**:

```
ModuleNotFoundError: No module named '_lzma'
```

**解决方案**:

```bash
# 使用Python 3.10 (不要用3.11)
python3.10 -m venv venv
source venv/bin/activate
python --version  # 确认是 3.10.x

# 重新安装依赖
pip install torch transformers opencv-python gradio
```

---

## 🔒 安全建议

### 生产环境部署

#### 1. 添加认证

编辑 `gradio_app.py`:

```python
demo.launch(
    server_name="0.0.0.0",
    server_port=7860,
    auth=("admin", "your_secure_password"),  # 添加用户名密码
    auth_message="请登录以使用灯具检测系统"
)
```

#### 2. 使用HTTPS

```bash
# 生成自签名证书
openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes

# 启动时指定证书
demo.launch(
    ssl_certfile="cert.pem",
    ssl_keyfile="key.pem"
)
```

#### 3. Nginx反向代理

```bash
# 安装Nginx
sudo apt install nginx

# 配置反向代理
sudo nano /etc/nginx/sites-available/gradio
```

```nginx
server {
    listen 80;
    server_name yourdomain.com;

    location / {
        proxy_pass http://localhost:7860;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket支持
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

#### 4. 防火墙配置

```bash
# 只允许特定IP访问
sudo ufw allow from YOUR_IP to any port 7860

# 或使用IP白名单
sudo ufw deny 7860
sudo ufw allow from 192.168.1.0/24 to any port 7860
```

---

## 📊 监控与日志

### 实时监控

```bash
# GPU监控
watch -n 1 nvidia-smi

# 进程监控
htop

# 网络监控
iftop
```

### 日志记录

编辑 `gradio_app.py` 添加日志:

```python
import logging

# 配置日志
logging.basicConfig(
    filename='/mnt/ai/luminaire-detection/gradio.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# 在处理函数中记录
def process_image(image, confidence_threshold, show_depth):
    logging.info(f"Processing image with threshold: {confidence_threshold}")
    # ... 处理逻辑
    logging.info(f"Detected {len(detections)} objects")
```

### 查看日志

```bash
# 实时查看
tail -f /mnt/ai/luminaire-detection/gradio.log

# 查看错误
grep ERROR /mnt/ai/luminaire-detection/gradio.log

# 查看最近100行
tail -n 100 /mnt/ai/luminaire-detection/gradio.log
```

---

## 📱 移动端使用

### Android/iOS浏览器

1. 确保手机和服务器在同一网络
2. 打开Chrome/Safari浏览器
3. 访问 `http://52.18.175.128:7860`
4. 选择"🎥 实时检测"
5. 授权摄像头权限
6. 使用后置摄像头获得更好效果

### 移动端优化

```python
# 针对移动端优化的配置
with gr.Blocks(theme=gr.themes.Soft()) as demo:
    gr.Markdown("""
    # 灯具检测
    移动端请使用后置摄像头
    """)
    
    # 降低分辨率
    webcam_input = gr.Image(
        source="webcam", 
        streaming=True,
        height=360  # 移动端使用更低分辨率
    )
```

---

## 🎨 自定义界面

### 修改主题

```python
# 可选主题: Soft, Glass, Monochrome, Base
demo = gr.Blocks(
    title="灯具检测系统",
    theme=gr.themes.Glass()  # 玻璃主题
)
```

### 添加自定义CSS

```python
custom_css = """
.gradio-container {
    max-width: 1200px;
    margin: auto;
}
.stat-card {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    padding: 20px;
    border-radius: 10px;
    color: white;
}
"""

demo = gr.Blocks(css=custom_css)
```

### 多语言支持

```python
# 中英文切换
languages = {
    "zh": {
        "title": "灯具检测系统",
        "upload": "上传图像",
        "detect": "开始检测"
    },
    "en": {
        "title": "Luminaire Detection System",
        "upload": "Upload Image",
        "detect": "Start Detection"
    }
}
```

---

## 🎯 最佳实践

### 1. 首次启动

- 等待模型下载完成(约5-10分钟)
- 检查GPU显存充足(10GB+)
- 确保网络稳定

### 2. 测试流程

```bash
# 1. 先测试静态图片
# 上传一张图片,确认模型加载成功

# 2. 再测试实时检测
# 启动摄像头,观察FPS

# 3. 调整参数优化
# 根据实际效果调整置信度阈值
```

### 3. 性能调优

- 根据需求选择模型大小(Base/Large)
- 实时模式关闭深度估计
- 调整分辨率平衡速度和质量
- 使用GPU 1独占运行

### 4. 稳定运行

```bash
# 使用tmux保持会话
tmux new -s gradio
./start_gradio.sh
# Ctrl+B, D 分离会话

# 重新连接
tmux attach -t gradio
```

### 5. 定期维护

```bash
# 清理缓存
rm -rf /mnt/ai/huggingface_cache/downloads/*.tmp

# 更新依赖
pip install --upgrade transformers gradio

# 备份配置
cp gradio_app.py gradio_app.py.bak
```

---

## 📈 性能指标

### 检测性能

| 指标 | 值 |
|------|---|
| 检测精度 | 90%+ (室内场景) |
| 处理速度 | 1-3 FPS (Large模型, GPU) |
| 深度精度 | ±0.3m (2-5m距离) |
| 支持类型 | 30+ 种灯具 |

### 系统资源

| 资源 | 占用 |
|------|------|
| GPU显存 | 8-12GB (Large模型) |
| CPU | 2-4核 |
| 内存 | 4-8GB |
| 磁盘 | 10GB+ (模型缓存) |

### 模型对比

| 模型 | 参数量 | 速度 | 精度 | 显存 |
|------|--------|------|------|------|
| Base | 86M+85M+97M | 快 | 良好 | 6GB |
| Large | 1.1B+304M+335M | 中等 | 优秀 | 12GB |

---

## 🆘 技术支持

### 获取帮助

- **GitHub Issues**: [提交问题](https://github.com/warchanged/Luminaire-Testing-and-Monocular-Depth-Distance/issues)
- **文档**: 查看项目README和Wiki
- **日志**: 提供详细的错误日志

### 问题报告模板

```markdown
**环境信息**:
- GPU型号: 
- CUDA版本: 
- Python版本: 
- 依赖版本: `pip list`

**问题描述**:


**复现步骤**:
1. 
2. 
3. 

**错误日志**:
```

粘贴错误信息

```

**期望行为**:

```

### 有用的命令

```bash
# 系统信息
nvidia-smi
python --version
pip list

# 检查服务
ps aux | grep gradio
netstat -tulnp | grep 7860

# 查看日志
journalctl -u gradio -f
tail -f /mnt/ai/luminaire-detection/gradio.log

# 重启服务
pkill -9 -f gradio_app.py
./start_gradio.sh
```

---

## 📚 相关链接

- **项目主页**: [GitHub Repository](https://github.com/warchanged/Luminaire-Testing-and-Monocular-Depth-Distance)
- **模型文档**:
  - [OWLv2](https://huggingface.co/google/owlv2-large-patch14-ensemble)
  - [DINOv2](https://huggingface.co/facebook/dinov2-large)
  - [Depth Anything V2](https://huggingface.co/depth-anything/Depth-Anything-V2-Large-hf)
- **Gradio文档**: [gradio.app](https://www.gradio.app/)
- **HuggingFace**: [huggingface.co](https://huggingface.co/)

---

## 📝 更新日志

### v1.0.0 (2025-10-24)

- ✅ 初始版本发布
- ✅ Gradio Web UI
- ✅ 实时摄像头检测
- ✅ 图像上传分析
- ✅ 深度图可视化
- ✅ 支持30+种灯具类型
- ✅ GPU加速(CUDA 12.1)
- ✅ 完整部署文档

---

**祝您使用愉快!** 🎉

如有问题,请随时联系技术支持。
