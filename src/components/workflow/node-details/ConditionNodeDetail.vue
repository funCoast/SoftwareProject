<script setup lang="ts">
import {ref, watch, computed, onMounted, watchEffect} from 'vue'
import { getAllUpstreamNodes } from '@/utils/getAllUpstreamNodes.ts'
import axios from 'axios'

interface Input {
  id: number
  name: string
  type: string
  value: {
    type: number // 1: 上游节点的输出
    nodeId: number
    outputId: number
    text: string
  }
}

interface Output {
  id: number
  name: string
  type: string
}

interface Condition {
  variable: Input['id'] | null
  compare_value: string
  compare_type: number
}

interface Case {
  condition: Condition[]
  and_or: number // 0: or, 1: and
  next_node: number | null
}

const props = defineProps<{
  node: {
    id: number
    type: string
    name: string
    nextWorkflowNodeIds: number[]
    inputs: Input[]
    outputs: Output[]
    data: {
      case: Case[]
    }
  }
  allNodes: any[]
  workflow_id: string
}>()

// 获取所有上游节点
const allUpstreamNodes = computed(() => {
  return getAllUpstreamNodes(props.node, props.allNodes)
})

// 初始化输入列表
const inputs = ref<Input[]>([])

// 初始化输出列表
const outputs = ref<Output[]>([])

// 初始化条件配置
const cases = ref<Case[]>(props.node.data?.case || [])

const emit = defineEmits<{
  (e: 'update:node', node: any): void
}>()

// 监听变化并更新节点
watch([inputs, outputs, cases], () => {
  emit('update:node', {
    ...props.node,
    inputs: inputs.value,
    outputs: outputs.value,
    data: {
      case: cases.value
    }
  })
}, { deep: true })

onMounted(() => {
  inputs.value = props.node.inputs;
  outputs.value = [{
    id: 0,
    name: 'option',
    type: 'number'
  }]
})

// 比较类型选项
const compareTypes = [
  { label: '包含', value: 1 },
  { label: '不包含', value: 2 },
  { label: '开始是', value: 3 },
  { label: '结束是', value: 4 },
  { label: '是', value: 5 },
  { label: '不是', value: 6 },
  { label: '为空', value: 7 },
  { label: '不为空', value: 8 }
]

// 运行面板相关
const showRunPanel = ref(false)
const isRunning = ref(false)
const runStatus = ref<'running' | 'success' | 'error' | null>(null)
const runResult = ref<{ name: string; value: string }[]>([])
const runError = ref<string | null>(null)
const runInputs = ref<Record<string, string>>({})

// 添加新输入
function addInput() {
  const newId = inputs.value.length
    ? Math.max(...inputs.value.map(i => i.id)) + 1
    : 0
  const newInput: Input = {
    id: newId,
    name: '',
    type: 'string',
    value: {
      type: 1,
      nodeId: -1,
      outputId: -1,
      text: ''
    }
  }
  bindInputType(newInput)
  inputs.value.push(newInput)
}

// 删除输入
function removeInput(id: number) {
  const index = inputs.value.findIndex(i => i.id === id)
  if (index !== -1) {
    inputs.value.splice(index, 1)
    // 同时删除相关的条件
    cases.value.forEach(case_ => {
      case_.condition = case_.condition.filter(cond => cond.variable !== id)
    })
  }
}

// 添加新的条件分支
function addCase() {
  cases.value.push({
    condition: [],
    and_or: 1,
    next_node: null
  })
}

// 删除条件分支
function removeCase(index: number) {
  cases.value.splice(index, 1)
}

// 添加条件
function addCondition(case_: Case) {
  if (inputs.value.length === 0) {
    ElMessage.warning('请先添加输入变量')
    return
  }
  case_.condition.push({
    variable: null,
    compare_value: '',
    compare_type: 1
  })
}

// 删除条件
function removeCondition(case_: Case, index: number) {
  case_.condition.splice(index, 1)
}

// 生成选择器的值
function generateSelectValue(input: Input): string {
  const val = input.value
  if (val?.type === 1 && val?.nodeId !== -1 && val?.outputId !== -1) {
    const node = allUpstreamNodes.value.find(n => n.id === val.nodeId)
    const outputExists = node?.outputs?.some((o: { id: number }) => o.id === val.outputId)
    if (node && outputExists) {
      return `${val.nodeId}|${val.outputId}`
    }
  }
  return ''
}

// 处理输入来源选择变化
function onSelectChange(val: string, input: Input): void {
  const [nodeId, outputId] = val.split('|').map(Number)
  if (input.value) {
    input.value.nodeId = nodeId
    input.value.outputId = outputId
  }
}

function getNodeNameById(id: number) {
  if (!props.node.nextWorkflowNodeIds.includes(id)) {
    return ''
  }
  const node = props.allNodes.find(n => n.id === id)
  return node ? node.name : ''
}

function handleNextNodeChange(val: number, case_: Case) {
  const isValid = props.node.nextWorkflowNodeIds.includes(val)
  const nodeExists = props.allNodes.some(n => n.id === val)
  if (isValid && nodeExists) {
    case_.next_node = val
  } else {
    case_.next_node = null
  }
}

function getNextNodeValue(case_: Case): number | null {
  if (case_.next_node === null) return null
  const isValid = props.node.nextWorkflowNodeIds.includes(case_.next_node)
  const nodeExists = props.allNodes.some((n: { id: number }) => n.id === case_.next_node)
  return (nodeExists && isValid) ? case_.next_node : null
}

function bindInputType(input: Input) {
  watchEffect(() => {
    if (!input.value) return
    const { nodeId, outputId } = input.value
    const node = allUpstreamNodes.value.find((n: { id: number }) => n.id === nodeId)
    const output = node?.outputs?.find((o: { id: number; type: string }) => o.id === outputId)
    input.type = output?.type ?? 'string'
  })
}

const validNextNodeIds = computed(() => {
  return props.node.nextWorkflowNodeIds.filter(id =>
      props.allNodes.some(n => n.id === id)
  )
})

function isNodeValid() {
  if (!props.node.name || props.node.name.length === 0) return '未配置节点名称'
  if (!inputs || inputs.value.length === 0) return '未配置输入变量！'
  if (!outputs || outputs.value.length === 0) return '未配置输出变量！'

  for (const input of inputs.value) {
    if (!input.name || input.name.trim() === '') return '未配置输入变量的名称！'
    const value = input.value
    if (value?.type === 1) {
      if (generateSelectValue(input).trim() === '') return '未选择输入变量的来源！'
    } else if (value?.type === 0) {
      if (!value.text || value.text.trim() === '') return '未配置输入变量的值！'
    } else {
      return '未知配置！'
    }
  }
  for (const output of outputs.value) {
    if (!output.name || output.name.trim() === '') return '未配置输出变量的名称！'
  }
  if (!cases || cases.value.length === 0) return '未配置分支！'
  for (const case_ of cases.value) {
    if (getNextNodeValue(case_) === null) return '未选择下一个节点！'
    for (const condition of case_.condition) {
      if (condition.variable === null) return '未选择条件变量！'
    }
  }
  return ''
}

// 打开运行面板
function openRunPanel() {
  const isValid = isNodeValid()
  if (isValid !== '') {
    ElMessage.warning(isValid)
    return
  }
  runInputs.value = {}
  runResult.value = []
  runStatus.value = null
  runError.value = null
  inputs.value.forEach(input => {
    runInputs.value[input.name] = ''
  })
  showRunPanel.value = true
}

// 运行节点
async function run() {
  isRunning.value = true
  runStatus.value = 'running'
  runResult.value = []
  runError.value = null
  
  const formattedInputs = inputs.value.map(input => ({
    name: input.name,
    type: input.type,
    value: runInputs.value[input.name] || ''
  }))

  try {
    const response = await axios({
      method: 'post',
      url: '/workflow/runSingle',
      data: {
        workflow_id: props.workflow_id,
        node_id: props.node.id,
        inputs: JSON.stringify(formattedInputs)
      }
    })
    const data = await response.data
    if (data.code === 0) {
      runResult.value = outputs.value.map(output => ({
        name: output.name,
        value: data.result[output.id.toString()] ?? ''
      }))
      runStatus.value = 'success'
    } else {
      runStatus.value = 'error'
      runError.value = data.message || '执行失败'
    }
  } catch (e: any) {
    runStatus.value = 'error'
    runError.value = e.message || String(e)
  } finally {
    isRunning.value = false
  }
}

defineExpose({
  openRunPanel
})
</script>

<template>
  <div class="condition-node-detail">
    <!-- 输入变量配置 -->
    <div class="section">
      <div class="section-header">
        <h4>输入变量</h4>
        <el-button type="primary" size="small" @click="addInput">
          添加变量
        </el-button>
      </div>

      <div v-if="inputs.length === 0" class="empty-state">
        <p>暂无输入变量，点击"添加变量"创建</p>
      </div>

      <div v-else class="input-list">
        <div v-for="input in inputs" :key="input.id" class="input-item">
          <div class="input-row">
            <el-input
                v-model="input.name"
                placeholder="变量名称（必填）"
                size="small"
                class="name-input"
            />
            <el-select
                :model-value="generateSelectValue(input)"
                placeholder="选择来源"
                size="small"
                class="source-select"
                @change="val => onSelectChange(val, input)"
            >
              <template v-for="node in allUpstreamNodes" :key="node.id">
                <el-option
                    v-for="(nodeOutput, idx) in node.outputs"
                    :key="`${node.id}-${idx}`"
                    :label="`${node.name}: ${nodeOutput.name} (${nodeOutput.type})`"
                    :value="`${node.id}|${nodeOutput.id}`"
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

    <!-- 条件配置 -->
    <div class="section">
      <div class="section-header">
        <h4>条件配置</h4>
        <el-button type="primary" size="small" @click="addCase">
          添加分支
        </el-button>
      </div>

      <div v-if="cases.length === 0" class="empty-state">
        <p>暂无条件分支，点击"添加分支"创建</p>
      </div>

      <div v-else class="case-list">
        <div v-for="(case_, idx) in cases" :key="idx" class="case-item">
          <div class="case-header">
            <span class="case-title">case {{ idx + 1 }}</span>
            <el-button
                type="danger"
                size="small"
                @click="removeCase(idx)"
            >
              删除分支
            </el-button>
          </div>

          <template v-if="idx !== cases.length">
            <div class="condition-list">
              <div v-for="(condition, condIdx) in case_.condition" :key="condIdx" class="condition-item">
                <el-select
                    v-model="condition.variable"
                    placeholder="请选择变量"
                    size="small"
                    class="variable-select"
                >
                  <el-option
                      v-for="input in inputs.filter(i => i.name)"
                      :key="input.id"
                      :label="input.name"
                      :value="input.id"
                  />
                </el-select>

                <el-select
                    v-model="condition.compare_type"
                    placeholder="选择比较方式"
                    size="small"
                    class="compare-type-select"
                >
                  <el-option
                      v-for="type in compareTypes"
                      :key="type.value"
                      :label="type.label"
                      :value="type.value"
                  />
                </el-select>

                <el-input
                    v-if="![7, 8].includes(condition.compare_type)"
                    v-model="condition.compare_value"
                    placeholder="比较值"
                    size="small"
                    class="compare-value-input"
                />

                <el-button
                    type="danger"
                    size="small"
                    @click="removeCondition(case_, condIdx)"
                    class="remove-btn"
                >
                  删除
                </el-button>
              </div>

              <div class="condition-actions" v-if="idx !== cases.length - 1">
                <el-button
                    type="primary"
                    size="small"
                    plain
                    @click="addCondition(case_)"
                >
                  添加条件
                </el-button>

                <el-select
                    v-if="case_.condition.length > 1"
                    v-model="case_.and_or"
                    size="small"
                    class="and-or-select"
                >
                  <el-option label="或" :value="0" />
                  <el-option label="且" :value="1" />
                </el-select>
              </div>
            </div>
          </template>

          <div class="next-node">
            <label>下一个节点</label>
            <el-select
                :model-value="getNextNodeValue(case_)"
                placeholder="请选择下游节点"
                size="small"
                @change="val => handleNextNodeChange(val, case_)"
            >
              <el-option
                  v-for="id in validNextNodeIds"
                  :key="id"
                  :label="getNodeNameById(id)"
                  :value="id"
              />
            </el-select>
          </div>
        </div>
      </div>
    </div>

    <!-- 输出变量显示 -->
    <div class="section">
      <div class="section-header">
        <h4>输出变量</h4>
      </div>
      <div class="output-list">
        <div v-for="output in outputs" :key="output.id" class="output-item">
          <div class="output-row">
            <el-input
                :placeholder="output.name"
                size="small"
                class="name-input"
                disabled
            />
            <el-input
                :placeholder="output.type"
                size="small"
                class="name-input"
                disabled
            />
          </div>
        </div>
      </div>
    </div>

    <!-- 运行面板 -->
    <el-dialog
        v-model="showRunPanel"
        title="运行节点"
        width="500px"
        :close-on-click-modal="false"
    >
      <div class="run-panel">
        <div v-for="(input, name) in runInputs" :key="name" class="run-input-item">
          <label>{{ name }}</label>
          <el-input
              v-model="runInputs[name]"
              size="small"
              :placeholder="`请输入 ${name}`"
          />
        </div>
      </div>

      <div v-if="runStatus" class="run-result-section">
        <div class="run-result-header">
          <h4>运行结果</h4>
          <span :class="['status-badge', runStatus]">
            {{ runStatus === 'running' ? '运行中' :
              runStatus === 'success' ? '成功' : '失败' }}
          </span>
        </div>

        <!-- 成功结果 -->
        <div v-if="runStatus === 'success' && runResult.length">
          <div class="result-list">
            <div v-for="item in runResult" :key="item.name" class="result-item">
              <div class="result-name">
                <span class="name-label">{{ item.name }}</span>
              </div>
              <div class="result-value">
                <div class="value-content">{{ item.value }}</div>
              </div>
            </div>
          </div>
        </div>

        <!-- 错误信息 -->
        <div v-if="runStatus === 'error' && runError"
             class="result-content error">
          <pre>{{ runError }}</pre>
        </div>

        <!-- 加载动画 -->
        <div v-if="runStatus === 'running'" class="result-content loading">
          <div class="loading-spinner"></div>
          <span>正在运行中...</span>
        </div>
      </div>

      <template #footer>
        <el-button @click="showRunPanel = false">取消</el-button>
        <el-button
            type="primary"
            :loading="isRunning"
            @click="run"
        >
          运行
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
.condition-node-detail {
  padding: 16px;
}

.section {
  background: #fff;
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 24px;
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

.input-list,
.output-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.input-item,
.output-item {
  background: #f8f9fa;
  border-radius: 8px;
  padding: 12px;
}

.input-row,
.output-row {
  display: flex;
  gap: 12px;
  align-items: center;
}

.name-input {
  flex: 0.7;
}

.source-select {
  flex: 0.8;
}

.remove-btn {
  flex-shrink: 0;
}

.case-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.case-item {
  background: #f8f9fa;
  border-radius: 8px;
  padding: 16px;
}

.case-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.case-title {
  font-weight: 500;
  color: #2c3e50;
}

.condition-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-bottom: 16px;
}

.condition-item {
  display: flex;
  gap: 12px;
  align-items: center;
}

.variable-select,
.compare-type-select {
  flex: 1;
}

.compare-value-input {
  flex: 1;
}

.condition-actions {
  display: flex;
  gap: 12px;
  align-items: center;
  margin-top: 12px;
}

.and-or-select {
  width: 100px;
}

.next-node {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.next-node label {
  font-size: 14px;
  color: #606266;
}

.output-info {
  display: flex;
  align-items: center;
  gap: 8px;
}

.output-name {
  font-weight: 500;
  color: #2c3e50;
}

.output-type {
  color: #606266;
  font-size: 13px;
}

/* 运行面板相关样式 */
.run-panel {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.run-input-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.run-input-item label {
  font-size: 14px;
  color: #666;
}

.run-result-section {
  margin-top: 16px;
  border-top: 1px solid #eee;
  padding-top: 16px;
}

.run-result-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.run-result-header h4 {
  margin: 0;
  color: #2c3e50;
  font-size: 14px;
}

.status-badge {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
}

.status-badge.running {
  background: #e3f2fd;
  color: #2196f3;
}

.status-badge.success {
  background: #e8f5e9;
  color: #4caf50;
}

.status-badge.error {
  background: #ffebee;
  color: #f44336;
}

.result-content {
  background: #f8f9fa;
  border-radius: 4px;
  padding: 12px;
  margin-top: 8px;
  font-family: monospace;
  font-size: 12px;
  max-height: 200px;
  overflow-y: auto;
}

.result-content.error {
  background: #ffebee;
  color: #d32f2f;
}

.result-content pre {
  margin: 0;
  white-space: pre-wrap;
  word-break: break-all;
}

.loading-spinner {
  width: 20px;
  height: 20px;
  border: 2px solid #e3e3e3;
  border-top: 2px solid #3498db;
  border-radius: 50%;
  margin-right: 8px;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.result-content.loading {
  display: flex;
  align-items: center;
  justify-content: center;
  color: #666;
}

.result-list {
  overflow-y: auto;
  flex: 1;
  padding: 12px;
}

.result-item {
  background: #ffffff;
  border: 1px solid #e6e8eb;
  border-radius: 6px;
  margin-bottom: 8px;
  overflow: hidden;
}

.result-item:last-child {
  margin-bottom: 0;
}

.result-name {
  padding: 10px 16px;
  background: #f9fafb;
  border-bottom: 1px solid #e6e8eb;
  font-size: 13px;
  font-weight: 500;
  color: #374151;
}

.result-value {
  padding: 12px 16px;
  font-family: monospace;
  font-size: 13px;
  line-height: 1.6;
  color: #1f2937;
  background: #ffffff;
  overflow-x: auto;
}

.result-value > div {
  white-space: pre-wrap;
  word-break: break-word;
}
</style> 