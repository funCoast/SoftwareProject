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
      <div
          class="sub-nav-item"
          :class="{ active: currentView === 'agent' }"
          @click="handleNavigation('agentDevelopment')"
      >
        <img src="https://api.iconify.design/material-symbols:smart-toy.svg" alt="智能体开发" class="sub-icon" />
        智能体开发
      </div>
      <div
          class="sub-nav-item"
          :class="{ active: currentView === 'resource' }"
          @click="handleNavigation('resourceLibrary')"
      >
        <img src="https://api.iconify.design/material-symbols:folder.svg" alt="资源库" class="sub-icon" />
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
  height: 100vh;
  background: #fdfdfd;
  overflow: hidden;
}

.sub-nav {
  width: 120px;
  background: #ffffff;
  flex-direction: column;
  margin-left: 0;
  border-left: none;
  z-index: 2;
  border-right: 1px solid #e0e0e0;
  padding-left: -5px;
  position: relative;
  left: -1px;
  border-left: none;
}

.sub-nav-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 16px 0;
  width: 100%;
  color: #94a3b8;
  font-size: 13px;
  transition: all 0.3s ease;
  cursor: pointer;
  position: relative;
  margin: 4px 0;
  height: 72px;
  box-sizing: border-box;
}

.sub-nav-item::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  width: 4px;
  height: 100%;
  background-color: #4FAFFF;
  opacity: 0;
  transition: opacity 0.3s ease;
  border-radius: 0 4px 4px 0;
}

.sub-nav-item:hover::before,
.sub-nav-item.active::before {
  opacity: 1;
  height: 100%;
}

.sub-icon {
  width: 20px;
  height: 20px;
  opacity: 0.6;
  transition: opacity 0.3s ease;
}

.sub-nav-item:hover .sub-icon,
.sub-nav-item.active .sub-icon {
  opacity: 0.95;
}

.sub-nav-item:hover,
.sub-nav-item.active {
  color: #4FAFFF;
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