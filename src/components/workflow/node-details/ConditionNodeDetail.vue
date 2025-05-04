<script setup lang="ts">
import { ref, watch, computed } from 'vue'
import { getAllUpstreamNodes } from '../../../utils/getAllUpstreamNodes'

interface Input {
  id: number
  name: string
  type: string
  value: {
    type?: number // 1: 上游节点的输出
    nodeId?: number
    outputId?: number
    text?: string // 手动输入的内容
  }
}

interface Condition {
  variable: Input['id'] // 引用输入变量的id
  compare_value: string
  compare_type: number
}

interface Case {
  condition: Condition[]
  and_or: number // 0: or, 1: and
  next_node: number
}

const props = defineProps<{
  node: {
    id: number
    type: string
    name: string
    nextWorkflowNodeIds: number[]
    inputs: Input[]
    data: {
      case: Case[]
    }
  }
  allNodes: any[]
}>()

const emit = defineEmits<{
  (e: 'update:node', node: any): void
}>()

// 获取所有上游节点
const allUpstreamNodes = computed(() => {
  return getAllUpstreamNodes(props.node, props.allNodes)
})

// 初始化输入列表
const inputs = ref<Input[]>(props.node.inputs || [])

// 初始化条件配置
const cases = ref<Case[]>(props.node.data?.case || [])

// 比较类型选项
const compareTypes = [
  { label: '包含', value: 1 },
  { label: '不包含', value: 2 },
  { label: '开始是', value: 3 },
  { label: '结束是', value: 4 },
  { label: '是', value: 5 },
  { label: '不是', value: 6 },
  { label: '为空', value: 7 },
  { label: '不为空', value: 8 }
]

// 输入类型选项
const inputTypes = [
  { label: '字符串', value: 'string' },
  { label: '数字', value: 'number' }
]

// 添加新输入
function addInput() {
  const newId = inputs.value.length
    ? Math.max(...inputs.value.map(i => i.id)) + 1
    : 0
  
  inputs.value.push({
    id: newId,
    name: '',
    type: 'string',
    value: {
      text: ''
    }
  })
}

// 删除输入
function removeInput(id: number) {
  const index = inputs.value.findIndex(i => i.id === id)
  if (index !== -1) {
    inputs.value.splice(index, 1)
    // 同时删除相关的条件
    cases.value.forEach(case_ => {
      case_.condition = case_.condition.filter(cond => cond.variable !== id)
    })
  }
}

// 添加新的条件分支
function addCase() {
  cases.value.push({
    condition: [],
    and_or: 1,
    next_node: -1
  })
}

// 删除条件分支
function removeCase(index: number) {
  cases.value.splice(index, 1)
}

// 添加条件
function addCondition(case_: Case) {
  if (inputs.value.length === 0) {
    alert('请先添加输入变量')
    return
  }
  case_.condition.push({
    variable: inputs.value[0].id,
    compare_value: '',
    compare_type: 1
  })
}

// 删除条件
function removeCondition(case_: Case, index: number) {
  case_.condition.splice(index, 1)
}

// 生成选择器的值
function generateSelectValue(val: Input['value']): string {
  if (!val?.type || val.type !== 1) return 'manual'
  return `${val.nodeId}|${val.outputId}`
}

// 处理输入来源选择变化
function onSelectChange(val: string, input: Input) {
  if (val === 'manual') {
    input.value = {
      type: 0,
      nodeId: -1,
      outputId: -1,
      text: ''
    }
  } else {
    const [nodeId, outputId] = val.split('|').map(Number)
    input.value = {
      type: 1,
      nodeId,
      outputId,
      text: ''
    }
  }
}

function getNodeNameById(id) {
  const node = props.allNodes.find(n => n.id === id);
  return node ? node.name : `未找到名称（ID: ${id}）`;
}

// 监听变化并更新节点
watch([inputs, cases], () => {
  emit('update:node', {
    ...props.node,
    inputs: inputs.value,
    data: {
      case: cases.value
    }
  })
}, { deep: true })
</script>

<template>
  <div class="condition-node-detail">
    <!-- 输入变量配置 -->
    <div class="section">
      <div class="section-header">
        <h4>输入变量</h4>
        <el-button type="primary" size="small" @click="addInput">
          添加变量
        </el-button>
      </div>

      <div v-if="inputs.length === 0" class="empty-state">
        <p>暂无输入变量，点击"添加变量"创建</p>
      </div>

      <div v-else class="input-list">
        <div v-for="input in inputs" :key="input.id" class="input-item">
          <div class="input-row">
            <el-input
                v-model="input.name"
                placeholder="变量名称"
                size="small"
                class="name-input"
            />
            <el-select
                v-model="input.type"
                placeholder="选择类型"
                size="small"
                class="type-select"
            >
              <el-option
                  v-for="type in inputTypes"
                  :key="type.value"
                  :label="type.label"
                  :value="type.value"
              />
            </el-select>
            <el-select
                :model-value="generateSelectValue(input.value)"
                placeholder="选择来源"
                size="small"
                class="source-select"
                @change="val => onSelectChange(val, input)"
            >
              <el-option
                  label="手动输入"
                  value="manual"
              />
              <template v-for="node in allUpstreamNodes" :key="node.id">
                <el-option
                    v-for="(nodeOutput, idx) in node.outputs"
                    :key="`${node.id}-${idx}`"
                    :label="`${node.name}: ${nodeOutput.name}`"
                    :value="`${node.id}|${nodeOutput.id}`"
                />
              </template>
            </el-select>
            <el-button
                type="danger"
                size="small"
                @click="removeInput(input.id)"
                class="remove-btn"
            >
              删除
            </el-button>
          </div>

          <div v-if="input.value && !input.value.type" class="manual-input">
            <el-input
                v-model="input.value.text"
                :placeholder="`请输入${input.name}`"
                size="small"
            />
          </div>
        </div>
      </div>
    </div>

    <!-- 条件配置 -->
    <div class="section">
      <div class="section-header">
        <h4>条件配置</h4>
        <el-button type="primary" size="small" @click="addCase">
          添加分支
        </el-button>
      </div>

      <div v-if="cases.length === 0" class="empty-state">
        <p>暂无条件分支，点击"添加分支"创建</p>
      </div>

      <div v-else class="case-list">
        <div v-for="(case_, idx) in cases" :key="idx" class="case-item">
          <div class="case-header">
            <span class="case-title">{{ idx === cases.length - 1 ? 'else' : `分支 ${idx + 1}` }}</span>
            <el-button
                v-if="idx !== cases.length - 1"
                type="danger"
                size="small"
                @click="removeCase(idx)"
            >
              删除分支
            </el-button>
          </div>

          <template v-if="idx !== cases.length - 1">
            <div class="condition-list">
              <div v-for="(condition, condIdx) in case_.condition" :key="condIdx" class="condition-item">
                <el-select
                    v-model="condition.variable"
                    placeholder="选择变量"
                    size="small"
                    class="variable-select"
                >
                  <el-option
                      v-for="input in inputs"
                      :key="input.id"
                      :label="input.name"
                      :value="input.id"
                  />
                </el-select>

                <el-select
                    v-model="condition.compare_type"
                    placeholder="选择比较方式"
                    size="small"
                    class="compare-type-select"
                >
                  <el-option
                      v-for="type in compareTypes"
                      :key="type.value"
                      :label="type.label"
                      :value="type.value"
                  />
                </el-select>

                <el-input
                    v-if="![7, 8].includes(condition.compare_type)"
                    v-model="condition.compare_value"
                    placeholder="比较值"
                    size="small"
                    class="compare-value-input"
                />

                <el-button
                    type="danger"
                    size="small"
                    @click="removeCondition(case_, condIdx)"
                    class="remove-btn"
                >
                  删除
                </el-button>
              </div>

              <div class="condition-actions">
                <el-button
                    type="primary"
                    size="small"
                    plain
                    @click="addCondition(case_)"
                >
                  添加条件
                </el-button>

                <el-select
                    v-if="case_.condition.length > 1"
                    v-model="case_.and_or"
                    size="small"
                    class="and-or-select"
                >
                  <el-option label="或" :value="0" />
                  <el-option label="且" :value="1" />
                </el-select>
              </div>
            </div>
          </template>

          <div class="next-node">
            <label>下一个节点</label>
            <el-select
                v-model="case_.next_node"
                placeholder="请选择下游节点"
                size="small"
                filterable
                clearable
            >
              <el-option
                  v-for="id in props.node.nextWorkflowNodeIds"
                  :key="id"
                  :label="getNodeNameById(id)"
                  :value="id"
              />
            </el-select>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.condition-node-detail {
  padding: 16px;
}

.section {
  background: #fff;
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 24px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.section-header h4 {
  margin: 0;
  font-size: 16px;
  color: #2c3e50;
}

.empty-state {
  text-align: center;
  padding: 24px;
  background: #f8f9fa;
  border-radius: 8px;
  color: #666;
}

.input-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.input-item {
  background: #f8f9fa;
  border-radius: 8px;
  padding: 12px;
}

.input-row {
  display: flex;
  gap: 12px;
  align-items: center;
}

.name-input {
  flex: 2;
}

.type-select {
  flex: 1;
}

.source-select {
  flex: 2;
}

.manual-input {
  margin-top: 12px;
}

.case-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.case-item {
  background: #f8f9fa;
  border-radius: 8px;
  padding: 16px;
}

.case-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.case-title {
  font-weight: 500;
  color: #2c3e50;
}

.condition-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-bottom: 16px;
}

.condition-item {
  display: flex;
  gap: 12px;
  align-items: center;
}

.variable-select,
.compare-type-select {
  flex: 1;
}

.compare-value-input {
  flex: 1;
}

.condition-actions {
  display: flex;
  gap: 12px;
  align-items: center;
  margin-top: 12px;
}

.and-or-select {
  width: 100px;
}

.next-node {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.next-node label {
  font-size: 14px;
  color: #606266;
}

.remove-btn {
  flex-shrink: 0;
}
</style> 