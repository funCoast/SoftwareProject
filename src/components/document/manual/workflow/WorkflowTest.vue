<template>
  <div class="workflow-test">
    <h2>试运行</h2>
    <p>工作流试运行功能可以帮助您验证工作流的正确性和性能。</p>

    <div class="section">
      <h3>运行方式</h3>
      <div class="run-mode">
        <h4>单次运行</h4>
        <ol>
          <li>点击"运行"按钮</li>
          <li>输入测试数据</li>
          <li>查看运行结果</li>
          <li>分析执行日志</li>
        </ol>
      </div>

      <div class="run-mode">
        <h4>批量测试</h4>
        <ol>
          <li>准备测试数据集</li>
          <li>配置测试参数</li>
          <li>执行批量测试</li>
          <li>查看测试报告</li>
        </ol>
      </div>
    </div>

    <div class="section">
      <h3>调试功能</h3>
      <div class="debug-feature">
        <h4>断点调试</h4>
        <ul>
          <li>在节点上设置断点</li>
          <li>运行到断点处暂停</li>
          <li>查看变量值</li>
          <li>单步执行</li>
        </ul>
      </div>

      <div class="debug-feature">
        <h4>日志查看</h4>
        <ul>
          <li>实时查看执行日志</li>
          <li>查看节点状态</li>
          <li>分析错误信息</li>
          <li>导出日志文件</li>
        </ul>
      </div>
    </div>

    <div class="section">
      <h3>性能分析</h3>
      <div class="performance">
        <h4>执行时间</h4>
        <ul>
          <li>查看节点执行时间</li>
          <li>分析性能瓶颈</li>
          <li>优化处理逻辑</li>
        </ul>
      </div>

      <div class="performance">
        <h4>资源使用</h4>
        <ul>
          <li>监控内存使用</li>
          <li>查看CPU占用</li>
          <li>分析网络请求</li>
        </ul>
      </div>
    </div>
  </div>
</template>

<style scoped>
.workflow-test {
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

.run-mode, .debug-feature, .performance {
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