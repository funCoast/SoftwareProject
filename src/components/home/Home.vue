<script setup lang="ts">
import axios from 'axios'
import { ref, computed, watch, onBeforeMount } from 'vue'
import moment from 'moment'
import { useRouter } from 'vue-router'
import { ElDialog } from 'element-plus'

const router = useRouter()

const currentAgentTab = ref<string>('hot')
const currentPage = ref(1)
const itemsPerPage = ref(9)
const baseImageUrl = 'http://101.201.208.165'

// 添加用于控制对话框显示的变量
const dialogVisible = ref(false)
const selectedAnnouncement = ref<announcement | null>(null)

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

const hotAgents = ref<agent[]> ([])

const followingAgents = ref<agent[]> ([])

const favoriteAgents = ref<agent[]> ([])

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
      uid: localStorage.getItem('LingXi_uid')
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
      uid: localStorage.getItem('LingXi_uid')
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
      uid: localStorage.getItem('LingXi_uid')
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
      uid: localStorage.getItem('LingXi_uid')
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

// 添加标题计算属性
const currentTitle = computed(() => {
  switch (currentAgentTab.value) {
    case 'hot':
      return '热度推荐'
    case 'following':
      return '关注用户智能体'
    case 'favorite':
      return '收藏智能体'
    default:
      return '智能体推荐'
  }
})

// 添加查看公告详情的方法
function showAnnouncementDetail(announcement: announcement) {
  selectedAnnouncement.value = announcement
  dialogVisible.value = true
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
            <div v-for="announcement in announcements" :key="announcement.id" class="notice-item" @click="showAnnouncementDetail(announcement)">
              <div class="notice-text">
                <h4>{{ announcement.title }}</h4>
                <p>{{ announcement.content }}</p>
                <span class="notice-time">{{ moment(announcement.time).format('YYYY-MM-DD HH:mm:ss') }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 添加公告详情对话框 -->
      <el-dialog
        v-model="dialogVisible"
        :title="selectedAnnouncement?.title"
        width="50%"
        class="announcement-dialog"
      >
        <div class="announcement-detail">
          <p class="announcement-content">{{ selectedAnnouncement?.content }}</p>
          <div class="announcement-footer">
            <span class="announcement-time">发布时间：{{ selectedAnnouncement ? moment(selectedAnnouncement.time).format('YYYY-MM-DD HH:mm:ss') : '' }}</span>
          </div>
        </div>
      </el-dialog>

      <!-- 右侧智能体推荐板块 -->
      <div class="agent-section">
        <div class="section-header">
          <h2>{{ currentTitle }}</h2>
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
          <span v-if="currentAgentTab === 'hot'">似乎没有相关内容，去社区看看吧</span>
          <span v-else-if="currentAgentTab === 'following'">似乎没有相关内容，去关注更多用户吧</span>
          <span v-else-if="currentAgentTab === 'favorite'">您还没有收藏任何智能体，去社区看看吧</span>
          <span v-else>暂无相关内容</span>
        </div>
        <div v-else class="agent-content">
          <div class="agent-grid">
            <div v-for="agent in paginatedAgents" :key="agent.id" class="agent-card" @click="goToAgentDetail(agent.id)">
              <el-container>
                <el-header style="height: 150px;">
                  <el-container>
                    <el-aside style="width: 80px; height: 150px;">
                      <div class="agent-image">
                        <img :src="baseImageUrl + agent.image" :alt="agent.name">
                      </div>
                    </el-aside>
                    <el-main style="width: 200px; height: 150px; padding: 0;">
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
  padding: 10px 20px 0 20px;
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
  margin-bottom: 24px;
  padding: 0 10px;
}

.section-header h2 {
  margin: 0;
  color: #2c3e50;
  font-size: 22px;
  font-weight: 600;
  position: relative;
  display: inline-block;
}

.section-header h2::after {
  content: '';
  position: absolute;
  bottom: -6px;
  left: 0;
  width: 100%;
  height: 3px;
  background: #4FAFFF;
  border-radius: 2px;
}

.tab-switch {
  display: flex;
  gap: 12px;
  background: #f8f9fa;
  padding: 4px;
  border-radius: 12px;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.05);
}

.tab-switch span {
  padding: 8px 16px;
  cursor: pointer;
  border-radius: 8px;
  font-size: 14px;
  color: #666;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.tab-switch span:hover {
  color: #4FAFFF;
  background: rgba(79, 175, 255, 0.1);
}

.tab-switch span.active {
  background: #4FAFFF;
  color: white;
  box-shadow: 0 2px 8px rgba(79, 175, 255, 0.3);
}

.tab-switch span::before {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  width: 0;
  height: 0;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 50%;
  transform: translate(-50%, -50%);
  transition: width 0.4s ease, height 0.4s ease;
}

.tab-switch span:active::before {
  width: 100px;
  height: 100px;
  opacity: 0;
}

.notice-section {
  width: 350px;
  height: 750px;
  background: white;
  border-radius: 16px;
  padding: 20px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  position: relative;
}

.notice-section::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: linear-gradient(90deg, #4FAFFF, #7cc5ff);
  border-radius: 16px 16px 0 0;
}

.notice-content {
  overflow-y: auto;
  height: calc(100% - 50px);
  /* 自定义滚动条样式 */
  scrollbar-width: thin;
  scrollbar-color: #4fafffbd #f1f5f9;
}

/* Webkit 浏览器滚动条美化 */
.notice-content::-webkit-scrollbar {
  width: 8px;
  background: #f1f5f9;
  border-radius: 8px;
}

.notice-content::-webkit-scrollbar-thumb {
  background: linear-gradient(180deg, #4FAFFF 60%, #7cc5ff 100%);
  border-radius: 8px;
  min-height: 30px;
}

.notice-content::-webkit-scrollbar-thumb:hover {
  background: linear-gradient(180deg, #3399ff 60%, #4FAFFF 100%);
}

.notice-content::-webkit-scrollbar-corner {
  background: transparent;
}

.notice-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
  margin-top: 10px;
}

.notice-item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 16px;
  border-radius: 12px;
  background-color: #f8f9fa;
  transition: all 0.3s ease;
  border: 1px solid rgba(79, 175, 255, 0.1);
  position: relative;
  overflow: hidden;
  cursor: pointer;
}

.notice-item::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  width: 4px;
  height: 100%;
  background: #4FAFFF;
  border-radius: 0 2px 2px 0;
  opacity: 0.6;
}

.notice-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  background-color: #ffffff;
  border-color: rgba(79, 175, 255, 0.2);

  &::before {
    opacity: 1;
  }
}

.notice-text {
  flex: 1;
}

.notice-text h4 {
  margin: 0 0 8px 0;
  color: #2c3e50;
  font-size: 15px;
  font-weight: 600;
  line-height: 1.4;
}

.notice-text p {
  margin: 0;
  color: #666;
  font-size: 14px;
  line-height: 1.6;
}

.notice-time {
  font-size: 12px;
  color: #94a3b8;
  margin-top: 8px;
  display: block;
  padding-top: 8px;
  border-top: 1px dashed rgba(0, 0, 0, 0.06);
}

.agent-section {
  width: 1000px;
  height: 750px;
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  position: relative;
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
  width: 70px;
  height: 70px;
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
  width: 190px;
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
  margin-left:  5px;
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
  position: absolute;
  bottom: 20px;
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
  font-size: 25px;
  padding: 20px;
}

/* 添加公告详情对话框样式 */
.announcement-dialog {
  :deep(.el-dialog__header) {
    padding: 20px;
    margin: 0;
    border-bottom: 1px solid #e0e0e0;
    background: #f8f9fa;
  }

  :deep(.el-dialog__title) {
    font-size: 18px;
    font-weight: 600;
    color: #2c3e50;
  }

  :deep(.el-dialog__body) {
    padding: 24px;
  }
}

.announcement-detail {
  .announcement-content {
    font-size: 15px;
    line-height: 1.6;
    color: #333;
    margin: 0 0 20px 0;
    white-space: pre-wrap;
  }

  .announcement-footer {
    padding-top: 16px;
    border-top: 1px solid #eee;
    
    .announcement-time {
      font-size: 13px;
      color: #666;
    }
  }
}
</style>