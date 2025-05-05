<template>
  <div class="current-time-plugin">
    <div class="form-group">
      <label>时区选择</label>
      <div class="timezone-selector">
        <div class="search-box">
          <input
            type="text"
            v-model="searchQuery"
            placeholder="搜索时区..."
            @focus="handleSearchFocus"
          />
        </div>

        <div class="region-selector" v-if="!searchQuery">
          <div
            v-for="group in groupedTimezones"
            :key="group.region"
            class="region-item"
            :class="{ active: selectedRegion === group.region }"
            @click="handleRegionSelect(group.region)"
          >
            {{ group.region }}
          </div>
        </div>

        <div class="timezone-list" v-if="showTimezoneList">
          <template v-if="searchQuery">
            <div
              v-for="tz in filteredTimezones"
              :key="tz.value"
              class="timezone-item"
              :class="{ active: nodeData.timezone === tz.value }"
              @click="selectTimezone(tz)"
            >
              <div class="timezone-name">{{ tz.label }}</div>
              <div class="timezone-offset">{{ tz.offset }}</div>
            </div>
          </template>
          <template v-else-if="selectedRegion">
            <div
              v-for="tz in currentRegionTimezones"
              :key="tz.value"
              class="timezone-item"
              :class="{ active: nodeData.timezone === tz.value }"
              @click="selectTimezone(tz)"
            >
              <div class="timezone-name">{{ tz.label }}</div>
              <div class="timezone-offset">{{ tz.offset }}</div>
            </div>
          </template>
        </div>

        <div class="selected-timezone" v-if="!showTimezoneList">
          {{ nodeData.timezone }}
        </div>
      </div>
    </div>

    <div class="form-group">
      <label>时间格式</label>
      <div class="format-selector">
        <select v-model="nodeData.format" @change="updateNode">
          <option value="YYYY-MM-DD HH:mm:ss">YYYY-MM-DD HH:mm:ss</option>
          <option value="YYYY/MM/DD HH:mm:ss">YYYY/MM/DD HH:mm:ss</option>
          <option value="DD/MM/YYYY HH:mm:ss">DD/MM/YYYY HH:mm:ss</option>
          <option value="MM/DD/YYYY HH:mm:ss">MM/DD/YYYY HH:mm:ss</option>
          <option value="YYYY-MM-DD">YYYY-MM-DD</option>
          <option value="HH:mm:ss">HH:mm:ss</option>
          <option value="custom">自定义格式</option>
        </select>
        <input
          v-if="nodeData.format === 'custom'"
          type="text"
          v-model="nodeData.customFormat"
          placeholder="例如：YYYY-MM-DD HH:mm:ss.SSS Z"
          @input="updateNode"
          class="custom-format-input"
        />
      </div>
      <div class="format-preview" v-if="previewTime">
        预览: {{ previewTime }}
      </div>
    </div>

    <div class="form-group">
      <label>高级选项</label>
      <div class="advanced-settings">
        <label class="checkbox-label">
          <input
            type="checkbox"
            v-model="nodeData.includeOffset"
            @change="updateNode"
          />
          包含时区偏移
        </label>
        <label class="checkbox-label">
          <input
            type="checkbox"
            v-model="nodeData.includeTimestamp"
            @change="updateNode"
          />
          包含时间戳
        </label>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import dayjs from 'dayjs'
import utc from 'dayjs/plugin/utc'
import timezone from 'dayjs/plugin/timezone'

dayjs.extend(utc)
dayjs.extend(timezone)

const props = defineProps<{
  node: any
}>()

const emit = defineEmits<{
  (e: 'update:node', node: any): void
}>()

const nodeData = ref({
  timezone: props.node.data?.timezone || 'Asia/Shanghai',
  format: props.node.data?.format || 'YYYY-MM-DD HH:mm:ss',
  customFormat: props.node.data?.customFormat || '',
  includeOffset: props.node.data?.includeOffset || false,
  includeTimestamp: props.node.data?.includeTimestamp || false
})

interface Timezone {
  value: string
  label: string
  offset: string
  region: string
}

// 按区域组织时区数据
const timezoneData: Record<string, Timezone[]> = {
  'Africa': [
    { value: 'Africa/Abidjan', label: 'Abidjan', offset: 'UTC+0', region: 'Africa' },
    { value: 'Africa/Accra', label: 'Accra', offset: 'UTC+0', region: 'Africa' },
    { value: 'Africa/Addis_Ababa', label: 'Addis Ababa', offset: 'UTC+3', region: 'Africa' },
    // ... 更多非洲时区
  ],
  'America': [
    { value: 'America/Adak', label: 'Adak', offset: 'UTC-10', region: 'America' },
    { value: 'America/Anchorage', label: 'Anchorage', offset: 'UTC-9', region: 'America' },
    // ... 更多美洲时区
  ],
  'Asia': [
    { value: 'Asia/Aden', label: 'Aden', offset: 'UTC+3', region: 'Asia' },
    { value: 'Asia/Almaty', label: 'Almaty', offset: 'UTC+6', region: 'Asia' },
    // ... 更多亚洲时区
  ],
  'Europe': [
    { value: 'Europe/Amsterdam', label: 'Amsterdam', offset: 'UTC+1', region: 'Europe' },
    { value: 'Europe/Andorra', label: 'Andorra', offset: 'UTC+1', region: 'Europe' },
    // ... 更多欧洲时区
  ],
  'Pacific': [
    { value: 'Pacific/Apia', label: 'Apia', offset: 'UTC+13', region: 'Pacific' },
    { value: 'Pacific/Auckland', label: 'Auckland', offset: 'UTC+12', region: 'Pacific' },
    // ... 更多太平洋时区
  ],
  // ... 其他区域
}

const searchQuery = ref('')
const selectedRegion = ref<string>('')
const showTimezoneList = ref(false)

// 获取所有时区列表
const allTimezones = computed(() => {
  return Object.values(timezoneData).flat()
})

// 按区域分组的时区
const groupedTimezones = computed(() => {
  return Object.entries(timezoneData).map(([region, zones]) => ({
    region,
    zones: zones.map(tz => ({
      ...tz,
      displayName: `${tz.label} (${tz.offset})`
    }))
  }))
})

// 搜索结果
const filteredTimezones = computed(() => {
  if (!searchQuery.value) return []
  const query = searchQuery.value.toLowerCase()
  return allTimezones.value.filter(tz =>
    tz.label.toLowerCase().includes(query) ||
    tz.value.toLowerCase().includes(query) ||
    tz.offset.toLowerCase().includes(query)
  ).map(tz => ({
    ...tz,
    displayName: `${tz.label} (${tz.offset})`
  }))
})

// 当前选中区域的时区
const currentRegionTimezones = computed(() => {
  if (!selectedRegion.value) return []
  return timezoneData[selectedRegion.value] || []
})

const previewTime = computed(() => {
  const format = nodeData.value.format === 'custom'
    ? nodeData.value.customFormat
    : nodeData.value.format

  let formatted = dayjs().tz(nodeData.value.timezone).format(format)

  if (nodeData.value.includeOffset) {
    formatted += ` (${dayjs().tz(nodeData.value.timezone).format('Z')})`
  }

  if (nodeData.value.includeTimestamp) {
    formatted += ` [${Date.now()}]`
  }

  return formatted
})

function filterTimezones() {
  // 搜索功能已通过计算属性实现
}

function selectTimezone(tz: Timezone) {
  nodeData.value.timezone = tz.value
  searchQuery.value = ''
  showTimezoneList.value = false
  updateNode()
}

function handleRegionSelect(region: string) {
  selectedRegion.value = region
  showTimezoneList.value = true
}

function handleSearchFocus() {
  showTimezoneList.value = true
  selectedRegion.value = ''
}

function handleClickOutside(event: MouseEvent) {
  const target = event.target as HTMLElement
  if (!target.closest('.timezone-selector')) {
    showTimezoneList.value = false
  }
}

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

// 监听数据变化
watch(nodeData, () => {
  updateNode()
}, { deep: true })

// 初始化时更新节点
onMounted(() => {
  updateNode()
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script>

<style scoped>
.current-time-plugin {
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

.timezone-selector {
  position: relative;
}

.search-box input {
  width: 100%;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.region-selector {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(100px, 1fr));
  gap: 8px;
  margin-top: 8px;
}

.region-item {
  padding: 8px;
  text-align: center;
  background: #f8f9fa;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.region-item:hover {
  background: #e9ecef;
}

.region-item.active {
  background: #e6f7ff;
  color: #1890ff;
}

.timezone-list {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  max-height: 300px;
  overflow-y: auto;
  background: white;
  border: 1px solid #ddd;
  border-radius: 4px;
  z-index: 1000;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  margin-top: 4px;
}

.timezone-item {
  padding: 8px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  cursor: pointer;
  transition: background-color 0.2s;
}

.timezone-item:hover {
  background: #f5f5f5;
}

.timezone-item.active {
  background: #e6f7ff;
}

.selected-timezone {
  margin-top: 8px;
  padding: 8px;
  background: #f8f9fa;
  border-radius: 4px;
  color: #666;
}

select,
input[type="text"] {
  width: 100%;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
  background: white;
}

.format-selector {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.custom-format-input {
  font-family: monospace;
}

.format-preview {
  margin-top: 8px;
  padding: 8px;
  background: #f8f9fa;
  border-radius: 4px;
  font-family: monospace;
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

.checkbox-label input[type="checkbox"] {
  width: 16px;
  height: 16px;
}

select:focus,
input:focus {
  outline: none;
  border-color: #4a90e2;
  box-shadow: 0 0 0 2px rgba(74, 144, 226, 0.2);
}

::-webkit-scrollbar {
  width: 6px;
}

::-webkit-scrollbar-track {
  background: #f1f1f1;
}

::-webkit-scrollbar-thumb {
  background: #888;
  border-radius: 3px;
}

::-webkit-scrollbar-thumb:hover {
  background: #555;
}
</style>