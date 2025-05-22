<template>
  <div class="head">
    <h2>结束节点</h2>

    <div class="section">
      <h3>功能</h3>
      <p>结束节点定义了工作流执行完成后的最终输出内容。<strong>为了确保工作流完整运行，必须至少包含一个结束节点，用于输出整个流程的最终结果。</strong>
        作为流程的终止节点，结束节点后不能再添加其他节点，工作流只有运行至结束节点时才会产生执行结果输出。</p>
      <p>在存在多分支的工作流中，可能需要定义多个结束节点，以覆盖所有可能的执行路径。结束节点需要声明一个或多个输出变量，这些变量可以引用流程中任意上游节点的输出内容。</p>
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