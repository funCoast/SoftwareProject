<script setup lang="ts">
import { ref, computed } from 'vue'
import { getAllUpstreamNodes } from '../../../utils/getAllUpstreamNodes'

interface Input {
  id: number
  name: 'city'
  type: 'string'
  value: {
    type: number // 0: 手动输入, 1: 上游节点的输出
    nodeId: number
    outputId: number
    text: string
  }
}

interface Output {
  id: number
  name: 'result'
  type: 'string'
}

const props = defineProps<{
  node: {
    id: number
    type: string
    name: string
    inputs: Input[]
    outputs: Output[]
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

// 初始化输入
const input = ref<Input>(props.node.inputs?.[0] || {
  id: 0,
  name: 'city',
  type: 'string',
  value: {
    type: 0,
    nodeId: -1,
    outputId: -1,
    text: ''
  }
})

// 是否为手动输入
const isManualInput = computed(() => {
  return !input.value.value?.type || input.value.value.type === 0
})

// 生成选择器的值
function generateSelectValue(val?: Input['value']): string {
  if (!val?.type || val.type === 0) return 'manual'
  return `${val.nodeId}|${val.outputId}`
}

// 处理选择变化
function onSelectChange(val: string) {
  if (val === 'manual') {
    input.value.value = {
      type: 0,
      nodeId: -1,
      outputId: -1,
      text: ''
    }
  } else {
    const [nodeId, outputId] = val.split('|').map(Number)
    input.value.value = {
      type: 1,
      nodeId,
      outputId,
      text: ''
    }
  }
  updateNode()
}

// 更新节点
function updateNode() {
  emit('update:node', {
    ...props.node,
    inputs: [input.value],
    outputs: [{
      id: 0,
      name: 'result',
      type: 'string'
    }]
  })
}
</script>

<template>
  <div class="weather-node-detail">
    <!-- 输入配置 -->
    <div class="section">
      <div class="section-header">
        <h4>输入变量</h4>
      </div>
      
      <div class="input-config">
        <div class="form-group">
          <label>输入来源</label>
          <el-select
            :model-value="generateSelectValue(input.value)"
            placeholder="选择输入来源"
            size="small"
            class="source-select"
            @change="onSelectChange"
          >
            <el-option
              label="手动输入"
              value="manual"
            />
            <template v-for="node in allUpstreamNodes" :key="node.id">
              <el-option
                v-for="(nodeOutput, idx) in node.outputs"
                :key="`${node.id}-${idx}`"
                :label="`${node.name}: ${nodeOutput.name}`"
                :value="`${node.id}|${nodeOutput.id}`"
              />
            </template>
          </el-select>
        </div>
        
        <div v-if="isManualInput" class="form-group">
          <label>城市名称</label>
          <el-input
            v-model="input.value.text"
            type="text"
            placeholder="请输入城市名称"
            size="small"
            @input="updateNode"
          />
        </div>

        <div v-else class="input-info">
          <div class="info-item">
            <label>变量名称:</label>
            <span>city</span>
          </div>
          <div class="info-item">
            <label>变量类型:</label>
            <span>string</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 输出信息 -->
    <div class="section">
      <div class="section-header">
        <h4>输出变量</h4>
      </div>
      
      <div class="output-info">
        <div class="info-item">
          <label>变量名称:</label>
          <span>result</span>
        </div>
        <div class="info-item">
          <label>变量类型:</label>
          <span>string</span>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.weather-node-detail {
  padding: 16px;
}

.section {
  background: #fff;
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 24px;
}

.section-header {
  margin-bottom: 16px;
}

.section-header h4 {
  margin: 0;
  font-size: 16px;
  color: #2c3e50;
}

.form-group {
  margin-bottom: 16px;
}

.form-group:last-child {
  margin-bottom: 0;
}

label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
  color: #2c3e50;
}

.source-select {
  width: 100%;
}

.input-info,
.output-info {
  background: #f5f7fa;
  border-radius: 4px;
  padding: 12px;
}

.info-item {
  display: flex;
  gap: 8px;
  margin-bottom: 8px;
}

.info-item:last-child {
  margin-bottom: 0;
}

.info-item label {
  margin: 0;
  color: #606266;
}

.info-item span {
  color: #2c3e50;
  font-family: monospace;
}
</style>