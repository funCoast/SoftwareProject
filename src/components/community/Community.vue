<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import router from '../../router'
import axios from "axios";

const currentTag = ref('all')
const currentPage = ref(1)
const itemsPerPage = ref(12)
const baseImageUrl = "http://122.9.33.84:8000"

const categoryIcons: Record<string, string> = {
  all: 'https://api.iconify.design/material-symbols:category.svg',
  教育学习: 'https://api.iconify.design/material-symbols:school.svg',
  法律服务: 'https://api.iconify.design/material-symbols:gavel.svg',
  医疗健康: 'https://api.iconify.design/material-symbols:health-and-safety.svg',
  设计创意: 'https://api.iconify.design/material-symbols:palette.svg',
  旅游出行: 'https://api.iconify.design/material-symbols:flight.svg',
  娱乐游戏: 'https://api.iconify.design/material-symbols:sports-esports.svg',
  其他: 'https://api.iconify.design/material-symbols:more-horiz.svg',
}

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
    const uid = localStorage.getItem('LingXi_uid')
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
      <div
        v-for="(icon, category) in categoryIcons"
        :key="category"
        class="sub-nav-item"
        :class="{ active: currentTag === category }"
        @click="currentTag = category"
      >
        <img :src="icon" :alt="category" class="sub-icon" />
        {{ category === 'all' ? '全部' : category }}
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
  height: 100vh;
  background: #fdfdfd;
  overflow: hidden;
}

.sub-nav {
  width: 120px;
  background: #ffffff;
  flex-direction: column;
  margin-left: 0;
  border-left: none; /* 移除可能自带的边框 */
  z-index: 2;
  border-right: 1px solid #e0e0e0;
  padding-left: -5px;
  position: relative;
  left: -1px; /* ✅ 向左吸附，覆盖分隔线缝隙 */
  border-left: none;      /* 避免双线 */
}

.sub-nav-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 12px 0;
  width: 100%;
  color: #4FAFFF;
  font-size: 12px;
  transition: all 0.3s ease;
  cursor: pointer;
  border-bottom: 1px solid #cce0f3; /* ✅ 添加分割线 */
}

.sub-nav-item:last-child {
  border-bottom: none; /* ✅ 最后一项不加分割线 */
}

.sub-nav-item:hover,
.sub-nav-item.active {
  background-color: #b3d9f9;
  color: #1277d3;
}

.sub-icon {
  width: 20px;
  height: 20px;
  opacity: 0.6;
  transition: opacity 0.3s ease;
}

.sub-nav-item:hover .sub-icon,
.sub-nav-item.active .sub-icon {
  opacity: 0.95;
}

.content {
    position: relative;
  flex: 1;
  padding: 24px 36px 80px;
  overflow-y: auto;
  background: #fdfdfd;
  color: #333;
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

.filter-select,
.search-box {
  padding: 6px 10px;
  border: 1px solid #cce0f3;
  border-radius: 6px;
  background: white;
  font-size: 13px;
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
  border-radius: 8px;
}

.agent-info {
  margin: 18px 0 0 10px;
  width: 200px;
  height: 130px;
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
  -webkit-line-clamp: 3;
  line-clamp: 3;
}

.agent-stats {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 10px;
  border-top: 1px solid #eee;
}

.stat-item {
  margin: 0 5px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #666;
  font-size: 13px;
  padding: 4px 0;
  flex: 1;
  text-align: center;
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

.stat-item svg.like-icon {
  color: #e74c3c; /* 红色：表示点赞 */
}

.stat-item svg.favorite-icon {
  color: #f1c40f; /* 黄色：表示收藏 */
}

.stat-item svg.comment-icon {
  color: #409EFF; /* 蓝色：表示评论数，与 Element Plus 主色调一致 */
}

.pagination {
  position: absolute;
  bottom: 24px; /* 距离底部的距离 */
  left: 50%;
  transform: translateX(-50%);
  padding: 4px 12px;
  background: #ffffff;
  border: 1px solid #d0e6f7;
  border-radius: 12px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.04);
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 13px;
  z-index: 10;
}

.pagination button {
  width: 28px;
  height: 28px;
  border-radius: 8px;
  font-size: 12px;
  border: 1px solid #4FAFFF;
  background: white;
  color: #4FAFFF;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s ease;
  padding: 0;
}

.pagination button:hover:not(:disabled) {
  background-color: #eaf4ff;
}

.pagination button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.page-info {
  font-size: 13px;
  color: #4FAFFF;
}

.no-content {
  text-align: center;
  color: #999;
  font-size: 30px;
  padding: 20px;
}
</style>
