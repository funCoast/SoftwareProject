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

      <!-- 主导航菜单 -->
      <nav>
        <ul>
          <li
            v-for="item in filteredNavItems"
            :key="item.path"
            :class="{ active: cur === item.path || (item.children && route.path.startsWith(item.path)) }"
            @click="handleNavigation(item.path)"
          >
            <img :src="item.icon" :alt="item.label" class="nav-icon" />
            <span>{{ item.label }}</span>
          </li>
        </ul>
      </nav>
    </div>

    <!-- 管理后台侧边栏 -->
    <div v-if="route.path.startsWith('/admin')" class="admin-side-nav">
      <nav>
        <ul>
          <li
            v-for="item in adminMenuItems"
            :key="item.path"
            :class="{ active: route.path === item.path }"
            @click="router.push(item.path)"
          >
            <img :src="item.icon" :alt="item.label" class="nav-icon" />
            <span>{{ item.label }}</span>
          </li>
        </ul>
      </nav>
    </div>

    <!-- 主体区域 -->
    <div class="main-content" :class="{ 'with-admin-nav': route.path.startsWith('/admin') }">
      <router-view :avatar="avatar" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onBeforeMount, provide, computed } from 'vue'
import router from '../router'
import { useRoute } from 'vue-router'
import axios from 'axios'

const route = useRoute()
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
      avatar.value = 'http://101.201.208.165' + response.data.avatar + '?' + Date.now()
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
  children?: NavItem[]
}

// 管理后台菜单项
const adminMenuItems = [
  { path: '/admin/userManage', label: '用户管理', icon: 'https://api.iconify.design/material-symbols:manage-accounts.svg' },
  { path: '/admin/reviewAgent', label: '智能体审核', icon: 'https://api.iconify.design/material-symbols:rate-review.svg' },
  { path: '/admin/reportAgent', label: '举报处理', icon: 'https://api.iconify.design/material-symbols:report.svg' },
  { path: '/admin/publishAnno', label: '公告发布', icon: 'https://api.iconify.design/material-symbols:campaign.svg' }
]

// 导航配置项（更易维护）
const navItems = ref<NavItem[]>([
  { path: '/home', label: '首页', icon: 'https://api.iconify.design/material-symbols:home.svg' },
  { path: '/workspace', label: '工作空间', icon: 'https://api.iconify.design/material-symbols:dashboard.svg' },
  { path: '/community', label: '社区', icon: 'https://api.iconify.design/material-symbols:groups.svg' },
  { path: '/admin', label: '管理后台', icon: 'https://api.iconify.design/material-symbols:admin-panel-settings.svg' }
])

// 根据用户角色过滤导航项
const filteredNavItems = computed(() => {
  const role = localStorage.getItem('LingXi_role')
  if (role === 'admin') {
    return navItems.value
  } else {
    return navItems.value.filter(item => item.path !== '/admin')
  }
})

// 计算属性
const cur = ref('/home')

// 导航处理方法
function handleNavigation(path: string) {
  cur.value = path
  if (path === '/admin') {
    router.push('/admin/userManage')
  } else {
    router.push(path)
  }
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
  background-color: #fdfdfd;
  min-width: 0;
  min-height: 0;
}

.side-nav {
  width: 100px;
  background-color: #ffffff;
  padding: 20px 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  border-right: 1px solid #e0e0e0;
  z-index: 2;
  box-shadow: 2px 0 8px rgba(0, 0, 0, 0.05);
}

/* 用户信息区域样式 */
.user-section {
  padding: 20px;
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: 20px;
  width: 100%;
  border-bottom: 1px solid #eef2f7;
}

.avatar {
  width: 52px;
  height: 52px;
  border-radius: 50%;
  margin-bottom: 15px;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 3px 10px rgba(0, 0, 0, 0.1);
  border: 2px solid #ffffff;
}

.avatar:hover {
  transform: scale(1.08);
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.15);
}

.button-group {
  display: flex;
  flex-direction: column;
  gap: 12px;
  align-items: center;
  width: 100%;
}

.icon-button {
  width: 42px;
  height: 42px;
  background-color: #ffffff;
  border: 2px solid #4FAFFF;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
  box-shadow: 0 2px 6px rgba(79, 175, 255, 0.15);
}

.icon-button:hover {
  background-color: #4FAFFF;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(79, 175, 255, 0.25);
}

.icon-button:hover img {
  filter: brightness(0) invert(1);
}

.icon-button img {
  width: 20px;
  height: 20px;
  transition: all 0.3s ease;
}

nav {
  width: 100%;
  margin-top: 10px;
}

nav ul {
  list-style: none;
  margin: 0;
  padding: 0;
  width: 100%;
}

nav ul li {
  padding: 14px 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  color: #94a3b8;
  transition: all 0.3s ease;
  position: relative;
  margin: 4px 0;
}

nav ul li::before {
  content: '';
  position: absolute;
  left: 0;
  width: 4px;
  height: 0;
  background-color: #4FAFFF;
  transition: height 0.3s ease;
  border-radius: 0 4px 4px 0;
}

nav ul li:hover::before,
nav ul li.active::before {
  height: 100%;
}

nav ul li:hover,
nav ul li.active {
  background-color: #f1f5f9;
  color: #4FAFFF;
}

.nav-icon {
  width: 24px;
  height: 24px;
  display: block;
  margin-bottom: 6px;
  opacity: 0.7;
  transition: all 0.3s ease;
}

nav ul li:hover .nav-icon,
nav ul li.active .nav-icon {
  opacity: 1;
  transform: scale(1.1);
}

nav ul li span {
  font-size: 12px;
  display: block;
  line-height: 1.2;
  margin-top: 4px;
  font-weight: 500;
  transition: all 0.3s ease;
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
  flex: 1 1 0%;
  min-width: 0;
  min-height: 0;
  background: #fdfdfd;
  padding: 0 20px 0 20px;
  color: #333;
  overflow: auto; /* 修改为 auto 允许滚动 */
}

.admin-side-nav {
  width: 120px;
  background: #ffffff;
  border-right: 1px solid #e0e0e0;
  z-index: 1;
  box-shadow: 2px 0 8px rgba(0, 0, 0, 0.05);
}

.admin-side-nav nav {
  width: 100%;
  margin-top: 10px;
}

.admin-side-nav ul {
  list-style: none;
  margin: 0;
  padding: 0;
  width: 100%;
}

.admin-side-nav li {
  height: 72px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s ease;
  color: #94a3b8;
  position: relative;
  margin: 4px 0;
}

.admin-side-nav li::before {
  content: '';
  position: absolute;
  left: 0;
  width: 4px;
  height: 0;
  background-color: #4FAFFF;
  transition: height 0.3s ease;
  border-radius: 0 4px 4px 0;
}

.admin-side-nav li:hover::before,
.admin-side-nav li.active::before {
  height: 100%;
}

.admin-side-nav li:hover,
.admin-side-nav li.active {
  background-color: #f1f5f9;
  color: #4FAFFF;
}

.admin-side-nav .nav-icon {
  width: 24px;
  height: 24px;
  display: block;
  margin-bottom: 6px;
  opacity: 0.7;
  transition: all 0.3s ease;
}

.admin-side-nav li:hover .nav-icon,
.admin-side-nav li.active .nav-icon {
  opacity: 1;
  transform: scale(1.1);
}

.admin-side-nav span {
  font-size: 12px;
  display: block;
  line-height: 1.2;
  margin-top: 4px;
  font-weight: 500;
  transition: all 0.3s ease;
}

.main-content.with-admin-nav {
  margin-left: 120px;
}
</style>