<template>
  <div class="head">
    <h2>配置工具</h2>
    <p>在灵犀平台中，为智能体配置工具，可以赋予其借助外部能力解决复杂任务的能力。
      通过任务理解、步骤拆解与工具调用，智能体能够高效自主地完成多阶段、多环节的任务处理。</p>

    <div class="section">
      <h3>工具配置</h3>
      <p>您可以为智能体添加多种工具资源，包括：</p>
      <ul>
        <li><strong>知识库：</strong>为智能体提供可查询的结构化文本资料，增强其信息检索与解答能力。</li>
        <li><strong>工作流：</strong>通过预设的流程化任务节点，帮助智能体在需要时调用复杂业务逻辑。</li>
      </ul>
    </div>

    <div class="section">
      <h3>人物设定</h3>
      <p>通过系统提示词为智能体设定角色身份、语气风格、行为边界等，赋予其特定“人格”，让交互更贴近预期场景。</p>
    </div>

    <div class="section">
      <h3>开场白</h3>
      <p>支持为智能体设置会话开场白与示例提问。开场白将在用户每次进入对话时展示，介绍智能体的能力范围与推荐提问方式，帮助用户快速了解如何与智能体互动。</p>
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