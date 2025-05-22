<template>
  <div class="app-container">
    <!-- 侧边导航栏 -->
    <div class="side-nav">
      <!-- 用户信息区域 -->
      <div class="user-section">
        <img :src="avatar" alt="avatar" class="avatar" @click="handleProfileNavigation" />
        <div class="button-group">
          <div class="icon-button" @click="toMessage">
            <img src="https://api.iconify.design/material-symbols:chat.svg" alt="私信" />
          </div>
          <div class="icon-button" @click="toDocument">
            <img src="https://api.iconify.design/material-symbols:menu-book.svg" alt="文档" />
          </div>
        </div>
      </div>

      <!-- 导航菜单 -->
      <nav>
        <ul>
          <li
            v-for="item in filteredNavItems"
            :key="item.path"
            :class="{ active: cur === item.path }"
            @click="handleNavigation(item.path)"
          >
            <img :src="item.icon" :alt="item.label" class="nav-icon" />
            <span>{{ item.label }}</span>
          </li>
        </ul>
      </nav>
    </div>

    <!-- 主体区域 -->
    <div class="main-content">
      <router-view :avatar="avatar" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onBeforeMount, provide, computed } from 'vue'
import router from '../router'
import axios from 'axios'

const avatar = ref('')
function refreshAvatar(newOne: string) {
  avatar.value = newOne
}
provide('avatar', avatar)
provide('refreshAvatar', refreshAvatar)

function getAvatar() {
  axios({
    method: 'get',
    url: 'user/getAvatar',
    params: {
      uid: localStorage.getItem('LingXi_uid')
    }
  }).then(function (response) {
    if (response.data.code === 0) {
      avatar.value = 'http://122.9.33.84:8000' + response.data.avatar + '?' + Date.now()
    } else {
      ElMessage.error(response.data.message)
    }
  })
}
onBeforeMount(() => {
  document.body.style.margin = '0'
  getAvatar()
})

interface NavItem {
  path: string
  label: string
  icon: string
}

// 导航配置项（更易维护）
const navItems = ref<NavItem[]>([
  { path: '/home', label: '首页', icon: 'https://api.iconify.design/material-symbols:home.svg' },
  { path: '/workspace', label: '工作空间', icon: 'https://api.iconify.design/material-symbols:dashboard.svg' },
  { path: '/community', label: '社区', icon: 'https://api.iconify.design/material-symbols:groups.svg' },
  { path: '/user-manage', label: '用户管理', icon: 'https://api.iconify.design/material-symbols:manage-accounts.svg' },
  { path: '/publish-anno', label: '公告管理', icon: 'https://api.iconify.design/material-symbols:announcement.svg' },
  { path: '/review-agent', label: '智能体审核', icon: 'https://api.iconify.design/material-symbols:check-circle.svg' },
  { path: '/report-agent', label: '智能体举报', icon: 'https://api.iconify.design/material-symbols:check-circle.svg' }
])

// 根据用户角色过滤导航项
const filteredNavItems = computed(() => {
  const role = localStorage.getItem('role')
  if (role === 'admin') {
    return navItems.value.filter(item =>
        item.path !== '/workspace'
    )
  } else {
    return navItems.value.filter(item =>
      !['/publish-anno', '/review-agent', '/user-manage', '/report-agent'].includes(item.path)
    )
  }
})

// 计算属性
const cur = ref('/home')

// 导航处理方法
function handleNavigation(path: string) {
  cur.value = path
  router.push(path)
}

function handleProfileNavigation() {
  router.push(`/profile/${localStorage.getItem('LingXi_uid')}`)
}
function toMessage() {
  router.push('/message')
}

// 添加文档导航方法
function toDocument() {
  router.push('/document')
}
</script>

<template>
  <div class="app-container">
    <!-- 侧边导航栏 -->
    <div class="side-nav">
      <!-- 用户信息区域 -->
      <div class="user-section">
        <div class="user-info">
          <img :src="avatar" alt="avatar" class="avatar" @click="handleProfileNavigation">
        </div>
        <div class="action-buttons">
          <div class="action-button" @click="toMessage">
            <img src="https://api.iconify.design/material-symbols:chat.svg" alt="私信" class="nav-icon">
          </div>
          <div class="action-button" @click="toDocument">
            <img src="https://api.iconify.design/material-symbols:menu-book.svg" alt="使用文档" class="nav-icon">
          </div>
        </div>
      </div>

      <!-- 导航菜单 -->
      <nav>
        <ul>
          <li v-for="item in filteredNavItems" :key="item.path" :class="{ active: cur === item.path }" @click="handleNavigation(item.path)">
            <img :src="item.icon" :alt="item.label" class="nav-icon">
            <span>{{ item.label }}</span>
          </li>
        </ul>
      </nav>
    </div>

    <!-- 主要内容区域 -->
    <div class="main-content">
      <router-view :avatar="avatar"></router-view>
    </div>
  </div>
</template>

<style scoped>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #2c3e50;
}

.app-container {
  display: flex;
  height: 100vh;
  background-color: #fdfdfd; /* 页面主背景：乳白色 */
}

.side-nav {
  width: 100px;
  background-color: transparent; /* 原蓝色背景去除 */
  padding: 20px 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  border-right: 1px solid #e0e0e0; /* 添加右侧浅灰边框 */
}

/* 用户信息区域样式 */
.user-section {
  padding: 20px;
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: 20px;
}

.avatar {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  margin-bottom: 12px;
  cursor: pointer;
  transition: transform 0.3s ease;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1); /* 头像立体感 */
}
.avatar:hover {
  transform: scale(1.1);
}

.button-group {
  display: flex;
  flex-direction: column;
  gap: 10px;
  align-items: center;
}

.icon-button {
  width: 40px;
  height: 40px;
  background-color: white;
  border: 2px solid #4FAFFF;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.08); /* 阴影增加立体感 */
}
.icon-button:hover {
  background-color: #e6f3ff;
  transform: scale(1.05);
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.15);
}

.icon-button img {
  width: 18px;
  height: 18px;
  filter: none;
  opacity: 0.8;
}

nav {
  width: 100%;
  margin-top: 16px;
}

nav ul {
  list-style: none;
  margin: 0;
  padding: 0;
  width: 100%;
}

nav ul li {
  padding: 12px 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;

  border-bottom: 1px solid #cce0f3;  /* ✅ 更深一点蓝 */
  cursor: pointer;
  color: #4FAFFF;
  transition: background-color 0.3s ease, color 0.3s ease;
}

nav ul li:last-child {
  border-bottom: none;
}

nav ul li:hover,
nav ul li.active {
  background-color: #b3d9f9; /* ✅ 更深一点的蓝色，比 d6ecfb 更明显 */
  color: #1277d3;           /* ✅ 更有层次的深蓝字体 */
}

.nav-icon {
  width: 24px;
  height: 24px;
  display: block;
  margin-bottom: 6px;
  opacity: 0.6; /* 默认浅灰色 */
  transition: opacity 0.3s ease;
  filter: none; /* ✅ 移除反转、变白逻辑 */
}

nav ul li:hover .nav-icon,
nav ul li.active .nav-icon {
  opacity: 0.95; /* ✅ 更深的灰色 */
}

nav ul li span {
  font-size: 12px;
  display: block;
  line-height: 1.2;
  margin-top: 2px;
}

.menu-group {
  width: 80%;
  background-color: white;
  border: 1px solid #4FAFFF;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  padding: 8px 0;
  display: flex;
  flex-direction: column;
  align-items: stretch;
}

.main-content {
  flex: 1;
  background: #fdfdfd;
  overflow-y: auto;
  padding: 24px;
  color: #333;
}
</style>