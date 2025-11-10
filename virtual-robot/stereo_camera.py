"""
虚拟双目相机模块
从 PyBullet 仿真中渲染立体视觉图像
"""
import pybullet as p
import numpy as np
import cv2


class StereoCamera:
    def __init__(self, robot_sim, width=640, height=480, fov=90, ipd=0.064):
        """
        初始化虚拟双目相机
        
        Args:
            robot_sim: VirtualRobot 实例
            width: 图像宽度
            height: 图像高度
            fov: 视场角（度）
            ipd: 瞳距（米），默认 64mm
        """
        self.robot_sim = robot_sim
        self.width = width
        self.height = height
        self.fov = fov
        self.ipd = ipd
        
        # 计算投影矩阵
        aspect = width / height
        near = 0.01
        far = 100
        self.projection_matrix = p.computeProjectionMatrixFOV(
            fov, aspect, near, far
        )
        
        print(f"✅ 虚拟双目相机初始化完成")
        print(f"   - 分辨率: {width}x{height}")
        print(f"   - 视场角: {fov}°")
        print(f"   - 瞳距: {ipd*1000:.1f}mm")
    
    def render_stereo(self):
        """
        渲染双目图像
        
        Returns:
            left_img: 左眼图像 (numpy array, BGR)
            right_img: 右眼图像 (numpy array, BGR)
        """
        # 获取机器人头部位置和朝向
        head_pos, head_orn = self.robot_sim.get_head_pose()
        
        # 将四元数转换为旋转矩阵
        rotation_matrix = p.getMatrixFromQuaternion(head_orn)
        rotation_matrix = np.array(rotation_matrix).reshape(3, 3)
        
        # 计算方向向量
        # PyBullet 的坐标系：X-前，Y-左，Z-上
        forward = rotation_matrix @ np.array([1, 0, 0])  # 前方
        up = rotation_matrix @ np.array([0, 0, 1])       # 上方
        right = rotation_matrix @ np.array([0, -1, 0])   # 右方（注意 Y 是左）
        
        # 计算左眼位置（向左偏移 IPD/2）
        left_eye_pos = np.array(head_pos) - right * (self.ipd / 2)
        left_target = left_eye_pos + forward
        
        # 计算右眼位置（向右偏移 IPD/2）
        right_eye_pos = np.array(head_pos) + right * (self.ipd / 2)
        right_target = right_eye_pos + forward
        
        # 渲染左眼
        left_view_matrix = p.computeViewMatrix(
            cameraEyePosition=left_eye_pos.tolist(),
            cameraTargetPosition=left_target.tolist(),
            cameraUpVector=up.tolist()
        )
        left_img = self._render_image(left_view_matrix)
        
        # 渲染右眼
        right_view_matrix = p.computeViewMatrix(
            cameraEyePosition=right_eye_pos.tolist(),
            cameraTargetPosition=right_target.tolist(),
            cameraUpVector=up.tolist()
        )
        right_img = self._render_image(right_view_matrix)
        
        return left_img, right_img
    
    def _render_image(self, view_matrix):
        """
        渲染单个图像

        Args:
            view_matrix: 视图矩阵

        Returns:
            img: BGR 格式的图像 (numpy array)
        """
        # 使用 PyBullet 渲染
        _, _, rgb, depth, seg = p.getCameraImage(
            width=self.width,
            height=self.height,
            viewMatrix=view_matrix,
            projectionMatrix=self.projection_matrix,
            renderer=p.ER_BULLET_HARDWARE_OPENGL  # 硬件加速
        )

        # rgb 已经是 numpy array，形状为 (height, width, 4) 包含 RGBA
        # 需要重塑并去掉 alpha 通道
        rgb_array = np.reshape(rgb, (self.height, self.width, 4))
        rgb_array = rgb_array[:, :, :3].astype(np.uint8)  # 只取 RGB，去掉 A

        # 转换为 BGR（OpenCV 格式）
        bgr_array = cv2.cvtColor(rgb_array, cv2.COLOR_RGB2BGR)

        return bgr_array
    
    def render_test_pattern(self):
        """
        渲染测试图案（用于调试）
        
        Returns:
            left_img: 左眼测试图案
            right_img: 右眼测试图案
        """
        # 左眼：红色背景
        left_img = np.zeros((self.height, self.width, 3), dtype=np.uint8)
        left_img[:, :] = (0, 0, 255)  # BGR 红色
        cv2.putText(
            left_img, "LEFT EYE", 
            (50, self.height // 2), 
            cv2.FONT_HERSHEY_SIMPLEX, 
            2, (255, 255, 255), 3
        )
        
        # 右眼：蓝色背景
        right_img = np.zeros((self.height, self.width, 3), dtype=np.uint8)
        right_img[:, :] = (255, 0, 0)  # BGR 蓝色
        cv2.putText(
            right_img, "RIGHT EYE", 
            (50, self.height // 2), 
            cv2.FONT_HERSHEY_SIMPLEX, 
            2, (255, 255, 255), 3
        )
        
        return left_img, right_img

