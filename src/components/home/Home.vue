<script setup lang="ts">
import { ref, computed, watch } from 'vue'

const currentNoticeTab = ref<string>('review')
const currentAgentTab = ref<string>('hot')
const currentPage = ref(1)
const itemsPerPage = ref(6)

interface notice {
  id: number
  title: string
  content: string
  time: string
}
const reviewNotices = ref<notice[]> ([
  {
    id: 1,
    title: '智能体审核通过',
    content: '您的智能体"AI助手"已通过审核，现已上线智能体市场。该智能体具有强大的自然语言处理能力，支持多轮对话和上下文理解，可以为用户提供智能问答、任务规划、信息检索等服务。系统对其进行了全面的安全性和稳定性测试，确保其能够安全可靠地为用户提供服务。',
    time: '2024-03-15 14:30'
  },
  {
    id: 2,
    title: '智能体更新提醒',
    content: '您的智能体"数据分析师"需要更新到最新版本。新版本增加了更多强大的数据分析功能，包括高级数据可视化、预测分析、机器学习模型训练等。同时优化了用户界面，提升了操作体验。建议您及时更新以获取最新功能和性能提升。',
    time: '2024-03-14 16:45'
  },
  {
    id: 3,
    title: '新智能体上线',
    content: '您的智能体"创意写作助手"已成功上线。该智能体采用最新的GPT模型，支持多种文体和风格，可以生成高质量的文章、故事、诗歌等。它能够理解用户的需求，提供个性化的写作建议，并支持多语言创作。欢迎广大用户体验新功能，提供宝贵意见。',
    time: '2024-03-13 09:15'
  }
])
const systemNotices = ref<notice[]> ([
  {
    id: 1,
    title: '系统维护通知',
    content: '系统将于今晚22:00-23:00进行例行维护。维护期间部分功能可能暂时无法使用，包括智能体发布等。我们将在维护完成后第一时间恢复服务，给您带来的不便敬请谅解。',
    time: '2025-04-13 9:37'
  },
  {
    id: 2,
    title: '新功能上线',
    content: '智能体市场新增智能体克隆功能。用户可以将模板智能体直接克隆到个人工作空间进行二次创作。',
    time: '2025-04-13 9:43'
  },
  {
    id: 3,
    title: '社区活动',
    content: '智能体开发者社区将于下周二举办线下分享会。欢迎广大开发者积极参与，共同探讨智能体技术的发展方向。',
    time: '2025-04-13 9:45'
  }
])
  
interface agent {
  id: number
  name: string
  category: string
  description: string
  icon: string
  image: string
  usage: string
  likes: string
  favorites: string
  author: {
    name: string
    avatar: string
  }
}
const hotAgents = ref<agent[]> ([
  {
    id: 1,
    name: 'AI助手',
    category: '对话助手',
    description: '智能对话助手，支持多轮对话和上下文理解，可进行自然语言交互',
    icon: 'fas fa-robot',
    image: 'https://picsum.photos/300/300?random=1',
    usage: '2.3k',
    likes: '1.2k',
    favorites: '856',
    author: {
      name: 'AI开发者',
      avatar: 'https://picsum.photos/50/50?random=1'
    }
  },
  {
    id: 2,
    name: '数据分析师',
    category: '数据分析',
    description: '专业的数据分析工具，支持多种数据可视化和预测分析',
    icon: 'fas fa-chart-line',
    image: 'https://picsum.photos/300/300?random=2',
    usage: '1.8k',
    likes: '980',
    favorites: '654',
    author: {
      name: '数据专家',
      avatar: 'https://picsum.photos/50/50?random=2'
    }
  },
  {
    id: 3,
    name: '创意写作',
    category: '写作助手',
    description: 'AI写作助手，支持多种文体和风格，可生成高质量文章',
    icon: 'fas fa-pen-fancy',
    image: 'https://picsum.photos/300/300?random=3',
    usage: '1.5k',
    likes: '890',
    favorites: '543',
    author: {
      name: '写作达人',
      avatar: 'https://picsum.photos/50/50?random=3'
    }
  },
  {
    id: 4,
    name: '代码助手',
    category: '开发工具',
    description: '编程辅助工具，支持多种编程语言，提供代码建议和调试',
    icon: 'fas fa-code',
    image: 'https://picsum.photos/300/300?random=4',
    usage: '1.2k',
    likes: '756',
    favorites: '432',
    author: {
      name: '程序猿',
      avatar: 'https://picsum.photos/50/50?random=4'
    }
  },
  {
    id: 5,
    name: '图像处理',
    category: '图像工具',
    description: '专业的图像处理工具，支持多种图像编辑和优化功能',
    icon: 'fas fa-image',
    image: 'https://picsum.photos/300/300?random=5',
    usage: '980',
    likes: '678',
    favorites: '321',
    author: {
      name: '图像专家',
      avatar: 'https://picsum.photos/50/50?random=5'
    }
  },
  {
    id: 6,
    name: '语音助手',
    category: '语音工具',
    description: '智能语音助手，支持语音识别和合成，提供语音交互',
    icon: 'fas fa-microphone',
    image: 'https://picsum.photos/300/300?random=6',
    usage: '850',
    likes: '567',
    favorites: '234',
    author: {
      name: '语音专家',
      avatar: 'https://picsum.photos/50/50?random=6'
    }
  },
  {
    id: 7,
    name: '数学助手',
    category: '教育工具',
    description: '智能数学解题助手，支持多种数学问题的解答和讲解',
    icon: 'fas fa-square-root-alt',
    image: 'https://picsum.photos/300/300?random=19',
    usage: '1.1k',
    likes: '789',
    favorites: '456',
    author: {
      name: '数学老师',
      avatar: 'https://picsum.photos/50/50?random=19'
    }
  },
  {
    id: 8,
    name: '化学助手',
    category: '教育工具',
    description: '化学实验模拟和知识讲解，支持化学反应预测',
    icon: 'fas fa-flask',
    image: 'https://picsum.photos/300/300?random=20',
    usage: '920',
    likes: '678',
    favorites: '345',
    author: {
      name: '化学专家',
      avatar: 'https://picsum.photos/50/50?random=20'
    }
  },
  {
    id: 9,
    name: '物理助手',
    category: '教育工具',
    description: '物理实验模拟和知识讲解，支持物理计算和预测',
    icon: 'fas fa-atom',
    image: 'https://picsum.photos/300/300?random=21',
    usage: '880',
    likes: '645',
    favorites: '321',
    author: {
      name: '物理专家',
      avatar: 'https://picsum.photos/50/50?random=21'
    }
  },
  {
    id: 10,
    name: '生物助手',
    category: '教育工具',
    description: '生物知识讲解和实验模拟，支持生物过程分析',
    icon: 'fas fa-dna',
    image: 'https://picsum.photos/300/300?random=22',
    usage: '850',
    likes: '623',
    favorites: '312',
    author: {
      name: '生物专家',
      avatar: 'https://picsum.photos/50/50?random=22'
    }
  },
  {
    id: 11,
    name: '历史助手',
    category: '教育工具',
    description: '历史知识讲解和事件分析，支持历史事件模拟',
    icon: 'fas fa-landmark',
    image: 'https://picsum.photos/300/300?random=23',
    usage: '780',
    likes: '567',
    favorites: '289',
    author: {
      name: '历史专家',
      avatar: 'https://picsum.photos/50/50?random=23'
    }
  },
  {
    id: 12,
    name: '地理助手',
    category: '教育工具',
    description: '地理知识讲解和地图分析，支持地理信息查询',
    icon: 'fas fa-globe-americas',
    image: 'https://picsum.photos/300/300?random=24',
    usage: '760',
    likes: '543',
    favorites: '278',
    author: {
      name: '地理专家',
      avatar: 'https://picsum.photos/50/50?random=24'
    }
  }
])

const followingAgents = ref<agent[]> ([
  {
    id: 1,
    name: '个人助手',
    category: '生活助手',
    description: '个性化AI助手，提供生活服务和日程管理',
    icon: 'fas fa-user-astronaut',
    image: 'https://picsum.photos/300/300?random=7',
    usage: '800',
    likes: '456',
    favorites: '234',
    author: {
      name: '生活达人',
      avatar: 'https://picsum.photos/50/50?random=7'
    }
  },
  {
    id: 2,
    name: '健康顾问',
    category: '健康管理',
    description: '智能健康管理助手，提供饮食建议和运动计划',
    icon: 'fas fa-heartbeat',
    image: 'https://picsum.photos/300/300?random=8',
    usage: '750',
    likes: '420',
    favorites: '210',
    author: {
      name: '健康专家',
      avatar: 'https://picsum.photos/50/50?random=8'
    }
  },
  {
    id: 3,
    name: '理财顾问',
    category: '财务管理',
    description: '智能理财助手，提供投资建议和理财规划',
    icon: 'fas fa-chart-pie',
    image: 'https://picsum.photos/300/300?random=9',
    usage: '680',
    likes: '380',
    favorites: '190',
    author: {
      name: '理财专家',
      avatar: 'https://picsum.photos/50/50?random=9'
    }
  },
  {
    id: 4,
    name: '学习助手',
    category: '教育工具',
    description: '智能学习助手，提供知识讲解和习题辅导',
    icon: 'fas fa-graduation-cap',
    image: 'https://picsum.photos/300/300?random=10',
    usage: '920',
    likes: '580',
    favorites: '320',
    author: {
      name: '教育专家',
      avatar: 'https://picsum.photos/50/50?random=10'
    }
  },
  {
    id: 5,
    name: '旅行规划',
    category: '旅游助手',
    description: '智能旅行规划助手，提供行程建议和攻略',
    icon: 'fas fa-plane',
    image: 'https://picsum.photos/300/300?random=11',
    usage: '650',
    likes: '350',
    favorites: '180',
    author: {
      name: '旅行达人',
      avatar: 'https://picsum.photos/50/50?random=11'
    }
  },
  {
    id: 6,
    name: '美食推荐',
    category: '美食助手',
    description: '智能美食推荐助手，提供菜谱和餐厅推荐',
    icon: 'fas fa-utensils',
    image: 'https://picsum.photos/300/300?random=12',
    usage: '780',
    likes: '450',
    favorites: '240',
    author: {
      name: '美食专家',
      avatar: 'https://picsum.photos/50/50?random=12'
    }
  }
])

const favoriteAgents = ref<agent[]> ([
{
  id: 1,
  name: '翻译助手',
  category: '语言工具',
  description: '多语言翻译，支持多种语言互译和实时翻译',
  icon: 'fas fa-language',
  image: 'https://picsum.photos/300/300?random=13',
  usage: '900',
  likes: '567',
  favorites: '345',
  author: {
    name: '语言专家',
    avatar: 'https://picsum.photos/50/50?random=13'
  }
},
{
  id: 2,
  name: '音乐创作',
  category: '音乐工具',
  description: 'AI音乐创作助手，支持作曲和编曲',
  icon: 'fas fa-music',
  image: 'https://picsum.photos/300/300?random=14',
  usage: '720',
  likes: '480',
  favorites: '280',
  author: {
    name: '音乐人',
    avatar: 'https://picsum.photos/50/50?random=14'
  }
},
{
  id: 3,
  name: '视频剪辑',
  category: '视频工具',
  description: '智能视频剪辑助手，提供视频编辑建议',
  icon: 'fas fa-video',
  image: 'https://picsum.photos/300/300?random=15',
  usage: '850',
  likes: '520',
  favorites: '310',
  author: {
    name: '视频专家',
    avatar: 'https://picsum.photos/50/50?random=15'
  }
},
{
  id: 4,
  name: '3D建模',
  category: '设计工具',
  description: 'AI辅助3D建模，提供建模建议和优化',
  icon: 'fas fa-cube',
  image: 'https://picsum.photos/300/300?random=16',
  usage: '680',
  likes: '420',
  favorites: '250',
  author: {
    name: '设计专家',
    avatar: 'https://picsum.photos/50/50?random=16'
  }
},
{
  id: 5,
  name: '法律顾问',
  category: '法律服务',
  description: '智能法律咨询助手，提供法律建议和解释',
  icon: 'fas fa-gavel',
  image: 'https://picsum.photos/300/300?random=17',
  usage: '750',
  likes: '450',
  favorites: '270',
  author: {
    name: '法律专家',
    avatar: 'https://picsum.photos/50/50?random=17'
  }
},
{
  id: 6,
  name: '心理咨询',
  category: '心理服务',
  description: 'AI心理咨询助手，提供心理建议和疏导',
  icon: 'fas fa-brain',
  image: 'https://picsum.photos/300/300?random=18',
  usage: '820',
  likes: '490',
  favorites: '290',
  author: {
    name: '心理专家',
    avatar: 'https://picsum.photos/50/50?random=18'
  }
}
])

const currentAgents =  computed(() => {
  switch (currentAgentTab.value) {
    case 'hot': 
      return hotAgents.value
    case 'following':
      return followingAgents.value
    case 'favorite':
      return favoriteAgents.value
    default:
      return hotAgents.value
  }
})
const totalPages =  computed(() => {
  return Math.ceil(currentAgents.value.length / itemsPerPage.value)
})
const paginatedAgents = computed(()=> {
  const start = (currentPage.value - 1) * itemsPerPage.value
  const end = start + itemsPerPage.value
  return currentAgents.value.slice(start, end)
})

watch (
  () => currentAgentTab,
  () => {
    currentPage.value = 1
  }
)
</script>

<template>
  <div class="home">
    <div class="home-container">
      <!-- 左侧公告板块 -->
      <div class="notice-section">
        <div class="section-header">
          <h2>公告</h2>
          <div class="tab-switch">
            <span 
              :class="{ active: currentNoticeTab === 'review' }" 
              @click="currentNoticeTab = 'review'"
            >审核通知</span>
            <span 
              :class="{ active: currentNoticeTab === 'system' }" 
              @click="currentNoticeTab = 'system'"
            >系统公告</span>
          </div>
        </div>
        <div class="notice-content">
          <div v-if="currentNoticeTab === 'review'" class="notice-list">
            <div v-for="notice in reviewNotices" :key="notice.id" class="notice-item">
              <i class="fas fa-check-circle"></i>
              <div class="notice-text">
                <h4>{{ notice.title }}</h4>
                <p>{{ notice.content }}</p>
                <span class="notice-time">{{ notice.time }}</span>
              </div>
            </div>
          </div>
          <div v-else class="notice-list">
            <div v-for="notice in systemNotices" :key="notice.id" class="notice-item">
              <i class="fas fa-bullhorn"></i>
              <div class="notice-text">
                <h4>{{ notice.title }}</h4>
                <p>{{ notice.content }}</p>
                <span class="notice-time">{{ notice.time }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 右侧智能体推荐板块 -->
      <div class="agent-section">
        <div class="section-header">
          <h2>智能体推荐</h2>
          <div class="tab-switch">
            <span 
              :class="{ active: currentAgentTab === 'hot' }" 
              @click="currentAgentTab = 'hot'"
            >热度推荐</span>
            <span 
              :class="{ active: currentAgentTab === 'following' }" 
              @click="currentAgentTab = 'following'"
            >关注用户智能体</span>
            <span 
              :class="{ active: currentAgentTab === 'favorite' }" 
              @click="currentAgentTab = 'favorite'"
            >收藏智能体</span>
          </div>
        </div>
        <div class="agent-content">
          <div class="agent-grid">
            <div v-for="agent in paginatedAgents" :key="agent.id" class="agent-card">
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
    </div>
  </div>
</template>

<style scoped>
.home {
  padding: 20px;
}

.home-container {
  display: grid;
  grid-template-columns: 1fr 2fr;
  gap: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.section-header h2 {
  margin: 0;
  color: #2c3e50;
}

.tab-switch {
  display: flex;
  gap: 10px;
}

.tab-switch span {
  padding: 5px 10px;
  cursor: pointer;
  border-radius: 4px;
  transition: all 0.3s ease;
}

.tab-switch span.active {
  background-color: #2c3e50;
  color: white;
}

.notice-section, .agent-section {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.notice-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.notice-item {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  padding: 10px;
  border-radius: 6px;
  background-color: #f8f9fa;
}

.notice-item i {
  color: #3498db;
  font-size: 20px;
}

.notice-text h4 {
  margin: 0 0 5px 0;
  color: #2c3e50;
}

.notice-text p {
  margin: 0;
  color: #666;
  font-size: 14px;
}

.agent-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 20px;
  padding: 10px;
}

.agent-card {
  background: white;
  border-radius: 12px;
  overflow: hidden;
  transition: all 0.3s ease;
  cursor: pointer;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  max-width: 280px;
  margin: 0 auto;
}

.agent-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
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
  border-radius: 8px 8px 0 0;
}

.agent-category {
  position: absolute;
  top: 10px;
  right: 10px;
  background: rgba(44, 62, 80, 0.8);
  color: white;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
}

.agent-info {
  padding: 15px;
  display: flex;
  flex-direction: column;
  height: 160px;
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
  flex: 1;
  overflow: hidden;
  display: -webkit-box;
  -webkit-box-orient: vertical;
}

.agent-stats {
  display: flex;
  justify-content: space-between;
  padding-top: 10px;
  border-top: 1px solid #eee;
  margin-top: auto;
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
  transform: none;
}

.page-info {
  color: #2c3e50;
  font-size: 16px;
  font-weight: 500;
  padding: 0 15px;
}

.notice-time {
  font-size: 12px;
  color: #999;
  margin-top: 5px;
  display: block;
}
</style> 