<template>
  <div class="head">
    <h2>产品简介</h2>
    <p>灵犀AI智能体社区是一款面向非技术用户与开发者的零代码智能体创作与管理平台，致力于以低门槛、高效率、强扩展性的方式推动AI智能体在教育、企业及公共服务等领域的广泛应用。
      平台核心理念在于“人人可开发，智能即服务”，以可视化工作流、知识库动态关联及完善的内容审查机制为支撑，构建了一个集智能体创作、模板共享、知识管理与生态治理于一体的创新社区。</p>

    <div class="section">
      <h3>核心功能特色</h3>
      <ul>
        <li>
          <strong>零代码智能体创作机制：</strong>
          平台通过拖拽式节点连接构建智能体逻辑，节点涵盖大模型调用、知识检索、条件判断等常用功能，用户无需掌握任何编程语言或API语法，即可构建复杂的交互式AI系统，极大降低了智能体开发的技术门槛。
        </li>
        <li>
          <strong>垂直模板生态与人设定制：</strong>
          社区预置超过多类高适配性场景模板，涵盖校园导览、健康咨询、客服应答等多个垂直领域。用户可一键复用并自定义角色设定、对话规则与触发条件，实现智能体行为的高度个性化与复用扩展。
        </li>
        <li>
          <strong>知识库构建与智能关联：</strong>
          系统支持上传PDF、TXT、Markdown等常见格式的知识文件，自动完成关键信息提取与向量化索引。智能体在响应用户问题时，可动态匹配相关知识段落并生成带溯源引用的回答，提升内容的可信度与专业性，例如基于校历内容自动解答节假日安排。
        </li>
        <li>
          <strong>安全合规与内容审查体系：</strong>
          为保障平台生态安全，灵犀社区建立了多层次审查机制。管理员可对每个智能体实施敏感词检测、内容审核等合规检查，未通过审核的智能体将被转入“隔离运行”环境，无法访问外部API或对外传播，且平台及时通知开发者发布内容所出现的问题，支持开发者据此进行整改优化。
        </li>
        <li>
          <strong>典型应用与场景适配：</strong>
          平台已上线多项北航特色智能体，包括“航概知识问答助手”、“北航导师选择推荐”等，验证了平台在高频校园服务场景中的落地能力与拓展潜力。
        </li>
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