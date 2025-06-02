<script setup lang="ts">
import { ref } from 'vue'
import image1 from '@/assets/pictures/知识库.png'

const showPreview = ref(false)
const openPreview = () => (showPreview.value = true)
const closePreview = () => (showPreview.value = false)
</script>

<template>
  <div class="head">
    <h2>知识库检索节点</h2>

    <div class="section">
      <h3>功能</h3>
      <p><strong>知识库检索节点用于从预先构建的知识库中提取与用户问题或所给关键词相关的文本信息。</strong>
        该节点可将检索结果作为上下文传递给下游的大语言模型节点，从而为其生成更准确、相关性更强的回答提供支持。</p>
    </div>

    <div class="section">
      <h3>应用场景</h3>
      <p>常见情景：构建基于外部数据/知识的 AI 问答系统。</p>
      <p>下图为一个最基础的知识库问答应用示例，该流程的执行逻辑为：知识库检索作为 LLM 节点的前置步骤，在用户问题传递至 LLM 节点之前，
        先在知识检索节点内将匹配用户问题最相关的文本内容并召回，随后<strong>在 LLM 节点内将检索到的上下文作为系统提示词，用户问题作为用户提示词</strong>，让 LLM 根据检索内容来回复问题。</p>
      <img :src="image1" alt="知识库" style="width: 100%; margin-top: 12px; cursor: zoom-in;" @click="openPreview" />
    </div>

    <!-- 图片预览遮罩层 -->
    <div v-if="showPreview" class="preview-overlay" @click="closePreview">
      <img :src="image1" alt="知识库大图" class="preview-image" />
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