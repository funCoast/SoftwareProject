<template>
  <div class="plugin-node-detail">
    <div class="form-group">
      <label>插件选择</label>
      <select v-model="nodeData.pluginId" @change="updateNode">
        <option value="">请选择插件</option>
        <option v-for="plugin in availablePlugins" :key="plugin.id" :value="plugin.id">
          {{ plugin.name }}
        </option>
      </select>
    </div>

    <div v-if="nodeData.pluginId" class="form-group">
      <label>插件版本</label>
      <select v-model="nodeData.pluginVersion" @change="updateNode">
        <option v-for="version in getPluginVersions(nodeData.pluginId)" :key="version" :value="version">
          {{ version }}
        </option>
      </select>
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
          <input
            type="text"
            v-model="param.value"
            @input="updateNode"
            placeholder="参数值"
          >
          <button @click="removeParam(index)" class="remove-param">×</button>
        </div>
        <button @click="addParam" class="add-param">+ 添加参数</button>
      </div>
    </div>

    <div class="form-group">
      <label>输出映射</label>
      <div class="mapping-container">
        <div v-for="(mapping, index) in nodeData.outputMappings" :key="index" class="mapping-item">
          <input
            type="text"
            v-model="mapping.source"
            @input="updateNode"
            placeholder="源字段"
          >
          <span>→</span>
          <input
            type="text"
            v-model="mapping.target"
            @input="updateNode"
            placeholder="目标字段"
          >
          <button @click="removeMapping(index)" class="remove-mapping">×</button>
        </div>
        <button @click="addMapping" class="add-mapping">+ 添加映射</button>
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
        <div v-if="nodeData.timeoutEnabled" class="setting-item">
          <label>超时时间(秒)</label>
          <input
            type="number"
            v-model="nodeData.timeout"
            @input="updateNode"
            min="1"
            max="300"
          >
        </div>
        <label class="checkbox-label">
          <input
            type="checkbox"
            v-model="nodeData.retryOnError"
            @change="updateNode"
          />
          错误时重试
        </label>
        <div v-if="nodeData.retryOnError" class="setting-item">
          <label>最大重试次数</label>
          <input
            type="number"
            v-model="nodeData.maxRetries"
            @input="updateNode"
            min="1"
            max="5"
          >
        </div>
      </div>
    </div>
  </div>
</template>

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
  pluginId: props.node.data?.pluginId || '',
  pluginVersion: props.node.data?.pluginVersion || '',
  inputParams: props.node.data?.inputParams || [],
  outputMappings: props.node.data?.outputMappings || [],
  useSandbox: props.node.data?.useSandbox || true,
  timeoutEnabled: props.node.data?.timeoutEnabled || false,
  timeout: props.node.data?.timeout || 30,
  retryOnError: props.node.data?.retryOnError || false,
  maxRetries: props.node.data?.maxRetries || 3
})

// 可用插件列表（示例数据）
const availablePlugins = ref([
  { id: '1', name: '天气查询插件', versions: ['1.0.0', '1.1.0'] },
  { id: '2', name: '翻译插件', versions: ['1.0.0', '1.2.0'] },
  { id: '3', name: '图片处理插件', versions: ['1.0.0', '1.3.0'] }
])

function getPluginVersions(pluginId: string) {
  const plugin = availablePlugins.value.find(p => p.id === pluginId)
  return plugin?.versions || []
}

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
  nodeData.value.inputParams.push({ name: '', type: 'string', value: '' })
  updateNode()
}

function removeParam(index: number) {
  nodeData.value.inputParams.splice(index, 1)
  updateNode()
}

function addMapping() {
  nodeData.value.outputMappings.push({ source: '', target: '' })
  updateNode()
}

function removeMapping(index: number) {
  nodeData.value.outputMappings.splice(index, 1)
  updateNode()
}
</script>

<style scoped>
.plugin-node-detail {
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

select, input[type="text"], input[type="number"] {
  width: 100%;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.params-container, .mapping-container {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.param-item, .mapping-item {
  display: flex;
  gap: 8px;
}

.param-item input, .param-item select, .mapping-item input {
  flex: 1;
}

.remove-param, .remove-mapping {
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

.add-param, .add-mapping {
  padding: 8px;
  border: 1px dashed #ddd;
  border-radius: 4px;
  background: none;
  cursor: pointer;
  color: #666;
}

.add-param:hover, .add-mapping:hover {
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

.setting-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
  margin-top: 8px;
  padding-left: 8px;
}
</style> 