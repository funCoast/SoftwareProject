<template>
  <div class="faq">
    <div class="section">
      <h2>其他问题</h2>
      <div class="faq-item">
        <h3>是否支持将智能体部署到外部系统或API对接？</h3>
        <p>当前智能体只能支持在平台内使用。未来版本可能开放 API 网关，允许外部系统调用已发布的智能体服务。</p>
      </div>

      <div class="faq-item">
        <h3>工作流是否存在节点数量或层级深度的限制？</h3>
        <p>出于性能和可视化操作体验考虑，平台建议控制流程复杂度。目前并未设置硬性限制，但超复杂流程可能导致智能体回复速度缓慢。</p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.faq {
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

.faq-item {
  margin-bottom: 24px;
  padding: 20px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

h3 {
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