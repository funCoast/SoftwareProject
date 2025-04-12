<template>
  <div class="workflow-container">
    <!-- 上侧导航栏 -->
    <div class="top-navbar">
      <button class="back-btn" @click="$router.go(-1)">
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
         @scroll.passive="updateCanvasPosition($event.target as HTMLElement)"
         @dragover.prevent="handleDragOver"
         @drop="handleDrop"
         @mousemove="handleCanvasMouseMove"
         @mousedown="handleCanvasMouseDown"
         @mouseup="handleCanvasMouseUp"
         @mouseleave="handleCanvasMouseUp"
         @click="handleCanvasClick"
         :style="{ transform: `scale(${zoom})`, cursor: isDraggingCanvas ? 'grabbing' : 'default' }">
      <div class="grid-background"></div>

      <WorkflowNodeManager
          :nodes="workflowNodes"
          :connections="connections"
          :nodeTypes="nodeTypes"
          :zoom="zoom"
          @update:nodes="updateNodes"
          @update:connections="updateConnections"
          @node-click="handleNodeClick"
          @node-drag-start="handleNodeDragStart"
          @node-drag-end="handleNodeDragEnd"
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
            <img v-if="getNodeImage(tempNode.type)" :src="getNodeImage(tempNode.type)" :alt="tempNode.label">
            <i v-else :class="nodeTypes.find(nt => nt.type === tempNode.type)?.icon"></i>
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
          <h3>选择节点类型</h3>
          <button class="close-btn" @click="showNodeSelector = false">
            <i class="fas fa-times"></i>
          </button>
        </div>
        <div class="node-types-grid">
          <div v-for="node in nodeTypes" :key="node.type" 
               class="node-type-item"
               @click="addNode(node.type)">
            <div class="node-icon">
              <img v-if="node.image" :src="node.image" :alt="node.label">
              <i v-else :class="node.icon"></i>
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
        <h3>{{ selectedNode.label || '节点详情' }}</h3>
        <button @click="closeDetailPanel" class="close-btn">×</button>
      </div>
      
      <div class="node-detail-content">
        <component
          :is="getNodeDetailComponent(selectedNode.type)"
          :node="selectedNode"
          @update:node="updateNode"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import ClassifierNodeDetail from './node-details/ClassifierNodeDetail.vue'
import CodeNodeDetail from "./node-details/CodeNodeDetail.vue"
import ConditionNodeDetail from "./node-details/ConditionNodeDetail.vue"
import ExtractNodeDetail from './node-details/ExtractNodeDetail.vue'
import HttpNodeDetail from "./node-details/HttpNodeDetail.vue"
import KnowledgeNodeDetail from "./node-details/KnowledgeNodeDetail.vue"
import LoopNodeDetail from "./node-details/LoopNodeDetail.vue"
import ModelNodeDetail from './node-details/ModelNodeDetail.vue'
import PluginNodeDetail from './node-details/PluginNodeDetail.vue'
import WorkflowNodeDetail from './node-details/WorkflowNodeDetail.vue'

const lastCanvasMousePos = ref({ x: 0, y: 0 })
const canvasEl = ref<HTMLElement>()
const canvasPosition = ref({ scrollLeft: 0, scrollTop: 0 })
const canvasRect = ref<DOMRect>()
const draggingNodeType = ref<string>()

const zoom = ref(1)
const showNodeSelector = ref(false)
const nodes = ref([
  { id: 1, name: '开始', icon: 'fas fa-play' },
  { id: 2, name: '结束', icon: 'fas fa-stop' },
  { id: 3, name: '大模型', icon: 'fas fa-brain' },
  { id: 4, name: '插件', icon: 'fas fa-puzzle-piece' },
  { id: 5, name: '工作流', icon: 'fas fa-project-diagram' },
  { id: 6, name: 'HTTP请求', icon: 'fas fa-network-wired' },
  { id: 7, name: '代码', icon: 'fas fa-code' },
  { id: 8, name: '条件分支', icon: 'fas fa-code-branch' },
  { id: 9, name: '循环', icon: 'fas fa-redo' },
  { id: 10, name: '意图识别', icon: 'fas fa-bullseye' },
  { id: 11, name: '知识库检索', icon: 'fas fa-book' }
])

interface nodeType {
  type: string
  label: string
  icon: string
  description: string
  image: string
}
const nodeTypes = ref<nodeType[]>([
  { 
    type: 'model',
    label: '大模型',
    icon: 'fas fa-brain',
    description: '使用AI大模型处理任务',
    image: 'https://api.iconify.design/carbon:machine-learning-model.svg',
    draggable: true
  },
  { 
    type: 'plugin',
    label: '插件',
    icon: 'fas fa-puzzle-piece',
    description: '使用自定义插件扩展功能',
    image: 'https://api.iconify.design/material-symbols:extension.svg',
    draggable: true
  },
  { 
    type: 'workflow',
    label: '工作流',
    icon: 'fas fa-project-diagram',
    description: '嵌套调用其他工作流',
    image: 'https://api.iconify.design/material-symbols:account-tree.svg',
    draggable: true,
  },
  { 
    type: 'http',
    label: 'HTTP请求',
    icon: 'fas fa-globe',
    description: '发送HTTP请求获取数据',
    image: 'https://api.iconify.design/material-symbols:api.svg',
    draggable: true
  },
  { 
    type: 'code',
    label: '代码',
    icon: 'fas fa-code',
    description: '执行自定义代码逻辑',
    image: 'https://api.iconify.design/material-symbols:code.svg',
    draggable: true
  },
  { 
    type: 'condition',
    label: '条件分支',
    icon: 'fas fa-code-branch',
    description: '根据条件选择执行路径',
    image: 'https://api.iconify.design/material-symbols:fork-right.svg',
    draggable: true
  },
  { 
    type: 'loop',
    label: '循环',
    icon: 'fas fa-redo',
    description: '重复执行特定任务',
    image: 'https://api.iconify.design/material-symbols:repeat.svg',
    draggable: true
  },
  { 
    type: 'classifier',
    label: '问题分类器',
    icon: 'fas fa-tags',
    description: '对输入内容进行分类',
    image: 'https://api.iconify.design/material-symbols:category.svg',
    draggable: true
  },
  { 
    type: 'knowledge',
    label: '知识库检索',
    icon: 'fas fa-database',
    description: '从知识库中检索信息',
    image: 'https://api.iconify.design/material-symbols:database.svg',
    draggable: true
  },
  { 
    type: 'extract',
    label: '提取文档',
    icon: 'fas fa-file-alt',
    description: '从文档中提取关键信息',
    image: 'https://api.iconify.design/material-symbols:description.svg',
    draggable: true
  }
])

interface WorkflowNode {
  id: number
  type: string
  label: string
  x: number
  y: number
  data?: any
}

interface Connection {
  id: number
  sourceId: number
  targetId: number
  sourceType: 'left' | 'right'
  targetType: 'left' | 'right'
}

const workflowNodes = ref<WorkflowNode[]>([])
const connections = ref<Connection[]>([])
const nextNodeId = ref(1)
const nextConnectionId = ref(1)

// 选中的节点
const selectedNode = ref<any>(null)

const isAddingNode = ref(false)
const tempNode = ref<WorkflowNode | null>(null)

const isDraggingCanvas = ref(false)
const isDraggingNode = ref(false)
const lastMousePosition = ref({ x: 0, y: 0 })
const dragStartTimeout = ref<number | null>(null)
const LONG_PRESS_DURATION = 200 // 长按触发时间（毫秒）

function handleDrop(e: DragEvent) {
  if (!draggingNodeType.value || !canvasRect.value) return

  const scale = zoom.value
  const rect = canvasRect.value

  // 计算精确位置
  const x = (e.clientX - rect.left + canvasPosition.value.scrollLeft) / scale
  const y = (e.clientY - rect.top + canvasPosition.value.scrollTop) / scale

  addNode(draggingNodeType.value, x, y)
  draggingNodeType.value = undefined
}

function updateCanvasPosition(el: HTMLElement) {
  canvasRect.value = el.getBoundingClientRect()
  canvasPosition.value = {
    scrollLeft: el.scrollLeft,
    scrollTop: el.scrollTop
  }
}

// 处理拖拽添加
function handleDragOver(e: DragEvent) {
  updateCanvasPosition(e.currentTarget as HTMLElement)
}

function getNodeImage(type: string): string {
  const nodeType = nodeTypes.value.find(nt => nt.type === type)
  return nodeType?.image || ''
}

function addNode(type: string, x?: number, y?:number) {
  const nodeType = nodeTypes.value.find(nt => nt.type === type)
  if (!nodeType) return

  const initX = x !== undefined ? x : lastCanvasMousePos.value.x
  const initY = y !== undefined ? y : lastCanvasMousePos.value.y

  isAddingNode.value = true
  tempNode.value = {
    id: nextNodeId.value++,
    type: type,
    label: nodeType.label,
    x: initX,
    y: initY
  }
  showNodeSelector.value = false
}

// 更新节点
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

// 获取节点详情组件
function getNodeDetailComponent(type: string) {
  switch (type) {
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
    case 'plugin':
      return PluginNodeDetail
    case 'workflow':
      return WorkflowNodeDetail
    default:
      return null
  }
}

// 点击节点时显示详情面板
function handleNodeClick(node: any) {
  selectedNode.value = node
}

// 关闭详情面板
function closeDetailPanel() {
  selectedNode.value = null
}

// 更新节点数据
function updateNode(updatedNode: any) {
  const index = nodes.value.findIndex(n => n.id === updatedNode.id)
  if (index !== -1) {
    nodes.value[index] = updatedNode
  }
}

const handleCanvasMouseDown = (e: MouseEvent) => {
  // 检查是否点击了画布背景
  const target = e.target as HTMLElement
  const isClickingCanvas = target.classList.contains('grid-background')
  
  if (e.button === 0 && !isDraggingNode.value && isClickingCanvas) {
    isDraggingCanvas.value = true
    lastMousePosition.value = {
      x: e.clientX,
      y: e.clientY
    }
  }
}

const handleCanvasMouseMove = (e: MouseEvent) => {
  const rect = canvasEl.value?.getBoundingClientRect()
  if (!rect) return

  // 统一计算鼠标在画布逻辑坐标中的位置（非像素）
  const posX = (e.clientX - rect.left)
  const posY = (e.clientY - rect.top)

  // 无论是否在添加节点，都记录最后的逻辑坐标（供点击添加使用）
  lastCanvasMousePos.value = { x: posX, y: posY }

  // 添加节点时更新预览位置
  if (isAddingNode.value && tempNode.value) {
    tempNode.value.x = posX
    tempNode.value.y = posY
  }

  // 拖动画布逻辑不变
  if (isDraggingCanvas.value && !isDraggingNode.value) {
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

const handleCanvasMouseUp = () => {
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

const handleCanvasClick = (e: MouseEvent) => {
  if (isAddingNode.value && tempNode.value) {
    // 确保拿到最新的 rect
    const rect = canvasEl.value!.getBoundingClientRect()  // :contentReference[oaicite:1]{index=1}

    // 先加上 scroll，再除以缩放
    const x = (e.clientX - rect.left + canvasPosition.value.scrollLeft) / zoom.value
    const y = (e.clientY - rect.top  + canvasPosition.value.scrollTop ) / zoom.value

    const newNode = { ...tempNode.value, x, y }
    workflowNodes.value.push(newNode)

    isAddingNode.value = false
    tempNode.value = null
  }
}

const handleTempNodeClick = (e: MouseEvent) => {
  e.stopPropagation()
  if (tempNode.value) {
    const newNode = { ...tempNode.value }
    workflowNodes.value.push(newNode)
    isAddingNode.value = false
    tempNode.value = null
  }
}

const handleNodeDragStart = () => {
  isDraggingNode.value = true
  if (dragStartTimeout.value) {
    clearTimeout(dragStartTimeout.value)
    dragStartTimeout.value = null
  }
}

const handleNodeDragEnd = () => {
  isDraggingNode.value = false
}

// 初始化画布位置
onMounted(() => {
  updateCanvasPosition(canvasEl.value!)
})
</script>

<style scoped>
.workflow-container {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background: #f8f9fa;
}

.top-navbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: white;
  padding: 10px 20px;
  border-bottom: 1px solid #eee;
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
  overflow: auto;
  background: white;
  transform-origin: top left;
  user-select: none;
  touch-action: none;
  will-change: transform;
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
  width: 300px;
  height: 100vh;
  background: white;
  box-shadow: -2px 0 8px rgba(0, 0, 0, 0.1);
  z-index: 1000;
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

.close-btn {
  background: none;
  border: none;
  font-size: 20px;
  cursor: pointer;
  color: #666;
}

.close-btn:hover {
  color: #ff6b6b;
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
</style> 