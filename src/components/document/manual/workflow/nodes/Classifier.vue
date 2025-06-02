<template>
  <div class="head">
    <h2>问题分类器节点</h2>

    <div class="section">
      <h3>功能</h3>
      <p>问题分类器节点通过设定分类标签及其描述，利用大语言模型的推理能力，根据用户的输入内容自动判断其所属类别，并输出分类结果，帮助下游节点更精准地处理任务。</p>
    </div>

    <div class="section">
      <h3>配置方式</h3>
      <ul>
        <li><strong>选择输入变量：</strong>指定用于分类判断的输入内容（如开始节点的输入变量）。</li>
        <li><strong>编写分类标签与描述：</strong>添加一个或多个分类标签，并提供关键词或描述性语句，帮助模型理解每个分类的判定依据。</li>
        <li><strong>配置分类结果对应的下游节点：</strong>问题分类器完成分类后，可根据分类结果配置跳转路径，分别连接到不同的下游节点，推动流程继续执行。</li>
      </ul>
    </div>

    <div class="section">
      <h3>应用场景</h3>
      <p>问题分类器广泛适用于需要对用户输入进行语义理解和分类的场景，例如：</p>
      <ul>
        <li>客服对话中的意图识别与分类</li>
        <li>产品评论或反馈的自动归类</li>
        <li>邮件的批量分类处理</li>
      </ul>
      <p>在典型的产品客服问答场景中，问题分类器通常作为知识库检索的前置步骤，先对用户问题进行分类，再引导至不同的知识库节点获取对应答案，从而实现更精确的回复。</p>
      <p>以下是一个产品客服场景的工作流模板示例：</p>
      <p>假设设定了以下三个分类标签/描述：</p>
      <ul>
        <li><strong>分类1：</strong>与售后相关的问题</li>
        <li><strong>分类2：</strong>与产品操作使用相关的问题</li>
        <li><strong>分类3：</strong>其他问题</li>
      </ul>
      <p>当用户输入如下问题时，问题分类器将进行自动分类：</p>
      <ul>
        <li>“iPhone 14 如何设置通讯录联系人？” → 与产品操作使用相关的问题</li>
        <li>“保修期限是多久？” → 与售后相关的问题</li>
        <li>“今天天气怎么样？” → 其他问题</li>
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