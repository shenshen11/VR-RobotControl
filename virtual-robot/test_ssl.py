"""
测试 SSL WebSocket 服务器
"""
import asyncio
import ssl
import websockets


async def test_server():
    """测试 SSL WebSocket 服务器"""
    
    print("🧪 测试 SSL WebSocket 服务器")
    print("=" * 60)
    
    # 检查证书
    import os
    if not os.path.exists('cert.pem') or not os.path.exists('key.pem'):
        print("❌ 证书文件不存在！")
        print("   请先运行: python regenerate_cert.py")
        return
    
    print("✅ 证书文件存在")
    
    # 配置 SSL
    ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    ssl_context.load_cert_chain('cert.pem', 'key.pem')
    
    print("✅ SSL 配置成功")
    
    # 简单的 echo 服务器
    async def echo(websocket):
        print(f"🔗 客户端连接: {websocket.remote_address}")
        async for message in websocket:
            print(f"📨 收到消息: {message}")
            await websocket.send(f"Echo: {message}")
    
    print("\n🚀 启动测试服务器...")
    print("   地址: wss://0.0.0.0:8080")
    print("\n📋 测试方法:")
    print("   1. 在浏览器控制台运行:")
    print("      const ws = new WebSocket('wss://localhost:8080');")
    print("      ws.onopen = () => console.log('✅ 连接成功');")
    print("      ws.onerror = (e) => console.error('❌ 连接失败', e);")
    print("      ws.onmessage = (e) => console.log('📨 收到:', e.data);")
    print("      ws.send('Hello');")
    print("\n   2. 按 Ctrl+C 停止")
    print("=" * 60)
    print()
    
    try:
        async with websockets.serve(echo, '0.0.0.0', 8080, ssl=ssl_context):
            print("✅ 服务器已启动")
            await asyncio.Future()  # 永久运行
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    try:
        asyncio.run(test_server())
    except KeyboardInterrupt:
        print("\n\n⏹️  已停止")

