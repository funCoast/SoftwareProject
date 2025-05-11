<script setup lang="ts">
import { ref, defineProps, defineEmits, onMounted, nextTick, watch } from 'vue'

const props = defineProps<{
  nodes: any[],
  selectedNode: any,
  connections: any[],
  zoom: number
}>()

const emit = defineEmits<{
  (e: 'update:nodes', nodes: any[]): void
  (e: 'update:connections', connections: any[]): void
  (e: 'node-click', node: any): void
  (e: 'run-node', node: any): void
}>()

// 拖拽相关
const draggedNode = ref<any>(null)
const dragOffset = ref({ x: 0, y: 0 })

// 正在拖动的连线
const activeConnection = ref<{
  sourceNode: any | null,
  sourceType: 'left' | 'right' | null,
  startX: number | null,
  startY: number | null
}>({
  sourceNode: null,
  sourceType: null,
  startX: null,
  startY: null
})

const showConnectorHint = ref(false)
const connectorHintStyle = ref({
  left: '0px',
  top: '0px'
})

// 节点右键菜单状态
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
// 连线时鼠标坐标状态
const connectionMousePos = ref({ x: 0, y: 0 })

// 处理节点点击
function handleNodeClick(node: any) {
  emit('node-click', node)
}

// 在节点上按下鼠标
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

// 拖动节点
function handleDrag(event: MouseEvent) {
  if (!draggedNode.value) return
  const canvas = document.querySelector('.canvas-area')
  if (!canvas) return
  const rect = canvas.getBoundingClientRect()
  const x = (event.clientX - rect.left - dragOffset.value.x) / props.zoom
  const y = (event.clientY - rect.top - dragOffset.value.y) / props.zoom
  
  // 获取节点元素
  const nodeEl = document.querySelector(`[data-node-id="${draggedNode.value.id}"]`)
  if (!nodeEl) return
  const nodeRect = nodeEl.getBoundingClientRect()
  const nodeWidth = nodeRect.width / props.zoom
  const nodeHeight = nodeRect.height / props.zoom
  
  // 计算画布边界（考虑缩放）
  const maxX = rect.width / props.zoom - nodeWidth
  const maxY = rect.height / props.zoom - nodeHeight
  
  // 限制节点位置在画布范围内
  draggedNode.value.x = Math.max(0, Math.min(x, maxX))
  draggedNode.value.y = Math.max(0, Math.min(y, maxY))
  
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

// 拖动节点后松开鼠标
function stopDrag() {
  draggedNode.value = null
  document.removeEventListener('mousemove', handleDrag)
  document.removeEventListener('mouseup', stopDrag)
}

// 按下鼠标开始连接
function startConnection(node: any, type: 'left' | 'right', event: MouseEvent) {
  const rect = (event.target as HTMLElement).getBoundingClientRect()
  const canvas = document.querySelector('.canvas-area')
  if (!canvas) return
  const canvasRect = canvas.getBoundingClientRect()
  connectionMousePos.value = {
    x: (event.clientX - canvasRect.left) / props.zoom,
    y: (event.clientY - canvasRect.top) / props.zoom
  }
  activeConnection.value = {
    sourceNode: node,
    sourceType: type,
    startX: rect.left + rect.width / 2,
    startY: rect.top + rect.height / 2
  }
  window.addEventListener('mousemove', handleConnectionDrag)
  window.addEventListener('mouseup', stopConnection)
}

// 连线
function handleConnectionDrag(event: MouseEvent) {
  if (!activeConnection.value.sourceNode) return
  // 实时记录鼠标逻辑坐标
  const canvas = document.querySelector('.canvas-area')
  if (!canvas) return
  const rect = canvas.getBoundingClientRect()
  connectionMousePos.value = {
    x: (event.clientX - rect.left) / props.zoom,
    y: (event.clientY - rect.top) / props.zoom
  }
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

// 连接时松开鼠标
function stopConnection(event: MouseEvent) {
  if (!activeConnection.value.sourceNode) return
  const targetConnector = findTargetConnector(event)
  if (targetConnector && targetConnector.node.id !== activeConnection.value.sourceNode.id && targetConnector.type !== activeConnection.value.sourceType) {
    const sourceId = targetConnector.type === 'left' ? activeConnection.value.sourceNode.id : targetConnector.node.id
    const targetId = targetConnector.type === 'left' ? targetConnector.node.id : activeConnection.value.sourceNode.id
    const sourceType = 'right'
    const targetType = 'left'
    const newConnection = {
      id: Date.now(),
      sourceId: sourceId,
      targetId: targetId,
      sourceType: sourceType,
      targetType: targetType
    }
    // 检查是否重复连接
    const exists = props.connections.some(conn =>
        (conn.sourceId === newConnection.sourceId && conn.targetId === newConnection.targetId) ||
        (conn.sourceId === newConnection.targetId && conn.targetId === newConnection.sourceId)
    )
    if (!exists) {
      emit('update:connections', [...props.connections, newConnection])
      // 更新目标节点的 beforeWorkflowNodeIds
      const targetNode = props.nodes.find(n => n.id === newConnection.targetId)
      const sourceNode = props.nodes.find(n => n.id === newConnection.sourceId)
      if (targetNode && sourceNode) {
        targetNode.beforeWorkflowNodeIds.push(sourceId)
        sourceNode.nextWorkflowNodeIds.push(targetId)
        // 更新节点
        const updatedNodes = [...props.nodes]
        const targetIndex = updatedNodes.findIndex(n => n.id === targetNode.id)
        if (targetIndex !== -1) {
          updatedNodes[targetIndex] = { ...targetNode }
          emit('update:nodes', updatedNodes)
        }
      }
    }
  }
  activeConnection.value = {
    sourceNode: null,
    sourceType: null,
    startX: null,
    startY: null
  }
  showConnectorHint.value = false
  window.removeEventListener('mousemove', handleConnectionDrag)
  window.removeEventListener('mouseup', stopConnection)
}

// 寻找目标连接点
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
  const mouseX = connectionMousePos.value.x
  const mouseY = connectionMousePos.value.y
  // 动态计算控制点
  const dx = mouseX - sourceX
  const controlOffset = Math.min(Math.abs(dx) * 0.5, 150) * (dx > 0 ? 1 : -1)
  return `M ${sourceX} ${sourceY}
          C ${sourceX + controlOffset} ${sourceY},
            ${mouseX} ${mouseY},
            ${mouseX} ${mouseY}`
}

// 右键菜单相关函数
function showContextMenu(node: any, event: MouseEvent) {
  if (node.type === 'start') return
  const canvas = document.querySelector('.canvas-area')
  if (!canvas) return
  const canvasRect = canvas.getBoundingClientRect()
  event.preventDefault()
  contextMenu.value = {
    show: true,
    x: event.clientX - canvasRect.left,
    y: event.clientY - canvasRect.top,
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
    id: Date.now(),
    type: originalNode.type,
    label: originalNode.label,
    name: originalNode.name,
    description: originalNode.description,
    image: originalNode.image,
    x: originalNode.x + 20, // 稍微偏移一点，避免完全重叠
    y: originalNode.y + 20,
    beforeWorkflowNodeIds: [],
    nextWorkflowNodeIds: [],
    inputs: [],
    outputs: [],
    data: originalNode.data ? JSON.parse(JSON.stringify(originalNode.data)) : undefined
  }
  const updatedNodes = [...props.nodes, newNode]
  emit('update:nodes', updatedNodes)
  hideContextMenu()
}

// 删除节点
function deleteNode() {
  if (!contextMenu.value.node) return
  const nodeId = contextMenu.value.node.id
  // 找到所有结束节点（即 nextWorkflowNodeIds.length === 0）
  const endNodes = props.nodes.filter(n => n.type === 'end')
  // 如果该节点是唯一的结束节点，不允许删除
  if (endNodes.length === 1 && endNodes[0].id === nodeId) {
    hideContextMenu()
    return
  }
  // 删除节点
  const updatedNodes = props.nodes.filter(n => n.id !== nodeId)
  for (const node of updatedNodes) {
    node.beforeWorkflowNodeIds = node.beforeWorkflowNodeIds.filter(id => id !== nodeId)
    node.nextWorkflowNodeIds = node.nextWorkflowNodeIds.filter(id => id !== nodeId)
  }
  emit('update:nodes', updatedNodes)
  // 删除与该节点相关的所有连接
  const updatedConnections = props.connections.filter(conn =>
      conn.sourceId !== nodeId && conn.targetId !== nodeId
  )
  emit('update:connections', updatedConnections)
  hideContextMenu()
}

// 删除连线
function deleteConnection() {
  const conn = connectionContextMenu.value.connection
  if (!conn) return
  const { sourceId, targetId } = conn
  const updatedConnections = props.connections.filter(c => c.id !== conn.id)
  const updatedNodes = props.nodes.map(n => {
    if (n.id === sourceId) {
      return {
        ...n,
        nextWorkflowNodeIds: n.nextWorkflowNodeIds.filter(id => id !== targetId)
      }
    } else if (n.id === targetId) {
      return {
        ...n,
        beforeWorkflowNodeIds: n.beforeWorkflowNodeIds.filter(id => id !== sourceId)
      }
    }
    return n
  })
  emit('update:nodes', updatedNodes)
  emit('update:connections', updatedConnections)
  hideConnectionContextMenu()
}

// 显示连线右键菜单
function showConnectionContextMenu(connection: any, event: MouseEvent) {
  event.preventDefault()
  const canvas = document.querySelector('.canvas-area')
  if (!canvas) return ''
  const canvasRect = canvas.getBoundingClientRect()
  connectionContextMenu.value = {
    show: true,
    x: event.clientX - canvasRect.left,
    y: event.clientY - canvasRect.top,
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

// 添加运行节点的函数
function runNode(node: any) {
  emit('run-node', node)
}

// 在 setup 中添加初始化函数
async function initializeConnections() {
  // 等待下一个 tick，确保节点 DOM 已渲染
  await nextTick()
  // 触发连线重绘
  connectionUpdateTrigger.value++
}

// 监听节点变化
watch(() => props.nodes, async () => {
  await initializeConnections()
}, { deep: true })

// 监听缩放变化
watch(() => props.zoom, async () => {
  await initializeConnections()
})

// 在 onMounted 中调用初始化
onMounted(async () => {
  // 延迟一小段时间确保 DOM 完全渲染
  setTimeout(async () => {
    await initializeConnections()
  }, 100)
})
</script>

<template>
  <div>
    <!-- 节点容器 -->
    <div class="nodes-container">
      <div v-for="node in nodes" 
           :key="node.id" 
           class="workflow-node"
           :class="{ selected: selectedNode && node.id === selectedNode.id }"
           :data-node-id="node.id"
           :style="{
             left: node.x + 'px',
             top: node.y + 'px',
             transform: `scale(${1/zoom})`
           }"
           @click="handleNodeClick(node)"
           @mousedown="startDrag(node, $event)"
           @contextmenu.prevent="showContextMenu(node, $event)">
        <!-- 左侧连接点 -->
        <div class="connector left"
             v-if="node.type !== 'start'"
             @mousedown.stop="startConnection(node, 'left', $event)">
          <div class="connector-plus">+</div>
        </div>
        
        <div class="node-content">
          <div class="node-header">
            <img :src="node.image" :alt="node.label" class="node-type-icon">
            <span class="node-title">{{ node.name || node.label }}</span>
<!--            <button class="run-btn" @click.stop="runNode(node)" title="运行节点">-->
<!--              <img src="https://api.iconify.design/material-symbols:play-circle.svg" alt="运行" class="run-icon">-->
<!--            </button>-->
          </div>
          <div class="node-description" v-if="node.description">
            {{ node.description }}
          </div>
        </div>

        <!-- 右侧连接点 -->
        <div class="connector right"
             v-if="node.type !== 'end'"
             @mousedown.stop="startConnection(node, 'right', $event)">
          <div class="connector-plus">+</div>
        </div>

        <!-- 运行结果显示 -->
        <div v-if="node.runResult" class="node-result">
          <div class="result-header">
            <span class="result-title">运行结果</span>
            <span class="result-type">{{ typeof node.runResult === 'object' ? 'Object' : typeof node.runResult }}</span>
          </div>
          <div class="result-content" :class="{ 'result-string': typeof node.runResult === 'string' }">
            <template v-if="typeof node.runResult === 'object'">
              <pre>{{ JSON.stringify(node.runResult, null, 2) }}</pre>
            </template>
            <template v-else>
              {{ node.runResult }}
            </template>
          </div>
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
  min-height: 120px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  pointer-events: all;
  user-select: none;
  border: 1px solid #eee;
  padding: 12px;
  display: flex;
  flex-direction: column;
  cursor: pointer;
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
  display: flex;
  flex-direction: column;
  position: relative;
  padding: 0 12px;
}

.node-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
  flex-shrink: 0;
  position: relative;
  padding-right: 32px;
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

.node-description {
  font-size: 12px;
  color: #666;
  margin: 8px 0;
  padding: 0 8px;
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

.run-btn {
  position: absolute;
  right: 0;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  padding: 4px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0.7;
  transition: all 0.2s;
}

.run-btn:hover {
  opacity: 1;
  transform: translateY(-50%) scale(1.1);
}

.run-icon {
  width: 20px;
  height: 20px;
  color: #3498db;
}

.node-result {
  position: absolute;
  left: 0;
  right: 0;
  top: 100%;
  margin-top: 8px;
  background: #f8f9fa;
  border-radius: 6px;
  border: 1px solid #e9ecef;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  width: 100%;
  z-index: 10;
}

.result-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 6px 10px;
  background: #e9ecef;
  border-bottom: 1px solid #dee2e6;
}

.result-title {
  font-size: 12px;
  font-weight: 500;
  color: #495057;
}

.result-type {
  font-size: 11px;
  color: #6c757d;
  background: #fff;
  padding: 2px 6px;
  border-radius: 4px;
}

.result-content {
  padding: 8px 10px;
  font-size: 12px;
  color: #495057;
  max-height: 120px;
  overflow: auto;
  background: white;
}

.result-content pre {
  margin: 0;
  white-space: pre-wrap;
  word-break: break-all;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', 'Consolas', 'source-code-pro', monospace;
}

.result-string {
  white-space: pre-wrap;
  word-break: break-all;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', 'Consolas', 'source-code-pro', monospace;
}

/* 自定义滚动条样式 */
.result-content::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}

.result-content::-webkit-scrollbar-track {
  background: #f1f3f5;
  border-radius: 3px;
}

.result-content::-webkit-scrollbar-thumb {
  background: #ced4da;
  border-radius: 3px;
}

.result-content::-webkit-scrollbar-thumb:hover {
  background: #adb5bd;
}
</style> 