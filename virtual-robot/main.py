"""
虚拟机器人主入口
整合所有模块，启动服务
"""
import asyncio
import argparse
from robot_sim import VirtualRobot
from stereo_camera import StereoCamera
from webrtc_server import WebRTCServer
from signaling_server import SignalingServer


async def simulation_loop(robot, interval=1/240):
    """
    物理仿真循环
    
    Args:
        robot: VirtualRobot 实例
        interval: 仿真步长（秒），默认 240Hz
    """
    print(f"🔄 物理仿真循环启动 ({1/interval:.0f} Hz)")
    
    while True:
        robot.step_simulation()
        await asyncio.sleep(interval)


async def main(use_gui=False, fps=30, resolution=(640, 480), use_ssl=True, test_pattern=False):
    """
    主函数

    Args:
        use_gui: 是否显示 PyBullet GUI
        fps: 视频帧率
        resolution: 视频分辨率 (width, height)
        use_ssl: 是否使用 SSL (WSS)
        test_pattern: 是否使用测试图案（调试用）
    """
    print("=" * 60)
    print("🤖 虚拟机器人 VR 遥操作系统")
    if test_pattern:
        print("🎨 测试图案模式 - 用于调试立体视觉")
    print("=" * 60)

    # 1. 初始化虚拟机器人
    print("\n[1/5] 初始化虚拟机器人...")
    robot = VirtualRobot(use_gui=use_gui)

    # 2. 初始化虚拟双目相机
    print("\n[2/5] 初始化虚拟双目相机...")
    camera = StereoCamera(
        robot,
        width=resolution[0],
        height=resolution[1],
        fov=90,
        ipd=0.064
    )

    # 3. 初始化 WebRTC 服务器
    print("\n[3/5] 初始化 WebRTC 服务器...")
    webrtc_server = WebRTCServer(robot, camera, fps=fps, test_pattern=test_pattern)
    
    # 4. 初始化信令服务器
    print("\n[4/5] 初始化信令服务器...")
    signaling = SignalingServer(webrtc_server)
    
    # 5. 启动所有服务
    print("\n[5/5] 启动所有服务...")
    print("=" * 60)
    print("✅ 系统启动成功！")
    print("=" * 60)
    print("\n📋 使用说明:")
    print("  1. 在另一个终端启动 VR 客户端:")
    print("     cd client")
    print("     npm run dev")
    print("  2. 用 VR 头显访问: https://localhost:5173")
    print("  3. 在 VR 中移动头部和手柄，观察控制台输出")
    print("\n💡 提示:")
    print(f"  - 视频分辨率: {resolution[0]}x{resolution[1]}")
    print(f"  - 视频帧率: {fps} fps")
    print(f"  - 物理仿真: 240 Hz")
    print(f"  - PyBullet GUI: {'开启' if use_gui else '关闭'}")
    print(f"  - 视频模式: {'测试图案（左眼红色，右眼蓝色）' if test_pattern else '真实场景'}")
    if test_pattern:
        print("\n🎨 测试图案说明:")
        print("  - 左眼应该看到红色背景 + 'LEFT EYE' 文字")
        print("  - 右眼应该看到蓝色背景 + 'RIGHT EYE' 文字")
        print("  - 如果看到这个，说明立体渲染工作正常")
    print("\n按 Ctrl+C 停止服务")
    print("=" * 60)
    print()
    
    try:
        # 并发运行信令服务器和物理仿真
        await asyncio.gather(
            signaling.start(host='0.0.0.0', port=8080, use_ssl=use_ssl),
            simulation_loop(robot, interval=1/240)
        )
    except KeyboardInterrupt:
        print("\n\n⏹️  收到停止信号，正在关闭...")
    finally:
        # 清理资源
        await webrtc_server.close()
        robot.close()
        print("✅ 系统已安全关闭")


if __name__ == '__main__':
    # 命令行参数
    parser = argparse.ArgumentParser(description='虚拟机器人 VR 遥操作系统')
    parser.add_argument('--gui', action='store_true', help='显示 PyBullet GUI（调试用）')
    parser.add_argument('--fps', type=int, default=30, help='视频帧率（默认: 30）')
    parser.add_argument('--width', type=int, default=640, help='视频宽度（默认: 640）')
    parser.add_argument('--height', type=int, default=480, help='视频高度（默认: 480）')
    parser.add_argument('--no-ssl', action='store_true', help='禁用 SSL（使用 WS 而不是 WSS）')
    parser.add_argument('--test-pattern', action='store_true', help='使用测试图案（调试立体视觉）')

    args = parser.parse_args()

    # 运行主函数
    asyncio.run(main(
        use_gui=args.gui,
        fps=args.fps,
        resolution=(args.width, args.height),
        use_ssl=not args.no_ssl,
        test_pattern=args.test_pattern
    ))

