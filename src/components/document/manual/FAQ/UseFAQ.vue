<template>
  <div class="faq">
    <div class="section">
      <h2>使用问题</h2>
      <div class="faq-item">
        <h3>为什么我无法删除画布上最后一个结束节点？</h3>
        <p> 系统要求每个工作流至少保留一个结束节点，因此当画布上只剩一个结束节点时，平台会禁止删除操作。</p>
      </div>

      <div class="faq-item">
        <h3>条件分支节点分出多个流程后能否在后续合并？</h3>
        <p>当前平台暂不支持并行流程的合流。每个分支应连接到独立的结束节点，流程不能合并回统一节点。</p>
      </div>

      <div class="faq-item">
        <h3>如何调试某一个节点的逻辑是否正确？</h3>
        <p>可点击该节点，在右侧详情面板中点击「运行」按钮，配置必要输入后立即执行该节点进行单独调试。</p>
      </div>

      <div class="faq-item">
        <h3>智能体调用工作流时，是否必须配置所有输入变量？</h3>
        <p>是的。工作流作为工具接入智能体时，其所需输入变量必须事先配置完整，其描述必要清晰准确，否则调用可能失败或产生错误。</p>
      </div>

      <div class="faq-item">
        <h3>智能体可以嵌套调用另一个智能体吗？</h3>
        <p>当前平台暂未支持智能体之间的直接嵌套调用，但可以通过工作流中的智能体节点组合来间接实现功能组合。</p>
      </div>

      <div class="faq-item">
        <h3>智能体调试时能否查看其推理过程？</h3>
        <p> 使用 DeepSeek 模型时，平台支持展示推理过程，包括模型的思考路径、调用工具的选择依据等，便于理解其逻辑。</p>
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
<script setup lang="ts">
</script>