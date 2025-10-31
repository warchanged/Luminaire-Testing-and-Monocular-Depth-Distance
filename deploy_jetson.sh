#!/bin/bash

# Jetson Docker 部署脚本

echo "=========================================="
echo "  Jetson AGX Orin Docker 部署"
echo "=========================================="
echo ""

# 检查 Docker 和 NVIDIA runtime
check_requirements() {
    echo "检查环境..."
    
    if ! command -v docker &> /dev/null; then
        echo "❌ Docker 未安装"
        echo "安装: curl https://get.docker.com | sh"
        exit 1
    fi
    
    if ! docker info | grep -i "nvidia" &> /dev/null; then
        echo "❌ NVIDIA Docker runtime 未配置"
        echo "安装: sudo apt-get install nvidia-docker2"
        exit 1
    fi
    
    echo "✅ 环境检查通过"
}

# 构建 Docker 镜像
build_image() {
    echo ""
    echo "构建 Docker 镜像..."
    docker build -f Dockerfile.jetson -t luminaire-detection:jetson-orin .
    
    if [ $? -eq 0 ]; then
        echo "✅ 镜像构建成功"
    else
        echo "❌ 镜像构建失败"
        exit 1
    fi
}

# 启动容器
start_container() {
    echo ""
    echo "启动容器..."
    
    # 创建必要的目录
    mkdir -p ./models ./results ./cache
    
    # 使用 docker-compose
    if command -v docker-compose &> /dev/null; then
        docker-compose -f docker-compose.jetson.yml up -d
    else
        # 手动启动
        docker run -d \
            --name luminaire-detection \
            --runtime=nvidia \
            --gpus all \
            -p 7860:7860 \
            -v $(pwd)/models:/app/models \
            -v $(pwd)/results:/app/results \
            -v $(pwd)/cache:/app/.cache \
            --device /dev/video0:/dev/video0 \
            --restart unless-stopped \
            luminaire-detection:jetson-orin
    fi
    
    if [ $? -eq 0 ]; then
        echo "✅ 容器启动成功"
        echo ""
        echo "访问 Gradio UI: http://$(hostname -I | awk '{print $1}'):7860"
    else
        echo "❌ 容器启动失败"
        exit 1
    fi
}

# 查看日志
show_logs() {
    echo ""
    echo "查看容器日志..."
    docker logs -f luminaire-detection
}

# 主菜单
main() {
    check_requirements
    
    echo ""
    echo "选择操作:"
    echo "1) 构建镜像"
    echo "2) 启动容器"
    echo "3) 构建并启动"
    echo "4) 查看日志"
    echo "5) 停止容器"
    echo "6) 重启容器"
    read -p "请选择 [1-6]: " choice
    
    case $choice in
        1)
            build_image
            ;;
        2)
            start_container
            ;;
        3)
            build_image
            start_container
            ;;
        4)
            show_logs
            ;;
        5)
            docker stop luminaire-detection
            echo "✅ 容器已停止"
            ;;
        6)
            docker restart luminaire-detection
            echo "✅ 容器已重启"
            ;;
        *)
            echo "无效选择"
            exit 1
            ;;
    esac
}

# 如果提供了参数,直接执行
if [ "$1" == "build" ]; then
    build_image
elif [ "$1" == "start" ]; then
    start_container
elif [ "$1" == "logs" ]; then
    show_logs
elif [ "$1" == "stop" ]; then
    docker stop luminaire-detection
elif [ "$1" == "restart" ]; then
    docker restart luminaire-detection
else
    main
fi
