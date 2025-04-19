<template>
  <div class="http-node-detail">
    <!-- 输入变量 -->
    <div class="section">
      <div class="section-header">
        <h4>输入变量</h4>
      </div>
      
      <div class="input-config">
        <!-- API 输入 -->
        <div class="form-group">
          <label>API 地址</label>
          <el-input
            v-model="inputs[0].value.text"
            placeholder="请输入 API 地址"
            size="small"
            @input="updateNode"
          />
        </div>
        
        <!-- 请求类型选择 -->
        <div class="form-group">
          <label>请求类型</label>
          <el-select
            v-model="inputs[1].value.text"
            placeholder="请选择请求类型"
            size="small"
            class="type-select"
            @change="updateNode"
          >
            <el-option label="GET" value="get" />
            <el-option label="POST" value="post" />
          </el-select>
        </div>
      </div>
    </div>

    <!-- 输出变量 -->
    <div class="section">
      <div class="section-header">
        <h4>输出变量</h4>
      </div>
      
      <div class="output-info">
        <div class="info-item" v-for="output in outputs" :key="output.id">
          <label>{{ output.name }}:</label>
          <span>{{ output.type }}</span>
        </div>
      </div>
    </div>

    <!-- 运行面板 -->
    <el-dialog
      v-model="showRunPanel"
      title="运行 HTTP 请求"
      width="500px"
      :close-on-click-modal="false"
    >
      <div class="run-panel">
        <div class="run-input">
          <div class="form-group">
            <label>API 地址</label>
            <el-input
              v-model="runInputs.api"
              type="text"
              :placeholder="inputs[0].value.text || '请输入 API 地址'"
            />
          </div>
          <div class="form-group">
            <label>请求类型</label>
            <el-select
              v-model="runInputs.apiType"
              placeholder="请选择请求类型"
              style="width: 100%"
            >
              <el-option label="GET" value="get" />
              <el-option label="POST" value="post" />
            </el-select>
          </div>
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
          <div class="result-item">
            <label>Status Code:</label>
            <span>{{ runResult.status_code }}</span>
          </div>
          <div class="result-item">
            <label>Body:</label>
            <pre>{{ runResult.body }}</pre>
          </div>
          <div class="result-item">
            <label>Headers:</label>
            <pre>{{ JSON.stringify(runResult.headers, null, 2) }}</pre>
          </div>
          <div class="result-item" v-if="runResult.files?.length">
            <label>Files:</label>
            <div v-for="(file, index) in runResult.files" :key="index">
              {{ file.name }} ({{ file.size }} bytes)
            </div>
          </div>
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

<script setup lang="ts">
import { ref, onMounted } from 'vue'

interface Input {
  id: number
  name: string
  type: string
  value: {
    text: string
  }
}

interface Output {
  id: number
  name: string
  type: string
  value?: any
}

const props = defineProps<{
  node: {
    id: number
    type: string
    name: string
    inputs: Input[]
    outputs: Output[]
    data: Record<string, any>
  }
}>()

const emit = defineEmits<{
  (e: 'update:node', node: any): void
}>()

// 初始化输入
const inputs = ref<Input[]>([
  {
    id: 0,
    name: 'api',
    type: 'string',
    value: {
      text: ''
    }
  },
  {
    id: 1,
    name: 'apiType',
    type: 'string',
    value: {
      text: 'get'
    }
  }
])

// 初始化输出
const outputs = ref<Output[]>([
  {
    id: 0,
    name: 'body',
    type: 'string'
  },
  {
    id: 1,
    name: 'status_code',
    type: 'number'
  },
  {
    id: 2,
    name: 'headers',
    type: 'Object'
  },
  {
    id: 3,
    name: 'files',
    type: 'Array[File]'
  }
])

// 运行相关
const showRunPanel = ref(false)
const isRunning = ref(false)
const runStatus = ref<'running' | 'success' | 'error' | null>(null)
const runResult = ref<any>(null)
const runError = ref<string | null>(null)
const runInputs = ref({
  api: '',
  apiType: 'get'
})

// 更新节点
function updateNode() {
  emit('update:node', {
    ...props.node,
    inputs: inputs.value,
    outputs: outputs.value,
    data: {
      initialized: true
    }
  })
}

// 运行
async function run() {
  isRunning.value = true
  runStatus.value = 'running'
  runResult.value = null
  runError.value = null

  try {
    const response = await fetch('/api/http/request', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        url: runInputs.value.api,
        method: runInputs.value.apiType
      })
    })

    const data = await response.json()
    if (data.success) {
      runResult.value = data.result
      runStatus.value = 'success'
    } else {
      runStatus.value = 'error'
      runError.value = data.error || '执行失败'
    }
  } catch (e: any) {
    runStatus.value = 'error'
    runError.value = e.message || String(e)
  } finally {
    isRunning.value = false
  }
}

// 初始化配置
onMounted(() => {
  if (!props.node.data?.initialized) {
    updateNode()
  } else {
    inputs.value = props.node.inputs
    outputs.value = props.node.outputs
  }
})

// 暴露方法给父组件
defineExpose({
  openRunPanel: () => {
    runInputs.value.api = inputs.value[0].value.text
    runInputs.value.apiType = inputs.value[1].value.text
    showRunPanel.value = true
  }
})
</script>

<style scoped>
.http-node-detail {
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

.type-select {
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
  max-height: 300px;
  overflow-y: auto;
}

.result-content.error {
  background: #ffebee;
  color: #d32f2f;
}

.result-item {
  margin-bottom: 12px;
}

.result-item:last-child {
  margin-bottom: 0;
}

.result-item label {
  display: block;
  color: #666;
  margin-bottom: 4px;
}

.result-item pre {
  margin: 0;
  white-space: pre-wrap;
  word-break: break-all;
  background: #fff;
  padding: 8px;
  border-radius: 4px;
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