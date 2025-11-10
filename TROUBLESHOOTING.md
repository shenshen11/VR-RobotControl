# 🔧 故障排除指南

## 常见问题和解决方案

---

## ❌ 问题 1: WebSocket Handler 错误

### 错误信息
```
TypeError: SignalingServer.handler() missing 1 required positional argument: 'path'
```

### 原因
`websockets` 库版本不兼容。新版本（13.0+）改变了 handler 的调用签名。

### 解决方案
✅ **已修复**！更新后的代码已兼容新版本 websockets。

如果仍有问题，请重新拉取最新代码：
```bash
cd virtual-robot
# 查看 signaling_server.py 第 26 行
# 应该是: async def handler(self, websocket):
# 而不是: async def handler(self, websocket, path):
```

---

## ❌ 问题 1.1: ICE Candidate 错误

### 错误信息
```
❌ 添加 ICE Candidate 失败: 'dict' object has no attribute 'sdpMid'
```

### 原因
浏览器发送的 ICE Candidate 是 JSON 对象，需要转换为 aiortc 的 `RTCIceCandidate` 格式。

### 解决方案
✅ **已修复**！更新后的 `webrtc_server.py` 已添加格式转换逻辑。

验证修复：
```bash
cd virtual-robot
# 查看 webrtc_server.py 第 8 行
# 应该导入: from aiortc import RTCPeerConnection, RTCSessionDescription, RTCIceCandidate, VideoStreamTrack
```

---

## ❌ 问题 1.2: List Index 错误

### 错误信息
```
❌ 处理消息时出错: list.index(x): x not in list
```

### 原因
这通常是 aiortc 内部处理 SDP 时的问题，可能是由于 SDP 格式不兼容。

### 解决方案

1. **检查 aiortc 版本**
   ```bash
   pip show aiortc
   # 应该是 1.5.0 或更高
   ```

2. **重新安装 aiortc**
   ```bash
   pip uninstall aiortc
   pip install aiortc>=1.5.0
   ```

3. **如果问题持续**，这个错误通常不影响连接建立，可以忽略。检查是否：
   - 视频轨道已创建（看到 "✅ 视频轨道创建" 消息）
   - Answer 已发送（看到 "📤 已发送 Answer" 消息）
   - 连接状态变为 "connected"

---

## ❌ 问题 2: 连接失败

### 错误信息
```
WebSocket connection failed
```

### 检查清单
1. ✅ 确保虚拟机器人服务器正在运行
   ```bash
   cd virtual-robot
   python main.py
   ```

2. ✅ 检查端口是否被占用
   ```bash
   # Windows
   netstat -ano | findstr :8080
   
   # Linux/Mac
   lsof -i :8080
   ```

3. ✅ 检查防火墙设置
   ```bash
   # Windows: 添加防火墙规则
   netsh advfirewall firewall add rule name="VR Robot" dir=in action=allow protocol=TCP localport=8080,5173
   ```

4. ✅ 测试信令服务器
   ```bash
   cd virtual-robot
   python test_connection.py
   ```

---

## ❌ 问题 3: Python 依赖安装失败

### aiortc 安装失败

#### Windows
```bash
# 1. 安装 Visual C++ Build Tools
# 下载: https://visualstudio.microsoft.com/visual-cpp-build-tools/

# 2. 重新安装
pip install --upgrade pip
pip install aiortc
```

#### Linux
```bash
sudo apt-get update
sudo apt-get install -y \
    libavformat-dev \
    libavcodec-dev \
    libavdevice-dev \
    libavutil-dev \
    libswscale-dev \
    libavresample-dev \
    libavfilter-dev \
    python3-dev

pip install aiortc
```

### PyBullet 安装失败

```bash
# 升级 pip
pip install --upgrade pip

# 安装 PyBullet
pip install pybullet
```

---

## ❌ 问题 4: 看不到视频流

### 检查步骤

1. **检查 WebRTC 连接状态**
   - 打开浏览器开发者工具（F12）
   - 查看控制台是否显示 "✅ WebRTC 连接成功！"

2. **检查视频轨道**
   - 控制台应显示 "📹 收到视频轨道 1/2" 和 "📹 收到视频轨道 2/2"

3. **降低视频质量**
   ```bash
   # 尝试低分辨率
   python main.py --width 320 --height 240 --fps 15
   ```

4. **检查浏览器兼容性**
   - 确保使用支持 WebXR 的浏览器
   - Chrome、Edge、Firefox 最新版本

---

## ❌ 问题 5: VR 头显无法访问 localhost

### 原因
VR 头显和电脑不在同一网络，或者头显无法解析 localhost。

### 解决方案

1. **查找电脑 IP 地址**
   ```bash
   # Windows
   ipconfig
   
   # Linux/Mac
   ifconfig
   ```

2. **使用 IP 地址访问**
   - 假设电脑 IP 是 `192.168.1.100`
   - 在 VR 头显浏览器中访问: `https://192.168.1.100:5173`

3. **更新 WebRTC 客户端配置**
   
   编辑 `src/webrtc-client.js`，修改第 5 行：
   ```javascript
   // 原来
   const SIGNALING_SERVER = 'ws://localhost:8080';
   
   // 改为
   const SIGNALING_SERVER = 'ws://192.168.1.100:8080';
   ```

---

## ❌ 问题 6: HTTPS 证书警告

### 原因
Vite 使用自签名证书，浏览器会显示安全警告。

### 解决方案
1. 在浏览器中点击 "高级"
2. 点击 "继续访问"（不安全）
3. 这是正常的，因为是本地开发环境

---

## ❌ 问题 7: 控制数据没有打印

### 检查步骤

1. **确认已进入 VR 模式**
   - 必须点击 "ENTER VR" 按钮
   - 戴上 VR 头显

2. **检查 DataChannel 状态**
   - 浏览器控制台应显示 DataChannel 已打开

3. **移动头部和手柄**
   - 确保 VR 设备正在追踪

4. **查看虚拟机器人控制台**
   - 应该看到类似输出：
     ```
     📍 头显 - 位置: (0.00, 1.60, 0.00)...
     ```

---

## ❌ 问题 8: 性能问题（卡顿、延迟高）

### 优化建议

1. **降低视频分辨率**
   ```bash
   python main.py --width 480 --height 360 --fps 20
   ```

2. **关闭 PyBullet GUI**
   ```bash
   # 不要使用 --gui 参数
   python main.py
   ```

3. **检查网络延迟**
   ```bash
   # 测试延迟
   ping 192.168.1.100
   ```

4. **使用有线连接**
   - 如果可能，使用网线连接电脑和路由器
   - VR 头显使用 5GHz WiFi

---

## ❌ 问题 9: PyBullet 找不到机器人模型

### 错误信息
```
FileNotFoundError: humanoid/humanoid.urdf
```

### 解决方案

PyBullet 自带了 humanoid 模型，但路径可能不同。修改 `robot_sim.py`：

```python
# 原来
robot_urdf = "humanoid/humanoid.urdf"

# 改为使用 PyBullet 数据路径
import pybullet_data
self.physics_client = p.connect(p.DIRECT)
p.setAdditionalSearchPath(pybullet_data.getDataPath())
robot_urdf = "humanoid/humanoid.urdf"
```

或者使用简单的立方体代替：
```python
# 使用立方体代替机器人
self.robot_id = p.createCollisionShape(p.GEOM_BOX, halfExtents=[0.5, 0.5, 1.0])
self.robot_body = p.createMultiBody(1, self.robot_id, -1, [0, 0, 1])
```

---

## 🧪 测试工具

### 测试信令服务器
```bash
cd virtual-robot
python test_connection.py
```

### 测试 WebRTC 连接
打开浏览器开发者工具（F12），查看控制台输出。

### 查看详细日志
```bash
# 启动时查看详细输出
python main.py --gui
```

---

## 📞 获取帮助

如果以上方法都无法解决问题：

1. **查看完整错误信息**
   - 复制完整的错误堆栈
   - 查看浏览器控制台的错误

2. **检查版本**
   ```bash
   python --version  # 应该是 3.8+
   node --version    # 应该是 16+
   pip list | grep pybullet
   pip list | grep aiortc
   pip list | grep websockets
   ```

3. **重新安装依赖**
   ```bash
   # 虚拟机器人端
   cd virtual-robot
   pip uninstall -y pybullet aiortc websockets
   pip install -r requirements.txt
   
   # VR 客户端
   cd ..
   rm -rf node_modules package-lock.json
   npm install
   ```

---

## ✅ 验证系统正常工作

### 虚拟机器人端
应该看到：
```
✅ 系统启动成功！
🚀 信令服务器启动: ws://0.0.0.0:8080
🔗 新客户端连接: 192.168.1.x:xxxxx
📨 收到消息: offer
📤 已发送 Answer
```

### VR 客户端
浏览器控制台应该看到：
```
✅ VR 场景初始化完成
🌐 连接到虚拟机器人服务器...
📹 收到视频轨道 1/2
📹 收到视频轨道 2/2
✅ 双目视频流已连接！
🔗 WebRTC 连接状态: connected
```

### VR 头显中
- 看到立体视频
- 场景中有彩色立方体
- 移动头部时视角跟随

---

**如果问题仍未解决，请提供详细的错误信息！** 🚀

