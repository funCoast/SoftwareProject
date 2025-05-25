<script setup lang="ts">
import { ref, onMounted, nextTick, computed, onUnmounted } from 'vue'
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
const searchQuery = ref('')

const filteredUsers = computed(() => {
  if (!searchQuery.value) return users.value
  const query = searchQuery.value.toLowerCase()
  return users.value.filter(user => 
    user.name.toLowerCase().includes(query) ||
    user.email.toLowerCase().includes(query) ||
    user.uid.toString().includes(query)
  )
})

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
let myChart: any = null

function initChart() {
  nextTick(() => {
    const chartDom = document.getElementById('loginChart')
    if (chartDom) {
      if (myChart) {
        myChart.dispose()
      }
      myChart = echarts.init(chartDom)
      const option = {
        title: {
          text: '最近七日用户登录次数',
          left: 'center'
        },
        tooltip: {
          trigger: 'axis'
        },
        grid: {
          top: 60,
          right: 30,
          bottom: 30,
          left: 40,
          containLabel: true
        },
        xAxis: {
          type: 'category',
          data: dates.value,
          axisLabel: {
            formatter: (value: string) => value.slice(5) // 只显示月-日
          }
        },
        yAxis: {
          type: 'value',
          minInterval: 1
        },
        series: [
          {
            name: '登录次数',
            data: loginData.value,
            type: 'line',
            smooth: true,
            lineStyle: {
              width: 3,
              color: '#4FAFFF'
            },
            itemStyle: {
              color: '#4FAFFF'
            },
            areaStyle: {
              color: {
                type: 'linear',
                x: 0,
                y: 0,
                x2: 0,
                y2: 1,
                colorStops: [
                  { offset: 0, color: 'rgba(79, 175, 255, 0.3)' },
                  { offset: 1, color: 'rgba(79, 175, 255, 0.1)' }
                ]
              }
            }
          }
        ]
      }
      myChart.setOption(option)

      // 添加窗口大小变化的监听
      window.addEventListener('resize', () => {
        myChart.resize()
      })
    }
  })
}

onMounted(() => {
  fetchUsers()
  initChart()
})

// 组件卸载时清理
onUnmounted(() => {
  if (myChart) {
    myChart.dispose()
    window.removeEventListener('resize', () => {
      myChart.resize()
    })
  }
})
</script>

<template>
  <div class="user-manage">
    <div class="header">
      <h2>用户管理</h2>
      <div class="header-actions">
        <el-input
          v-model="searchQuery"
          placeholder="搜索用户..."
          prefix-icon="Search"
          class="search-input"
          clearable
        />
        <el-button type="primary" @click="fetchUsers">
          <img src="https://api.iconify.design/material-symbols:refresh.svg" class="action-icon" />
          刷新
        </el-button>
      </div>
    </div>
    
    <div class="stats-cards">
      <div class="stat-card">
        <div class="stat-icon">
          <img src="https://api.iconify.design/material-symbols:group.svg" alt="total users" />
        </div>
        <div class="stat-info">
          <h3>总用户数</h3>
          <p>{{ users.length }}</p>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon warning">
          <img src="https://api.iconify.design/material-symbols:gpp-bad.svg" alt="banned users" />
        </div>
        <div class="stat-info">
          <h3>封禁用户</h3>
          <p>{{ users.filter(u => !u.can_log).length }}</p>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon danger">
          <img src="https://api.iconify.design/material-symbols:block.svg" alt="restricted users" />
        </div>
        <div class="stat-info">
          <h3>发布受限</h3>
          <p>{{ users.filter(u => !u.can_post).length }}</p>
        </div>
      </div>
    </div>

    <div id="loginChart" class="chart-card"></div>

    <el-table
      v-loading="loading"
      :data="filteredUsers"
      style="width: 100%"
      border
      class="user-table"
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
          <div v-if="row.can_log && row.can_post">
            <el-button
              type="danger"
              size="small"
              @click="banUser(row.uid, 'account')"
            >
              封禁账号
            </el-button>
            <el-button
              type="warning"
              size="small"
              @click="banUser(row.uid, 'post')"
            >
              限制发布
            </el-button>
          </div>
          <el-button
            v-else
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
  width: 100%;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.header h2 {
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

.stat-icon.danger {
  background: #fef0f0;
}

.stat-icon.danger img {
  color: #f56c6c;
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

.chart-card {
  background: white;
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 24px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  height: 400px;
}

#loginChart {
  width: 100%;
  height: 100%;
}

.user-table {
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.ban-time-input {
  display: flex;
  gap: 8px;
}

:deep(.el-input-number) {
  width: 100px;
}

:deep(.el-select) {
  width: 80px;
}
</style>
