<template>
  <div class="workflow-intro">
    <h2>工作流简介</h2>
    <p>工作流是灵犀平台的核心功能之一，它允许用户通过可视化方式编排多个节点，实现复杂的业务逻辑。</p>

    <div class="section">
      <h3>什么是工作流？</h3>
      <p>工作流是一种将多个智能体连接起来，形成自动化处理流程的工具。</p>
      <p>工作流通过将复杂的任务分解成较小的步骤（节点）降低系统复杂度，减少了对提示词技术和模型推理能力的依赖，提高了 LLM 应用面向复杂任务的性能，提升了系统的可解释性、稳定性和容错性。</p>
      <p>通过工作流，您可以：</p>
      <ul>
        <li>将多个节点串联起来，形成完整的处理链路</li>
        <li>实现数据在不同节点之间的传递和转换</li>
        <li>通过多分支实现复杂的业务逻辑</li>
      </ul>
    </div>

    <div class="section">
      <h3>工作流的特点</h3>
      <ul>
        <li>可视化编排：通过拖拽方式连接节点，直观易懂</li>
        <li>灵活配置：支持多种节点类型和参数配置</li>
        <li>实时调试：提供试运行功能，方便调试和优化</li>
      </ul>
    </div>
  </div>
</template>

<style scoped>
.workflow-intro {
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