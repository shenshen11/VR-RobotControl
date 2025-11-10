/**
 * 立体视频 Shader
 * 支持双纹理模式和 Side-by-Side 模式
 */

// 双纹理模式（原有方案）
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

// Side-by-Side 模式（新方案）
export const StereoVideoShaderSBS = {
    vertexShader: `
        varying vec2 vUv;

        void main() {
            vUv = uv;
            gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
        }
    `,

    fragmentShader: `
        uniform sampler2D videoTexture;  // Side-by-Side 视频纹理
        uniform int eyeIndex;  // 0 = 左眼, 1 = 右眼

        varying vec2 vUv;

        void main() {
            vec2 uv = vUv;

            if (eyeIndex == 0) {
                // 左眼：采样左半部分 (U: 0.0 ~ 0.5)
                uv.x = uv.x * 0.5;
            } else {
                // 右眼：采样右半部分 (U: 0.5 ~ 1.0)
                uv.x = uv.x * 0.5 + 0.5;
            }

            gl_FragColor = texture2D(videoTexture, uv);
        }
    `
};

