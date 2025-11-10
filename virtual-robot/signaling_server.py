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
    
    async def handler(self, websocket):
        """
        处理 WebSocket 连接

        Args:
            websocket: WebSocket 连接
        """
        self.clients.add(websocket)

        try:
            async for message in websocket:
                try:
                    data = json.loads(message)
                    msg_type = data.get('type')

                    if msg_type == 'offer':
                        answer = await self.webrtc_server.handle_offer(data)
                        await websocket.send(json.dumps(answer))

                    elif msg_type == 'ice-candidate':
                        candidate = data.get('candidate')
                        if candidate:
                            await self.webrtc_server.add_ice_candidate(candidate)

                    elif msg_type == 'ping':
                        await websocket.send(json.dumps({'type': 'pong'}))

                except:
                    pass

        except websockets.exceptions.ConnectionClosed:
            pass

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
        ssl_context = None

        if use_ssl:
            cert_file = 'cert.pem'
            key_file = 'key.pem'

            if os.path.exists(cert_file) and os.path.exists(key_file):
                ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
                ssl_context.load_cert_chain(cert_file, key_file)

        async with websockets.serve(self.handler, host, port, ssl=ssl_context):
            await asyncio.Future()  # 永久运行

