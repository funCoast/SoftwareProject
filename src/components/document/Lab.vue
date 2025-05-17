<template>
  <div class="lab">
    <h1>动手实验室</h1>

    <div class="section">
      <h2>基础实验</h2>
      <div class="lab-card">
        <h3>实验一：创建第一个智能体</h3>
        <p>学习如何创建和配置一个基础的智能体。</p>
        <div class="lab-steps">
          <h4>实验步骤：</h4>
          <ol>
            <li>创建工作空间</li>
            <li>创建新智能体</li>
            <li>配置基本参数</li>
            <li>测试智能体功能</li>
          </ol>
        </div>
        <div class="lab-tips">
          <h4>实验要点：</h4>
          <ul>
            <li>了解智能体的基本结构</li>
            <li>掌握参数配置方法</li>
            <li>学习测试和调试技巧</li>
          </ul>
        </div>
      </div>

      <div class="lab-card">
        <h3>实验二：工作流编排入门</h3>
        <p>学习如何创建和运行简单的工作流。</p>
        <div class="lab-steps">
          <h4>实验步骤：</h4>
          <ol>
            <li>创建工作流</li>
            <li>添加基础节点</li>
            <li>连接节点</li>
            <li>运行工作流</li>
          </ol>
        </div>
        <div class="lab-tips">
          <h4>实验要点：</h4>
          <ul>
            <li>理解工作流概念</li>
            <li>掌握节点连接方法</li>
            <li>学习工作流调试</li>
          </ul>
        </div>
      </div>
    </div>

    <div class="section">
      <h2>进阶实验</h2>
      <div class="lab-card">
        <h3>实验三：智能体集成</h3>
        <p>学习如何将多个智能体集成到工作流中。</p>
        <div class="lab-steps">
          <h4>实验步骤：</h4>
          <ol>
            <li>选择多个智能体</li>
            <li>创建工作流</li>
            <li>配置智能体间通信</li>
            <li>测试集成效果</li>
          </ol>
        </div>
        <div class="lab-tips">
          <h4>实验要点：</h4>
          <ul>
            <li>理解智能体通信机制</li>
            <li>掌握数据流转方法</li>
            <li>学习错误处理</li>
          </ul>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.lab {
  max-width: 800px;
  margin: 0 auto;
}

h1 {
  color: #2c3e50;
  margin-bottom: 32px;
}

.section {
  margin-bottom: 40px;
}

h2 {
  color: #2c3e50;
  margin-bottom: 24px;
  padding-bottom: 8px;
  border-bottom: 2px solid #e6e6e6;
}

.lab-card {
  background: white;
  border-radius: 8px;
  padding: 24px;
  margin-bottom: 24px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

h3 {
  color: #2c3e50;
  margin-bottom: 16px;
}

p {
  color: #606266;
  line-height: 1.6;
  margin-bottom: 16px;
}

.lab-steps, .lab-tips {
  margin-top: 16px;
}

h4 {
  color: #2c3e50;
  margin-bottom: 12px;
  font-size: 16px;
}

ol, ul {
  color: #606266;
  line-height: 1.6;
  padding-left: 24px;
}

li {
  margin-bottom: 8px;
}

.lab-tips {
  margin-top: 24px;
  padding-top: 16px;
  border-top: 1px solid #e6e6e6;
}
</style> 