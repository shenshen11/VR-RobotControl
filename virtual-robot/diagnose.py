"""
系统诊断脚本
检查所有依赖和配置是否正确
"""
import sys
import subprocess


def check_python_version():
    """检查 Python 版本"""
    print("🔍 检查 Python 版本...")
    version = sys.version_info
    print(f"   Python {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("   ❌ Python 版本过低，需要 3.8+")
        return False
    else:
        print("   ✅ Python 版本符合要求")
        return True


def check_package(package_name, import_name=None):
    """检查 Python 包是否安装"""
    if import_name is None:
        import_name = package_name
    
    try:
        __import__(import_name)
        
        # 尝试获取版本
        try:
            result = subprocess.run(
                [sys.executable, '-m', 'pip', 'show', package_name],
                capture_output=True,
                text=True
            )
            for line in result.stdout.split('\n'):
                if line.startswith('Version:'):
                    version = line.split(':')[1].strip()
                    print(f"   ✅ {package_name} ({version})")
                    return True
        except:
            pass
        
        print(f"   ✅ {package_name}")
        return True
        
    except ImportError:
        print(f"   ❌ {package_name} 未安装")
        return False


def check_all_packages():
    """检查所有依赖包"""
    print("\n🔍 检查依赖包...")
    
    packages = [
        ('pybullet', 'pybullet'),
        ('aiortc', 'aiortc'),
        ('opencv-python', 'cv2'),
        ('numpy', 'numpy'),
        ('websockets', 'websockets'),
        ('av', 'av'),
        ('aiohttp', 'aiohttp'),
    ]
    
    all_ok = True
    for package_name, import_name in packages:
        if not check_package(package_name, import_name):
            all_ok = False
    
    return all_ok


def check_files():
    """检查必要的文件是否存在"""
    print("\n🔍 检查项目文件...")
    
    import os
    
    files = [
        'main.py',
        'robot_sim.py',
        'stereo_camera.py',
        'webrtc_server.py',
        'signaling_server.py',
        'requirements.txt',
    ]
    
    all_ok = True
    for filename in files:
        if os.path.exists(filename):
            print(f"   ✅ {filename}")
        else:
            print(f"   ❌ {filename} 不存在")
            all_ok = False
    
    return all_ok


def check_ports():
    """检查端口是否被占用"""
    print("\n🔍 检查端口...")
    
    import socket
    
    ports = [8080, 5173]
    
    for port in ports:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('127.0.0.1', port))
        sock.close()
        
        if result == 0:
            print(f"   ⚠️  端口 {port} 已被占用（可能服务器正在运行）")
        else:
            print(f"   ✅ 端口 {port} 可用")


def test_pybullet():
    """测试 PyBullet 是否正常工作"""
    print("\n🔍 测试 PyBullet...")
    
    try:
        import pybullet as p
        import pybullet_data
        
        # 尝试连接
        physics_client = p.connect(p.DIRECT)
        p.setAdditionalSearchPath(pybullet_data.getDataPath())
        
        # 尝试加载地面
        p.loadURDF("plane.urdf")
        
        # 断开连接
        p.disconnect()
        
        print("   ✅ PyBullet 工作正常")
        return True
        
    except Exception as e:
        print(f"   ❌ PyBullet 测试失败: {e}")
        return False


def test_aiortc():
    """测试 aiortc 是否正常工作"""
    print("\n🔍 测试 aiortc...")
    
    try:
        from aiortc import RTCPeerConnection, RTCSessionDescription, RTCIceCandidate
        
        # 创建一个 PeerConnection
        pc = RTCPeerConnection()
        
        print("   ✅ aiortc 工作正常")
        return True
        
    except Exception as e:
        print(f"   ❌ aiortc 测试失败: {e}")
        return False


def main():
    """主函数"""
    print("=" * 60)
    print("🤖 VR 虚拟机器人系统诊断")
    print("=" * 60)
    
    results = []
    
    # 检查 Python 版本
    results.append(check_python_version())
    
    # 检查依赖包
    results.append(check_all_packages())
    
    # 检查文件
    results.append(check_files())
    
    # 检查端口
    check_ports()
    
    # 测试 PyBullet
    results.append(test_pybullet())
    
    # 测试 aiortc
    results.append(test_aiortc())
    
    # 总结
    print("\n" + "=" * 60)
    if all(results):
        print("✅ 所有检查通过！系统已准备就绪！")
        print("\n下一步：")
        print("  1. 运行 'python main.py' 启动虚拟机器人服务器")
        print("  2. 在另一个终端运行 'npm run dev' 启动 VR 客户端")
        print("  3. 用 VR 头显访问 https://localhost:5173")
    else:
        print("❌ 部分检查失败，请修复上述问题")
        print("\n建议：")
        print("  1. 运行 'pip install -r requirements.txt' 安装依赖")
        print("  2. 确保在 virtual-robot 目录中运行此脚本")
        print("  3. 查看 TROUBLESHOOTING.md 获取详细帮助")
    
    print("=" * 60)
    
    return all(results)


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

