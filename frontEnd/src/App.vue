<template>
  <div class="app-container">
    <!-- 侧边导航栏，在工作流画布页面隐藏 -->
    <div class="side-nav" v-if="!isWorkflowCanvas">
      <!-- 用户信息区域 -->
      <div class="user-section">
        <div class="user-info">
          <img :src="userAvatar" :alt="userName" class="avatar" @click="goToProfile">
          <span class="user-name">{{ userName }}</span>
        </div>
        <div class="message-icon">
          <i class="fas fa-envelope"></i>
          <i @click="navigateTo('/message')">
            <img src="https://api.iconify.design/material-symbols:chat.svg" alt="私信" class="nav-icon">
            <span class="message-badge">114514</span>
          </i>
        </div>
      </div>
      
      <!-- 导航菜单 -->
      <nav>
        <ul>
          <li :class="{ active: currentRoute === '/' }" @click="navigateTo('/')">
            <img src="https://api.iconify.design/material-symbols:home.svg" alt="首页" class="nav-icon">
            <span>首页</span>
          </li>
          <li :class="{ active: currentRoute === '/workspace' }" @click="navigateTo('/workspace')">
            <img src="https://api.iconify.design/material-symbols:dashboard.svg" alt="工作空间" class="nav-icon">
            <span>工作空间</span>
          </li>
          <li :class="{ active: currentRoute === '/community' }" @click="navigateTo('/community')">
            <img src="https://api.iconify.design/material-symbols:groups.svg" alt="社区" class="nav-icon">
            <span>社区</span>
          </li>
        </ul>
      </nav>
    </div>

    <!-- 主要内容区域 -->
    <div class="main-content" :class="{ 'full-width': isWorkflowCanvas }">
      <router-view></router-view>
    </div>
  </div>
</template>

<script>
export default {
  name: 'App',
  data() {
    return {
      currentRoute: 'home',
      userAvatar: 'https://picsum.photos/50/50?random=1',
      userName: 'AI开发者'
    }
  },
  computed: {
    isWorkflowCanvas() {
      return this.$route.path === '/workspace/workflow'
    }
  },
  methods: {
    navigateTo(route) {
      this.currentRoute = route
      this.$router.push(route)
    },
    goToProfile() {
      this.currentRoute = 'profile'
      this.$router.push('/profile')
    }
  }
}
</script>

<style>
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
  width: 240px;
  background: #2c3e50;
  color: white;
  padding: 20px;
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
  border-bottom: 1px solid #34495e;
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
</style>
