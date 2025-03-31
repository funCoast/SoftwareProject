<template>
  <div class="content">
    <!-- 顶部标题栏 -->
    <div class="header">
      <h1>智能体开发</h1>
      <button class="create-btn">
        <svg viewBox="0 0 24 24" fill="currentColor" width="20" height="20">
          <path d="M19 13h-6v6h-2v-6H5v-2h6V5h2v6h6v2z"/>
        </svg>
        创建智能体
      </button>
    </div>

    <!-- 筛选栏 -->
    <div class="filter-bar">
      <select class="filter-select">
        <option value="create-time">按创建时间排序</option>
        <option value="name">按名称排序</option>
        <option value="modify-time">按修改时间排序</option>
      </select>
      <select class="filter-select">
        <option value="all">默认</option>
        <option value="published">已发布</option>
        <option value="unpublished">未发布</option>
      </select>
      <div class="search-box">
        <svg viewBox="0 0 24 24" fill="currentColor" width="16" height="16">
          <path d="M15.5 14h-.79l-.28-.27C15.41 12.59 16 11.11 16 9.5 16 5.91 13.09 3 9.5 3S3 5.91 3 9.5 5.91 16 9.5 16c1.61 0 3.09-.59 4.23-1.57l.27.28v.79l5 4.99L20.49 19l-4.99-5zm-6 0C7.01 14 5 11.99 5 9.5S7.01 5 9.5 5 14 7.01 14 9.5 11.99 14 9.5 14z"/>
        </svg>
        <input type="text" placeholder="搜索智能体...">
      </div>
    </div>

    <!-- 智能体列表 -->
    <div class="agent-list">
      <div v-for="agent in agents" :key="agent.id" class="agent-card">
        <div class="agent-image">
          <img :src="agent.image" :alt="agent.name">
          <div class="agent-status" :class="agent.status">{{ agent.statusText }}</div>
        </div>
        <div class="agent-info">
          <h3>{{ agent.name }}</h3>
          <p>{{ agent.description }}</p>
          <div class="agent-meta">
            <span class="category">{{ agent.category }}</span>
            <span class="update-time">最后更新：{{ agent.updateTime }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
interface agent {
  id: number
  name: string
  description: string
  category: string
  image: string
  status: string
  statusText: string
  updateTime: string
}
const agents = ref<agent[]> ([
  {
    id: 1,
    name: 'AI助手',
    description: '智能对话助手，支持多轮对话和上下文理解',
    category: '对话助手',
    image: 'https://picsum.photos/300/300?random=1',
    status: 'published',
    statusText: '已发布',
    updateTime: '2024-03-15'
  },
  {
    id: 2,
    name: '数据分析师',
    description: '专业的数据分析工具，支持多种数据可视化',
    category: '数据分析',
    image: 'https://picsum.photos/300/300?random=2',
    status: 'draft',
    statusText: '草稿',
    updateTime: '2024-03-14'
  },
  {
    id: 3,
    name: '创意写作',
    description: 'AI写作助手，支持多种文体和风格',
    category: '写作助手',
    image: 'https://picsum.photos/300/300?random=3',
    status: 'review',
    statusText: '审核中',
    updateTime: '2024-03-13'
  },
  {
    id: 4,
    name: '代码助手',
    description: '编程辅助工具，支持多种编程语言',
    category: '开发工具',
    image: 'https://picsum.photos/300/300?random=4',
    status: 'published',
    statusText: '已发布',
    updateTime: '2024-03-12'
  },
  {
    id: 5,
    name: '图像处理',
    description: '专业的图像处理工具，支持多种编辑功能',
    category: '图像工具',
    image: 'https://picsum.photos/300/300?random=5',
    status: 'draft',
    statusText: '草稿',
    updateTime: '2024-03-11'
  },
  {
    id: 6,
    name: '语音助手',
    description: '智能语音助手，支持语音识别和合成',
    category: '语音工具',
    image: 'https://picsum.photos/300/300?random=6',
    status: 'review',
    statusText: '审核中',
    updateTime: '2024-03-10'
  }
])
</script>

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

.header h1 {
  margin: 0;
  color: #2c3e50;
  font-size: 24px;
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

.agent-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
}

.agent-card {
  background: white;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  transition: all 0.3s ease;
}

.agent-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0,0,0,0.1);
}

.agent-image {
  position: relative;
  width: 100%;
  padding-top: 75%;
}

.agent-image img {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.agent-status {
  position: absolute;
  top: 10px;
  right: 10px;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  color: white;
}

.agent-status.published {
  background: #2ecc71;
}

.agent-status.draft {
  background: #95a5a6;
}

.agent-status.review {
  background: #f1c40f;
}

.agent-info {
  padding: 16px;
}

.agent-info h3 {
  margin: 0 0 8px 0;
  color: #2c3e50;
}

.agent-info p {
  margin: 0 0 12px 0;
  color: #666;
  font-size: 14px;
  line-height: 1.5;
}

.agent-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 12px;
  color: #95a5a6;
}

.category {
  background: #f8f9fa;
  padding: 2px 8px;
  border-radius: 12px;
}
</style> 