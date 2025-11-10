# 🤖 VR 虚拟机器人遥操作系统

基于 WebXR 和 WebRTC 的虚拟机器人远程控制系统。

## 📋 系统架构

```
VR 客户端 (浏览器)  ←→  WebRTC  ←→  虚拟机器人服务器 (Python + PyBullet)
```

- **VR 客户端**: Three.js + WebXR，运行在 VR 头显的浏览器中
- **虚拟机器人**: PyBullet 物理仿真 + 双目相机渲染
- **通信**: WebRTC 实时视频流 + 控制数据传输

## 🚀 快速开始

### 1. 安装依赖

#### 虚拟机器人端 (Python)

```bash
cd virtual-robot
pip install -r requirements.txt
```

#### VR 客户端 (Node.js)

```bash
cd ..
npm install
```

### 2. 启动虚拟机器人服务器

```bash
cd virtual-robot
python main.py
```

**可选参数**：
- `--gui`: 显示 PyBullet GUI（调试用）
- `--fps 30`: 设置视频帧率（默认 30）
- `--width 640`: 设置视频宽度（默认 640）
- `--height 480`: 设置视频高度（默认 480）

**示例**：
```bash
# 显示 GUI，60fps，高分辨率
python main.py --gui --fps 60 --width 1280 --height 720
```

### 3. 启动 VR 客户端

在**另一个终端**中：

```bash
npm run dev
```

### 4. 进入 VR

1. 用 VR 头显的浏览器访问: `https://localhost:5173`
2. 等待连接成功提示
3. 点击 "ENTER VR" 按钮
4. 移动头部和手柄，观察虚拟机器人服务器的控制台输出

## 📊 预期效果

### VR 头显中
- 看到虚拟机器人"眼睛"看到的 3D 世界
- 左右眼分别显示不同视角（立体视觉）
- 场景中有彩色立方体和地面

### 虚拟机器人服务器控制台
```
📍 头显 - 位置: (0.00, 1.60, 0.00), 旋转: (0.00, 0.00, 0.00, 1.00)
🎮 left 手柄 - 位置: (-0.20, 1.40, -0.30), 扳机: 0.00, 握持: 0.00, 摇杆: (0.00, 0.00)
🎮 right 手柄 - 位置: (0.20, 1.40, -0.30), 扳机: 0.50, 握持: 0.00, 摇杆: (0.00, 0.00)
```

## 🛠️ 技术栈

### 虚拟机器人端
- **Python 3.8+**
- **PyBullet**: 物理仿真和渲染
- **aiortc**: WebRTC 实现
- **OpenCV**: 图像处理
- **WebSockets**: 信令服务器

### VR 客户端
- **Three.js**: 3D 渲染引擎
- **WebXR Device API**: VR 设备接口
- **WebRTC API**: 实时通信
- **Vite**: 开发服务器

## 📁 项目结构

```
virtual-robot/
├── main.py                 # 主入口
├── robot_sim.py            # PyBullet 仿真
├── stereo_camera.py        # 虚拟双目相机
├── webrtc_server.py        # WebRTC 服务端
├── signaling_server.py     # 信令服务器
├── requirements.txt        # Python 依赖
└── README.md              # 本文档

../  (VR 客户端)
├── src/
│   ├── webrtc-client.js   # WebRTC 客户端
│   └── vr-scene.js        # VR 场景
├── main.js                # 主入口
├── index.html             # HTML 页面
└── package.json           # Node.js 依赖
```

## 🔧 故障排除

### 问题 1: WebRTC 连接失败

**检查**：
1. 确保虚拟机器人服务器正在运行
2. 检查防火墙是否阻止了 8080 端口
3. 查看浏览器控制台的错误信息

### 问题 2: 看不到视频流

**检查**：
1. 确认 WebRTC 连接状态为 "connected"
2. 检查浏览器是否支持 WebRTC
3. 尝试降低分辨率和帧率

### 问题 3: PyBullet 导入失败

**解决**：
```bash
pip install --upgrade pybullet
```

### 问题 4: aiortc 安装失败

**Windows 用户**：
```bash
# 需要先安装 Visual C++ Build Tools
# 下载: https://visualstudio.microsoft.com/visual-cpp-build-tools/
```

**Linux 用户**：
```bash
sudo apt-get install libavformat-dev libavcodec-dev libavdevice-dev libavutil-dev libswscale-dev libavresample-dev libavfilter-dev
```

## 🎯 下一步开发

- [ ] 实现逆运动学，用手柄控制机器人手臂
- [ ] 添加性能监控（帧率、延迟）
- [ ] 支持更多机器人模型（URDF）
- [ ] 添加虚拟环境交互（抓取物体）
- [ ] 对接真实机器人硬件

## 📝 许可证

MIT License

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

