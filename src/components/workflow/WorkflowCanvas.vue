<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { usePersistentRef } from '../../utils/usePersistentRef'
import ClassifierNodeDetail from './node-details/ClassifierNodeDetail.vue'
import CodeNodeDetail from "./node-details/CodeNodeDetail.vue"
import ConditionNodeDetail from "./node-details/ConditionNodeDetail.vue"
import ExtractNodeDetail from './node-details/ExtractNodeDetail.vue'
import HttpNodeDetail from "./node-details/HttpNodeDetail.vue"
import KnowledgeNodeDetail from "./node-details/KnowledgeNodeDetail.vue"
import LoopNodeDetail from "./node-details/LoopNodeDetail.vue"
import ModelNodeDetail from './node-details/ModelNodeDetail.vue'
import WorkflowNodeDetail from './node-details/WorkflowNodeDetail.vue'
import CodeExplainPlugin from "./node-details/CodeExplainPlugin.vue";
import CurrentTimePlugin from "./node-details/CurrentTimePlugin.vue";
import TimestampPlugin from "./node-details/TimestampPlugin.vue";
import TimestampTransformPlugin from "./node-details/TimestampTransformPlugin.vue";
import TimezoneSwitchPlugin from "./node-details/TimezoneSwitchPlugin.vue";
import WeekdayCalculatorPlugin from "./node-details/WeekdayCalculatorPlugin.vue";
import WorkflowNodeManager from "./WorkflowNodeManager.vue";
import StartNodeDetail from './node-details/StartNodeDetail.vue'
import EndNodeDetail from './node-details/EndNodeDetail.vue'
import {useRouter} from "vue-router";
const router = useRouter()

interface nodeType {
  type: string
  label: string
  description: string
  image: string
  isPlugin: boolean
}

const nodeTypes = ref<nodeType[]>([
  { 
    type: 'model',
    label: '大模型',
    description: '使用AI大模型处理任务',
    image: 'https://api.iconify.design/carbon:machine-learning-model.svg',
    isPlugin: false
  },
  { 
    type: 'workflow',
    label: '工作流',
    description: '嵌套调用其他工作流',
    image: 'https://api.iconify.design/material-symbols:account-tree.svg',
    isPlugin: false
  },
  { 
    type: 'http',
    label: 'HTTP请求',
    description: '发送HTTP请求获取数据',
    image: 'https://api.iconify.design/material-symbols:api.svg',
    isPlugin: false
  },
  { 
    type: 'code',
    label: '代码',
    description: '执行自定义代码逻辑',
    image: 'https://api.iconify.design/material-symbols:code.svg',
    isPlugin: false
  },
  { 
    type: 'condition',
    label: '条件分支',
    description: '根据条件选择执行路径',
    image: 'https://api.iconify.design/material-symbols:fork-right.svg',
    isPlugin: false
  },
  { 
    type: 'loop',
    label: '循环',
    description: '重复执行特定任务',
    image: 'https://api.iconify.design/material-symbols:repeat.svg',
    isPlugin: false
  },
  { 
    type: 'classifier',
    label: '问题分类器',
    description: '对输入内容进行分类',
    image: 'https://api.iconify.design/material-symbols:category.svg',
    isPlugin: false
  },
  { 
    type: 'knowledge',
    label: '知识库检索',
    description: '从知识库中检索信息',
    image: 'https://api.iconify.design/material-symbols:database.svg',
    isPlugin: false
  },
  { 
    type: 'extract',
    label: '提取文档',
    description: '从文档中提取关键信息',
    image: 'https://api.iconify.design/material-symbols:description.svg',
    isPlugin: false
  },
  {
    type: 'current-time',
    label: '获取当前时间',
    description: '获取当前时间，支持多种格式和时区',
    image: 'https://api.iconify.design/material-symbols:extension.svg',
    isPlugin: true
  },
  {
    type: 'timezone-switch',
    label: '时区转换',
    description: '计算世界各个时区的时差，获取目标时区当前时间',
    image: 'https://api.iconify.design/material-symbols:extension.svg',
    isPlugin: true
  },
  {
    type: 'timestamp',
    label: '时间转时间戳',
    description: '将当前时间转换为时间戳',
    image: 'https://api.iconify.design/material-symbols:extension.svg',
    isPlugin: true
  },
  {
    type: 'timestamp-transform',
    label: '时间戳转时间',
    description: '将当前时间戳转换为时间',
    image: 'https://api.iconify.design/material-symbols:extension.svg',
    isPlugin: true
  },
  {
    type: 'weekday-calculator',
    label: '星期计算',
    description: '计算所给日期对应的星期',
    image: 'https://api.iconify.design/material-symbols:extension.svg',
    isPlugin: true
  },
  {
    type: 'code-explain',
    label: '代码解释器',
    description: '执行自定义代码逻辑',
    image: 'https://api.iconify.design/material-symbols:extension.svg',
    isPlugin: true
  }
])

const filteredNodeTypes = computed(() => nodeTypes.value.filter(n => !n.isPlugin))
const pluginNodeTypes = computed(() => nodeTypes.value.filter(n => n.isPlugin))

interface WorkflowNode {
  id: number
  type: string
  label: string
  name: string
  description: string
  image: string
  x: number
  y: number
  beforeWorkflowNodeIds: number[]
  nextWorkflowNodeIds: number[]
  inputs: Input[]
  outputs: Output[]
  data?: any
}

interface Input {
  id: number
  name: string
  type: string
  value?: {
    type: number //0:用户输入 1:上游节点的输出变量
    text: string //用户输入
    nodeId: number //上游节点id
    outputId: number //上游节点的输出变量id
  }
}

interface Output {
  id: number
  name: string
  type: string
  value?: any
}

interface Connection {
  id: number
  sourceId: number
  targetId: number
  sourceType: 'left' | 'right'
  targetType: 'left' | 'right'
}

const canvasEl = ref<HTMLElement>()
const zoom = ref(1)

const workflowNodes = usePersistentRef<WorkflowNode[]>('workflowNodes', [])
const connections = usePersistentRef<Connection[]>('connections', [])
const tempNode = ref<WorkflowNode | null>(null)
const selectedNode = ref<WorkflowNode | null>(null)

const showNodeSelector = ref(false)
const isAddingNode = ref(false)
const isDraggingCanvas = ref(false)
// 记录按下鼠标时的鼠标位置
const lastMousePosition = ref({ x: 0, y: 0 })
// 运行状态
const isNodeRunning = ref(false)
// 运行节点
const nodeComponentRefs = new Map<number, any>()
// 添加节点还是添加插件
const selectorPage = ref<'nodes' | 'plugins'>('nodes')

onMounted(() => {
  if (workflowNodes.value.length === 0) {
    workflowNodes.value.push(
        {
          id: 1,
          type: 'start',
          label: '开始节点',
          name: '开始节点',
          description: '',
          image: 'https://api.iconify.design/material-symbols:play-circle.svg',
          x: 200,
          y: 300,
          beforeWorkflowNodeIds: [],
          nextWorkflowNodeIds: [],
          inputs: [],
          outputs: [],
        },
        {
          id: 2,
          type: 'end',
          label: '结束节点',
          name: '结束节点',
          description: '',
          image: 'https://api.iconify.design/material-symbols:stop-circle.svg',
          x: 1200,
          y: 300,
          beforeWorkflowNodeIds: [],
          nextWorkflowNodeIds: [],
          inputs: [],
          outputs: [],
        }
    )
  }
  console.log('nodes:', workflowNodes.value)
  console.log('connections:', connections.value)
})

// 添加节点
function addNode(type: string, x: number, y: number) {
  const rect = canvasEl.value?.getBoundingClientRect()
  const nodeType = nodeTypes.value.find(nt => nt.type === type)
  if (!nodeType || !rect) return
  isAddingNode.value = true
  tempNode.value = {
    id: 0,
    type: type,
    label: nodeType.label,
    name: nodeType.label,
    description: '',
    image: nodeType.image,
    x: x - rect.left,
    y: y - rect.top,
    beforeWorkflowNodeIds: [],
    nextWorkflowNodeIds: [],
    inputs: [],
    outputs: [],
  }
  showNodeSelector.value = false
}

// 放下临时节点
function handleTempNodeClick(e: MouseEvent) {
  e.stopPropagation() // 阻止事件冒泡，防止点击临时节点时触发外层的 click 事件
  if (tempNode.value) {
    const newNode = {
      ...tempNode.value,
      id: Date.now()
    } as WorkflowNode
    workflowNodes.value.push(newNode) // 把节点添加到正式工作流中
    isAddingNode.value = false // 标记添加过程结束
    tempNode.value = null // 清空临时节点
  }
}

// 在画布上按下鼠标
function handleCanvasMouseDown(e: MouseEvent) {
  // 检查是否点击了画布背景
  const target = e.target as HTMLElement
  const isClickingCanvas = target.classList.contains('grid-background')
  // 鼠标左键 && 点击的是画布背景
  if (e.button === 0 && isClickingCanvas) {
    isDraggingCanvas.value = true
    lastMousePosition.value = {
      x: e.clientX,
      y: e.clientY
    }
  }
}

// 鼠标在画布上移动
function handleCanvasMouseMove(e: MouseEvent) {
  const rect = canvasEl.value?.getBoundingClientRect()
  // 拖动添加的节点
  if (isAddingNode.value && tempNode.value) {
    tempNode.value.x = e.clientX - rect.left
    tempNode.value.y = e.clientY - rect.top
  }
  // 拖动画布
  if (isDraggingCanvas.value) {
    const deltaX = e.clientX - lastMousePosition.value.x
    const deltaY = e.clientY - lastMousePosition.value.y
    const currentTransform = new DOMMatrix(getComputedStyle(canvasEl.value!).transform)
    const newTransform = currentTransform.translate(deltaX, deltaY)
    canvasEl.value!.style.transform = newTransform.toString()
    // 更新所有节点的位置以保持连线同步
    const translateX = newTransform.e - currentTransform.e
    const translateY = newTransform.f - currentTransform.f
    workflowNodes.value = workflowNodes.value.map(node => ({
      ...node,
      x: node.x + translateX / zoom.value,
      y: node.y + translateY / zoom.value
    }))
    lastMousePosition.value = {
      x: e.clientX,
      y: e.clientY
    }
  }
}

// 在画布上按下鼠标后松开鼠标
function handleCanvasMouseUp() {
  if (isDraggingCanvas.value) {
    // 拖拽结束时，将 transform 的位移应用到节点位置上
    const transform = new DOMMatrix(getComputedStyle(canvasEl.value!).transform)
    const translateX = transform.e
    const translateY = transform.f
    // 更新节点位置
    workflowNodes.value = workflowNodes.value.map(node => ({
      ...node,
      x: node.x + translateX / zoom.value,
      y: node.y + translateY / zoom.value
    }))
    // 重置画布 transform
    canvasEl.value!.style.transform = `scale(${zoom.value})`
  }
  isDraggingCanvas.value = false
}

// 点击节点时显示详情面板
function handleNodeClick(node: WorkflowNode) {
  selectedNode.value = node
}

// 打开运行面板
function runSelectedNode() {
  if (!selectedNode.value) return
  const nodeId = selectedNode.value.id
  const componentInstance = nodeComponentRefs.get(nodeId)
  if (!componentInstance) {
    console.error(`节点 ${nodeId} 没有渲染组件实例`)
    return
  }
  if (typeof componentInstance.openRunPanel === 'function') {
    componentInstance.openRunPanel()
  } else {
    console.error(`节点 ${nodeId} 没有暴露 openRunPanel()`)
  }
}

// 通过详情面板更新节点数据
function updateNode(updatedNode: WorkflowNode) {
  const index = workflowNodes.value.findIndex(n => n.id === updatedNode.id)
  if (index !== -1) {
    const currentNode = workflowNodes.value[index]
    workflowNodes.value[index] = {
      ...updatedNode,
      x: currentNode.x,
      y: currentNode.y
    }
  }
}

// 关闭详情面板
function closeDetailPanel() {
  selectedNode.value = null
}

// 通过复制、删除更新节点数量
function updateNodes(newNodes: WorkflowNode[]) {
  workflowNodes.value = newNodes;
  if (selectedNode.value && !newNodes.find(n => n.id === selectedNode.value!.id)) {
    selectedNode.value = null
  }
}

// 更新连接
function updateConnections(newConnections: Connection[]) {
  connections.value = newConnections
}

function runTest() {
  // 试运行逻辑
}

function debug() {
  // 调试逻辑
}

// 保存工作流
function saveWorkflow() {
  console.log("workflowNodes: ", workflowNodes.value)
  console.log("connections ", connections.value)
}

function setNodeComponentRef(id: number) {
  return (el: any) => {
    if (el) nodeComponentRefs.set(id, el)
    else nodeComponentRefs.delete(id)
  }
}

// 获取节点详情组件
function getNodeDetailComponent(type: string) {
  switch (type) {
    case 'start':
      return StartNodeDetail
    case 'end':
      return EndNodeDetail
    case 'classifier':
      return ClassifierNodeDetail
    case 'code':
      return CodeNodeDetail
    case 'condition':
      return ConditionNodeDetail
    case 'extract':
      return ExtractNodeDetail
    case 'http':
      return HttpNodeDetail
    case 'knowledge':
      return KnowledgeNodeDetail
    case 'loop':
      return LoopNodeDetail
    case 'model':
      return ModelNodeDetail
    case 'workflow':
      return WorkflowNodeDetail
    case 'current-time':
      return CurrentTimePlugin
    case 'timezone-switch':
      return TimezoneSwitchPlugin
    case 'timestamp':
      return TimestampPlugin
    case 'timestamp-transform':
      return TimestampTransformPlugin
    case 'weekday-calculator':
      return WeekdayCalculatorPlugin
    case 'code-explain':
      return CodeExplainPlugin
    default:
      return null
  }
}

const clearWorkflowCacheAndGoBack = () => {
  // 清除 localStorage 缓存
  localStorage.removeItem('workflowNodes')
  localStorage.removeItem('connections')
  // 返回上一页
  router.go(-1)
}
</script>

<template>
  <div class="workflow-container">
    <!-- 上侧导航栏 -->
    <div class="top-navbar">
      <button class="back-btn" @click="clearWorkflowCacheAndGoBack">
        <i class="fas fa-arrow-left"></i>
        返回
      </button>
      <div class="workflow-info">
        <img src="https://picsum.photos/40/40?random=11" alt="Workflow" class="workflow-image">
        <div class="workflow-details">
          <h3 class="workflow-name">工作流名称</h3>
          <p class="workflow-description">这是工作流的描述信息。</p>
        </div>
      </div>
      <button class="publish-btn">
        发布
      </button>
    </div>

    <!-- 中间画布区域 -->
    <div class="canvas-area"
         ref="canvasEl"
         @mousedown="handleCanvasMouseDown"
         @mousemove="handleCanvasMouseMove"
         @mouseup="handleCanvasMouseUp"
         @mouseleave="handleCanvasMouseUp"
         :style="{ transform: `scale(${zoom})`, cursor: isDraggingCanvas ? 'grabbing' : 'default' }">
      <div class="grid-background"></div>

      <WorkflowNodeManager
          :nodes="workflowNodes"
          :selectedNode="selectedNode"
          :connections="connections"
          :nodeTypes="nodeTypes"
          :zoom="zoom"
          @update:nodes="updateNodes"
          @update:connections="updateConnections"
          @node-click="handleNodeClick"
          @run-node="runSelectedNode"
      />

      <!-- 临时节点 -->
      <div
        v-if="isAddingNode && tempNode"
        class="workflow-node"
        :style="{
          left: `${tempNode.x}px`,
          top: `${tempNode.y}px`,
          opacity: 0.8,
          position: 'absolute'
        }"
        @click="handleTempNodeClick"
      >
        <div class="node-content">
          <div class="node-icon">
            <img :src="tempNode.image" :alt="tempNode.label">
          </div>
          <div class="node-title">{{ tempNode.label }}</div>
        </div>
      </div>
    </div>

    <!-- 底部工具栏 -->
    <div class="floating-toolbar">
      <button class="tool-btn primary" @click="showNodeSelector = true">
        <img src="https://api.iconify.design/material-symbols:add-box.svg" alt="添加" class="tool-btn-icon">
        添加节点
      </button>
      <button class="tool-btn secondary" @click="saveWorkflow">
        <img src="https://api.iconify.design/material-symbols:save.svg" alt="保存" class="tool-btn-icon">
        保存工作流
      </button>
      <button class="tool-btn secondary" @click="debug">
        <img src="https://api.iconify.design/material-symbols:bug-report.svg" alt="调试" class="tool-btn-icon">
        调试
      </button>
      <button class="tool-btn accent" @click="runTest">
        <img src="https://api.iconify.design/material-symbols:play-circle.svg" alt="运行" class="tool-btn-icon">
        试运行
      </button>
    </div>

    <!-- 节点选择弹窗 -->
    <div class="node-selector-modal" v-if="showNodeSelector" @click.self="showNodeSelector = false">
      <div class="node-selector-content">
        <div class="node-selector-header">
          <h3>{{ selectorPage === 'nodes' ? '选择节点类型' : '选择插件' }}</h3>
          <div class="selector-tabs">
            <button 
              :class="['tab-btn', { active: selectorPage === 'nodes' }]"
              @click="selectorPage = 'nodes'"
            >
              节点类型
            </button>
            <button 
              :class="['tab-btn', { active: selectorPage === 'plugins' }]"
              @click="selectorPage = 'plugins'"
            >
              插件
            </button>
          </div>
        </div>
        
        <!-- 节点类型网格 -->
        <div v-if="selectorPage === 'nodes'" class="node-types-grid">
          <div v-for="node in filteredNodeTypes" :key="node.type"
               class="node-type-item"
               @click="addNode(node.type, $event.x, $event.y)">
            <div class="node-icon">
              <img :src="node.image" :alt="node.label">
            </div>
            <div class="node-info">
              <span class="node-label">{{ node.label }}</span>
              <span class="node-desc">{{ node.description }}</span>
            </div>
          </div>
        </div>
        
        <!-- 插件类型网格 -->
        <div v-if="selectorPage === 'plugins'" class="node-types-grid">
          <div v-for="node in pluginNodeTypes" :key="node.type"
               class="node-type-item"
               @click="addNode(node.type, $event.x, $event.y)">
            <div class="node-icon">
              <img :src="node.image" :alt="node.label">
            </div>
            <div class="node-info">
              <span class="node-label">{{ node.label }}</span>
              <span class="node-desc">{{ node.description }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 节点详情面板 -->
    <div v-if="selectedNode" class="node-detail-panel">
      <div class="node-detail-header">
        <h3>{{ selectedNode.label }}</h3>
        <div class="header-actions">
          <button 
            class="action-btn run-btn" 
            @click="runSelectedNode"
            v-if="selectedNode.type !== 'start' && selectedNode.type !== 'end'"
            title="运行节点">
            <img 
              src="https://api.iconify.design/material-symbols:play-circle.svg"
              alt="运行" 
              class="action-icon">
          </button>
          <button @click="closeDetailPanel" class="action-btn close-btn" title="关闭">×</button>
        </div>
      </div>
      
      <div class="node-detail-content">
        <!-- 添加名称和描述编辑区域 -->
        <div class="edit-section">
          <div class="edit-item">
            <label>节点名称</label>
            <input 
              type="text" 
              v-model="selectedNode.name"
              @input="updateNode(selectedNode)"
              placeholder="请输入节点名称"
              class="edit-input"
            >
          </div>
          <div class="edit-item">
            <label>节点描述</label>
            <textarea 
              v-model="selectedNode.description"
              @input="updateNode(selectedNode)"
              placeholder="请输入节点描述"
              class="edit-textarea"
              rows="3"
            ></textarea>
          </div>
        </div>
        
        <component
          :is="getNodeDetailComponent(selectedNode.type)"
          :node="selectedNode"
          :allNodes="workflowNodes"
          :key="selectedNode?.id"
          :ref="setNodeComponentRef(selectedNode.id)"
          @update:node="updateNode"
        />
      </div>
    </div>
  </div>
</template>

<style scoped>
.workflow-container {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background: #f8f9fa;
  margin: 0;
  padding: 0;
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
}

.top-navbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: white;
  padding: 10px 20px;
  border-bottom: 1px solid #eee;
  position: relative;
  z-index: 1001;
  margin: 0;
}

.back-btn, .publish-btn {
  background: #2c3e50;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: background-color 0.3s;
}

.back-btn:hover, .publish-btn:hover {
  background: #34495e;
}

.workflow-info {
  display: flex;
  align-items: center;
  gap: 10px;
}

.workflow-image {
  width: 40px;
  height: 40px;
  border-radius: 50%;
}

.workflow-details {
  display: flex;
  flex-direction: column;
}

.workflow-name {
  margin: 0;
  font-size: 18px;
  color: #2c3e50;
}

.workflow-description {
  margin: 0;
  font-size: 14px;
  color: #666;
}

.canvas-area {
  flex: 1;
  position: relative;
  background: white;
  transform-origin: top left;
  user-select: none;
  touch-action: none;
  will-change: transform;
  z-index: 1;
}

.canvas-area[data-dragging="true"]::after {
  content: "释放以添加节点";
  position: fixed;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  padding: 8px 16px;
  background: rgba(0, 0, 0, 0.7);
  color: white;
  border-radius: 4px;
  pointer-events: none;
}

.grid-background {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-image: linear-gradient(#eee 1px, transparent 1px),
                    linear-gradient(90deg, #eee 1px, transparent 1px);
  background-size: 20px 20px;
  opacity: 0.5;
  z-index: 0;
}

.floating-toolbar {
  position: fixed;
  bottom: 30px;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  gap: 16px;
  padding: 12px 20px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  z-index: 100;
}

.tool-btn {
  padding: 10px 20px;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.3s ease;
  color: white;
}

.tool-btn i {
  font-size: 16px;
}

.tool-btn.primary {
  background: #2c3e50;
}

.tool-btn.secondary {
  background: #34495e;
}

.tool-btn.accent {
  background: #3498db;
}

.tool-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  opacity: 0.9;
}

.node-selector-modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.node-selector-content {
  background: white;
  border-radius: 12px;
  padding: 24px;
  width: 80%;
  max-width: 900px;
  max-height: 80vh;
  overflow-y: auto;
}

.node-selector-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 1px solid #eee;
}

.node-selector-header h3 {
  margin: 0;
  font-size: 20px;
  color: #2c3e50;
  font-weight: 600;
}

.close-btn {
  background: none;
  border: none;
  font-size: 20px;
  cursor: pointer;
  color: #666;
  padding: 4px;
  transition: color 0.3s;
}

.close-btn:hover {
  color: #2c3e50;
}

.node-types-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 16px;
  padding: 16px;
}

.node-type-item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 16px;
  background: #f8f9fa;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  border: 1px solid #eee;
}

.node-type-item[draggable="true"] {
  cursor: grab;
  &:active {
    cursor: grabbing;
  }
}

.node-type-item:hover {
  background: #fff;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  border-color: #2c3e50;
}

.node-icon {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #fff;
  border-radius: 8px;
  padding: 8px;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.06);
}

.node-icon img {
  width: 24px;
  height: 24px;
}

.node-icon i {
  font-size: 20px;
  color: #2c3e50;
}

.node-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.node-label {
  font-size: 14px;
  font-weight: 600;
  color: #2c3e50;
}

.node-desc {
  font-size: 12px;
  color: #666;
  line-height: 1.4;
}

.tool-btn-icon {
  width: 20px;
  height: 20px;
  filter: brightness(0) invert(1);
}

.node-detail-panel {
  position: fixed;
  top: 0;
  right: 0;
  width: 550px;
  height: 100vh;
  background: white;
  box-shadow: -2px 0 8px rgba(0, 0, 0, 0.1);
  z-index: 1002;
  display: flex;
  flex-direction: column;
}

.node-detail-header {
  padding: 16px;
  border-bottom: 1px solid #eee;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.action-btn {
  background: none;
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 4px;
  opacity: 0.7;
  transition: all 0.2s;
}

.action-btn:hover {
  opacity: 1;
  transform: scale(1.1);
}

.action-btn.run-btn {
  color: #3498db;
}

.action-icon {
  width: 24px;
  height: 24px;
}

.close-btn {
  font-size: 20px;
  color: #666;
}

.close-btn:hover {
  color: #ff6b6b;
}

.node-detail-content {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
}

.node-detail-header h3 {
  margin: 0;
  font-size: 16px;
  color: #2c3e50;
}

.workflow-node {
  position: relative;
  z-index: 1;
  transition: opacity 0.2s;
  cursor: pointer;
}

.workflow-node:hover {
  opacity: 1 !important;
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

.spinning {
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

.selector-tabs {
  display: flex;
  gap: 12px;
}

.tab-btn {
  background: none;
  border: none;
  padding: 8px 16px;
  font-size: 14px;
  color: #666;
  cursor: pointer;
  border-radius: 4px;
  transition: all 0.3s ease;
}

.tab-btn:hover {
  background: #f5f5f5;
}

.tab-btn.active {
  background: #e3f2fd;
  color: #1976d2;
}

.edit-section {
  margin-bottom: 16px;
  padding: 16px;
  background: #f8f9fa;
  border-radius: 8px;
}

.edit-item {
  margin-bottom: 12px;
}

.edit-item:last-child {
  margin-bottom: 0;
}

.edit-item label {
  display: block;
  font-size: 14px;
  color: #666;
  margin-bottom: 8px;
}

.edit-input, .edit-textarea {
  width: 100%;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  color: #2c3e50;
  background: white;
}

.edit-input:focus, .edit-textarea:focus {
  outline: none;
  border-color: #3498db;
}

.edit-textarea {
  resize: vertical;
  min-height: 60px;
}
</style> 