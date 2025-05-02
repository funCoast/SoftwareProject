<template>
  <div class="agent-edit">
    <!-- 头部信息 -->
    <div class="agent-header">
      <div class="agent-info">
        <el-avatar :size="50" :src="agentInfo.avatar" />
        <div class="agent-meta">
          <h2>{{ agentInfo.name }}</h2>
          <p>{{ agentInfo.description }}</p>
        </div>
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
            <div v-for="kb in selectedKbsList" :key="kb.id" class="selected-item">
              <el-avatar :size="32" :src="kb.icon" />
              <div class="item-info">
                <div class="item-name">{{ kb.name }}</div>
                <div class="item-desc">{{ kb.description }}</div>
                <div class="item-type">{{ kb.type }}</div>
              </div>
            </div>
          </div>
        </div>

        <div class="config-section">
          <h3>插件配置</h3>
          <el-select
            v-model="selectedPlugins"
            multiple
            filterable
            placeholder="选择插件"
            class="full-width"
            popper-class="custom-select-dropdown"
          >
            <el-option
              v-for="plugin in plugins"
              :key="plugin.id"
              :label="plugin.name"
              :value="plugin.id"
            >
              <div class="option-item">
                <el-avatar :size="24" :src="plugin.icon" />
                <div class="option-info">
                  <div class="option-name">{{ plugin.name }}</div>
                  <div class="option-desc">{{ plugin.description }}</div>
                </div>
              </div>
            </el-option>
          </el-select>

          <div class="selected-items">
            <div v-for="plugin in selectedPluginsList" :key="plugin.id" class="selected-item">
              <el-avatar :size="32" :src="plugin.icon" />
              <div class="item-info">
                <div class="item-name">{{ plugin.name }}</div>
                <div class="item-desc">{{ plugin.description }}</div>
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
                <el-avatar :size="24" :src="workflow.icon" />
                <div class="option-info">
                  <div class="option-name">{{ workflow.name }}</div>
                  <div class="option-desc">{{ workflow.description }}</div>
                </div>
              </div>
            </el-option>
          </el-select>

          <div class="selected-items">
            <div v-for="workflow in selectedWorkflowsList" :key="workflow.id" class="selected-item">
              <el-avatar :size="32" :src="workflow.icon" />
              <div class="item-info">
                <div class="item-name">{{ workflow.name }}</div>
                <div class="item-desc">{{ workflow.description }}</div>
              </div>
            </div>
          </div>
        </div>

        <div class="config-section">
          <h3>人物设定</h3>
          <el-input
            v-model="agentInfo.system_prompt"
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
               :class="['message', message.type]">
            <template v-if="message.type === 'user'">
              <div class="message-content user-message">
                <div class="message-info">
                  <span class="message-time">{{ message.time }}</span>
                  <span class="sender-name">{{ message.sender }}</span>
                </div>
                <div class="message-text" style="white-space: pre-line;">{{ message.content }}</div>
              </div>
              <el-avatar class="user-avatar" :size="40" :src="message.avatar" />
            </template>
            <template v-else>
              <el-avatar class="assistant-avatar" :size="40" :src="message.avatar" />
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

<script setup lang="ts">
import { ref, computed, onMounted, onBeforeMount } from 'vue'
import { Plus } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import axios from 'axios'
import router from "../../router";

const agentIdentifier = router.currentRoute.value.params.id

interface Workflow {
  workflow_id: number
  name: string
  description: string
  icon: string
  hover?: boolean
}

onMounted(() => {
  getKnowledgeBases()
  getWorkflows()
  getPlugins()
  getAgentInfo()
})

// 智能体信息
const agentInfo = ref({
  name: 'AI讲师',
  description: 'AI讲师',
  system_prompt: '',
  avatar: 'http://127.0.0.1:8000/media/workflow_icons/00011e25afd2401bba7df0de1db41f6a.png',
  selectedKbs: ref<number[]>([]),
  selectedPlugins: ref<number[]>([]),
  selectedWorkflows: ref<number[]>([])
})

onBeforeMount(() => {
  getAvatar()
  fetchUserInfo()
})

const useravatar = ref('')
function getAvatar() {
  axios({
    method: 'get',
    url: 'user/getAvatar',
    params: {
      uid: sessionStorage.getItem('uid')
    }
  }).then(function (response) {
    if (response.data.code === 0) {
      useravatar.value = 'http://127.0.0.1:8000' + response.data.avatar
      console.log(useravatar.value)
    } else {
      alert(response.data.message)
    }
  })
}

const userInfo = ref({
  name: '',
  account: '',
  description: '',
  following: 0,
  followers: 0,
})
function fetchUserInfo() {
  axios({
    method: 'get',
      url: '/user/fetchProfile',
    params: {
      uid: sessionStorage.getItem('uid')
    }
  }).then(function (response) {
    if (response.data.code === 0) {
      userInfo.value = response.data.data
      console.log('获取用户信息成功')
    } else {
      console.log(response.data.message)
    }
  })
}




// 知识库列表
const knowledgeBases = ref([])

// 获取知识库列表
async function getKnowledgeBases() {
  try {
    const response = await axios({
      method: 'get',
      url: '/rl/getKnowledgeBases',
      params: {
        uid: sessionStorage.getItem('uid')
      },
    })
    
    if (response.data.code === 0) {
      knowledgeBases.value = response.data.knowledgeBases
      console.log('获取知识库列表成功')
    } else {
      console.log(response.data.message)
    }
  } catch (error) {
    console.error('获取知识库列表失败:', error)
  }
}

// 插件相关
const plugins = ref([])

async function getPlugins() {
  try {
    const response = await axios({
      method: 'get',
      url: '/plugins/getPlugins',
      params: {
        uid: sessionStorage.getItem('uid')
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
const workflows = ref([])

// 获取所有工作流
async function getWorkflows() {
  try {
    const uid = sessionStorage.getItem('uid')
    if (!uid) {
      console.error('用户ID不存在')
      return
    }

    const response = await axios({
      method: 'get',
      url: '/workflow/fetchAll',
      params: {
        uid
      }
    })
    
    if (response.data.code === 0) {
      workflows.value = response.data.workflows.map((workflow: Workflow) => ({
        ...workflow,
        icon: 'http://127.0.0.1:8000' + workflow.icon,
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

async function getAgentInfo() {
  try {
    const response = await axios({
      method: 'get',
      url: 'agent/getAgentInfo',
      params: {
        ag_id: agentIdentifier
      },
    })
    if (response.data.code === 0) {
      agentInfo.value = response.data.agentInfo
      console.log('获取配置成功')
    } else {
      console.log(response.data.message)
    }
  } catch (error) {
    console.error('获取配置失败:', error)
  }
}

// 计算选中的列表
const selectedKbsList = computed(() => 
  knowledgeBases.value.filter(kb => agentInfo.value.selectedKbs.includes(kb.id))
)

const selectedPluginsList = computed(() => 
  plugins.value.filter(plugin => agentInfo.value.selectedPlugins.includes(plugin.id))
)

const selectedWorkflowsList = computed(() => 
  workflows.value.filter(workflow => agentInfo.value.selectedWorkflows.includes(workflow.id))
)

// 聊天相关
const messageInput = ref('')
const chatHistory = ref([
  // {
  //   type: 'assistant',
  //   sender: '天气助手',
  //   content: '你好！我是你的天气助手，可以为你提供天气预报和穿衣建议。',
  //   time: '10:00',
  //   avatar: 'https://example.com/weather-bot-avatar.png'
  // },
  {
    type: 'user',
    sender: 'Herry',
    content: '北京限行规则是什么？',
    time: '2025-04-28 11:08',
    avatar: 'http://127.0.0.1:8000/media/avatars/2.jpg'
  },
  {
    type: 'assistant',
    sender: 'AI讲师',
    content: '根据2025年最新政策，北京市工作日实行机动车尾号限行，限行时间为早7:00至晚20:00，限行范围为五环路以内（不含五环路）。具体规则如下：\n' +
        '周一：限行尾号1和6\n' +
        '周二：限行尾号2和7\n' +
        '周三：限行尾号3和8\n' +
        '周四：限行尾号4和9\n' +
        '周五：限行尾号5和0\n' +
        '（节假日不限行）\n' +
        '请注意规则会每年调整一次，建议出行前查询官方通知。',
    time: '2025-04-28 11:09',
    avatar: 'http://127.0.0.1:8000/media/workflow_icons/00011e25afd2401bba7df0de1db41f6a.png'
  }
])

async function sendsendMessage() {
  try {
    const response = await axios({
      method: 'post',
      url: 'agent/sendMessage',
      params: {
        type: 'user',
        sender: userInfo.value.name,
        content: messageInput.value,
        time: new Date().toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' }),
        avatar: useravatar.value
      },
    })
    if (response.data.code === 0) {
      chatHistory.value.push({
        type: response.data.type,
        sender: response.data.sender,
        content: response.data.content,
        time: response.data.time,
        avatar: response.data.avatar
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
    type: 'user',
    sender: userInfo.value.name,
    content: messageInput.value,
    time: new Date().toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' }),
    avatar: useravatar.value
  })
  
  messageInput.value = ''
}

async function updateAgentInfo() {
  try {
    const response = await axios({
      method: 'post',
      url: 'agent/updateAgentInfo',
      params: {
        ag_id: agentIdentifier,
        name: agentInfo.value.name,
        description: agentInfo.value.description,
        system_prompt: agentInfo.value.system_prompt,
        avatar: agentInfo.value.avatar,
        selectedKbs: agentInfo.value.selectedKbs,
        selectedPlugins: agentInfo.value.selectedPlugins,
        selectedWorkflows: agentInfo.value.selectedWorkflows
      },
    })
    if (response.data.code === 0) {
      console.log('配置更新成功')
      alert("配置已保存")
      ElMessage.success('配置已保存')
    } else {
      console.log(response.data.message)
    }
  } catch (error) {
    console.error('配置更新失败:', error)
  }
}

// 确认按钮处理函数
const handleConfirm = () => {
  updateAgentInfo()
}
</script>

<style scoped>
.agent-edit {
  padding: 20px;
  height: 100vh;
  display: flex;
  flex-direction: column;
}

.agent-header {
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
</style>
