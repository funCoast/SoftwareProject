<template>
  <div class="head">
    <h2>管理知识库</h2>

    <div class="section">
      <h3>创建</h3>
      <p>在工作空间的资源库中，点击「创建资源」→「知识库」，在弹窗中选择知识库类型后，编辑知识库的名称与描述，支持从本地上传图片作为知识库的图标。
        创建成功后，知识库添加到开发者的资源库中，后续可对其名称等进行修改。</p>
    </div>

    <div class="section">
      <h3>添加内容</h3>
      <p>在知识库页面，点击「添加」为知识库添加内容。</p>
      <ul>
        <li><strong>文本知识库：</strong>支持 txt, pdf, doc, docx, md 格式，提供自动分段、自定义分段（设置最大分段长度）、按层级分段（针对Markdown）三种分段方式</li>
        <li><strong>图像知识库：</strong>支持 jpg, png, jpeg 格式，上传后自动对图像进行标注</li>
        <li><strong>表格知识库：</strong>支持 xls, xlsx, csv 格式，上传后自动解析表头和数据</li>
      </ul>
    </div>

    <div class="section">
      <h3>编辑内容</h3>
      <p>对于失去效用的内容，开发者可以将其从知识库中删除。对于图像知识库，开发者可以修改图像的标注；对于表格知识库，开发者可以在线编辑表格内容。</p>
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
<script setup lang="ts">
</script>