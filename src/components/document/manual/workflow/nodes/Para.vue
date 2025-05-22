<template>
  <div class="head">
    <h2>参数提取器节点</h2>

    <div class="section">
      <h3>功能</h3>
      <p>参数提取器节点利用大语言模型对用户输入的自然语言进行理解和推理，从中提取出结构化的参数信息，供工作流中其他节点使用。</p>
    </div>

    <div class="section">
      <h3>应用场景</h3>
      <p>该节点常用于从自由表达的用户输入中提取执行工具操作所需的关键参数。例如，在构建一个天气查询应用时：</p>
      <ul>
        <li>用户输入：“北京明天天气如何？”</li>
        <li>参数提取器会自动识别并提取出城市：北京。</li>
        <li>然后将这些参数传递给天气查询节点，实现精准查询。</li>
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
<script setup>
</script>