/**
 * VR 场景模块
 * 负责 Three.js 场景设置和立体渲染
 */

import * as THREE from 'three';
import { VRButton } from 'three/examples/jsm/webxr/VRButton.js';
import { StereoVideoShaderSBS } from './stereo-shader.js';

export class VRScene {
    constructor() {
        // 创建场景
        this.scene = new THREE.Scene();
        this.scene.background = new THREE.Color(0x505050);

        // 创建相机
        this.camera = new THREE.PerspectiveCamera(
            75,
            window.innerWidth / window.innerHeight,
            0.1,
            1000
        );
        this.camera.position.set(0, 1.6, 0);

        // 创建渲染器
        this.renderer = new THREE.WebGLRenderer({ antialias: true });
        this.renderer.setSize(window.innerWidth, window.innerHeight);
        this.renderer.setPixelRatio(window.devicePixelRatio);
        this.renderer.xr.enabled = true;
        document.body.appendChild(this.renderer.domElement);

        // 添加 VR 按钮
        const vrButton = VRButton.createButton(this.renderer);
        document.body.appendChild(vrButton);

        // 添加光照
        const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
        this.scene.add(ambientLight);

        const directionalLight = new THREE.DirectionalLight(0xffffff, 0.4);
        directionalLight.position.set(5, 10, 5);
        this.scene.add(directionalLight);

        // 暂时隐藏地板和参考物体，专注于视频流
        // this.addFloorGrid();
        // this.addReferenceObjects();

        // 屏幕对象
        this.leftScreen = null;
        this.rightScreen = null;
        this.leftTexture = null;
        this.rightTexture = null;

        // 手柄
        this.controllers = [];

        // 图层配置标志
        this.layersConfigured = false;

        // 窗口大小调整
        window.addEventListener('resize', () => {
            this.camera.aspect = window.innerWidth / window.innerHeight;
            this.camera.updateProjectionMatrix();
            this.renderer.setSize(window.innerWidth, window.innerHeight);
        });

        console.log('✅ VR 场景初始化完成');
    }

    addFloorGrid() {
        // 创建地板网格
        const gridHelper = new THREE.GridHelper(10, 20, 0x888888, 0x444444);
        gridHelper.position.y = 0;
        this.scene.add(gridHelper);

        // 创建坐标轴辅助线
        const axesHelper = new THREE.AxesHelper(2);
        axesHelper.position.y = 0.01;
        this.scene.add(axesHelper);

        console.log('✅ 地板网格已添加');
    }

    addReferenceObjects() {
        // 添加一些参考立方体，帮助感知3D深度
        const cubeGeometry = new THREE.BoxGeometry(0.3, 0.3, 0.3);

        // 左侧立方体（红色）
        const leftCube = new THREE.Mesh(
            cubeGeometry,
            new THREE.MeshStandardMaterial({ color: 0xff0000 })
        );
        leftCube.position.set(-1.5, 0.5, -3);
        this.scene.add(leftCube);

        // 右侧立方体（蓝色）
        const rightCube = new THREE.Mesh(
            cubeGeometry,
            new THREE.MeshStandardMaterial({ color: 0x0000ff })
        );
        rightCube.position.set(1.5, 0.5, -3);
        this.scene.add(rightCube);

        // 远处立方体（绿色）
        const farCube = new THREE.Mesh(
            cubeGeometry,
            new THREE.MeshStandardMaterial({ color: 0x00ff00 })
        );
        farCube.position.set(0, 0.5, -5);
        this.scene.add(farCube);

        console.log('✅ 参考物体已添加');
    }
    
    setupStereoVideo(leftStream, rightStream) {
        console.log('🎬 设置双目视频流...');

        // 创建左眼视频元素
        const leftVideo = document.createElement('video');
        leftVideo.srcObject = leftStream;
        leftVideo.autoplay = true;
        leftVideo.playsInline = true;
        leftVideo.muted = true;

        // 创建右眼视频元素
        const rightVideo = document.createElement('video');
        rightVideo.srcObject = rightStream;
        rightVideo.autoplay = true;
        rightVideo.playsInline = true;
        rightVideo.muted = true;

        // 等待视频加载
        leftVideo.play().catch(e => console.error('左眼视频播放失败:', e));
        rightVideo.play().catch(e => console.error('右眼视频播放失败:', e));

        // 监听视频元数据加载
        leftVideo.addEventListener('loadedmetadata', () => {
            console.log(`📹 左眼视频: ${leftVideo.videoWidth}x${leftVideo.videoHeight}`);
        });
        rightVideo.addEventListener('loadedmetadata', () => {
            console.log(`📹 右眼视频: ${rightVideo.videoWidth}x${rightVideo.videoHeight}`);
        });

        // 定期检查视频播放状态
        setInterval(() => {
            if (this.renderer.xr.isPresenting) {
                console.log('🎥 视频状态:');
                console.log(`   - 左眼: ${leftVideo.paused ? '暂停' : '播放'}, 时间: ${leftVideo.currentTime.toFixed(2)}s`);
                console.log(`   - 右眼: ${rightVideo.paused ? '暂停' : '播放'}, 时间: ${rightVideo.currentTime.toFixed(2)}s`);
            }
        }, 5000); // 每 5 秒检查一次

        // 创建视频纹理
        const leftTexture = new THREE.VideoTexture(leftVideo);
        leftTexture.minFilter = THREE.LinearFilter;
        leftTexture.magFilter = THREE.LinearFilter;
        leftTexture.format = THREE.RGBFormat;

        const rightTexture = new THREE.VideoTexture(rightVideo);
        rightTexture.minFilter = THREE.LinearFilter;
        rightTexture.magFilter = THREE.LinearFilter;
        rightTexture.format = THREE.RGBFormat;

        // 保存纹理引用
        this.leftTexture = leftTexture;
        this.rightTexture = rightTexture;

        // 🎥 方法：创建一个大的平面屏幕，填满视野
        // 使用合适的视场角和距离，让视频看起来像是真实的3D场景

        // 计算屏幕尺寸：假设 FOV = 90度，距离 = 1米
        // 屏幕宽度 = 2 * tan(FOV/2) * 距离 = 2 * tan(45°) * 1 = 2米
        const distance = 1.0;  // 屏幕距离相机 1 米
        const fov = 90;        // 视场角 90 度
        const screenWidth = 2 * Math.tan((fov * Math.PI / 180) / 2) * distance;
        const screenHeight = screenWidth * (480 / 640);  // 保持 4:3 比例

        const geometry = new THREE.PlaneGeometry(screenWidth, screenHeight);

        // 左眼屏幕
        const leftMaterial = new THREE.MeshBasicMaterial({
            map: leftTexture,
            side: THREE.FrontSide,
            depthTest: false,
            depthWrite: false
        });

        this.leftScreen = new THREE.Mesh(geometry, leftMaterial);
        this.leftScreen.position.set(0, 0, -distance);
        this.leftScreen.renderOrder = -1;  // 在最前面渲染（背景）
        this.leftScreen.layers.set(1);
        this.scene.add(this.leftScreen);

        // 右眼屏幕
        const rightMaterial = new THREE.MeshBasicMaterial({
            map: rightTexture,
            side: THREE.FrontSide,
            depthTest: false,
            depthWrite: false
        });

        this.rightScreen = new THREE.Mesh(geometry, rightMaterial);
        this.rightScreen.position.set(0, 0, -distance);
        this.rightScreen.renderOrder = -1;  // 在最前面渲染（背景）
        this.rightScreen.layers.set(2);
        this.scene.add(this.rightScreen);

        console.log('📺 视频背景已创建');
        console.log(`   - 屏幕尺寸: ${screenWidth.toFixed(2)}m x ${screenHeight.toFixed(2)}m`);
        console.log(`   - 距离: ${distance}m`);
        console.log(`   - 视场角: ${fov}°`);
        console.log('   - 左眼: 图层 1, 右眼: 图层 2');

        // 监听 VR 会话开始
        this.renderer.xr.addEventListener('sessionstart', () => {
            console.log('🥽 VR 会话已启动');
            this.layersConfigured = false;
        });

        console.log('✅ 双目视频设置完成');
    }

    setupStereoVideoSBS(stream) {
        console.log('🎬 设置 Side-by-Side 双目视频流...');

        // 创建视频元素
        const video = document.createElement('video');
        video.srcObject = stream;
        video.autoplay = true;
        video.playsInline = true;
        video.muted = true;
        video.play().catch(e => console.error('视频播放失败:', e));

        // 监听视频元数据加载
        video.addEventListener('loadedmetadata', () => {
            console.log(`📹 Side-by-Side 视频: ${video.videoWidth}x${video.videoHeight}`);
        });

        // 定期检查视频播放状态
        setInterval(() => {
            if (this.renderer.xr.isPresenting) {
                console.log('🎥 视频状态:');
                console.log(`   - Side-by-Side: ${video.paused ? '暂停' : '播放'}, 时间: ${video.currentTime.toFixed(2)}s`);
            }
        }, 5000); // 每 5 秒检查一次

        // 创建视频纹理
        const videoTexture = new THREE.VideoTexture(video);
        videoTexture.minFilter = THREE.LinearFilter;
        videoTexture.magFilter = THREE.LinearFilter;
        videoTexture.format = THREE.RGBFormat;

        // 保存纹理引用
        this.videoTexture = videoTexture;

        // 🔑 关键修复：让视频填满整个视野
        // PyBullet 相机 FOV = 90°，所以我们需要匹配这个视场角

        // 方案：将屏幕放置在相机正前方，尺寸刚好填满 90° 视场角
        const distance = 0.5;  // 屏幕距离相机 0.5 米（更近，更沉浸）
        const fov = 90;        // 视场角 90 度（匹配 PyBullet 相机）

        // 计算屏幕尺寸：tan(fov/2) * distance * 2
        const screenWidth = 2 * Math.tan((fov * Math.PI / 180) / 2) * distance;
        const screenHeight = screenWidth * (480 / 640);  // 保持 4:3 比例

        // 创建更大的平面几何体，确保填满视野
        const geometry = new THREE.PlaneGeometry(screenWidth * 1.2, screenHeight * 1.2);

        // 左眼屏幕 - 使用 Shader Material
        const leftMaterial = new THREE.ShaderMaterial({
            uniforms: {
                videoTexture: { value: videoTexture },
                eyeIndex: { value: 0 }  // 左眼
            },
            vertexShader: StereoVideoShaderSBS.vertexShader,
            fragmentShader: StereoVideoShaderSBS.fragmentShader,
            depthTest: false,
            depthWrite: false
        });

        this.leftScreen = new THREE.Mesh(geometry, leftMaterial);
        // 🔑 关键修复：不设置固定位置，而是在渲染循环中跟随相机
        this.leftScreen.renderOrder = -1;  // 在最前面渲染（背景）
        this.leftScreen.layers.set(1);
        // 暂时不添加到场景，等 VR 会话开始后再添加

        // 右眼屏幕 - 使用 Shader Material
        const rightMaterial = new THREE.ShaderMaterial({
            uniforms: {
                videoTexture: { value: videoTexture },
                eyeIndex: { value: 1 }  // 右眼
            },
            vertexShader: StereoVideoShaderSBS.vertexShader,
            fragmentShader: StereoVideoShaderSBS.fragmentShader,
            depthTest: false,
            depthWrite: false
        });

        this.rightScreen = new THREE.Mesh(geometry, rightMaterial);
        // 🔑 关键修复：不设置固定位置，而是在渲染循环中跟随相机
        this.rightScreen.renderOrder = -1;  // 在最前面渲染（背景）
        this.rightScreen.layers.set(2);
        // 暂时不添加到场景，等 VR 会话开始后再添加

        // 保存距离参数，用于后续更新位置
        this.screenDistance = distance;

        console.log('📺 Side-by-Side 视频屏幕已创建');
        console.log(`   - 屏幕尺寸: ${screenWidth.toFixed(2)}m x ${screenHeight.toFixed(2)}m (放大 1.2 倍)`);
        console.log(`   - 距离: ${distance}m (更近，更沉浸)`);
        console.log(`   - 视场角: ${fov}° (匹配 PyBullet 相机)`);
        console.log('   - 左眼: 图层 1 (采样左半部分), 右眼: 图层 2 (采样右半部分)');

        // 监听 VR 会话开始
        this.renderer.xr.addEventListener('sessionstart', () => {
            console.log('🥽 VR 会话已启动');
            this.layersConfigured = false;
        });

        console.log('✅ Side-by-Side 双目视频设置完成');
    }

    updateVideoScreenPositions() {
        /**
         * 🔑 关键方法：更新视频屏幕位置，使其跟随 VR 相机
         *
         * 问题：如果屏幕固定在世界坐标 (0, 0, -0.5)，当用户头部高度不是 0 时，
         *      屏幕会显得在脚下或头顶
         *
         * 解决方案：每帧更新屏幕位置，使其始终在相机正前方
         */
        if (!this.leftScreen || !this.rightScreen) return;
        if (!this.renderer.xr.isPresenting) return;

        const xrCamera = this.renderer.xr.getCamera();
        if (!xrCamera) return;

        // 确保屏幕已添加到场景
        if (!this.leftScreen.parent) {
            this.scene.add(this.leftScreen);
            this.scene.add(this.rightScreen);
            console.log('📺 视频屏幕已添加到场景');
        }

        // 获取相机的世界位置和方向
        const cameraPosition = new THREE.Vector3();
        const cameraQuaternion = new THREE.Quaternion();
        xrCamera.getWorldPosition(cameraPosition);
        xrCamera.getWorldQuaternion(cameraQuaternion);

        // 计算相机正前方的位置（-Z 方向）
        const forward = new THREE.Vector3(0, 0, -1);
        forward.applyQuaternion(cameraQuaternion);
        forward.multiplyScalar(this.screenDistance);

        // 设置屏幕位置：相机位置 + 前方偏移
        const screenPosition = cameraPosition.clone().add(forward);

        this.leftScreen.position.copy(screenPosition);
        this.rightScreen.position.copy(screenPosition);

        // 设置屏幕朝向：面向相机
        this.leftScreen.quaternion.copy(cameraQuaternion);
        this.rightScreen.quaternion.copy(cameraQuaternion);
    }

    configureStereoLayers() {
        // 配置立体图层
        if (this.layersConfigured) return;

        if (!this.renderer.xr.isPresenting) return;

        const xrCamera = this.renderer.xr.getCamera();

        if (!xrCamera || !xrCamera.cameras || xrCamera.cameras.length < 2) {
            return;
        }

        console.log('🥽 配置立体图层...');
        console.log(`📷 XR 相机数量: ${xrCamera.cameras.length}`);

        // 🔑 关键修复：必须同时配置 VRCamera 本身和子相机！
        // 参考: https://discourse.threejs.org/t/layers-and-webxr/17751/5

        // 1. 配置 VRCamera 本身（父相机）
        xrCamera.layers.disableAll();
        xrCamera.layers.enable(0);  // 场景
        xrCamera.layers.enable(1);  // 左眼视频
        xrCamera.layers.enable(2);  // 右眼视频
        console.log('   - VRCamera (父) -> 图层 0 + 1 + 2');

        // 2. 配置左眼相机：看图层 0（场景）+ 图层 1（左眼视频）
        xrCamera.cameras[0].layers.disableAll();
        xrCamera.cameras[0].layers.enable(0);
        xrCamera.cameras[0].layers.enable(1);
        console.log('   - 左眼相机 -> 图层 0 + 1');

        // 3. 配置右眼相机：看图层 0（场景）+ 图层 2（右眼视频）
        xrCamera.cameras[1].layers.disableAll();
        xrCamera.cameras[1].layers.enable(0);
        xrCamera.cameras[1].layers.enable(2);
        console.log('   - 右眼相机 -> 图层 0 + 2');

        this.layersConfigured = true;
        console.log('✅ 双目图层配置完成');
        console.log('');
        console.log('👀 现在应该能看到立体效果了！');
    }
    
    setupControllers() {
        console.log('🎮 设置手柄...');
        
        // 创建两个手柄
        for (let i = 0; i < 2; i++) {
            const controller = this.renderer.xr.getController(i);
            
            // 添加手柄可视化（简单的线条）
            const geometry = new THREE.BufferGeometry().setFromPoints([
                new THREE.Vector3(0, 0, 0),
                new THREE.Vector3(0, 0, -1)
            ]);
            const line = new THREE.Line(geometry);
            line.scale.z = 5;
            controller.add(line);
            
            this.scene.add(controller);
            this.controllers.push(controller);
        }
        
        console.log('✅ 手柄设置完成');
    }
    
    getInputData(frame) {
        if (!frame) return null;
        
        const session = this.renderer.xr.getSession();
        if (!session) return null;
        
        const referenceSpace = this.renderer.xr.getReferenceSpace();
        const pose = frame.getViewerPose(referenceSpace);
        
        if (!pose) return null;
        
        // 构建控制数据
        const data = {
            timestamp: performance.now(),
            headset: {
                position: {
                    x: pose.transform.position.x,
                    y: pose.transform.position.y,
                    z: pose.transform.position.z
                },
                rotation: {
                    x: pose.transform.orientation.x,
                    y: pose.transform.orientation.y,
                    z: pose.transform.orientation.z,
                    w: pose.transform.orientation.w
                }
            },
            controllers: []
        };
        
        // 获取手柄数据
        for (const source of session.inputSources) {
            if (source.gripSpace) {
                const gripPose = frame.getPose(source.gripSpace, referenceSpace);
                
                if (gripPose && source.gamepad) {
                    const controllerData = {
                        hand: source.handedness,
                        position: {
                            x: gripPose.transform.position.x,
                            y: gripPose.transform.position.y,
                            z: gripPose.transform.position.z
                        },
                        rotation: {
                            x: gripPose.transform.orientation.x,
                            y: gripPose.transform.orientation.y,
                            z: gripPose.transform.orientation.z,
                            w: gripPose.transform.orientation.w
                        },
                        buttons: {
                            trigger: source.gamepad.buttons[0]?.value || 0,
                            grip: source.gamepad.buttons[1]?.value || 0,
                            thumbstick: {
                                x: source.gamepad.axes[2] || 0,
                                y: source.gamepad.axes[3] || 0
                            }
                        }
                    };
                    
                    data.controllers.push(controllerData);
                }
            }
        }
        
        return data;
    }
    
    startRenderLoop(onFrame) {
        console.log('🔄 启动渲染循环...');

        this.renderer.setAnimationLoop((_timestamp, frame) => {
            // 在 VR 模式下配置立体图层和更新屏幕位置
            if (this.renderer.xr.isPresenting) {
                this.configureStereoLayers();
                this.updateVideoScreenPositions();  // 🔑 更新视频屏幕位置
            }

            if (onFrame) {
                onFrame(frame);
            }
            this.renderer.render(this.scene, this.camera);
        });
    }
}

