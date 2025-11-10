"""
调试工具：保存相机渲染的图像到文件
用于检查机器人视角是否正确
"""
import cv2
import os
from robot_sim import VirtualRobot
from stereo_camera import StereoCamera


def save_camera_images(output_dir="debug_output"):
    """
    保存相机渲染的图像到文件
    
    Args:
        output_dir: 输出目录
    """
    print("=" * 60)
    print("🔍 相机调试工具")
    print("=" * 60)
    
    # 创建输出目录
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"📁 创建输出目录: {output_dir}")
    
    # 1. 初始化虚拟机器人（不显示 GUI）
    print("\n[1/3] 初始化虚拟机器人...")
    robot = VirtualRobot(use_gui=False)
    print("✅ 虚拟机器人初始化完成")
    
    # 2. 初始化虚拟相机
    print("\n[2/3] 初始化虚拟相机...")
    camera = StereoCamera(robot, width=640, height=480)
    print("✅ 虚拟相机初始化完成")
    
    # 3. 渲染并保存图像
    print("\n[3/3] 渲染并保存图像...")
    
    # 渲染真实场景
    print("\n📸 渲染真实场景...")
    left_img, right_img = camera.render_stereo()
    
    left_path = os.path.join(output_dir, "left_eye.png")
    right_path = os.path.join(output_dir, "right_eye.png")
    
    cv2.imwrite(left_path, left_img)
    cv2.imwrite(right_path, right_img)
    
    print(f"✅ 左眼图像已保存: {left_path}")
    print(f"✅ 右眼图像已保存: {right_path}")
    print(f"   - 分辨率: {left_img.shape[1]}x{left_img.shape[0]}")
    
    # 渲染测试图案
    print("\n🎨 渲染测试图案...")
    test_left, test_right = camera.render_test_pattern()
    
    test_left_path = os.path.join(output_dir, "test_left_eye.png")
    test_right_path = os.path.join(output_dir, "test_right_eye.png")
    
    cv2.imwrite(test_left_path, test_left)
    cv2.imwrite(test_right_path, test_right)
    
    print(f"✅ 测试图案（左眼）已保存: {test_left_path}")
    print(f"✅ 测试图案（右眼）已保存: {test_right_path}")
    
    # 创建并排对比图
    print("\n🖼️  创建并排对比图...")
    comparison = cv2.hconcat([left_img, right_img])
    comparison_path = os.path.join(output_dir, "stereo_comparison.png")
    cv2.imwrite(comparison_path, comparison)
    print(f"✅ 并排对比图已保存: {comparison_path}")
    
    test_comparison = cv2.hconcat([test_left, test_right])
    test_comparison_path = os.path.join(output_dir, "test_comparison.png")
    cv2.imwrite(test_comparison_path, test_comparison)
    print(f"✅ 测试图案对比图已保存: {test_comparison_path}")
    
    print("\n" + "=" * 60)
    print("✅ 调试图像保存完成！")
    print("=" * 60)
    print(f"\n📂 输出目录: {os.path.abspath(output_dir)}")
    print("\n请检查以下文件：")
    print(f"  1. {left_path} - 左眼真实场景")
    print(f"  2. {right_path} - 右眼真实场景")
    print(f"  3. {comparison_path} - 左右眼对比")
    print(f"  4. {test_left_path} - 左眼测试图案（红色）")
    print(f"  5. {test_right_path} - 右眼测试图案（蓝色）")
    print(f"  6. {test_comparison_path} - 测试图案对比")
    print("\n💡 提示：")
    print("  - 如果真实场景图像是空白或全黑，说明相机位置有问题")
    print("  - 如果测试图案正常，说明渲染管道工作正常")
    print("  - 左右眼图像应该有轻微的视差（物体位置略有不同）")


if __name__ == "__main__":
    save_camera_images()

