"""
信令服务器模块
使用 WebSocket 处理 WebRTC 信令
"""
import asyncio
import websockets
import json
import ssl
import os


class SignalingServer:
    """
    WebSocket 信令服务器
    负责 WebRTC 的 SDP 和 ICE Candidate 交换
    """
    
    def __init__(self, webrtc_server):
        """
        Args:
            webrtc_server: WebRTCServer 实例
        """
        self.webrtc_server = webrtc_server
        self.clients = set()
        
        print(f"✅ 信令服务器初始化完成")
    
    async def handler(self, websocket):
        """
        处理 WebSocket 连接

        Args:
            websocket: WebSocket 连接
        """
        # 兼容新版本 websockets (13.0+)
        client_id = f"{websocket.remote_address[0]}:{websocket.remote_address[1]}"
        print(f"🔗 新客户端连接: {client_id}")
        
        self.clients.add(websocket)
        
        try:
            async for message in websocket:
                try:
                    data = json.loads(message)
                    msg_type = data.get('type')
                    
                    print(f"📨 收到消息: {msg_type}")
                    
                    if msg_type == 'offer':
                        # 处理 Offer，返回 Answer
                        try:
                            answer = await self.webrtc_server.handle_offer(data)
                            await websocket.send(json.dumps(answer))
                            print(f"📤 已发送 Answer")
                        except Exception as e:
                            print(f"❌ 处理 Offer 失败: {e}")
                            import traceback
                            traceback.print_exc()
                    
                    elif msg_type == 'ice-candidate':
                        # 处理 ICE Candidate
                        candidate = data.get('candidate')
                        if candidate:
                            await self.webrtc_server.add_ice_candidate(candidate)
                    
                    elif msg_type == 'ping':
                        # 心跳响应
                        await websocket.send(json.dumps({'type': 'pong'}))
                    
                    else:
                        print(f"⚠️ 未知消息类型: {msg_type}")
                
                except json.JSONDecodeError as e:
                    print(f"❌ JSON 解析错误: {e}")
                except Exception as e:
                    print(f"❌ 处理消息时出错: {e}")
        
        except websockets.exceptions.ConnectionClosed:
            print(f"🔌 客户端断开连接: {client_id}")
        
        finally:
            self.clients.remove(websocket)
    
    async def start(self, host='0.0.0.0', port=8080, use_ssl=True):
        """
        启动信令服务器

        Args:
            host: 监听地址
            port: 监听端口
            use_ssl: 是否使用 SSL (WSS)
        """
        print(f"🚀 信令服务器启动中...")

        # 配置 SSL
        ssl_context = None
        protocol = 'ws'

        if use_ssl:
            # 检查证书文件
            cert_file = 'cert.pem'
            key_file = 'key.pem'

            if os.path.exists(cert_file) and os.path.exists(key_file):
                ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
                ssl_context.load_cert_chain(cert_file, key_file)
                protocol = 'wss'
                print(f"   - SSL: 已启用 (使用 {cert_file})")
            else:
                print(f"   - SSL: 未找到证书文件，使用不安全的 WS")
                print(f"   - 提示: 运行 'python generate_cert.py' 生成证书")
                use_ssl = False

        print(f"   - 地址: {protocol}://{host}:{port}")

        async with websockets.serve(self.handler, host, port, ssl=ssl_context):
            print(f"✅ 信令服务器已启动")
            await asyncio.Future()  # 永久运行

