<template>
  <div class="faq">
    <div class="section">
      <h2>基础问题</h2>
      <div class="faq-item">
        <h3>灵犀平台是什么？</h3>
        <p>灵犀平台是一个用于构建、编排、调试和应用智能体的开发平台。它面向开发者、产品经理和运营人员，支持图形化编排、自定义模型调用和工具集成。</p>
      </div>

      <div class="faq-item">
        <h3>灵犀平台适合哪些人使用？</h3>
        <p>灵犀平台适用于 AI 应用开发者、产品经理、数据分析师、运营人员等，尤其适合希望快速构建和验证智能体原型的用户。</p>
      </div>

      <div class="faq-item">
        <h3>灵犀平台支持哪些模型？</h3>
        <p>灵犀平台支持三种主流大语言模型（LLMs），包括通义千问、DeepSeek、智谱AI，用户可按需选择和切换。</p>
      </div>

      <div class="faq-item">
        <h3>什么是“工作流编排”？</h3>
        <p>工作流编排指的是通过图形化界面将多个功能节点（如大模型、知识库检索等）有逻辑地串联起来，构建一个能自动化处理流程的工具。</p>
      </div>

      <div class="faq-item">
        <h3>灵犀平台支持无代码或低代码开发吗？</h3>
        <p>是的。通过拖拽式的节点编排、参数设置和可视化调试，即使不具备编程经验，也可以构建功能完善的智能体。</p>
      </div>

      <div class="faq-item">
        <h3>是否可以在灵犀平台中训练自己的模型？</h3>
        <p>目前灵犀平台主要以调用已有大模型为主，但支持接入私有知识库进行效果定制，适合企业级场景的定向优化。</p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.faq {
  max-width: 800px;
  margin: 0 auto;
}

h1 {
  color: #2c3e50;
  margin-bottom: 32px;
}

.section {
  margin-bottom: 40px;
}

h2 {
  color: #2c3e50;
  margin-bottom: 24px;
  padding-bottom: 8px;
  border-bottom: 2px solid #e6e6e6;
}

.faq-item {
  margin-bottom: 24px;
  padding: 20px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

h3 {
  color: #2c3e50;
  margin-bottom: 12px;
  font-size: 18px;
}

p {
  color: #606266;
  line-height: 1.6;
  margin-bottom: 12px;
}

ul {
  color: #606266;
  line-height: 1.6;
  padding-left: 24px;
  margin-top: 8px;
}

li {
  margin-bottom: 8px;
}
</style>
<script setup>
</script>