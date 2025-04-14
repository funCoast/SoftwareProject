<script setup lang="ts">
import { computed, defineEmits } from 'vue'
import ClassifierNodeDetail from './node-details/ClassifierNodeDetail.vue'
import CodeNodeDetail from './node-details/CodeNodeDetail.vue'
import ConditionNodeDetail from './node-details/ConditionNodeDetail.vue'
import ExtractNodeDetail from './node-details/ExtractNodeDetail.vue'
import HttpNodeDetail from './node-details/HttpNodeDetail.vue'
import KnowledgeNodeDetail from './node-details/KnowledgeNodeDetail.vue'
import LoopNodeDetail from './node-details/LoopNodeDetail.vue'
import ModelNodeDetail from './node-details/ModelNodeDetail.vue'
import PluginNodeDetail from './node-details/PluginNodeDetail.vue'
import WorkflowNodeDetail from './node-details/WorkflowNodeDetail.vue'

const props = defineProps<{
  show: boolean,
  node: any,
  nodeTypes: any[]
}>()

const emit = defineEmits<{
  (e: 'close'): void
  (e: 'update:node', node: any): void
}>()

// 获取节点图标
const nodeImage = computed(() => {
  if (!props.node) return ''
  const nodeType = props.nodeTypes.find(nt => nt.type === props.node.type)
  return nodeType?.image || ''
})

// 根据节点类型获取对应的详情组件
const getNodeDetailComponent = computed(() => {
  if (!props.node) return null
  
  const componentMap: Record<string, any> = {
    'model': ModelNodeDetail,
    'plugin': PluginNodeDetail,
    'workflow': WorkflowNodeDetail,
    'http': HttpNodeDetail,
    'code': CodeNodeDetail,
    'condition': ConditionNodeDetail,
    'loop': LoopNodeDetail,
    'classifier': ClassifierNodeDetail,
    'knowledge': KnowledgeNodeDetail,
    'extract': ExtractNodeDetail
  }
  
  return componentMap[props.node.type] || null
})

// 关闭面板
function closePanel() {
  emit('close')
}

// 更新节点
function updateNode(updatedNode: any) {
  emit('update:node', updatedNode)
}
</script>

<template>
  <div class="node-detail-panel" v-if="show">
    <div class="panel-header">
      <div class="node-title">
        <img :src="nodeImage" :alt="node?.label" class="node-icon">
        <h3>{{ node?.label }}</h3>
      </div>
      <button class="close-btn" @click="closePanel">
        <i class="fas fa-times"></i>
      </button>
    </div>
    
    <div class="panel-content">
      <!-- 根据节点类型动态加载不同的详情组件 -->
      <component 
        :is="getNodeDetailComponent" 
        :node="node"
        @update:node="updateNode"
      ></component>
    </div>
  </div>
</template>

<style scoped>
.node-detail-panel {
  position: fixed;
  top: 0;
  right: 0;
  width: 350px;
  height: 100vh;
  background: white;
  box-shadow: -2px 0 10px rgba(0, 0, 0, 0.1);
  z-index: 1000;
  display: flex;
  flex-direction: column;
  animation: slideIn 0.3s ease;
}

@keyframes slideIn {
  from {
    transform: translateX(100%);
  }
  to {
    transform: translateX(0);
  }
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  border-bottom: 1px solid #eee;
}

.node-title {
  display: flex;
  align-items: center;
  gap: 12px;
}

.node-title h3 {
  margin: 0;
  font-size: 18px;
  color: #2c3e50;
}

.node-icon {
  width: 24px;
  height: 24px;
}

.close-btn {
  background: none;
  border: none;
  font-size: 18px;
  cursor: pointer;
  color: #666;
  padding: 4px;
  transition: color 0.3s;
}

.close-btn:hover {
  color: #2c3e50;
}

.panel-content {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
}
</style> 