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
         @dragover.prevent
         @drop="handleDrop"
         :style="{ transform: `scale(${zoom})` }">
      <div class="grid-background"></div>
      <!-- 这里将显示工作流节点 -->
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
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const zoom = ref(1)
const showNodeSelector = ref(false)
const nodes =ref ([
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
const nodeTypes = ref<nodeType[]> ([
  { 
    type: 'start',
    label: '开始',
    icon: 'fas fa-play-circle',
    description: '工作流的起始节点',
    image: 'https://api.iconify.design/material-symbols:play-circle.svg'
  },
  { 
    type: 'end',
    label: '结束',
    icon: 'fas fa-stop-circle',
    description: '工作流的结束节点',
    image: 'https://api.iconify.design/material-symbols:stop-circle.svg'
  },
  { 
    type: 'model',
    label: '大模型',
    icon: 'fas fa-brain',
    description: '使用AI大模型处理任务',
    image: 'https://api.iconify.design/carbon:machine-learning-model.svg'
  },
  { 
    type: 'plugin',
    label: '插件',
    icon: 'fas fa-puzzle-piece',
    description: '使用自定义插件扩展功能',
    image: 'https://api.iconify.design/material-symbols:extension.svg'
  },
  { 
    type: 'workflow',
    label: '工作流',
    icon: 'fas fa-project-diagram',
    description: '嵌套调用其他工作流',
    image: 'https://api.iconify.design/material-symbols:account-tree.svg'
  },
  { 
    type: 'http',
    label: 'HTTP请求',
    icon: 'fas fa-globe',
    description: '发送HTTP请求获取数据',
    image: 'https://api.iconify.design/material-symbols:api.svg'
  },
  { 
    type: 'code',
    label: '代码',
    icon: 'fas fa-code',
    description: '执行自定义代码逻辑',
    image: 'https://api.iconify.design/material-symbols:code.svg'
  },
  { 
    type: 'condition',
    label: '条件分支',
    icon: 'fas fa-code-branch',
    description: '根据条件选择执行路径',
    image: 'https://api.iconify.design/material-symbols:fork-right.svg'
  },
  { 
    type: 'loop',
    label: '循环',
    icon: 'fas fa-redo',
    description: '重复执行特定任务',
    image: 'https://api.iconify.design/material-symbols:repeat.svg'
  },
  { 
    type: 'intent',
    label: '意图识别',
    icon: 'fas fa-lightbulb',
    description: '识别用户输入的意图',
    image: 'https://api.iconify.design/material-symbols:psychology-alt.svg'
  },
  { 
    type: 'knowledge',
    label: '知识库检索',
    icon: 'fas fa-database',
    description: '从知识库中检索信息',
    image: 'https://api.iconify.design/material-symbols:database.svg'
  }
])

function handleDrop() {
    // 处理节点放置逻辑
}
function addNode(type: string) {
    // 添加节点的逻辑
    console.log('Adding node of type:', type)
    showNodeSelector.value = false
}
function runTest() {
  // 试运行逻辑
}

function debug() {
  // 调试逻辑
}
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
</style> 