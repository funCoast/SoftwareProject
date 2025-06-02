<script setup lang="ts">
import { ref } from 'vue'
import image1 from '@/assets/pictures/发布与下架.png'

const showPreview = ref(false)
const openPreview = () => (showPreview.value = true)
const closePreview = () => (showPreview.value = false)
</script>

<template>
  <div class="head">
    <h2>发布与下架</h2>
    <p>当开发者完成智能体的调试后，可在编排界面右上角点击 “发布智能体” 提交审核。审核通过后，智能体将成功发布，并在社区页面展示，供其他用户使用或进行二次创作。</p>
    <p>如需修改已发布的智能体，开发者可选择 “下架” 操作，完成后即可重新进入编排流程，并再次提交发布申请。</p>
    <img :src="image1" alt="发布与下架" style="width: 100%; margin-top: 12px; cursor: zoom-in;" @click="openPreview" />
  </div>

  <!-- 图片预览遮罩层 -->
  <div v-if="showPreview" class="preview-overlay" @click="closePreview">
    <img :src="image1" alt="发布与下架大图" class="preview-image" />
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