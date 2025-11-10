@echo off
echo ========================================
echo   VR 虚拟机器人遥操作系统
echo   启动 VR 客户端
echo ========================================
echo.

echo [1/2] 检查 Node.js 环境...
node --version
if errorlevel 1 (
    echo 错误: 未找到 Node.js，请先安装 Node.js
    pause
    exit /b 1
)

echo.
echo [2/2] 启动 VR 客户端开发服务器...
echo.
echo 提示: 
echo   - 服务器启动后，用 VR 头显访问 https://localhost:5173
echo   - 按 Ctrl+C 停止服务器
echo.

npm run dev

pause

