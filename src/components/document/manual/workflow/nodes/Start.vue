<template>
  <div class="head">
    <h2>开始节点</h2>

    <div class="section">
      <h3>功能</h3>
      <p><strong>开始节点是整个工作流的入口。</strong>当工作流被启动时，系统将从开始节点开始，按照预设的连接关系依次触发后续节点执行。
        开始节点通常用于接收用户的输入以及用户上传的文件内容，并将这些数据作为上下文传递给下游节点。</p>
    </div>

    <div class="section">
      <h3>配置方式</h3>
      <p>点击开始节点即可打开详情面板，进行输入变量的配置。您可以自由添加或删除输入变量，变量名称可自行定义。变量类型支持字符串和数字两种选择。
        若选择数字类型，为确保工作流的正常运行，您应在智能体的开场白部分提示用户输入合法的数字。<strong>为了保证智能体能够正确调用工作流，应当为每个输入变量提供准确且清晰的描述。</strong></p>
      <p>推荐您按照如下示例进行配置：</p>
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