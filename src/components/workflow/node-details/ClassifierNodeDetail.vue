<script setup lang="ts">
import { ref, watch } from 'vue'

interface WorkflowNode {
  id: string
  type: string
  position: {
    x: number
    y: number
  }
  data: {
    type?: string
    tags?: string[]
    confidenceThreshold?: number
    enableMultiLabel?: boolean
    saveHistory?: boolean
  }
}

const props = defineProps<{
  node: WorkflowNode
}>()

const emit = defineEmits<{
  (e: 'update:node', node: WorkflowNode): void
}>()

const nodeData = ref({
  type: props.node.data?.type || 'intent',
  tags: props.node.data?.tags || [],
  confidenceThreshold: props.node.data?.confidenceThreshold || 0.7,
  enableMultiLabel: props.node.data?.enableMultiLabel || false,
  saveHistory: props.node.data?.saveHistory || false
})

const newTag = ref('')

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

const addTag = () => {
  if (newTag.value.trim()) {
    nodeData.value.tags.push(newTag.value.trim())
    newTag.value = ''
    updateNode()
  }
}

const removeTag = (index: number) => {
  nodeData.value.tags.splice(index, 1)
  updateNode()
}

const updateNode = () => {
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

<template>
  <div class="classifier-node-detail">
    <div class="form-group">
      <label>分类类型</label>
      <select v-model="nodeData.type" @change="updateNode">
        <option value="intent">意图识别</option>
        <option value="topic">主题分类</option>
        <option value="sentiment">情感分析</option>
      </select>
    </div>

    <div class="form-group">
      <label>分类标签</label>
      <div class="tags-input">
        <div v-for="(tag, index) in nodeData.tags" :key="index" class="tag">
          {{ tag }}
          <button @click="removeTag(index)" class="remove-tag">×</button>
        </div>
        <input
          v-model="newTag"
          @keyup.enter="addTag"
          placeholder="输入标签后按回车"
          class="tag-input"
        />
      </div>
    </div>

    <div class="form-group">
      <label>置信度阈值</label>
      <input
        type="range"
        v-model="nodeData.confidenceThreshold"
        min="0"
        max="1"
        step="0.01"
        @input="updateNode"
      />
      <span class="threshold-value">{{ nodeData.confidenceThreshold }}</span>
    </div>

    <div class="form-group">
      <label>高级设置</label>
      <div class="advanced-settings">
        <label class="checkbox-label">
          <input
            type="checkbox"
            v-model="nodeData.enableMultiLabel"
            @change="updateNode"
          />
          允许多标签
        </label>
        <label class="checkbox-label">
          <input
            type="checkbox"
            v-model="nodeData.saveHistory"
            @change="updateNode"
          />
          保存历史记录
        </label>
      </div>
    </div>
  </div>
</template>

<style scoped>
.classifier-node-detail {
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

select, input[type="range"] {
  width: 100%;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.tags-input {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
  min-height: 40px;
}

.tag {
  display: flex;
  align-items: center;
  padding: 4px 8px;
  background: #e3f2fd;
  border-radius: 4px;
  font-size: 14px;
}

.remove-tag {
  margin-left: 8px;
  border: none;
  background: none;
  color: #666;
  cursor: pointer;
  font-size: 16px;
}

.tag-input {
  flex: 1;
  min-width: 100px;
  border: none;
  outline: none;
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
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
}
</style> 