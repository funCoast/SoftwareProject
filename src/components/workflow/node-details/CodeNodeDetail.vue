<script setup lang="ts">
import { ref, watch, computed, onMounted, onBeforeUnmount, nextTick, watchEffect } from 'vue'
import { getAllUpstreamNodes } from '@/utils/getAllUpstreamNodes.ts'
import * as monaco from 'monaco-editor'

import EditorWorker from 'monaco-editor/esm/vs/editor/editor.worker?worker'
import TsWorker from 'monaco-editor/esm/vs/language/typescript/ts.worker?worker'
import axios from "axios";

self.MonacoEnvironment = {
  getWorker: function (_moduleId, label) {
    if (label === 'typescript' || label === 'javascript') {
      return new TsWorker()
    }
    return new EditorWorker()
  }
}

interface Input {
  id: number
  name: string
  type: string
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
    name: string
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
  workflow_id: string
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
const outputs = ref<Output[]>(props.node.outputs || [])
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
const runResult = ref<{ name: string; value: string }[]>([])
const runError = ref<string | null>(null)
const runInputs = ref<Record<string, string>>({})

// Monaco Editor 相关
const editorContainer = ref<HTMLElement | null>(null)
let editor: monaco.editor.IStandaloneCodeEditor | null = null

// 全屏相关
const isFullscreen = ref(false)
const fullscreenContainer = ref<HTMLElement | null>(null)

// 结果全屏相关
const isResultFullscreen = ref(false)

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

// 切换结果全屏
function toggleResultFullscreen() {
  isResultFullscreen.value = !isResultFullscreen.value
}

// 监听 ESC 键退出全屏
function handleResultKeydown(e: KeyboardEvent) {
  if (e.key === 'Escape' && isResultFullscreen.value) {
    toggleResultFullscreen()
  }
}

onMounted(() => {
  initEditor()
  window.addEventListener('keydown', handleKeydown)
  window.addEventListener('keydown', handleResultKeydown)
})

onBeforeUnmount(() => {
  if (editor) {
    editor.dispose()
  }
  window.removeEventListener('keydown', handleKeydown)
  window.removeEventListener('keydown', handleResultKeydown)
})

// 监听变化并更新节点
watch([inputs, outputs, code, language], () => {
  emit('update:node', {
    ...props.node,
    inputs: inputs.value,
    outputs: outputs.value,
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

function bindInputType(input: Input) {
  watchEffect(() => {
    if (!input.value) return
    const { nodeId, outputId } = input.value
    const node = allUpstreamNodes.value.find(n => n.id === nodeId)
    const output = node?.outputs.find(o => o.id === outputId)
    input.type = output?.type ?? 'string'
  })
}

// 处理上游输出选择变化
function onSelectChange(val: string, input: Input) {
  const [nodeId, outputId] = val.split('|').map(Number)
  if (input.value) {
    input.value.nodeId = nodeId
    input.value.outputId = outputId
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
    runInputs.value[input.name] = ''
  })
  showRunPanel.value = true
}

// 运行代码
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
  if (!code || code.value.trim() === '') return '未输入代码！'
  return ''
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
                placeholder="变量名称（必填）"
                size="small"
                class="name-input"
            />
            <el-select
                :model-value="generateSelectValue(input)"
                placeholder="选择上游输出"
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
                placeholder="变量名称（必填）"
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
  flex: 0.7;
}

.type-select {
  flex: 0.8;
}

.source-select {
  flex: 0.8;
}

.remove-btn {
  flex-shrink: 0;
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

.fullscreen-btn img {
  width: 20px;
  height: 20px;
  opacity: 0.7;
}

.fullscreen-btn:hover img {
  opacity: 1;
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
</style> 