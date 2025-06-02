<script setup lang="ts">
import { ref } from 'vue'
import image1 from '@/assets/pictures/多个结束节点.png'

const showPreview = ref(false)
const openPreview = () => (showPreview.value = true)
const closePreview = () => (showPreview.value = false)
</script>

<template>
  <div class="head">
    <h2>结束节点</h2>

    <div class="section">
      <h3>功能</h3>
      <p>结束节点定义了工作流执行完成后的最终输出内容。<strong>为了确保工作流完整运行，必须至少包含一个结束节点，用于输出整个流程的最终结果。</strong>
        作为流程的终止节点，结束节点后不能再添加其他节点，工作流只有运行至结束节点时才会产生执行结果输出。</p>
      <p>在存在多分支的工作流中，可能需要定义多个结束节点，以覆盖所有可能的执行路径。结束节点需要声明一个或多个输出变量，这些变量可以引用流程中任意上游节点的输出内容。</p>
      <img :src="image1" alt="多个结束节点示例" style="width: 100%; margin-top: 12px; cursor: zoom-in;" @click="openPreview" />
    </div>
  </div>

  <!-- 图片预览遮罩层 -->
  <div v-if="showPreview" class="preview-overlay" @click="closePreview">
    <img :src="image1" alt="多个结束节点大图" class="preview-image" />
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