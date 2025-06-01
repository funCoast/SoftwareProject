<script setup lang="ts">
import { ref, onMounted, watch,onUnmounted, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import axios from 'axios'
import moment from 'moment'

const baseImageUrl = "http://101.201.208.165"
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
  personID.value = localStorage.getItem('LingXi_uid') || ''
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
            </div>
            <div class="last-message">
              {{ contact.lastMessage.text }}
            </div>
          </div>
          <div v-if="contact.lastMessageTime" class="message-time">
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
        <img src="https://api.iconify.design/material-symbols:chat.svg" alt="开始聊天" class="chat-icon"/>
        <span>请选择一个联系人开始聊天</span>
      </div>

      <!-- 消息列表 -->
      <div v-if="currentContact" ref="messageListRef" class="message-list">
        <div
            v-for="(message, index) in messages"
            :key="index"
            class="message-item"
            :class="{ 'message-self': message.sender !== currentContact.name }"
        >
          <el-avatar :size="32" :src="baseImageUrl + message.avatar" class="message-avatar"/>
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
            placeholder="输入消息，按Enter发送，Shift+Enter换行..."
            @keydown.enter="handleEnterKey"
        />
        <el-button type="primary" :disabled="!newMessage.trim()" @click="sendMessage">
          <img src="https://api.iconify.design/material-symbols:send.svg" alt="发送" class="send-icon"/>
          发送
        </el-button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.message-container {
  display: flex;
  height: 100%;
  background-color: #f8f9fa;
}

.contact-list {
  width: 280px;
  background-color: white;
  border-right: 1px solid #e0e0e0;
  display: flex;
  flex-direction: column;
  box-shadow: 2px 0 8px rgba(0, 0, 0, 0.05);
}

.contact-header {
  padding: 20px;
  border-bottom: 1px solid #eef2f7;
  background: linear-gradient(to right, #ffffff, #f8f9fa);
}

.contact-header h2 {
  margin: 0;
  font-size: 18px;
  color: #2c3e50;
  font-weight: 600;
  position: relative;
  display: inline-block;
}

.contact-header h2::after {
  content: '';
  position: absolute;
  bottom: -6px;
  left: 0;
  width: 100%;
  height: 3px;
  background: #4FAFFF;
  border-radius: 2px;
}

.contact-items {
  flex: 1;
  overflow-y: auto;
}

.no-contacts {
  text-align: center;
  color: #94a3b8;
  padding: 40px 20px;
  font-size: 15px;
}

.contact-item {
  display: flex;
  align-items: center;
  padding: 15px;
  cursor: pointer;
  transition: all 0.3s ease;
  border-bottom: 1px solid #f1f5f9;
  position: relative;
}

.contact-item::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  height: 100%;
  width: 3px;
  background-color: #4FAFFF;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.contact-item:hover {
  background-color: #f8fafc;
}

.contact-item.active {
  background-color: #f0f7ff;
}

.contact-item.active::before {
  opacity: 1;
}

.avatar-wrapper {
  position: relative;
  width: 40px;
  height: 40px;
}

.unread-dot {
  position: absolute;
  top: -4px;
  right: -4px;
  background-color: #f56c6c;
  color: white;
  border-radius: 50%;
  font-size: 10px;
  min-width: 16px;
  height: 16px;
  line-height: 16px;
  text-align: center;
  box-shadow: 0 0 0 2px white;
  padding: 0 4px;
}

.contact-info {
  flex: 1;
  margin-left: 12px;
  overflow: hidden;
}

.contact-name {
  font-size: 14px;
  color: #2c3e50;
  margin-bottom: 4px;
  font-weight: 500;
}

.last-message {
  font-size: 12px;
  color: #94a3b8;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.message-time {
  font-size: 11px;
  color: #94a3b8;
  white-space: nowrap;
}

.message-area {
  flex: 1;
  display: flex;
  flex-direction: column;
  background-color: white;
  position: relative;
}

.message-header {
  padding: 16px 24px;
  border-bottom: 1px solid #eef2f7;
  display: flex;
  align-items: center;
  background: linear-gradient(to right, #ffffff, #f8f9fa);
}

.message-header .contact-name {
  margin-left: 12px;
  font-size: 16px;
  color: #2c3e50;
  font-weight: 500;
}

.no-contact {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: #94a3b8;
  font-size: 16px;
  gap: 16px;
}

.chat-icon {
  width: 48px;
  height: 48px;
  opacity: 0.6;
}

.message-list {
  flex: 1;
  padding: 24px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 20px;
  background-color: #f8fafc;
}

.message-item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  max-width: 80%;
}

.message-item.message-self {
  flex-direction: row-reverse;
  align-self: flex-end;
}

.message-avatar {
  margin-top: 4px;
}

.message-content {
  position: relative;
}

.message-text {
  background-color: white;
  padding: 12px 16px;
  border-radius: 12px;
  font-size: 14px;
  color: #2c3e50;
  line-height: 1.5;
  word-break: break-word;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.05);
  border: 1px solid #e2e8f0;
}

.message-self .message-text {
  background-color: #4FAFFF;
  color: white;
  border: none;
}

.message-time {
  font-size: 11px;
  color: #94a3b8;
  margin-top: 4px;
  text-align: right;
}

.message-input {
  padding: 16px 24px;
  border-top: 1px solid #eef2f7;
  display: flex;
  gap: 12px;
  background: white;
}

.message-input .el-input {
  flex: 1;
}

.message-input .el-textarea__inner {
  border-radius: 8px;
  border-color: #e2e8f0;
  padding: 8px 12px;
  font-size: 14px;
  resize: none;
  transition: all 0.3s ease;
}

.message-input .el-textarea__inner:focus {
  border-color: #4FAFFF;
  box-shadow: 0 0 0 2px rgba(79, 175, 255, 0.1);
}

.message-input .el-button {
  align-self: flex-end;
  height: 36px;
  border-radius: 8px;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 0 16px;
  transition: all 0.3s ease;
}

.send-icon {
  width: 18px;
  height: 18px;
  filter: brightness(0) invert(1);
}

.message-input .el-button:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(79, 175, 255, 0.2);
}

.message-input .el-button:disabled {
  opacity: 0.6;
  transform: none;
  box-shadow: none;
}

::-webkit-scrollbar {
  width: 6px;
}

::-webkit-scrollbar-track {
  background: transparent;
}

::-webkit-scrollbar-thumb {
  background: #cbd5e1;
  border-radius: 3px;
}

::-webkit-scrollbar-thumb:hover {
  background: #94a3b8;
}
</style>
