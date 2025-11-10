/**
 * VR 虚拟机器人遥操作系统 - 客户端
 * 主入口文件
 */

import { WebRTCClient } from './src/webrtc-client.js';
import { VRScene } from './src/vr-scene.js';

/**
 * 识别哪个视频流是左眼，哪个是右眼
 * 通过分析视频帧的颜色来判断（测试图案模式下）
 */
async function identifyEyeStreams(stream1, stream2) {
    return new Promise((resolve, reject) => {
        const video1 = document.createElement('video');
        const video2 = document.createElement('video');

        video1.srcObject = stream1;
        video2.srcObject = stream2;
        video1.play();
        video2.play();

        // 等待视频加载
        const checkVideos = () => {
            if (video1.readyState >= 2 && video2.readyState >= 2) {
                // 创建 canvas 来分析视频帧
                const canvas = document.createElement('canvas');
                const ctx = canvas.getContext('2d');
                canvas.width = video1.videoWidth;
                canvas.height = video1.videoHeight;

                // 分析第一个视频
                ctx.drawImage(video1, 0, 0);
                const data1 = ctx.getImageData(0, 0, canvas.width, canvas.height).data;
                const avgColor1 = analyzeColor(data1);

                // 分析第二个视频
                canvas.width = video2.videoWidth;
                canvas.height = video2.videoHeight;
                ctx.drawImage(video2, 0, 0);
                const data2 = ctx.getImageData(0, 0, canvas.width, canvas.height).data;
                const avgColor2 = analyzeColor(data2);

                console.log('🎨 视频流颜色分析:');
                console.log(`   - 流 1: R=${avgColor1.r}, G=${avgColor1.g}, B=${avgColor1.b}`);
                console.log(`   - 流 2: R=${avgColor2.r}, G=${avgColor2.g}, B=${avgColor2.b}`);

                // 判断哪个是左眼（红色），哪个是右眼（蓝色）
                // 左眼应该是红色 (R > B)，右眼应该是蓝色 (B > R)
                let leftStream, rightStream;

                if (avgColor1.r > avgColor1.b && avgColor2.b > avgColor2.r) {
                    // 流1是红色（左眼），流2是蓝色（右眼）
                    leftStream = stream1;
                    rightStream = stream2;
                    console.log('✅ 识别结果: 流1=左眼(红), 流2=右眼(蓝)');
                } else if (avgColor1.b > avgColor1.r && avgColor2.r > avgColor2.b) {
                    // 流1是蓝色（右眼），流2是红色（左眼）
                    leftStream = stream2;
                    rightStream = stream1;
                    console.log('✅ 识别结果: 流1=右眼(蓝), 流2=左眼(红)');
                } else {
                    // 无法识别，使用默认顺序
                    console.warn('⚠️  无法通过颜色识别，使用默认顺序');
                    leftStream = stream1;
                    rightStream = stream2;
                }

                // 清理
                video1.pause();
                video2.pause();
                video1.srcObject = null;
                video2.srcObject = null;

                resolve({ leftStream, rightStream });
            } else {
                // 继续等待
                setTimeout(checkVideos, 100);
            }
        };

        // 开始检查
        setTimeout(checkVideos, 500);

        // 超时保护
        setTimeout(() => {
            reject(new Error('识别超时'));
        }, 5000);
    });
}

/**
 * 分析图像数据的平均颜色
 */
function analyzeColor(imageData) {
    let r = 0, g = 0, b = 0;
    const pixelCount = imageData.length / 4;

    for (let i = 0; i < imageData.length; i += 4) {
        r += imageData[i];
        g += imageData[i + 1];
        b += imageData[i + 2];
    }

    return {
        r: Math.round(r / pixelCount),
        g: Math.round(g / pixelCount),
        b: Math.round(b / pixelCount)
    };
}

// 配置
// 自动检测服务器地址：
// - 如果通过 IP 访问（如 192.168.x.x），使用该 IP
// - 如果通过 localhost 访问，使用 localhost
// - 如果页面是 HTTPS，使用 WSS；否则使用 WS
function getSignalingServer() {
    const hostname = window.location.hostname;
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';

    // 如果是 IP 地址，使用该 IP
    if (hostname !== 'localhost' && hostname !== '127.0.0.1') {
        return `${protocol}//${hostname}:8080`;
    }

    // 否则使用 localhost
    return `${protocol}//localhost:8080`;
}

const SIGNALING_SERVER = getSignalingServer();
const SEND_INTERVAL = 16; // 60Hz 发送频率
const VIDEO_MODE = 'sbs'; // 'sbs' (Side-by-Side) 或 'dual' (双轨道)

// 全局变量
let webrtcClient = null;
let vrScene = null;
let lastSendTime = 0;
let isConnected = false;

// 显示状态信息
function showStatus(message, type = 'info') {
    console.log(`[${type.toUpperCase()}] ${message}`);

    // 在页面上显示状态
    let statusDiv = document.getElementById('status');
    if (!statusDiv) {
        statusDiv = document.createElement('div');
        statusDiv.id = 'status';
        statusDiv.style.cssText = `
            position: fixed;
            top: 10px;
            left: 10px;
            background: rgba(0, 0, 0, 0.8);
            color: white;
            padding: 15px;
            border-radius: 5px;
            font-family: monospace;
            font-size: 14px;
            z-index: 1000;
            max-width: 400px;
        `;
        document.body.appendChild(statusDiv);
    }

    const color = type === 'error' ? '#ff4444' : type === 'success' ? '#44ff44' : '#ffffff';
    const timestamp = new Date().toLocaleTimeString();
    statusDiv.innerHTML = `<span style="color: ${color}">[${timestamp}] ${message}</span>`;
}

// 初始化应用
async function init() {
    try {
        showStatus('🚀 初始化 VR 虚拟机器人系统...', 'info');

        // 1. 创建 VR 场景
        showStatus('📐 创建 VR 场景...', 'info');
        vrScene = new VRScene();
        vrScene.setupControllers();

        // 2. 创建 WebRTC 客户端
        showStatus(`🌐 连接到虚拟机器人服务器 (${SIGNALING_SERVER})...`, 'info');
        webrtcClient = new WebRTCClient(SIGNALING_SERVER, VIDEO_MODE);

        // 监听视频轨道
        if (VIDEO_MODE === 'sbs') {
            // Side-by-Side 模式：只接收一个视频轨道
            webrtcClient.onVideoTrack = (stream) => {
                showStatus('📹 收到 Side-by-Side 视频轨道', 'info');
                vrScene.setupStereoVideoSBS(stream);
                isConnected = true;
                showStatus('✅ Side-by-Side 视频流已连接！可以进入 VR 了', 'success');
            };
        } else {
            // 双轨道模式：接收两个视频轨道并识别
            let receivedStreams = [];
            webrtcClient.onVideoTrack = (stream) => {
                receivedStreams.push(stream);
                showStatus(`📹 收到视频轨道 ${receivedStreams.length}/2`, 'info');

                // 当收到两个视频轨道时，识别并设置立体视频
                if (receivedStreams.length === 2) {
                    showStatus('🔍 正在识别左右眼视频流...', 'info');

                    // 识别哪个是左眼，哪个是右眼
                    identifyEyeStreams(receivedStreams[0], receivedStreams[1])
                        .then(({ leftStream, rightStream }) => {
                            vrScene.setupStereoVideo(leftStream, rightStream);
                            isConnected = true;
                            showStatus('✅ 双目视频流已连接！可以进入 VR 了', 'success');
                        })
                        .catch(error => {
                            console.error('❌ 识别视频流失败:', error);
                            showStatus('❌ 识别视频流失败，使用默认顺序', 'error');
                            // 失败时使用默认顺序
                            vrScene.setupStereoVideo(receivedStreams[0], receivedStreams[1]);
                            isConnected = true;
                        });
                }
            };
        }

        // 监听连接状态
        webrtcClient.onConnectionStateChange = (state) => {
            showStatus(`🔗 WebRTC 连接状态: ${state}`, 'info');

            if (state === 'connected') {
                showStatus('✅ WebRTC 连接成功！', 'success');
            } else if (state === 'failed' || state === 'disconnected') {
                showStatus('❌ WebRTC 连接失败或断开', 'error');
                isConnected = false;
            }
        };

        // 3. 连接到信令服务器
        await webrtcClient.connect();

        // 4. 创建 Offer
        await webrtcClient.createOffer();

        showStatus('⏳ 等待虚拟机器人响应...', 'info');

        // 5. 启动渲染循环
        vrScene.startRenderLoop((frame) => {
            // 获取 VR 输入数据
            const inputData = vrScene.getInputData(frame);

            // 定期发送控制数据（60Hz）
            if (inputData && isConnected) {
                const now = performance.now();
                if (now - lastSendTime > SEND_INTERVAL) {
                    webrtcClient.sendControlData(inputData);
                    lastSendTime = now;
                }
            }
        });

    } catch (error) {
        console.error('❌ 初始化失败:', error);
        showStatus(`❌ 初始化失败: ${error.message}`, 'error');
    }
}

// 页面加载完成后初始化
window.addEventListener('load', () => {
    console.log('🎬 页面加载完成，开始初始化...');
    init();
});

// 页面卸载时清理
window.addEventListener('beforeunload', () => {
    if (webrtcClient) {
        webrtcClient.close();
    }
});