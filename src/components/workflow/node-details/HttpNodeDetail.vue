<template>
  <div class="http-node-detail">
    <div class="form-group">
      <label>请求方法</label>
      <select v-model="nodeData.method" @change="updateNode">
        <option value="GET">GET</option>
        <option value="POST">POST</option>
        <option value="PUT">PUT</option>
        <option value="DELETE">DELETE</option>
        <option value="PATCH">PATCH</option>
      </select>
    </div>
    
    <div class="form-group">
      <label>请求URL</label>
      <input 
        type="text" 
        v-model="nodeData.url"
        @input="updateNode"
        placeholder="输入请求URL"
      >
    </div>
    
    <div class="form-group">
      <label>请求头</label>
      <div class="headers-container">
        <div v-for="(header, index) in nodeData.headers" :key="index" class="header-item">
          <input 
            type="text" 
            v-model="header.key"
            @input="updateNode"
            placeholder="键"
          >
          <input 
            type="text" 
            v-model="header.value"
            @input="updateNode"
            placeholder="值"
          >
          <button @click="removeHeader(index)" class="remove-header">×</button>
        </div>
        <button @click="addHeader" class="add-header">+ 添加请求头</button>
      </div>
    </div>
    
    <div class="form-group">
      <label>请求体</label>
      <textarea 
        v-model="nodeData.body"
        @input="updateNode"
        placeholder="输入请求体（JSON格式）"
        rows="4"
      ></textarea>
    </div>
    
    <div class="form-group">
      <label>高级设置</label>
      <div class="advanced-settings">
        <div class="setting-item">
          <label>超时时间(ms)</label>
          <input 
            type="number" 
            v-model="nodeData.timeout"
            @input="updateNode"
            min="1000"
            step="1000"
          >
        </div>
        <div class="setting-item">
          <label>重试次数</label>
          <input 
            type="number" 
            v-model="nodeData.retryCount"
            @input="updateNode"
            min="0"
            max="5"
          >
        </div>
        <div class="checkbox-group">
          <label>
            <input 
              type="checkbox" 
              v-model="nodeData.verifySSL"
              @change="updateNode"
            >
            验证SSL证书
          </label>
          <label>
            <input 
              type="checkbox" 
              v-model="nodeData.followRedirects"
              @change="updateNode"
            >
            跟随重定向
          </label>
        </div>
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
  method: props.node.data?.method || 'GET',
  url: props.node.data?.url || '',
  headers: props.node.data?.headers || [{ key: '', value: '' }],
  body: props.node.data?.body || '',
  timeout: props.node.data?.timeout || 5000,
  retryCount: props.node.data?.retryCount || 3,
  verifySSL: props.node.data?.verifySSL || true,
  followRedirects: props.node.data?.followRedirects || true
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

// 添加请求头
function addHeader() {
  nodeData.value.headers.push({ key: '', value: '' })
  updateNode()
}

// 删除请求头
function removeHeader(index: number) {
  nodeData.value.headers.splice(index, 1)
  updateNode()
}
</script>

<style scoped>
.http-node-detail {
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

select, input[type="text"], input[type="number"], textarea {
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
}

select:focus, input:focus, textarea:focus {
  outline: none;
  border-color: #4a90e2;
}

.headers-container {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.header-item {
  display: flex;
  gap: 8px;
}

.header-item input {
  flex: 1;
}

.remove-header {
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

.add-header {
  padding: 8px;
  border: 1px dashed #ddd;
  border-radius: 4px;
  background: none;
  cursor: pointer;
  color: #666;
}

.add-header:hover {
  border-color: #4a90e2;
  color: #4a90e2;
}

.advanced-settings {
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding: 12px;
  background: #f8f9fa;
  border-radius: 4px;
}

.setting-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
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