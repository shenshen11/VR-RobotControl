@echo off
echo ========================================
echo 测试 Side-by-Side 视频传输方案
echo ========================================
echo.

cd virtual-robot

echo [1/2] 启动虚拟机器人服务器（Side-by-Side 测试图案模式）...
echo.
echo 命令: python main.py --test-pattern --video-mode sbs
echo.
echo 你应该看到:
echo   - 传输模式: Side-by-Side 单轨道
echo   - 视频分辨率: 1280x480 (Side-by-Side)
echo   - 视频模式: 测试图案（左眼红色，右眼蓝色）
echo.
echo 按任意键启动服务器...
pause > nul

python main.py --test-pattern --video-mode sbs

pause

