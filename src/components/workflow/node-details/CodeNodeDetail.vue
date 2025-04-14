<script setup lang="ts">
import { ref, watch } from 'vue'
import { WorkflowNode } from '@/types/workflow'

const props = defineProps<{
  node: WorkflowNode
}>()

const emit = defineEmits<{
  (e: 'update:node', node: WorkflowNode): void
}>()

const nodeData = ref({
  language: props.node.data?.language || 'javascript',
  code: props.node.data?.code || '',
  inputParams: props.node.data?.inputParams || [],
  outputParams: props.node.data?.outputParams || [],
  useSandbox: props.node.data?.useSandbox || true,
  timeoutEnabled: props.node.data?.timeoutEnabled || false,
  timeout: props.node.data?.timeout || 30
})

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

function addParam() {
  nodeData.value.inputParams.push({ name: '', type: 'string' })
  updateNode()
}

function removeParam(index: number) {
  nodeData.value.inputParams.splice(index, 1)
  updateNode()
}

function addOutputParam() {
  nodeData.value.outputParams.push({ name: '', type: 'string' })
  updateNode()
}

function removeOutputParam(index: number) {
  nodeData.value.outputParams.splice(index, 1)
  updateNode()
}
</script>

<template>
  <div class="code-node-detail">
    <div class="form-group">
      <label>编程语言</label>
      <select v-model="nodeData.language" @change="updateNode">
        <option value="javascript">JavaScript</option>
        <option value="python">Python</option>
        <option value="typescript">TypeScript</option>
        <option value="java">Java</option>
        <option value="csharp">C#</option>
      </select>
    </div>

    <div class="form-group">
      <label>代码内容</label>
      <textarea
        v-model="nodeData.code"
        @input="updateNode"
        placeholder="输入代码..."
        rows="10"
      ></textarea>
    </div>

    <div class="form-group">
      <label>输入参数</label>
      <div class="params-container">
        <div v-for="(param, index) in nodeData.inputParams" :key="index" class="param-item">
          <input
            type="text"
            v-model="param.name"
            @input="updateNode"
            placeholder="参数名"
          >
          <select v-model="param.type" @change="updateNode">
            <option value="string">字符串</option>
            <option value="number">数字</option>
            <option value="boolean">布尔值</option>
            <option value="object">对象</option>
            <option value="array">数组</option>
          </select>
          <button @click="removeParam(index)" class="remove-param">×</button>
        </div>
        <button @click="addParam" class="add-param">+ 添加参数</button>
      </div>
    </div>

    <div class="form-group">
      <label>输出参数</label>
      <div class="params-container">
        <div v-for="(param, index) in nodeData.outputParams" :key="index" class="param-item">
          <input
            type="text"
            v-model="param.name"
            @input="updateNode"
            placeholder="参数名"
          >
          <select v-model="param.type" @change="updateNode">
            <option value="string">字符串</option>
            <option value="number">数字</option>
            <option value="boolean">布尔值</option>
            <option value="object">对象</option>
            <option value="array">数组</option>
          </select>
          <button @click="removeOutputParam(index)" class="remove-param">×</button>
        </div>
        <button @click="addOutputParam" class="add-param">+ 添加输出参数</button>
      </div>
    </div>

    <div class="form-group">
      <label>高级设置</label>
      <div class="advanced-settings">
        <label class="checkbox-label">
          <input
            type="checkbox"
            v-model="nodeData.useSandbox"
            @change="updateNode"
          />
          使用沙箱环境
        </label>
        <label class="checkbox-label">
          <input
            type="checkbox"
            v-model="nodeData.timeoutEnabled"
            @change="updateNode"
          />
          启用超时限制
        </label>
        <div v-if="nodeData.timeoutEnabled" class="timeout-setting">
          <input
            type="number"
            v-model="nodeData.timeout"
            @input="updateNode"
            min="1"
            max="300"
          />
          <span>秒</span>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.code-node-detail {
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
  color: #333;
}

select, input[type="text"], input[type="number"], textarea {
  width: 100%;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

textarea {
  font-family: monospace;
  resize: vertical;
}

.params-container {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.param-item {
  display: flex;
  gap: 8px;
}

.param-item input, .param-item select {
  flex: 1;
}

.remove-param {
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

.add-param {
  padding: 8px;
  border: 1px dashed #ddd;
  border-radius: 4px;
  background: none;
  cursor: pointer;
  color: #666;
}

.add-param:hover {
  border-color: #4a90e2;
  color: #4a90e2;
}

.advanced-settings {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 12px;
  background: #f8f9fa;
  border-radius: 4px;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
}

.timeout-setting {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 8px;
}

.timeout-setting input {
  width: 80px;
}
</style> 