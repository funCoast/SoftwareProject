<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import {getAllUpstreamNodes} from '../../../utils/getAllUpstreamNodes'
import axios from 'axios'

interface Input {
  id: number
  name: string
  type: string
  value: {
    type: number
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

interface ClassConfig {
  description: string
  next_node: number
}

interface WorkflowNode {
  id: number
  name: string
  type: string
  inputs: Input[]
  outputs: Output[]
}

const props = defineProps<{
  node: {
    id: number
    type: string
    name: string
    inputs: Input[]
    outputs: Output[]
    nextWorkflowNodeIds: number[]
    data: {
      classes?: ClassConfig[]
      initialized?: boolean
    }
  }
  allNodes: WorkflowNode[]
  workflow_id: string
}>()

const allUpstreamNodes = computed(() => {
  return getAllUpstreamNodes(props.node, props.allNodes)
})

const emit = defineEmits<{
  (e: 'update:node', node: any): void
}>()

// 选中的输入变量
const selectedInput = ref<{
  nodeId: number
  outputId: number
  name: string
  type: string
} | null>(null)

// 初始化输入
const input = ref<Input>({
  id: 0,
  name: '',
  type: 'string',
  value: {
    type: 1,
    nodeId: -1,
    outputId: -1
  }
})

// 初始化输出
const output = ref<Output>({
  id: 0,
  name: 'option',
  type: 'string'
})

// 后置节点列表
const nextNodes = computed(() => props.node.nextWorkflowNodeIds || [])

// 分支配置
const classConfigs = ref<ClassConfig[]>(
  props.node.data?.classes || []
)

// 运行相关
const showRunPanel = ref(false)
const isRunning = ref(false)
const runStatus = ref<'running' | 'success' | 'error' | null>(null)
const runResult = ref<any>(null)
const runError = ref<string | null>(null)
const runInput = ref('')

// 获取节点名称
function getNodeName(nodeId: number): string {
  const node = props.allNodes.find(n => n.id === nodeId)
  return node?.name || '未知节点'
}

// 获取分支配置
function getClassConfig(nodeId: number): ClassConfig {
  let config = classConfigs.value.find(c => c.next_node === nodeId)
  if (!config) {
    config = {
      description: '',
      next_node: nodeId
    }
    classConfigs.value.push(config)
  }
  return config
}

// 更新节点
function updateNode() {
  emit('update:node', {
    ...props.node,
    inputs: [input.value],
    outputs: [output.value],
    data: {
      classes: classConfigs.value,
      initialized: true
    }
  })
}

// 更新输入变量
function updateInput() {
  if (selectedInput.value) {
    input.value = {
      id: 0,
      name: selectedInput.value.name,
      type: selectedInput.value.type,
      value: {
        type: 1,
        nodeId: selectedInput.value.nodeId,
        outputId: selectedInput.value.outputId
      }
    }
    updateNode()
  }
}

// 运行
async function run() {
  isRunning.value = true
  runStatus.value = 'running'
  runResult.value = null
  runError.value = null

  try {
    const formattedInputs = [
      {
        name: input.value.name,
        type: input.value.type,
        value: runInput.value
      }
    ]

    const response = await axios({
      method: 'post',
      url: '/workflow/runSingle',
      data: {
        workflow_id: Number(props.workflow_id),
        node_id: props.node.id,
        inputs: JSON.stringify(formattedInputs)
      }
    })

    const data = response.data
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

// 初始化配置
onMounted(() => {
  if (!props.node.data?.initialized) {
    updateNode()
  } else {
    input.value = props.node.inputs[0]
    classConfigs.value = props.node.data.classes || []
  }

  if (props.node.inputs[0]?.value) {
    const nodeId = props.node.inputs[0].value.nodeId
    const outputId = props.node.inputs[0].value.outputId
    const node = allUpstreamNodes.value.find((n: WorkflowNode) => n.id === nodeId)
    const output = node?.outputs.find((o: Output) => o.id === outputId)
    
    if (node && output) {
      selectedInput.value = {
        nodeId,
        outputId,
        name: output.name,
        type: output.type
      }
      input.value = {
        id: 0,
        name: output.name,
        type: output.type,
        value: {
          type: 1,
          nodeId,
          outputId
        }
      }
    }
  }
})

// 暴露方法给父组件
defineExpose({
  openRunPanel: () => {
    runInput.value = ''
    showRunPanel.value = true
  }
})
</script>

<template>
  <div class="classifier-node-detail">
    <!-- 输入变量 -->
    <div class="section">
      <div class="section-header">
        <h4>输入变量</h4>
      </div>

      <div class="input-config">
        <div class="form-group">
          <label>选择输入变量</label>
          <el-select
              v-model="selectedInput"
              placeholder="请选择上游节点的输出变量"
              class="input-select"
              @change="updateInput"
          >
            <el-option-group
                v-for="node in allUpstreamNodes"
                :key="node.id"
                :label="node.name"
            >
              <el-option
                  v-for="output in node.outputs"
                  :key="`${node.id}-${output.id}`"
                  :label="output.name"
                  :value="{
                  nodeId: node.id,
                  outputId: output.id,
                  name: output.name,
                  type: output.type
                }"
              >
                <span>{{ output.name }}</span>
                <span class="output-type">{{ output.type }}</span>
              </el-option>
            </el-option-group>
          </el-select>
        </div>
      </div>
    </div>

    <!-- 分支配置 -->
    <div class="section">
      <div class="section-header">
        <h4>分支配置</h4>
      </div>

      <div v-if="!nextNodes.length" class="empty-state">
        <p>暂无可用的后置节点</p>
      </div>

      <div v-else class="class-list">
        <div v-for="nodeId in nextNodes" :key="nodeId" class="class-item">
          <div class="class-header">
            <span class="branch-name">{{ getNodeName(nodeId) }}</span>
          </div>

          <div class="class-content">
            <div class="form-group">
              <label>分支描述</label>
              <el-input
                  v-model="getClassConfig(nodeId).description"
                  type="textarea"
                  :rows="2"
                  placeholder="请输入分支描述"
                  @input="updateNode"
              />
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 输出变量 -->
    <div class="section">
      <div class="section-header">
        <h4>输出变量</h4>
      </div>

      <div class="output-info">
        <div class="info-item">
          <label>变量名称:</label>
          <span>option</span>
        </div>
        <div class="info-item">
          <label>变量类型:</label>
          <span>string</span>
        </div>
      </div>
    </div>

    <!-- 运行面板 -->
    <el-dialog
        v-model="showRunPanel"
        title="运行分类器"
        width="500px"
        :close-on-click-modal="false"
    >
      <div class="run-panel">
        <div class="run-input">
          <label>{{ input.name }}</label>
          <el-input
              v-model="runInput"
              type="textarea"
              :rows="4"
              :placeholder="`请输入${input.name}`"
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
          <div class="result-item">
            <label>选择的分支:</label>
            <div class="branch-result">
              <span class="branch-name">{{ getNodeName(runResult.next_node) }}</span>
              <span class="branch-desc">{{ getClassConfig(runResult.next_node).description }}</span>
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

<style scoped>
.classifier-node-detail {
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

.class-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.class-item {
  background: #f8f9fa;
  border-radius: 8px;
  padding: 16px;
}

.class-header {
  margin-bottom: 16px;
}

.branch-name {
  font-weight: 500;
  color: #2c3e50;
}

.class-content {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

label {
  font-weight: 500;
  color: #2c3e50;
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

.branch-result {
  margin-top: 8px;
  padding: 12px;
  background: #fff;
  border-radius: 4px;
}

.branch-result .branch-name {
  display: block;
  margin-bottom: 4px;
}

.branch-result .branch-desc {
  display: block;
  color: #666;
  font-size: 12px;
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

.input-select {
  width: 100%;
}

.output-type {
  float: right;
  color: #909399;
  font-size: 12px;
}
</style> 