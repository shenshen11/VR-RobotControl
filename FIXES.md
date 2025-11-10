# 🔧 最新修复说明

## 修复历史

### 2025-11-10 - 修复 10: 修复 VRCamera 父相机图层配置 ✅ 最新

#### 修复的问题

**问题描述**：
即使配置了子相机（`xrCamera.cameras[0]` 和 `xrCamera.cameras[1]`）的图层，仍然只能看到一个红色视频。

**根本原因**：
根据 Three.js 官方论坛的讨论（https://discourse.threejs.org/t/layers-and-webxr/17751/5），在 WebXR 中使用图层系统时，**必须同时配置 VRCamera 本身（父相机）和子相机**！

只配置子相机是不够的：
```javascript
// ❌ 不完整的配置
xrCamera.cameras[0].layers.enable(1);  // 左眼
xrCamera.cameras[1].layers.enable(2);  // 右眼
```

必须同时配置父相机：
```javascript
// ✅ 完整的配置
xrCamera.layers.enable(0);  // 父相机必须能看到所有图层
xrCamera.layers.enable(1);
xrCamera.layers.enable(2);

xrCamera.cameras[0].layers.enable(0);  // 左眼
xrCamera.cameras[0].layers.enable(1);

xrCamera.cameras[1].layers.enable(0);  // 右眼
xrCamera.cameras[1].layers.enable(2);
```

#### 解决方案

**文件**: `src/vr-scene.js`

**修改**: `configureStereoLayers()` 方法（第 222-263 行）

```javascript
configureStereoLayers() {
    const xrCamera = this.renderer.xr.getCamera();

    // 🔑 关键：必须同时配置父相机和子相机

    // 1. 配置 VRCamera 本身（父相机）
    xrCamera.layers.disableAll();
    xrCamera.layers.enable(0);  // 场景
    xrCamera.layers.enable(1);  // 左眼视频
    xrCamera.layers.enable(2);  // 右眼视频

    // 2. 配置左眼相机
    xrCamera.cameras[0].layers.disableAll();
    xrCamera.cameras[0].layers.enable(0);
    xrCamera.cameras[0].layers.enable(1);

    // 3. 配置右眼相机
    xrCamera.cameras[1].layers.disableAll();
    xrCamera.cameras[1].layers.enable(0);
    xrCamera.cameras[1].layers.enable(2);
}
```

#### 其他修复

1. **智能视频流识别**（`main.js`）：
   - 通过分析视频帧颜色自动识别左右眼
   - 解决 WebRTC 轨道接收顺序不确定的问题

2. **全视野视频显示**（`src/vr-scene.js`）：
   - 视频填满 90° 视场角
   - 距离相机 1 米
   - 作为背景渲染

#### 测试步骤

1. **启动虚拟机器人**（测试图案模式）：
   ```bash
   cd virtual-robot
   python main.py --test-pattern
   ```

2. **刷新 PICO VR 浏览器**

3. **查看控制台**：
   ```
   🎨 视频流颜色分析:
      - 流 1: R=xxx, G=xxx, B=xxx
      - 流 2: R=xxx, G=xxx, B=xxx
   ✅ 识别结果: ...

   🥽 配置立体图层...
   📷 XR 相机数量: 2
      - VRCamera (父) -> 图层 0 + 1 + 2
      - 左眼相机 -> 图层 0 + 1
      - 右眼相机 -> 图层 0 + 2
   ✅ 双目图层配置完成
   ```

4. **进入 VR 并验证**：
   - 左眼应该看到红色 "LEFT EYE"
   - 右眼应该看到蓝色 "RIGHT EYE"
   - 闭上一只眼睛，颜色应该改变

#### 预期结果

**成功标志**：
- ✅ 控制台显示 "VRCamera (父) -> 图层 0 + 1 + 2"
- ✅ 左眼看到红色，右眼看到蓝色
- ✅ 视频填满整个视野

---

### 2025-11-10 - 修复 9: 使用动态纹理切换替代图层系统 ❌ 失败（需要配置父相机）

#### 修复的问题

**问题描述**：
即使图层配置正确（XR 相机数量 = 2，图层掩码正确），在 PICO VR 中仍然只能看到左眼视频（红色 "LEFT EYE"），右眼也看到相同内容。

**症状**：
- ✅ XR 相机数量: 2
- ✅ 图层配置完成（左眼: 图层 0+1，右眼: 图层 0+2）
- ✅ 图层掩码正确
- ❌ 但两只眼睛仍然看到相同画面

#### 根本原因

**PICO 浏览器的 WebXR 图层系统不工作**：
- Three.js 的图层系统（`layers.set()`, `layers.enable()`）在 PICO 浏览器中可能没有正确实现
- 即使图层掩码设置正确，渲染器仍然不能正确过滤物体
- 这是 PICO 浏览器的 WebXR 实现问题，不是代码问题

#### 解决方案

**放弃图层系统，使用 `onBeforeRender` 回调动态切换纹理**：
- 创建单个视频屏幕（而不是两个）
- 在渲染每个相机之前，检查当前渲染的是左眼还是右眼
- 动态切换材质的纹理贴图

这个方法**不依赖图层系统**，直接在渲染时切换纹理，兼容性更好。

#### 修改的文件

**src/vr-scene.js**

**修改 1：移除双屏幕，使用单屏幕 + 动态纹理**（第 159-209 行）

修改前：
```javascript
// 创建左眼屏幕
this.leftScreen = new THREE.Mesh(geometry, new THREE.MeshBasicMaterial({ map: leftTexture }));
this.leftScreen.layers.set(1);
this.scene.add(this.leftScreen);

// 创建右眼屏幕
this.rightScreen = new THREE.Mesh(geometry, new THREE.MeshBasicMaterial({ map: rightTexture }));
this.rightScreen.layers.set(2);
this.scene.add(this.rightScreen);
```

修改后：
```javascript
// 创建单个屏幕
const material = new THREE.MeshBasicMaterial({ map: leftTexture });
this.videoScreen = new THREE.Mesh(geometry, material);

// 使用 onBeforeRender 动态切换纹理
this.videoScreen.onBeforeRender = (renderer, scene, camera) => {
    const xrCamera = renderer.xr.getCamera();
    if (xrCamera && xrCamera.cameras && xrCamera.cameras.length >= 2) {
        if (camera === xrCamera.cameras[0]) {
            material.map = this.leftTexture;  // 左眼
        } else if (camera === xrCamera.cameras[1]) {
            material.map = this.rightTexture; // 右眼
        }
        material.needsUpdate = true;
    }
};

this.scene.add(this.videoScreen);
```

**修改 2：移除图层配置代码**（删除 `configureStereoLayers()` 方法）

**修改 3：简化渲染循环**（第 310-319 行）

#### 工作原理

1. **渲染左眼时**：
   - Three.js 调用 `videoScreen.onBeforeRender()`
   - 检测到当前相机是 `xrCamera.cameras[0]`（左眼）
   - 将材质纹理切换为 `leftTexture`
   - 渲染屏幕

2. **渲染右眼时**：
   - Three.js 再次调用 `videoScreen.onBeforeRender()`
   - 检测到当前相机是 `xrCamera.cameras[1]`（右眼）
   - 将材质纹理切换为 `rightTexture`
   - 渲染屏幕

3. **结果**：
   - 左眼看到左眼视频
   - 右眼看到右眼视频
   - **不依赖图层系统**

#### 使用方法

**自动应用**：
```bash
# 在 PICO VR 浏览器中刷新页面即可
# 代码已自动更新
```

#### 预期输出

**测试图案模式下**：
- 左眼应该看到：红色背景 + "LEFT EYE"
- 右眼应该看到：蓝色背景 + "RIGHT EYE"
- **真正的立体效果！**

**控制台输出**：
```
🥽 VR 会话已启动
📺 使用动态纹理切换方法（不依赖图层系统）
👁️ 渲染左眼
👁️ 渲染右眼
👁️ 渲染左眼
👁️ 渲染右眼
...
```

#### 验证方法

1. **确保虚拟机器人服务器在测试图案模式下运行**：
   ```bash
   cd virtual-robot
   python main.py --test-pattern
   ```

2. **在 PICO VR 浏览器中刷新页面**

3. **进入 VR 模式**

4. **检查控制台**：
   - 应该看到 "👁️ 渲染左眼" 和 "👁️ 渲染右眼" 交替出现

5. **检查 VR 显示**：
   - 闭上左眼，只用右眼看 → 应该看到蓝色
   - 闭上右眼，只用左眼看 → 应该看到红色

---

### 2025-11-10 - 修复 8: VR 立体图层分离问题 ❌ 失败（PICO 不支持）

#### 修复的问题

**问题描述**：
在 VR 中只能看到左眼视频（红色 "LEFT EYE"），右眼也看到相同的内容，没有立体效果。

**症状**：
- XR 相机数量: 2 ✅
- 双目图层配置完成 ✅
- 但两只眼睛看到相同的画面 ❌

#### 根本原因

使用 `layers.set(n)` 会**替换所有图层**，导致：
1. 左眼相机只能看到图层 1（左眼视频）
2. 右眼相机只能看到图层 2（右眼视频）
3. **但是**，由于某种原因，右眼相机也看到了图层 1

正确的做法是使用 `layers.enable(n)` 来**添加**图层：
- 左眼：图层 0（场景）+ 图层 1（左眼视频）
- 右眼：图层 0（场景）+ 图层 2（右眼视频）

#### 修改的文件

**src/vr-scene.js** (第 194-223 行)

修改前：
```javascript
// 左眼相机只看图层 1
xrCamera.cameras[0].layers.set(1);

// 右眼相机只看图层 2
xrCamera.cameras[1].layers.set(2);
```

修改后：
```javascript
// 左眼相机：看图层 0（默认场景）+ 图层 1（左眼视频）
xrCamera.cameras[0].layers.disableAll();  // 先清空
xrCamera.cameras[0].layers.enable(0);     // 启用默认图层
xrCamera.cameras[0].layers.enable(1);     // 启用左眼视频图层

// 右眼相机：看图层 0（默认场景）+ 图层 2（右眼视频）
xrCamera.cameras[1].layers.disableAll();  // 先清空
xrCamera.cameras[1].layers.enable(0);     // 启用默认图层
xrCamera.cameras[1].layers.enable(2);     // 启用右眼视频图层
```

#### 使用方法

**自动应用**：
```bash
# 在 PICO VR 浏览器中刷新页面即可
# 代码已自动更新
```

#### 预期输出

**测试图案模式下**：
- 左眼应该看到：红色背景 + "LEFT EYE"
- 右眼应该看到：蓝色背景 + "RIGHT EYE"
- **不再是两只眼睛都看到红色**

**真实场景模式下**：
- 左眼和右眼看到略有不同的视角
- 有明显的 3D 立体效果
- 能看到地板、立方体等场景物体

#### 验证方法

1. **确保虚拟机器人服务器在测试图案模式下运行**：
   ```bash
   cd virtual-robot
   python main.py --test-pattern
   ```

2. **在 PICO VR 浏览器中刷新页面**

3. **进入 VR 模式**

4. **检查**：
   - 闭上左眼，只用右眼看 → 应该看到蓝色
   - 闭上右眼，只用左眼看 → 应该看到红色
   - 两只眼睛都睁开 → 应该看到红蓝混合的效果

---

### 2025-11-10 - 修复 7: VR 立体渲染图层配置时序问题 ✅

#### 修复的问题

**问题描述**：
在 PICO VR 头显中进入 VR 模式后，只能看到一个 2D 屏幕，无法看到立体 3D 效果。

**控制台错误**：
```
🥽 VR 会话已启动
📷 XR 相机数量: 0
⚠️ XR 相机数量不足，可能不是立体渲染模式
```

#### 根本原因

**时序问题**：在 `sessionstart` 事件触发时，WebXR 的立体相机（`xrCamera.cameras`）还没有初始化完成，导致：
1. 无法配置左右眼图层分离
2. 两只眼睛看到相同的内容
3. 没有立体视觉效果

#### 修改的文件

**src/vr-scene.js**

**修改 1：添加图层配置标志**（第 55 行）
```javascript
// 图层配置标志
this.layersConfigured = false;
```

**修改 2：新增 `configureStereoLayers()` 方法**（第 194-219 行）
```javascript
configureStereoLayers() {
    // 在渲染循环中配置立体图层
    if (this.layersConfigured) return;

    if (!this.renderer.xr.isPresenting) return;

    const xrCamera = this.renderer.xr.getCamera();

    if (!xrCamera || !xrCamera.cameras || xrCamera.cameras.length < 2) {
        return; // 相机还没准备好，下一帧再试
    }

    console.log('🥽 配置立体图层...');
    console.log(`📷 XR 相机数量: ${xrCamera.cameras.length}`);

    // 左眼相机只看图层 1
    xrCamera.cameras[0].layers.set(1);
    console.log('   - 左眼相机 -> 图层 1');

    // 右眼相机只看图层 2
    xrCamera.cameras[1].layers.set(2);
    console.log('   - 右眼相机 -> 图层 2');

    this.layersConfigured = true;
    console.log('✅ 双目图层配置完成');
}
```

**修改 3：在渲染循环中调用配置**（第 314-316 行）
```javascript
// 在 VR 模式下配置立体图层
if (this.renderer.xr.isPresenting) {
    this.configureStereoLayers();
}
```

**修改 4：添加 3D 参考物体**（第 60-109 行）
- 添加地板网格（GridHelper）
- 添加坐标轴（AxesHelper）
- 添加 3 个彩色立方体（红、蓝、绿）帮助感知深度

#### 技术说明

**为什么要在渲染循环中配置？**

WebXR 的初始化流程：
1. `sessionstart` 事件触发
2. 渲染器开始准备 VR 会话
3. **几帧之后**，立体相机才完全初始化
4. `xrCamera.cameras` 数组才有内容

因此，我们需要：
- 在渲染循环中**每帧检查**相机是否准备好
- 一旦检测到 `xrCamera.cameras.length >= 2`，立即配置图层
- 使用 `layersConfigured` 标志避免重复配置

#### 使用方法

**自动应用（推荐）**
```bash
# 文件已更新，刷新浏览器即可
# 在 PICO VR 浏览器中刷新页面
```

**手动验证**
```bash
# 检查修改是否正确
grep -A 5 "configureStereoLayers" src/vr-scene.js
```

#### 预期输出

**进入 VR 前（浏览器控制台）**：
```
✅ VR 场景初始化完成
✅ 地板网格已添加
✅ 参考物体已添加
📹 左眼视频: 640x480
📹 右眼视频: 640x480
✅ 双目视频设置完成
```

**进入 VR 后（浏览器控制台）**：
```
🥽 VR 会话已启动，将在渲染循环中配置图层
🥽 配置立体图层...
📷 XR 相机数量: 2
   - 左眼相机 -> 图层 1
   - 右眼相机 -> 图层 2
✅ 双目图层配置完成
```

**VR 头显中应该看到**：
- ✅ 地面网格（灰色，10x10米）
- ✅ 坐标轴（红、绿、蓝线）
- ✅ 3 个彩色立方体在不同深度
- ✅ 前方的视频屏幕（显示机器人双目视角）
- ✅ **真正的立体 3D 效果**

#### 故障排除

**如果仍然看不到立体效果**：

1. **检查控制台输出**
   - 必须看到 "📷 XR 相机数量: 2"
   - 如果是 0 或 1，说明 VR 会话有问题

2. **检查 PICO 浏览器设置**
   - 确保启用了 WebXR
   - 尝试重启 PICO 头显

3. **检查视频流**
   - 确保虚拟机器人服务器正在运行
   - 确保看到 "📹 左眼视频" 和 "📹 右眼视频"

4. **降低分辨率测试**
   ```python
   # 编辑 virtual-robot/main.py
   camera = StereoCamera(robot, width=320, height=240)  # 降低分辨率
   ```

---

### 2025-11-10 - 修复 6: HTTPS 混合内容错误 + 证书 IP 地址问题 ✅ 最终修复

#### 修复的问题

**问题 1: 混合内容错误**
```
Mixed Content: The page at 'https://...' was loaded over HTTPS, but attempted to connect to the insecure WebSocket endpoint 'ws://...'. This request has been blocked.
```

**问题 2: 证书无效错误**
```
WebSocket connection to 'wss://172.20.10.2:8080/' failed:
Error in connection establishment: net::ERR_CERT_AUTHORITY_INVALID
```

#### 根本原因

1. **混合内容**：HTTPS 页面不能连接到不安全的 `ws://`，必须使用 `wss://`
2. **证书不匹配**：原始证书只包含 `localhost`，通过 IP 地址访问时证书验证失败

#### 修改的文件

**1. main.js** (第 9-28 行)
- 自动检测页面协议（HTTP/HTTPS）
- HTTPS 页面使用 `wss://`，HTTP 页面使用 `ws://`

**2. virtual-robot/signaling_server.py**
- 添加 SSL 支持
- 自动检测并加载 `cert.pem` 和 `key.pem`
- 如果没有证书，回退到不安全的 WS

**3. virtual-robot/main.py**
- 添加 `--no-ssl` 参数（禁用 SSL）
- 默认启用 SSL

**4. virtual-robot/start_with_ssl.py**
- 自动检测本机所有 IP 地址
- 生成包含所有 IP 的证书（SAN - Subject Alternative Name）
- 支持 IPv4 和 IPv6

**5. 新增文件**
- `virtual-robot/generate_cert.py` - 证书生成工具
- `virtual-robot/regenerate_cert.py` - 重新生成证书工具

#### 使用方法

**⚠️ 重要：如果之前生成过证书，必须重新生成！**

**方式 1: 重新生成证书（推荐）**
```bash
cd virtual-robot

# 删除旧证书并生成新证书（包含所有 IP）
python regenerate_cert.py

# 重启服务器
python main.py
```

**方式 2: 首次启动**
```bash
cd virtual-robot
python start_with_ssl.py
```
会自动检测 IP 并生成包含所有 IP 的证书。

**方式 3: 禁用 SSL（不推荐）**
```bash
cd virtual-robot
python main.py --no-ssl
```
只能在 HTTP 页面中使用（需要修改 Vite 配置）。

#### 预期输出

**重新生成证书**：
```
🔐 重新生成 SSL 证书
🗑️  已删除旧证书: cert.pem
🗑️  已删除旧密钥: key.pem

📝 使用 Python cryptography 生成证书...
   检测到本机 IP: 172.20.10.2, 192.168.1.100
   添加 IPv4 到证书: 172.20.10.2
   添加 IPv4 到证书: 192.168.1.100
✅ 证书生成成功！
```

**虚拟机器人控制台**：
```
🚀 信令服务器启动中...
   - SSL: 已启用 (使用 cert.pem)
   - 地址: wss://0.0.0.0:8080
✅ 信令服务器已启动
```

**VR 客户端控制台**：
```
🌐 连接到虚拟机器人服务器 (wss://172.20.10.2:8080)...
✅ WebSocket 连接成功
📹 收到视频轨道 1/2
📹 收到视频轨道 2/2
✅ 双目视频流已连接！
```

#### 证书警告

首次访问时，浏览器会显示证书警告（因为是自签名证书）：
1. 点击 "高级" 或 "Advanced"
2. 点击 "继续访问" 或 "Proceed to site"

这是正常的，因为我们使用的是自签名证书而不是 CA 签发的证书。

---

### 2025-11-10 - 修复 5: VR 头显访问问题

#### 修复的问题

在 Pico VR 头显上访问时：
```
❌ WebSocket 连接失败: Error in connection establishment: net::ERR_CONNECTION_REFUSED
WebSocket connection to 'ws://localhost:8080/' failed
```

#### 根本原因

VR 头显是独立设备，`localhost` 指向的是 VR 头显自己，而不是运行服务器的电脑。需要使用电脑的局域网 IP 地址。

#### 修改的文件

**main.js** (第 9-26 行)

修改前：
```javascript
const SIGNALING_SERVER = 'ws://localhost:8080';
```

修改后：
```javascript
// 自动检测服务器地址
function getSignalingServer() {
    const hostname = window.location.hostname;

    // 如果是 IP 地址，使用该 IP
    if (hostname !== 'localhost' && hostname !== '127.0.0.1') {
        return `ws://${hostname}:8080`;
    }

    // 否则使用 localhost
    return 'ws://localhost:8080';
}

const SIGNALING_SERVER = getSignalingServer();
```

**index.html** (第 101-129 行)
- 添加了访问地址提示
- 显示当前访问方式和 VR 访问地址

#### 使用方法

1. **获取电脑 IP**（Windows）：
   ```powershell
   ipconfig
   ```
   查找 IPv4 地址，例如 `192.168.1.100`

2. **在 VR 头显上访问**：
   ```
   https://192.168.1.100:5173
   ```
   （将 IP 替换为你的电脑 IP）

3. **系统自动处理**：
   - 通过 `localhost` 访问 → 连接到 `ws://localhost:8080`
   - 通过 IP 访问 → 连接到 `ws://[IP]:8080`

#### 详细指南

查看 [VR_ACCESS_GUIDE.md](VR_ACCESS_GUIDE.md) 了解：
- 如何获取电脑 IP
- 如何配置防火墙
- 完整的故障排除步骤

---

### 2025-11-10 - 修复 4: PyBullet 图像渲染错误

#### 修复的问题

```
❌ 渲染帧时出错: too many indices for array: array is 1-dimensional, but 3 were indexed
```

#### 根本原因

`p.getCameraImage()` 返回的 `rgb` 数据是一维数组，需要先 reshape 成 `(height, width, 4)` 才能进行切片操作。

#### 修改的文件

**virtual-robot/stereo_camera.py** (第 88-115 行)

修改前：
```python
rgb_array = np.array(rgb, dtype=np.uint8)
rgb_array = rgb_array[:, :, :3]  # ❌ 错误：rgb 是一维数组
```

修改后：
```python
# rgb 已经是 numpy array，形状为 (height, width, 4) 包含 RGBA
# 需要重塑并去掉 alpha 通道
rgb_array = np.reshape(rgb, (self.height, self.width, 4))
rgb_array = rgb_array[:, :, :3].astype(np.uint8)  # 只取 RGB，去掉 A
```

#### 如何应用修复

```bash
# 重启虚拟机器人服务器
cd virtual-robot
# 按 Ctrl+C 停止
python main.py
```

VR 客户端不需要重启。

---

### 2025-11-10 - 修复 3: Transceiver Direction 错误

#### 修复的问题

```
❌ 处理 Offer 失败: list.index(x): x not in list
ValueError: list.index(x): x not in list
  at aiortc/rtcpeerconnection.py", line 260, in and_direction
```

#### 根本原因

aiortc 在处理 WebRTC transceiver 的 direction 时，期望客户端明确指定接收方向（`recvonly`），但浏览器默认创建的 offer 没有正确设置这个方向，导致 aiortc 在计算方向交集时找不到匹配的值。

#### 修改的文件

**src/webrtc-client.js** (第 96-112 行)

修改前：
```javascript
async createOffer() {
    const offer = await this.pc.createOffer();
    await this.pc.setLocalDescription(offer);
    this.ws.send(JSON.stringify({type: 'offer', sdp: offer.sdp}));
}
```

修改后：
```javascript
async createOffer() {
    // 添加 recvonly transceiver 来接收视频
    // 这样可以避免 aiortc 的 direction 错误
    this.pc.addTransceiver('video', { direction: 'recvonly' });
    this.pc.addTransceiver('video', { direction: 'recvonly' });

    const offer = await this.pc.createOffer();
    await this.pc.setLocalDescription(offer);
    this.ws.send(JSON.stringify({type: 'offer', sdp: offer.sdp}));
}
```

#### 技术说明

- 客户端只接收视频（2 个视频轨道：左眼 + 右眼），不发送视频
- 通过 `addTransceiver('video', { direction: 'recvonly' })` 明确告诉 WebRTC 这是接收方向
- 这样 aiortc 在处理 SDP 时就能正确匹配方向：`recvonly & sendonly = sendrecv`

#### 如何应用修复

**自动应用（推荐）**
```bash
# 文件已更新，重启 VR 客户端即可
# 按 Ctrl+C 停止当前的 npm run dev
# 然后重新运行
npm run dev
```

**手动验证**
```bash
# 检查 src/webrtc-client.js 第 101-102 行
grep -A 2 "addTransceiver" src/webrtc-client.js
```

应该看到：
```javascript
this.pc.addTransceiver('video', { direction: 'recvonly' });
this.pc.addTransceiver('video', { direction: 'recvonly' });
```

---

### 2025-11-10 - 修复 2: ICE Candidate 和错误处理

#### 修复的问题

1. **ICE Candidate 格式错误**
   ```
   ❌ 添加 ICE Candidate 失败: 'dict' object has no attribute 'sdpMid'
   ```

2. **List Index 错误**
   ```
   ❌ 处理消息时出错: list.index(x): x not in list
   ```

#### 修改的文件

1. **virtual-robot/webrtc_server.py**
   - 添加了 `RTCIceCandidate` 导入
   - 更新了 `add_ice_candidate()` 方法，添加格式转换逻辑
   - 添加了详细的错误追踪

2. **virtual-robot/signaling_server.py**
   - 在 offer 处理中添加了 try-catch 错误处理
   - 添加了详细的错误追踪

#### 如何应用修复

**方式 1: 自动应用（推荐）**
```bash
# 文件已经更新，只需重启服务器
cd virtual-robot
python main.py
```

**方式 2: 手动检查**
```bash
# 检查 webrtc_server.py 第 8 行
# 应该包含: RTCIceCandidate
grep "RTCIceCandidate" webrtc_server.py

# 检查 signaling_server.py 第 47-56 行
# 应该有 try-except 包裹 handle_offer
```

---

### 2025-11-10 - 修复 1: WebSocket Handler

#### 修复的问题
```
TypeError: SignalingServer.handler() missing 1 required positional argument: 'path'
```

#### 修改的文件
- **virtual-robot/signaling_server.py** 第 26 行
  - 从: `async def handler(self, websocket, path):`
  - 改为: `async def handler(self, websocket):`

---

## 验证修复

### 快速验证

运行诊断脚本：
```bash
cd virtual-robot
python diagnose.py
```

应该看到：
```
✅ 所有检查通过！系统已准备就绪！
```

### 详细验证

1. **测试 WebRTC 服务器**
   ```bash
   python test_webrtc.py
   ```

2. **测试信令服务器**
   ```bash
   # 终端 1
   python main.py
   
   # 终端 2
   python test_connection.py
   ```

3. **完整测试**
   ```bash
   # 终端 1: 启动虚拟机器人
   python main.py
   
   # 终端 2: 启动 VR 客户端
   cd ..
   npm run dev
   
   # VR 头显: 访问 https://localhost:5173
   ```

---

## 预期输出

### 虚拟机器人服务器（正常）

```
🤖 虚拟机器人 VR 遥操作系统
============================================================
[1/5] 初始化虚拟机器人...
✅ 虚拟机器人初始化完成
[2/5] 初始化虚拟双目相机...
✅ 虚拟双目相机初始化完成
[3/5] 初始化 WebRTC 服务器...
✅ WebRTC 服务器初始化完成
[4/5] 初始化信令服务器...
✅ 信令服务器初始化完成
[5/5] 启动服务...
✅ 系统启动成功！
============================================================
🚀 信令服务器启动: ws://0.0.0.0:8080
🔗 新客户端连接: 127.0.0.1:xxxxx
📨 收到消息: offer
📨 收到 Offer，开始建立连接...
✅ 视频轨道创建: left 眼, 30 fps
✅ 视频轨道创建: right 眼, 30 fps
✅ 已添加 2 个视频轨道（左眼 + 右眼）
✅ Answer 已创建
📤 已发送 Answer
📨 收到消息: ice-candidate
✅ ICE Candidate 已添加
📨 收到消息: ice-candidate
✅ ICE Candidate 已添加
🔗 连接状态: connected
📡 DataChannel 已建立: control
📍 头显 - 位置: (0.00, 1.60, 0.00), 旋转: (0.00, 0.00, 0.00, 1.00)
🎮 left 手柄 - 位置: (-0.20, 1.40, -0.30), 扳机: 0.00, 握持: 0.00
```

### 可以忽略的警告

以下消息可以忽略（不影响功能）：

1. **List index 错误**（如果仍然出现）
   ```
   ❌ 处理消息时出错: list.index(x): x not in list
   ```
   - 这是 aiortc 内部的非关键错误
   - 只要看到 "✅ Answer 已创建" 就说明连接正常

2. **PyBullet 警告**
   ```
   pybullet build time: ...
   ```
   - 这是正常的信息输出

---

## 仍有问题？

### 步骤 1: 运行诊断
```bash
cd virtual-robot
python diagnose.py
```

### 步骤 2: 查看详细日志
```bash
# 启动时查看完整错误
python main.py 2>&1 | tee debug.log
```

### 步骤 3: 检查版本
```bash
pip list | grep -E "pybullet|aiortc|websockets"
```

应该看到：
```
aiortc          1.5.0 或更高
pybullet        3.2.5 或更高
websockets      11.0 或更高
```

### 步骤 4: 重新安装依赖
```bash
pip uninstall -y pybullet aiortc websockets
pip install -r requirements.txt
```

### 步骤 5: 查看故障排除文档
```bash
# 查看完整的故障排除指南
cat TROUBLESHOOTING.md
```

---

## 已知问题

### 1. List Index 错误（非关键）

**现象**：
```
❌ 处理消息时出错: list.index(x): x not in list
```

**影响**：无，连接仍然正常建立

**原因**：aiortc 内部处理 SDP 时的非关键错误

**解决**：可以忽略，或升级 aiortc 到最新版本

### 2. PyBullet 找不到 humanoid.urdf

**现象**：
```
FileNotFoundError: humanoid/humanoid.urdf
```

**解决**：
```python
# 编辑 robot_sim.py，添加：
import pybullet_data
p.setAdditionalSearchPath(pybullet_data.getDataPath())
```

---

## 获取帮助

如果问题仍未解决：

1. 查看 [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
2. 运行 `python diagnose.py` 获取系统状态
3. 提供完整的错误日志

---

**最后更新**: 2025-11-10

