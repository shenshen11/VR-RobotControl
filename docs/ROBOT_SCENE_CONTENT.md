# Robot 场景内容详解

## 📦 场景组成

PyBullet 虚拟机器人场景包含以下元素：

---

## 1️⃣ 人形机器人（Humanoid）

### 基本信息
- **模型文件**：`humanoid/humanoid.urdf`（PyBullet 自带）
- **初始位置**：`[0, 0, 0.9]`（离地面 0.9 米）
- **固定基座**：`False`（可以移动和倒下）
- **机器人 ID**：`self.robot_id`

### 关节结构
```python
# 关节数量
self.num_joints = p.getNumJoints(self.robot_id)  # 约 30+ 个关节

# 关键关节索引
self.head_link_index = 1        # 头部链接
self.left_arm_joints = [2, 3, 4]   # 左肩、左肘、左腕
self.right_arm_joints = [5, 6, 7]  # 右肩、右肘、右腕
```

### 机器人外观
```
        ●  ← 头部 (link 1)
       /|\
      / | \
     /  |  \
    ●   ●   ●  ← 肩膀
    |   |   |
    ●   ●   ●  ← 肘部
    |   |   |
    ●   ●   ●  ← 手腕
        |
       / \
      /   \
     ●     ●  ← 髋部
     |     |
     ●     ●  ← 膝盖
     |     |
     ●     ●  ← 脚踝
```

### 头部位置和朝向
```python
def get_head_pose(self):
    """获取机器人头部的世界坐标和朝向"""
    link_state = p.getLinkState(self.robot_id, self.head_link_index)
    position = link_state[0]      # [x, y, z]
    orientation = link_state[1]   # [x, y, z, w] 四元数
    
    # 如果有 VR 控制数据，使用 VR 头显的朝向
    if hasattr(self, 'head_target_orientation'):
        orientation = self.head_target_orientation
    
    return position, orientation
```

**关键点**：
- 双目相机安装在机器人头部（`head_link_index = 1`）
- VR 用户的头部转动会控制机器人头部朝向
- 相机视角 = 机器人"眼睛"看到的世界

---

## 2️⃣ 彩色立方体（4个）

### 立方体配置
```python
cube_positions = [
    [1, 0, 0.5],   # 前方（X轴正方向）- 红色
    [0, 1, 0.5],   # 左侧（Y轴正方向）- 绿色
    [-1, 0, 0.5],  # 后方（X轴负方向）- 蓝色
    [0, -1, 0.5]   # 右侧（Y轴负方向）- 黄色
]

colors = [
    [1, 0, 0, 1],  # 红色 (RGBA)
    [0, 1, 0, 1],  # 绿色
    [0, 0, 1, 1],  # 蓝色
    [1, 1, 0, 1]   # 黄色
]
```

### 立方体属性
- **尺寸**：0.2m × 0.2m × 0.2m（边长 20cm）
- **质量**：0.5 kg
- **高度**：0.5m（离地面）
- **物理属性**：有碰撞体积，可以被推动

### 场景俯视图
```
            Y轴 (左)
             ↑
             │
             │  🟢 绿色立方体
             │  (0, 1, 0.5)
             │
             │
🟦 蓝色 ─────┼───── 🟥 红色
(-1,0,0.5)   │      (1, 0, 0.5)
             │
             │  🤖 机器人
             │  (0, 0, 0.9)
             │
             │  🟨 黄色立方体
             │  (0, -1, 0.5)
             │
             └──────────→ X轴 (前)
```

### 场景侧视图
```
高度 (Z轴)
  ↑
  │
1.0m    🤖 机器人头部
  │     ●
  │    /|\
0.9m   | |  ← 机器人身体
  │    | |
  │   / | \
0.5m 🟥 🟢 🟦 🟨  ← 立方体
  │
  │
0.0m ═══════════  ← 地面
```

---

## 3️⃣ 地面平面（Plane）

### 基本信息
- **模型文件**：`plane.urdf`（PyBullet 自带）
- **位置**：`[0, 0, 0]`（Z = 0）
- **尺寸**：无限大平面
- **颜色**：灰白色

### 物理属性
- **摩擦系数**：默认值
- **碰撞检测**：启用
- **作用**：防止物体掉落，提供物理支撑

---

## 4️⃣ 双目相机系统

### 相机参数
```python
width = 640        # 图像宽度
height = 480       # 图像高度
fov = 90           # 视场角（度）
ipd = 0.064        # 瞳距（米）= 64mm
```

### 相机位置计算

**坐标系（PyBullet）：**
- **X轴**：前方（Forward）
- **Y轴**：左侧（Left）
- **Z轴**：上方（Up）

**左眼相机：**
```python
# 1. 获取头部位置和朝向
head_pos = [x, y, z]
head_orn = [qx, qy, qz, qw]  # 四元数

# 2. 计算右向量
rotation_matrix = quaternion_to_matrix(head_orn)
right = rotation_matrix @ [0, -1, 0]  # 注意：Y是左，所以右是-Y

# 3. 左眼位置 = 头部位置 - 右向量 × 32mm
left_eye_pos = head_pos - right * 0.032
```

**右眼相机：**
```python
# 右眼位置 = 头部位置 + 右向量 × 32mm
right_eye_pos = head_pos + right * 0.032
```

### 相机视角示意图
```
俯视图：

        左眼相机          右眼相机
           ●                ●
            \              /
             \            /
              \          /
               \        /
                \      /
                 \    /
                  \  /
                   ●  ← 头部中心
                   
        ←─ 64mm ─→
        (瞳距 IPD)
```

### 视场角（FOV）
```
侧视图：

         90° 视场角
          ╱│╲
         ╱ │ ╲
        ╱  │  ╲
       ╱   │   ╲
      ╱    │    ╲
     ╱     │     ╲
    ╱      ●      ╲  ← 相机
   ╱     相机      ╲
  ╱                 ╲
 ╱___________________╲
    可见范围
```

---

## 5️⃣ 物理仿真参数

### 重力设置
```python
p.setGravity(0, 0, -9.8)  # 标准地球重力
```

### 仿真频率
- **物理步进**：240 Hz（每秒 240 次）
- **视频帧率**：30 fps（可配置到 60 fps）
- **控制频率**：60 Hz（VR 输入数据）

### 时间步长
```python
# 每次调用 p.stepSimulation() 推进 1/240 秒
time_step = 1.0 / 240.0  # ≈ 4.17ms
```

---

## 🎬 场景渲染效果

### 从机器人视角看到的内容

**正前方（X轴正方向）：**
- 🟥 红色立方体（距离 1 米）
- 地面平面

**左侧（Y轴正方向）：**
- 🟢 绿色立方体（距离 1 米）

**右侧（Y轴负方向）：**
- 🟨 黄色立方体（距离 1 米）

**后方（X轴负方向）：**
- 🟦 蓝色立方体（距离 1 米）

**上方：**
- 天空（灰色背景）

**下方：**
- 地面平面
- 机器人自己的身体（部分可见）

---

## 🔄 VR 控制交互

### 头部控制
```python
def apply_vr_control(self, control_data):
    # 获取 VR 头显的旋转数据
    headset = control_data.get('headset', {})
    head_rotation = headset.get('rotation', {})
    
    # 提取四元数
    quat = [
        head_rotation.get('x', 0),
        head_rotation.get('y', 0),
        head_rotation.get('z', 0),
        head_rotation.get('w', 1)
    ]
    
    # 保存目标朝向（用于相机渲染）
    self.head_target_orientation = quat
```

**效果**：
- VR 用户转头 → 机器人头部朝向改变 → 相机视角改变
- 实时响应，延迟 < 100ms

### 手柄控制（TODO）
```python
# 当前只打印手柄数据
controllers = control_data.get('controllers', [])
for controller in controllers:
    hand = controller.get('hand')  # 'left' 或 'right'
    position = controller.get('position')
    buttons = controller.get('buttons')
    
    # TODO: 实现逆运动学，控制机器人手臂
```

---

## 📊 场景数据统计

| 项目 | 数量/数值 |
|------|----------|
| **物体总数** | 6 个（1 机器人 + 4 立方体 + 1 地面） |
| **关节数量** | 30+ 个（机器人） |
| **相机数量** | 2 个（左眼 + 右眼） |
| **渲染分辨率** | 640×480 × 2 |
| **场景范围** | 约 2m × 2m × 2m |
| **物理仿真频率** | 240 Hz |
| **视频帧率** | 30 fps |

---

## 🎨 视觉效果特点

### 1. 立体深度感
由于左右眼视差（64mm），用户可以感知到：
- 立方体的 3D 位置
- 距离远近
- 物体大小

### 2. 沉浸式视角
- 从机器人"眼睛"观察世界
- 头部转动时视角跟随
- 360° 环视场景

### 3. 真实物理
- 立方体受重力影响
- 碰撞检测
- 物理交互（未来可实现）

---

## 🔧 调试和可视化

### 启动 PyBullet GUI
```bash
python main.py --gui
```

**效果**：
- 打开 PyBullet 可视化窗口
- 可以看到完整的 3D 场景
- 方便调试相机位置和朝向

### 测试图案模式
```bash
python main.py --test-pattern
```

**效果**：
- 左眼：红色背景 + "LEFT EYE" 文字
- 右眼：蓝色背景 + "RIGHT EYE" 文字
- 用于验证立体视频渲染

---

## 📝 扩展场景

### 添加更多物体
```python
def _setup_scene(self):
    # 添加球体
    sphere_collision = p.createCollisionShape(p.GEOM_SPHERE, radius=0.1)
    sphere_visual = p.createVisualShape(
        p.GEOM_SPHERE, 
        radius=0.1,
        rgbaColor=[1, 0, 1, 1]  # 紫色
    )
    p.createMultiBody(
        baseMass=0.3,
        baseCollisionShapeIndex=sphere_collision,
        baseVisualShapeIndex=sphere_visual,
        basePosition=[0.5, 0.5, 0.5]
    )
```

### 加载自定义 URDF
```python
# 加载其他机器人模型
custom_robot = p.loadURDF(
    "path/to/custom_robot.urdf",
    [x, y, z],
    [qx, qy, qz, qw]
)
```

### 添加纹理和材质
```python
# 加载纹理
texture_id = p.loadTexture("path/to/texture.png")

# 应用到物体
p.changeVisualShape(
    objectUniqueId=cube_id,
    linkIndex=-1,
    textureUniqueId=texture_id
)
```

---

## 🎯 总结

Robot 场景是一个简单但完整的 3D 虚拟环境，包含：

✅ **人形机器人**：作为视角载体  
✅ **彩色立方体**：提供视觉参考和深度感  
✅ **地面平面**：物理支撑  
✅ **双目相机**：模拟人眼立体视觉  
✅ **物理仿真**：真实的重力和碰撞  

这个场景为 VR 遥操作提供了基础平台，未来可以扩展为更复杂的任务场景（如装配、抓取等）。

