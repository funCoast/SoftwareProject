<script setup lang="ts">
import { ref, defineEmits, watch } from 'vue'

const props = defineProps<{
  node: any
}>()

const emit = defineEmits<{
  (e: 'update:node', node: any): void
}>()

// 节点数据
const nodeData = ref({
  workflowId: props.node.data?.workflowId || '',
  inputMappings: props.node.data?.inputMappings || [{ source: '', target: '' }],
  outputMappings: props.node.data?.outputMappings || [{ source: '', target: '' }],
  continueOnError: props.node.data?.continueOnError || false,
  returnAllOutputs: props.node.data?.returnAllOutputs || false
})

// 可用工作流列表（示例数据）
const availableWorkflows = ref([
  { id: '1', name: '工作流1' },
  { id: '2', name: '工作流2' },
  { id: '3', name: '工作流3' }
])

// 监听数据变化并更新节点
watch(nodeData, (newData) => {
  const updatedNode = {
    ...props.node,
    data: {
      ...props.node.data,
      ...newData
    }
  }
  emit('update:node', updatedNode)
}, { deep: true })

// 更新节点
function updateNode() {
  const updatedNode = {
    ...props.node,
    data: {
      ...props.node.data,
      ...nodeData.value
    }
  }
  emit('update:node', updatedNode)
}

// 添加映射
function addMapping() {
  nodeData.value.inputMappings.push({ source: '', target: '' })
  updateNode()
}

// 删除映射
function removeMapping(index: number) {
  nodeData.value.inputMappings.splice(index, 1)
  updateNode()
}
</script>

<template>
  <div class="workflow-node-detail">
    <div class="form-group">
      <label>工作流选择</label>
      <select v-model="nodeData.workflowId" @change="updateNode">
        <option value="">请选择工作流</option>
        <option v-for="wf in availableWorkflows" :key="wf.id" :value="wf.id">
          {{ wf.name }}
        </option>
      </select>
    </div>
    
    <div class="form-group">
      <label>输入参数映射</label>
      <div class="mapping-container">
        <div v-for="(mapping, index) in nodeData.inputMappings" :key="index" class="mapping-item">
          <input 
            type="text" 
            v-model="mapping.source"
            @input="updateNode"
            placeholder="源参数"
          >
          <span>→</span>
          <input 
            type="text" 
            v-model="mapping.target"
            @input="updateNode"
            placeholder="目标参数"
          >
          <button @click="removeMapping(index)" class="remove-mapping">×</button>
        </div>
        <button @click="addMapping" class="add-mapping">+ 添加映射</button>
      </div>
    </div>
    
    <div class="form-group">
      <label>输出参数映射</label>
      <div class="mapping-container">
        <div v-for="(mapping, index) in nodeData.outputMappings" :key="index" class="mapping-item">
          <input 
            type="text" 
            v-model="mapping.source"
            @input="updateNode"
            placeholder="源参数"
          >
          <span>→</span>
          <input 
            type="text" 
            v-model="mapping.target"
            @input="updateNode"
            placeholder="目标参数"
          >
          <button @click="removeMapping(index)" class="remove-mapping">×</button>
        </div>
        <button @click="addMapping" class="add-mapping">+ 添加映射</button>
      </div>
    </div>
    
    <div class="form-group">
      <label>高级设置</label>
      <div class="checkbox-group">
        <label>
          <input 
            type="checkbox" 
            v-model="nodeData.continueOnError"
            @change="updateNode"
          >
          错误时继续执行
        </label>
        <label>
          <input 
            type="checkbox" 
            v-model="nodeData.returnAllOutputs"
            @change="updateNode"
          >
          返回所有输出
        </label>
      </div>
    </div>
  </div>
</template>

<style scoped>
.workflow-node-detail {
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

select {
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
}

select:focus {
  outline: none;
  border-color: #4a90e2;
}

.mapping-container {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.mapping-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.mapping-item input {
  flex: 1;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
}

.remove-mapping {
  width: 24px;
  height: 24px;
  border: none;
  background: #ff6b6b;
  color: white;
  border-radius: 4px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
}

.add-mapping {
  padding: 8px;
  border: 1px dashed #ddd;
  border-radius: 4px;
  background: none;
  cursor: pointer;
  color: #666;
}

.add-mapping:hover {
  border-color: #4a90e2;
  color: #4a90e2;
}

.checkbox-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.checkbox-group label {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: normal;
}
</style> 