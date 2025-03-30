.nav-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 12px;
  color: #666;
  text-decoration: none;
  border-radius: 8px;
  transition: all 0.3s ease;
  position: relative;
}

.nav-item svg {
  width: 20px;
  height: 20px;
  color: #666;
}

.nav-item:hover {
  background: #f8f9fa;
  color: #2c3e50;
}

.nav-item:hover svg {
  color: #2c3e50;
}

.nav-item.active {
  background: #2c3e50;
  color: white;
}

.nav-item.active svg {
  color: white;
}

.message-badge {
  position: absolute;
  top: 0;
  right: 0;
  background: #e74c3c;
  color: white;
  font-size: 12px;
  padding: 2px 6px;
  border-radius: 10px;
  min-width: 18px;
  height: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
  transform: translate(25%, -25%);
}

<template>
  <nav class="nav-menu">
    <router-link to="/" class="nav-item" :class="{ active: currentPath === '/' }">
      <svg viewBox="0 0 24 24" fill="currentColor">
        <path d="M10 20v-6h4v6h5v-8h3L12 3 2 12h3v8z"/>
      </svg>
      首页
    </router-link>
    <router-link to="/workspace" class="nav-item" :class="{ active: currentPath === '/workspace' }">
      <svg viewBox="0 0 24 24" fill="currentColor">
        <path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm0 16H5V5h14v14z"/>
        <path d="M7 12h2v5H7zm4-7h2v3h-2zm4 2h2v7h-2z"/>
      </svg>
      工作台
    </router-link>
    <router-link to="/market" class="nav-item" :class="{ active: currentPath === '/market' }">
      <svg viewBox="0 0 24 24" fill="currentColor">
        <path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm0 16H5V5h14v14z"/>
        <path d="M7 7h10v2H7zm0 4h10v2H7zm0 4h7v2H7z"/>
      </svg>
      智能体市场
    </router-link>
    <router-link to="/messages" class="nav-item" :class="{ active: currentPath === '/messages' }">
      <svg viewBox="0 0 24 24" fill="currentColor" width="20" height="20">
        <path d="M20 2H4c-1.1 0-2 .9-2 2v18l4-4h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zm0 14H6l-2 2V4h16v12z"/>
      </svg>
      消息
      <span v-if="unreadCount > 0" class="message-badge">{{ unreadCount }}</span>
    </router-link>
    <router-link to="/profile" class="nav-item" :class="{ active: currentPath === '/profile' }">
      <svg viewBox="0 0 24 24" fill="currentColor">
        <path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/>
      </svg>
      个人中心
    </router-link>
  </nav>
</template>

<script>
export default {
  name: 'App',
  data() {
    return {
      currentPath: '/',
      unreadCount: 5 // 添加未读消息数量
    }
  },
  // ... existing code ...
}
</script> 