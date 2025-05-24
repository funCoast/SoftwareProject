<template>
  <div class="head">
    <h2>知识库简介</h2>
    <p>知识库（KnowledgeBase）是灵犀平台的核心功能之一，开发者将智能体可能用到的信息存储在知识库中，帮助智能体快速获取知识、解答问题或支持决策。</p>

    <div class="section">
      <h3>什么是知识库？</h3>
      <p><strong>知识库是一个存储和组织知识的信息系统或数据集合，用于保存、管理和访问结构化或非结构化的信息。</strong>
        当智能体需要根据某些专业知识或特殊数据作出回复时，从知识库中检索是高效可靠的方式。</p>
      <p>通过知识库，您可以：</p>
      <ul>
        <li>用定制化数据补充或覆盖通用知识</li>
        <li>灵活更新知识库内容，保持信息时效性</li>
        <li>显著提升智能体回复质量和效率</li>
      </ul>
    </div>

    <div class="section">
      <h3>知识库的特点</h3>
      <ul>
        <li><strong>支持多种类型：</strong>灵犀目前支持文本、图片、表格类型的知识库</li>
        <li><strong>操作简便：</strong>提供对文件内容的自动解析，帮助开发者快速构建知识库</li>
        <li><strong>灵活更新：</strong>开发者可随时对知识库内容进行更新，保持信息时效性</li>
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