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
  height: 100vh; /* 高度占满整屏 */
  background: #fdfdfd;
  overflow: hidden;
}

.sub-nav {
  width: 120px; /* ✅ 与 community 页面统一宽度 */
  background: #ffffff;
  padding: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  height: 100%; /* ✅ 占满父容器高度 */
  border-right: 1px solid #e0e0e0;
  box-sizing: border-box;
  position: relative;
  left: -1px; /* ✅ 贴合主菜单，避免间隙 */
}

.sub-nav-item {
  width: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  padding: 12px 0;
  font-size: 12px;
  color: #4FAFFF;
  cursor: pointer;
  transition: all 0.3s ease;
  border-bottom: 1px solid #cce0f3; /* ✅ 增加分割线 */
}

.sub-nav-item:last-child {
  border-bottom: none;
}

.sub-nav-item.active,
.sub-nav-item:hover {
  background-color: #b3d9f9; /* 与 main/community 统一 */
  color: #1277d3;
}

.sub-nav-item svg {
  fill: #909399;
  opacity: 0.85;
  transition: fill 0.3s ease;
}

.sub-nav-item.active svg,
.sub-nav-item:hover svg {
  fill: #000000;
  opacity: 1;
}

.create-agent,
.create-resource {
  position: absolute;
  bottom: 24px;
  right: 24px;
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  background: #4FAFFF;
  color: white;
  border: none;
  border-radius: 10px;
  font-size: 14px;
  cursor: pointer;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.12);
  transition: all 0.3s ease;
}

.create-agent:hover,
.create-resource:hover {
  background: #1277d3;
  transform: translateY(-2px);
}

.create-agent svg,
.create-resource svg {
  width: 18px;
  height: 18px;
}

</style>