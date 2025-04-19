<script setup lang="ts">
import { ref } from 'vue'
import router from '../../router'

const currentView = ref<string>('agent')

function handleNavigation(dst: string) {
  if(dst === 'agentDevelopment') currentView.value = 'agent'
  else currentView.value = 'resource'
  
  router.push('/workspace/' + dst)
}
</script>

<template>
  <div class="workspace-container">
    <!-- 二级导航栏 -->
    <div class="sub-nav">
      <div class="sub-nav-item" :class="{ active: currentView === 'agent' }" @click="handleNavigation('agentDevelopment')">
        <svg viewBox="0 0 24 24" fill="currentColor" width="20" height="20">
          <path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm0 16H5V5h14v14z"/>
          <path d="M7 12h2v5H7zm4-7h2v3h-2zm4 2h2v7h-2z"/>
        </svg>
        智能体开发
      </div>
      <div class="sub-nav-item" :class="{ active: currentView === 'resource' }" @click="handleNavigation('resourceLibrary')">
        <svg viewBox="0 0 24 24" fill="currentColor" width="20" height="20">
          <path d="M20 6h-8l-2-2H4c-1.1 0-1.99.9-1.99 2L2 18c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V8c0-1.1-.9-2-2-2zm0 12H4V8h16v10z"/>
        </svg>
        资源库
      </div>
    </div>

    <!-- 内容区域 -->
    <router-view> </router-view>
  </div>
</template>

<style scoped>
.workspace-container {
  display: flex;
  height: 100%;
  background: #f8f9fa;
}

.sub-nav {
  width: 150px;
  background: white;
  padding: 20px 0;
  border-right: 1px solid #e9ecef;
}

.sub-nav-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 20px;
  color: #666;
  cursor: pointer;
  transition: all 0.3s ease;
}

.sub-nav-item:hover {
  background: #f8f9fa;
  color: #2c3e50;
}

.sub-nav-item.active {
  background: #2c3e50;
  color: white;
}
</style> 