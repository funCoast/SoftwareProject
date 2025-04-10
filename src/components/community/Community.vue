<template>
  <div class="community-container">
    <!-- 二级导航栏 -->
    <div class="sub-nav">
      <div class="sub-nav-item" :class="{ active: currentTag === 'all' }" @click="currentTag = 'all'">
        <svg viewBox="0 0 24 24" fill="currentColor" width="20" height="20">
          <path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm0 16H5V5h14v14z"/>
        </svg>
        全部
      </div>
      <div class="sub-nav-item" :class="{ active: currentTag === 'template' }" @click="currentTag = 'template'">
        <svg viewBox="0 0 24 24" fill="currentColor" width="20" height="20">
          <path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm0 16H5V5h14v14z"/>
          <path d="M7 7h10v2H7zm0 4h10v2H7zm0 4h7v2H7z"/>
        </svg>
        模板
      </div>
      <div class="sub-nav-item" :class="{ active: currentTag === '对话助手' }" @click="currentTag = '对话助手'">
        <svg viewBox="0 0 24 24" fill="currentColor" width="20" height="20">
          <path d="M20 2H4c-1.1 0-2 .9-2 2v18l4-4h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zm0 14H6l-2 2V4h16v12z"/>
        </svg>
        对话助手
      </div>
      <div class="sub-nav-item" :class="{ active: currentTag === '数据分析' }" @click="currentTag = '数据分析'">
        <svg viewBox="0 0 24 24" fill="currentColor" width="20" height="20">
          <path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm0 16H5V5h14v14z"/>
          <path d="M7 12h2v5H7zm4-7h2v3h-2zm4 2h2v7h-2z"/>
        </svg>
        数据分析
      </div>
      <div class="sub-nav-item" :class="{ active: currentTag === '开发工具' }" @click="currentTag = '开发工具'">
        <svg viewBox="0 0 24 24" fill="currentColor" width="20" height="20">
          <path d="M9.4 16.6L4.8 12l4.6-4.6L8 6l-6 6 6 6 1.4-1.4zm5.2 0l4.6-4.6-4.6-4.6L16 6l6 6-6 6-1.4-1.4z"/>
        </svg>
        开发工具
      </div>
      <div class="sub-nav-item" :class="{ active: currentTag === '图像处理' }" @click="currentTag = '图像处理'">
        <svg viewBox="0 0 24 24" fill="currentColor" width="20" height="20">
          <path d="M21 19V5c0-1.1-.9-2-2-2H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2zM8.5 13.5l2.5 3.01L14.5 12l4.5 6H5l3.5-4.5z"/>
        </svg>
        图像处理
      </div>
      <div class="sub-nav-item" :class="{ active: currentTag === '语音工具' }" @click="currentTag = '语音工具'">
        <svg viewBox="0 0 24 24" fill="currentColor" width="20" height="20">
          <path d="M12 14c1.66 0 3-1.34 3-3V5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3zm-1 4v2c0 .55-.45 1-1 1s-1-.45-1-1v-2H7c-.55 0-1 .45-1 1v2c0 1.1.9 2 2 2h10c1.1 0 2-.9 2-2v-2c0-.55-.45-1-1-1h-2v2c0 .55-.45 1-1 1s-1-.45-1-1v-2h-2z"/>
        </svg>
        语音工具
      </div>
    </div>

    <!-- 内容区域 -->
    <div class="content">
      <!-- 顶部标题栏 -->
      <div class="header">
        <h1>{{ currentTag === 'all' ? '全部' : currentTag === 'template' ? '模板' : currentTag }}</h1>
        <div class="header-right">
          <select class="filter-select">
            <option value="trend">按当前趋势</option>
            <option value="usage">按使用量</option>
            <option value="likes">按点赞量</option>
            <option value="favorites">按收藏量</option>
            <option value="time">按发布时间</option>
          </select>
          <div class="search-box">
            <svg viewBox="0 0 24 24" fill="currentColor" width="16" height="16">
              <path d="M15.5 14h-.79l-.28-.27C15.41 12.59 16 11.11 16 9.5 16 5.91 13.09 3 9.5 3S3 5.91 3 9.5 5.91 16 9.5 16c1.61 0 3.09-.59 4.23-1.57l.27.28v.79l5 4.99L20.49 19l-4.99-5zm-6 0C7.01 14 5 11.99 5 9.5S7.01 5 9.5 5 14 7.01 14 9.5 11.99 14 9.5 14z"/>
            </svg>
            <input type="text" placeholder="搜索智能体...">
          </div>
          <button class="publish-btn">
            <svg viewBox="0 0 24 24" fill="currentColor" width="20" height="20">
              <path d="M19 13h-6v6h-2v-6H5v-2h6V5h2v6h6v2z"/>
            </svg>
            发布智能体
          </button>
        </div>
      </div>

      <!-- 智能体列表 -->
      <div class="agent-list">
        <div v-for="agent in paginatedAgents" :key="agent.id" class="agent-card" @click="goToAgentDetail()">
          <div class="agent-image">
            <img :src="agent.image" :alt="agent.name">
            <div class="agent-category">{{ agent.category }}</div>
          </div>
          <div class="agent-info">
            <div class="agent-header">
              <h3>{{ agent.name }}</h3>
              <div class="agent-author">
                <img :src="agent.author.avatar" :alt="agent.author.name">
                <span>{{ agent.author.name }}</span>
              </div>
            </div>
            <p class="agent-description">{{ agent.description }}</p>
            <div class="agent-stats">
              <span class="stat-item" title="使用量">
                <svg class="usage-icon" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M13 3L4 14h7l-2 5 9-11h-7l2-5z"/>
                </svg>
                {{ agent.usage }}
              </span>
              <span class="stat-item" title="点赞量">
                <svg class="like-icon" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z"/>
                </svg>
                {{ agent.likes }}
              </span>
              <span class="stat-item" title="收藏量">
                <svg class="favorite-icon" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M17 3H7c-1.1 0-1.99.9-1.99 2L5 21l7-3 7 3V5c0-1.1-.9-2-2-2zm0 15l-5-2.18L7 18V5h10v13z"/>
                </svg>
                {{ agent.favorites }}
              </span>
            </div>
          </div>
        </div>
      </div>

      <!-- 分页控件 -->
      <div class="pagination">
        <button 
          :disabled="currentPage === 1"
          @click="currentPage--"
        >
          <svg viewBox="0 0 24 24" fill="currentColor">
            <path d="M15.41 7.41L14 6l-6 6 6 6 1.41-1.41L10.83 12z"/>
          </svg>
        </button>
        <span class="page-info">{{ currentPage }} / {{ totalPages }}</span>
        <button 
          :disabled="currentPage === totalPages"
          @click="currentPage++"
        >
          <svg viewBox="0 0 24 24" fill="currentColor">
            <path d="M10 6L8.59 7.41 13.17 12l-4.58 4.59L10 18l6-6z"/>
          </svg>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import router from '../../router'

const currentTag = ref('all')
const currentPage = ref(1)
const itemsPerPage = ref(20)

interface agent {
  id: number
  name: string
  category: string
  description: string
  image: string
  usage: string
  likes: string
  favorites: string
  isTemplate: boolean
  author: {
    name: string
    avatar: string
  }
}
const agents = ref<agent[]> ([
  // 模板智能体
  {
    id: 21,
    name: '通用对话模板',
    category: '对话助手',
    description: '适用于各类对话场景的基础模板，支持自定义角色和对话风格',
    image: 'https://picsum.photos/300/300?random=21',
    usage: '1.5k',
    likes: '890',
    favorites: '543',
    isTemplate: true,
    author: {
      name: '模板专家',
      avatar: 'https://picsum.photos/50/50?random=21'
    }
  },
  {
    id: 22,
    name: '数据分析模板',
    category: '数据分析',
    description: '标准数据分析流程模板，包含数据清洗、分析和可视化步骤',
    image: 'https://picsum.photos/300/300?random=22',
    usage: '1.2k',
    likes: '756',
    favorites: '432',
    isTemplate: true,
    author: {
      name: '数据专家',
      avatar: 'https://picsum.photos/50/50?random=22'
    }
  },
  // 对话助手
  {
    id: 23,
    name: '多语言翻译助手',
    category: '对话助手',
    description: '支持多种语言互译的智能助手，提供实时翻译和语言学习建议',
    image: 'https://picsum.photos/300/300?random=23',
    usage: '1.8k',
    likes: '980',
    favorites: '654',
    isTemplate: false,
    author: {
      name: '语言专家',
      avatar: 'https://picsum.photos/50/50?random=23'
    }
  },
  {
    id: 24,
    name: '写作助手',
    category: '对话助手',
    description: '智能写作辅助工具，提供写作建议、语法检查和内容优化',
    image: 'https://picsum.photos/300/300?random=24',
    usage: '1.6k',
    likes: '920',
    favorites: '580',
    isTemplate: false,
    author: {
      name: '写作专家',
      avatar: 'https://picsum.photos/50/50?random=24'
    }
  },
  // 数据分析
  {
    id: 25,
    name: '销售数据分析',
    category: '数据分析',
    description: '专业的销售数据分析工具，支持销售预测和客户行为分析',
    image: 'https://picsum.photos/300/300?random=25',
    usage: '1.3k',
    likes: '780',
    favorites: '450',
    isTemplate: false,
    author: {
      name: '销售专家',
      avatar: 'https://picsum.photos/50/50?random=25'
    }
  },
  {
    id: 26,
    name: '用户行为分析',
    category: '数据分析',
    description: '用户行为分析工具，提供用户画像和行为路径分析',
    image: 'https://picsum.photos/300/300?random=26',
    usage: '1.1k',
    likes: '690',
    favorites: '380',
    isTemplate: false,
    author: {
      name: '用户研究专家',
      avatar: 'https://picsum.photos/50/50?random=26'
    }
  },
  // 开发工具
  {
    id: 27,
    name: '代码审查助手',
    category: '开发工具',
    description: '智能代码审查工具，提供代码质量分析和优化建议',
    image: 'https://picsum.photos/300/300?random=27',
    usage: '950',
    likes: '580',
    favorites: '320',
    isTemplate: false,
    author: {
      name: '代码专家',
      avatar: 'https://picsum.photos/50/50?random=27'
    }
  },
  {
    id: 28,
    name: 'API文档生成器',
    category: '开发工具',
    description: '自动生成API文档的工具，支持多种编程语言和框架',
    image: 'https://picsum.photos/300/300?random=28',
    usage: '880',
    likes: '520',
    favorites: '290',
    isTemplate: false,
    author: {
      name: '文档专家',
      avatar: 'https://picsum.photos/50/50?random=28'
    }
  },
  // 图像处理
  {
    id: 29,
    name: '图像风格迁移',
    category: '图像处理',
    description: 'AI图像风格迁移工具，支持多种艺术风格转换',
    image: 'https://picsum.photos/300/300?random=29',
    usage: '920',
    likes: '650',
    favorites: '380',
    isTemplate: false,
    author: {
      name: '图像专家',
      avatar: 'https://picsum.photos/50/50?random=29'
    }
  },
  {
    id: 30,
    name: '图像修复工具',
    category: '图像处理',
    description: '智能图像修复工具，支持老照片修复和图像增强',
    image: 'https://picsum.photos/300/300?random=30',
    usage: '850',
    likes: '580',
    favorites: '320',
    isTemplate: false,
    author: {
      name: '图像专家',
      avatar: 'https://picsum.photos/50/50?random=30'
    }
  },
  // 语音工具
  {
    id: 31,
    name: '语音合成助手',
    category: '语音工具',
    description: '高质量语音合成工具，支持多种音色和情感表达',
    image: 'https://picsum.photos/300/300?random=31',
    usage: '780',
    likes: '520',
    favorites: '280',
    isTemplate: false,
    author: {
      name: '语音专家',
      avatar: 'https://picsum.photos/50/50?random=31'
    }
  },
  {
    id: 32,
    name: '语音降噪工具',
    category: '语音工具',
    description: '智能语音降噪工具，提供清晰的语音处理效果',
    image: 'https://picsum.photos/300/300?random=32',
    usage: '720',
    likes: '480',
    favorites: '250',
    isTemplate: false,
    author: {
      name: '语音专家',
      avatar: 'https://picsum.photos/50/50?random=32'
    }
  }
])
  
const filteredAgents = computed(() => {
  if (currentTag.value === 'all') {
    return agents.value
  }
  if (currentTag.value === 'template') {
    return agents.value.filter(agent => agent.isTemplate)
  }
  return agents.value.filter(agent => agent.category === currentTag.value)
})
const totalPages = computed(() => {
  return Math.ceil(filteredAgents.value.length / itemsPerPage.value)
})
const paginatedAgents = computed(() => {
  const start = (currentPage.value - 1) * itemsPerPage.value
  const end = start + itemsPerPage.value
  return filteredAgents.value.slice(start, end)
})

watch (
  () => currentTag,
  () => {
    currentPage.value = 1
  }
)

function goToAgentDetail() {
  router.push(`/agentDetail`)
}
  
</script>

<style scoped>
.community-container {
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

.header-right {
  display: flex;
  gap: 16px;
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

.publish-btn {
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

.publish-btn:hover {
  background: #34495e;
}

.agent-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
}

.agent-card {
  background: white;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
  cursor: pointer;
}

.agent-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
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

.agent-category {
  position: absolute;
  top: 10px;
  right: 10px;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  color: white;
  background: rgba(0,0,0,0.6);
}

.agent-info {
  padding: 16px;
}

.agent-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.agent-header h3 {
  margin: 0;
  color: #2c3e50;
  font-size: 16px;
}

.agent-author {
  display: flex;
  align-items: center;
  gap: 5px;
}

.agent-author img {
  width: 24px;
  height: 24px;
  border-radius: 50%;
}

.agent-author span {
  font-size: 12px;
  color: #666;
}

.agent-description {
  margin: 0 0 15px 0;
  color: #666;
  font-size: 14px;
  line-height: 1.5;
  display: -webkit-box;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.agent-stats {
  display: flex;
  justify-content: space-between;
  padding-top: 10px;
  border-top: 1px solid #eee;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 5px;
  color: #666;
  font-size: 13px;
  padding: 4px 8px;
  border-radius: 12px;
  background: #f8f9fa;
  transition: all 0.3s ease;
}

.stat-item:hover {
  background: #e9ecef;
}

.stat-item svg {
  width: 16px;
  height: 16px;
}

.stat-item svg.usage-icon {
  color: #e74c3c;
}

.stat-item svg.like-icon {
  color: #e74c3c;
}

.stat-item svg.favorite-icon {
  color: #f1c40f;
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 15px;
  margin-top: 30px;
  padding: 20px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.pagination button {
  background: #f8f9fa;
  border: none;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s ease;
  color: #2c3e50;
}

.pagination button svg {
  width: 20px;
  height: 20px;
  color: #2c3e50;
}

.pagination button:hover:not(:disabled) {
  background: #e9ecef;
  transform: scale(1.1);
}

.pagination button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.page-info {
  color: #666;
  font-size: 14px;
}
</style> 