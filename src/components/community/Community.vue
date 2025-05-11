<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import router from '../../router'
import axios from "axios";

const currentTag = ref('all')
const currentPage = ref(1)
const itemsPerPage = ref(12)
const baseImageUrl = "http://122.9.33.84:8000"

interface agent {
  id: number
  name: string
  category: string
  description: string
  image: string
  likes: number
  favorites: number
  comments: number
  author: {
    id?: number
    name: string
    avatar: string
  }
}
const agents = ref<agent[]> ([
])

async function fetchAllAgents() {
  try {
    const uid = sessionStorage.getItem('uid')
    if (!uid) {
      console.error('用户ID不存在')
      return
    }
    const response = await axios({
      method: 'get',
      url: '/community/fetchAllAgents',
      params: {
        uid
      }
    })
    if (response.data.code === 0) {
      agents.value = response.data.agents
      console.log('获取智能体成功')
    } else {
      console.log(response.data.message)
    }
  } catch (error) {
    console.error('获取智能体失败:', error)
  }
}
  
const filteredAgents = computed(() => {
  if (currentTag.value === 'all') {
    return agents.value
  }
  return agents.value.filter(agent => agent.category === currentTag.value)
})
const totalPages = computed(() => {
  const pages = Math.ceil(filteredAgents.value.length / itemsPerPage.value);
  return pages > 0 ? pages : 0; // 如果没有智能体，页码为 0
});

const paginatedAgents = computed(() => {
  const start = (currentPage.value - 1) * itemsPerPage.value
  const end = start + itemsPerPage.value
  return filteredAgents.value.slice(start, end)
})

watch(
  () => totalPages.value,
  (newTotalPages) => {
    if (newTotalPages === 0) {
      currentPage.value = 0; // 如果总页数为 0，当前页也设置为 0
    } else {
      currentPage.value = 1;
    }
  }
);

function goToAgentDetail(id: number) {
  router.push(`/agentDetail/${id}`)
}

onMounted(() => {
  fetchAllAgents()
})
</script>

<template>
  <div class="community-container">
    <!-- 二级导航栏 -->
    <div class="sub-nav">
      <div class="sub-nav-item" :class="{ active: currentTag === 'all' }" @click="currentTag = 'all'">
        <svg viewBox="0 0 24 24" fill="currentColor" width="20" height="20">
          <path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm0 16H5V5h14v14z"/>
        </svg>
        全部
      </div>
      <div class="sub-nav-item" :class="{ active: currentTag === '教育学习' }" @click="currentTag = '教育学习'">
        <svg viewBox="0 0 24 24" fill="currentColor" width="20" height="20">
          <path d="M12 3L1 9l4 2.18v6L12 21l7-3.82v-6l2-1.09V17h2V9L12 3zm6.82 6L12 12.72 5.18 9 12 5.28 18.82 9zM17 15.99l-5 2.73-5-2.73v-3.72L12 15l5-2.73v3.72z"/>
        </svg>
        教育学习
      </div>
      <div class="sub-nav-item" :class="{ active: currentTag === '法律服务' }" @click="currentTag = '法律服务'">
        <svg viewBox="0 0 24 24" fill="currentColor" width="20" height="20">
          <path d="M14 2H6c-1.1 0-1.99.9-1.99 2L4 20c0 1.1.89 2 1.99 2H18c1.1 0 2-.9 2-2V8l-6-6zm2 16H8v-2h8v2zm0-4H8v-2h8v2zm-3-5V3.5L18.5 9H13z"/>
        </svg>
        法律服务
      </div>
      <div class="sub-nav-item" :class="{ active: currentTag === '医疗健康' }" @click="currentTag = '医疗健康'">
        <svg viewBox="0 0 24 24" fill="currentColor" width="20" height="20">
          <path d="M19 3H5c-1.1 0-1.99.9-1.99 2L3 19c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm-1 11h-4v4h-4v-4H6v-4h4V6h4v4h4v4z"/>
        </svg>
        医疗健康
      </div>
      <div class="sub-nav-item" :class="{ active: currentTag === '设计创意' }" @click="currentTag = '设计创意'">
        <svg viewBox="0 0 24 24" fill="currentColor" width="20" height="20">
          <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8zm-5.5-2.5l7.51-3.49L17.5 6.5 9.99 9.99 6.5 17.5zm5.5-6.6c.61 0 1.1.49 1.1 1.1s-.49 1.1-1.1 1.1-1.1-.49-1.1-1.1.49-1.1 1.1-1.1z"/>
        </svg>
        设计创意
      </div>
      <div class="sub-nav-item" :class="{ active: currentTag === '旅游出行' }" @click="currentTag = '旅游出行'">
        <svg viewBox="0 0 24 24" fill="currentColor" width="20" height="20">
          <path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5c-1.38 0-2.5-1.12-2.5-2.5s1.12-2.5 2.5-2.5 2.5 1.12 2.5 2.5-1.12 2.5-2.5 2.5z"/>
        </svg>
        旅游出行
      </div>
      <div class="sub-nav-item" :class="{ active: currentTag === '娱乐游戏' }" @click="currentTag = '娱乐游戏'">
        <svg viewBox="0 0 24 24" fill="currentColor" width="20" height="20">
          <path d="M15 7.5V2H9v5.5l3 3 3-3zM7.5 9H2v6h5.5l3-3-3-3zM9 16.5V22h6v-5.5l-3-3-3 3zM16.5 9l-3 3 3 3H22V9h-5.5z"/>
        </svg>
        娱乐游戏
      </div>
      <div class="sub-nav-item" :class="{ active: currentTag === '其他' }" @click="currentTag = '其他'">
        <svg viewBox="0 0 24 24" fill="currentColor" width="20" height="20">
          <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 17h-2v-2h2v2zm2.07-7.75l-.9.92C13.45 12.9 13 13.5 13 15h-2v-.5c0-1.1.45-2.1 1.17-2.83l1.24-1.26c.37-.36.59-.86.59-1.41 0-1.1-.9-2-2-2s-2 .9-2 2H8c0-2.21 1.79-4 4-4s4 1.79 4 4c0 .88-.36 1.68-.93 2.25z"/>
        </svg>
        其他
      </div>
    </div>

    <!-- 内容区域 -->
    <div class="content">
      <!-- 顶部标题栏 -->
      <div class="header">
        <h1>{{ currentTag === 'all' ? '全部' : currentTag === 'template' ? '模板' : currentTag }}</h1>
        <div class="header-right">
          <select class="filter-select">
            <option value="trend">按当前趋势</option>
            <option value="usage">按使用量</option>
            <option value="likes">按点赞量</option>
            <option value="favorites">按收藏量</option>
            <option value="time">按发布时间</option>
          </select>
          <div class="search-box">
            <svg viewBox="0 0 24 24" fill="currentColor" width="16" height="16">
              <path d="M15.5 14h-.79l-.28-.27C15.41 12.59 16 11.11 16 9.5 16 5.91 13.09 3 9.5 3S3 5.91 3 9.5 5.91 16 9.5 16c1.61 0 3.09-.59 4.23-1.57l.27.28v.79l5 4.99L20.49 19l-4.99-5zm-6 0C7.01 14 5 11.99 5 9.5S7.01 5 9.5 5 14 7.01 14 9.5 11.99 14 9.5 14z"/>
            </svg>
          </div>
<!--          <button class="publish-btn">-->
<!--            <svg viewBox="0 0 24 24" fill="currentColor" width="20" height="20">-->
<!--              <path d="M19 13h-6v6h-2v-6H5v-2h6V5h2v6h6v2z"/>-->
<!--            </svg>-->
<!--            发布智能体-->
<!--          </button>-->
        </div>
      </div>

      <div v-if="filteredAgents.length === 0" class="no-content">
          暂无相关内容，快来抢先发布吧！
      </div>
      <!-- 智能体列表 -->
      <div v-else class="agent-list">
        <div v-for="agent in paginatedAgents" :key="agent.id" class="agent-card" @click="goToAgentDetail(agent.id)">
          <el-container>
            <el-header style="height: 160px;">
              <el-container>
                <el-aside style="width: 70px; height: 160px;">
                  <div class="agent-image">
                    <img :src="baseImageUrl + agent.image" :alt="agent.name">
                  </div>
                </el-aside>
                <el-main style="width: 210px; height: 160px; padding: 0;">
                  <div class="agent-info">
                    <div class="agent-header">
                      <h3>{{ agent.name }}</h3>
                    </div>
                    <div class="agent-author">
                      <img :src="baseImageUrl + agent.author.avatar" :alt="agent.author.name">
                      <span>{{ agent.author.name }}</span>
                    </div>
                    <p class="agent-description">{{ agent.description }}</p>
                  </div>
                </el-main>
              </el-container>
            </el-header>  
            <el-footer>
              <div class="agent-stats">
                <span class="stat-item" title="点赞量">
                  <svg class="like-icon" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z"/>
                  </svg>
                  {{ agent.likes }}
                </span>
                <span class="stat-item" title="收藏量">
                  <svg class="favorite-icon" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M17 3H7c-1.1 0-1.99.9-1.99 2L5 21l7-3 7 3V5c0-1.1-.9-2-2-2zm0 15l-5-2.18L7 18V5h10v13z"/>
                  </svg>
                  {{ agent.favorites }}
                </span>
                <span class="stat-item" title="评论量">
                  <svg class="comment-icon" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M20 2H4c-1.1 0-2 .9-2 2v14l4-4h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2z"/>
                  </svg>
                  {{ agent.comments }}
                </span>
              </div>
              </el-footer>
            </el-container>
          </div>
        </div>

      <!-- 分页控件 -->
      <div class="pagination">
        <button 
          :disabled="currentPage <= 1"
          @click="currentPage--"
        >
          <svg viewBox="0 0 24 24" fill="currentColor">
            <path d="M15.41 7.41L14 6l-6 6 6 6 1.41-1.41L10.83 12z"/>
          </svg>
        </button>
        <span class="page-info">{{ totalPages === 0 ? 0 : currentPage }} / {{ totalPages }}</span>
        <button 
          :disabled="currentPage >= totalPages || totalPages === 0"
          @click="currentPage++"
        >
          <svg viewBox="0 0 24 24" fill="currentColor">
            <path d="M10 6L8.59 7.41 13.17 12l-4.58 4.59L10 18l6-6z"/>
          </svg>
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.community-container {
  display: flex;
  height: 100%;
  background: #f8f9fa;
}

.sub-nav {
  width: 150px;
  background: white;
  padding: 20px 0;
  border-right: 1px solid #e9ecef;
}

.sub-nav-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 20px;
  color: #666;
  cursor: pointer;
  transition: all 0.3s ease;
}

.sub-nav-item:hover {
  background: #f8f9fa;
  color: #2c3e50;
}

.sub-nav-item.active {
  background: #2c3e50;
  color: white;
}

.content {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.header h1 {
  margin: 0;
  color: #2c3e50;
  font-size: 24px;
}

.header-right {
  display: flex;
  gap: 16px;
  align-items: center;
}

.filter-select {
  padding: 8px 12px;
  border: 1px solid #e9ecef;
  border-radius: 6px;
  background: white;
  color: #2c3e50;
  cursor: pointer;
}

.search-box {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  background: white;
  border: 1px solid #e9ecef;
  border-radius: 6px;
  flex: 1;
  max-width: 300px;
}

.search-box input {
  border: none;
  outline: none;
  width: 100%;
  color: #2c3e50;
}

.publish-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background: #2c3e50;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.publish-btn:hover {
  background: #34495e;
}

.agent-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
}

.agent-card {
  height: 205px;
  width: 320px;
  display: flex;
  background: white;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
  cursor: pointer;
}

.agent-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
}

.agent-image {
  width: 70px;
  height: 70px;
  overflow: hidden;
  border-radius: 8px;
  margin: 18px 0 0 0; 
  background: #f8f9fa;
}

.agent-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: 8px; /* 确保图片的圆角与容器一致 */
}

.agent-info {
  margin: 18px 0 0 10px;
  width: 200px;
  height: 130px;
  justify-content: space-between;
}

.agent-header {
  display: flex;
  justify-content: space-between;
  align-items: center; 
  margin-bottom: 10px;
}

.agent-header h3 {
  margin: 0;
  color: #2c3e50;
  font-size: 18px;
  font-weight: bold;
  white-space: nowrap; 
  overflow: hidden; 
  text-overflow: ellipsis; 
}

.agent-author {
  margin-bottom: 10px;
  display: flex;
  align-items: center;
  gap: 5px;
}

.agent-author img {
  width: 24px;
  height: 24px;
  border-radius: 50%;
}

.agent-author span {
  font-size: 12px;
  color: #666;
}

.agent-description {
  margin: 0 0 15px 0;
  color: #666;
  font-size: 14px;
  line-height: 1.5;
  display: -webkit-box;
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-overflow: ellipsis;
  -webkit-line-clamp: 3; /* 限制描述显示三行 */
  line-clamp: 3; /* Standard property for compatibility */
}

.agent-stats {
  display: flex;
  justify-content: space-between; /* 平均分布 */
  align-items: center;
  padding-top: 10px;
  border-top: 1px solid #eee; /* 添加分隔线 */
}

.stat-item {
  margin-left: 5px;
  margin-right: 5px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #666;
  font-size: 13px;
  padding: 4px 0;
  flex: 1; /* 平均分配宽度 */
  text-align: center; /* 居中对齐 */
  background: #f8f9fa;
  border-radius: 8px;
  transition: all 0.3s ease;
}

.stat-item:hover {
  background: #e9ecef;
}

.stat-item svg {
  width: 16px;
  height: 16px;
}

.stat-item svg.usage-icon {
  color: #e74c3c;
}

.stat-item svg.like-icon {
  color: #e74c3c;
}

.stat-item svg.favorite-icon {
  color: #f1c40f;
}

.pagination {
  position: fixed;
  bottom: 20px;
  width: 500px;
  left: 250px;
  right: 0;
  margin-left: auto;
  margin-right: auto;
  height: 50px;
  display: flex;
  justify-content: center;
  align-items: center;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.pagination button {
  background: #f8f9fa;
  border: none;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s ease;
  color: #2c3e50;
}

.pagination button svg {
  width: 20px;
  height: 20px;
  color: #2c3e50;
}

.pagination button:hover:not(:disabled) {
  background: #e9ecef;
  transform: scale(1.1);
}

.pagination button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.page-info {
  color: #666;
  font-size: 14px;
}

.no-content {
  text-align: center;
  color: #999;
  font-size: 30px;
  padding: 20px;
}
</style>