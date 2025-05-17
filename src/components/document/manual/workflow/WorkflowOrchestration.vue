<template>
  <div class="workflow-orchestration">
    <h2>编排节点</h2>
    <p>工作流编排是将不同节点连接起来，形成完整处理流程的过程。</p>

    <div class="section">
      <h3>基本操作</h3>
      <div class="operation">
        <h4>添加节点</h4>
        <ol>
          <li>从左侧节点列表中选择需要的节点</li>
          <li>拖拽节点到画布中</li>
          <li>调整节点位置</li>
        </ol>
      </div>

      <div class="operation">
        <h4>连接节点</h4>
        <ol>
          <li>点击源节点的输出端口</li>
          <li>拖动到目标节点的输入端口</li>
          <li>确认连接类型和参数</li>
        </ol>
      </div>
    </div>

    <div class="section">
      <h3>节点配置</h3>
      <div class="config">
        <h4>参数设置</h4>
        <ul>
          <li>点击节点打开配置面板</li>
          <li>设置必要的参数</li>
          <li>配置数据映射关系</li>
          <li>设置错误处理策略</li>
        </ul>
      </div>

      <div class="config">
        <h4>条件配置</h4>
        <ul>
          <li>设置条件表达式</li>
          <li>配置分支逻辑</li>
          <li>设置默认分支</li>
        </ul>
      </div>
    </div>

    <div class="section">
      <h3>最佳实践</h3>
      <div class="practice">
        <h4>工作流设计建议</h4>
        <ul>
          <li>保持工作流结构清晰</li>
          <li>合理使用条件分支</li>
          <li>添加适当的错误处理</li>
          <li>注意数据流转效率</li>
        </ul>
      </div>

      <div class="practice">
        <h4>性能优化</h4>
        <ul>
          <li>避免不必要的节点</li>
          <li>合理使用并行处理</li>
          <li>优化数据转换逻辑</li>
          <li>注意资源使用效率</li>
        </ul>
      </div>
    </div>
  </div>
</template>

<style scoped>
.workflow-orchestration {
  max-width: 800px;
  margin: 0 auto;
}

h2 {
  color: #2c3e50;
  margin-bottom: 24px;
}

.section {
  margin-bottom: 40px;
}

h3 {
  color: #2c3e50;
  margin-bottom: 24px;
  padding-bottom: 8px;
  border-bottom: 2px solid #e6e6e6;
}

.operation, .config, .practice {
  margin-bottom: 32px;
  padding: 20px;
  background: #f8f9fa;
  border-radius: 8px;
}

h4 {
  color: #2c3e50;
  margin-bottom: 16px;
  font-size: 18px;
}

p {
  color: #606266;
  line-height: 1.6;
  margin-bottom: 24px;
}

ol, ul {
  color: #606266;
  line-height: 1.6;
  padding-left: 24px;
  margin-top: 8px;
}

li {
  margin-bottom: 8px;
}

ol li {
  margin-bottom: 12px;
}
</style>
<script setup>
</script>