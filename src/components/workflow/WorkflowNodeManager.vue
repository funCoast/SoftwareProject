<template>
  <div>
    <!-- 节点容器 -->
    <div class="nodes-container">
      <div v-for="node in nodes" 
           :key="node.id" 
           class="workflow-node"
           :class="{ selected: node.id === selectedNodeId }"
           :data-node-id="node.id"
           :style="{
             left: node.x + 'px',
             top: node.y + 'px',
             transform: `scale(${1/zoom})`  // 反向缩放保持节点实际大小
           }"
           @click="handleNodeClick(node)"
           @mousedown="startDrag(node, $event)"
           @contextmenu.prevent="showContextMenu(node, $event)">
        <!-- 左侧连接点 -->
        <div class="connector left" 
             @mousedown.stop="startConnection(node, 'left', $event)"
             @mouseenter="showConnectorTooltip(node, 'left')"
             @mouseleave="hideConnectorTooltip">
          <div class="connector-plus">+</div>
        </div>
        
        <div class="node-content">
          <div class="node-header">
            <img :src="getNodeImage(node.type)" :alt="node.label" class="node-type-icon">
            <span class="node-title">{{ node.label }}</span>
          </div>
        </div>

        <!-- 右侧连接点 -->
        <div class="connector right" 
             @mousedown.stop="startConnection(node, 'right', $event)"
             @mouseenter="showConnectorTooltip(node, 'right')"
             @mouseleave="hideConnectorTooltip">
          <div class="connector-plus">+</div>
        </div>
      </div>
    </div>

    <!-- 连线 -->
    <svg class="connections-layer">
      <g v-for="connection in connections" 
         :key="`${connection.id}-${connectionUpdateTrigger}`"
         class="connection-group"
         @contextmenu.prevent="showConnectionContextMenu(connection, $event)">
        <path :d="getConnectionPath(connection)"
              :stroke-width="2/zoom"
              class="connection-path"/>
      </g>
      <!-- 正在创建的连线 -->
      <path v-if="activeConnection.sourceNode"
            :d="getActiveConnectionPath()"
            class="connection-path active"/>
    </svg>

    <!-- 连接提示 -->
    <div v-if="showConnectorHint" 
         class="connector-hint"
         :style="connectorHintStyle">
      <i class="fas fa-link"></i>
      <span>连接到此</span>
    </div>

    <!-- 右键菜单 -->
    <div v-if="contextMenu.show" 
         class="context-menu"
         :style="{ left: contextMenu.x + 'px', top: contextMenu.y + 'px' }">
      <div class="context-menu-item" @click="copyNode">
        <i class="fas fa-copy"></i>
        <span>复制节点</span>
      </div>
      <div class="context-menu-item" @click="deleteNode">
        <i class="fas fa-trash"></i>
        <span>删除节点</span>
      </div>
    </div>

    <!-- 连线右键菜单 -->
    <div v-if="connectionContextMenu.show" 
         class="context-menu"
         :style="{ left: connectionContextMenu.x + 'px', top: connectionContextMenu.y + 'px' }">
      <div class="context-menu-item" @click="deleteConnection">
        <i class="fas fa-trash"></i>
        <span>删除连线</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, defineProps, defineEmits } from 'vue'
const NODE_WIDTH = 200
const NODE_HEIGHT = 120
const NODE_PADDING = 12
const CONNECTOR_OFFSET = 8

const props = defineProps<{
  nodes: any[],
  connections: any[],
  nodeTypes: any[],
  zoom: number
}>()

const emit = defineEmits<{
  (e: 'update:nodes', nodes: any[]): void
  (e: 'update:connections', connections: any[]): void
  (e: 'node-click', node: any): void
}>()

// 拖拽相关
const draggedNode = ref<any>(null)
const dragOffset = ref({ x: 0, y: 0 })

// 连接相关
const activeConnection = ref<{
  sourceNode: any | null,
  sourceType: 'left' | 'right' | null,
  startX: number,
  startY: number
}>({
  sourceNode: null,
  sourceType: null,
  startX: 0,
  startY: 0
})

const showConnectorHint = ref(false)
const connectorHintStyle = ref({
  left: '0px',
  top: '0px'
})

// 右键菜单状态
const contextMenu = ref({
  show: false,
  x: 0,
  y: 0,
  node: null as any
})

// 连线右键菜单状态
const connectionContextMenu = ref({
  show: false,
  x: 0,
  y: 0,
  connection: null as any
})

// 添加一个计数器来触发连线重绘
const connectionUpdateTrigger = ref(0)

// 获取节点图标
function getNodeImage(type: string): string {
  const nodeType = props.nodeTypes.find(nt => nt.type === type)
  return nodeType?.image || ''
}

// 拖拽相关函数
function startDrag(node: any, event: MouseEvent) {
  draggedNode.value = node
  const rect = (event.target as HTMLElement).getBoundingClientRect()
  dragOffset.value = {
    x: event.clientX - rect.left,
    y: event.clientY - rect.top
  }
  
  document.addEventListener('mousemove', handleDrag)
  document.addEventListener('mouseup', stopDrag)
}

function handleDrag(event: MouseEvent) {
  if (!draggedNode.value) return
  
  const canvas = document.querySelector('.canvas-area')
  if (!canvas) return
  
  const rect = canvas.getBoundingClientRect()
  const x = (event.clientX - rect.left - dragOffset.value.x) / props.zoom
  const y = (event.clientY - rect.top - dragOffset.value.y) / props.zoom
  
  draggedNode.value.x = Math.max(0, x)
  draggedNode.value.y = Math.max(0, y)
  
  // 更新节点位置
  const updatedNodes = [...props.nodes]
  const nodeIndex = updatedNodes.findIndex(n => n.id === draggedNode.value.id)
  if (nodeIndex !== -1) {
    updatedNodes[nodeIndex] = { ...draggedNode.value }
    emit('update:nodes', updatedNodes)
    // 触发连线更新
    connectionUpdateTrigger.value++
  }
}

function stopDrag() {
  draggedNode.value = null
  document.removeEventListener('mousemove', handleDrag)
  document.removeEventListener('mouseup', stopDrag)
}

function startConnection(node: any, type: 'left' | 'right', event: MouseEvent) {
  const rect = (event.target as HTMLElement).getBoundingClientRect()
  activeConnection.value = {
    sourceNode: node,
    sourceType: type,
    startX: rect.left + rect.width / 2,
    startY: rect.top + rect.height / 2
  }
  
  window.addEventListener('mousemove', handleConnectionDrag)
  window.addEventListener('mouseup', stopConnection)
}

function handleConnectionDrag(event: MouseEvent) {
  if (!activeConnection.value.sourceNode) return
  
  const targetConnector = findTargetConnector(event)
  if (targetConnector) {
    showConnectorHint.value = true
    connectorHintStyle.value = {
      left: `${targetConnector.x}px`,
      top: `${targetConnector.y}px`
    }
  } else {
    showConnectorHint.value = false
  }
}

function stopConnection(event: MouseEvent) {
  if (!activeConnection.value.sourceNode) return
  
  const targetConnector = findTargetConnector(event)
  if (targetConnector && targetConnector.node.id !== activeConnection.value.sourceNode.id) {
    const newConnection = {
      id: Date.now(),
      sourceId: activeConnection.value.sourceNode.id,
      targetId: targetConnector.node.id,
      sourceType: activeConnection.value.sourceType,
      targetType: targetConnector.type
    }
    
    emit('update:connections', [...props.connections, newConnection])
  }
  
  activeConnection.value = {
    sourceNode: null,
    sourceType: null,
    startX: 0,
    startY: 0
  }
  
  showConnectorHint.value = false
  window.removeEventListener('mousemove', handleConnectionDrag)
  window.removeEventListener('mouseup', stopConnection)
}

function findTargetConnector(event: MouseEvent) {
  const canvas = document.querySelector('.canvas-area')
  if (!canvas) return null
  const canvasRect = canvas.getBoundingClientRect()

  // 计算鼠标在画布中的逻辑坐标（考虑缩放）
  const mouseX = (event.clientX - canvasRect.left) / props.zoom
  const mouseY = (event.clientY - canvasRect.top) / props.zoom

  // 遍历所有连接点
  const connectors = document.querySelectorAll('.connector')
  for (const connector of connectors) {
    const connectorRect = connector.getBoundingClientRect()

    // 转换为画布逻辑坐标
    const connectorX = (connectorRect.left - canvasRect.left + connectorRect.width/2) / props.zoom
    const connectorY = (connectorRect.top - canvasRect.top + connectorRect.height/2) / props.zoom

    // 精确碰撞检测（5px容差）
    if (Math.abs(mouseX - connectorX) < 5 && Math.abs(mouseY - connectorY) < 5) {
      const nodeElement = connector.closest('.workflow-node')
      if (!nodeElement) continue

      const nodeId = parseInt(nodeElement.getAttribute('data-node-id') || '0')
      const node = props.nodes.find(n => n.id === nodeId)
      if (!node) continue

      return {
        node,
        type: connector.classList.contains('left') ? 'left' : 'right',
        x: connectorX * props.zoom + canvasRect.left,
        y: connectorY * props.zoom + canvasRect.top
      }
    }
  }
  return null
}

function getConnectionPath(connection: any): string {
  // 使用connectionUpdateTrigger触发重新计算
  connectionUpdateTrigger.value
  
  const source = props.nodes.find(n => n.id === connection.sourceId)
  const target = props.nodes.find(n => n.id === connection.targetId)
  if (!source || !target) return ''

  // 获取画布和节点DOM元素
  const canvas = document.querySelector('.canvas-area')
  if (!canvas) return ''
  const canvasRect = canvas.getBoundingClientRect()

  // 动态获取源节点连接点位置
  const sourceNodeEl = document.querySelector(`[data-node-id="${source.id}"]`)
  const sourceConnectorEl = connection.sourceType === 'right'
      ? sourceNodeEl?.querySelector('.connector.right')
      : sourceNodeEl?.querySelector('.connector.left')
  if (!sourceConnectorEl) return ''

  // 计算相对于画布的坐标（考虑缩放）
  const sourceConnectorRect = sourceConnectorEl.getBoundingClientRect()
  const sourceX = (sourceConnectorRect.left - canvasRect.left + sourceConnectorRect.width/2) / props.zoom
  const sourceY = (sourceConnectorRect.top - canvasRect.top + sourceConnectorRect.height/2) / props.zoom

  // 动态获取目标节点连接点位置
  const targetNodeEl = document.querySelector(`[data-node-id="${target.id}"]`)
  const targetConnectorEl = connection.targetType === 'right'
      ? targetNodeEl?.querySelector('.connector.right')
      : targetNodeEl?.querySelector('.connector.left')
  if (!targetConnectorEl) return ''

  const targetConnectorRect = targetConnectorEl.getBoundingClientRect()
  const targetX = (targetConnectorRect.left - canvasRect.left + targetConnectorRect.width/2) / props.zoom
  const targetY = (targetConnectorRect.top - canvasRect.top + targetConnectorRect.height/2) / props.zoom

  // 计算贝塞尔曲线控制点
  const dx = targetX - sourceX
  const controlOffset = Math.min(Math.abs(dx) * 0.5, 150) * (dx > 0 ? 1 : -1)

  return `M ${sourceX} ${sourceY}
          C ${sourceX + controlOffset} ${sourceY},
            ${targetX - controlOffset} ${targetY},
            ${targetX} ${targetY}`
}

function getActiveConnectionPath(): string {
  if (!activeConnection.value.sourceNode) return ''

  // 获取源连接点实际位置
  const sourceNodeEl = document.querySelector(`[data-node-id="${activeConnection.value.sourceNode.id}"]`)
  const sourceConnectorEl = activeConnection.value.sourceType === 'right'
      ? sourceNodeEl?.querySelector('.connector.right')
      : sourceNodeEl?.querySelector('.connector.left')
  if (!sourceConnectorEl) return ''

  const canvas = document.querySelector('.canvas-area')
  if (!canvas) return ''
  const canvasRect = canvas.getBoundingClientRect()
  const sourceConnectorRect = sourceConnectorEl.getBoundingClientRect()

  // 源点坐标
  const sourceX = (sourceConnectorRect.left - canvasRect.left + sourceConnectorRect.width/2) / props.zoom
  const sourceY = (sourceConnectorRect.top - canvasRect.top + sourceConnectorRect.height/2) / props.zoom

  // 当前鼠标位置
  const mouseEvent = window.event as MouseEvent
  if (!mouseEvent) return ''
  const mouseX = (mouseEvent.clientX - canvasRect.left) / props.zoom
  const mouseY = (mouseEvent.clientY - canvasRect.top) / props.zoom

  // 动态计算控制点
  const dx = mouseX - sourceX
  const controlOffset = Math.min(Math.abs(dx) * 0.5, 150) * (dx > 0 ? 1 : -1)

  return `M ${sourceX} ${sourceY}
          C ${sourceX + controlOffset} ${sourceY},
            ${mouseX} ${mouseY},
            ${mouseX} ${mouseY}`
}

function showConnectorTooltip(node: any, type: 'left' | 'right') {
  // 可以在这里添加连接点提示
}

function hideConnectorTooltip() {
  // 隐藏连接点提示
}

// 右键菜单相关函数
function showContextMenu(node: any, event: MouseEvent) {
  event.preventDefault()
  contextMenu.value = {
    show: true,
    x: event.clientX,
    y: event.clientY,
    node: node
  }
  
  // 点击其他地方关闭菜单
  document.addEventListener('click', hideContextMenu)
}

function hideContextMenu() {
  contextMenu.value.show = false
  document.removeEventListener('click', hideContextMenu)
}

// 复制节点
function copyNode() {
  if (!contextMenu.value.node) return
  
  const originalNode = contextMenu.value.node
  const newNode = {
    id: Date.now(), // 使用时间戳作为临时ID
    type: originalNode.type,
    label: originalNode.label,
    x: originalNode.x + 20, // 稍微偏移一点，避免完全重叠
    y: originalNode.y + 20
  }
  
  const updatedNodes = [...props.nodes, newNode]
  emit('update:nodes', updatedNodes)
  hideContextMenu()
}

// 删除节点
function deleteNode() {
  if (!contextMenu.value.node) return
  
  const nodeId = contextMenu.value.node.id
  
  // 删除节点
  const updatedNodes = props.nodes.filter(n => n.id !== nodeId)
  emit('update:nodes', updatedNodes)
  
  // 删除与该节点相关的所有连接
  const updatedConnections = props.connections.filter(conn => 
    conn.sourceId !== nodeId && conn.targetId !== nodeId
  )
  emit('update:connections', updatedConnections)
  
  hideContextMenu()
}

// 显示连线右键菜单
function showConnectionContextMenu(connection: any, event: MouseEvent) {
  event.preventDefault()
  connectionContextMenu.value = {
    show: true,
    x: event.clientX,
    y: event.clientY,
    connection: connection
  }
  
  // 点击其他地方关闭菜单
  document.addEventListener('click', hideConnectionContextMenu)
}

// 隐藏连线右键菜单
function hideConnectionContextMenu() {
  connectionContextMenu.value.show = false
  document.removeEventListener('click', hideConnectionContextMenu)
}

// 删除连线
function deleteConnection() {
  if (!connectionContextMenu.value.connection) return
  
  const connectionId = connectionContextMenu.value.connection.id
  const updatedConnections = props.connections.filter(c => c.id !== connectionId)
  emit('update:connections', updatedConnections)
  
  hideConnectionContextMenu()
}

// 处理节点点击
function handleNodeClick(node: any) {
  emit('node-click', node)
}
</script>

<style scoped>
.nodes-container {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  transform-origin: 0 0;
}

.workflow-node {
  position: absolute;
  width: 200px;
  height: 120px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  pointer-events: all;
  user-select: none;
  border: 1px solid #eee;
  padding: 12px;
  display: flex;
  align-items: center;
  cursor: pointer;
  transform: scale(calc(1 / var(--zoom-factor, 1)));
  transform-origin: 0 0;
  
  &:hover {
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  }
  
  &.selected {
    border: 2px solid #4a90e2;
  }
}

.node-content {
  flex: 1;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.node-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
  flex-shrink: 0;
}

.node-type-icon {
  width: 24px;
  height: 24px;
}

.node-title {
  font-size: 14px;
  font-weight: 500;
  color: #2c3e50;
}

.connector {
  position: absolute;
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: crosshair;
  z-index: 2;
}

.connector.left {
  left: -12px;
  top: 50%;
  transform: translateY(-50%);
}

.connector.right {
  right: -12px;
  top: 50%;
  transform: translateY(-50%);
}

.connector-plus {
  width: 16px;
  height: 16px;
  background: #3498db;
  border-radius: 50%;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: bold;
}

.connections-layer {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 1;
}

.connection-group {
  cursor: pointer;
  pointer-events: all;
}

.connection-path {
  fill: none;
  stroke: #3498db;
  stroke-width: 2;
  pointer-events: all;
  vector-effect: non-scaling-stroke;
}

.connection-path.active {
  stroke-dasharray: 5,5;
  animation: dash 1s linear infinite;
}

@keyframes dash {
  to {
    stroke-dashoffset: 10;
  }
}

.connector-hint {
  position: absolute;
  background: rgba(52, 152, 219, 0.9);
  color: white;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  pointer-events: none;
  z-index: 1000;
  transform: translate(-50%, -50%);
}

.context-menu {
  position: fixed;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.15);
  padding: 8px 0;
  min-width: 160px;
  z-index: 1000;
}

.context-menu-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  cursor: pointer;
  transition: all 0.2s ease;
  color: #2c3e50;
}

.context-menu-item:hover {
  background: #f8f9fa;
  color: #3498db;
}

.context-menu-item i {
  width: 16px;
  text-align: center;
}
</style> 