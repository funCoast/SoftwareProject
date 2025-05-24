<script setup lang="ts">
import { ref, watch, computed, onMounted, onBeforeUnmount, nextTick } from 'vue'
import { getAllUpstreamNodes } from '@/utils/getAllUpstreamNodes.ts'
import * as monaco from 'monaco-editor'

interface Input {
  id: number
  name: string
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
  value?: any
}

const props = defineProps<{
  node: {
    id: number
    type: string
    label: string
    x: number
    y: number
    inputs: Input[]
    outputs: Output[]
    data: {
      code: string
      language: string
    }
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

// 初始化输入输出列表
const inputs = ref<Input[]>(props.node.inputs || [])
const outputs = ref<Output[]>(props.node.outputs?.map(output => ({
  ...output,
})) || [])
const code = ref(props.node.data?.code || '')
const language = ref(props.node.data?.language || 'python')

// 可选的输出类型
const outputTypes = [
  { label: '字符串', value: 'string' },
  { label: '数字', value: 'number' },
]

// 可选的编程语言
const languages = [
  { label: 'Python', value: 'python' },
  { label: 'JavaScript', value: 'javascript' }
]

// 运行面板相关
const showRunPanel = ref(false)
const isRunning = ref(false)
const runStatus = ref<'running' | 'success' | 'error' | null>(null)
const runResult = ref<any>(null)
const runError = ref<string | null>(null)
const runInputs = ref<Record<string, string>>({})

// Monaco Editor 相关
const editorContainer = ref<HTMLElement | null>(null)
let editor: monaco.editor.IStandaloneCodeEditor | null = null

// 全屏相关
const isFullscreen = ref(false)
const fullscreenContainer = ref<HTMLElement | null>(null)

// 初始化编辑器
function initEditor() {
  if (!editorContainer.value) return

  // 配置编辑器主题
  monaco.editor.defineTheme('customTheme', {
    base: 'vs',
    inherit: true,
    rules: [],
    colors: {
      'editor.background': '#f8f9fa',
    }
  })

  editor = monaco.editor.create(editorContainer.value, {
    value: code.value,
    language: language.value,
    theme: 'customTheme',
    minimap: { enabled: false },
    scrollBeyondLastLine: false,
    fontSize: 14,
    lineHeight: 21,
    padding: { top: 10, bottom: 10 },
    automaticLayout: true,
    tabSize: 4,
    wordWrap: 'off',
    lineNumbersMinChars: 4
  })

  // 监听编辑器内容变化
  editor.onDidChangeModelContent(() => {
    code.value = editor?.getValue() || ''
  })
}

// 更新编辑器语言
function updateEditorLanguage(newLanguage: string) {
  if (!editor) return
  monaco.editor.setModelLanguage(editor.getModel()!, newLanguage)
}

// 监听语言变化
watch(language, (newLang) => {
  updateEditorLanguage(newLang)
})

// 切换全屏模式
function toggleFullscreen() {
  isFullscreen.value = !isFullscreen.value
  if (isFullscreen.value) {
    // 进入全屏时重新初始化编辑器大小
    nextTick(() => {
      if (editor) {
        editor.layout()
      }
    })
  }
}

// 监听 ESC 键退出全屏
function handleKeydown(e: KeyboardEvent) {
  if (e.key === 'Escape' && isFullscreen.value) {
    toggleFullscreen()
  }
}

onMounted(() => {
  initEditor()
  window.addEventListener('keydown', handleKeydown)
})

onBeforeUnmount(() => {
  if (editor) {
    editor.dispose()
  }
  window.removeEventListener('keydown', handleKeydown)
})

// 监听变化并更新节点
watch([inputs, outputs, code, language], () => {
  const returnConfig: Record<string, string> = {}
  outputs.value.forEach(output => {
    returnConfig[output.name] = output.returnValue
  })

  emit('update:node', {
    ...props.node,
    inputs: inputs.value,
    outputs: outputs.value, // 从输出中移除 returnValue
    data: {
      code: code.value,
      language: language.value,
    }
  })
}, { deep: true })

// 添加新输入
function addInput() {
  const newId = inputs.value.length
      ? Math.max(...inputs.value.map((i: Input) => i.id)) + 1
      : 0

  inputs.value.push({
    id: newId,
    name: '',
    value: {
      type: 1,
      nodeId: -1,
      text: '',
      outputId: -1
    }
  })
}

// 删除输入
function removeInput(id: number) {
  const index = inputs.value.findIndex(i => i.id === id)
  if (index !== -1) {
    inputs.value.splice(index, 1)
  }
}

// 添加新输出
function addOutput() {
  const newId = outputs.value.length
      ? Math.max(...outputs.value.map((o: Output) => o.id)) + 1
      : 0

  outputs.value.push({
    id: newId,
    name: '',
    type: 'string'
  })
}

// 删除输出
function removeOutput(id: number) {
  const index = outputs.value.findIndex(o => o.id === id)
  if (index !== -1) {
    outputs.value.splice(index, 1)
  }
}

// 用于保持 select 的 value 绑定正确
function generateSelectValue(val: Input['value']): string {
  if (val?.type === 1 && val?.nodeId !== -1 && val?.outputId !== -1) {
    return `${val.nodeId}|${val.outputId}`
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

// 获取上游节点输出的类型
function getUpstreamOutputType(nodeId: number, outputId: number): string {
  const node = allUpstreamNodes.value.find((n: { id: number }) => n.id === nodeId)
  const output = node?.outputs?.find((o: { id: number }) => o.id === outputId)
  return output?.type || '未知类型'
}

// 打开运行面板
function openRunPanel() {
  // 初始化运行输入值
  runInputs.value = {}
  inputs.value.forEach(input => {
    runInputs.value[input.name] = ''
  })
  showRunPanel.value = true
}

// 运行代码
async function run() {
  isRunning.value = true
  runStatus.value = 'running'
  runResult.value = null
  runError.value = null

  try {
    const response = await fetch('/api/code/execute', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        code: code.value,
        language: language.value,
        inputs: runInputs.value
      })
    })

    const data = await response.json()
    if (data.success) {
      runResult.value = data.result
      runStatus.value = 'success'
      // 更新输出值
      Object.entries(data.result).forEach(([key, value]) => {
        const output = outputs.value.find(o => o.name === key)
        if (output) {
          output.value = value
        }
      })
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

defineExpose({
  openRunPanel
})
</script>

<template>
  <div class="code-node-detail">
    <!-- 输入变量区域 -->
    <div class="inputs-section">
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
                placeholder="变量名称"
                size="small"
                class="name-input"
            />
            <el-select
                :model-value="generateSelectValue(input.value)"
                placeholder="选择上游输出"
                size="small"
                class="type-select"
                @change="(val: string) => onSelectChange(val, input)"
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
          <div v-if="input.value && input.value.nodeId !== -1" class="input-type">
            类型: {{ getUpstreamOutputType(input.value.nodeId, input.value.outputId) }}
          </div>
        </div>
      </div>
    </div>

    <!-- 代码编辑区域 -->
    <div class="code-section" :class="{ 'fullscreen': isFullscreen }" ref="fullscreenContainer">
      <div class="section-header">
        <div class="header-left">
          <h4>代码编辑</h4>
          <el-select
              v-model="language"
              size="small"
              style="width: 120px; margin-left: 12px;"
          >
            <el-option
                v-for="lang in languages"
                :key="lang.value"
                :label="lang.label"
                :value="lang.value"
            />
          </el-select>
        </div>
        <div class="header-right">
          <img
              :src="isFullscreen
              ? 'https://api.iconify.design/material-symbols:fullscreen-exit.svg'
              : 'https://api.iconify.design/material-symbols:fullscreen.svg'"
              @click="toggleFullscreen"
              class="fullscreen-icon"
              :alt="isFullscreen ? '退出全屏' : '全屏'"
              :title="isFullscreen ? '退出全屏 (ESC)' : '全屏'"
          >
        </div>
      </div>
      <div class="code-editor-container">
        <div ref="editorContainer" class="monaco-editor"></div>
      </div>
    </div>

    <!-- 输出变量区域 -->
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
        </div>
      </div>
    </div>

    <!-- 运行面板 -->
    <el-dialog
        v-model="showRunPanel"
        title="运行代码"
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
        <div v-if="runStatus === 'success' && runResult"
             class="result-content success">
          <pre>{{ JSON.stringify(runResult, null, 2) }}</pre>
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
.code-node-detail {
  padding: 16px;
}

.code-section,
.inputs-section,
.outputs-section {
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

.code-editor-container {
  position: relative;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
}

.monaco-editor {
  height: 300px;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  overflow: hidden;
}

.code-editor :deep(.el-textarea__inner) {
  border: none;
  border-bottom: 1px dashed #dcdfe6;
  border-radius: 4px 4px 0 0;
  resize: vertical;
  min-height: 200px;
  font-family: monospace;
  padding-bottom: 60px; /* 为返回代码预留空间 */
}

.return-empty pre,
.return-content pre {
  margin: 0;
  font-family: monospace;
  font-size: 14px;
  color: #606266;
}

.return-value-input :deep(.el-input__inner) {
  font-family: monospace;
  font-size: 14px;
  padding: 0 8px;
  height: 24px;
  background: rgba(255, 255, 255, 0.8);
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
  flex: 2;
}

.type-select {
  flex: 2;
}

.remove-btn {
  flex-shrink: 0;
}

.input-type {
  margin-top: 8px;
  font-size: 12px;
  color: #666;
  padding-left: 4px;
}

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

.code-section {
  background: #fff;
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 24px;
  transition: all 0.3s ease;
}

.code-section.fullscreen {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 1000;
  margin: 0;
  border-radius: 0;
  background: #fff;
  padding: 24px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.fullscreen-icon {
  width: 24px;
  height: 24px;
  cursor: pointer;
  opacity: 0.7;
  transition: all 0.2s ease;
}

.fullscreen-icon:hover {
  opacity: 1;
  transform: scale(1.1);
}

.monaco-editor {
  height: 300px;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  overflow: hidden;
  transition: height 0.3s ease;
}

.fullscreen .monaco-editor {
  height: calc(100vh - 120px);
}

.fullscreen .code-editor-container {
  margin-bottom: 0;
}
</style> 