/**
 * 立体视频 Shader
 * 使用 gl_ViewID_OVR 或 cameraIndex 来选择左右眼纹理
 */

export const StereoVideoShader = {
    vertexShader: `
        varying vec2 vUv;
        
        void main() {
            vUv = uv;
            gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
        }
    `,
    
    fragmentShader: `
        uniform sampler2D leftTexture;
        uniform sampler2D rightTexture;
        uniform int eyeIndex;  // 0 = 左眼, 1 = 右眼
        
        varying vec2 vUv;
        
        void main() {
            if (eyeIndex == 0) {
                gl_FragColor = texture2D(leftTexture, vUv);
            } else {
                gl_FragColor = texture2D(rightTexture, vUv);
            }
        }
    `
};

