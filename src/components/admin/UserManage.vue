<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import axios from 'axios'
import * as echarts from 'echarts'

interface User {
  uid: number
  email: string
  name: string
  avatar: string
  can_log: boolean
  can_post: boolean
  ban_expire: string
  post_expire: string
  banTime?: number
  banTimeUnit?: '日' | '月' | '年'
}

const users = ref<User[]>([])
const loading = ref(false)
const baseImageUrl = 'http://122.9.33.84:8000'

// 获取用户列表
async function fetchUsers() {
  loading.value = true
  try {
    const response = await axios({
      method: 'get',
      url: 'admin/fetchUser'
    })
    if (response.data.code === 0) {
      users.value = response.data.users
        .filter((user: User) => user.uid !== 3 && user.uid !== 4)
        .sort((a: User, b: User) => a.uid - b.uid)
    } else {
      ElMessage.error(response.data.message)
    }
  } catch (error) {
    console.error('获取用户列表失败:', error)
    ElMessage.error('获取用户列表失败')
  } finally {
    loading.value = false
  }
}

// 封禁用户
async function banUser(uid: number, banType: string) {
  const user = users.value.find(u => u.uid === uid)
  if (!user?.banTime || !user?.banTimeUnit) {
    ElMessage.warning('请输入封禁时长')
    return
  }

  try {
    const response = await axios({
      method: 'post',
      url: 'admin/banUser',
      data: {
        uid,
        type: banType,
        time: `${user.banTime} ${user.banTimeUnit || '日'}`
      }
    })
    if (response.data.code === 0) {
      ElMessage.success('封禁成功')
      fetchUsers() // 刷新用户列表
    } else {
      ElMessage.error(response.data.message)
    }
  } catch (error) {
    console.error('封禁失败:', error)
    ElMessage.error('封禁失败')
  }
}

// 解封用户
async function unbanUser(uid: number) {
  try {
    const response = await axios({
      method: 'post',
      url: 'admin/unbanUser',
      data: { uid }
    })
    if (response.data.code === 0) {
      ElMessage.success('解封成功')
      fetchUsers() // 刷新用户列表
    } else {
      ElMessage.error(response.data.message)
    }
  } catch (error) {
    console.error('解封失败:', error)
    ElMessage.error('解封失败')
  }
}

// 格式化日期
function formatDate(dateStr: string) {
  if (!dateStr) return '无'
  return new Date(dateStr).toLocaleString()
}

// 模拟最近七天的登录次数数据
const loginData = ref([5, 3, 4, 6, 8, 7, 9])
const dates = ref([
  '2025-05-15', '2025-05-16', '2025-05-17',
  '2025-05-18', '2025-05-19', '2025-05-20', '2025-05-21'
])

// 初始化折线图
function initChart() {
  const chartDom = document.getElementById('loginChart') as HTMLDivElement
  const myChart = echarts.init(chartDom)

  const option = {
    title: {
      text: '最近七日用户登录次数'
    },
    tooltip: {
      trigger: 'axis'
    },
    xAxis: {
      type: 'category',
      data: dates.value
    },
    yAxis: {
      type: 'value'
    },
    series: [
      {
        data: loginData.value,
        type: 'line',
        smooth: true,
        lineStyle: {
          width: 3
        }
      }
    ]
  }

  myChart.setOption(option)
}

onMounted(() => {
  fetchUsers()
  initChart()
})
</script>

<template>
  <div class="user-manage">
    <div class="header">
      <h2>用户管理</h2>
    </div>
    <div id="loginChart" style="height: 400px; margin-top: 20px;"></div>
    <el-table
      v-loading="loading"
      :data="users"
      style="width: 100%"
      border
    >
      <el-table-column prop="uid" label="ID" width="80" />
      <el-table-column label="头像" width="80">
        <template #default="{ row }">
          <el-avatar :size="40" :src="baseImageUrl + row.avatar" />
        </template>
      </el-table-column>
      <el-table-column prop="name" label="用户名" width="120" />
      <el-table-column prop="email" label="邮箱" min-width="180" />
      <el-table-column label="账号状态" width="120">
        <template #default="{ row }">
          <el-tag :type="row.can_log ? 'success' : 'danger'">
            {{ row.can_log ? '正常' : '已封禁' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="发布状态" width="120">
        <template #default="{ row }">
          <el-tag :type="row.can_post ? 'success' : 'warning'">
            {{ row.can_post ? '正常' : '已限制' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="账号封禁到期" width="180">
        <template #default="{ row }">
          {{ formatDate(row.ban_expire) }}
        </template>
      </el-table-column>
      <el-table-column label="发布限制到期" width="180">
        <template #default="{ row }">
          {{ formatDate(row.post_expire) }}
        </template>
      </el-table-column>
      <el-table-column label="封禁时长" width="200">
        <template #default="{ row }">
          <div class="ban-time-input">
            <el-input-number 
              v-model="row.banTime" 
              :min="1" 
              :max="365"
              placeholder="时长"
              size="small"
            />
            <el-select 
              v-model="row.banTimeUnit" 
              placeholder="单位"
              size="small"
            >
              <el-option label="日" value="日" />
              <el-option label="月" value="月" />
              <el-option label="年" value="年" />
            </el-select>
          </div>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="200">
        <template #default="{ row }">
          <el-button
            v-if="row.can_log"
            type="danger"
            size="small"
            @click="banUser(row.uid, 'account')"
          >
            封禁账号
          </el-button>
          <el-button
            v-if="row.can_post"
            type="warning"
            size="small"
            @click="banUser(row.uid, 'post')"
          >
            限制发布
          </el-button>
          <el-button
            v-if="!row.can_log || !row.can_post"
            type="success"
            size="small"
            @click="unbanUser(row.uid)"
          >
            解封
          </el-button>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<style scoped>
.user-manage {
  padding: 20px;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.header h2 {
  margin: 0;
  color: #2c3e50;
}

#loginChart {
  width: 100%;
  height: 300px;
}

:deep(.el-table) {
  margin-top: 20px;
  border-radius: 8px;
  overflow: hidden;
}
</style>
