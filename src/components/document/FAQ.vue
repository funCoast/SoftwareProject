<template>
  <div class="faq">
    <h1>常见问题</h1>

    <div class="section">
      <h2>基础问题</h2>
      <div class="faq-item">
        <h3>什么是智能体？</h3>
        <p>智能体是基于人工智能技术的自动化工具，可以执行特定的任务和功能。在我们的平台上，智能体可以处理文本、图像、数据分析等多种任务。</p>
      </div>

      <div class="faq-item">
        <h3>如何开始使用平台？</h3>
        <p>首先注册账号，然后可以浏览智能体市场或创建工作空间。建议先完成"动手实验室"中的基础实验，熟悉平台的基本功能。</p>
      </div>

      <div class="faq-item">
        <h3>工作流是什么？</h3>
        <p>工作流是将多个智能体连接起来，形成自动化处理流程的工具。通过工作流，可以实现复杂任务的自动化处理。</p>
      </div>
    </div>

    <div class="section">
      <h2>使用问题</h2>
      <div class="faq-item">
        <h3>如何创建智能体？</h3>
        <p>在工作空间中点击"新建智能体"，填写基本信息并配置参数即可。详细步骤请参考使用手册中的"创建智能体"部分。</p>
      </div>

      <div class="faq-item">
        <h3>如何发布智能体到社区？</h3>
        <p>在工作空间中选择要发布的智能体，点击"发布到社区"按钮，填写相关信息后提交审核。审核通过后即可在社区中展示。</p>
      </div>

      <div class="faq-item">
        <h3>工作流运行失败怎么办？</h3>
        <p>首先检查节点连接是否正确，然后查看各个节点的配置参数。如果仍然无法解决，可以查看运行日志或联系技术支持。</p>
      </div>
    </div>

    <div class="section">
      <h2>其他问题</h2>
      <div class="faq-item">
        <h3>如何获取技术支持？</h3>
        <p>您可以通过以下方式获取支持：</p>
        <ul>
          <li>查看使用文档和常见问题</li>
          <li>在社区中提问</li>
          <li>联系客服支持</li>
        </ul>
      </div>

      <div class="faq-item">
        <h3>平台收费情况如何？</h3>
        <p>平台提供基础版和高级版两种服务。基础版免费使用，高级版提供更多功能和资源。具体价格请查看会员中心。</p>
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