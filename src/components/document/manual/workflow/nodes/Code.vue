<script setup lang="ts">
import { ref } from 'vue'
import image1 from '@/assets/pictures/提取今天温度.png'
import image2 from '@/assets/pictures/最大公因数.png'
import image3 from '@/assets/pictures/拼接数据.png'

const showPreview1 = ref(false)
const openPreview1 = () => (showPreview1.value = true)
const closePreview1 = () => (showPreview1.value = false)
const showPreview2 = ref(false)
const openPreview2 = () => (showPreview2.value = true)
const closePreview2 = () => (showPreview2.value = false)
const showPreview3 = ref(false)
const openPreview3 = () => (showPreview3.value = true)
const closePreview3 = () => (showPreview3.value = false)
</script>

<template>
  <div class="head">
    <h2>代码节点</h2>

    <div class="section">
      <h3>功能</h3>
      <p>代码节点支持运行 Python 或 JavaScript 脚本，适用于算术运算、JSON 转换、文本处理等场景。
        该节点显著提升了开发者在工作流中的灵活性，允许在预设节点无法满足需求时，自定义操作变量或处理逻辑。</p>
      <p>通过配置输入和输出变量，并编写相应代码，您可以轻松实现各种自定义功能，从而简化复杂业务流程。</p>
    </div>

    <div class="section">
      <h3>应用场景</h3>
      <p>使用代码节点，您可以完成以下常见的操作：</p>
      <h4>数据化结构处理</h4>
      <p>在某些工作流场景中，节点返回的结果为非结构化或嵌套的 JSON 数据，您可以从中提取特定字段。</p>
      <p>以天气查询为例，查询结果为一个 JSON 对象数组，代码节点可用于提取“今天”的温度：</p>
      <img :src="image1" alt="提取温度" style="width: 100%; margin-top: 12px; cursor: zoom-in;" @click="openPreview1" />
      <h4>数学计算</h4>
      <p>代码节点支持执行各类数学运算，适用于需要进行计算逻辑的场景。</p>
      <p>例如，计算两个正整数的最大公因数：</p>
      <img :src="image2" alt="最大公因数" style="width: 100%; margin-top: 12px; cursor: zoom-in;" @click="openPreview2" />
      <h4>拼接数据</h4>
      <p>在某些场景中，需将多个数据源合并为统一结构，例如多个知识库检索结果、网页爬取内容或与用户输入的数据进行拼接。
        代码节点可轻松实现数据的整合处理：</p>
      <img :src="image3" alt="拼接数据" style="width: 100%; margin-top: 12px; cursor: zoom-in;" @click="openPreview3" />
    </div>
  </div>

  <!-- 图片预览遮罩层 -->
  <div v-if="showPreview1" class="preview-overlay" @click="closePreview1">
    <img :src="image1" alt="提取温度大图" class="preview-image" />
  </div>

  <!-- 图片预览遮罩层 -->
  <div v-if="showPreview2" class="preview-overlay" @click="closePreview2">
    <img :src="image2" alt="最大公因数大图" class="preview-image" />
  </div>

  <!-- 图片预览遮罩层 -->
  <div v-if="showPreview3" class="preview-overlay" @click="closePreview3">
    <img :src="image3" alt="拼接数据大图" class="preview-image" />
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