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
  knowledgeBaseId: props.node.data?.knowledgeBaseId || '',
  searchMethod: props.node.data?.searchMethod || 'semantic',
  similarityThreshold: props.node.data?.similarityThreshold || 0.7,
  maxResults: props.node.data?.maxResults || 5,
  useCache: props.node.data?.useCache || true,
  includeMetadata: props.node.data?.includeMetadata || false,
  metadataFields: props.node.data?.metadataFields || [],
  includeContext: props.node.data?.includeContext || false,
  contextLength: props.node.data?.contextLength || 200
})

// 可用知识库列表（示例数据）
const availableKnowledgeBases = ref([
  { id: '1', name: '产品知识库' },
  { id: '2', name: '技术文档库' },
  { id: '3', name: '常见问题库' }
])

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

function addMetadataField() {
  nodeData.value.metadataFields.push({ name: '' })
  updateNode()
}

function removeMetadataField(index: number) {
  nodeData.value.metadataFields.splice(index, 1)
  updateNode()
}
</script>

<template>
  <div class="knowledge-node-detail">
    <div class="form-group">
      <label>知识库选择</label>
      <select v-model="nodeData.knowledgeBaseId" @change="updateNode">
        <option value="">请选择知识库</option>
        <option v-for="kb in availableKnowledgeBases" :key="kb.id" :value="kb.id">
          {{ kb.name }}
        </option>
      </select>
    </div>

    <div class="form-group">
      <label>检索方式</label>
      <select v-model="nodeData.searchMethod" @change="updateNode">
        <option value="semantic">语义检索</option>
        <option value="keyword">关键词检索</option>
        <option value="hybrid">混合检索</option>
      </select>
    </div>

    <div class="form-group">
      <label>检索参数</label>
      <div class="search-params">
        <div class="param-item">
          <label>相似度阈值</label>
          <input
            type="range"
            v-model="nodeData.similarityThreshold"
            @input="updateNode"
            min="0"
            max="1"
            step="0.01"
          >
          <span class="threshold-value">{{ nodeData.similarityThreshold }}</span>
        </div>
        <div class="param-item">
          <label>返回结果数</label>
          <input
            type="number"
            v-model="nodeData.maxResults"
            @input="updateNode"
            min="1"
            max="10"
          >
        </div>
      </div>
    </div>

    <div class="form-group">
      <label>高级设置</label>
      <div class="advanced-settings">
        <label class="checkbox-label">
          <input
            type="checkbox"
            v-model="nodeData.useCache"
            @change="updateNode"
          />
          使用缓存
        </label>
        <label class="checkbox-label">
          <input
            type="checkbox"
            v-model="nodeData.includeMetadata"
            @change="updateNode"
          />
          包含元数据
        </label>
        <div v-if="nodeData.includeMetadata" class="metadata-settings">
          <div class="setting-item">
            <label>元数据字段</label>
            <div class="metadata-fields">
              <div v-for="(field, index) in nodeData.metadataFields" :key="index" class="field-item">
                <input
                  type="text"
                  v-model="field.name"
                  @input="updateNode"
                  placeholder="字段名"
                >
                <button @click="removeMetadataField(index)" class="remove-field">×</button>
              </div>
              <button @click="addMetadataField" class="add-field">+ 添加字段</button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="form-group">
      <label>输出设置</label>
      <div class="output-settings">
        <label class="checkbox-label">
          <input
            type="checkbox"
            v-model="nodeData.includeContext"
            @change="updateNode"
          />
          包含上下文
        </label>
        <div v-if="nodeData.includeContext" class="setting-item">
          <label>上下文长度</label>
          <input
            type="number"
            v-model="nodeData.contextLength"
            @input="updateNode"
            min="1"
            max="1000"
          >
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.knowledge-node-detail {
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

select, input[type="text"], input[type="number"], input[type="range"] {
  width: 100%;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.search-params {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.param-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.threshold-value {
  text-align: right;
  color: #666;
  font-size: 14px;
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

.metadata-settings {
  margin-top: 8px;
}

.metadata-fields {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.field-item {
  display: flex;
  gap: 8px;
}

.field-item input {
  flex: 1;
}

.remove-field {
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

.add-field {
  padding: 8px;
  border: 1px dashed #ddd;
  border-radius: 4px;
  background: none;
  cursor: pointer;
  color: #666;
}

.add-field:hover {
  border-color: #4a90e2;
  color: #4a90e2;
}

.output-settings {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 12px;
  background: #f8f9fa;
  border-radius: 4px;
}

.setting-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
  margin-top: 8px;
}
</style> 