<script setup lang="ts">
import axios from 'axios'
import { ref, computed, watch, onBeforeMount } from 'vue'
import moment from 'moment'

const currentAgentTab = ref<string>('hot')
const currentPage = ref(1)
const itemsPerPage = ref(6)
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
  author: {
    id?: number
    name: string
    avatar: string
  }
}

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

const totalPages =  computed(() => {
  return Math.ceil(currentAgents.value.length / itemsPerPage.value)
})
const paginatedAgents = computed(()=> {
  const start = (currentPage.value - 1) * itemsPerPage.value
  const end = start + itemsPerPage.value
  return currentAgents.value.slice(start, end)
})

watch (
    () => currentAgentTab,
    () => {
      currentPage.value = 1
    }
)
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
        <div class="agent-content">
          <div class="agent-grid">
            <div v-for="agent in paginatedAgents" :key="agent.id" class="agent-card">
              <div class="agent-image">
                <img :src="baseImageUrl + agent.image" :alt="agent.name">
                <div class="agent-category">{{ agent.category }}</div>
              </div>
              <div class="agent-info">
                <div class="agent-header">
                  <h3>{{ agent.name }}</h3>
                  <div class="agent-author">
                    <img :src="baseImageUrl + agent.author.avatar" :alt="agent.author.name">
                    <span>{{ agent.author.name }}</span>
                  </div>
                </div>
                <p class="agent-description">{{ agent.description }}</p>
                <div class="agent-stats">
<!--                  <span class="stat-item" title="使用量">-->
<!--                    <svg class="usage-icon" viewBox="0 0 24 24" fill="currentColor">-->
<!--                      <path d="M13 3L4 14h7l-2 5 9-11h-7l2-5z"/>-->
<!--                    </svg>-->
<!--                    {{ agent.usage }}-->
<!--                  </span>-->
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
                </div>
              </div>
            </div>
          </div>
          <!-- 分页控件 -->
          <div class="pagination">
            <button
                :disabled="currentPage === 1"
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

.notice-section, .agent-section {
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

.agent-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 20px;
  padding: 10px;
}

.agent-card {
  background: white;
  border-radius: 12px;
  overflow: hidden;
  transition: all 0.3s ease;
  cursor: pointer;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.agent-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
}

.agent-image {
  position: relative;
  width: 100%;
  padding-top: 56.25%; /* 16:9 宽高比 */
}

.agent-image img {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: 8px 8px 0 0;
}

.agent-category {
  position: absolute;
  top: 10px;
  right: 10px;
  background: rgba(44, 62, 80, 0.8);
  color: white;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
}

.agent-info {
  padding: 15px;
  display: flex;
  flex-direction: column;
  flex: 1;
  min-height: 180px;
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
  font-size: 16px;
}

.agent-author {
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
  flex: 1;
  overflow: hidden;
  display: -webkit-box;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 3; /* 限制显示3行 */
}

.agent-stats {
  display: flex;
  justify-content: space-between;
  padding-top: 10px;
  border-top: 1px solid #eee;
  margin-top: auto;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 5px;
  color: #666;
  font-size: 13px;
  padding: 4px 8px;
  border-radius: 12px;
  background: #f8f9fa;
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
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 15px;
  margin-top: 30px;
  padding: 20px;
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
</style> 