<template>
  <div class="head">
    <h2>网页爬取节点</h2>
    <p>网页爬取节点用于抓取指定网页上的内容，并将其作为结构化或非结构化数据提供给工作流中的下游节点使用。
      通过配置目标网址，开发者可以自动获取网页上的文本、表格、链接等信息，避免手动复制，提高数据处理效率</p>

    <div class="section">
      <h3>应用场景</h3>
      <p>网页爬取节点适用于以下典型场景：</p>
      <ul>
        <li><strong>新闻摘要生成：</strong>抓取新闻网站的实时头条信息，提供给大模型节点生成摘要或提炼要点。</li>
        <li><strong>商品价格监控：</strong>定时抓取电商页面上的商品价格与库存状态，结合后续逻辑判断是否推送预警。</li>
        <li><strong>资料收集：</strong>在行业报告、政府官网等公开平台抓取有用资料，用于知识库构建或问答服务。</li>
        <li><strong>论坛/评论分析：</strong>获取社区论坛、评论区等内容，用于情感分析或用户观点挖掘。</li>
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