"""
虚拟机器人仿真模块
使用 PyBullet 进行物理仿真和渲染
"""
import pybullet as p
import pybullet_data
import numpy as np
import time


class VirtualRobot:
    def __init__(self, use_gui=False):
        """
        初始化虚拟机器人
        
        Args:
            use_gui: 是否显示 PyBullet GUI（调试用）
        """
        # 连接 PyBullet
        if use_gui:
            self.physics_client = p.connect(p.GUI)
        else:
            self.physics_client = p.connect(p.DIRECT)
        
        p.setAdditionalSearchPath(pybullet_data.getDataPath())
        
        # 设置重力
        p.setGravity(0, 0, -9.8)
        
        # 加载地面
        self.plane_id = p.loadURDF("plane.urdf")

        # 加载机器人模型
        try:
            # 尝试加载 R2D2 机器人
            self.robot_id = p.loadURDF(
                "r2d2.urdf",
                [0, 0, 0.5],
                useFixedBase=True,
                globalScaling=0.5
            )
            self.head_link_index = 1
        except:
            # 如果 R2D2 不可用，使用人形机器人
            self.robot_id = p.loadURDF(
                "humanoid/humanoid.urdf",
                [0, 0, 0.5],
                useFixedBase=True,
                globalScaling=0.3
            )
            self.head_link_index = 1

        # 添加一些物体到场景中（让场景更有趣）
        self._setup_scene()

        # 获取关节信息
        self.num_joints = p.getNumJoints(self.robot_id)
        self.joint_indices = list(range(self.num_joints))

        # 左右手臂的关节索引（根据 humanoid.urdf）
        self.left_arm_joints = [2, 3, 4]   # 左肩、左肘、左腕
        self.right_arm_joints = [5, 6, 7]  # 右肩、右肘、右腕
        
        # 控制参数
        self.head_target_orientation = [0, 0, 0, 1]  # 四元数
    
    def _setup_scene(self):
        """设置场景中的物体"""
        cube_positions = [
            [2.0, 0, 0.5],
            [0, 2.0, 0.5],
            [-2.0, 0, 0.5],
            [0, -2.0, 0.5]
        ]

        colors = [
            [1, 0, 0, 1],  # 红色
            [0, 1, 0, 1],  # 绿色
            [0, 0, 1, 1],  # 蓝色
            [1, 1, 0, 1]   # 黄色
        ]

        for pos, color in zip(cube_positions, colors):
            cube_collision = p.createCollisionShape(p.GEOM_BOX, halfExtents=[0.3, 0.3, 0.3])
            cube_visual = p.createVisualShape(
                p.GEOM_BOX,
                halfExtents=[0.3, 0.3, 0.3],
                rgbaColor=color
            )
            p.createMultiBody(
                baseMass=1.0,
                baseCollisionShapeIndex=cube_collision,
                baseVisualShapeIndex=cube_visual,
                basePosition=pos
            )
    
    def step_simulation(self):
        """执行一步物理模拟"""
        p.stepSimulation()
    
    def apply_vr_control(self, control_data):
        """
        根据 VR 输入控制机器人
        
        Args:
            control_data: 来自 VR 的控制数据
                {
                    'timestamp': float,
                    'headset': {
                        'position': {'x': float, 'y': float, 'z': float},
                        'rotation': {'x': float, 'y': float, 'z': float, 'w': float}
                    },
                    'controllers': [
                        {
                            'hand': 'left' | 'right',
                            'position': {'x': float, 'y': float, 'z': float},
                            'rotation': {'x': float, 'y': float, 'z': float, 'w': float},
                            'buttons': {...}
                        }
                    ]
                }
        """
        if not control_data:
            return
        
        # 获取头显数据
        headset = control_data.get('headset', {})
        head_rotation = headset.get('rotation', {})
        
        if head_rotation:
            # 提取四元数
            quat = [
                head_rotation.get('x', 0),
                head_rotation.get('y', 0),
                head_rotation.get('z', 0),
                head_rotation.get('w', 1)
            ]
            
            # 保存目标朝向（用于相机渲染）
            self.head_target_orientation = quat
    
    def get_head_pose(self):
        """
        获取机器人头部的世界坐标和朝向
        
        Returns:
            position: [x, y, z]
            orientation: [x, y, z, w] 四元数
        """
        link_state = p.getLinkState(self.robot_id, self.head_link_index)
        position = link_state[0]  # 世界坐标
        orientation = link_state[1]  # 四元数
        
        # 使用 VR 控制的朝向（如果有）
        if hasattr(self, 'head_target_orientation'):
            orientation = self.head_target_orientation
        
        return position, orientation
    
    def reset(self):
        """重置机器人到初始状态"""
        p.resetBasePositionAndOrientation(
            self.robot_id,
            [0, 0, 0.5],
            [0, 0, 0, 1]
        )

    def close(self):
        """关闭物理引擎"""
        p.disconnect()

