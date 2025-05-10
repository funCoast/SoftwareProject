<script setup lang="ts">
import axios from 'axios'
import { ref, computed, watch, onBeforeMount } from 'vue'
import moment from 'moment'
import { useRouter } from 'vue-router'

const router = useRouter()

const currentAgentTab = ref<string>('hot')
const currentPage = ref(1)
const itemsPerPage = ref(9)
const baseImageUrl = 'http://122.9.33.84:8000'

interface announcement {
  id: number
  title: string
  content: string
  time: Date
}

const announcements = ref<announcement[]>([])

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

const hotAgents = ref<agent[]> ([
])

const followingAgents = ref<agent[]> ([
])

const favoriteAgents = ref<agent[]> ([
])

const currentAgents =  computed(() => {
  switch (currentAgentTab.value) {
    case 'hot':
      return hotAgents.value
    case 'following':
      return followingAgents.value
    case 'favorite':
      return favoriteAgents.value
    default:
      return hotAgents.value
  }
})

const totalPages = computed(() => {
  const pages = Math.ceil(currentAgents.value.length / itemsPerPage.value);
  return pages > 0 ? pages : 0; // 如果没有智能体，页码为 0
});

const paginatedAgents = computed(()=> {
  const start = (currentPage.value - 1) * itemsPerPage.value
  const end = start + itemsPerPage.value
  return currentAgents.value.slice(start, end)
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
)

onBeforeMount (() => {
  fetchAnnouncement()
  fetchHot()
  fetchFollowing()
  fetchFavorites()
})

async function fetchAnnouncement() {
  axios({
    method: 'get',
    url: 'anno/get',
    params: {
      uid: sessionStorage.getItem('uid')
    }
  }).then(function (response) {
    if(response.data.code === 0) {
      announcements.value=response.data.announcements
    }
  })
}

async function fetchHot() {
  axios({
    method: 'get',
    url: 'user/fetchHot',
    params: {
      uid: sessionStorage.getItem('uid')
    }
  }).then(function (response) {
    if(response.data.code === 0) {
      hotAgents.value=response.data.data
      console.log(response.data.data)
    }
  })
}

async function fetchFavorites() {
  axios({
    method: 'get',
    url: 'user/fetchFavorites',
    params: {
      uid: sessionStorage.getItem('uid')
    }
  }).then(function (response) {
    if(response.data.code === 0) {
      favoriteAgents.value=response.data.data
    }
  })
}

async function fetchFollowing() {
  axios({
    method: 'get',
    url: 'user/fetchFollowWorks',
    params: {
      uid: sessionStorage.getItem('uid')
    }
  }).then(function (response) {
    if(response.data.code === 0) {
      followingAgents.value=response.data.data
    }
  })
}

// 跳转到智能体详情页
function goToAgentDetail(agentId: number) {
  router.push({
    path: `/agentDetail/${agentId}`
  })
}
</script>

<template>
  <div class="home">
    <div class="home-container">
      <!-- 左侧公告板块 -->
      <div class="notice-section">
        <div class="section-header">
          <h2>公告</h2>
        </div>
        <div class="notice-content">
          <div class="notice-list">
            <div v-for="announcement in announcements" :key="announcement.id" class="notice-item">
              <!--              <i class="fas fa-check-circle"></i>-->
              <div class="notice-text">
                <h4>{{ announcement.title }}</h4>
                <p>{{ announcement.content }}</p>
                <span class="notice-time">{{ moment(announcement.time).format('YYYY-MM-DD hh:mm:ss') }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 右侧智能体推荐板块 -->
      <div class="agent-section">
        <div class="section-header">
          <h2>智能体推荐</h2>
          <div class="tab-switch">
            <span
                :class="{ active: currentAgentTab === 'hot' }"
                @click="currentAgentTab = 'hot'"
            >热度推荐</span>
            <span
                :class="{ active: currentAgentTab === 'following' }"
                @click="currentAgentTab = 'following'"
            >关注用户智能体</span>
            <span
                :class="{ active: currentAgentTab === 'favorite' }"
                @click="currentAgentTab = 'favorite'"
            >收藏智能体</span>
          </div>
        </div>
        <div v-if="currentAgents.length === 0" class="no-content">
          暂无相关内容
        </div>
        <div v-else class="agent-content">
          <div class="agent-grid">
            <div v-for="agent in paginatedAgents" :key="agent.id" class="agent-card" @click="goToAgentDetail(agent.id)">
              <el-container>
                <el-header style="height: 150px;">
                  <el-container>
                    <el-aside style="width: 100px; height: 150px;">
                      <div class="agent-image">
                        <img :src="baseImageUrl + agent.image" :alt="agent.name">
                      </div>
                    </el-aside>
                    <el-main style="width: 180px; height: 150px; padding: 0;">
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
            <span class="page-info">{{ currentPage }} / {{ totalPages }}</span>
            <button
                :disabled="currentPage === totalPages"
                @click="currentPage++"
            >
              <svg viewBox="0 0 24 24" fill="currentColor">
                <path d="M10 6L8.59 7.41 13.17 12l-4.58 4.59L10 18l6-6z"/>
              </svg>
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.home {
  padding: 20px;
}

.home-container {
  display: grid;
  grid-template-columns: 1fr 2fr;
  gap: 20px;
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

.tab-switch {
  display: flex;
  gap: 10px;
}

.tab-switch span {
  padding: 5px 10px;
  cursor: pointer;
  border-radius: 4px;
  transition: all 0.3s ease;
}

.tab-switch span.active {
  background-color: #2c3e50;
  color: white;
}

.notice-section {
  width: 300px;
  height: 750px;
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.agent-section {
  width: 1000px;
  height: 750px;
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}
.notice-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.notice-item {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  padding: 10px;
  border-radius: 6px;
  background-color: #f8f9fa;
}

.notice-item i {
  color: #3498db;
  font-size: 20px;
}

.notice-text h4 {
  margin: 0 0 5px 0;
  color: #2c3e50;
}

.notice-text p {
  margin: 0;
  color: #666;
  font-size: 14px;
}

.agent-content {
  flex: 1;
  overflow-y: auto;
}

.agent-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  grid-template-rows:minmax(200px, 1fr) minmax(200px, 1fr) minmax(200px, 1fr);
  column-gap: 20px;
  row-gap: 10px;
  padding: 10px;
}

.agent-card {
  height: 195px;
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
  width: 90px;
  height: 90px;
  overflow: hidden;
  border-radius: 8px;
  margin: 16px 0 0 0;
  background: #f8f9fa;
}

.agent-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: 8px; /* 确保图片的圆角与容器一致 */
}

.agent-info {
  margin: 16px 0 0 10px;
  width: 170px;
  height: 120px;
  justify-content: space-between;
}

.agent-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.agent-header h3 {
  margin: 0;
  color: #2c3e50;
  font-size: 16px;
  font-weight: bold;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.agent-author {
  margin-bottom: 8px;
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
  margin: 0 0 10px 0;
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
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 5px;
  color: #666;
  font-size: 13px;
  padding: 4px 8px;
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
  margin-top: auto;
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 15px;
  margin-top: 10px;
  padding: 10px;
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
  transform: none;
}

.page-info {
  color: #2c3e50;
  font-size: 16px;
  font-weight: 500;
  padding: 0 15px;
}

.notice-time {
  font-size: 12px;
  color: #999;
  margin-top: 5px;
  display: block;
}

.no-content {
  text-align: center;
  color: #999;
  font-size: 25px;
  padding: 20px;
}
</style>