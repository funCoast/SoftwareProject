<script setup lang="ts">
import { ref, computed, onMounted, onBeforeMount, watch, inject, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import axios from 'axios'
import {useRoute} from "vue-router";
import { marked } from 'marked'
import router from "@/router.ts";
import {Close, Document, Plus, Search, ArrowDown} from "@element-plus/icons-vue";
import type { UploadInstance } from 'element-plus'

const route = useRoute()
const agent_id = route.params.id
const uid = ref<string>('')
const currentUid = ref<string>('')
const userAvatar = inject('avatar') as string

interface KnowledgeBase {
  id: number
  name: string
  description: string
  icon: string
  type: string
}

interface Workflow {
  id: number
  name: string
  description: string
  icon: string
  hover?: boolean
}

interface AgentInfo {
  name: string
  description: string
  icon: string
  status: number
  config: {
    system_prompt: string
    selectedKbs: number[]
    selectedPlugins: number[]
    selectedWorkflows: number[]
    selectedModel: string
    opening_line: string
  }
}

onMounted(() => {
  getAgentInfo()
  getKnowledgeBases()
  getWorkflows()
  fetchMessage()
})

onBeforeMount(() => {
  uid.value = route.query.uid as string
  currentUid.value = localStorage.getItem('LingXi_uid') || ''
  fetchUserInfo()
})

// 智能体信息
const agentInfo = ref<AgentInfo>({
  name: '',
  description: '',
  icon: '',
  status: 0,
  config: {
    system_prompt: '',
    selectedKbs: [],
    selectedPlugins: [],
    selectedWorkflows: [],
    selectedModel: 'qwen-plus',
    opening_line: ''
  }
})

// 模型选项
const modelOptions = [
  { label: '通义千问', value: 'qwen-plus' },
  { label: 'DeepSeek', value: 'deepseek-r1' },
  { label: '智谱AI', value: 'chatglm-6b-v2' }
]

const userName = ref('')
function fetchUserInfo() {
  axios({
    method: 'get',
    url: '/user/fetchProfile',
    params: {
      uid: uid.value
    }
  }).then(function (response) {
    if (response.data.code === 0) {
      userName.value = response.data.data.name
      console.log('获取用户信息成功')
    } else {
      console.log(response.data.message)
    }
  })
}

// 知识库列表
const knowledgeBases = ref<KnowledgeBase[]>([])

// 获取知识库列表
async function getKnowledgeBases() {
  try {
    const response = await axios({
      method: 'get',
      url: '/rl/getKnowledgeBases',
      params: {
        uid: uid.value
      },
    })

    if (response.data.code === 0) {
      knowledgeBases.value = response.data.knowledgeBases.map((kb: KnowledgeBase) => ({
        ...kb,
        icon: 'http://122.9.33.84:8000' + kb.icon
      }))
      console.log('获取知识库列表成功')
    } else {
      console.log(response.data.message)
    }
  } catch (error) {
    console.error('获取知识库列表失败:', error)
  }
}

// 工作流相关
const workflows = ref<Workflow[]>([])

// 获取所有工作流
async function getWorkflows() {
  try {
    const currentUid = uid.value
    if (!currentUid) {
      console.error('用户ID不存在')
      return
    }

    const response = await axios({
      method: 'get',
      url: '/workflow/fetchAll',
      params: {
        uid: currentUid
      }
    })
    if (response.data.code === 0) {
      workflows.value = response.data.workflows.map((workflow: Workflow) => ({
        ...workflow,
        icon: 'http://122.9.33.84:8000' + workflow.icon,
        hover: false
      }))
      console.log('获取工作流列表成功')
    } else {
      console.log(response.data.message)
    }
  } catch (error) {
    console.error('获取工作流列表失败:', error)
  }
}

// 状态按钮相关
const statusButton = computed<{
  text: string
  disabled: boolean
  type: 'primary' | 'success' | 'warning' | 'danger' | 'info' | 'text'
  handler?: () => void
}>(() => {
  switch (agentInfo.value.status) {
    case 0:
      return {
        text: '发布智能体',
        disabled: false,
        type: 'primary',
        handler: handleRelease
      }
    case 1:
      return {
        text: '正在审核中',
        disabled: true,
        type: 'info'
      }
    case 2:
      return {
        text: '下架智能体',
        disabled: false,
        type: 'warning',
        handler: handleRemove
      }
    default:
      return {
        text: '未知状态',
        disabled: true,
        type: 'info'
      }
  }
})

// 获取智能体信息
async function getAgentInfo() {
  try {
    const response = await axios({
      method: 'get',
      url: 'agent/getInfo',
      params: {
        agent_id: agent_id
      }
    })
    if (response.data.code === 0) {
      agentInfo.value = response.data
      console.log(agentInfo.value)
      console.log("智能体：", response.data.status)
      console.log('获取配置成功')
    } else {
      ElMessage.error('获取配置失败：' + response.data.message)
    }
  } catch (error) {
    console.error('获取配置失败:', error)
    ElMessage.error('获取配置失败')
  }
}

// 发布智能体
async function handleRelease() {
  try {
    const response = await axios({
      method: 'post',
      url: 'agent/release',
      data: {
        uid: uid.value,
        agent_id: agent_id
      }
    })
    if (response.data.code === 0) {
      ElMessage.success('发布成功')
      agentInfo.value.status = 1 // 更新状态为审核中
    } else {
      ElMessage.error(response.data.message)
    }
  } catch (error) {
    console.error('发布失败:', error)
    ElMessage.error('发布失败')
  }
}

// 下架智能体
async function handleRemove() {
  try {
    const response = await axios({
      method: 'post',
      url: 'agent/remove',
      data: {
        uid: uid.value,
        agent_id: agent_id
      }
    })
    if (response.data.code === 0) {
      ElMessage.success('下架成功')
      agentInfo.value.status = 0 // 更新状态为未发布
    } else {
      ElMessage.error(response.data.message)
    }
  } catch (error) {
    console.error('下架失败:', error)
    ElMessage.error('下架失败')
  }
}

// 更新智能体信息
async function updateAgentInfo() {
  try {
    const response = await axios({
      method: 'post',
      url: 'agent/updateInfo',
      data: {
        agent_id: agent_id,
        system_prompt: agentInfo.value.config.system_prompt,
        selectedKbs: agentInfo.value.config.selectedKbs,
        selectedWorkflows: agentInfo.value.config.selectedWorkflows,
        selectedModel: agentInfo.value.config.selectedModel,
        opening_line: agentInfo.value.config.opening_line
      }
    })
    if (response.data.code === 0) {
      console.log("配置: ", agentInfo.value.config)
      if (agentInfo.value.config.opening_line) {
        chatHistory.value.push({
          sender: 'assistant',
          content: {
            thinking_chain: '',
            response: agentInfo.value.config.opening_line
          },
          time: new Date().toISOString().replace('T', ' ').slice(0, 19)
        })
      }
      ElMessage.success("保存成功！")
    } else {
      ElMessage.error(response.data.message)
    }
  } catch (error) {
    console.error('配置更新失败:', error)
    ElMessage.error('配置更新失败')
  }
}

// 修改计算属性为响应式引用
const selectedKbs = ref<number[]>([])
const selectedWorkflows = ref<number[]>([])

// 监听agentInfo的变化，更新选中的知识库和大模型
watch(() => agentInfo.value.config.selectedKbs, (newVal) => {
  if (JSON.stringify(newVal) !== JSON.stringify(selectedKbs.value)) {
    selectedKbs.value = [...newVal]
  }
}, { immediate: true })

watch(() => agentInfo.value.config.selectedWorkflows, (newVal) => {
  if (JSON.stringify(newVal) !== JSON.stringify(selectedWorkflows.value)) {
    selectedWorkflows.value = [...newVal]
  }
}, { immediate: true })

// 监听选中的知识库和大模型变化，更新agentInfo
watch(selectedKbs, (newVal) => {
  if (JSON.stringify(newVal) !== JSON.stringify(agentInfo.value.config.selectedKbs)) {
    agentInfo.value.config.selectedKbs = [...newVal]
  }
})

watch(selectedWorkflows, (newVal) => {
  if (JSON.stringify(newVal) !== JSON.stringify(agentInfo.value.config.selectedWorkflows)) {
    agentInfo.value.config.selectedWorkflows = [...newVal]
  }
})

function goToWorkflowEdit(id: number) {
  router.push({
    path: `/workspace/workflow/${id}`,
    query: { uid: uid.value }
  })
}

function goToKBEdit(id: number, type: string | undefined) {
  if (!type) return
  router.push({
    path: `/workspace/${type}/${id}`,
    query: { uid: uid.value }
  })
}


interface Message {
  sender: 'user' | 'assistant'
  content: {
    thinking_chain: string,
    response: string
  }
  time: string
  files?: string[]
  search?: boolean
  showThinking?: boolean
}

// 聊天相关
const messageInput = ref('')
const chatHistory = ref<Message[]>([])
const uploadRef = ref<UploadInstance>()
const fileList = ref<File[]>([])
const enableSearch = ref(false)

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

// 文件上传前的钩子，用于校验文件类型和大小
function handleChange(file: File) {
  const isLt5M = file.size / 1024 / 1024 < 20
  if (!isLt5M) {
    ElMessage.warning("文件大小不能超过 20MB！")
    fileList.value.splice(fileList.value.indexOf(file), 1)
    return
  }
  // 将文件添加到fileList中
  fileList.value.push(file)
  console.log('fileList:', fileList.value)
}

function handleFileRemove(file: File) {
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

// 添加折叠控制函数
function toggleThinkingChain(index: number) {
  if (chatHistory.value[index]) {
    chatHistory.value[index].showThinking = !chatHistory.value[index].showThinking
  }
}

// 修改发送消息函数，添加默认折叠状态
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
    files: fileList.value.map(file => file.name),
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
    formData.append('uid', uid.value)
    formData.append('content', messageInput.value)
    formData.append('agent_id', agent_id as string)
    formData.append('search', enableSearch.value.toString())

    for (const file of fileList.value) {
      console.log('file:', file)
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
      method: 'get',
      url: 'agent/clearHistoryMessage',
      params: {
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

// 确认按钮处理函数
const handleConfirm = () => {
  updateAgentInfo()
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

// 渲染Markdown格式
function renderedMarkdown(content: string) {
  return marked(content)
}
</script>

<template>
  <div class="agent-edit">
    <!-- 头部信息 -->
    <div class="agent-header">
      <div class="agent-info">
        <el-avatar :size="50" :src="'http://122.9.33.84:8000' + agentInfo.icon" />
        <div class="agent-meta">
          <h2>{{ agentInfo.name }}</h2>
          <p>{{ agentInfo.description }}</p>
        </div>
      </div>
      <div class="status-actions">
        <el-button
          type="danger"
          plain
          @click="clearMessage"
        >
          清除历史对话
        </el-button>
        <el-button
          :type="statusButton.type"
          :disabled="statusButton.disabled"
          @click="statusButton.handler"
        >
          {{ statusButton.text }}
        </el-button>
      </div>
    </div>

    <div class="main-content">
      <!-- 左侧配置面板 -->
      <div class="left-panel">
        <div class="config-section">
          <h3>大模型配置</h3>
          <el-select
              v-model="agentInfo.config.selectedModel"
              placeholder="请选择大模型"
              class="full-width"
          >
            <el-option
                v-for="option in modelOptions"
                :key="option.value"
                :label="option.label"
                :value="option.value"
            />
          </el-select>
        </div>

        <div class="config-section">
          <h3>知识库配置</h3>
          <el-select
            v-model="selectedKbs"
            multiple
            filterable
            placeholder="选择知识库"
            class="full-width"
            popper-class="custom-select-dropdown"
          >
            <el-option
              v-for="kb in knowledgeBases"
              :key="kb.id"
              :label="kb.name"
              :value="kb.id"
            >
              <div class="option-item">
                <el-avatar :size="24" :src="kb.icon" style="margin-top: -6px;"/>
                <div class="option-info">
                  <div class="option-name" style="margin-top: -3px;">{{ kb.name }}</div>
                </div>
              </div>
            </el-option>
          </el-select>

          <div class="selected-items">
            <div v-for="kb in selectedKbs"
                 :key="kb"
                 class="selected-item"
                 @click="goToKBEdit(kb, knowledgeBases.find(k => k.id === kb)?.type)"
                 style="cursor: pointer;"
            >
              <el-avatar :size="32" :src="knowledgeBases.find(k => k.id === kb)?.icon"/>
              <div class="item-info">
                <div class="item-name">{{ knowledgeBases.find(k => k.id === kb)?.name }}</div>
                <div class="item-desc">{{ knowledgeBases.find(k => k.id === kb)?.description }}</div>
                <div class="item-type">{{ knowledgeBases.find(k => k.id === kb)?.type }}</div>
              </div>
            </div>
          </div>
        </div>

        <div class="config-section">
          <h3>工作流配置</h3>
          <el-select
            v-model="selectedWorkflows"
            multiple
            filterable
            placeholder="选择工作流"
            class="full-width"
            popper-class="custom-select-dropdown"
          >
            <el-option
              v-for="workflow in workflows"
              :key="workflow.id"
              :label="workflow.name"
              :value="workflow.id"
            >
              <div class="option-item">
                <el-avatar :size="24" :src="workflow.icon" style="margin-top: -6px;"/>
                <div class="option-info">
                  <div class="option-name" style="margin-top: -3px;">{{ workflow.name }}</div>
                </div>
              </div>
            </el-option>
          </el-select>

          <div class="selected-items">
            <div v-for="workflow in selectedWorkflows"
                 :key="workflow"
                 class="selected-item"
                 @click="goToWorkflowEdit(workflow)"
                 style="cursor: pointer;">
              <el-avatar :size="32" :src="workflows.find(w => w.id === workflow)?.icon" />
              <div class="item-info">
                <div class="item-name">{{ workflows.find(w => w.id === workflow)?.name }}</div>
                <div class="item-desc">{{ workflows.find(w => w.id === workflow)?.description }}</div>
              </div>
            </div>
          </div>
        </div>

        <div class="config-section">
          <h3>人物设定</h3>
          <el-input
            v-model="agentInfo.config.system_prompt"
            type="textarea"
            :rows="6"
            placeholder="请输入智能体的人物设定..."
          />
        </div>

        <div class="config-section">
          <h3>开场白</h3>
          <el-input
              v-model="agentInfo.config.opening_line"
              type="textarea"
              :rows="6"
              placeholder="请输入智能体的开场白..."
          />
        </div>

        <div class="config-actions">
          <el-button type="primary" @click="handleConfirm">确定</el-button>
        </div>
      </div>

      <!-- 右侧聊天面板 -->
      <div class="chat-panel">
        <div class="chat-messages" ref="chatMessagesRef">
          <div v-for="(message, index) in chatHistory" :key="index"
               :class="['message', message.sender]">
            <template v-if="message.sender === 'user'">
              <div class="message-content user-message">
                <div class="message-info">
                  <span class="message-time">{{ message.time }}</span>
                  <span class="sender-name">{{ message.sender }}</span>
                </div>
                <div class="message-text" style="white-space: pre-line;">{{ message.content.response }}</div>
                <div v-if="message.files && message.files.length > 0" class="message-files">
                  <div v-for="file in message.files" :key="file" class="message-file">
                    <el-icon><Document /></el-icon>
                    <span class="file-name">{{ file }}</span>
                  </div>
                </div>
                <div v-if="message.search" class="message-search">
                  <el-icon><Search /></el-icon>
                  <span>已开启联网搜索</span>
                </div>
              </div>
              <el-avatar class="user-avatar" :size="40" :src="userAvatar" />
            </template>
            <template v-else>
              <el-avatar class="assistant-avatar" :size="40" :src="'http://122.9.33.84:8000' + agentInfo.icon" />
              <div class="message-content assistant-message">
                <div class="message-info">
                  <span class="sender-name">{{ message.sender }}</span>
                  <span class="message-time">{{ message.time }}</span>
                </div>
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
            </template>
          </div>

          <!-- 添加加载提示 -->
          <div v-if="isLoading" class="message assistant">
            <el-avatar class="assistant-avatar" :size="40" :src="'http://122.9.33.84:8000' + agentInfo.icon" />
            <div class="message-content assistant-message">
              <div class="message-info">
                <span class="sender-name">assistant</span>
              </div>
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

        <div class="chat-input">
          <div class="input-container">
            <div class="input-wrapper">
              <div v-if="fileList.length > 0" class="file-preview">
                <div class="file-list">
                  <div v-for="file in fileList" :key="file.name" class="file-item">
                    <el-icon><Document /></el-icon>
                    <span class="file-name">{{ file.name }}</span>
                    <el-button type="text" class="remove-file" @click="handleFileRemove(file)">
                      <el-icon><Close /></el-icon>
                    </el-button>
                  </div>
                </div>
              </div>

              <div class="input-area">
                <el-input
                  v-model="messageInput"
                  type="textarea"
                  :rows="3"
                  placeholder="输入消息... (Ctrl+Shift+Enter 发送)"
                  @keydown.enter.prevent="handleEnter"
                  resize="none"
                  class="message-input"
                />

                <div class="input-actions">
                  <el-upload
                    ref="uploadRef"
                    class="upload-button"
                    action=""
                    accept=".txt,.pdf,.doc,.docx,.md,.xls,.xlsx"
                    :auto-upload="false"
                    :show-file-list="false"
                    :on-change="handleChange"
                    :on-remove="handleFileRemove"
                    :disabled="enableSearch"
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
                    type="primary" 
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
  </div>
</template>

<style scoped>
.agent-edit {
  padding: 20px;
  height: 100vh;
  display: flex;
  flex-direction: column;
}

.agent-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding: 20px;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0,0,0,0.1);
}

.agent-info {
  display: flex;
  align-items: center;
  gap: 20px;
}

.agent-meta {
  flex: 1;
}

.agent-meta h2 {
  margin: 0 0 8px 0;
  font-size: 24px;
}

.agent-meta p {
  margin: 0;
  color: #666;
}

.status-actions {
  margin-left: 20px;
}

.main-content {
  flex: 1;
  display: flex;
  gap: 20px;
  min-height: 0;
}

.left-panel {
  width: 300px;
  background: #fff;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 12px 0 rgba(0,0,0,0.1);
  overflow-y: auto;
}

.config-section {
  margin-bottom: 30px;
}

.config-section h3 {
  margin: 0 0 16px 0;
  font-size: 18px;
  color: #333;
}

.full-width {
  width: 100%;
}

:deep(.custom-select-dropdown) {
  .el-select-dropdown__item {
    padding: 0;
    height: auto;
    
    &.selected {
      font-weight: normal;
    }
  }
}

.option-item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 12px;
  min-height: 70px;
}

.option-info {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.option-name {
  font-weight: 500;
  font-size: 14px;
  line-height: 1.4;
  margin-bottom: 4px;
  color: #333;
}

.option-desc {
  font-size: 12px;
  line-height: 1.4;
  color: #666;
  margin-bottom: 4px;
}

.option-type {
  font-size: 12px;
  line-height: 1.4;
  color: #409EFF;
}

.selected-items {
  margin-top: 16px;
}

.selected-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  margin-bottom: 8px;
  background: #f5f7fa;
  border-radius: 6px;
}

.item-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.item-name {
  font-weight: 500;
  line-height: 1.2;
  margin-bottom: 4px;
}

.item-desc {
  font-size: 12px;
  color: #666;
  line-height: 1.2;
}

.item-type {
  font-size: 12px;
  color: #409EFF;
  line-height: 1.2;
  margin-top: 2px;
}

.chat-panel {
  flex: 1;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0,0,0,0.1);
  display: flex;
  flex-direction: column;
}

.chat-messages {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
}

.message {
  display: flex;
  gap: 12px;
  margin-bottom: 20px;
  width: 100%;
}

.message.user {
  justify-content: flex-end;
}

.message-content {
  flex: 0 1 auto;
  max-width: 70%;
  padding: 12px;
  border-radius: 8px;
}

.message.assistant {
  justify-content: flex-start;
}

.assistant-message {
  background: #f5f7fa;
  border-radius: 0 8px 8px 8px;
  margin-right: auto;
}

.user-message {
  background: #ecf5ff;
  border-radius: 8px 0 8px 8px;
  margin-left: auto;
}

.message-info {
  margin-bottom: 8px;
  display: flex;
  gap: 8px;
  font-size: 12px;
}

.sender-name {
  font-weight: 500;
  color: #333;
}

.message-time {
  color: #999;
}

.message-text {
  line-height: 1.5;
  word-break: break-word;
}

.thinking-chain {
  background: #f8f9fa;
  border-left: 3px solid #409EFF;
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

.chat-input {
  padding: 20px;
  border-top: 1px solid #eee;
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

.message-input {
  padding: 12px;
}

.message-input :deep(.el-textarea__inner) {
  border: none;
  box-shadow: none;
  resize: none;
  padding: 0;
  min-height: 24px;
  max-height: 200px;
  font-size: 14px;
  line-height: 1.5;
}

.input-actions {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  background: #fff;
}

.search-button {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 6px 16px;
  border-radius: 20px;
  font-size: 14px;
  color: #909399;
  border: 1px solid #dcdfe6;
  background: #fff;
  transition: all 0.3s;
  height: 32px;
}

.search-button:hover:not(:disabled) {
  color: #409EFF;
  border-color: #409EFF;
}

.search-button.active {
  color: #409EFF;
  border-color: #409EFF;
  background: #ecf5ff;
}

.search-button:disabled {
  opacity: 0.5;
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

.upload-button {
  margin-right: 8px;
}

.upload-icon {
  padding: 8px;
  font-size: 20px;
  color: #909399;
  border-radius: 4px;
}

.upload-icon:hover {
  background: #f5f7fa;
  color: #409EFF;
}

.send-button {
  padding: 8px 20px;
  font-size: 14px;
}

.send-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
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
  padding: 6px 12px;
  background: #f0f2f5;
  border-radius: 6px;
  border: 1px solid #e5e5e5;
}

.message-file .el-icon {
  font-size: 16px;
  color: #909399;
}

.message-file .file-name {
  font-size: 13px;
  color: #333;
  max-width: 200px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.message-search {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  margin-top: 8px;
  padding: 4px 8px;
  background: #ecf5ff;
  border-radius: 4px;
  font-size: 12px;
  color: #409EFF;
}

.message-search .el-icon {
  font-size: 14px;
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
  background: #409EFF;
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
</style>
