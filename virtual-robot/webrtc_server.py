"""
WebRTC 服务端模块
使用 aiortc 实现视频流传输和控制数据接收
"""
import asyncio
import json
import time
from aiortc import RTCPeerConnection, RTCSessionDescription, RTCIceCandidate, VideoStreamTrack
from av import VideoFrame
import numpy as np


class RobotVideoTrack(VideoStreamTrack):
    """
    自定义视频轨道 - 从虚拟机器人获取帧
    支持双轨道模式和 Side-by-Side 模式
    """

    def __init__(self, camera, mode='sbs', eye='left', fps=30, test_pattern=False):
        """
        Args:
            camera: StereoCamera 实例
            mode: 'sbs' (Side-by-Side 单轨道) 或 'dual' (双轨道)
            eye: 'left' 或 'right' (仅在 dual 模式下使用)
            fps: 目标帧率
            test_pattern: 是否使用测试图案（调试用）
        """
        super().__init__()
        self.camera = camera
        self.mode = mode
        self.eye = eye
        self.fps = fps
        self.counter = 0
        self.test_pattern = test_pattern

        # 用于帧率控制
        self.frame_interval = 1.0 / fps
        self.last_frame_time = 0

    async def recv(self):
        """
        WebRTC 调用此方法获取视频帧

        Returns:
            VideoFrame: 视频帧
        """
        # 生成时间戳
        pts, time_base = await self.next_timestamp()

        # 帧率控制
        current_time = time.time()
        if current_time - self.last_frame_time < self.frame_interval:
            await asyncio.sleep(self.frame_interval - (current_time - self.last_frame_time))
        self.last_frame_time = time.time()

        try:
            # 从虚拟相机获取帧
            if self.mode == 'sbs':
                # Side-by-Side 模式：发送拼接后的图像
                if self.test_pattern:
                    img = self.camera.render_test_pattern_sbs()
                else:
                    img = self.camera.render_stereo_sbs()
            else:
                # 双轨道模式：发送单眼图像
                if self.test_pattern:
                    left_img, right_img = self.camera.render_test_pattern()
                else:
                    left_img, right_img = self.camera.render_stereo()

                # 选择左眼或右眼
                img = left_img if self.eye == 'left' else right_img

            # 转换为 VideoFrame
            frame = VideoFrame.from_ndarray(img, format='bgr24')
            frame.pts = pts
            frame.time_base = time_base
            self.counter += 1
            return frame

        except Exception as e:
            # 返回黑色帧作为备用
            if self.mode == 'sbs':
                black_frame = np.zeros((480, 1280, 3), dtype=np.uint8)
            else:
                black_frame = np.zeros((480, 640, 3), dtype=np.uint8)
            frame = VideoFrame.from_ndarray(black_frame, format='bgr24')
            frame.pts = pts
            frame.time_base = time_base
            return frame


class WebRTCServer:
    """
    WebRTC 服务器
    处理与 VR 客户端的连接
    """

    def __init__(self, robot_sim, camera, fps=30, test_pattern=False, video_mode='sbs'):
        """
        Args:
            robot_sim: VirtualRobot 实例
            camera: StereoCamera 实例
            fps: 视频帧率
            test_pattern: 是否使用测试图案（调试用）
            video_mode: 'sbs' (Side-by-Side 单轨道) 或 'dual' (双轨道)
        """
        self.robot_sim = robot_sim
        self.camera = camera
        self.fps = fps
        self.test_pattern = test_pattern
        self.video_mode = video_mode
        self.pc = None
        self.data_channel = None
    
    async def handle_offer(self, offer_sdp):
        """
        处理来自 VR 客户端的 Offer

        Args:
            offer_sdp: SDP Offer 字典 {'sdp': str, 'type': str}

        Returns:
            answer_sdp: SDP Answer 字典 {'sdp': str, 'type': str}
        """
        # 创建 RTCPeerConnection
        self.pc = RTCPeerConnection()

        # 添加视频轨道
        if self.video_mode == 'sbs':
            # Side-by-Side 模式：只添加一个轨道
            sbs_track = RobotVideoTrack(
                self.camera,
                mode='sbs',
                fps=self.fps,
                test_pattern=self.test_pattern
            )
            self.pc.addTrack(sbs_track)
        else:
            # 双轨道模式：添加左右眼两个轨道
            left_track = RobotVideoTrack(
                self.camera,
                mode='dual',
                eye='left',
                fps=self.fps,
                test_pattern=self.test_pattern
            )
            right_track = RobotVideoTrack(
                self.camera,
                mode='dual',
                eye='right',
                fps=self.fps,
                test_pattern=self.test_pattern
            )
            self.pc.addTrack(left_track)
            self.pc.addTrack(right_track)
        
        # 处理 DataChannel（接收控制数据）
        @self.pc.on("datachannel")
        def on_datachannel(channel):
            self.data_channel = channel

            @channel.on("message")
            def on_message(message):
                try:
                    control_data = json.loads(message)
                    self.robot_sim.apply_vr_control(control_data)
                except:
                    pass

        # 监听连接状态
        @self.pc.on("connectionstatechange")
        async def on_connectionstatechange():
            if self.pc.connectionState == "failed":
                await self.pc.close()
        
        # 设置远程描述
        await self.pc.setRemoteDescription(
            RTCSessionDescription(sdp=offer_sdp['sdp'], type=offer_sdp['type'])
        )

        # 创建 Answer
        answer = await self.pc.createAnswer()
        await self.pc.setLocalDescription(answer)

        return {
            'sdp': self.pc.localDescription.sdp,
            'type': self.pc.localDescription.type
        }
    
    async def add_ice_candidate(self, candidate_dict):
        """
        添加 ICE Candidate

        Args:
            candidate_dict: ICE Candidate 字典（来自浏览器）
        """
        if self.pc:
            try:
                if isinstance(candidate_dict, dict):
                    candidate = RTCIceCandidate(
                        component=candidate_dict.get('component', 1),
                        foundation=candidate_dict.get('foundation', ''),
                        ip=candidate_dict.get('address', candidate_dict.get('ip', '')),
                        port=candidate_dict.get('port', 0),
                        priority=candidate_dict.get('priority', 0),
                        protocol=candidate_dict.get('protocol', 'udp'),
                        type=candidate_dict.get('type', 'host'),
                        sdpMid=candidate_dict.get('sdpMid'),
                        sdpMLineIndex=candidate_dict.get('sdpMLineIndex')
                    )
                else:
                    candidate = candidate_dict
                await self.pc.addIceCandidate(candidate)
            except:
                pass

    async def close(self):
        """关闭连接"""
        if self.pc:
            await self.pc.close()

