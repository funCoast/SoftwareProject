<template>
  <div class="profile-container">
    <!-- 个人信息头部 -->
    <div class="profile-header">
      <div class="profile-info">
        <div class="avatar-section">
          <img :src="userInfo.avatar" :alt="userInfo.name" class="avatar">
        </div>
        <div class="info-section">
          <div class="user-name">{{ userInfo.name }}</div>
          <div class="user-account">@{{ userInfo.account }}</div>
          <div class="user-description">{{ userInfo.description }}</div>
          <div class="user-stats">
            <div class="stat-item">
              <span class="stat-value">{{ userInfo.following }}</span>
              <span class="stat-label">关注</span>
            </div>
            <div class="stat-item">
              <span class="stat-value">{{ userInfo.followers }}</span>
              <span class="stat-label">粉丝</span>
            </div>
            <div class="stat-item">
              <span class="stat-value">{{ userInfo.likes }}</span>
              <span class="stat-label">获赞</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 内容切换栏 -->
    <div class="content-tabs">
      <div 
        v-for="tab in tabs" 
        :key="tab.id"
        class="tab-item"
        :class="{ active: currentTab === tab.id }"
        @click="currentTab = tab.id"
      >
        {{ tab.name }}
      </div>
    </div>

    <!-- 内容展示区 -->
    <div class="content-section">
      <!-- 作品列表 -->
      <div v-if="currentTab === 'works'" class="agent-list">
        <div v-for="agent in userWorks" :key="agent.id" class="agent-card">
          <div class="agent-image">
            <img :src="agent.image" :alt="agent.name">
            <div class="agent-category">{{ agent.category }}</div>
          </div>
          <div class="agent-info">
            <div class="agent-header">
              <h3>{{ agent.name }}</h3>
              <div class="agent-author">
                <img :src="userInfo.avatar" :alt="userInfo.name">
                <span>{{ userInfo.name }}</span>
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

      <!-- 喜欢列表 -->
      <div v-if="currentTab === 'likes'" class="agent-list">
        <div v-for="agent in userLikes" :key="agent.id" class="agent-card">
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

      <!-- 收藏列表 -->
      <div v-if="currentTab === 'favorites'" class="agent-list">
        <div v-for="agent in userFavorites" :key="agent.id" class="agent-card">
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
    </div>
  </div>
</template>

<script>
export default {
  name: 'ProfilePage',
  data() {
    return {
      currentTab: 'works',
      tabs: [
        { id: 'works', name: '作品' },
        { id: 'likes', name: '喜欢' },
        { id: 'favorites', name: '收藏' }
      ],
      userInfo: {
        name: 'AI开发者',
        account: 'ai_developer',
        avatar: 'https://picsum.photos/200/200?random=1',
        description: '专注于AI应用开发，致力于为用户提供优质的智能体服务。擅长对话系统、数据分析、图像处理等领域。',
        following: 128,
        followers: 256,
        likes: 1024
      },
      userWorks: [
        {
          id: 1,
          name: '智能对话助手',
          category: '对话助手',
          description: '基于大语言模型的智能对话系统，支持多轮对话和上下文理解',
          image: 'https://picsum.photos/300/300?random=1',
          usage: '2.3k',
          likes: '1.2k',
          favorites: '856'
        },
        {
          id: 2,
          name: '数据分析工具',
          category: '数据分析',
          description: '专业的数据分析工具，支持多种数据可视化和预测分析',
          image: 'https://picsum.photos/300/300?random=2',
          usage: '1.5k',
          likes: '890',
          favorites: '654'
        },
        {
          id: 3,
          name: '图像处理助手',
          category: '图像处理',
          description: '智能图像处理工具，支持多种图像编辑和优化功能',
          image: 'https://picsum.photos/300/300?random=3',
          usage: '980',
          likes: '678',
          favorites: '432'
        }
      ],
      userLikes: [
        {
          id: 4,
          name: '多语言翻译助手',
          category: '对话助手',
          description: '支持多种语言互译的智能助手，提供实时翻译和语言学习建议',
          image: 'https://picsum.photos/300/300?random=4',
          usage: '1.8k',
          likes: '980',
          favorites: '765',
          author: {
            name: '语言专家',
            avatar: 'https://picsum.photos/50/50?random=4'
          }
        },
        {
          id: 5,
          name: '代码审查助手',
          category: '开发工具',
          description: '智能代码审查工具，提供代码质量分析和优化建议',
          image: 'https://picsum.photos/300/300?random=5',
          usage: '950',
          likes: '580',
          favorites: '345',
          author: {
            name: '代码专家',
            avatar: 'https://picsum.photos/50/50?random=5'
          }
        }
      ],
      userFavorites: [
        {
          id: 6,
          name: '语音合成助手',
          category: '语音工具',
          description: '高质量语音合成工具，支持多种音色和情感表达',
          image: 'https://picsum.photos/300/300?random=6',
          usage: '780',
          likes: '520',
          favorites: '234',
          author: {
            name: '语音专家',
            avatar: 'https://picsum.photos/50/50?random=6'
          }
        },
        {
          id: 7,
          name: '用户行为分析',
          category: '数据分析',
          description: '用户行为分析工具，提供用户画像和行为路径分析',
          image: 'https://picsum.photos/300/300?random=7',
          usage: '1.1k',
          likes: '690',
          favorites: '456',
          author: {
            name: '用户研究专家',
            avatar: 'https://picsum.photos/50/50?random=7'
          }
        }
      ]
    }
  }
}
</script>

<style scoped>
.profile-container {
  padding: 20px;
  background: #f8f9fa;
  min-height: 100vh;
}

.profile-header {
  background: white;
  border-radius: 8px;
  padding: 30px;
  margin-bottom: 20px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.profile-info {
  display: flex;
  gap: 30px;
  align-items: flex-start;
}

.avatar-section {
  flex-shrink: 0;
  display: flex;
  align-items: flex-start;
  gap: 20px;
}

.avatar {
  width: 160px;
  height: 160px;
  border-radius: 50%;
  object-fit: cover;
}

.info-section {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: flex-start;
  padding-top: 10px;
}

.user-name {
  margin-left: -1000px;
  font-size: 28px;
  font-weight: bold;
  color: #2c3e50;
  margin-bottom: 10px;
}

.user-account {
  font-size: 16px;
  color: #666;
  margin-bottom: 10px;
}

.user-description {
  color: #666;
  line-height: 1.6;
  margin-bottom: 20px;
  max-width: 600px;
}

.user-stats {
  display: flex;
  gap: 30px;
  margin-top: 20px;
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.stat-value {
  font-size: 20px;
  font-weight: bold;
  color: #2c3e50;
}

.stat-label {
  font-size: 14px;
  color: #666;
}

.content-tabs {
  display: flex;
  background: white;
  border-radius: 8px;
  padding: 0 20px;
  margin-bottom: 20px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.tab-item {
  padding: 15px 20px;
  color: #666;
  cursor: pointer;
  position: relative;
  transition: all 0.3s ease;
}

.tab-item:hover {
  color: #2c3e50;
}

.tab-item.active {
  color: #2c3e50;
  font-weight: bold;
}

.tab-item.active::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  width: 100%;
  height: 2px;
  background: #2c3e50;
}

.content-section {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.agent-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
  padding: 20px;
}

.agent-card {
  background: white;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  transition: all 0.3s ease;
  display: flex;
  flex-direction: column;
}

.agent-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0,0,0,0.1);
}

.agent-image {
  position: relative;
  width: 100%;
  padding-top: 75%;
  background: #f8f9fa;
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
  flex: 1;
  display: flex;
  flex-direction: column;
}

.agent-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 10px;
}

.agent-header h3 {
  margin: 0;
  color: #2c3e50;
  font-size: 16px;
  font-weight: 600;
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
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  flex: 1;
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
  color: #e74c3c;
}
</style> 