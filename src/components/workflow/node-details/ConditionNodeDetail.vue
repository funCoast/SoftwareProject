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
  conditionType: props.node.data?.conditionType || 'expression',
  expression: props.node.data?.expression || '',
  leftOperand: props.node.data?.leftOperand || '',
  operator: props.node.data?.operator || '==',
  rightOperand: props.node.data?.rightOperand || '',
  customCode: props.node.data?.customCode || '',
  trueLabel: props.node.data?.trueLabel || '是',
  falseLabel: props.node.data?.falseLabel || '否',
  caseSensitive: props.node.data?.caseSensitive || false,
  logResult: props.node.data?.logResult || false
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

<template>
  <div class="condition-node-detail">
    <div class="form-group">
      <label>条件类型</label>
      <select v-model="nodeData.conditionType" @change="updateNode">
        <option value="expression">表达式</option>
        <option value="comparison">比较</option>
        <option value="custom">自定义</option>
      </select>
    </div>

    <div v-if="nodeData.conditionType === 'expression'" class="form-group">
      <label>表达式</label>
      <textarea
        v-model="nodeData.expression"
        @input="updateNode"
        placeholder="输入条件表达式..."
        rows="4"
      ></textarea>
    </div>

    <div v-if="nodeData.conditionType === 'comparison'" class="form-group">
      <label>比较设置</label>
      <div class="comparison-settings">
        <div class="comparison-item">
          <input
            type="text"
            v-model="nodeData.leftOperand"
            @input="updateNode"
            placeholder="左操作数"
          >
          <select v-model="nodeData.operator" @change="updateNode">
            <option value="==">等于</option>
            <option value="!=">不等于</option>
            <option value=">">大于</option>
            <option value="<">小于</option>
            <option value=">=">大于等于</option>
            <option value="<=">小于等于</option>
            <option value="contains">包含</option>
            <option value="startsWith">开头是</option>
            <option value="endsWith">结尾是</option>
          </select>
          <input
            type="text"
            v-model="nodeData.rightOperand"
            @input="updateNode"
            placeholder="右操作数"
          >
        </div>
      </div>
    </div>

    <div v-if="nodeData.conditionType === 'custom'" class="form-group">
      <label>自定义代码</label>
      <textarea
        v-model="nodeData.customCode"
        @input="updateNode"
        placeholder="输入自定义条件判断代码..."
        rows="6"
      ></textarea>
    </div>

    <div class="form-group">
      <label>分支标签</label>
      <div class="branch-labels">
        <div class="branch-item">
          <span class="branch-name">真分支</span>
          <input
            type="text"
            v-model="nodeData.trueLabel"
            @input="updateNode"
            placeholder="真分支标签"
          >
        </div>
        <div class="branch-item">
          <span class="branch-name">假分支</span>
          <input
            type="text"
            v-model="nodeData.falseLabel"
            @input="updateNode"
            placeholder="假分支标签"
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
            v-model="nodeData.caseSensitive"
            @change="updateNode"
          />
          区分大小写
        </label>
        <label class="checkbox-label">
          <input
            type="checkbox"
            v-model="nodeData.logResult"
            @change="updateNode"
          />
          记录判断结果
        </label>
      </div>
    </div>
  </div>
</template>

<style scoped>
.condition-node-detail {
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

.comparison-settings {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.comparison-item {
  display: flex;
  gap: 8px;
}

.comparison-item input {
  flex: 1;
}

.comparison-item select {
  width: 120px;
}

.branch-labels {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.branch-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.branch-name {
  width: 60px;
  color: #666;
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
</style> 