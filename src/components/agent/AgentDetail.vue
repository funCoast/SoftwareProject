<script setup lang="ts">
import { ref, onMounted, inject, type Ref, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import axios from 'axios'
import { ElMessage } from 'element-plus'
import { Document, Search, Close, Plus, ArrowDown } from '@element-plus/icons-vue'
import { marked } from 'marked'

const userAvatar = inject('avatar') as Ref
const route = useRoute()
const router = useRouter()
const agent_id = route.params.id
const uid = Number(localStorage.getItem('LingXi_uid'))
const baseImageUrl = "http://122.9.33.84:8000"

// 智能体基本信息
interface Author {
  id: number;
  account: string;
  name: string;
  avatar: string;
}

interface Stats {
  usage: number;
  likes: number;
  favorites: number;
}

interface AgentInfo {
  id: number;
  name: string;
  description: string;
  icon: string;
  author: Author;
  stats: Stats;
}

const agentInfo = ref<AgentInfo>({
  id: 0,
  name: "",
  description: "",
  icon: "",
  author: {
    id: 0,
    account: "",
    name: "",
    avatar: "",
  },
  stats: {
    usage: 0,
    likes: 0,
    favorites: 0,
  },
});

// 用户操作状态
const userActions = ref({
  isLiked: false,
  isFavorited: false,
  isFollowed: false
})

interface Comment {
  id: number
  name: string
  userId: number
  userAccount: string
  avatar: string
  content: string
  time: string
}

// 评论相关
const newComment = ref('')
const comments = ref<Comment[]>([])
// 举报相关
const showReportDialog = ref(false)
const reportDescription = ref('')

// 添加加载状态
const isLoading = ref(false)

const chatMessagesRef = ref<HTMLElement | null>(null)

// 滚动到底部
function scrollToBottom() {
  nextTick(() => {
    if (chatMessagesRef.value) {
      chatMessagesRef.value.scrollTop = chatMessagesRef.value.scrollHeight
    }
  })
}

// 获取智能体基本信息
async function fetchAgentInfo() {
  try {
    const response = await axios({
      method: 'get',
      url: `community/agentFetchBasicInfo`,
      params: {
        agent_id: agent_id,
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

// 修改 Message 接口
interface Message {
  sender: 'user' | 'assistant'
  content: {
    thinking_chain: string
    response: string
  }
  time: string
  file?: string[]
  search?: boolean
  showThinking?: boolean
}

// 聊天相关
const messageInput = ref('')
const chatHistory = ref<Message[]>([])
const fileList = ref<File[]>([])
const enableSearch = ref(false)

// 文件上传相关
const handleFileUpload = (file: File) => {
  if (enableSearch.value) {
    ElMessage.warning('请先关闭联网搜索')
    return false
  }
  fileList.value.push(file)
  return false // 阻止自动上传
}

const removeFile = (file: File) => {
  const index = fileList.value.indexOf(file)
  if (index !== -1) {
    fileList.value.splice(index, 1)
  }
}

// 切换搜索模式
const toggleSearch = () => {
  if (fileList.value.length > 0) {
    ElMessage.warning('请先移除已上传的文件')
    return
  }
  enableSearch.value = !enableSearch.value
}

// 处理回车键
const handleEnter = (e: KeyboardEvent) => {
  if (e.ctrlKey && e.shiftKey) {
    trySendMessage()
  } else {
    // 普通回车，插入换行
    const textarea = e.target as HTMLTextAreaElement
    const start = textarea.selectionStart
    const end = textarea.selectionEnd
    messageInput.value = messageInput.value.substring(0, start) + '\n' + messageInput.value.substring(end)
    // 保持光标位置
    nextTick(() => {
      textarea.selectionStart = textarea.selectionEnd = start + 1
    })
  }
}

// 修改发送消息函数
const trySendMessage = () => {
  if (!messageInput.value.trim() && fileList.value.length === 0) return
  
  isLoading.value = true
  sendMessage()
  chatHistory.value.push({
    sender: 'user',
    content: {
      thinking_chain: '',
      response: messageInput.value
    },
    time: new Date().toISOString().replace('T', ' ').slice(0, 19),
    file: fileList.value.map(file => file.name),
    search: enableSearch.value,
    showThinking: true
  })

  messageInput.value = ''
  fileList.value = []
  enableSearch.value = false
  scrollToBottom() // 发送消息后滚动到底部
}

async function sendMessage() {
  try {
    const formData = new FormData()
    formData.append('uid', localStorage.getItem('LingXi_uid') as string)
    formData.append('content', messageInput.value)
    formData.append('agent_id', agent_id as string)
    formData.append('search', enableSearch.value.toString())
    
    for (const file of fileList.value) {
      formData.append('file', file.raw)
    }

    const response = await axios({
      method: 'post',
      url: 'agent/sendAgentMessage',
      data: formData
    })
    
    if (response.data.code === 0) {
      chatHistory.value.push({
        sender: 'assistant',
        content: response.data.content,
        time: response.data.time,
        showThinking: true
      })
      console.log('信息发送成功')
      scrollToBottom() // 收到回复后滚动到底部
    } else {
      console.log(response.data.message)
    }
  } catch (error) {
    console.error('信息发送失败:', error)
  } finally {
    isLoading.value = false
  }
}

// 添加折叠控制函数
function toggleThinkingChain(index: number) {
  if (chatHistory.value[index]) {
    chatHistory.value[index].showThinking = !chatHistory.value[index].showThinking
  }
}

async function fetchMessage() {
  try {
    const response = await axios({
      method: 'get',
      url: 'agent/fetchAgentMessage',
      params: {
        uid: localStorage.getItem('LingXi_uid'),
        agent_id: agent_id,
      }
    })
    if (response.data.code === 0) {
      chatHistory.value = response.data.chatHistory.map((msg: Message) => ({
        ...msg,
        showThinking: true
      }))
      console.log('历史信息获取成功')
      console.log(response.data.chatHistory)
      scrollToBottom() // 获取历史消息后滚动到底部
    } else {
      console.log(response.data.message)
    }
  } catch (error) {
    console.error('获取历史消息失败:', error)
  }
}

async function clearMessage() {
  try {
    const response = await axios({
      method: 'post',
      url: 'agent/clearHistoryMessage',
      data: {
        uid: localStorage.getItem('LingXi_uid'),
        agent_id: agent_id,
      }
    })
    if (response.data.code === 0) {
      chatHistory.value = [];
      ElMessage.success('清除历史对话成功')
    } else {
      console.log(response.data.message)
    }
  } catch (error) {
    console.error('清除历史消息失败:', error)
  }
}

// 添加渲染Markdown的函数
function renderedMarkdown(content: string) {
  return marked(content)
}

// 获取用户操作状态
async function fetchUserActions() {
  try {
    const response = await axios({
      method: 'get',
      url: `community/agentFetchUserActions`,
      params: {
        agent_id: agent_id,
        uid: localStorage.getItem('LingXi_uid')
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
        agent_id: agent_id
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
        uid: localStorage.getItem('LingXi_uid'),
        agent_id: agent_id
      }
    })
    if (response.data.code === 0) {
      userActions.value.isLiked = !userActions.value.isLiked
      agentInfo.value.stats.likes += userActions.value.isLiked ? 1 : -1
      if (userActions.value.isLiked) {
        ElMessage.success('点赞成功')
      } else {
        ElMessage.success('取消点赞成功')
      }
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
        uid: localStorage.getItem('LingXi_uid'),
        agent_id: agent_id
      }
    })
    if (response.data.code === 0) {
      userActions.value.isFavorited = !userActions.value.isFavorited
      agentInfo.value.stats.favorites += userActions.value.isFavorited ? 1 : -1
      if (userActions.value.isFavorited) {
        ElMessage.success('收藏成功')
      } else {
        ElMessage.success('取消收藏成功')
      }
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
        uid: localStorage.getItem('LingXi_uid'),
        author_id: agentInfo.value.author.id
      }
    })
    if (response.data.code === 0) {
      userActions.value.isFollowed = !userActions.value.isFollowed
      if (userActions.value.isFollowed) {
        ElMessage.success('关注成功')
      } else {
        ElMessage.success('取消关注成功')
      }
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
        uid: localStorage.getItem('LingXi_uid'),
        agent_id: agent_id
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
  if (!reportDescription.value.trim()) {
    ElMessage.warning('请输入举报描述')
    return
  }
  try {
    const response = await axios({
      method: 'post',
      url: `agent/report`,
      data: {
        uid: localStorage.getItem('LingXi_uid'),
        agent_id: agent_id,
        reason: reportDescription.value
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
        uid: localStorage.getItem('LingXi_uid'),
        agent_id: agent_id,
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

onMounted(() => {
  fetchAgentInfo()
  fetchMessage()
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
          <div class="chat-actions">
            <button class="action-btn" title="清空对话" @click="clearMessage">
              <img src="https://api.iconify.design/material-symbols:delete-outline.svg" alt="清空" class="action-icon">
            </button>
          </div>
        </div>

        <!-- 聊天内容区 -->
        <div class="chat-content" ref="chatMessagesRef">
          <!-- 遍历消息 -->
          <div
            v-for="(message, index) in chatHistory"
            :class="['message', message.sender]"
          >
            <!-- 用户消息 -->
            <template v-if="message.sender === 'user'">
              <div class="message-avatar">
                <img :src="userAvatar" alt="用户头像" />
              </div>
              <div class="message-content">
                <div class="message-text">{{ message.content.response }}</div>
                <div v-if="message.file && message.file.length > 0" class="message-files">
                  <div v-for="file in message.file" :key="file" class="message-file">
                    <el-icon><Document /></el-icon>
                    <span class="file-name">{{ file }}</span>
                  </div>
                </div>
                <div v-if="message.search" class="message-search">
                  <el-icon><Search /></el-icon>
                  <span>已开启联网搜索</span>
                </div>
              </div>
              <div class="message-time">{{ message.time }}</div>
            </template>

            <!-- 助手消息 -->
            <template v-else-if="message.sender === 'assistant'">
              <div class="message-avatar">
                <img :src="'http://122.9.33.84:8000' + agentInfo.icon" alt="助手头像" />
              </div>
              <div class="message-content">
                <div class="message-text">
                  <div v-if="message.content.thinking_chain" class="thinking-chain">
                    <div class="thinking-header" @click="toggleThinkingChain(index)">
                      <span>思考过程</span>
                      <el-icon :class="{ 'is-active': !message.showThinking }">
                        <ArrowDown />
                      </el-icon>
                    </div>
                    <div v-show="message.showThinking" class="thinking-content" v-html="renderedMarkdown(message.content.thinking_chain)"></div>
                  </div>
                  <div class="response" v-html="renderedMarkdown(message.content.response)"></div>
                </div>
              </div>
              <div class="message-time">{{ message.time }}</div>
            </template>
          </div>

          <!-- 在消息列表的最后添加加载动画 -->
          <div v-if="isLoading" class="message assistant">
            <div class="message-avatar">
              <img :src="'http://122.9.33.84:8000' + agentInfo.icon" alt="助手头像" />
            </div>
            <div class="message-content">
              <div class="message-text">
                <div class="typing-indicator">
                  <div class="typing-dot"></div>
                  <div class="typing-dot"></div>
                  <div class="typing-dot"></div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 输入区域 -->
        <div class="chat-input-area">
          <div class="input-container">
            <div class="input-wrapper">
              <div v-if="fileList.length > 0" class="file-preview">
                <div class="file-list">
                  <div v-for="file in fileList" :key="file.name" class="file-item">
                    <el-icon><Document /></el-icon>
                    <span class="file-name">{{ file.name }}</span>
                    <el-button type="text" class="remove-file" @click="removeFile(file)">
                      <el-icon><Close /></el-icon>
                    </el-button>
                  </div>
                </div>
              </div>
              
              <div class="input-area">
                <textarea
                  class="chat-input"
                  v-model="messageInput"
                  placeholder="输入消息... (Ctrl+Shift+Enter 发送)"
                  rows="1"
                  @keydown.enter.prevent="handleEnter"
                ></textarea>
                
                <div class="input-actions">
                  <el-upload
                    class="upload-button"
                    :auto-upload="false"
                    :show-file-list="false"
                    :on-change="handleFileUpload"
                    :disabled="enableSearch"
                    accept=".txt,.pdf,.doc,.docx,.md,.xls,.xlsx"
                  >
                    <el-button type="text" class="upload-icon" :class="{ 'disabled': enableSearch }">
                      <el-icon><Plus /></el-icon>
                    </el-button>
                  </el-upload>
                  
                  <el-button
                    class="search-button"
                    :class="{ 'active': enableSearch }"
                    @click="toggleSearch"
                    :disabled="fileList.length > 0"
                  >
                    <el-icon><Search /></el-icon>
                    <span>联网搜索</span>
                  </el-button>
                  
                  <el-button 
                    class="send-button"
                    :disabled="!messageInput.trim()"
                    @click="trySendMessage"
                  >
                    发送
                  </el-button>
                </div>
              </div>
            </div>
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
        </div>
        <div class="action-buttons">
          <button class="action-btn secondary" @click="handleCopy">
            <img src="https://api.iconify.design/material-symbols:content-copy.svg" alt="复制" class="action-icon">
            <span>复制</span>
          </button>
          <button class="action-btn secondary" @click="showReportDialog = true">
            <img src="https://api.iconify.design/material-symbols:report.svg" alt="举报" class="action-icon">
            <span>举报</span>
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

        <!-- 举报弹窗 -->
        <el-dialog
            v-model="showReportDialog"
            title="举报智能体"
            width="400px"
            :close-on-click-modal="false"
        >
          <div class="report-dialog">
            <div class="form-group">
              <label>举报描述</label>
              <el-input
                  v-model="reportDescription"
                  type="textarea"
                  :rows="4"
                  placeholder="请详细描述举报原因..."
              />
            </div>
          </div>
          <template #footer>
            <el-button @click="showReportDialog = false">取消</el-button>
            <el-button @click="handleReport">确认举报</el-button>
          </template>
        </el-dialog>
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
  display: flex;
  align-items: center;
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
  background: #2c3e50;
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
  max-width: 800px;
  margin: 0 auto;
}

.input-wrapper {
  position: relative;
  background: #fff;
  border: 1px solid #e5e5e5;
  border-radius: 8px;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.05);
  overflow: hidden;
}

.input-area {
  display: flex;
  flex-direction: column;
}

.chat-input {
  padding: 12px;
  border: none;
  outline: none;
  background: none;
  resize: none;
  font-size: 14px;
  line-height: 1.5;
  max-height: 200px;
  min-height: 24px;
}

.input-actions {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  background: #fff;
}

.upload-button {
  margin-right: 8px;
}

.upload-icon {
  padding: 8px;
  font-size: 20px;
  color: #2c3e50;
  border-radius: 4px;
}

.upload-icon:hover {
  background: #f5f7fa;
  color: #34495e;
}

.upload-icon.disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.search-button {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 6px 16px;
  border-radius: 20px;
  font-size: 14px;
  color: #2c3e50;
  border: 1px solid #2c3e50;
  background: #fff;
  transition: all 0.3s;
  height: 32px;
}

.search-button:hover:not(:disabled) {
  background: #2c3e50;
  color: white;
}

.search-button.active {
  background: #2c3e50;
  color: white;
}

.search-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.send-button {
  background: #2c3e50 !important;
  border: none !important;
  border-radius: 6px;
  padding: 8px 20px;
  color: white !important;
  cursor: pointer;
  transition: all 0.3s;
  font-size: 14px;
}

.send-button:hover:not(:disabled) {
  background: #34495e !important;
}

.send-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.file-preview {
  padding: 8px;
  background: #f8f9fa;
  border-bottom: 1px solid #e5e5e5;
}

.file-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  max-width: 600px;
}

.file-item {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 4px 8px;
  background: #fff;
  border-radius: 4px;
  border: 1px solid #e5e5e5;
  max-width: 200px;
}

.file-item .el-icon {
  font-size: 16px;
  color: #909399;
}

.file-name {
  flex: 1;
  font-size: 13px;
  color: #333;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.remove-file {
  padding: 2px;
  color: #909399;
}

.remove-file:hover {
  color: #f56c6c;
}

.message-files {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 8px;
}

.message-file {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 4px 8px;
  background: rgba(255, 255, 255, 0.15);
  border-radius: 4px;
}

.message-file .el-icon {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.9);
}

.message-file .file-name {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.9);
  max-width: 200px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.message.assistant .message-file {
  background: rgba(0, 0, 0, 0.05);
}

.message.assistant .message-file .el-icon,
.message.assistant .message-file .file-name {
  color: #2c3e50;
}

.message-search {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  margin-top: 8px;
  padding: 4px 8px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 4px;
  font-size: 12px;
  color: rgba(255, 255, 255, 0.9);
}

.message.assistant .message-search {
  background: rgba(0, 0, 0, 0.03);
  color: #2c3e50;
}

.message-search .el-icon {
  font-size: 14px;
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

.thinking-chain {
  background: #f8f9fa;
  border-left: 3px solid #2c3e50;
  padding: 12px;
  margin-bottom: 12px;
  border-radius: 0 4px 4px 0;
  font-size: 13px;
  color: #666;
}

.thinking-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  cursor: pointer;
  padding: 4px 0;
  user-select: none;
}

.thinking-header .el-icon {
  transition: transform 0.3s;
}

.thinking-header .el-icon.is-active {
  transform: rotate(-90deg);
}

.thinking-content {
  margin-top: 8px;
  white-space: pre-wrap;
}

.response {
  color: #2c3e50;
}

.action-btn.warning:hover .el-icon {
  color: white;
}

.report-dialog {
  padding: 16px 0;
}

.report-dialog .form-group {
  margin-bottom: 0;
}

.report-dialog label {
  margin-bottom: 8px;
  color: #606266;
}
</style>