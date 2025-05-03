<script setup lang="ts">
import { ref, onBeforeMount, provide } from 'vue'
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
      uid: sessionStorage.getItem('uid')
    }
  }).then(function (response) {
    if (response.data.code === 0) {
      avatar.value = 'http://127.0.0.1:8000' + response.data.avatar
      console.log(avatar.value)
    } else {
      alert(response.data.message)
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
  {
    path: '/home',
    label: '首页',
    icon: 'https://api.iconify.design/material-symbols:home.svg'
  },
  {
    path: '/workspace',
    label: '工作空间',
    icon: 'https://api.iconify.design/material-symbols:dashboard.svg'
  },
  {
    path: '/community',
    label: '社区',
    icon: 'https://api.iconify.design/material-symbols:groups.svg'
  }
])

// 计算属性
const cur = ref('/home')

// 导航处理方法
function handleNavigation(path: string) {
  cur.value = path
  router.push(path)
}

function handleProfileNavigation() {
  router.push(`/profile/${sessionStorage.getItem('uid')}`)
}
function toMessage() {
  router.push('/message')
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
        <div class="message-icon">
          <i class="fas fa-envelope"></i>
          <i @click="toMessage">
            <img src="https://api.iconify.design/material-symbols:chat.svg" alt="私信" class="nav-icon">
            <span class="message-badge">114514</span>
          </i>
        </div>
      </div>

      <!-- 导航菜单 -->
      <nav>
        <ul>
          <li v-for="item in navItems" :key="item.path" :class="{ active: cur === item.path }" @click="handleNavigation(item.path)">
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
}

.side-nav {
  width: 100px;
  background: #2c3e50;
  color: white;
  padding: 6px;
  display: flex;
  flex-direction: column;
  gap: 30px;
}

.main-content {
  flex: 1;
  overflow: auto;
  transition: margin-left 0.3s;
}

.main-content.full-width {
  margin-left: 0;
}

/* 用户信息区域样式 */
.user-section {
  padding: 20px;
  display: flex;
  flex-direction: column;
  align-items: center;
  border-bottom: 1px solid #4f6f8f;
}

.user-info {
  margin-bottom: 15px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

.avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  cursor: pointer;
  transition: transform 0.3s ease;
}

.avatar:hover {
  transform: scale(1.1);
}

.user-name {
  color: #fff;
  font-size: 14px;
  text-align: center;
}

.message-icon {
  position: relative;
  font-size: 24px;
  color: #fff;
  cursor: pointer;
  padding: 10px;
  border-radius: 50%;
  transition: all 0.3s ease;
  background-color: #34495e;
}

.message-icon:hover {
  background-color: #2c3e50;
  transform: scale(1.1);
}

.message-badge {
  position: absolute;
  top: -5px;
  right: -5px;
  background-color: #e74c3c;
  color: white;
  font-size: 12px;
  padding: 2px 6px;
  border-radius: 10px;
  min-width: 18px;
  text-align: center;
}

.side-nav nav ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.side-nav nav ul li {
  padding: 15px 20px;
  color: #fff;
  cursor: pointer;
  display: flex;
  align-items: center;
  transition: background-color 0.3s;
}

.side-nav nav ul li:hover {
  background-color: #34495e;
}

.side-nav nav ul li.active {
  background-color: #34495e;
}

.side-nav nav ul li i {
  margin-right: 10px;
  width: 20px;
}

.nav-icon {
  width: 24px;
  height: 24px;
  filter: brightness(0) invert(1);
  opacity: 0.8;
  transition: opacity 0.3s;
}

nav ul li {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 24px;
  cursor: pointer;
  transition: all 0.3s;
}

nav ul li:hover .nav-icon,
nav ul li.active .nav-icon {
  opacity: 1;
}

.app-container {
  /* 添加安全区域适配 */
  height: 100vh;
  height: calc(var(--vh, 1vh) * 100);
}

/* 添加过渡动画 */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* 响应式优化 */
@media (max-width: 768px) {
  .side-nav {
    width: 180px;
    padding: 15px;

    nav ul li {
      padding: 12px 15px;
    }
  }
}
</style>