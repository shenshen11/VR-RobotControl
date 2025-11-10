# 🥽 VR 头显访问指南

## 问题说明

在 **Pico VR 头显**（或其他独立 VR 设备）上访问时，不能使用 `localhost`，因为 `localhost` 指向的是 VR 头显自己，而不是运行服务器的电脑。

## ✅ 解决方案

### 步骤 1: 获取电脑的局域网 IP 地址

#### Windows
```powershell
ipconfig
```
查找 "无线局域网适配器 WLAN" 或 "以太网适配器" 下的 **IPv4 地址**，例如：
```
IPv4 地址 . . . . . . . . . . . . : 192.168.1.100
```

#### macOS / Linux
```bash
ifconfig
# 或
ip addr show
```
查找 `inet` 地址，例如 `192.168.1.100`

### 步骤 2: 确保 VR 头显和电脑在同一网络

- VR 头显和电脑必须连接到**同一个 WiFi 网络**
- 确保路由器没有启用 AP 隔离（某些公共 WiFi 会隔离设备）

### 步骤 3: 在 VR 头显浏览器中访问

使用电脑的 IP 地址访问：
```
https://192.168.1.100:5173
```
（将 `192.168.1.100` 替换为你的电脑 IP）

### 步骤 4: 接受 HTTPS 证书警告

因为使用的是自签名证书，浏览器会显示安全警告：
1. 点击 "高级" 或 "Advanced"
2. 点击 "继续访问" 或 "Proceed to site"

---

## 🔧 系统已自动修复

现在系统会**自动检测**访问方式：

- **通过 `localhost` 访问**：连接到 `ws://localhost:8080`
- **通过 IP 访问**（如 `192.168.1.100`）：连接到 `ws://192.168.1.100:8080`

这样在 VR 头显上访问时，会自动使用正确的服务器地址。

---

## 📊 验证连接

### 正常情况

**VR 头显浏览器控制台**（Chrome DevTools）：
```
✅ VR 场景初始化完成
🌐 连接到虚拟机器人服务器 (ws://192.168.1.100:8080)...
🔗 连接到信令服务器: ws://192.168.1.100:8080
✅ WebSocket 连接成功
📹 收到视频轨道 1/2
📹 收到视频轨道 2/2
✅ 双目视频流已连接！
```

**虚拟机器人服务器控制台**：
```
🔗 新客户端连接: 192.168.1.xxx:xxxxx
📨 收到消息: offer
✅ Answer 已创建
📤 已发送 Answer
🔗 连接状态: connected
📡 DataChannel 已建立: control
```

### 错误情况

#### 错误 1: 连接被拒绝
```
❌ WebSocket 连接失败: Error in connection establishment: net::ERR_CONNECTION_REFUSED
```

**原因**：
- 虚拟机器人服务器未启动
- 使用了错误的 IP 地址
- 防火墙阻止了连接

**解决**：
1. 确保虚拟机器人服务器正在运行：
   ```bash
   cd virtual-robot
   python main.py
   ```

2. 检查防火墙设置（Windows）：
   ```powershell
   # 允许端口 8080
   netsh advfirewall firewall add rule name="VR Robot Port 8080" dir=in action=allow protocol=TCP localport=8080
   
   # 允许端口 5173
   netsh advfirewall firewall add rule name="VR Robot Port 5173" dir=in action=allow protocol=TCP localport=5173
   ```

3. 验证 IP 地址是否正确

#### 错误 2: 网络不可达
```
❌ WebSocket 连接失败: net::ERR_NETWORK_UNREACHABLE
```

**原因**：VR 头显和电脑不在同一网络

**解决**：
- 确保 VR 头显和电脑连接到同一个 WiFi
- 检查路由器是否启用了 AP 隔离

---

## 🧪 测试连接

### 方法 1: 在 VR 头显上测试 WebSocket

在 VR 头显浏览器的控制台中运行：
```javascript
const ws = new WebSocket('ws://192.168.1.100:8080');
ws.onopen = () => console.log('✅ 连接成功！');
ws.onerror = (e) => console.error('❌ 连接失败:', e);
```

### 方法 2: 在电脑上测试

在电脑浏览器中访问：
```
https://192.168.1.100:5173
```
（使用电脑的 IP，而不是 localhost）

如果在电脑上能正常工作，说明服务器配置正确，问题可能在网络连接上。

---

## 📝 完整启动流程

### 1. 启动虚拟机器人服务器（电脑）

```bash
cd virtual-robot
python main.py
```

应该看到：
```
✅ 系统启动成功！
🚀 信令服务器启动: ws://0.0.0.0:8080
```

### 2. 启动 VR 客户端（电脑）

```bash
# 在项目根目录
npm run dev
```

应该看到：
```
VITE v7.2.2  ready in xxx ms

➜  Local:   https://localhost:5173/
➜  Network: https://192.168.1.100:5173/
```

**重要**：记下 `Network` 后面的地址！

### 3. 在 VR 头显上访问

1. 打开 VR 头显的浏览器
2. 访问上面 `Network` 显示的地址（例如 `https://192.168.1.100:5173`）
3. 接受 HTTPS 证书警告
4. 等待连接成功
5. 点击 "ENTER VR" 进入 VR 模式

---

## 🎯 预期效果

### VR 头显中
- ✅ 看到虚拟机器人的双目视野
- ✅ 场景中有彩色立方体和地面
- ✅ 左右眼显示不同视角（立体效果）
- ✅ 移动头部，视角跟随移动

### 虚拟机器人控制台
```
📍 头显 - 位置: (0.00, 1.60, 0.00), 旋转: (0.00, 0.00, 0.00, 1.00)
🎮 left 手柄 - 位置: (-0.20, 1.40, -0.30), 扳机: 0.00, 握持: 0.00
🎮 right 手柄 - 位置: (0.20, 1.40, -0.30), 扳机: 0.00, 握持: 0.00
```

---

## 🔍 故障排除

### 问题：在电脑上能访问，但 VR 头显不能

**检查清单**：
1. ✅ VR 头显和电脑在同一 WiFi？
2. ✅ 使用的是电脑的 IP 地址，而不是 localhost？
3. ✅ 防火墙允许端口 8080 和 5173？
4. ✅ 虚拟机器人服务器正在运行？

### 问题：连接成功但看不到视频

**检查**：
1. 浏览器控制台是否显示 "✅ 双目视频流已连接"？
2. 虚拟机器人控制台是否显示 "📹 left 眼已发送 xxx 帧"？
3. 是否点击了 "ENTER VR" 按钮？

### 问题：视频卡顿或延迟高

**优化**：
1. 确保 WiFi 信号强度良好
2. 降低视频分辨率（编辑 `virtual-robot/main.py`）：
   ```python
   camera = StereoCamera(robot, width=320, height=240)  # 降低分辨率
   ```
3. 降低帧率：
   ```python
   webrtc = WebRTCServer(robot, camera, fps=15)  # 降低帧率
   ```

---

## 📚 相关文档

- [README.md](README.md) - 项目总览
- [QUICKSTART.md](QUICKSTART.md) - 快速开始指南
- [FIXES.md](FIXES.md) - 修复历史
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - 故障排除

---

**最后更新**: 2025-11-10

