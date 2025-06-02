<script setup lang="ts">
import { ref } from 'vue'
import image1 from '@/assets/pictures/对话调试.png'

const showPreview = ref(false)
const openPreview = () => (showPreview.value = true)
const closePreview = () => (showPreview.value = false)
</script>

<template>
  <div class="head">
    <h2>对话调试</h2>
    <p>在智能体编排界面右侧，开发者可以通过内置的会话框与智能体进行模拟对话，实现实时调试与效果验证。</p>
    <p>灵犀平台支持在调试过程中启用<strong>联网搜索</strong>或<strong>文件上传</strong>功能，但出于隐私保护考虑，两者不能同时开启。</p>
    <p>此外，<strong>当使用 DeepSeek 模型时，平台支持展示智能体的思考过程</strong>，帮助开发者深入理解其推理路径与响应逻辑。</p>
    <img :src="image1" alt="对话调试" style="width: 100%; margin-top: 12px; cursor: zoom-in;" @click="openPreview" />
  </div>

  <!-- 图片预览遮罩层 -->
  <div v-if="showPreview" class="preview-overlay" @click="closePreview">
    <img :src="image1" alt="对话调试大图" class="preview-image" />
  </div>
</template>

<style scoped>
.head {
  max-width: 800px;
  margin: 0 auto;
}

h2 {
  color: #2c3e50;
  margin-bottom: 24px;
}

.section {
  margin-bottom: 32px;
}

h3 {
  color: #2c3e50;
  margin-bottom: 16px;
  padding-bottom: 8px;
  border-bottom: 2px solid #e6e6e6;
}

p {
  color: #606266;
  line-height: 1.6;
  margin-bottom: 16px;
}

ul {
  color: #606266;
  line-height: 1.6;
  padding-left: 24px;
}

li {
  margin-bottom: 8px;
}

.preview-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background: rgba(0, 0, 0, 0.75);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 999;
  cursor: zoom-out;
}

.preview-image {
  max-width: 90vw;
  max-height: 90vh;
  border-radius: 8px;
  box-shadow: 0 0 20px rgba(0, 0, 0, 0.3);
}
</style>