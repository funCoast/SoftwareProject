<script setup lang="ts">
import axios from 'axios'
import { ref, onMounted, computed } from 'vue'
import { ElMessage } from 'element-plus'
import router from '@/router'

const baseImageUrl = "http://122.9.33.84:8000"

// 待审核智能体相关
const pendingAgents = ref<{
  id: number
  name: string
  description: string
  icon: string
  author: {
    id: number
    name: string
    avatar: string
  }
  category: string
}[]>([])

// 添加搜索相关的变量
const searchQuery = ref('')

// 添加过滤后的智能体计算属性
const filteredAgents = computed(() => {
  if (!searchQuery.value) return pendingAgents.value
  const query = searchQuery.value.toLowerCase()
  return pendingAgents.value.filter(agent => 
    agent.name.toLowerCase().includes(query) ||
    agent.description.toLowerCase().includes(query) ||
    agent.author.name.toLowerCase().includes(query)
  )
})

const categories = [
  { value: 'education', label: '教育学习' },
  { value: 'legal', label: '法律服务' },
  { value: 'medical', label: '医疗健康' },
  { value: 'design', label: '设计创意' },
  { value: 'travel', label: '旅游出行' },
  { value: 'entertainment', label: '娱乐游戏' },
  { value: 'other', label: '其他' }
]

// 获取待审核智能体列表
async function fetchPendingAgents() {
  try {
    const response = await axios({
      method: 'get',
      url: 'admin/fetchPendingAgents',
      params: {
        uid: localStorage.getItem('LingXi_uid')
      }
    })
    if (response.data.code === 0) {
      pendingAgents.value = response.data.agents
    } else {
      ElMessage.error('获取待审核智能体失败：' + response.data.message)
    }
  } catch (error) {
    console.error('获取待审核智能体失败:', error)
    ElMessage.error('获取待审核智能体失败')
  }
}

// 审核智能体
async function reviewAgent(agentId: number, action: 'approve' | 'reject', category?: string) {
  try {
    const response = await axios({
      method: 'post',
      url: 'admin/reviewAgent',
      data: {
        uid: localStorage.getItem('LingXi_uid'),
        agent_id: agentId,
        action,
        category
      }
    })
    if (response.data.code === 0) {
      if (action === 'approve') {
        ElMessage.success('已通过')
      } else {
        ElMessage.success('已拒绝')
      }
      await fetchPendingAgents()
    } else {
      ElMessage.error('审核操作失败：' + response.data.message)
    }
  } catch (error) {
    console.error('审核操作失败:', error)
    ElMessage.error('审核操作失败')
  }
}

// 进入智能体编辑页面
function goToAgentEdit(agentId: number, authorId: number) {
  router.push({
    path: `/agentEdit/${agentId}`,
    query: {
      uid: authorId,
    }
  })
}

onMounted(() => {
  fetchPendingAgents()
})
</script>

<template>
  <div class="review-agent">
    <div class="section-header">
      <h2>智能体审核</h2>
      <div class="header-actions">
        <el-input
          placeholder="搜索智能体..."
          prefix-icon="Search"
          class="search-input"
          v-model="searchQuery"
        />
        <el-button type="primary" @click="fetchPendingAgents">
          <img src="https://api.iconify.design/material-symbols:refresh.svg" class="action-icon" />
          刷新
        </el-button>
      </div>
    </div>

    <div class="stats-cards">
      <div class="stat-card">
        <div class="stat-icon">
          <img src="https://api.iconify.design/material-symbols:pending-actions.svg" alt="pending" />
        </div>
        <div class="stat-info">
          <h3>待审核</h3>
          <p>{{ pendingAgents.length }}</p>
        </div>
      </div>
    </div>

    <div class="agents-content">
      <div class="agents-grid">
        <div v-for="agent in filteredAgents" :key="agent.id" class="agent-card">
          <div class="agent-header">
            <div class="agent-image">
              <el-avatar :size="60" :src="baseImageUrl + agent.icon" />
            </div>
            <div class="agent-title">
              <h3>{{ agent.name }}</h3>
              <div class="agent-author">
                <el-avatar :size="24" :src="baseImageUrl + agent.author.avatar" />
                <span>{{ agent.author.name }}</span>
              </div>
            </div>
            <el-button 
              type="text" 
              class="detail-btn"
              @click="goToAgentEdit(agent.id, agent.author.id)"
            >
              查看详情
              <img src="https://api.iconify.design/material-symbols:chevron-right.svg" class="action-icon" />
            </el-button>
          </div>
          <p class="agent-description">{{ agent.description }}</p>
          <div class="agent-actions">
            <el-select
              v-model="agent.category"
              placeholder="选择分类"
              class="category-select"
            >
              <el-option
                v-for="cat in categories"
                :key="cat.value"
                :label="cat.label"
                :value="cat.label"
              />
            </el-select>
            <div class="review-buttons">
              <el-button
                type="success"
                :disabled="!agent.category"
                @click="reviewAgent(agent.id, 'approve', agent.category)"
              >
                通过
              </el-button>
              <el-button
                type="danger"
                @click="reviewAgent(agent.id, 'reject')"
              >
                拒绝
              </el-button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.review-agent {
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

.stat-icon.success {
  background: #f0f9eb;
}

.stat-icon.success img {
  color: #67c23a;
}

.stat-icon.warning {
  background: #fdf6ec;
}

.stat-icon.warning img {
  color: #e6a23c;
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

.agents-content {
  background: transparent;
  padding: 0;
  box-shadow: none;
}

.agents-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(360px, 1fr));
  gap: 20px;
}

.agent-card {
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.agent-header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 16px;
}

.agent-title {
  flex: 1;
}

.agent-title h3 {
  margin: 0 0 8px;
  font-size: 18px;
  color: #2c3e50;
}

.agent-author {
  display: flex;
  align-items: center;
  gap: 8px;
}

.agent-author span {
  font-size: 14px;
  color: #666;
}

.detail-btn {
  color: #409EFF;
  font-size: 14px;
}

.agent-description {
  margin: 0 0 16px;
  color: #666;
  font-size: 14px;
  line-height: 1.6;
  display: -webkit-box;
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-overflow: ellipsis;
  -webkit-line-clamp: 3;
}

.agent-actions {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.category-select {
  width: 100%;
}

.review-buttons {
  display: flex;
  gap: 12px;
}

.review-buttons .el-button {
  flex: 1;
}
</style>