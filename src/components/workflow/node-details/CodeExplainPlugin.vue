<template>
  <div class="code-explain-node-detail">
    <div class="form-group">
      <label>代码输入</label>
      <textarea
          v-model="nodeData.code"
          @input="updateNode"
          placeholder="请输入需要解释的代码"
          rows="6"
      ></textarea>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'

const props = defineProps<{
  node: any
}>()

const emit = defineEmits<{
  (e: 'update:node', node: any): void
}>()

const nodeData = ref({
  code: props.node.data?.code || '',
  language: props.node.data?.language || 'javascript',
  detailLevel: props.node.data?.detailLevel || 'detailed',
  outputLanguage: props.node.data?.outputLanguage || 'zh',
  includeTimeComplexity: props.node.data?.includeTimeComplexity || false,
  includeSpaceComplexity: props.node.data?.includeSpaceComplexity || false,
  includeExamples: props.node.data?.includeExamples || true,
  includeAlternatives: props.node.data?.includeAlternatives || false,
  outputFormat: {
    markdown: props.node.data?.outputFormat?.markdown || true,
    html: props.node.data?.outputFormat?.html || false,
    plainText: props.node.data?.outputFormat?.plainText || false
  }
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
</script>

<style scoped>
.code-explain-node-detail {
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

select, textarea {
  width: 100%;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', 'Consolas', monospace;
}

textarea {
  resize: vertical;
  min-height: 120px;
  line-height: 1.4;
}

.checkbox-label input[type="checkbox"] {
  width: 16px;
  height: 16px;
}

select:focus, textarea:focus {
  outline: none;
  border-color: #4a90e2;
  box-shadow: 0 0 0 2px rgba(74, 144, 226, 0.2);
}
</style>