<script setup lang="ts">
import { ref, computed } from 'vue'

const weatherData = ref([
  { "日期": "17日（今天）", "天气": "小雨", "温度": "21℃", "风向风力": "北风 <3级" },
  { "日期": "18日（明天）", "天气": "多云", "温度": "28℃/21℃", "风向风力": "西风, 东风 <3级" },
  { "日期": "19日（后天）", "天气": "多云", "温度": "31℃/21℃", "风向风力": "东风, 东北风 <3级" },
  { "日期": "20日（周二）", "天气": "多云", "温度": "32℃/23℃", "风向风力": "西北风, 东风 <3级" },
  { "日期": "21日（周三）", "天气": "晴转多云", "温度": "34℃/25℃", "风向风力": "东风, 东风 <3级" },
  { "日期": "22日（周四）", "天气": "中雨", "温度": "31℃/21℃", "风向风力": "东北风, 西北风 <3级" },
  { "日期": "23日（周五）", "天气": "阴", "温度": "27℃/20℃", "风向风力": "南风, 东风 <3级" }
])

const formattedJson = computed(() => {
  return JSON.stringify(weatherData.value, null, 2)
})
</script>

<template>
  <div class="head">
    <h2>天气查询节点</h2>

    <div class="section">
      <h3>功能</h3>
      <p>
        天气查询节点用于获取指定城市未来 7 天的天气预报信息。
        <strong>该节点支持查询中国境内的一级行政区和二级行政区（如“杭州”、“苏州”等），城市名称需去除“市”“区”等后缀。</strong>
      </p>
      <p>查询结果为包含每日天气信息的列表，格式如下：</p>

      <div class="ide-container">
        <div class="ide-header">
          <div class="ide-dots">
            <span></span>
            <span></span>
            <span></span>
          </div>
          <div class="ide-title">weather-data.json</div>
        </div>
        <pre class="ide-content"><code>{{ formattedJson }}</code></pre>
      </div>

      <p>开发者可在工作流中结合代码节点，对返回的 JSON 数据进行解析和处理，例如提取明天的温度或筛选特定天气条件。</p>
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

.ide-container {
  background: #1e1e1e;
  border-radius: 8px;
  overflow: hidden;
  margin: 20px 0;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
  font-family: 'JetBrains Mono', 'Fira Code', 'Consolas', monospace;
}

.ide-header {
  background: #2d2d2d;
  padding: 8px 16px;
  display: flex;
  align-items: center;
  border-bottom: 1px solid #3d3d3d;
}

.ide-dots {
  display: flex;
  gap: 6px;
  margin-right: 12px;
}

.ide-dots span {
  width: 12px;
  height: 12px;
  border-radius: 50%;
}

.ide-dots span:nth-child(1) {
  background: #ff5f56;
}

.ide-dots span:nth-child(2) {
  background: #ffbd2e;
}

.ide-dots span:nth-child(3) {
  background: #27c93f;
}

.ide-title {
  color: #abb2bf;
  font-size: 13px;
}

.ide-content {
  margin: 0;
  padding: 20px;
  background: transparent;
  font-size: 14px;
  line-height: 1.6;
  overflow-x: auto;
}

.ide-content code {
  color: #e6e6e6;
}

/* JSON syntax highlighting */
:deep(.ide-content) {
  & .string { color: #98c379; }
  & .number { color: #d19a66; }
  & .boolean { color: #56b6c2; }
  & .null { color: #c678dd; }
  & .key { color: #e06c75; }
}
</style>
