<template>
  <div class="plugin-container">
    <div class="form-group">
      <label>输入时间</label>
      <input type="datetime-local" v-model="config.date" class="form-control">
    </div>

    <div class="form-group">
      <label>时区</label>
      <select v-model="config.timezone" class="form-control">
        <option value="UTC">UTC</option>
        <option value="Asia/Shanghai">Asia/Shanghai</option>
        <option value="America/New_York">America/New_York</option>
        <option value="Europe/London">Europe/London</option>
      </select>
    </div>

    <div class="form-group">
      <label>时间戳单位</label>
      <select v-model="config.unit" class="form-control">
        <option value="seconds">秒</option>
        <option value="milliseconds">毫秒</option>
      </select>
    </div>

    <div v-if="result" class="result-panel">
      <div class="result-header">运行结果：</div>
      <div class="result-content">
        {{ result.data }}
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { TimePluginConfig, PluginResult } from '@/types/plugins'
import dayjs from 'dayjs'
import utc from 'dayjs/plugin/utc'
import timezone from 'dayjs/plugin/timezone'

dayjs.extend(utc)
dayjs.extend(timezone)

interface TimestampConfig extends TimePluginConfig {
  unit: 'seconds' | 'milliseconds'
}

const props = defineProps<{
  node: any
}>()

const emit = defineEmits<{
  (e: 'update:node', node: any): void
  (e: 'run-result', result: PluginResult): void
}>()

const config = ref<TimestampConfig>({
  date: dayjs().format('YYYY-MM-DDTHH:mm'),
  timezone: 'UTC',
  unit: 'seconds'
})

const result = ref<PluginResult | null>(null)

// 监听配置变化，更新节点数据
watch(config, (newConfig) => {
  emit('update:node', {
    ...props.node,
    data: { ...newConfig }
  })
}, { deep: true })

// 运行插件
async function run(): Promise<PluginResult> {
  try {
    if (!config.value.date) {
      throw new Error('请输入时间')
    }

    const time = dayjs.tz(config.value.date, config.value.timezone)
    const timestamp = config.value.unit === 'seconds' 
      ? time.unix()
      : time.valueOf()
    
    const pluginResult = {
      success: true,
      data: timestamp
    }
    result.value = pluginResult
    return pluginResult
  } catch (error) {
    const errorResult = {
      success: false,
      data: null,
      error: error instanceof Error ? error.message : '时间戳转换失败'
    }
    result.value = errorResult
    return errorResult
  }
}

// 暴露run方法给父组件
defineExpose({ run })
</script>

<style scoped>
.plugin-container {
  padding: 16px;
}

.form-group {
  margin-bottom: 16px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
  color: #2c3e50;
}

.form-control {
  width: 100%;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
}

.result-panel {
  margin-top: 20px;
  padding: 12px;
  background: #f8f9fa;
  border-radius: 4px;
}

.result-header {
  font-weight: 500;
  margin-bottom: 8px;
  color: #2c3e50;
}

.result-content {
  font-family: monospace;
  white-space: pre-wrap;
  color: #3498db;
}
</style> 