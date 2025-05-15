<script setup lang="ts">
import { ref, onBeforeMount, watch, computed } from 'vue'
import axios from 'axios'
import router from '../../router'
import {useRoute} from "vue-router";
import { ElMessage } from 'element-plus'

const avatar = ref<string>('')
const baseImageUrl = 'http://122.9.33.84:8000'

const currentTab = ref('likes')
const tabs = ref([
  { id: 'works', name: '作品' },
  { id: 'likes', name: '喜欢' },
  { id: 'favorites', name: '收藏' }
])

const userInfo = ref({
  name: '',
  account: '',
  description: '',
  following: 0,
  followers: 0,
})

const route = useRoute()
const uid = computed(() => route.params.id)
const currentUid = sessionStorage.getItem('uid')

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

const myWorks = ref<agent[]>([])
const likes = ref<agent[]>([])
const favorites = ref<agent[]>([])
const agentsPerPage = ref(6) // 每页显示的智能体数量
const currentPage = ref(1) // 当前页码  

const curAgents =  computed(() => {
  switch (currentTab.value) {
    case 'works':
      return myWorks.value
    case 'likes':
      return likes.value
    case 'favorites':
      return favorites.value
    default:
      return myWorks.value
  }
})

const totalPages = computed(() => {
  const pages = Math.ceil(curAgents.value.length / agentsPerPage.value);
  return pages > 0 ? pages : 0; // 如果没有智能体，页码为 0
});

const paginatedAgents = computed(()=> {
  const start = (currentPage.value - 1) * agentsPerPage.value
  const end = start + agentsPerPage.value
  return curAgents.value.slice(start, end)
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

const error = ref({
  userInfo: '',
  works: '',
  likes: '',
  favorites: ''
})

// 加载用户数据
function loadUserData() {
  getAvatar()
  fetchUserInfo()
  fetchWorks()
  fetchLikes()
  fetchFavorites()
}

onBeforeMount(() => {
  loadUserData()
})

// 监听uid变化
watch(uid, (newUid) => {
  if (newUid) {
    loadUserData()
  }
}, { immediate: true })

function getAvatar() {
  axios({
    method: 'get',
    url: 'user/getAvatar',
    params: {
      uid: uid.value
    }
  }).then(function (response) {
    if (response.data.code === 0) {
      avatar.value = 'http://122.9.33.84:8000' + response.data.avatar + '?' + Date.now()
    } else {
      ElMessage.error(response.data.message)
    }
  })
}

async function fetchUserInfo() {
  if (!uid.value) {
    console.error('用户未登录，无法获取用户信息')
    return
  }
  try {
    const response = await axios({
      method: 'get',
      url: '/user/fetchProfile',
      params: { uid: uid.value }
    })
    if (response.data.code === 0) {
      userInfo.value = response.data.data
    } else {
      ElMessage.error(response.data.message)
      console.error('获取用户信息失败:', response.data.message)
      error.value.userInfo = response.data.message || '获取用户信息失败'
    }
  } catch (err) {
    console.error('获取用户信息错误:', err)
    error.value.userInfo = '网络错误，请稍后重试'
  }
}

async function fetchWorks() {
  if (!uid.value) return

  try {
    const response = await axios({
      method: 'get',
      url: '/user/fetchWorks',
      params: { uid: uid.value }
    })
    if (response.data.code === 0) {
      myWorks.value = response.data.data || []
    } else {
      console.error('获取作品列表失败:', response.data.message)
      error.value.works = response.data.message || '获取作品列表失败'
    }
  } catch (err) {
    console.error('获取作品列表错误:', err)
    error.value.works = '网络错误，请稍后重试'
  }
}

async function fetchLikes() {
  if (!uid.value) return

  try {
    const response = await axios({
      method: 'get',
      url: '/user/fetchLikes',
      params: { uid: uid.value }
    })
    if (response.data.code === 0) {
      likes.value = response.data.data || []
    } else {
      console.error('获取喜欢列表失败:', response.data.message)
      error.value.likes = response.data.message || '获取喜欢列表失败'
      likes.value = []
    }
  } catch (err) {
    console.error('获取喜欢列表错误:', err)
    error.value.likes = '网络错误，请稍后重试'
    likes.value = []
  }
}

async function fetchFavorites() {
  if (!uid.value) return

  try {
    const response = await axios({
      method: 'get',
      url: '/user/fetchFavorites',
      params: { uid: uid.value }
    })
    if (response.data.code === 0) {
      favorites.value = response.data.data || []
    } else {
      console.error('获取收藏列表失败:', response.data.message)
      error.value.favorites = response.data.message || '获取收藏列表失败'
      favorites.value = []
    }
  } catch (err) {
    console.error('获取收藏列表错误:', err)
    error.value.favorites = '网络错误，请稍后重试'
    favorites.value = []
  }
}

function goToEditProfile() {
  router.push({
    path: '/editProfile',
    query: {
      name: userInfo.value.name,
      description: userInfo.value.description,
    }
  });
}

async function sendMessage() {
  try {
    const response = await axios({
      method: 'post',
      url: 'user/contactRequest',
      data: {
        uid: currentUid,
        target_uid: uid.value,
      }
    })
    if (response.data.code === 0) {
      await router.push('/message');
    } else {
      ElMessage.error(response.data.message)
      console.log('失败：', response.data.message)
    }
  } catch (error) {
    console.error('失败：', error)
    ElMessage.error('失败')
  }
}

// 跳转到智能体详情页
function goToAgentDetail(agentId: number) {
  router.push({
    path: `/agentDetail/${agentId}`
  })
}

// 退出登录
function logout() {
  sessionStorage.clear()
  router.push('/login')
}

</script>

<template>
  <div class="profile-container">
    <!-- 个人信息头部 -->
    <div class="profile-header">
      <div class="profile-info">
        <div class="avatar-section">
          <img :src="avatar" :alt="userInfo.name" class="avatar">
        </div>
        <div class="info-section">
          <div class="user-name">{{ userInfo.name }}</div>
          <div class="user-account">{{ userInfo.account }}</div>
          <div class="user-description">{{ userInfo.description }}</div>
          <div class="user-stats">
            <div class="socialInfo-item">
              <span class="stat-value">{{ userInfo.following }}</span>
              <span class="stat-label">关注</span>
            </div>
            <div class="socialInfo-item">
              <span class="stat-value">{{ userInfo.followers }}</span>
              <span class="stat-label">粉丝</span>
            </div>
          </div>
        </div>
      </div>
      <!-- 添加设置按钮 -->
      <div class="profile-actions" v-if="uid === currentUid">
        <button class="edit-profile-btn" @click="goToEditProfile">
          <svg class="settings-icon" viewBox="0 0 24 24" fill="currentColor" width="18" height="18">
            <path d="M19.14 12.94c.04-.3.06-.61.06-.94 0-.32-.02-.64-.07-.94l2.03-1.58c.18-.14.23-.41.12-.61l-1.92-3.32c-.12-.22-.37-.29-.59-.22l-2.39.96c-.5-.38-1.03-.7-1.62-.94l-.36-2.54c-.04-.24-.24-.41-.48-.41h-3.84c-.24 0-.43.17-.47.41l-.36 2.54c-.59.24-1.13.57-1.62.94l-2.39-.96c-.22-.08-.47 0-.59.22L2.74 8.87c-.12.21-.08.47.12.61l2.03 1.58c-.05.3-.09.63-.09.94s.02.64.07.94l-2.03 1.58c-.18.14-.23.41-.12.61l1.92 3.32c.12.22.37.29.59.22l2.39-.96c.5.38 1.03.7 1.62.94l.36 2.54c.05.24.24.41.48.41h3.84c.24 0 .44-.17.47-.41l.36-2.54c.59-.24 1.13-.56 1.62-.94l2.39.96c.22.08.47 0 .59-.22l1.92-3.32c.12-.22.07-.47-.12-.61l-2.01-1.58zM12 15.6c-1.98 0-3.6-1.62-3.6-3.6s1.62-3.6 3.6-3.6 3.6 1.62 3.6 3.6-1.62 3.6-3.6 3.6z"/>
          </svg>
          <span>编辑资料</span>
        </button>
        <button class="logout-btn" v-if="uid === currentUid" @click="logout">
          <svg class="logout-icon" viewBox="0 0 24 24" fill="currentColor" width="18" height="18">
            <path d="M17 7l-1.41 1.41L18.17 11H8v2h10.17l-2.58 2.58L17 17l5-5zM4 5h8V3H4c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h8v-2H4V5z"/>
          </svg>
          <span>退出登录</span>
        </button>
      </div>
      <div class="profile-actions" v-if="uid !== currentUid">
        <button class="edit-profile-btn" @click="sendMessage">
          <svg class="settings-icon" viewBox="0 0 24 24" fill="currentColor" width="18" height="18">
            <path d="M20 2H4c-1.1 0-2 .9-2 2v18l4-4h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zm0 14H6l-2 2V4h16v12z"/>
          </svg>
          <span>私信</span>
        </button>
      </div>
    </div>

    <!-- 内容切换栏 -->
    <div class="content-tabs">
      <div 
        v-for="tab in tabs" 
        :key="tab.id"
        class="tab-item"
        :class="{ active: currentTab === tab.id }"
        @click="currentTab = tab.id"
      >
        {{ tab.name }}
      </div>
    </div>

    <!-- 内容展示区 -->
    <div class="content-section">
      <div v-if="curAgents.length === 0" class="no-content">
        <span v-if="currentTab === 'works'">您没有已发布的作品</span>
        <span v-else-if="currentTab === 'likes'">您还没有点赞任何作品，去社区看看吧</span>
        <span v-else-if="currentTab === 'favorites'">您还没有收藏任何作品，去社区看看吧</span>
        <span v-else>暂无相关内容</span>
      </div>
      <div v-else>
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
                  <el-main style="width: 210px; height: 150px; padding: 0;">
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
</template>

<style scoped>
.profile-container {
  padding: 20px;
  background: #f8f9fa;
  min-height: 100vh;
}

.profile-header {
  background: white;
  border-radius: 8px;
  padding: 30px;
  margin-bottom: 20px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  position: relative;
}

.profile-info {
  display: flex;
  gap: 30px;
  align-items: flex-start;
}

.avatar-section {
  flex-shrink: 0;
  display: flex;
  align-items: flex-start;
  gap: 20px;
}

.avatar {
  width: 160px;
  height: 160px;
  border-radius: 50%;
  object-fit: cover;
}

.info-section {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: flex-start;
  padding-top: 10px;
}

.user-name {
  font-size: 28px;
  font-weight: bold;
  color: #2c3e50;
  margin-bottom: 10px;
}

.user-account {
  font-size: 16px;
  color: #666;
  margin-bottom: 10px;
}

.user-description {
  color: #666;
  line-height: 1.6;
  margin-bottom: 20px;
  max-width: 600px;
}

.user-stats {
  display: flex;
  gap: 30px;
  margin-top: 20px;
}

.socialInfo-item {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.stat-value {
  font-size: 20px;
  font-weight: bold;
  color: #2c3e50;
}

.stat-label {
  font-size: 14px;
  color: #666;
}

.content-tabs {
  display: flex;
  background: white;
  border-radius: 8px;
  padding: 0 20px;
  margin-bottom: 20px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.tab-item {
  padding: 15px 20px;
  color: #666;
  cursor: pointer;
  position: relative;
  transition: all 0.3s ease;
}

.tab-item:hover {
  color: #2c3e50;
}

.tab-item.active {
  color: #2c3e50;
  font-weight: bold;
}

.tab-item.active::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  width: 100%;
  height: 2px;
  background: #2c3e50;
}

.content-section {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
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
  width: 330px;
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
  width: 200px;
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

.stat-item svg.like-icon {
  color: #e74c3c;
}

.stat-item svg.favorite-icon {
  color: #f1c40f;
}

/* 设置图标和按钮样式 */
.profile-actions {
  position: absolute;
  top: 30px;
  right: 30px;
  display: flex;
  gap: 12px;
}

.edit-profile-btn,
.logout-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  background: #2c3e50;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.3s ease;
}

.edit-profile-btn:hover,
.logout-btn:hover {
  background: #1e2b38;
}

.settings-icon,
.logout-icon {
  width: 18px;
  height: 18px;
}

.logout-btn {
  background: #e74c3c;
}

.logout-btn:hover {
  background: #c0392b;
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 15px;
  padding: 10px;
  background: transparent;
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

.no-content {
  text-align: center;
  color: #999;
  font-size: 25px;
  padding: 20px;
}
</style>