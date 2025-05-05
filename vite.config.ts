import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import AutoImport from 'unplugin-auto-import/vite'
import Components from 'unplugin-vue-components/vite'
import { ElementPlusResolver } from 'unplugin-vue-components/resolvers'

export default defineConfig({
  // ...
  plugins: [
    vue(),
    AutoImport({
      resolvers: [ElementPlusResolver()],
    }),
    Components({
      resolvers: [ElementPlusResolver()],
    }),
  ],
  server: {
    host: '0.0.0.0', // 这个用于启动
    port: 8080, // 指定启动端口
    open: true, //启动后是否自动打开浏览器
    proxy: {
      '/api': {
          target: 'http://122.9.33.84:8000/',
          // target: 'http://127.0.0.1:8000/',
          changeOrigin: true,
          rewrite:(path)=>path.replace(/^\/api/, '/'),
      }
    }
  }
})