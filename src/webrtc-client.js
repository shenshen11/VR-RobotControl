/**
 * WebRTC 客户端模块
 * 负责与虚拟机器人服务器建立 WebRTC 连接
 */

export class WebRTCClient {
    constructor(signalingUrl, videoMode = 'sbs') {
        this.signalingUrl = signalingUrl;
        this.videoMode = videoMode;  // 'sbs' 或 'dual'
        this.ws = null;
        this.pc = null;
        this.dataChannel = null;
        this.videoTracks = [];

        // 回调函数
        this.onVideoTrack = null;
        this.onConnectionStateChange = null;
    }
    
    async connect() {
        console.log('🔗 连接到信令服务器:', this.signalingUrl);
        
        // 连接 WebSocket
        this.ws = new WebSocket(this.signalingUrl);
        
        return new Promise((resolve, reject) => {
            this.ws.onopen = () => {
                console.log('✅ WebSocket 连接成功');
                this._setupPeerConnection();
                resolve();
            };
            
            this.ws.onerror = (error) => {
                console.error('❌ WebSocket 连接失败:', error);
                reject(error);
            };
            
            this.ws.onmessage = async (event) => {
                await this._handleSignalingMessage(event.data);
            };
        });
    }
    
    _setupPeerConnection() {
        console.log('🔧 创建 RTCPeerConnection...');
        
        // 创建 PeerConnection
        this.pc = new RTCPeerConnection({
            iceServers: [
                { urls: 'stun:stun.l.google.com:19302' },
                { urls: 'stun:stun1.l.google.com:19302' }
            ]
        });
        
        // 监听 ICE Candidate
        this.pc.onicecandidate = (event) => {
            if (event.candidate) {
                console.log('📤 发送 ICE Candidate');
                this.ws.send(JSON.stringify({
                    type: 'ice-candidate',
                    candidate: event.candidate
                }));
            }
        };
        
        // 监听视频轨道
        this.pc.ontrack = (event) => {
            const trackIndex = this.videoTracks.length;
            console.log(`📹 收到视频轨道 ${trackIndex + 1}:`, event.track.id);
            console.log(`   - Track label: ${event.track.label}`);
            console.log(`   - Stream ID: ${event.streams[0].id}`);

            this.videoTracks.push(event.streams[0]);

            if (this.onVideoTrack) {
                this.onVideoTrack(event.streams[0], trackIndex);
            }
        };
        
        // 监听连接状态
        this.pc.onconnectionstatechange = () => {
            console.log('🔗 连接状态:', this.pc.connectionState);
            
            if (this.onConnectionStateChange) {
                this.onConnectionStateChange(this.pc.connectionState);
            }
        };
        
        // 创建 DataChannel（用于发送控制数据）
        this.dataChannel = this.pc.createDataChannel('control');
        
        this.dataChannel.onopen = () => {
            console.log('✅ DataChannel 已打开');
        };
        
        this.dataChannel.onclose = () => {
            console.log('🔌 DataChannel 已关闭');
        };
    }
    
    async createOffer() {
        console.log('📝 创建 Offer...');

        // 添加 recvonly transceiver 来接收视频
        if (this.videoMode === 'sbs') {
            // Side-by-Side 模式：只需要一个视频轨道
            this.pc.addTransceiver('video', { direction: 'recvonly' });
            console.log('   - 添加 1 个 recvonly transceiver (Side-by-Side)');
        } else {
            // 双轨道模式：需要两个视频轨道
            this.pc.addTransceiver('video', { direction: 'recvonly' });
            this.pc.addTransceiver('video', { direction: 'recvonly' });
            console.log('   - 添加 2 个 recvonly transceiver (双轨道)');
        }

        const offer = await this.pc.createOffer();
        await this.pc.setLocalDescription(offer);

        console.log('📤 发送 Offer');
        this.ws.send(JSON.stringify({
            type: 'offer',
            sdp: offer.sdp
        }));
    }
    
    async _handleSignalingMessage(message) {
        const data = JSON.parse(message);
        
        console.log('📨 收到信令消息:', data.type);
        
        if (data.type === 'answer') {
            console.log('✅ 收到 Answer，设置远程描述');
            await this.pc.setRemoteDescription(
                new RTCSessionDescription({ type: data.type, sdp: data.sdp })
            );
        } else if (data.type === 'ice-candidate') {
            console.log('✅ 收到 ICE Candidate');
            await this.pc.addIceCandidate(new RTCIceCandidate(data.candidate));
        }
    }
    
    sendControlData(data) {
        if (this.dataChannel && this.dataChannel.readyState === 'open') {
            this.dataChannel.send(JSON.stringify(data));
        }
    }
    
    getVideoStreams() {
        if (this.videoMode === 'sbs') {
            // Side-by-Side 模式：返回单个视频流
            return this.videoTracks[0];
        } else {
            // 双轨道模式：返回左右眼视频流
            return {
                left: this.videoTracks[0],
                right: this.videoTracks[1]
            };
        }
    }
    
    close() {
        if (this.dataChannel) {
            this.dataChannel.close();
        }
        if (this.pc) {
            this.pc.close();
        }
        if (this.ws) {
            this.ws.close();
        }
        console.log('🔌 WebRTC 客户端已关闭');
    }
}

