# 🚀 快速开始指南

## VR 虚拟机器人遥操作系统

这是一个基于 WebXR 和 WebRTC 的虚拟机器人远程控制系统。你可以通过 VR 头显看到虚拟机器人的双目视野，并实时控制它。

---

## 📋 系统要求

### 硬件
- VR 头显（Meta Quest、Pico、HTC Vive 等）
- 电脑（Windows/Linux/Mac）

### 软件
- Python 3.8+ 
- Node.js 16+
- 支持 WebXR 的浏览器（Chrome、Edge、Firefox）

---

## ⚡ 三步启动

### 步骤 1: 安装依赖

打开终端，执行：

```bash
# 安装虚拟机器人端依赖
cd virtual-robot
pip install -r requirements.txt

# 安装 VR 客户端依赖
cd ..
npm install
```

**注意**：
- Windows 用户可能需要安装 [Visual C++ Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/)
- 如果 `pip install` 很慢，可以使用国内镜像：
  ```bash
  pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
  ```

### 步骤 2: 启动虚拟机器人服务器

**方式 A: 双击启动脚本（推荐）**
```
双击 start-robot.bat
```

**方式 B: 手动启动**
```bash
cd virtual-robot
python main.py
```

你应该看到类似的输出：
```
🤖 虚拟机器人 VR 遥操作系统
============================================================
[1/5] 初始化虚拟机器人...
✅ 虚拟机器人初始化完成
[2/5] 初始化虚拟双目相机...
✅ 虚拟双目相机初始化完成
...
✅ 系统启动成功！
🚀 信令服务器启动: ws://0.0.0.0:8080
```

### 步骤 3: 启动 VR 客户端

在**另一个终端**中：

**方式 A: 双击启动脚本（推荐）**
```
双击 start-client.bat
```

**方式 B: 手动启动**
```bash
npm run dev
```

你应该看到：
```
  VITE v7.x.x  ready in xxx ms

  ➜  Local:   https://localhost:5173/
  ➜  Network: https://192.168.x.x:5173/
```

### 步骤 4: 进入 VR

1. **戴上 VR 头显**
2. **打开浏览器**（Quest Browser、Pico Browser 等）
3. **访问**: `https://localhost:5173` 或 `https://你的电脑IP:5173`
4. **等待连接**：页面会显示连接状态
5. **看到 "✅ 双目视频流已连接！"** 后，点击 **"ENTER VR"** 按钮
6. **移动头部和手柄**，观察虚拟机器人服务器的控制台输出

---

## 🎯 预期效果

### 在 VR 头显中
- ✅ 看到虚拟机器人的双目视野
- ✅ 场景中有彩色立方体和地面
- ✅ 左右眼显示不同视角（立体效果）
- ✅ 移动头部时视角跟随

### 在虚拟机器人控制台
```
📍 头显 - 位置: (0.00, 1.60, 0.00), 旋转: (0.00, 0.00, 0.00, 1.00)
🎮 left 手柄 - 位置: (-0.20, 1.40, -0.30), 扳机: 0.00, 握持: 0.00, 摇杆: (0.00, 0.00)
🎮 right 手柄 - 位置: (0.20, 1.40, -0.30), 扳机: 0.50, 握持: 0.00, 摇杆: (0.00, 0.00)
```

---

## 🔧 常见问题

### Q1: 连接失败怎么办？

**检查清单**：
1. ✅ 确保虚拟机器人服务器正在运行
2. ✅ 确保 VR 客户端开发服务器正在运行
3. ✅ 检查防火墙是否阻止了 8080 和 5173 端口
4. ✅ 确保 VR 头显和电脑在同一局域网

**解决方案**：
```bash
# Windows 防火墙添加规则
netsh advfirewall firewall add rule name="VR Robot" dir=in action=allow protocol=TCP localport=8080,5173
```

### Q2: 看不到视频流？

**检查**：
1. 浏览器控制台是否有错误？
2. WebRTC 连接状态是否为 "connected"？
3. 尝试刷新页面

**解决方案**：
- 降低分辨率：`python main.py --width 320 --height 240`
- 降低帧率：`python main.py --fps 15`

### Q3: PyBullet 安装失败？

**Windows**：
```bash
pip install --upgrade pip
pip install pybullet
```

**Linux**：
```bash
sudo apt-get install python3-dev
pip install pybullet
```

### Q4: aiortc 安装失败？

**Windows**：
1. 安装 [Visual C++ Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/)
2. 重新运行 `pip install aiortc`

**Linux**：
```bash
sudo apt-get install libavformat-dev libavcodec-dev libavdevice-dev libavutil-dev libswscale-dev libavresample-dev libavfilter-dev
pip install aiortc
```

### Q5: VR 头显无法访问 localhost？

**解决方案**：使用电脑的局域网 IP

1. 查看电脑 IP：
   ```bash
   # Windows
   ipconfig
   
   # Linux/Mac
   ifconfig
   ```

2. 在 VR 头显浏览器中访问：`https://192.168.x.x:5173`（替换为你的 IP）

---

## 🎮 高级选项

### 显示 PyBullet GUI（调试用）

```bash
python main.py --gui
```

这会打开一个 3D 窗口，显示虚拟机器人的仿真场景。

### 调整视频质量

```bash
# 高质量（需要更好的网络）
python main.py --fps 60 --width 1280 --height 720

# 低质量（适合弱网络）
python main.py --fps 15 --width 320 --height 240
```

### 查看所有选项

```bash
python main.py --help
```

---

## 📚 更多文档

- **详细文档**: `virtual-robot/README.md`
- **项目计划**: `docs/PROJECT_PLAN.md`
- **技术架构**: 见项目计划文档

---

## 🎉 成功运行后

恭喜！你已经成功运行了 VR 虚拟机器人系统。

**下一步可以做什么？**
1. 尝试移动头部和手柄，观察数据传输
2. 修改 `robot_sim.py` 中的场景（添加更多物体）
3. 实现手柄控制机器人手臂（逆运动学）
4. 添加性能监控面板
5. 对接真实机器人硬件

**需要帮助？**
- 查看控制台错误信息
- 阅读 `virtual-robot/README.md`
- 检查浏览器开发者工具

---

**祝你玩得开心！🚀**

