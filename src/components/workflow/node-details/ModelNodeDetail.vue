<script setup lang="ts">
import { ref, computed, defineProps, defineEmits, onMounted } from 'vue'
import { getAllUpstreamNodes } from '../../../utils/getAllUpstreamNodes'
import axios from "axios";

interface Input {
  id: number
  name: string
  type: 'string'
  value: {
    type?: number // 1: 上游节点的输出
    nodeId?: number
    outputId?: number
    text?: string // 手动输入的内容
  }
}

interface Output {
  id: number
  name: 'text'
  type: 'string'
  value?: string
}

const props = defineProps<{
  node: {
    id: number
    type: string
    name: string
    inputs: Input[]
    outputs: Output[]
  }
  allNodes: any[],
  workflow_id: string
}>()

const emit = defineEmits<{
  (e: 'update:node', node: any): void
}>()

// 获取所有上游节点
const allUpstreamNodes = computed(() => {
  return getAllUpstreamNodes(props.node, props.allNodes)
})

// 初始化输入
const inputs = ref<Input[]>(props.node.inputs?.length ? props.node.inputs : [
  {
    id: 0,
    name: 'system_prompt',
    type: 'string',
    value: {
      text: '',
      type: 0,
      nodeId: -1,
      outputId: -1
    }
  },
  {
    id: 1,
    name: 'user_prompt',
    type: 'string',
    value: {
      text: '',
      type: 0,
      nodeId: -1,
      outputId: -1
    }
  }
])

// 运行相关
const showRunPanel = ref(false)
const isRunning = ref(false)
const runStatus = ref<'running' | 'success' | 'error' | null>(null)
const runResult = ref<string | null>(null)
const runError = ref<string | null>(null)
const runSystemPrompt = ref('')
const runUserPrompt = ref('')

// 是否为手动输入
function isManualInput(input: Input) {
  return !input.value?.type || input.value.type !== 1
}

// 生成选择器的值
function generateSelectValue(val?: Input['value']): string {
  if (!val?.type || val.type !== 1) return 'manual'
  return `${val.nodeId}|${val.outputId}`
}

// 处理选择变化
function onSelectChange(inputId: number, val: string) {
  const input = inputs.value.find(i => i.id === inputId)
  if (!input) return

  if (val === 'manual') {
    input.value = {
      type: 0,
      nodeId: -1,
      outputId: -1,
      text: ''
    }
  } else {
    const [nodeId, outputId] = val.split('|').map(Number)
    input.value = {
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
    inputs: inputs.value,
    outputs: [{
      id: 0,
      name: 'text',
      type: 'string'
    }]
  })
}

// 运行模型
async function run() {
  isRunning.value = true
  runStatus.value = 'running'
  runResult.value = null
  runError.value = null

  try {
    const formattedInputs = [
      {
        "name": "system_prompt",
        "type": "string",
        "value": runSystemPrompt.value
      },
      {
        "name": "user_prompt",
        "type": "string",
        "value": runUserPrompt.value
      }
    ]
    console.log(props.workflow_id)
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
      runResult.value = data.result
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

// 暴露方法给父组件
defineExpose({
  openRunPanel: () => {
    const systemPromptInput = inputs.value.find(i => i.name === 'system_prompt')
    const userPromptInput = inputs.value.find(i => i.name === 'user_prompt')
    runSystemPrompt.value = systemPromptInput?.value?.text || ''
    runUserPrompt.value = userPromptInput?.value?.text || ''
    showRunPanel.value = true
  }
})
</script>

<template>
  <div class="model-node-detail">
    <!-- 输入配置 -->
    <div class="section">
      <div class="section-header">
        <h4>输入变量</h4>
      </div>
      
      <div class="input-config">
        <template v-for="input in inputs" :key="input.id">
          <div class="input-group">
            <div class="input-header">
              <h5>{{ input.name === 'system_prompt' ? '系统提示词' : '用户提示词' }}</h5>
            </div>
            
            <div class="form-group">
              <label>输入来源</label>
              <el-select
                :model-value="generateSelectValue(input.value)"
                placeholder="选择输入来源"
                size="small"
                class="source-select"
                @change="val => onSelectChange(input.id, val)"
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
            
            <div v-if="isManualInput(input)" class="form-group">
              <label>输入内容</label>
              <el-input
                v-model="input.value.text"
                type="textarea"
                :rows="3"
                :placeholder="input.name === 'system_prompt' ? '请输入系统提示词' : '请输入用户提示词'"
                @input="updateNode"
              />
            </div>
          </div>
        </template>
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
          <span>text</span>
        </div>
        <div class="info-item">
          <label>变量类型:</label>
          <span>string</span>
        </div>
      </div>
    </div>

    <!-- 模型配置 -->
    <div class="section">
      <div class="section-header">
        <h4>模型配置</h4>
      </div>
      
      <div class="form-group">
        <label>模型类型</label>
        <div class="model-type">通义千问</div>
      </div>
    </div>

    <!-- 运行面板 -->
    <el-dialog
      v-model="showRunPanel"
      title="运行模型"
      width="500px"
      :close-on-click-modal="false"
    >
      <div class="run-panel">
        <div class="run-input">
          <label>系统提示词</label>
          <el-input
            v-model="runSystemPrompt"
            type="textarea"
            :rows="3"
            placeholder="请输入系统提示词"
          />
        </div>
        <div class="run-input">
          <label>用户提示词</label>
          <el-input
            v-model="runUserPrompt"
            type="textarea"
            :rows="3"
            placeholder="请输入用户提示词"
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
        
        <div v-if="runStatus === 'success' && runResult" 
             class="result-content success">
          <pre>{{ runResult }}</pre>
        </div>
        
        <div v-if="runStatus === 'error' && runError" 
             class="result-content error">
          <pre>{{ runError }}</pre>
        </div>
        
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
.model-node-detail {
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

.input-group {
  background: #f8f9fa;
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 16px;
}

.input-group:last-child {
  margin-bottom: 0;
}

.input-header {
  margin-bottom: 16px;
}

.input-header h5 {
  margin: 0;
  font-size: 14px;
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

.model-type {
  padding: 8px 12px;
  background: #f5f7fa;
  border-radius: 4px;
  color: #606266;
  font-size: 14px;
}

.source-select {
  width: 100%;
}

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
</style> 