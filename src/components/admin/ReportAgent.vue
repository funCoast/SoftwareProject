<script setup lang="ts">
import axios from 'axios'
import { ref, onMounted } from 'vue'
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

const adminId = sessionStorage.getItem('admin_id')  // 管理员ID

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
      result
    })
    if (res.data.code === 0) {
      ElMessage.success('处理成功')
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
  <div class="report-admin">
    <h2>智能体举报处理</h2>
    <el-table :data="reportList" stripe style="width: 100%" v-loading="!reportList.length">
      <el-table-column prop="report_id" label="ID" width="60" />
      <el-table-column prop="agent_name" label="被举报智能体" />
      <el-table-column prop="reporter" label="举报人" />
      <el-table-column prop="reason" label="举报理由" />
      <el-table-column prop="report_time" label="举报时间" width="160" />
      <el-table-column label="处理状态" width="120">
        <template #default="{ row }">
          <el-tag :type="row.is_processed ? 'success' : 'info'">
            {{ row.is_processed ? '已处理' : '未处理' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="300">
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
          <div v-else>
            {{ row.process_result }}（{{ row.processed_by }} 于 {{ row.processed_time }}）
          </div>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<style scoped>
.report-admin {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}
.row-op {
  display: flex;
  gap: 10px;
  align-items: center;
}
</style>