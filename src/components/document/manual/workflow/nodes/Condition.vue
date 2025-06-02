<script setup lang="ts">
import { ref } from 'vue'
import image1 from '@/assets/pictures/条件分支.png'

const showPreview = ref(false)
const openPreview = () => (showPreview.value = true)
const closePreview = () => (showPreview.value = false)
</script>

<template>
  <div class="head">
    <h2>条件分支节点</h2>

    <div class="section">
      <h3>功能</h3>
      <p>条件分支节点用于根据设定的 if / elif / else 条件，将工作流流程拆分为多个分支路径，实现逻辑判断与流程分流。
        通过该节点，工作流可以根据不同的输入情况，执行不同的操作逻辑，提升流程的智能化和灵活性。</p>
    </div>

    <div class="section">
      <h3>配置方式</h3>
      <p>您可通过配置输入变量来获取判断条件所需的值，并点击“添加分支”设置各分支的条件与流向。每个分支需指定一个跳转的目标节点。</p>
      <p>系统支持以下常用的条件判断类型：</p>
      <ul>
        <li><strong>包含 / 不包含</strong></li>
        <li><strong>开始是 / 结束是</strong></li>
        <li><strong>是 / 不是</strong></li>
        <li><strong>为空 / 不为空</strong></li>
      </ul>
      <p>对于更复杂的判断逻辑，支持设置多个条件组合，并通过“且（AND）”或“或（OR）”的逻辑关系进行组合，实现更精细的分支控制。</p>
    </div>

    <div class="section">
      <h3>应用场景</h3>
      <img :src="image1" alt="条件分支" style="width: 100%; margin-top: 12px; cursor: zoom-in;" @click="openPreview" />
    </div>

    <!-- 图片预览遮罩层 -->
    <div v-if="showPreview" class="preview-overlay" @click="closePreview">
      <img :src="image1" alt="条件分支大图" class="preview-image" />
    </div>
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