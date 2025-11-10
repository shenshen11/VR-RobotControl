"""
测试脚本：验证信令服务器是否正常工作
"""
import asyncio
import websockets
import json


async def test_signaling_server():
    """测试信令服务器连接"""
    uri = "ws://localhost:8080"
    
    print("🧪 开始测试信令服务器...")
    print(f"📡 连接到: {uri}")
    
    try:
        async with websockets.connect(uri) as websocket:
            print("✅ WebSocket 连接成功！")
            
            # 测试 ping
            print("\n📤 发送 ping...")
            await websocket.send(json.dumps({'type': 'ping'}))
            
            response = await websocket.recv()
            data = json.loads(response)
            
            if data.get('type') == 'pong':
                print("✅ 收到 pong 响应！")
                print("\n🎉 信令服务器工作正常！")
            else:
                print(f"⚠️ 收到意外响应: {data}")
    
    except ConnectionRefusedError:
        print("❌ 连接被拒绝！请确保虚拟机器人服务器正在运行。")
        print("   运行命令: python main.py")
    
    except Exception as e:
        print(f"❌ 测试失败: {e}")


if __name__ == "__main__":
    asyncio.run(test_signaling_server())

