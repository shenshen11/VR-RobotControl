// vite.config.js

import { defineConfig } from 'vite'
import basicSsl from '@vitejs/plugin-basic-ssl'

export default defineConfig({
  // base: "./", // 在开发阶段，base 通常不需要设置，部署时才需要
  plugins: [
    basicSsl() // 启用 SSL 插件
  ],
  server: {
    // host: '0.0.0.0' 或 true，都表示监听所有地址
    host: true, // 关键：将服务器暴露到局域网
    https: true, // 关键：启用 HTTPS
    open: true, // 建议设为 false，避免每次都自动打开本地浏览器
    port: 3000, // 保持你习惯的 3000 端口
  },
})