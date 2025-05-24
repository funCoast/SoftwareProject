<template>
  <div class="head">
    <h2>智能体简介</h2>
    <p>智能体（Agent）是灵犀平台的核心功能之一，能够理解复杂需求，制定执行方案，并通过调用平台上的工具自动完成整个任务过程。</p>

    <div class="section">
      <h3>什么是智能体？</h3>
      <p><strong>智能体是灵犀平台中基于大语言模型构建的任务自动化执行单元。</strong>
        它能够模拟人类思维过程，自主完成目标规划、任务拆解与多工具协同调用，并在无需人工干预的情况下，自动完成复杂任务。</p>
      <p>智能体集成了大模型的强推理能力和平台已有资源（如知识库、工作流等），具备感知、思考、决策与执行的能力，能够处理跨步骤、跨工具的复合型需求。</p>
      <p>通过智能体，您可以：</p>
      <ul>
        <li>构建具备自主决策能力的任务执行体，自动完成复杂问题的全流程处理；</li>
        <li>结合已有知识库与工作流，实现智能体在推理过程中灵活选择和调用外部工具；</li>
        <li>实现业务流程的高度自动化，减少人工参与，提高系统智能性与执行效率。</li>
      </ul>
    </div>

    <div class="section">
      <h3>智能体的特点</h3>
      <ul>
        <li><strong>自主推理与任务规划：</strong>通过 LLM 理解用户意图并生成多步任务执行计划；</li>
        <li><strong>多工具协同调用：</strong>可根据需求动态调用知识库和工作流等平台工具；</li>
        <li><strong>可组合性强：</strong>智能体可作为工作流中的节点灵活接入从而实现嵌套调用；</li>
      </ul>
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
</style>
<script setup lang="ts">
</script>