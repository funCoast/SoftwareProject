<script setup lang="ts">
import axios from 'axios'
import { ref, onMounted } from 'vue'
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
    </div>
    <div class="agents-content">
      <div class="agents-grid">
        <div v-for="agent in pendingAgents" :key="agent.id" class="agent-card" @click="goToAgentEdit(agent.id, agent.author.id)">
          <div class="agent-image">
            <el-avatar :size="80" :src="baseImageUrl + agent.icon" />
          </div>
          <div class="agent-info">
            <div class="agent-header">
              <h3>{{ agent.name }}</h3>
              <div class="agent-author">
                <el-avatar :size="24" :src="baseImageUrl + agent.author.avatar" />
                <span>{{ agent.author.name }}</span>
              </div>
            </div>
            <p class="agent-description">{{ agent.description }}</p>
            <div class="agent-actions">
              <el-select
                v-model="agent.category"
                placeholder="选择分类"
                class="category-select"
                @click.stop
              >
                <el-option
                  v-for="cat in categories"
                  :key="cat.value"
                  :label="cat.label"
                  :value="cat.label"
                />
              </el-select>
              <div class="review-buttons" @click.stop>
                <el-button
                  type="success"
                  :disabled="!agent.category"
                  @click="reviewAgent(agent.id, 'approve', agent.category)"
                >
                  通过
                </el-button>
                <el-button
                  type="danger"
                  @click="reviewAgent(agent.id, 'reject', agent.category)"
                >
                  拒绝
                </el-button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.review-agent {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.section-header h2 {
  margin: 0;
  color: #2c3e50;
}

.agents-content {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.agents-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
}

.agent-card {
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  cursor: pointer;
  transition: all 0.3s ease;
}

.agent-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
}

.agent-image {
  display: flex;
  justify-content: center;
  margin-bottom: 15px;
}

.agent-info {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.agent-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.agent-header h3 {
  margin: 0;
  font-size: 18px;
  color: #2c3e50;
}

.agent-author {
  display: flex;
  align-items: center;
  gap: 5px;
}

.agent-author span {
  font-size: 12px;
  color: #666;
}

.agent-description {
  margin: 0;
  color: #666;
  font-size: 14px;
  line-height: 1.5;
}

.agent-actions {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-top: 15px;
}

.category-select {
  width: 100%;
}

.review-buttons {
  display: flex;
  gap: 10px;
  justify-content: flex-end;
}
</style>