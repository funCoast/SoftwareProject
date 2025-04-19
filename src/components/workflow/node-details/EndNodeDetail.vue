<script setup lang="ts">
import { ref, watch, computed } from 'vue'
import { getAllUpstreamNodes } from '../../../utils/getAllUpstreamNodes'

interface Input {
  id: number
  name: string,
  type: string,
  value?: {
    type: number // 1: 上游节点的输出变量
    nodeId: number
    outputId: number
  }
}

const props = defineProps<{
  node: {
    id: number
    type: string
    label: string
    x: number
    y: number
    inputs: Input[]
  }
  allNodes: any[]
}>()

const emit = defineEmits<{
  (e: 'update:node', node: any): void
}>()

// 获取所有上游节点
const allUpstreamNodes = computed(() => {
  return getAllUpstreamNodes(props.node, props.allNodes)
})

// 初始化输出列表
const inputs = ref<Input[]>(props.node.inputs || [])

// 监听输出变化并更新节点
watch(inputs, () => {
  emit('update:node', {
    ...props.node,
    inputs: inputs.value,
    outputs: inputs.value
  })
}, { deep: true })

// 添加新输出
function addInput() {
  const newId = inputs.value.length
    ? Math.max(...inputs.value.map(o => o.id)) + 1
    : 0
  
  inputs.value.push({
    id: newId,
    name: '',
    type: '',
    value: {
      type: 1,
      nodeId: -1,
      outputId: -1
    }
  })
}

// 删除输出
function removeInput(id: number) {
  const index = inputs.value.findIndex(o => o.id === id)
  if (index !== -1) {
    inputs.value.splice(index, 1)
  }
}

// 用于保持 select 的 value 绑定正确
function generateSelectValue(val: any) {
  if (val?.type === 1 && val?.nodeId !== -1 && val?.outputId !== -1) {
    return `${val.nodeId}|${val.outputId}`
  }
  return ''
}

// 处理上游输出选择变化
function onSelectChange(val: string, input: Input) {
  const [nodeId, outputId] = val.split('|')
  input.value = {
    type: 1,
    nodeId: parseInt(nodeId),
    outputId: parseInt(outputId)
  }
  input.type = getUpstreamOutputType(parseInt(nodeId), parseInt(outputId))
}

// 获取上游节点输出的类型
function getUpstreamOutputType(nodeId: number, outputId: number): string {
  const node = allUpstreamNodes.value.find(n => n.id === nodeId)
  if (!node?.outputs?.[outputId]) return '未知类型'
  return node.outputs[outputId].type || '未知类型'
}
</script>

<template>
  <div class="end-node-detail">
    <div class="outputs-section">
      <div class="section-header">
        <h4>输出变量</h4>
        <el-button type="primary" size="small" @click="addInput">
          添加变量
        </el-button>
      </div>

      <div v-if="inputs.length === 0" class="empty-state">
        <p>暂无输出变量，点击"添加变量"创建</p>
      </div>

      <div v-else class="output-list">
        <div v-for="input in inputs" :key="input.id" class="output-item">
          <div class="output-row">
            <el-input
              v-model="input.name"
              placeholder="变量名称"
              size="small"
              class="name-input"
            />
            <el-select
              :model-value="generateSelectValue(input.value)"
              placeholder="选择上游输出"
              size="small"
              class="type-select"
              @change="val => onSelectChange(val, input)"
            >
              <template v-for="node in allUpstreamNodes" :key="node.id">
                <el-option
                  v-for="(nodeOutput, idx) in node.outputs"
                  :key="`${node.id}-${idx}`"
                  :label="`${node.name}: ${nodeOutput.name} (${nodeOutput.type})`"
                  :value="`${node.id}|${idx}`"
                />
              </template>
            </el-select>
            <el-button
              type="danger"
              size="small"
              @click="removeInput(input.id)"
              class="remove-btn"
            >
              删除
            </el-button>
          </div>
          <div v-if="input.value?.nodeId !== -1" class="output-type">
            类型: {{ getUpstreamOutputType(input.value.nodeId, input.value.outputId) }}
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.end-node-detail {
  padding: 16px;
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
}

.name-input {
  flex: 2;
}

.type-select {
  flex: 2;
}

.remove-btn {
  flex-shrink: 0;
}

.output-type {
  margin-top: 8px;
  font-size: 12px;
  color: #666;
  padding-left: 4px;
}
</style> 