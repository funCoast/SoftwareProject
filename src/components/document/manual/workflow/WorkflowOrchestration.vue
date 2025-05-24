<script setup lang="ts">
const supportTable = [
  { type: '大模型', manual: true, upper: true },
  { type: '代码', manual: false, upper: true },
  { type: '条件分支', manual: true, upper: true },
  { type: '问题分类器', manual: false, upper: true },
  { type: '知识库检索', manual: false, upper: true },
  { type: '天气查询', manual: true, upper: true },
  { type: '参数提取器', manual: false, upper: true },
  { type: '网页爬取', manual: true, upper: false },
  { type: '智能体', manual: true, upper: true }
]
</script>

<template>
  <div class="head">
    <h2>编排工作流</h2>
    <p>
      在灵犀平台中，开发者可以通过可视化拖拽方式灵活编排工作流，实现任务流程的快速搭建与调整。
      <strong>平台支持串行流程与多分支流程两种编排模式，并通过丰富的节点组件实现复杂逻辑控制。</strong>
    </p>

    <div class="section">
      <h3>工作流结构与基本规则</h3>
      <p>每个工作流必须包含一个开始节点，可配置多个结束节点；初次进入编排画布时，系统将自动添加一个“开始节点”和一个“结束节点”。</p>
      <p>连接规则为：</p>
      <ul>
        <li><strong>每个节点左侧为输入连接点，右侧为输出连接点；</strong></li>
        <li><strong>开始节点仅有输出连接点，结束节点仅有输入连接点；</strong></li>
        <li><strong>禁止这些连接方式：节点连接自身，两节点间重复连线，同侧连接点互连（左对左 / 右对右）。</strong></li>
      </ul>
    </div>

    <div class="section">
      <h3>节点管理与操作方式</h3>
      <p>点击画布底部的“添加节点”按钮，弹出选择框，可选择除“开始节点”外的10种节点类型；
        移动左键选中的预览节点至合适位置再次点击左键，就能完成节点放置；拖动画布背景可调整整体视图。</p>
      <p>节点操作方式包括：</p>
      <ul>
        <li>长按节点：拖动位置；</li>
        <li>左键点击节点：右侧弹出配置面板；</li>
        <li>右键节点（除开始节点）：支持复制或删除；</li>
        <li><strong>当画布上仅剩一个结束节点时，无法删除结束节点。</strong></li>
      </ul>
      <p>有关节点间连接：</p>
      <ul>
        <li>鼠标悬停在连接点处出现“十字准心”；</li>
        <li>按住拖动至目标节点连接点松开，形成连线；</li>
        <li>右键连线可选择“删除连线”。</li>
      </ul>
    </div>

    <div class="section">
      <h3>节点详情配置</h3>
      <p>每个节点都包含以下基本信息：</p>
      <ul>
        <li>节点名称与节点描述：均可编辑，编辑后将在画布节点上同步显示；</li>
        <li>输入变量：节点运行所需数据来源；</li>
        <li>输出变量：节点执行后产生的数据结果（仅代码节点需手动配置输出变量，其余为固定）。</li>
        <li>其他配置</li>
      </ul>
    </div>

    <div class="section">
      <h3>输入变量配置规则</h3>
      <p>不同节点对输入变量的来源有不同要求，具体如下：</p>

      <!-- ✅ 表格展示输入变量支持情况 -->
      <table class="support-table">
        <thead>
        <tr>
          <th>节点类型</th>
          <th>支持手动输入</th>
          <th>支持引用上游输出变量</th>
        </tr>
        </thead>
        <tbody>
        <tr v-for="row in supportTable" :key="row.type">
          <td>{{ row.type }}</td>
          <td>{{ row.manual ? '✅' : '❌' }}</td>
          <td>{{ row.upper ? '✅' : '❌' }}</td>
        </tr>
        </tbody>
      </table>
    </div>

    <div class="section">
      <h3>流程设计模式说明</h3>
      <ul>
        <li><strong>串行流程：</strong>节点依次连接，适合线性任务处理；</li>
        <li><strong>多分支流程：</strong>通过条件分支节点或问题分类器节点将流程根据逻辑拆分为多个分支，适合处理不同情境下的决策逻辑；</li>
        <li><strong>不支持并行合流：</strong>不同分支在拆分后将分别走向各自的结束节点，当前平台尚未支持多个分支最终合并至统一节点。</li>
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

table.support-table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 16px;
  font-size: 14px;
  color: #444;
}

.support-table th,
.support-table td {
  border: 1px solid #ccc;
  padding: 8px 12px;
  text-align: center;
}

.support-table th {
  background-color: #f2f2f2;
  color: #2c3e50;
}

.support-table td {
  background-color: #fff;
}
</style>
