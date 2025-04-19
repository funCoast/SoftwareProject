<template>
  <div class="plugin-container">
    <div class="form-group">
      <label>时间戳</label>
      <input type="number" v-model="config.timestamp" class="form-control" placeholder="请输入时间戳">
    </div>

    <div class="form-group">
      <label>时间戳单位</label>
      <select v-model="config.unit" class="form-control">
        <option value="seconds">秒</option>
        <option value="milliseconds">毫秒</option>
      </select>
    </div>

    <div class="form-group">
      <label>目标时区</label>
      <select v-model="config.timezone" class="form-control">
        <option value="UTC">UTC</option>
        <option value="Asia/Shanghai">Asia/Shanghai</option>
        <option value="America/New_York">America/New_York</option>
        <option value="Europe/London">Europe/London</option>
      </select>
    </div>

    <div class="form-group">
      <label>输出格式</label>
      <select v-model="config.format" class="form-control">
        <option value="YYYY-MM-DD HH:mm:ss">YYYY-MM-DD HH:mm:ss</option>
        <option value="YYYY/MM/DD HH:mm:ss">YYYY/MM/DD HH:mm:ss</option>
        <option value="DD/MM/YYYY HH:mm:ss">DD/MM/YYYY HH:mm:ss</option>
        <option value="MM/DD/YYYY HH:mm:ss">MM/DD/YYYY HH:mm:ss</option>
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

interface TimestampTransformConfig extends TimePluginConfig {
  unit: 'seconds' | 'milliseconds'
  timestamp: number
}

const props = defineProps<{
  node: any
}>()

const emit = defineEmits<{
  (e: 'update:node', node: any): void
  (e: 'run-result', result: PluginResult): void
}>()

const config = ref<TimestampTransformConfig>({
  timestamp: 0,
  unit: 'seconds',
  timezone: 'UTC',
  format: 'YYYY-MM-DD HH:mm:ss'
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
    if (!config.value.timestamp) {
      throw new Error('请输入时间戳')
    }

    let time = dayjs.unix(0)
    if (config.value.unit === 'seconds') {
      time = dayjs.unix(config.value.timestamp)
    } else {
      time = dayjs(config.value.timestamp)
    }

    const formattedTime = time.tz(config.value.timezone).format(config.value.format)
    
    const pluginResult = {
      success: true,
      data: formattedTime
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