<script setup lang="ts">
import { ref, onMounted, watch,onUnmounted, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import axios from 'axios'
import moment from 'moment'

const baseImageUrl = "http://122.9.33.84:8000"
const personID = ref('')
const messageListRef = ref<HTMLElement | null>(null)
// 联系人列表
const contacts = ref<{
  id: number
  name: string
  avatar: string
  unread: number
  lastMessage: {
    text: string
  }
  lastMessageTime: string
}[]>([])

// 当前选中的联系人
const currentContact = ref<{
  id: number
  name: string
  avatar: string
} | null>(null)

// 消息列表
const messages = ref<{
  sender: string
  avatar: string
  time: string
  text: string
}[]>([])

// 新消息内容
const newMessage = ref('')

// 获取联系人列表
async function fetchContacts() {
  try {
    const response = await axios({
      method: 'get',
      url: 'user/getContacts',
      params: {
        uid: personID.value
      }
    })
    if (response.data.code === 0) {
      contacts.value = response.data.data
      console.log(contacts.value)
    } else {
      console.log(response.data.message)
      ElMessage.error('获取联系人列表失败：' + response.data.message)
    }
  } catch (error) {
    console.error('获取联系人列表失败:', error)
    ElMessage.error('获取联系人列表失败')
  }
}
function scrollToBottom() {
  nextTick(() => {
    const el = messageListRef.value
    if (!el) return

    const isAtBottom = el.scrollHeight - el.scrollTop - el.clientHeight < 10
    if (isAtBottom) {
      el.scrollTop = el.scrollHeight
    }
  })
}
// 获取与特定联系人的消息记录
async function fetchMessages(contactId: string) {
  try {
    const response = await axios({
      method: 'get',
      url: 'user/getMessages',
      params: {
        messagerId1: personID.value,
        messagerId2: contactId
      }
    })
    if (response.data.code === 0) {
      messages.value = response.data.data
    } else {
      console.log(response.data.message)
      ElMessage.error('获取消息记录失败：' + response.data.message)
    }
  } catch (error) {
    console.error('获取消息记录失败:', error)
    ElMessage.error('获取消息记录失败')
  }
}

// 发送消息
async function sendMessage() {
  if (!newMessage.value.trim() || !currentContact.value) {
    return
  }

  try {
    const response = await axios({
      method: 'post',
      url: 'user/sendMessage',
      data: {
        sender: personID.value,
        receiver: currentContact.value.id,
        message: newMessage.value
      }
    })
    if (response.data.code === 0) {
      newMessage.value = ''
      await fetchMessages(currentContact.value.id.toString())
      nextTick(() => {
        const el = messageListRef.value
        if (el) {
          el.scrollTop = el.scrollHeight
        }
      })
    } else {
      ElMessage.error('发送消息失败：' + response.data.message)
    }
  } catch (error) {
    console.error('发送消息失败:', error)
    ElMessage.error('发送消息失败')
  }
}

// 选择联系人
async function selectContact(contact: any) {
  currentContact.value = {
    id: contact.id,
    name: contact.name,
    avatar: contact.avatar
  }
  await fetchMessages(contact.id.toString())
  nextTick(() => {
    const el = messageListRef.value
    if (el) {
      el.scrollTop = el.scrollHeight
    }
  })
}

function handleEnterKey(event : KeyboardEvent) {
  if (event.ctrlKey || !event.shiftKey) {
    // 阻止默认行为（换行）
    event.preventDefault()
    sendMessage()
  }
}

// 监听当前联系人变化
watch(currentContact, (newVal) => {
  if (newVal) {
    fetchMessages(newVal.id.toString())
  }
})
let refreshTimer: ReturnType<typeof setInterval> | null = null

function startAutoRefresh() {
  refreshTimer = setInterval(async () => {
    if (!currentContact.value || !messageListRef.value) return

    const el = messageListRef.value
    const isNearBottom = el.scrollHeight - el.scrollTop - el.clientHeight < 10

    await fetchMessages(currentContact.value.id.toString())
    await fetchContacts()

    nextTick(() => {
      if (isNearBottom) {
        el.scrollTop = el.scrollHeight
      }
    })
  }, 1000)
}
function stopAutoRefresh() {
  if (refreshTimer) clearInterval(refreshTimer)
}
function formatMessageTime(time: string) {
  const msgTime = moment(time)
  const now = moment()

  if (msgTime.isSame(now, 'day')) {
    return msgTime.format('HH:mm') // 同一天只显示时间
  } else {
    return msgTime.format('MM-DD HH:mm') // 不同天显示日期+时间
  }
}
onMounted(() => {
  personID.value = sessionStorage.getItem('uid') || ''
  fetchContacts()
  startAutoRefresh()
  //sendHelloTo9()
})
onUnmounted(() => {
  stopAutoRefresh()
})
</script>

<template>
  <div class="message-container">
    <!-- 联系人列表 -->
    <div class="contact-list">
      <div class="contact-header">
        <h2>联系人</h2>
      </div>
      <div class="contact-items">
        <!-- 没有联系人时显示 -->
        <div v-if="contacts.length === 0" class="no-contacts">
          暂无联系人
        </div>
        <div
            v-for="contact in contacts"
            :key="contact.id"
            class="contact-item"
            :class="{ active: currentContact?.id === contact.id }"
            @click="selectContact(contact)"
        >
          <div class="avatar-wrapper">
            <el-avatar :size="40" :src="baseImageUrl + contact.avatar" />
            <span v-if="contact.unread > 0" class="unread-dot">{{ contact.unread }}</span>
          </div>
          <div class="contact-info">
            <div class="contact-name">
              {{ contact.name }}
              <!--              <span v-if="contact.unread > 0" class="unread-badge">-->
              <!--                {{ contact.unread }}-->
              <!--              </span>-->
            </div>
            <div class="last-message">
              {{ contact.lastMessage.text }}
            </div>
          </div>
          <div class="message-time">
            {{ formatMessageTime(contact.lastMessageTime)}}
          </div>
        </div>
      </div>
    </div>

    <!-- 消息区域 -->
    <div class="message-area">
      <div v-if="currentContact" class="message-header">
        <el-avatar :size="40" :src="baseImageUrl + currentContact.avatar" />
        <span class="contact-name">{{ currentContact.name }}</span>
      </div>
      <div v-else class="no-contact">
        请选择一个联系人开始聊天
      </div>

      <!-- 消息列表 -->
      <div v-if="currentContact" ref="messageListRef" class="message-list">
        <div
            v-for="(message, index) in messages"
            :key="index"
            class="message-item"
            :class="{ 'message-self': message.sender !== currentContact.name }"
        >
          <el-avatar :size="32" :src="baseImageUrl + message.avatar" />
          <div class="message-content">
            <div class="message-text">{{ message.text }}</div>
            <div class="message-time">
              {{ formatMessageTime(message.time) }}
            </div>
          </div>
        </div>
      </div>

      <!-- 消息输入框 -->
      <div v-if="currentContact" class="message-input">
        <el-input
            v-model="newMessage"
            type="textarea"
            :autosize="{ minRows: 1, maxRows: 3 }"
            placeholder="输入消息..."
            @keydown.enter="handleEnterKey"
        />
        <el-button type="primary" @click="sendMessage">发送</el-button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.message-container {
  display: flex;
  height: 100%;
  background-color: #f5f5f5;
}
.avatar-wrapper {
  position: relative;
  width: 40px;
  height: 40px;
}

.unread-dot {
  position: absolute;
  bottom: -2px;
  left: -2px;
  background-color: #f56c6c;
  color: white;
  border-radius: 50%;
  font-size: 10px;
  width: 16px;
  height: 16px;
  line-height: 16px;
  text-align: center;
  box-shadow: 0 0 0 2px white; /* 白边更像微信 */
}
.no-contacts {
  text-align: center;
  color: #999;
  padding: 20px;
}

.contact-list {
  width: 300px;
  background-color: white;
  border-right: 1px solid #e0e0e0;
  display: flex;
  flex-direction: column;
}

.contact-header {
  padding: 20px;
  border-bottom: 1px solid #e0e0e0;
}

.contact-header h2 {
  margin: 0;
  font-size: 18px;
  color: #333;
}

.contact-items {
  flex: 1;
  overflow-y: auto;
}

.contact-item {
  display: flex;
  align-items: center;
  padding: 15px;
  cursor: pointer;
  transition: background-color 0.3s;
}

.contact-item:hover {
  background-color: #f5f5f5;
}

.contact-item.active {
  background-color: #e6f7ff;
}

.contact-info {
  flex: 1;
  margin-left: 12px;
  overflow: hidden;
}

.contact-name {
  font-size: 14px;
  color: #333;
  margin-bottom: 4px;
  display: flex;
  align-items: center;
}

.unread-badge {
  background-color: #f56c6c;
  color: white;
  font-size: 12px;
  padding: 2px 6px;
  border-radius: 10px;
  margin-left: 8px;
}

.last-message {
  font-size: 12px;
  color: #999;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.message-time {
  font-size: 12px;
  color: #999;
  white-space: nowrap;
}

.message-area {
  flex: 1;
  display: flex;
  flex-direction: column;
  background-color: white;
}

.message-header {
  padding: 20px;
  border-bottom: 1px solid #e0e0e0;
  display: flex;
  align-items: center;
}

.message-header .contact-name {
  margin-left: 12px;
  font-size: 16px;
  color: #333;
}

.no-contact {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #999;
  font-size: 16px;
}

.message-list {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.message-item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
}

.message-item.message-self {
  flex-direction: row-reverse;
}

.message-content {
  max-width: 60%;
}

.message-text {
  background-color: #f0f0f0;
  padding: 10px 15px;
  border-radius: 4px;
  font-size: 14px;
  color: #333;
  word-break: break-word;
}

.message-self .message-text {
  background-color: #e6f7ff;
}

.message-input {
  padding: 20px;
  border-top: 1px solid #e0e0e0;
  display: flex;
  gap: 12px;
}

.message-input .el-input {
  flex: 1;
}

.message-input .el-button {
  align-self: flex-end;
}
</style>
