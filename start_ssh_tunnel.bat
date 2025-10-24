@echo off
echo ========================================
echo     Gradio SSH 端口转发启动器
echo ========================================
echo.
echo 正在创建SSH隧道...
echo 本地端口: 7860
echo 远程服务器: 52.18.175.128:7860
echo.
echo 保持此窗口打开!
echo 关闭窗口将断开连接
echo.
echo 浏览器访问: http://localhost:7860
echo.
echo ========================================
echo.

ssh -i "C:\Users\19395\Downloads\haoyu.pem" -L 7860:localhost:7860 haoyu@52.18.175.128 -N

pause
