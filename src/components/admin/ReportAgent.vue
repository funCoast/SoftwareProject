<script setup lang="ts">
import axios from 'axios'
import { ref, onMounted, computed } from 'vue'
import { ElMessage } from 'element-plus'

const reportList = ref<{
  report_id: number
  agent_id: number
  agent_name: string
  reporter: string
  reason: string
  is_processed: boolean
  process_result: string
  processed_by: string
  report_time: string
  processed_time: string
  decision?: string // 用于前端选择处理结果
}[]>([])

const adminId = localStorage.getItem('LingXi_uid')  // 管理员ID
const searchQuery = ref('')

const filteredReports = computed(() => {
  if (!searchQuery.value) return reportList.value
  const query = searchQuery.value.toLowerCase()
  return reportList.value.filter(report => 
    report.agent_name.toLowerCase().includes(query) ||
    report.reporter.toLowerCase().includes(query) ||
    report.reason.toLowerCase().includes(query) ||
    (report.process_result && report.process_result.toLowerCase().includes(query))
  )
})

const decisionOptions = [
  { value: '举报有效，已处理', label: '举报有效，已处理' },
  { value: '举报无效，驳回', label: '举报无效，驳回' },
  { value: '其他', label: '其他' }
]

async function fetchReports() {
  try {
    const res = await axios.get('/admin/getAgentReports')
    if (res.data.code === 0) {
      reportList.value = res.data.reports.map((r: any) => ({
        ...r,
        decision: ''  // 初始化选择框
      }))
    } else {
      ElMessage.error('获取举报记录失败：' + res.data.message)
    }
  } catch (err) {
    console.error(err)
    ElMessage.error('获取失败')
  }
}

async function processReport(reportId: number, result: string) {
  try {
    const res = await axios.post('/admin/processAgentReport', {
      report_id: reportId,
      admin_id: adminId,
      result: result
    })
    if (res.data.code === 0) {
      if (result === '举报有效，已处理') {
        ElMessage.success('下架该智能体成功！')
      } else {
        ElMessage.success('处理成功')
      }
      await fetchReports()
    } else {
      ElMessage.error('处理失败：' + res.data.message)
    }
  } catch (err) {
    console.error(err)
    ElMessage.error('网络错误，处理失败')
  }
}

onMounted(() => {
  fetchReports()
})
</script>

<template>
  <div class="report-agent">
    <div class="section-header">
      <h2>智能体举报处理</h2>
      <div class="header-actions">
        <el-input
          placeholder="搜索举报..."
          prefix-icon="Search"
          class="search-input"
          v-model="searchQuery"
        />
        <el-button type="primary">
          <img src="https://api.iconify.design/material-symbols:refresh.svg" class="action-icon" />
          刷新
        </el-button>
      </div>
    </div>

    <div class="stats-cards">
      <div class="stat-card">
        <div class="stat-icon">
          <img src="https://api.iconify.design/material-symbols:report.svg" alt="total" />
        </div>
        <div class="stat-info">
          <h3>总举报数</h3>
          <p>{{ reportList.length }}</p>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon warning">
          <img src="https://api.iconify.design/material-symbols:pending.svg" alt="pending" />
        </div>
        <div class="stat-info">
          <h3>待处理</h3>
          <p>{{ reportList.filter(r => !r.is_processed).length }}</p>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon success">
          <img src="https://api.iconify.design/material-symbols:task-alt.svg" alt="processed" />
        </div>
        <div class="stat-info">
          <h3>已处理</h3>
          <p>{{ reportList.filter(r => r.is_processed).length }}</p>
        </div>
      </div>
    </div>

    <div class="table-card">
      <el-table 
        :data="filteredReports" 
        stripe 
        style="width: 100%" 
        v-loading="!reportList.length"
      >
        <el-table-column prop="report_id" label="ID" width="60" />
        <el-table-column prop="agent_name" label="被举报智能体" />
        <el-table-column prop="reporter" label="举报人" />
        <el-table-column prop="reason" label="举报理由" show-overflow-tooltip />
        <el-table-column prop="report_time" label="举报时间" width="160" />
        <el-table-column label="处理状态" width="120">
          <template #default="{ row }">
            <el-tag :type="row.is_processed ? 'success' : 'warning'">
              {{ row.is_processed ? '已处理' : '未处理' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="300" fixed="right">
          <template #default="{ row }">
            <div v-if="!row.is_processed" class="row-op">
              <el-select v-model="row.decision" placeholder="选择处理结果" style="width: 160px">
                <el-option
                  v-for="opt in decisionOptions"
                  :key="opt.value"
                  :label="opt.label"
                  :value="opt.value"
                />
              </el-select>
              <el-button
                type="primary"
                size="small"
                :disabled="!row.decision"
                @click="processReport(row.report_id, row.decision!)"
              >
                提交处理
              </el-button>
            </div>
            <div v-else class="process-info">
              <span class="process-result">{{ row.process_result }}</span>
              <span class="process-detail">{{ row.processed_by }} 于 {{ row.processed_time }}</span>
            </div>
          </template>
        </el-table-column>
      </el-table>
    </div>
  </div>
</template>

<style scoped>
.report-agent {
  width: 100%;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.section-header h2 {
  margin: 0;
  font-size: 24px;
  color: #2c3e50;
}

.header-actions {
  display: flex;
  gap: 12px;
}

.search-input {
  width: 240px;
}

.action-icon {
  width: 18px;
  height: 18px;
  margin-right: 4px;
  vertical-align: middle;
}

.stats-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 20px;
  margin-bottom: 24px;
}

.stat-card {
  background: white;
  border-radius: 12px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  background: #ecf5ff;
  display: flex;
  align-items: center;
  justify-content: center;
}

.stat-icon img {
  width: 28px;
  height: 28px;
  color: #409EFF;
}

.stat-icon.warning {
  background: #fdf6ec;
}

.stat-icon.warning img {
  color: #e6a23c;
}

.stat-icon.success {
  background: #f0f9eb;
}

.stat-icon.success img {
  color: #67c23a;
}

.stat-info h3 {
  margin: 0;
  font-size: 14px;
  color: #666;
}

.stat-info p {
  margin: 4px 0 0;
  font-size: 24px;
  font-weight: bold;
  color: #2c3e50;
}

.table-card {
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.row-op {
  display: flex;
  gap: 12px;
  align-items: center;
}

.process-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.process-result {
  color: #2c3e50;
  font-weight: 500;
}

.process-detail {
  color: #909399;
  font-size: 12px;
}

:deep(.el-table) {
  border-radius: 8px;
  overflow: hidden;
}

:deep(.el-table__header) {
  background-color: #f5f7fa;
}

:deep(.el-table__header th) {
  background-color: #f5f7fa;
  color: #606266;
  font-weight: 600;
}

:deep(.el-table__row) {
  transition: all 0.3s ease;
}

:deep(.el-table__row:hover) {
  background-color: #f5f7fa;
}
</style>