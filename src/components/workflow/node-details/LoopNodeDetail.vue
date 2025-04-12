<template>
  <div class="loop-node-detail">
    <div class="form-group">
      <label>循环类型</label>
      <select v-model="nodeData.loopType" @change="updateNode">
        <option value="for">For循环</option>
        <option value="while">While循环</option>
        <option value="foreach">ForEach循环</option>
      </select>
    </div>

    <div v-if="nodeData.loopType === 'for'" class="form-group">
      <label>For循环设置</label>
      <div class="for-settings">
        <div class="setting-item">
          <label>初始值</label>
          <input
            type="text"
            v-model="nodeData.initialValue"
            @input="updateNode"
            placeholder="初始值"
          >
        </div>
        <div class="setting-item">
          <label>条件</label>
          <input
            type="text"
            v-model="nodeData.condition"
            @input="updateNode"
            placeholder="循环条件"
          >
        </div>
        <div class="setting-item">
          <label>步进</label>
          <input
            type="text"
            v-model="nodeData.increment"
            @input="updateNode"
            placeholder="步进表达式"
          >
        </div>
      </div>
    </div>

    <div v-if="nodeData.loopType === 'while'" class="form-group">
      <label>While循环条件</label>
      <textarea
        v-model="nodeData.whileCondition"
        @input="updateNode"
        placeholder="输入循环条件..."
        rows="4"
      ></textarea>
    </div>

    <div v-if="nodeData.loopType === 'foreach'" class="form-group">
      <label>ForEach设置</label>
      <div class="foreach-settings">
        <div class="setting-item">
          <label>集合变量</label>
          <input
            type="text"
            v-model="nodeData.collectionVariable"
            @input="updateNode"
            placeholder="集合变量名"
          >
        </div>
        <div class="setting-item">
          <label>当前项变量</label>
          <input
            type="text"
            v-model="nodeData.currentItemVariable"
            @input="updateNode"
            placeholder="当前项变量名"
          >
        </div>
      </div>
    </div>

    <div class="form-group">
      <label>循环限制</label>
      <div class="loop-limits">
        <div class="setting-item">
          <label>最大迭代次数</label>
          <input
            type="number"
            v-model="nodeData.maxIterations"
            @input="updateNode"
            min="1"
            max="1000"
          >
        </div>
        <div class="setting-item">
          <label>超时时间(秒)</label>
          <input
            type="number"
            v-model="nodeData.timeout"
            @input="updateNode"
            min="1"
            max="3600"
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
            v-model="nodeData.breakOnError"
            @change="updateNode"
          />
          错误时中断循环
        </label>
        <label class="checkbox-label">
          <input
            type="checkbox"
            v-model="nodeData.parallelExecution"
            @change="updateNode"
          />
          并行执行
        </label>
        <div v-if="nodeData.parallelExecution" class="setting-item">
          <label>最大并行数</label>
          <input
            type="number"
            v-model="nodeData.maxParallel"
            @input="updateNode"
            min="1"
            max="10"
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
  loopType: props.node.data?.loopType || 'for',
  initialValue: props.node.data?.initialValue || '',
  condition: props.node.data?.condition || '',
  increment: props.node.data?.increment || '',
  whileCondition: props.node.data?.whileCondition || '',
  collectionVariable: props.node.data?.collectionVariable || '',
  currentItemVariable: props.node.data?.currentItemVariable || '',
  maxIterations: props.node.data?.maxIterations || 100,
  timeout: props.node.data?.timeout || 60,
  breakOnError: props.node.data?.breakOnError || true,
  parallelExecution: props.node.data?.parallelExecution || false,
  maxParallel: props.node.data?.maxParallel || 3
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
.loop-node-detail {
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

.for-settings, .foreach-settings, .loop-limits {
  display: flex;
  flex-direction: column;
  gap: 8px;
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
</style> 