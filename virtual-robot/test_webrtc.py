"""
测试 WebRTC 服务器的基本功能
"""
import asyncio
import json
from robot_sim import VirtualRobot
from stereo_camera import StereoCamera
from webrtc_server import WebRTCServer


async def test_webrtc_server():
    """测试 WebRTC 服务器初始化和基本功能"""
    
    print("🧪 开始测试 WebRTC 服务器...")
    print("=" * 60)
    
    try:
        # 1. 初始化虚拟机器人
        print("\n[1/4] 初始化虚拟机器人...")
        robot = VirtualRobot(use_gui=False)
        print("✅ 虚拟机器人初始化成功")
        
        # 2. 初始化虚拟相机
        print("\n[2/4] 初始化虚拟相机...")
        camera = StereoCamera(robot, width=320, height=240)
        print("✅ 虚拟相机初始化成功")
        
        # 3. 初始化 WebRTC 服务器
        print("\n[3/4] 初始化 WebRTC 服务器...")
        webrtc = WebRTCServer(robot, camera, fps=15)
        print("✅ WebRTC 服务器初始化成功")
        
        # 4. 测试视频渲染
        print("\n[4/4] 测试视频渲染...")
        left_img, right_img = camera.render_stereo()
        print(f"✅ 视频渲染成功")
        print(f"   - 左眼图像: {left_img.shape}")
        print(f"   - 右眼图像: {right_img.shape}")
        
        # 5. 测试控制数据接收
        print("\n[5/5] 测试控制数据接收...")
        test_control_data = {
            'timestamp': 12345,
            'headset': {
                'position': {'x': 0, 'y': 1.6, 'z': 0},
                'rotation': {'x': 0, 'y': 0, 'z': 0, 'w': 1}
            },
            'controllers': [
                {
                    'hand': 'left',
                    'position': {'x': -0.2, 'y': 1.4, 'z': -0.3},
                    'rotation': {'x': 0, 'y': 0, 'z': 0, 'w': 1},
                    'buttons': {
                        'trigger': 0.5,
                        'grip': 0.0,
                        'thumbstick': {'x': 0, 'y': 0}
                    }
                }
            ]
        }
        robot.apply_vr_control(test_control_data)
        print("✅ 控制数据接收成功")
        
        print("\n" + "=" * 60)
        print("🎉 所有测试通过！WebRTC 服务器工作正常！")
        print("\n下一步：")
        print("  1. 运行 'python main.py' 启动完整服务器")
        print("  2. 运行 'python test_connection.py' 测试信令服务器")
        print("  3. 启动 VR 客户端并连接")
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


if __name__ == "__main__":
    success = asyncio.run(test_webrtc_server())
    exit(0 if success else 1)

