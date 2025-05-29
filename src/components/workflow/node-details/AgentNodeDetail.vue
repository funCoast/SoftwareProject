<script setup lang="ts">
import { ref, computed, defineProps, defineEmits, onMounted, watch } from 'vue'
import { getAllUpstreamNodes } from '@/utils/getAllUpstreamNodes.ts'
import axios from 'axios'
import { ElMessage } from 'element-plus'

interface Input {
  id: number
  name: string
  type: string
  value: {
    type: number // 1: 上游节点的输出, 0: 手动输入
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

interface Agent {
  id: number
  icon: string
  name: string
  description: string
  status: 0 | 1 | 2
}

const props = defineProps<{
  node: {
    id: number
    type: string
    name: string
    inputs: Input[]
    outputs: Output[]
    data: {
      agent_id?: number
    }
  }
  allNodes: any[]
  workflow_id: string
  uid: string
}>()

// 初始化输入
const inputs = ref<Input[]>([])
const outputs = ref<Output[]>([])
// 智能体列表
const agents = ref<Agent[]>([])
const selectedAgentId = ref<number | null>(props.node.data?.agent_id || null)

const emit = defineEmits<{
  (e: 'update:node', node: any): void
}>()

// 监听变化并更新节点
watch([inputs, outputs, selectedAgentId], () => {
  emit('update:node', {
    ...props.node,
    inputs: inputs.value,
    outputs: outputs.value,
    data: {
      agent_id: selectedAgentId.value
    }
  })
}, { deep: true })

onMounted(() => {
  if (props.node.inputs && props.node.inputs.length > 0) {
    inputs.value = props.node.inputs;
  } else {
    inputs.value = [{
      id: 0,
      name: 'text',
      type: 'manual',
      value: {
        type: 0,
        nodeId: -1,
        outputId: -1,
        text: ''
      }
    }];
  }
  outputs.value = [{
    id: 0,
    name: 'output',
    type: 'string'
  }]
  fetchAgents()
})

// 获取所有上游节点
const allUpstreamNodes = computed(() => {
  return getAllUpstreamNodes(props.node, props.allNodes)
})

// 运行相关
const showRunPanel = ref(false)
const isRunning = ref(false)
const runStatus = ref<'running' | 'success' | 'error' | null>(null)
const runResult = ref<{ name: string; value: string }[]>([])
const runError = ref<string | null>(null)
const runInputs = ref<Record<string, string>>({})

// 添加弹窗控制变量
const showAgentDialog = ref(false)
const baseImageUrl = 'http://101.201.208.165'

// 获取智能体列表
async function fetchAgents() {
  try {
    const response = await axios({
      method: 'get',
      url: '/agent/fetchAll',
      params: {
        uid: props.uid
      }
    })

    if (response.data.code === 0) {
      agents.value = response.data.agents
    } else {
      ElMessage.error(response.data.message)
    }
  } catch (error) {
    console.error('获取智能体列表失败:', error)
    ElMessage.error('获取智能体列表失败')
  }
}

// 生成选择器的值
function generateSelectValue(input: Input): string {
  const val = input.value
  if (val.type === 0) {
    return 'manual'
  }
  if (val.type === 1 && val.nodeId !== -1 && val.outputId !== -1) {
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
  if (val === 'manual') {
    input.value.type = 0
    input.value.nodeId = -1
    input.value.outputId = -1
    return
  }
  const [nodeId, outputId] = val.split('|').map(Number)
  if (input.value) {
    input.value.nodeId = nodeId
    input.value.outputId = outputId
    input.value.type = 1
  }
}

// 运行模型
async function run() {
  isRunning.value = true
  runStatus.value = 'running'
  runResult.value = []
  runError.value = null

  try {
    const formattedInputs = inputs.value.map(input => ({
      name: input.name,
      type: input.type,
      value: runInputs.value[input.name] || ''
    }))

    const response = await axios({
      method: 'post',
      url: '/workflow/runSingle',
      data: {
        workflow_id: Number(props.workflow_id),
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
    runInputs.value[input.name] = input.value.type === 0 ? input.value.text : ''
  })
  showRunPanel.value = true
}

// 验证节点配置
function isNodeValid() {
  if (!props.node.name || props.node.name.length === 0) return '未配置节点名称'
  if (!props.node.inputs || props.node.inputs.length === 0) return '未配置输入变量！'
  if (!props.node.outputs || props.node.outputs.length === 0) return '未配置输出变量！'

  for (const input of props.node.inputs) {
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
  return ''
}

// 添加状态处理函数
function getStatusType(status?: string) {
  switch (status) {
    case 2:
      return 'success'
    case 1:
      return 'warning'
    case 0:
      return 'info'
    default:
      return 'info'
  }
}

function getStatusText(status?: string) {
  switch (status) {
    case 2:
      return '已发布'
    case 1:
      return '审核中'
    case 0:
      return '私有'
    default:
      return '未知'
  }
}

// 暴露方法给父组件
defineExpose({
  openRunPanel: openRunPanel,
  isNodeValid: isNodeValid
})
</script>

<template>
  <div class="agent-node-detail">
    <!-- 输入变量 -->
    <div class="section">
      <div class="section-header">
        <h4>输入变量</h4>
      </div>

      <div class="input-list">
        <div v-for="input in inputs" :key="input.id" class="input-item">
          <div class="input-row">
            <el-input
                :placeholder="input.name"
                size="small"
                class="name-input"
                disabled
            />
            <el-select
                :model-value="generateSelectValue(input)"
                placeholder="选择来源"
                size="small"
                class="source-select"
                @change="(val: string) => onSelectChange(val, input)"
            >
              <el-option
                  label="手动输入"
                  value="manual"
              />
              <template v-for="node in allUpstreamNodes" :key="node.id">
                <el-option
                    v-for="(nodeOutput, idx) in node.outputs"
                    :key="`${node.id}-${idx}`"
                    :label="`${node.name}: ${nodeOutput.name} (${nodeOutput.type})`"
                    :value="`${node.id}|${nodeOutput.id}`"
                />
              </template>
            </el-select>
          </div>
          <div v-if="input.value.type === 0" class="input-row" style="margin-top: 8px;">
            <el-input
                v-model="input.value.text"
                type="textarea"
                :rows="3"
                placeholder="请输入内容（必填）"
            />
          </div>
        </div>
      </div>
    </div>

    <!-- 智能体配置 -->
    <div class="section">
      <div class="section-header">
        <h4>智能体配置</h4>
      </div>
      
      <div class="form-group">
        <el-button
            type="primary"
            size="small"
            class="select-agent-btn"
            @click="showAgentDialog = true"
        >
          选择智能体 {{ selectedAgentId ? '(已选择)' : '' }}
        </el-button>
      </div>

      <!-- 已选智能体展示 -->
      <div v-if="selectedAgentId" class="selected-agent">
        <div class="agent-item">
          <el-avatar
              :size="32"
              :src="baseImageUrl + agents.find(a => a.id === selectedAgentId)?.icon"
              class="agent-icon"
          />
          <div class="agent-info">
            <div class="agent-name">{{ agents.find(a => a.id === selectedAgentId)?.name }}</div>
            <div class="agent-desc">{{ agents.find(a => a.id === selectedAgentId)?.description }}</div>
          </div>
          <el-tag
              :type="getStatusType(agents.find(a => a.id === selectedAgentId)?.status)"
              size="small"
              class="status-tag"
          >
            {{ getStatusText(agents.find(a => a.id === selectedAgentId)?.status) }}
          </el-tag>
          <el-button
              type="text"
              class="remove-btn"
              @click="selectedAgentId = null"
          >
            移除
          </el-button>
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

    <!-- 智能体选择弹窗 -->
    <el-dialog
        v-model="showAgentDialog"
        title="选择智能体"
        width="800px"
        :close-on-click-modal="false"
    >
      <div class="agent-dialog-content">
        <div class="agent-list">
          <div
              v-for="agent in agents"
              :key="agent.id"
              class="agent-dialog-item"
              :class="{ 'selected': selectedAgentId === agent.id }"
              @click="selectedAgentId = agent.id"
          >
            <div class="agent-header">
              <el-avatar :size="40" :src="baseImageUrl + agent.icon" class="agent-icon" />
              <div class="agent-title">
                <div class="agent-name">{{ agent.name }}</div>
                <el-tag
                    :type="getStatusType(agent.status)"
                    size="small"
                    class="status-tag"
                >
                  {{ getStatusText(agent.status) }}
                </el-tag>
              </div>
            </div>
            <div class="agent-description">{{ agent.description }}</div>
          </div>
        </div>
      </div>
      <template #footer>
        <el-button @click="showAgentDialog = false">取消</el-button>
        <el-button type="primary" @click="showAgentDialog = false">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
.agent-node-detail {
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

.agent-select {
  width: 100%;
}

.agent-option {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 4px 0;
}

.agent-icon {
  width: 32px;
  height: 32px;
  border-radius: 6px;
  object-fit: cover;
}

.agent-info {
  flex: 1;
  min-width: 0;
}

.agent-name {
  font-weight: 500;
  color: #2c3e50;
  margin-bottom: 2px;
}

.agent-desc {
  font-size: 12px;
  color: #666;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.run-panel {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.run-input {
  display: flex;
  flex-direction: column;
  gap: 8px;
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
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
}

.result-value {
  padding: 12px 16px;
  font-family: 'SF Mono', SFMono-Regular, ui-monospace, 'DejaVu Sans Mono', Menlo, Consolas, monospace;
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

/* 暗色模式 */
@media (prefers-color-scheme: dark) {
  .result-item {
    background: #1a1a1a;
    border-color: #2d2d2d;
  }

  .result-name {
    background: #1f1f1f;
    border-color: #2d2d2d;
    color: #e5e7eb;
  }

  .result-value {
    color: #e5e7eb;
    background: #1a1a1a;
  }
}

/* 滚动条样式 */
.result-list::-webkit-scrollbar,
.result-value::-webkit-scrollbar {
  width: 4px;
  height: 4px;
}

.result-list::-webkit-scrollbar-thumb,
.result-value::-webkit-scrollbar-thumb {
  background: #d1d5db;
  border-radius: 4px;
}

.result-list::-webkit-scrollbar-track,
.result-value::-webkit-scrollbar-track {
  background: transparent;
}

/* 暗色模式滚动条 */
@media (prefers-color-scheme: dark) {
  .result-list::-webkit-scrollbar-thumb,
  .result-value::-webkit-scrollbar-thumb {
    background: #4d4d4d;
  }
}

.select-agent-btn {
  width: 100%;
}

.selected-agent {
  margin-top: 16px;
}

.agent-item {
  display: flex;
  align-items: center;
  padding: 12px;
  background: #f5f7fa;
  border-radius: 8px;
  gap: 12px;
}

.agent-icon {
  flex-shrink: 0;
}

.agent-info {
  flex: 1;
  min-width: 0;
}

.agent-name {
  font-weight: 500;
  color: #2c3e50;
  margin-bottom: 4px;
}

.agent-desc {
  font-size: 12px;
  color: #606266;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.status-tag {
  margin: 0 8px;
}

.remove-btn {
  color: #f56c6c;
  padding: 0;
}

.agent-dialog-content {
  max-height: 60vh;
  overflow-y: auto;
}

.agent-list {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
  padding: 16px;
}

.agent-dialog-item {
  position: relative;
  padding: 16px;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s;
}

.agent-dialog-item:hover {
  border-color: #409eff;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.agent-dialog-item.selected {
  border-color: #409eff;
  background-color: #ecf5ff;
}

.agent-header {
  display: flex;
  align-items: flex-start;
  margin-bottom: 12px;
  gap: 12px;
}

.agent-title {
  flex: 1;
  min-width: 0;
}

.agent-description {
  font-size: 13px;
  color: #606266;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>