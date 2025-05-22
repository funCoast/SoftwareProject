<template>
  <div class="head">
    <h2>调试与运行</h2>
    <p>灵犀平台提供了一套完整的运行与调试机制，帮助开发者在工作流开发过程中快速定位问题、验证功能逻辑。
      平台支持<strong>单节点调试</strong>与<strong>工作流试运行</strong>两种模式，满足不同阶段的调试需求。</p>

    <div class="section">
      <h3>单节点调试</h3>
      <p>工作流支持对任意节点进行独立调试，便于开发者在节点配置完成后快速验证其功能是否符合预期。</p>
      <ul>
        <li>开发者配置好节点后，可点击节点详情面板右上角的“运行”按钮；</li>
        <li>系统将弹出运行面板，开发者可在其中手动输入该节点所需的输入变量；</li>
        <li>点击“运行”后，平台将立即执行该节点；</li>
        <li>执行结果将在面板中展示，包括运行状态（成功 / 失败）以及节点的输出信息或报错详情。</li>
      </ul>
      <p>该功能支持多次重复测试，适用于调试函数逻辑、检查数据格式、验证配置正确性等场景。</p>
    </div>

    <div class="section">
      <h3>工作流试运行</h3>
      <p>完成工作流整体编排后，开发者可通过试运行功能验证整个流程的执行效果。</p>
      <ul>
        <li>点击画布下方的“试运行”按钮，弹出试运行面板；</li>
        <li>在面板中填写开始节点的输入变量；</li>
        <li>点击“运行”后，平台将按流程顺序依次执行各节点；</li>
        <li>仅已执行的节点会在其下方显示运行结果或失败信息，未触达的节点不会显示状态；</li>
      </ul>
      <p>该模式适用于整体流程的端到端验证，帮助开发者在上线前预先发现逻辑错误或配置问题。</p>
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