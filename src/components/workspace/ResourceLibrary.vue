<script setup lang="ts">
import { ref } from 'vue'
import router from '../../router'

interface resource {
  id: number
  name: string
  description: string
  category: string
  icon: string
  type: string
  updateTime: string
}
const resources = ref<resource[]> ([
  {
    id: 1,
    name: '数据分析工作流',
    description: '完整的数据分析流程，包含数据清洗、转换和可视化',
    category: '数据分析',
    icon: 'https://picsum.photos/100/100?random=7',
    type: '工作流',
    updateTime: '2024-03-15'
  },
  {
    id: 2,
    name: '图像处理插件',
    description: '支持多种图像格式转换和基础处理功能',
    category: '图像处理',
    icon: 'https://picsum.photos/100/100?random=8',
    type: '插件',
    updateTime: '2024-03-14'
  },
  {
    id: 3,
    name: '机器学习知识库',
    description: '包含常用机器学习算法和最佳实践指南',
    category: '机器学习',
    icon: 'https://picsum.photos/100/100?random=9',
    type: '知识库',
    updateTime: '2024-03-13'
  },
  {
    id: 4,
    name: '自动化测试工作流',
    description: '完整的测试流程，包含单元测试和集成测试',
    category: '测试',
    icon: 'https://picsum.photos/100/100?random=10',
    type: '工作流',
    updateTime: '2024-03-12'
  },
  {
    id: 5,
    name: '代码格式化插件',
    description: '支持多种编程语言的代码格式化工具',
    category: '开发工具',
    icon: 'https://picsum.photos/100/100?random=11',
    type: '插件',
    updateTime: '2024-03-11'
  },
  {
    id: 6,
    name: '安全开发知识库',
    description: 'Web应用安全开发指南和最佳实践',
    category: '安全',
    icon: 'https://picsum.photos/100/100?random=12',
    type: '知识库',
    updateTime: '2024-03-10'
  }
])

function createWorkflow() {
  router.push('/workflow')
}
function createKnowledge() {
  // 处理创建知识库的逻辑
  console.log('创建知识库')
} 
</script>

<template>
  <div class="content">
    <!-- 顶部标题栏 -->
    <div class="header">
      <h2>资源库</h2>
      <el-dropdown>
        <button class="create-btn">
          <svg viewBox="0 0 24 24" fill="currentColor" width="20" height="20">
            <path d="M19 13h-6v6h-2v-6H5v-2h6V5h2v6h6v2z"/>
          </svg>
          创建资源
        </button>
        <template #dropdown>
          <el-dropdown-menu>
            <div>
            <el-dropdown-item class="dropdown-item" @click="createWorkflow">
              <svg viewBox="0 0 24 24" fill="currentColor" width="16" height="16">
                <path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm0 16H5V5h14v14zM7 10h2v7H7zm4-3h2v10h-2zm4 6h2v4h-2z"/>
              </svg>
              <span>工作流</span>
            </el-dropdown-item>
          </div>
            <el-dropdown-item @click="createKnowledge">
              <svg viewBox="0 0 24 24" fill="currentColor" width="16" height="16">
                <path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm0 16H5V5h14v14zM7 10h2v7H7zm4-3h2v10h-2zm4 6h2v4h-2z"/>
              </svg>
              <span>知识库</span>
            </el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>
    </div>

    <!-- 筛选栏 -->
    <div class="filter-bar">
      <select class="filter-select">
        <option value="create-time">按创建时间排序</option>
        <option value="name">按名称排序</option>
        <option value="modify-time">按修改时间排序</option>
      </select>
      <select class="filter-select">
        <option value="all">全部</option>
        <option value="workflow">工作流</option>
        <option value="plugin">插件</option>
        <option value="knowledge">知识库</option>
      </select>
      <div class="search-box">
        <svg viewBox="0 0 24 24" fill="currentColor" width="16" height="16">
          <path d="M15.5 14h-.79l-.28-.27C15.41 12.59 16 11.11 16 9.5 16 5.91 13.09 3 9.5 3S3 5.91 3 9.5 5.91 16 9.5 16c1.61 0 3.09-.59 4.23-1.57l.27.28v.79l5 4.99L20.49 19l-4.99-5zm-6 0C7.01 14 5 11.99 5 9.5S7.01 5 9.5 5 14 7.01 14 9.5 11.99 14 9.5 14z"/>
        </svg>
        <input type="text" placeholder="搜索资源...">
      </div>
    </div>

    <!-- 资源列表 -->
    <div class="resource-list">
      <div v-for="resource in resources" :key="resource.id" class="resource-card">
        <div class="resource-icon">
          <img :src="resource.icon" :alt="resource.name">
          <div class="resource-type">{{ resource.type }}</div>
        </div>
        <div class="resource-info">
          <h3>{{ resource.name }}</h3>
          <p>{{ resource.description }}</p>
          <div class="resource-meta">
            <span class="update-time">最后更新：{{ resource.updateTime }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.content {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.header h2 {
  margin: 0;
  color: #2c3e50;
  font-size: 24px;
}

.create-dropdown {
  position: relative;
}

.create-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background: #2c3e50;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.create-btn:hover {
  background: #34495e;
}

.filter-bar {
  display: flex;
  gap: 16px;
  margin-bottom: 20px;
  align-items: center;
}

.filter-select {
  padding: 8px 12px;
  border: 1px solid #e9ecef;
  border-radius: 6px;
  background: white;
  color: #2c3e50;
  cursor: pointer;
}

.search-box {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  background: white;
  border: 1px solid #e9ecef;
  border-radius: 6px;
  flex: 1;
  max-width: 300px;
}

.search-box input {
  border: none;
  outline: none;
  width: 100%;
  color: #2c3e50;
}

.resource-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 20px;
}

.resource-card {
  background: white;
  border-radius: 12px;
  padding: 16px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  transition: all 0.3s ease;
  display: flex;
  gap: 16px;
}

.resource-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0,0,0,0.1);
}

.resource-icon {
  position: relative;
  width: 80px;
  height: 80px;
  flex-shrink: 0;
}

.resource-icon img {
  width: 100%;
  height: 100%;
  border-radius: 50%;
  object-fit: cover;
}

.resource-type {
  position: absolute;
  bottom: 0;
  right: 0;
  background: #2c3e50;
  color: white;
  padding: 2px 6px;
  border-radius: 10px;
  font-size: 10px;
}

.resource-info {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
}

.resource-info h3 {
  margin: 0 0 8px 0;
  color: #2c3e50;
  font-size: 16px;
}

.resource-info p {
  margin: 0;
  color: #666;
  font-size: 13px;
  line-height: 1.5;
  display: -webkit-box;
  -webkit-box-orient: vertical;
  overflow: hidden;
  flex: 1;
}

.resource-meta {
  display: flex;
  justify-content: flex-end;
  margin-top: 8px;
}

.update-time {
  color: #95a5a6;
  font-size: 11px;
}
</style> 