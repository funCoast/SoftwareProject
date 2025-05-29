<script setup lang="ts">
import { ref, onMounted, nextTick, computed, onUnmounted, watch } from 'vue'
import { ElMessage } from 'element-plus'
import axios from 'axios'
import * as echarts from 'echarts'

const timeRange = ref(7) // 默认7天

const timeOptions = [
  { label: '最近一星期', value: 7 },
  { label: '最近一个月', value: 30 },
  { label: '最近三个月', value: 90 }
]

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
const baseImageUrl = 'http://101.201.208.165'
const searchQuery = ref('')
const selectedUser = ref<User | null>(null)

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
const loginData = ref<number[]>([]);
const dates = ref<string[]>([]);

import dayjs from 'dayjs'

async function initInfo() {
  try {
    const response = await axios.get('admin/cntInfo')
    if (response.data.code === 0) {
      const allData = response.data.data.login
      // 生成最近 N 天的日期（含今天）
      const today = dayjs()
      const recentNDates = Array.from({ length: timeRange.value }, (_, i) =>
        today.subtract(timeRange.value - 1 - i, 'day').format('YYYY-MM-DD')
      )
      // 补全数据
      dates.value = recentNDates
      loginData.value = recentNDates.map(date => allData[date] || 0)
    } else {
      ElMessage.error('获取信息失败：' + response.data.message)
    }
  } catch (error) {
    console.error('获取信息失败:', error)
    ElMessage.error('获取信息失败')
  }
  initChart()
}

watch(timeRange, () => {
  initInfo()
})


// 初始化折线图
let myChart: any = null
let resizeHandler: (() => void) | null = null

function initChart() {
  nextTick(async () => {
    // 等待一小段时间确保 DOM 完全渲染
    await new Promise(resolve => setTimeout(resolve, 100))
    
    const chartDom = document.getElementById('loginChart')
    if (chartDom) {
      if (myChart) {
        myChart.dispose()
      }
      myChart = echarts.init(chartDom)
      const option = {
        title: {
          text: '用户登录次数',
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

      // 更新 resize 处理函数
      if (resizeHandler) {
        window.removeEventListener('resize', resizeHandler)
      }
      resizeHandler = () => {
        if (myChart) {
          myChart.resize()
        }
      }
      window.addEventListener('resize', resizeHandler)
    }
  })
}

// 组件卸载时清理
onUnmounted(() => {
  if (myChart) {
    myChart.dispose()
  }
  if (resizeHandler) {
    window.removeEventListener('resize', resizeHandler)
  }
})

onMounted(() => {
  fetchUsers()
  initInfo()
})

// 图表相关数据和方法
const userCharts = ref<any[]>([])
const globalCharts = ref<any[]>([])

interface ChartData {
  [key: string]: {
    [date: string]: number
  }
}

async function fetchUserData(uid: number) {
  try {
    const response = await axios({
      method: 'get',
      url: 'admin/cntUserInfo',
      params: { uid }
    })
    if (response.data.code === 0) {
      return response.data.data
    } else {
      ElMessage.error(response.data.message)
      return null
    }
  } catch (error) {
    console.error('获取用户数据失败:', error)
    return null
  }
}

async function fetchGlobalData() {
  try {
    const response = await axios({
      method: 'get',
      url: 'admin/cntInfo'
    })
    if (response.data.code === 0) {
      return response.data.data
    } else {
      ElMessage.error(response.data.message)
      return null
    }
  } catch (error) {
    console.error('获取全局数据失败:', error)
    return null
  }
}

function initCharts(containerId: string, data: ChartData) {
  nextTick(() => {
    // 活跃度趋势图
    const activityElement = document.getElementById(`${containerId}-activity`)
    if (activityElement) {
      const activityChart = echarts.init(activityElement)
      const dates = Object.keys(data.login || {}).sort()
      const loginData = dates.map(date => data.login[date] || 0)
      const useData = dates.map(date => data.use[date] || 0)
      
      activityChart.setOption({
        title: {
          text: '用户活跃度趋势',
          top: 10,
          left: 'center'
        },
        tooltip: { trigger: 'axis' },
        legend: {
          data: ['登录次数', '使用次数'],
          top: 40
        },
        grid: {
          top: 80,
          right: 20,
          bottom: 20,
          left: 50,
          containLabel: true
        },
        xAxis: {
          type: 'category',
          data: dates,
          axisLabel: {
            formatter: (value: string) => value.slice(5) // 只显示月-日
          }
        },
        yAxis: { type: 'value' },
        series: [
          {
            name: '登录次数',
            type: 'line',
            data: loginData,
            smooth: true,
            lineStyle: { width: 3 }
          },
          {
            name: '使用次数',
            type: 'line',
            data: useData,
            smooth: true,
            lineStyle: { width: 3 }
          }
        ]
      })
    }

    // 行为分布饼图
    const behaviorElement = document.getElementById(`${containerId}-behavior`)
    if (behaviorElement) {
      const behaviorChart = echarts.init(behaviorElement)
      const behaviors = ['create', 'favorite', 'like', 'login', 'use']
      const behaviorData = behaviors.map(type => ({
        name: {
          'create': '创建',
          'favorite': '收藏',
          'like': '点赞',
          'login': '登录',
          'use': '使用'
        }[type],
        value: Object.values(data[type] || {}).reduce((a, b) => a + b, 0)
      })).filter(item => item.value > 0) // 过滤掉数值为0的行为

      behaviorChart.setOption({
        title: {
          text: '用户行为分布',
          top: 10,
          left: 'center'
        },
        tooltip: { 
          trigger: 'item',
          formatter: '{b}: {c}次 ({d}%)'
        },
        legend: {
          orient: 'horizontal',
          top: 40,
          left: 'center'
        },
        grid: {
          top: 70,
          containLabel: true
        },
        series: [{
          type: 'pie',
          radius: ['30%', '70%'],
          center: ['50%', '60%'],
          data: behaviorData,
          label: {
            show: true,
            formatter: '{b}\n{c}次\n({d}%)'
          },
          emphasis: {
            itemStyle: {
              shadowBlur: 10,
              shadowOffsetX: 0,
              shadowColor: 'rgba(0, 0, 0, 0.5)'
            }
          }
        }]
      })
    }

    // 行为对比柱状图
    const compareElement = document.getElementById(`${containerId}-compare`)
    if (compareElement) {
      const compareChart = echarts.init(compareElement)
      const allTypes = ['login', 'create', 'use', 'favorite', 'like']
      const typeNames = {
        'login': '登录',
        'create': '创建',
        'use': '使用',
        'favorite': '收藏',
        'like': '点赞'
      }
      
      compareChart.setOption({
        title: { text: '用户行为对比' },
        tooltip: { trigger: 'axis' },
        xAxis: {
          type: 'category',
          data: allTypes.map(type => typeNames[type as keyof typeof typeNames])
        },
        yAxis: { type: 'value' },
        series: [{
          type: 'bar',
          data: allTypes.map(type => 
            Object.values(data[type] || {}).reduce((a, b) => a + b, 0)
          )
        }]
      })
    }

    // 活跃时间热力图
    const heatmapElement = document.getElementById(`${containerId}-heatmap`)
    if (heatmapElement) {
      const heatmapChart = echarts.init(heatmapElement)
      const hours = Array.from({ length: 24 }, (_, i) => i)
      const days = ['周日', '周一', '周二', '周三', '周四', '周五', '周六']
      
      // 生成更合理的热力图数据
      const heatmapData = hours.map(hour => 
        days.map(day => [hour, days.indexOf(day), Math.floor(Math.random() * 5)])
      ).flat()

      heatmapChart.setOption({
        title: {
          text: '活跃时间分布',
          top: 10,
          left: 'center'
        },
        tooltip: {
          position: 'top',
          formatter: function (params: any) {
            return `${days[params.data[1]]} ${params.data[0]}:00<br>活跃度：${params.data[2]}`
          }
        },
        grid: {
          top: 80,
          bottom: 70,
          left: 90,
          right: 30
        },
        xAxis: {
          type: 'category',
          data: hours.map(h => `${h}:00`),
          splitArea: { show: true },
          axisLabel: {
            interval: 3,
            formatter: '{value}'
          }
        },
        yAxis: {
          type: 'category',
          data: days,
          splitArea: { show: true }
        },
        visualMap: {
          min: 0,
          max: 5,
          calculable: true,
          orient: 'horizontal',
          left: 'center',
          bottom: 20,
          textStyle: {
            color: '#666'
          },
          inRange: {
            color: ['#feffe6', '#fffb8f', '#ffd666', '#ffa940', '#fa541c', '#d4380d']
          }
        },
        series: [{
          name: '活跃度',
          type: 'heatmap',
          data: heatmapData,
          label: {
            show: true,
            color: function(params: any) {
              // 根据背景色的深浅来决定文字颜色
              const value = params.data[2];
              if (value === 0) return 'transparent';  // 当值为0时不显示文字
              if (value >= 4) return '#ffffff';       // 深色背景用白色
              return '#000000';                       // 浅色背景用黑色
            },
            formatter: function(params: any) {
              return params.data[2] === 0 ? '' : params.data[2]
            },
            textStyle: {
              fontWeight: 'bold',  // 加粗文字
              textShadow: '0 0 2px rgba(255, 255, 255, 0.5)'  // 添加文字阴影
            }
          },
          emphasis: {
            itemStyle: {
              shadowBlur: 10,
              shadowColor: 'rgba(250, 84, 28, 0.5)'
            }
          }
        }]
      })
    }
  })
}

// 修改初始化函数
async function initializeCharts() {
  await nextTick()
  // 获取并初始化全局数据图表
  const globalData = await fetchGlobalData()
  if (globalData) {
    initCharts('global', globalData)
  }

  // 如果有选中的用户，初始化用户数据图表
  if (selectedUser.value) {
    const userData = await fetchUserData(selectedUser.value.uid)
    if (userData) {
      initCharts('user', userData)
    }
  }
}

// 修改监听选中用户变化的逻辑
watch(() => selectedUser.value, async (newUser) => {
  if (newUser) {
    await nextTick()
    const userData = await fetchUserData(newUser.uid)
    if (userData) {
      initCharts('user', userData)
    }
  }
})

// 在组件挂载时初始化图表
onMounted(() => {
  initializeCharts()
  
  // 监听窗口大小变化，调整图表大小
  window.addEventListener('resize', () => {
    const charts = document.querySelectorAll('.chart-item')
    charts.forEach(chart => {
      const instance = echarts.getInstanceByDom(chart as HTMLElement)
      instance?.resize()
    })
  })
})

// 在组件卸载时销毁图表实例
onUnmounted(() => {
  const charts = document.querySelectorAll('.chart-item')
  charts.forEach(chart => {
    const instance = echarts.getInstanceByDom(chart as HTMLElement)
    instance?.dispose()
  })
  window.removeEventListener('resize', () => {})
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
    
    <!-- 统计卡片和图表区域 -->
    <div class="stats-section">
      <!-- 统计卡片 -->
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

      <!-- 图表区域 -->
      <el-button-group style="margin-bottom: 16px">
        <el-button
          v-for="option in timeOptions"
          :key="option.value"
          :type="timeRange === option.value ? 'primary' : 'default'"
          @click="timeRange = option.value"
        >
          {{ option.label }}
        </el-button>
      </el-button-group>
      <div class="chart-section">
        <div class="chart-card">
          <div id="loginChart"></div>
        </div>
      </div>
    </div>

    <!-- 数据可视化部分 -->
    <div class="charts-container">
      <div class="chart-section">
        <h3>全局数据分析</h3>
        <div class="charts-grid">
          <div id="global-activity" class="chart-item"></div>
          <div id="global-behavior" class="chart-item"></div>
          <div id="global-compare" class="chart-item"></div>
          <div id="global-heatmap" class="chart-item"></div>
        </div>
      </div>

      <div v-if="selectedUser" class="chart-section">
        <h3>用户 {{ selectedUser.name }} 的数据分析</h3>
        <div class="charts-grid">
          <div id="user-activity" class="chart-item"></div>
          <div id="user-behavior" class="chart-item"></div>
          <div id="user-compare" class="chart-item"></div>
          <div id="user-heatmap" class="chart-item"></div>
        </div>
      </div>
    </div>

    <!-- 用户表格区域 -->
    <div class="table-section">
      <h3 class="section-title">用户列表</h3>
      <el-table
        v-loading="loading"
        :data="filteredUsers"
        style="width: 100%"
        border
        class="user-table"
        @row-click="(row) => selectedUser = row"
        :row-class-name="(row) => row === selectedUser ? 'selected-row' : ''"
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
  </div>
</template>

<style scoped>
.user-manage {
  width: 100%;
  padding: 20px;
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

/* 统计卡片和图表区域样式 */
.stats-section {
  margin-bottom: 30px;
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

/* 图表区域样式 */
.chart-section {
  margin-bottom: 30px;
}

.chart-card {
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  height: 300px;
}

#loginChart {
  width: 100%;
  height: 100%;
}

/* 表格区域样式 */
.table-section {
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.section-title {
  margin: 0 0 20px 0;
  font-size: 18px;
  color: #2c3e50;
}

.user-table {
  margin-top: 10px;
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

.charts-container {
  margin-top: 20px;
  background: #fff;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.chart-section h3 {
  margin: 0 0 20px 0;
  color: #333;
  font-size: 18px;
}

.charts-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 24px;
  margin-bottom: 30px;
}

.chart-item {
  height: 360px;
  background: #fff;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.selected-row {
  background-color: #ecf5ff !important;
}
</style>
