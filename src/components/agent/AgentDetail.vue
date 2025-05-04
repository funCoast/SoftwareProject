<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import axios from 'axios'
import { ElMessage } from 'element-plus'

const route = useRoute()
const router = useRouter()
const agentId = route.params.id
const uid = Number(sessionStorage.getItem('uid'))
const baseImageUrl = "http://122.9.33.84:8000"

// 智能体基本信息
const agentInfo = ref({
  id: 0,
  name: '',
  description: '',
  icon: '',
  author: {
    id: '',
    account: '',
    name: '',
    avatar: ''
  },
  stats: {
    usage: 0,
    likes: 0,
    favorites: 0
  }
})

// 用户操作状态
const userActions = ref({
  isLiked: false,
  isFavorited: false,
  isFollowed: false
})

// 评论相关
const newComment = ref('')
const comments = ref<Comment[]>([])

interface Comment {
  id: number
  name: string
  userId: string
  userAccount: string
  avatar: string
  content: string
  time: string
}

interface AgentInfo {
  id: number
  name: string
  description: string
  icon: string
  author: {
    id: number
    account: string
    name: string
    avatar: string
  }
  stats: {
    usage: number
    likes: number
    favorites: number
  }
}

// 获取智能体基本信息
async function fetchAgentInfo() {
  try {
    const response = await axios({
      method: 'get',
      url: `community/agentFetchBasicInfo`,
      params: {
        agent_id: agentId,
      }
    })
    if (response.data.code === 0) {
      agentInfo.value = response.data.basicInfo
      console.log(agentInfo.value)
    } else {
      ElMessage.error('获取智能体信息失败：' + response.data.message)
    }
  } catch (error) {
    console.error('获取智能体信息异常：', error)
    ElMessage.error('获取智能体信息失败')
  }
}

// 获取用户操作状态
async function fetchUserActions() {
  try {
    const response = await axios({
      method: 'get',
      url: `community/agentFetchUserActions`,
      params: {
        agent_id: agentId,
        uid: sessionStorage.getItem('uid')
      }
    })
    if (response.data.code === 0) {
      userActions.value = response.data.actions
    } else {
      ElMessage.error('获取用户操作状态失败：' + response.data.message)
    }
  } catch (error) {
    console.error('获取用户操作状态异常：', error)
  }
}

// 获取评论列表
async function fetchComments() {
  try {
    const response = await axios({
      method: 'get',
      url: `community/agentFetchComments`,
      params: {
        agent_id: agentId
      }
    })
    if (response.data.code === 0) {
      comments.value = response.data.comments
    } else {
      ElMessage.error('获取评论失败：' + response.data.message)
    }
  } catch (error) {
    console.error('获取评论异常：', error)
    ElMessage.error('获取评论失败')
  }
}

// 点赞操作
async function handleLike() {
  try {
    const response = await axios({
      method: 'post',
      url: `community/agentHandleLike`,
      data: {
        uid: sessionStorage.getItem('uid'),
        agent_id: agentId
      }
    })
    if (response.data.code === 0) {
      userActions.value.isLiked = !userActions.value.isLiked
      agentInfo.value.stats.likes += userActions.value.isLiked ? 1 : -1
      ElMessage.success(userActions.value.isLiked ? '点赞成功' : '取消点赞成功')
    } else {
      ElMessage.error(response.data.message)
    }
  } catch (error) {
    console.error('点赞操作异常：', error)
    ElMessage.error('操作失败')
  }
}

// 收藏操作
async function handleFavorite() {
  try {
    const response = await axios({
      method: 'post',
      url: `community/agentHandleFavorite`,
      data: {
        uid: sessionStorage.getItem('uid'),
        agent_id: agentId
      }
    })
    if (response.data.code === 0) {
      userActions.value.isFavorited = !userActions.value.isFavorited
      agentInfo.value.stats.favorites += userActions.value.isFavorited ? 1 : -1
      ElMessage.success(userActions.value.isFavorited ? '收藏成功' : '取消收藏成功')
    } else {
      ElMessage.error(response.data.message)
    }
  } catch (error) {
    console.error('收藏操作异常：', error)
    ElMessage.error('操作失败')
  }
}

// 关注操作
async function handleFollow() {
  try {
    const response = await axios({
      method: 'post',
      url: `community/agentHandleFollow`,
      data: {
        uid: sessionStorage.getItem('uid'),
        author_id: agentInfo.value.author.id
      }
    })
    if (response.data.code === 0) {
      userActions.value.isFollowed = !userActions.value.isFollowed
      ElMessage.success(userActions.value.isFollowed ? '关注成功' : '取消关注成功')
    } else {
      ElMessage.error(response.data.message)
    }
  } catch (error) {
    console.error('关注操作异常：', error)
    ElMessage.error('操作失败')
  }
}

// 复制操作
async function handleCopy() {
  try {
    const response = await axios({
      method: 'post',
      url: `community/agentHandleCopy`,
      data: {
        uid: sessionStorage.getItem('uid'),
        agent_id: agentId
      }
    })
    if (response.data.code === 0) {
      ElMessage.success('复制成功')
    } else {
      ElMessage.error(response.data.message)
    }
  } catch (error) {
    console.error('复制操作异常：', error)
    ElMessage.error('操作失败')
  }
}

// 举报操作
async function handleReport() {
  try {
    const response = await axios({
      method: 'post',
      url: `community/agentHandleReport`,
      data: {
        uid: sessionStorage.getItem('uid'),
        agent_id: agentId
      }
    })
    if (response.data.code === 0) {
      ElMessage.success('举报成功')
    } else {
      ElMessage.error(response.data.message)
    }
  } catch (error) {
    console.error('举报操作异常：', error)
    ElMessage.error('操作失败')
  }
}

// 发布评论
async function publishComment() {
  if (!newComment.value.trim()) {
    ElMessage.warning('请输入评论内容')
    return
  }
  try {
    const response = await axios({
      method: 'post',
      url: `community/agentSendComment`,
      data: {
        uid: sessionStorage.getItem('uid'),
        agent_id: agentId,
        comment: newComment.value
      }
    })
    if (response.data.code === 0) {
      newComment.value = ''
      await fetchComments()
      ElMessage.success('评论发布成功')
    } else {
      ElMessage.error(response.data.message)
    }
  } catch (error) {
    console.error('发布评论异常：', error)
    ElMessage.error('发布评论失败')
  }
}

function navigateToProfile(userId: number) {
  router.push(`/profile/${userId}`)
}

function goToChat() {
  router.push({
    path: '/chat',
    query: {
      receiver_id: agentInfo.value.author.id
    }
  })
}

onMounted(() => {
  fetchAgentInfo()
  fetchUserActions()
  fetchComments()
})
</script>

<template>
  <div class="agent-detail">
    <!-- 左侧智能体展示区 -->
    <div class="agent-preview">
      <div class="agent-chat-window">
        <!-- 聊天头部 -->
        <div class="chat-header">
          <div class="chat-header-left">
            <img :src="baseImageUrl + agentInfo.icon" alt="智能体" class="agent-icon">
            <div class="agent-status">
              <span class="agent-name">{{ agentInfo.name }}</span>
              <span class="status-badge online">在线</span>
            </div>
          </div>
<!--          <div class="chat-actions">-->
<!--            <button class="action-btn" title="清空对话">-->
<!--              <img src="https://api.iconify.design/material-symbols:delete-outline.svg" alt="清空" class="action-icon">-->
<!--            </button>-->
<!--            <button class="action-btn" title="导出对话">-->
<!--              <img src="https://api.iconify.design/material-symbols:download.svg" alt="导出" class="action-icon">-->
<!--            </button>-->
<!--          </div>-->
        </div>

        <!-- 聊天内容区 -->
        <div class="chat-content">
          <div class="chat-day-divider">今天</div>

          <!-- 系统消息 -->
          <div class="message system">
            <div class="message-content">
              我是你的智能写作助手，可以帮你：
              <ul>
                <li>优化文章结构和表达</li>
                <li>检查语法和用词</li>
                <li>生成创意内容</li>
                <li>提供写作建议</li>
              </ul>
              让我们开始创作吧！
            </div>
          </div>

          <!-- 用户消息 -->
          <div class="message user">
            <div class="message-avatar">
              <img src="https://picsum.photos/40/40?random=1" alt="用户头像">
            </div>
            <div class="message-content">
              帮我写一篇关于人工智能对未来教育影响的文章，要求：
              1. 1500字左右
              2. 包含具体案例
              3. 重点讨论利弊
            </div>
            <div class="message-time">14:23</div>
          </div>

          <!-- 助手消息 -->
          <div class="message assistant">
            <div class="message-avatar">
              <img src="https://api.iconify.design/material-symbols:robot.svg" alt="助手头像">
            </div>
            <div class="message-content">
              好的，我来帮你写一篇关于人工智能对未来教育影响的文章。以下是文章大纲：

              <div class="outline-block">
                <div class="outline-title">文章大纲：</div>
                <div class="outline-content">
                  1. 引言：AI 教育变革的时代背景
                  2. AI 在教育中的应用现状
                  3. AI 教育的优势分析
                  4. 潜在的挑战和风险
                  5. 案例分析
                  6. 未来展望和建议
                </div>
              </div>

              需要我按这个大纲展开写作吗？
            </div>
            <div class="message-time">14:24</div>
          </div>

          <!-- 用户消息 -->
          <div class="message user">
            <div class="message-avatar">
              <img src="https://picsum.photos/40/40?random=1" alt="用户头像">
            </div>
            <div class="message-content">
              好的，请帮我完整写出这篇文章
            </div>
            <div class="message-time">14:24</div>
          </div>

          <!-- 助手消息（带进度条） -->
          <div class="message assistant">
            <div class="message-avatar">
              <img src="https://api.iconify.design/material-symbols:robot.svg" alt="助手头像">
            </div>
            <div class="message-content">
              <div class="typing-indicator">
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
              </div>
              <div class="progress-bar">
                <div class="progress" style="width: 65%"></div>
              </div>
              <div class="progress-text">正在生成文章...</div>
            </div>
          </div>
        </div>

        <!-- 输入区域 -->
        <div class="chat-input-area">
          <div class="input-container">
            <textarea
                placeholder="输入消息..."
                rows="1"
                class="chat-input"
            ></textarea>
            <div class="input-actions">
              <button class="action-btn" title="上传文件">
                <img src="https://api.iconify.design/material-symbols:attach-file.svg" alt="上传" class="action-icon">
              </button>
              <button class="send-btn" title="发送">
                <img src="https://api.iconify.design/material-symbols:send.svg" alt="发送" class="action-icon">
              </button>
            </div>
          </div>
          <div class="input-tips">
            Shift + Enter 换行 &nbsp;|&nbsp; Enter 发送
          </div>
        </div>
      </div>
    </div>

    <!-- 右侧信息区 -->
    <div class="agent-info">
      <!-- 基本信息板块 -->
      <div class="info-panel basic-info">
        <!-- 智能体基本信息区域 -->
        <div class="agent-basic">
          <div class="agent-header">
            <img :src="baseImageUrl + agentInfo.icon" alt="智能体图片" class="agent-photo">
            <div class="agent-meta">
              <h2>{{ agentInfo.name }}</h2>
              <p class="description">{{ agentInfo.description }}</p>
            </div>
          </div>
        </div>

        <!-- 分隔线 -->
        <div class="divider"></div>

        <!-- 统计信息区域 -->
        <div class="stats-section">
          <div class="stats">
            <div class="stat-item">
              <img src="https://api.iconify.design/material-symbols:favorite.svg" alt="点赞" class="stat-icon">
              <span>点赞 {{ agentInfo.stats.likes }}</span>
            </div>
            <div class="stat-item">
              <img src="https://api.iconify.design/material-symbols:bookmark.svg" alt="收藏" class="stat-icon">
              <span>收藏 {{ agentInfo.stats.favorites }}</span>
            </div>
          </div>
        </div>

        <!-- 分隔线 -->
        <div class="divider"></div>

        <!-- 作者信息区域 -->
        <div class="author-info">
          <img 
            :src="baseImageUrl + agentInfo.author.avatar"
            alt="作者头像" 
            class="author-avatar"
            @click="navigateToProfile(agentInfo.author.id)"
          >
          <div class="author-meta">
            <span 
              class="author-name"
              @click="navigateToProfile(agentInfo.author.id)"
            >{{ agentInfo.author.name }}</span>
            <span class="author-id">{{ agentInfo.author.account }}</span>
          </div>
          <button
            class="follow-btn"
            v-if="uid !== agentInfo.author.id"
            :class="{ 'followed': userActions.isFollowed }"
            @click="handleFollow"
          >
            <img 
              :src="userActions.isFollowed 
                ? 'https://api.iconify.design/material-symbols:person-check.svg'
                : 'https://api.iconify.design/material-symbols:person-add-outline.svg'" 
              alt="关注" 
              class="action-icon"
            >
            <span>{{ userActions.isFollowed ? '已关注' : '关注' }}</span>
          </button>
        </div>

        <!-- 分隔线 -->
        <div class="divider"></div>

        <!-- 操作按钮区域 -->
        <div class="action-buttons">
          <button 
            class="action-btn primary" 
            :class="{ 'active': userActions.isLiked }"
            @click="handleLike"
          >
            <img 
              :src="userActions.isLiked 
                ? 'https://api.iconify.design/material-symbols:favorite.svg'
                : 'https://api.iconify.design/material-symbols:favorite-outline.svg'" 
              alt="点赞" 
              class="action-icon"
            >
            <span>{{ userActions.isLiked ? '已点赞' : '点赞' }}</span>
          </button>
          <button 
            class="action-btn primary" 
            :class="{ 'active': userActions.isFavorited }"
            @click="handleFavorite"
          >
            <img 
              :src="userActions.isFavorited 
                ? 'https://api.iconify.design/material-symbols:bookmark.svg'
                : 'https://api.iconify.design/material-symbols:bookmark-outline.svg'" 
              alt="收藏" 
              class="action-icon"
            >
            <span>{{ userActions.isFavorited ? '已收藏' : '收藏' }}</span>
          </button>
          <button class="action-btn secondary" @click="handleCopy">
            <img src="https://api.iconify.design/material-symbols:content-copy.svg" alt="复制" class="action-icon">
            <span>复制</span>
          </button>
        </div>
      </div>

      <!-- 评论区板块 -->
      <div class="info-panel comments-section">
        <h3>评论区</h3>
        <div class="comments-list">
          <div v-for="comment in comments" :key="comment.id" class="comment-card">
            <div class="comment-header">
              <div class="comment-user">
                <img 
                  :src="baseImageUrl + comment.avatar"
                  :alt="comment.name" 
                  class="comment-avatar"
                  @click="navigateToProfile(comment.userId)"
                >
                <div class="user-info">
                  <span 
                    class="comment-name"
                    @click="navigateToProfile(comment.userId)"
                  >{{ comment.name }}</span>
                  <span class="comment-id">{{ comment.userAccount }}</span>
                </div>
              </div>
              <span class="comment-time">{{ comment.time }}</span>
            </div>
            <p class="comment-text">{{ comment.content }}</p>
          </div>
        </div>

        <!-- 发布评论区域 -->
        <div class="comment-publish">
          <div class="publish-content">
            <textarea
                placeholder="写下你的评论..."
                class="comment-textarea"
                v-model="newComment"
                rows="1"
                @keydown.enter.prevent="publishComment"
            ></textarea>
            <button class="publish-btn" @click="publishComment">
              <img src="https://api.iconify.design/material-symbols:send.svg" alt="发布" class="action-icon">
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.agent-detail {
  display: flex;
  gap: 24px;
  padding: 24px;
  min-height: 100vh;
  background: #f5f6fa;
}

.agent-preview {
  flex: 1;
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  height: calc(100vh - 48px);
}

.agent-info {
  width: 400px;
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.info-panel {
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.basic-info {
  padding: 24px;
}

.agent-chat-window {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: #fff;
}

.chat-header {
  padding: 16px 20px;
  border-bottom: 1px solid #e6e6e6;
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: #f8f9fa;
}

.chat-header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.agent-icon {
  width: 32px;
  height: 32px;
  padding: 4px;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}

.agent-status {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.agent-name {
  font-weight: 600;
  color: #2c3e50;
}

.status-badge {
  font-size: 12px;
  color: #666;
  display: flex;
  align-items: center;
  gap: 4px;
}

.status-badge.online::before {
  content: '';
  display: inline-block;
  width: 6px;
  height: 6px;
  background: #4caf50;
  border-radius: 50%;
}

.chat-actions {
  display: flex;
  gap: 8px;
}

.action-btn {
  background: none;
  border: none;
  padding: 6px;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.3s;
}

.action-btn:hover {
  background: #e9ecef;
}

.action-icon {
  width: 20px;
  height: 20px;
  opacity: 0.7;
}

.chat-content {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 20px;
  background: #fff;
}

.chat-day-divider {
  text-align: center;
  color: #666;
  font-size: 12px;
  margin: 20px 0;
  position: relative;
}

.chat-day-divider::before,
.chat-day-divider::after {
  content: '';
  position: absolute;
  top: 50%;
  width: 100px;
  height: 1px;
  background: #e6e6e6;
}

.chat-day-divider::before {
  right: calc(50% + 30px);
}

.chat-day-divider::after {
  left: calc(50% + 30px);
}

.message {
  display: flex;
  gap: 12px;
  max-width: 88%;
}

.message.user {
  margin-left: auto;
  flex-direction: row-reverse;
}

.message.system {
  margin: 0 auto;
  background: #f8f9fa;
  border-radius: 8px;
  padding: 16px;
  width: 100%;
}

.message-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  overflow: hidden;
  flex-shrink: 0;
}

.message-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.message-content {
  padding: 12px 16px;
  border-radius: 12px;
  font-size: 14px;
  line-height: 1.5;
  position: relative;
}

.message.user .message-content {
  background: #2c3e50;
  color: white;
  border-top-right-radius: 4px;
}

.message.assistant .message-content {
  background: #f8f9fa;
  color: #2c3e50;
  border-top-left-radius: 4px;
}

.message-time {
  font-size: 12px;
  color: #999;
  margin-top: 4px;
  flex-shrink: 0;
}

.outline-block {
  margin-top: 12px;
  background: #fff;
  border: 1px solid #e6e6e6;
  border-radius: 8px;
  overflow: hidden;
}

.outline-title {
  padding: 8px 12px;
  background: #f8f9fa;
  border-bottom: 1px solid #e6e6e6;
  font-weight: 600;
}

.outline-content {
  padding: 12px;
  line-height: 1.6;
}

.typing-indicator {
  display: flex;
  gap: 4px;
  padding: 8px;
  margin-bottom: 8px;
}

.typing-dot {
  width: 8px;
  height: 8px;
  background: #666;
  border-radius: 50%;
  animation: typing 1s infinite ease-in-out;
}

.typing-dot:nth-child(1) { animation-delay: 0.2s; }
.typing-dot:nth-child(2) { animation-delay: 0.3s; }
.typing-dot:nth-child(3) { animation-delay: 0.4s; }

@keyframes typing {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-4px); }
}

.progress-bar {
  height: 4px;
  background: #e6e6e6;
  border-radius: 2px;
  overflow: hidden;
  margin: 8px 0;
}

.progress {
  height: 100%;
  background: #4caf50;
  border-radius: 2px;
  transition: width 0.3s ease;
}

.progress-text {
  font-size: 12px;
  color: #666;
  text-align: center;
}

.chat-input-area {
  padding: 20px;
  border-top: 1px solid #e6e6e6;
  background: #fff;
}

.input-container {
  display: flex;
  gap: 12px;
  background: #f8f9fa;
  border: 1px solid #e6e6e6;
  border-radius: 8px;
  padding: 8px 12px;
}

.chat-input {
  flex: 1;
  border: none;
  outline: none;
  background: none;
  resize: none;
  font-size: 14px;
  line-height: 1.5;
  max-height: 150px;
  min-height: 24px;
}

.input-actions {
  display: flex;
  align-items: flex-end;
  gap: 8px;
}

.send-btn {
  background: #2c3e50;
  border: none;
  border-radius: 6px;
  padding: 8px;
  cursor: pointer;
  transition: all 0.3s;
}

.send-btn:hover {
  background: #34495e;
}

.send-btn .action-icon {
  filter: brightness(0) invert(1);
}

.input-tips {
  text-align: center;
  color: #999;
  font-size: 12px;
  margin-top: 8px;
}

.system ul {
  margin: 10px 0;
  padding-left: 20px;
}

.system li {
  margin: 5px 0;
}

.agent-header {
  display: flex;
  gap: 20px;
  margin-bottom: 24px;
}

.agent-photo {
  width: 100px;
  height: 100px;
  border-radius: 12px;
  object-fit: cover;
}

.agent-meta {
  flex: 1;
}

.agent-meta h2 {
  margin: 0 0 12px 0;
  color: #2c3e50;
}

.description {
  color: #666;
  font-size: 14px;
  line-height: 1.5;
  margin-bottom: 16px;
}

.stats-section {
  padding: 16px 0;
}

.stats {
  display: flex;
  gap: 20px;
  padding: 12px 16px;
  background: #f8f9fa;
  border-radius: 8px;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #2c3e50;
  font-size: 14px;
}

.stat-icon {
  width: 20px;
  height: 20px;
  filter: invert(23%) sepia(19%) saturate(1111%) hue-rotate(182deg) brightness(95%) contrast(85%);
}

.author-info {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px 0;
  border-top: 1px solid #eee;
  border-bottom: 1px solid #eee;
  margin-bottom: 24px;
}

.author-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  border: 2px solid #fff;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  cursor: pointer;
  transition: transform 0.3s ease;
}

.author-avatar:hover {
  transform: scale(1.05);
}

.author-meta {
  display: flex;
  flex-direction: column;
  flex: 1;
}

.author-name {
  font-weight: 600;
  color: #2c3e50;
  cursor: pointer;
  transition: color 0.3s ease;
}

.author-name:hover {
  color: #3498db;
}

.author-id {
  font-size: 14px;
  color: #666;
}

.follow-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  border: 1px solid #2c3e50;
  border-radius: 20px;
  background: transparent;
  color: #2c3e50;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s;
}

.follow-btn:hover {
  background: #2c3e50;
  color: white;
}

.follow-btn:hover .action-icon {
  filter: brightness(0) invert(1);
}

.follow-btn .action-icon {
  width: 18px;
  height: 18px;
}

.action-buttons {
  display: flex;
  gap: 12px;
  margin-top: 16px;
}

.action-btn {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 12px;
  border: 1px solid #2c3e50;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.3s;
  background: white;
  color: #2c3e50;
}

.action-btn .action-icon {
  width: 20px;
  height: 20px;
  order: -1;
}

.action-btn span {
  white-space: nowrap;
}

.action-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  background: #2c3e50;
  color: white;
}

.action-btn:hover .action-icon {
  filter: brightness(0) invert(1);
}

.comments-section {
  background: white;
  display: flex;
  flex-direction: column;
  height: calc(100vh - 518px);
  min-height: 100px;
  position: relative;
  border-radius: 12px;
}

.comments-section h3 {
  margin: 0;
  color: #2c3e50;
  font-size: 18px;
  padding: 24px 24px 16px 24px;
  background: white;
  border-bottom: 1px solid #eee;
  position: sticky;
  top: 0;
  z-index: 1;
}

.comments-list {
  flex: 1;
  overflow-y: auto;
  padding: 0 24px;
  margin: 16px 0 80px 0;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.comments-list::-webkit-scrollbar {
  width: 6px;
}

.comments-list::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

.comments-list::-webkit-scrollbar-thumb {
  background: #ccc;
  border-radius: 3px;
}

.comment-card {
  background: #f8f9fa;
  border-radius: 12px;
  padding: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  transition: all 0.3s;
}

.comment-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.comment-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 12px;
}

.comment-user {
  display: flex;
  align-items: center;
  gap: 12px;
}

.comment-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  border: 2px solid #fff;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  cursor: pointer;
  transition: transform 0.3s ease;
}

.comment-avatar:hover {
  transform: scale(1.05);
}

.user-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.comment-name {
  font-weight: 600;
  color: #2c3e50;
  font-size: 14px;
  cursor: pointer;
  transition: color 0.3s ease;
}

.comment-name:hover {
  color: #3498db;
}

.comment-id {
  color: #666;
  font-size: 12px;
}

.comment-time {
  color: #999;
  font-size: 12px;
  flex-shrink: 0;
}

.comment-text {
  color: #2c3e50;
  font-size: 14px;
  line-height: 1.6;
  margin: 0;
  word-break: break-word;
}

/* 发布评论区域样式 */
.comment-publish {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  background: white;
  border-radius: 0 0 12px 12px;
  padding: 12px 16px;
  box-shadow: 0 -2px 8px rgba(0, 0, 0, 0.05);
  border-top: 1px solid #eee;
}

.publish-content {
  display: flex;
  align-items: center;
  gap: 12px;
}

.comment-textarea {
  flex: 1;
  padding: 8px 12px;
  border: 1px solid #e6e6e6;
  border-radius: 6px;
  resize: none;
  font-size: 14px;
  line-height: 1.5;
  color: #2c3e50;
  background: #f8f9fa;
  transition: all 0.3s;
  height: 36px;
}

.comment-textarea:focus {
  outline: none;
  border-color: #2c3e50;
  background: white;
}

.publish-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 8px;
  border: none;
  border-radius: 6px;
  background: #2c3e50;
  color: white;
  cursor: pointer;
  transition: all 0.3s;
}

.publish-btn:hover {
  background: #34495e;
  transform: translateY(-2px);
}

.publish-btn .action-icon {
  width: 20px;
  height: 20px;
  filter: brightness(0) invert(1);
}

.follow-btn.followed {
  background: #2c3e50;
  color: white;
}

.follow-btn.followed .action-icon {
  filter: brightness(0) invert(1);
}

.action-btn.active {
  background: #2c3e50;
  color: white;
}

.action-btn.active .action-icon {
  filter: brightness(0) invert(1);
}

.agent-basic {
  margin-bottom: 16px;
}

.divider {
  height: 1px;
  background: #eee;
  margin: 0;
}
</style>