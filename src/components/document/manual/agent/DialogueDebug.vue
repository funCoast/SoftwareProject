<template>
  <div class="head">
    <h2>对话调试</h2>
    <p>在智能体编排界面右侧，开发者可以通过内置的会话框与智能体进行模拟对话，实现实时调试与效果验证。</p>
    <p>灵犀平台支持在调试过程中启用<strong>联网搜索</strong>或<strong>文件上传</strong>功能，但出于隐私保护考虑，两者不能同时开启。</p>
    <p>此外，<strong>当使用 DeepSeek 模型时，平台支持展示智能体的思考过程</strong>，帮助开发者深入理解其推理路径与响应逻辑。</p>
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
</style>
<script setup>
</script>