<script setup lang="ts">
import { ref, watch, computed, watchEffect } from 'vue'
import { getAllUpstreamNodes } from '@/utils/getAllUpstreamNodes.ts'

interface Input {
  id: number
  name: string,
  type: string,
  value?: {
    type: number // 1: 上游节点的输出变量
    text: string
    nodeId: number
    outputId: number
  }
}

interface Output {
  id: number
  name: string
  type: string
}

const props = defineProps<{
  node: {
    id: number
    name: string
    type: string
    label: string
    x: number
    y: number
    inputs: Input[]
    outputs: Output[]
  }
  allNodes: any[]
}>()

// 获取所有上游节点
const allUpstreamNodes = computed(() => {
  return getAllUpstreamNodes(props.node, props.allNodes)
})

// 初始化输出列表
const inputs = ref<Input[]>(props.node.inputs || [])

const emit = defineEmits<{
  (e: 'update:node', node: any): void
}>()

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
  const newInput: Input = {
    id: newId,
    name: '',
    type: 'string',
    value: {
      type: 1,
      nodeId: -1,
      text: '',
      outputId: -1
    }
  }
  bindInputType(newInput)
  inputs.value.push(newInput)
}

// 删除输出
function removeInput(id: number) {
  const index = inputs.value.findIndex(o => o.id === id)
  if (index !== -1) {
    inputs.value.splice(index, 1)
  }
}

function bindInputType(input: Input) {
  watchEffect(() => {
    if (!input.value) return
    const { nodeId, outputId } = input.value
    const node = allUpstreamNodes.value.find(n => n.id === nodeId)
    const output = node?.outputs.find(o => o.id === outputId)
    input.type = output?.type ?? 'string'
  })
}

// 用于保持 select 的 value 绑定正确
function generateSelectValue(input: Input): string {
  const val = input['value']
  if (val?.type === 1 && val?.nodeId !== -1 && val?.outputId !== -1) {
    const node = allUpstreamNodes.value.find(n => n.id === val.nodeId)
    const outputExists = node?.outputs?.some(o => o.id === val.outputId)
    if (node && outputExists) {
      return `${val.nodeId}|${val.outputId}`
    }
  }
  return ''
}

// 处理上游输出选择变化
function onSelectChange(val: string, input: Input) {
  const [nodeId, outputId] = val.split('|').map(Number)
  if (input.value) {
    input.value.nodeId = nodeId
    input.value.outputId = outputId
  }
}

function isNodeValid() {
  if (!props.node.name || props.node.name.length === 0) return '未配置节点名称'
  if (!inputs || inputs.value.length === 0) return '未配置输出变量！'

  for (const input of inputs.value) {
    if (!input.name || input.name.trim() === '') return '未配置输出变量的名称！'
    const value = input.value
    if (generateSelectValue(input).trim() === '') return '未选择输出变量的来源！'
  }
  return ''
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
              placeholder="变量名称（必填）"
              size="small"
              class="name-input"
            />
            <el-select
              :model-value="generateSelectValue(input)"
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
  flex: 0.7;
}

.type-select {
  flex: 0.8;
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