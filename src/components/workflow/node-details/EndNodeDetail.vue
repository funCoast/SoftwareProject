<script setup lang="ts">
import { defineProps, defineEmits } from 'vue'

const props = defineProps<{
  node: {
    id: number
    type: string
    label: string
    x: number
    y: number
    data?: any
  }
}>()

const emit = defineEmits<{
  (e: 'update:node', node: any): void
}>()

// 运行节点
async function run() {
  return {
    success: true,
    data: {
      message: '结束节点执行成功'
    }
  }
}

defineExpose({
  run
})
</script>

<template>
  <div class="end-node-detail">
    <div class="info-section">
      <div class="info-item">
        <label>节点类型</label>
        <span>结束节点</span>
      </div>
      <div class="info-item">
        <label>节点说明</label>
        <p class="description">工作流的结束节点，标志着工作流的结束。</p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.end-node-detail {
  padding: 16px;
}

.info-section {
  background: #f8f9fa;
  border-radius: 8px;
  padding: 16px;
}

.info-item {
  margin-bottom: 16px;
}

.info-item:last-child {
  margin-bottom: 0;
}

.info-item label {
  display: block;
  font-size: 14px;
  color: #666;
  margin-bottom: 8px;
}

.info-item span {
  font-size: 14px;
  color: #2c3e50;
  font-weight: 500;
}

.description {
  font-size: 14px;
  color: #2c3e50;
  line-height: 1.5;
  margin: 0;
}
</style> 