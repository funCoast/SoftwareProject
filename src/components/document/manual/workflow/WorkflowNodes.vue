<template>
  <div class="workflow-nodes">
    <h2>节点说明</h2>
    <p>工作流由不同类型的节点组成，每种节点都有其特定的功能和用途。</p>

    <div class="section">
      <h3>基础节点</h3>
      <div class="node-type">
        <h4>开始节点</h4>
        <p>工作流的起点，用于接收输入参数。</p>
        <ul>
          <li>支持多种输入类型</li>
          <li>可配置参数验证规则</li>
          <li>支持默认值设置</li>
        </ul>
      </div>

      <div class="node-type">
        <h4>结束节点</h4>
        <p>工作流的终点，用于输出处理结果。</p>
        <ul>
          <li>支持多种输出格式</li>
          <li>可配置结果转换</li>
          <li>支持错误处理</li>
        </ul>
      </div>
    </div>

    <div class="section">
      <h3>处理节点</h3>
      <div class="node-type">
        <h4>智能体节点</h4>
        <p>调用已创建的智能体进行处理。</p>
        <ul>
          <li>支持参数传递</li>
          <li>可配置重试机制</li>
          <li>支持超时设置</li>
        </ul>
      </div>

      <div class="node-type">
        <h4>条件节点</h4>
        <p>根据条件进行分支处理。</p>
        <ul>
          <li>支持多条件判断</li>
          <li>可配置复杂逻辑</li>
          <li>支持默认分支</li>
        </ul>
      </div>
    </div>

    <div class="section">
      <h3>工具节点</h3>
      <div class="node-type">
        <h4>数据转换节点</h4>
        <p>对数据进行格式转换和处理。</p>
        <ul>
          <li>支持多种数据格式</li>
          <li>可配置转换规则</li>
          <li>支持数据验证</li>
        </ul>
      </div>

      <div class="node-type">
        <h4>循环节点</h4>
        <p>对数据进行循环处理。</p>
        <ul>
          <li>支持多种循环方式</li>
          <li>可配置循环条件</li>
          <li>支持中断控制</li>
        </ul>
      </div>
    </div>
  </div>
</template>

<style scoped>
.workflow-nodes {
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

.node-type {
  margin-bottom: 32px;
  padding: 20px;
  background: #f8f9fa;
  border-radius: 8px;
}

h4 {
  color: #2c3e50;
  margin-bottom: 12px;
  font-size: 18px;
}

p {
  color: #606266;
  line-height: 1.6;
  margin-bottom: 12px;
}

ul {
  color: #606266;
  line-height: 1.6;
  padding-left: 24px;
  margin-top: 8px;
}

li {
  margin-bottom: 8px;
}
</style>
<script setup>
</script>