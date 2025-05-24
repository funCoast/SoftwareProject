<template>
  <div class="head">
    <h2>智能体节点</h2>

    <div class="section">
      <h3>功能</h3>
      <p>智能体节点用于在工作流中与其他已发布的智能体进行交互，调动其已有的能力资源（如知识库、工作流等），实现模块化、协同式处理任务。
        通过调用智能体，当前工作流可高效复用已构建的智能服务，提升整体流程的灵活性与可扩展性。其具备以下特性：</p>
      <ul>
        <li>仅支持调用已发布的智能体；</li>
        <li>可向目标智能体传递输入变量，并获取其输出结果；</li>
        <li>支持在多智能体之间构建协同链路，实现复杂任务的解耦执行。</li>
      </ul>
    </div>

    <div class="section">
      <h3>应用场景</h3>
      <ul>
        <li><strong>任务拆解：</strong>主流程调用多个子智能体分别处理不同子任务，最终汇总结果；</li>
        <li><strong>能力复用：</strong>在多个工作流中共用某个功能智能体（如FAQ问答、知识检索等）；</li>
        <li><strong>跨域协作：</strong>实现多个专业智能体之间的信息流转与能力衔接。</li>
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