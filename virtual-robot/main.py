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
    while True:
        robot.step_simulation()
        await asyncio.sleep(interval)


async def main(use_gui=False, fps=30, resolution=(640, 480), use_ssl=True, test_pattern=False, video_mode='sbs'):
    """
    主函数

    Args:
        use_gui: 是否显示 PyBullet GUI
        fps: 视频帧率
        resolution: 视频分辨率 (width, height)
        use_ssl: 是否使用 SSL (WSS)
        test_pattern: 是否使用测试图案（调试用）
        video_mode: 'sbs' (Side-by-Side 单轨道) 或 'dual' (双轨道)
    """
    print("🤖 Virtual Robot VR Teleoperation System")
    print(f"Server starting on port 8080...")
    print(f"Resolution: {resolution[0]}x{resolution[1]} @ {fps}fps")
    print(f"Mode: {'Side-by-Side' if video_mode == 'sbs' else 'Dual Track'}")
    if test_pattern:
        print("Test pattern mode enabled")
    print()

    # 初始化组件
    robot = VirtualRobot(use_gui=use_gui)
    camera = StereoCamera(robot, width=resolution[0], height=resolution[1], fov=90, ipd=0.064)
    webrtc_server = WebRTCServer(robot, camera, fps=fps, test_pattern=test_pattern, video_mode=video_mode)
    signaling = SignalingServer(webrtc_server)

    print("✅ Server ready")
    print("Press Ctrl+C to stop\n")

    try:
        await asyncio.gather(
            signaling.start(host='0.0.0.0', port=8080, use_ssl=use_ssl),
            simulation_loop(robot, interval=1/240)
        )
    except KeyboardInterrupt:
        print("\n\nShutting down...")
    finally:
        await webrtc_server.close()
        robot.close()
        print("✅ Server stopped")


if __name__ == '__main__':
    # 命令行参数
    parser = argparse.ArgumentParser(description='虚拟机器人 VR 遥操作系统')
    parser.add_argument('--gui', action='store_true', help='显示 PyBullet GUI（调试用）')
    parser.add_argument('--fps', type=int, default=30, help='视频帧率（默认: 30）')
    parser.add_argument('--width', type=int, default=640, help='视频宽度（默认: 640）')
    parser.add_argument('--height', type=int, default=480, help='视频高度（默认: 480）')
    parser.add_argument('--no-ssl', action='store_true', help='禁用 SSL（使用 WS 而不是 WSS）')
    parser.add_argument('--test-pattern', action='store_true', help='使用测试图案（调试立体视觉）')
    parser.add_argument('--video-mode', type=str, default='sbs', choices=['sbs', 'dual'],
                        help='视频传输模式: sbs (Side-by-Side 单轨道, 默认) 或 dual (双轨道)')

    args = parser.parse_args()

    # 运行主函数
    asyncio.run(main(
        use_gui=args.gui,
        fps=args.fps,
        resolution=(args.width, args.height),
        use_ssl=not args.no_ssl,
        test_pattern=args.test_pattern,
        video_mode=args.video_mode
    ))

