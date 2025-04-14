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
  documentType: props.node.data?.documentType || 'text',
  extractMethod: props.node.data?.extractMethod || 'regex',
  regexPattern: props.node.data?.regexPattern || '',
  templateFields: props.node.data?.templateFields || [],
  aiInstruction: props.node.data?.aiInstruction || '',
  outputFormat: props.node.data?.outputFormat || 'json',
  includeMetadata: props.node.data?.includeMetadata || false,
  cleanText: props.node.data?.cleanText || false,
  removeWhitespace: props.node.data?.removeWhitespace || true,
  removeSpecialChars: props.node.data?.removeSpecialChars || false
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

function addTemplateField() {
  nodeData.value.templateFields.push({ name: '', pattern: '' })
  updateNode()
}

function removeTemplateField(index: number) {
  nodeData.value.templateFields.splice(index, 1)
  updateNode()
}
</script>

<template>
  <div class="extract-node-detail">
    <div class="form-group">
      <label>文档类型</label>
      <select v-model="nodeData.documentType" @change="updateNode">
        <option value="text">纯文本</option>
        <option value="pdf">PDF文档</option>
        <option value="word">Word文档</option>
        <option value="excel">Excel表格</option>
        <option value="html">HTML网页</option>
      </select>
    </div>

    <div class="form-group">
      <label>提取方式</label>
      <select v-model="nodeData.extractMethod" @change="updateNode">
        <option value="regex">正则表达式</option>
        <option value="template">模板匹配</option>
        <option value="ai">AI提取</option>
      </select>
    </div>

    <div v-if="nodeData.extractMethod === 'regex'" class="form-group">
      <label>正则表达式</label>
      <textarea
        v-model="nodeData.regexPattern"
        @input="updateNode"
        placeholder="输入正则表达式..."
        rows="3"
      ></textarea>
    </div>

    <div v-if="nodeData.extractMethod === 'template'" class="form-group">
      <label>提取模板</label>
      <div class="template-settings">
        <div v-for="(field, index) in nodeData.templateFields" :key="index" class="field-item">
          <input
            type="text"
            v-model="field.name"
            @input="updateNode"
            placeholder="字段名"
          >
          <input
            type="text"
            v-model="field.pattern"
            @input="updateNode"
            placeholder="匹配模式"
          >
          <button @click="removeTemplateField(index)" class="remove-field">×</button>
        </div>
        <button @click="addTemplateField" class="add-field">+ 添加字段</button>
      </div>
    </div>

    <div v-if="nodeData.extractMethod === 'ai'" class="form-group">
      <label>AI提取设置</label>
      <div class="ai-settings">
        <div class="setting-item">
          <label>提取指令</label>
          <textarea
            v-model="nodeData.aiInstruction"
            @input="updateNode"
            placeholder="输入AI提取指令..."
            rows="4"
          ></textarea>
        </div>
        <div class="setting-item">
          <label>输出格式</label>
          <select v-model="nodeData.outputFormat" @change="updateNode">
            <option value="json">JSON</option>
            <option value="text">文本</option>
            <option value="table">表格</option>
          </select>
        </div>
      </div>
    </div>

    <div class="form-group">
      <label>高级设置</label>
      <div class="advanced-settings">
        <label class="checkbox-label">
          <input
            type="checkbox"
            v-model="nodeData.includeMetadata"
            @change="updateNode"
          />
          包含元数据
        </label>
        <label class="checkbox-label">
          <input
            type="checkbox"
            v-model="nodeData.cleanText"
            @change="updateNode"
          />
          清理文本
        </label>
        <div v-if="nodeData.cleanText" class="setting-item">
          <label>清理选项</label>
          <div class="clean-options">
            <label class="checkbox-label">
              <input
                type="checkbox"
                v-model="nodeData.removeWhitespace"
                @change="updateNode"
              />
              移除多余空白
            </label>
            <label class="checkbox-label">
              <input
                type="checkbox"
                v-model="nodeData.removeSpecialChars"
                @change="updateNode"
              />
              移除特殊字符
            </label>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.extract-node-detail {
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

select, input[type="text"], textarea {
  width: 100%;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

textarea {
  font-family: monospace;
  resize: vertical;
}

.template-settings {
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

.ai-settings {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.setting-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
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

.clean-options {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-top: 8px;
  padding-left: 8px;
}
</style> 