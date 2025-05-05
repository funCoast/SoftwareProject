<script setup lang="ts">
import { ref, computed, onMounted, onBeforeMount, watch, inject } from 'vue'
import { ElMessage } from 'element-plus'
import axios from 'axios'
import {useRoute} from "vue-router";
import router from "../../router.ts";

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

interface Plugin {
  id: number
  name: string
  description: string
  icon: string
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
  }
}

onMounted(() => {
  getAgentInfo()
  getKnowledgeBases()
  getWorkflows()
  // getPlugins()
})

onBeforeMount(() => {
  uid.value = route.query.uid as string
  currentUid.value = sessionStorage.getItem('uid') || ''
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
    selectedWorkflows: []
  }
})


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
        icon: 'http://122.9.33.84:8000/' + kb.icon
      }))
      console.log('获取知识库列表成功')
    } else {
      console.log(response.data.message)
    }
  } catch (error) {
    console.error('获取知识库列表失败:', error)
  }
}

// 插件相关
const plugins = ref<Plugin[]>([])

async function getPlugins() {
  try {
    const response = await axios({
      method: 'get',
      url: '/plugins/getPlugins',
      params: {
        uid: uid.value
      },
    })

    if (response.data.code === 0) {
      plugins.value = response.data.plugins
      console.log('获取插件列表成功')
    } else {
      console.log(response.data.message)
    }
  } catch (error) {
    console.error('获取插件列表失败:', error)
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
        selectedPlugins: [],
        selectedWorkflows: agentInfo.value.config.selectedWorkflows
      }
    })
    if (response.data.code === 0) {
      console.log("配置: ", agentInfo.value.config)
      // ElMessage.success('配置已保存')
      alert("保存成功！")
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

// 监听agentInfo的变化，更新选中的知识库和工作流
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

// 监听选中的知识库和工作流变化，更新agentInfo
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

function goToKBEdit(id: number, type: string) {
  router.push({
    path: `/workspace/${type}/${id}`,
    query: { uid: uid.value }
  })
}


interface Message {
  sender: 'user' | 'assistant'
  content: string
  time: string
}

// 聊天相关
const messageInput = ref('')
const chatHistory = ref<Message[]>([])

async function sendsendMessage() {
  try {
    const response = await axios({
      method: 'post',
      url: 'agent/sendMessage',
      data: {
        uid: uid.value,
        agent_id: agent_id,
        content: messageInput.value
      },
    })
    if (response.data.code === 0) {
      chatHistory.value.push({
        sender: 'assistant',
        content: response.data.content,
        time: response.data.time,
      })
      console.log('信息发送成功')
    } else {
      console.log(response.data.message)
    }
  } catch (error) {
    console.error('信息发送失败:', error)
  }
}

// 发送消息
const sendMessage = () => {
  if (!messageInput.value.trim()) return
  sendsendMessage()
  chatHistory.value.push({
    sender: 'user',
    content: messageInput.value,
    time: new Date().toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' }),
  })

  messageInput.value = ''
}

// 确认按钮处理函数
const handleConfirm = () => {
  updateAgentInfo()
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
      <div class="status-actions" v-if="uid === currentUid">
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
                <el-avatar :size="24" :src="kb.icon" />
                <div class="option-info">
                  <div class="option-name">{{ kb.name }}</div>
                  <div class="option-desc">{{ kb.description }}</div>
                  <div class="option-type">类型: {{ kb.type }}</div>
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
              <el-avatar :size="32" :src="knowledgeBases.find(k => k.id === kb)?.icon" />
              <div class="item-info">
                <div class="item-name">{{ knowledgeBases.find(k => k.id === kb)?.name }}</div>
                <div class="item-desc">{{ knowledgeBases.find(k => k.id === kb)?.description }}</div>
                <div class="item-type">{{ knowledgeBases.find(k => k.id === kb)?.type }}</div>
              </div>
            </div>
          </div>
        </div>

<!--        <div class="config-section">-->
<!--          <h3>插件配置</h3>-->
<!--          <el-select-->
<!--            v-model="selectedPlugins"-->
<!--            multiple-->
<!--            filterable-->
<!--            placeholder="选择插件"-->
<!--            class="full-width"-->
<!--            popper-class="custom-select-dropdown"-->
<!--          >-->
<!--            <el-option-->
<!--              v-for="plugin in plugins"-->
<!--              :key="plugin.id"-->
<!--              :label="plugin.name"-->
<!--              :value="plugin.id"-->
<!--            >-->
<!--              <div class="option-item">-->
<!--                <el-avatar :size="24" :src="plugin.icon" />-->
<!--                <div class="option-info">-->
<!--                  <div class="option-name">{{ plugin.name }}</div>-->
<!--                  <div class="option-desc">{{ plugin.description }}</div>-->
<!--                </div>-->
<!--              </div>-->
<!--            </el-option>-->
<!--          </el-select>-->

<!--          <div class="selected-items">-->
<!--            <div v-for="plugin in selectedPlugins" :key="plugin.id" class="selected-item">-->
<!--              <el-avatar :size="32" :src="plugin.icon" />-->
<!--              <div class="item-info">-->
<!--                <div class="item-name">{{ plugin.name }}</div>-->
<!--                <div class="item-desc">{{ plugin.description }}</div>-->
<!--              </div>-->
<!--            </div>-->
<!--          </div>-->
<!--        </div>-->

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
                <el-avatar :size="24" :src="workflow.icon" />
                <div class="option-info">
                  <div class="option-name">{{ workflow.name }}</div>
                  <div class="option-desc">{{ workflow.description }}</div>
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

        <div class="config-actions">
          <el-button type="primary" @click="handleConfirm">确定</el-button>
        </div>
      </div>

      <!-- 右侧聊天面板 -->
      <div class="chat-panel">
        <div class="chat-messages" ref="chatMessages">
          <div v-for="(message, index) in chatHistory" :key="index" 
               :class="['message', message.sender]">
            <template v-if="message.sender === 'user'">
              <div class="message-content user-message">
                <div class="message-info">
                  <span class="message-time">{{ message.time }}</span>
                  <span class="sender-name">{{ message.sender }}</span>
                </div>
                <div class="message-text" style="white-space: pre-line;">{{ message.content }}</div>
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
                <div class="message-text" style="white-space: pre-line;">{{ message.content }}</div>
              </div>
            </template>
          </div>
        </div>

        <div class="chat-input">
          <el-input
            v-model="messageInput"
            type="textarea"
            :rows="3"
            placeholder="输入消息..."
            @keyup.enter.native="sendMessage"
          />
          <el-button type="primary" @click="sendMessage">发送</el-button>
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

.chat-input {
  padding: 20px;
  border-top: 1px solid #eee;
  display: flex;
  gap: 12px;
  background: #fff;
}

.chat-input .el-textarea {
  flex: 1;
}

.chat-input .el-button {
  align-self: flex-end;
}

:deep(.el-select-dropdown__item) {
  padding: 8px 12px;
  height: auto;
  line-height: inherit;
}

:deep(.el-select-dropdown__item.selected) {
  font-weight: normal;
}

:deep(.el-select-dropdown__item .el-avatar) {
  vertical-align: middle;
}

.config-actions {
  margin-top: 20px;
  padding: 0 20px;
  display: flex;
  justify-content: flex-end;
}

.agent-icon {
  width: 24px;
  height: 24px;
  padding: 2px;
  background: #fff;
  border-radius: 6px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}
</style>
