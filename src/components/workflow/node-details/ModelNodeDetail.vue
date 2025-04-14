<template>
  <div class="model-node-detail">
    <div class="form-group">
      <label>模型选择</label>
      <select v-model="nodeData.modelType" @change="updateNode">
        <option value="gpt-4">GPT-4</option>
        <option value="gpt-3.5">GPT-3.5</option>
        <option value="claude">Claude</option>
      </select>
    </div>
    
    <div class="form-group">
      <label>温度 (Temperature)</label>
      <input 
        type="range" 
        v-model="nodeData.temperature" 
        min="0" 
        max="1" 
        step="0.1"
        @input="updateNode"
      >
      <span class="value">{{ nodeData.temperature }}</span>
    </div>
    
    <div class="form-group">
      <label>最大输出长度</label>
      <input 
        type="number" 
        v-model="nodeData.maxTokens" 
        min="1" 
        max="4096"
        @input="updateNode"
      >
    </div>
    
    <div class="form-group">
      <label>系统提示词</label>
      <textarea 
        v-model="nodeData.systemPrompt" 
        rows="4"
        @input="updateNode"
        placeholder="输入系统提示词..."
      ></textarea>
    </div>
    
    <div class="form-group">
      <label>高级设置</label>
      <div class="checkbox-group">
        <label>
          <input 
            type="checkbox" 
            v-model="nodeData.streamOutput"
            @change="updateNode"
          >
          流式输出
        </label>
        <label>
          <input 
            type="checkbox" 
            v-model="nodeData.saveHistory"
            @change="updateNode"
          >
          保存对话历史
        </label>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, defineProps, defineEmits, watch } from 'vue'

const props = defineProps<{
  node: any
}>()

const emit = defineEmits<{
  (e: 'update:node', node: any): void
}>()

// 节点数据
const nodeData = ref({
  modelType: props.node.data?.modelType || 'gpt-3.5',
  temperature: props.node.data?.temperature || 0.7,
  maxTokens: props.node.data?.maxTokens || 2048,
  systemPrompt: props.node.data?.systemPrompt || '',
  streamOutput: props.node.data?.streamOutput || false,
  saveHistory: props.node.data?.saveHistory || false
})

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
</script>

<style scoped>
.model-node-detail {
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

select, input[type="number"], textarea {
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
}

select:focus, input:focus, textarea:focus {
  outline: none;
  border-color: #4a90e2;
}

input[type="range"] {
  width: 100%;
}

.value {
  font-size: 14px;
  color: #666;
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

textarea {
  resize: vertical;
  min-height: 80px;
}
</style> 