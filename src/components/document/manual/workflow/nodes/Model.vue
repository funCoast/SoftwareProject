<template>
  <div class="head">
    <h2>大模型节点</h2>

    <div class="section">
      <h3>功能</h3>
      <p>大模型节点具备调用大语言模型的能力，能够综合处理来自“开始”节点的用户输入信息以及工作流中其他节点的输出内容，生成具有针对性的回应。
        该节点可广泛应用于对话生成、意图识别、信息提取、文本处理等任务，是整个工作流中的核心处理节点之一。</p>
    </div>

    <div class="section">
      <h3>应用场景</h3>
      <p>大模型节点适用于多种典型的应用场景：</p>
      <ul>
        <li><strong>意图识别：</strong>在客服对话情景中，用于识别用户问题的意图，并根据识别结果引导流程分支。<strong>意图识别也可以用问题分类器节点实现。</strong></li>
        <li><strong>文本生成：</strong>在内容创作类应用中，根据输入的主题或关键词生成符合要求的文章、文段或文案内容。</li>
        <li><strong>自动分类：</strong>在邮件处理场景中，对邮件内容进行自动分类，如划分为“咨询类”“投诉类”或“垃圾邮件”等。</li>
        <li><strong>文本转换：</strong>在翻译场景中，将用户提供的原始文本翻译为指定语言，实现语言转换。</li>
        <li><strong>RAG（检索增强生成）：</strong>在知识库问答情景中，将从知识库中检索到的内容与用户问题结合，通过系统提示词与用户提示词协同作用，生成准确的问答内容。</li>
      </ul>
    </div>

    <div class="section">
      <h3>配置方式</h3>
      <p>您可以在节点中选择适配的大语言模型。灵犀平台目前支持三种主流模型：</p>
      <ul>
        <li><strong>通义千问（qwen-plus）</strong></li>
        <li><strong>DeepSeek（deepseek-r1）</strong></li>
        <li><strong>智谱 AI（chatglm-6b-v2）</strong></li>
      </ul>
      <p>您可以根据业务场景和任务类型选择合适的模型，并配置以下提示词：</p>
      <ul>
        <li><strong>系统提示词（System Prompt）：</strong>用于为模型设定行为边界和角色定位，作为模型的初始指导。在 RAG（检索增强生成）场景中，系统提示词还承担着引导模型合理利用检索信息的重要角色。</li>
        <li><strong>用户提示词（User Prompt）：</strong>用于传入用户的实际问题或输入内容，引导模型输出结果。</li>
      </ul>
      <p>通过合理配置提示词，可以显著提升大模型节点在具体场景中的表现力和响应质量。</p>
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
<script setup>
</script>