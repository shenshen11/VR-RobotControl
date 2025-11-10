@echo off
echo ========================================
echo   VR 虚拟机器人遥操作系统
echo   启动虚拟机器人服务器
echo ========================================
echo.

cd virtual-robot

echo [1/2] 检查 Python 环境...
python --version
if errorlevel 1 (
    echo 错误: 未找到 Python，请先安装 Python 3.8+
    pause
    exit /b 1
)

echo.
echo [2/2] 启动虚拟机器人服务器...
echo.
echo 提示: 按 Ctrl+C 停止服务器
echo.

python main.py

pause

