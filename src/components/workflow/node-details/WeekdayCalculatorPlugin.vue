<script setup lang="ts">
import {computed, defineExpose, ref, watch} from 'vue'
import {getAllUpstreamNodes} from '../../../utils/getAllUpstreamNodes'
import axios from 'axios'
import dayjs from 'dayjs'

interface Input {
  id: number
  name: string
  type: string
  value?: {
    type: number
    text: string
    nodeId: number
    outputId: number
  }
}

interface Output {
  id: number
  name: string
  type: string
  value?: any
}

const props = defineProps<{ node: any, allNodes: any[]}>()
const emit = defineEmits<{ (e: 'update:node', node: any): void }>()

const allUpstreamNodes = computed(() => {
  return getAllUpstreamNodes(props.node, props.allNodes)
})

// 初始化 inputs/outputs
const inputs = ref<Input[]>(props.node.inputs?.length
    ? props.node.inputs
    : [{ id: 0, name: 'date', type: 'str', value: { type: 0, text: '', nodeId: -1, outputId: -1 } }]
)

const outputs = ref<Output[]>(props.node.outputs.length
    ? props.node.outputs
    : [{ id: 0, name: 'weekday', type: 'string', value: '' }]
)

emit('update:node', {
  ...props.node,
  inputs: inputs.value,
  outputs: outputs.value
})

watch([inputs, outputs], () => {
  const updatedNode = {
    ...props.node,
    inputs: inputs.value,
    outputs: outputs.value,
  }
  emit('update:node', updatedNode)
}, { deep: true })

const activeTab = ref(inputs.value[0].value.type === 1 ? 'upstream' : 'manual')

const showRunPanel = ref(false)
const runInputText = ref('')

function openRunPanel() {
  showRunPanel.value = true
}

const runResult = ref<{ success: boolean; message: string }>({ success: false, message: '' })
async function handleRunClick() {
  if (!dayjs(runInputText.value, 'YYYY-MM-DD', true).isValid()) {
    runResult.value = {
      success: false,
      message: '请输入正确格式的日期（YYYY-MM-DD）',
    }
    return
  }

  try {
    const response = await axios.post('/plugins/WeekdayCalculatorPlugin/execute/', {
      args: [],
      kwargs: { date: runInputText.value }
    })
    if (response.data.status === 'success') {
      runResult.value = { success: true, message: `运行成功，结果：${response.data.result.weekday}` }
    } else {
      runResult.value = { success: false, message: response.data.message || '执行失败' }
    }
  } catch (e: any) {
    runResult.value = { success: false, message: e.message || String(e) }
  }
}

function onTabChange(tab: any) {
  inputs.value[0].value.type = tab.props.name === 'upstream' ? 1 : 0
}

// 用于保持 select 的 value 绑定正确
function generateSelectValue(val: any) {
  if (val.type === 1 && val.nodeId !== -1 && val.outputId !== -1) {
    return `${val.nodeId}|${val.outputId}`
  }
  return ''
}

function onSelectChange(val: string) {
  const [nodeId, outputId] = val.split('|')
  inputs.value[0].value = {
    type: 1,
    text: '',
    nodeId: parseInt(nodeId),
    outputId: parseInt(outputId)
  }
}

defineExpose({ openRunPanel })
</script>

<template>
  <div class="plugin-container">
    <el-form label-position="top">
      <el-form-item label="输入 (date: string)">
        <el-tabs v-model="activeTab" @tab-click="onTabChange">
          <el-tab-pane label="手动输入" name="manual">
            <el-input
                placeholder="YYYY-MM-DD"
                v-model="inputs[0].value.text"
            />
          </el-tab-pane>

          <el-tab-pane label="选择上游输出" name="upstream" v-if="allUpstreamNodes.length">
            <el-select
                placeholder="选择上游输出"
                :model-value="generateSelectValue(inputs[0].value)"
                @change="onSelectChange"
                style="width: 100%"
            >
              <template v-for="node in allUpstreamNodes" :key="node.id">
                <el-option
                    v-for="(output, idx) in node.outputs"
                    :key="`${node.id}-${idx}`"
                    :label="`${node.name}: ${output.name}`"
                    :value="`${node.id}|${output.id}`"
                />
              </template>
            </el-select>
          </el-tab-pane>
        </el-tabs>
      </el-form-item>

      <el-form-item label="输出 (weekday: string)" />
    </el-form>

    <!-- 运行面板覆盖层 -->
    <div v-if="showRunPanel" class="run-panel-overlay">
      <div class="run-panel-content">
        <el-divider>运行面板</el-divider>
        <el-form label-position="top" style="margin-top:16px;">
          <el-form-item label="date: string">
            <el-input
                placeholder="请输入日期（YYYY-MM-DD）"
                v-model="runInputText"
            />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="handleRunClick">运行</el-button>
            <el-button @click="showRunPanel=false" style="margin-left:8px;">
              取消
            </el-button>
          </el-form-item>
          <el-alert
              v-if="runResult.message"
              :title="runResult.message"
              :type="runResult.success ? 'success' : 'error'"
              show-icon
          />
        </el-form>
      </div>
    </div>
  </div>
</template>

<style scoped>
.plugin-container {
  position: relative;
  padding: 16px;
}

.run-panel-overlay {
  position: absolute;
  inset: 0;
  background: rgba(0,0,0,0.3);
  z-index: 10;
  display: flex;
  justify-content: center;
  align-items: flex-start;
  padding-top: 20px;
}

.run-panel-content {
  width: 400px;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.15);
  padding: 16px;
}
</style>
