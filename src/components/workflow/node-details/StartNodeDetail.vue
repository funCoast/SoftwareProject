<script setup lang="ts">
import { ref, watch } from 'vue'

interface Output {
  id: number
  name: string
  type: string
  description: string
}

const props = defineProps<{
  node: {
    id: number
    type: string
    label: string
    x: number
    y: number
    outputs: Output[]
  }
}>()

const emit = defineEmits<{
  (e: 'update:node', node: any): void
}>()

// 可选的输出类型
const outputTypes = [
  { label: '字符串', value: 'string' },
  { label: '数字', value: 'number' },
  { label: '文件数组', value: 'Array[File]' }
]

// 初始化输出列表
const outputs = ref<Output[]>(props.node.outputs || [])

// 监听输出变化并更新节点
watch(outputs, () => {
  emit('update:node', {
    ...props.node,
    outputs: outputs.value
  })
}, { deep: true })

// 添加新输出
function addOutput() {
  const newId = outputs.value.length 
    ? Math.max(...outputs.value.map(o => o.id)) + 1 
    : 0
  outputs.value.push({
    id: newId,
    name: '',
    type: 'string',
    description: ''
  })
}

// 删除输出
function removeOutput(id: number) {
  const index = outputs.value.findIndex(o => o.id === id)
  if (index !== -1) {
    outputs.value.splice(index, 1)
  }
}
</script>

<template>
  <div class="start-node-detail">
    <div class="outputs-section">
      <div class="section-header">
        <h4>输出变量</h4>
        <el-button type="primary" size="small" @click="addOutput">
          添加变量
        </el-button>
      </div>
      <div v-if="outputs.length === 0" class="empty-state">
        <p>暂无输出变量，点击"添加变量"创建</p>
      </div>
      <div v-else class="output-list">
        <div v-for="output in outputs" :key="output.id" class="output-item">
          <div class="output-row">
            <el-input
              v-model="output.name"
              placeholder="变量名称"
              size="small"
              class="name-input"
            />
            <el-select
              v-model="output.type"
              placeholder="选择类型"
              size="small"
              class="type-select"
            >
              <el-option
                v-for="type in outputTypes"
                :key="type.value"
                :label="type.label"
                :value="type.value"
              />
            </el-select>
            <el-button
              type="danger"
              size="small"
              @click="removeOutput(output.id)"
              class="remove-btn"
            >
              删除
            </el-button>
          </div>
          <div class="description-row">
            <el-input
              v-model="output.description"
              type="textarea"
              :rows="2"
              placeholder="请输入变量描述"
              size="small"
              class="description-input"
            />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.start-node-detail {
  padding: 16px;
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

.outputs-section {
  background: #fff;
  border-radius: 8px;
  padding: 16px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.section-header h4 {
  margin: 0;
  font-size: 16px;
  color: #2c3e50;
}

.empty-state {
  text-align: center;
  padding: 24px;
  background: #f8f9fa;
  border-radius: 8px;
  color: #666;
}

.output-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.output-item {
  background: #f8f9fa;
  border-radius: 8px;
  padding: 12px;
}

.output-row {
  display: flex;
  gap: 12px;
  align-items: center;
  margin-bottom: 12px;
}

.name-input {
  flex: 2;
}

.type-select {
  flex: 1;
}

.remove-btn {
  flex-shrink: 0;
}

.description-row {
  margin-top: 8px;
}

.description-input {
  width: 100%;
}
</style> 