<template>
    <div class="messaging-container">
      <!-- 主内容区域 -->
      <div class="main-content">
        <!-- 左侧联系人列表 -->
        <div class="contact-list">
          <div class="search-contact">
            <input type="text" placeholder="搜索联系人">
            <button class="search-icon">
              <svg viewBox="0 0 24 24" fill="currentColor" width="16" height="16">
                <path d="M15.5 14h-.79l-.28-.27C15.41 12.59 16 11.11 16 9.5 16 5.91 13.09 3 9.5 3S3 5.91 3 9.5 5.91 16 9.5 16c1.61 0 3.09-.59 4.23-1.57l.27.28v.79l5 4.99L20.49 19l-4.99-5zm-6 0C7.01 14 5 11.99 5 9.5S7.01 5 9.5 5 14 7.01 14 9.5 11.99 14 9.5 14z"/>
              </svg>
            </button>
          </div>
          <div class="recent-contacts">
            <div class="contact-item" :class="{ active: selectedContact === contact.id }" v-for="contact in contacts" :key="contact.id" @click="selectContact(contact.id)">
              <div class="contact-avatar">
                <img :src="contact.avatar" alt="Contact Avatar">
                <span v-if="contact.unread > 0" class="unread-badge">{{ contact.unread }}</span>
              </div>
              <div class="contact-info">
                <div class="contact-name">{{ contact.name }}</div>
                <div class="contact-preview">
                  <span v-if="contact.lastMessage">{{ contact.lastMessage.text }}</span>
                  <span v-else>暂无消息</span>
                </div>
              </div>
              <div class="contact-time">{{ contact.lastMessageTime }}</div>
            </div>
          </div>
        </div>
  
        <!-- 右侧聊天窗口 -->
        <div class="chat-window">
          <div class="chat-header">
            <h2 v-if="selectedContactName">{{ selectedContactName }}</h2>
            <div class="chat-actions">
              <button class="chat-action-btn">
                <svg viewBox="0 0 24 24" fill="currentColor" width="16" height="16">
                  <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 15h-2v-2h2v2zm0-4h-2V7h2v6z"/>
                </svg>
              </button>
              <button class="chat-action-btn">
                <svg viewBox="0 0 24 24" fill="currentColor" width="16" height="16">
                  <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 15h-2v-2h2v2zm0-4h-2V7h2v6z"/>
                </svg>
              </button>
            </div>
          </div>
          <div class="message-list" ref="messageList">
            <div v-for="(message, index) in currentMessages" :key="index" class="message-item">
              <div v-if="message.type === 'system'" class="system-message">
                <div class="system-message-content">
                  <div class="message-avatar">
                    <img :src="message.avatar" alt="System">
                  </div>
                  <div class="message-bubble">
                    <div class="message-header">
                      <span class="message-sender">{{ message.sender }}</span>
                      <span class="message-time">{{ message.time }}</span>
                    </div>
                    <div class="message-text">{{ message.text }}</div>
                  </div>
                </div>
              </div>
              <div v-else-if="message.type === 'user'" class="my-message">
                <div class="message-bubble">
                  <div class="message-header">
                    <span class="message-sender">{{ message.sender }}</span>
                    <span class="message-time">{{ message.time }}</span>
                  </div>
                  <div class="message-text">{{ message.text }}</div>
                </div>
                <div class="message-avatar">
                  <img :src="message.avatar" alt="User">
                </div>
              </div>
              <div v-else class="assistant-message">
                <div class="message-avatar">
                  <img :src="message.avatar" alt="Assistant">
                </div>
                <div class="message-bubble">
                  <div class="message-header">
                    <span class="message-sender">{{ message.sender }}</span>
                    <span class="message-time">{{ message.time }}</span>
                  </div>
                  <div class="message-text">{{ message.text }}</div>
                </div>
              </div>
            </div>
          </div>
          <div class="chat-input">
            <div class="input-area">
              <textarea
                v-model="newMessage"
                @keydown.enter.prevent="sendMessage"
                placeholder="输入消息..."
                rows="1"
                ref="messageInput"
              ></textarea>
            </div>
            <div class="input-actions">
              <button class="send-btn" @click="sendMessage">
                <svg viewBox="0 0 24 24" fill="currentColor" width="20" height="20">
                  <path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/>
                </svg>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </template>
  
  <script>
  export default {
    name: 'PrivateMessaging',
    data() {
      return {
        selectedContact: null,
        selectedContactName: '',
        newMessage: '',
        contacts: [
          {
            id: 1,
            name: 'Joyful Mind',
            avatar: 'https://picsum.photos/40/40?random=1',
            unread: 0,
            lastMessage: {
              text: 'https://www.zhihu.com/q...',
              type: 'assistant'
            },
            lastMessageTime: '1 小时前'
          },
          {
            id: 2,
            name: 'AI实验室',
            avatar: 'https://picsum.photos/40/40?random=2',
            unread: 1,
            lastMessage: {
              text: '亲爱的 Saisyc 我们有接单策...',
              type: 'assistant'
            },
            lastMessageTime: '昨天 14:24'
          },
          {
            id: 3,
            name: '段超',
            avatar: 'https://picsum.photos/40/40?random=3',
            unread: 0,
            lastMessage: {
              text: '[耶][耶][耶]',
              type: 'user'
            },
            lastMessageTime: '04-04'
          },
          {
            id: 4,
            name: '史密斯',
            avatar: 'https://picsum.photos/40/40?random=4',
            unread: 0,
            lastMessage: {
              text: 'https://www.zhihu.com/q...',
              type: 'assistant'
            },
            lastMessageTime: '04-03'
          },
          {
            id: 5,
            name: 'Wille Zur Macht',
            avatar: 'https://picsum.photos/40/40?random=5',
            unread: 0,
            lastMessage: {
              text: 'https://www.zhihu.com/q...',
              type: 'assistant'
            },
            lastMessageTime: '04-03'
          },
          {
            id: 6,
            name: 'Nefelibata',
            avatar: 'https://picsum.photos/40/40?random=6',
            unread: 0,
            lastMessage: {
              text: 'https://www.zhihu.com/q...',
              type: 'assistant'
            },
            lastMessageTime: '04-03'
          },
          {
            id: 7,
            name: '专喷民科和公知',
            avatar: 'https://picsum.photos/40/40?random=7',
            unread: 0,
            lastMessage: {
              text: 'https://www.zhihu.com/q...',
              type: 'assistant'
            },
            lastMessageTime: '04-03'
          },
          {
            id: 8,
            name: '知乎知识付费小...',
            avatar: 'https://picsum.photos/40/40?random=8',
            unread: 1,
            lastMessage: {
              text: '亲爱的Saisyc： 注意到你经...',
              type: 'assistant'
            },
            lastMessageTime: '04-02'
          }
        ],
        messages: {
          1: [
            {
              type: 'system',
              sender: '系统',
              avatar: 'https://picsum.photos/40/40?random=9',
              time: '10:30',
              text: '欢迎使用知乎私信！有什么可以帮助您的？'
            },
            {
              type: 'user',
              sender: '我',
              avatar: 'https://picsum.photos/40/40?random=10',
              time: '10:31',
              text: '你好，我想了解一些关于人工智能的知识。'
            },
            {
              type: 'assistant',
              sender: 'Joyful Mind',
              avatar: 'https://picsum.photos/40/40?random=1',
              time: '10:32',
              text: '您好！人工智能（AI）是计算机科学的一个分支，旨在创造能够模拟人类智能的机器。它包括学习、推理和自我修正等能力。您具体想了解哪方面的内容？'
            }
          ],
          2: [
            {
              type: 'assistant',
              sender: 'AI实验室',
              avatar: 'https://picsum.photos/40/40?random=2',
              time: '14:24',
              text: '亲爱的 Saisyc，我们有接单策略和合作方案，您可以随时联系我们了解详情！'
            }
          ],
          3: [
            {
              type: 'user',
              sender: '段超',
              avatar: 'https://picsum.photos/40/40?random=3',
              time: '04-04',
              text: '[耶][耶][耶]'
            }
          ],
          8: [
            {
              type: 'assistant',
              sender: '知乎知识付费小...',
              avatar: 'https://picsum.photos/40/40?random=8',
              time: '04-02',
              text: '亲爱的 Saisyc：注意到您经常浏览知识付费相关内容，我们有专属优惠活动，点击查看详情！'
            }
          ]
        }
      };
    },
    computed: {
      currentMessages() {
        if (this.selectedContact) {
          return this.messages[this.selectedContact] || [];
        }
        return [];
      }
    },
    methods: {
      selectContact(contactId) {
        this.selectedContact = contactId;
        const contact = this.contacts.find(c => c.id === contactId);
        if (contact) {
          this.selectedContactName = contact.name;
          // 重置未读消息
          contact.unread = 0;
        }
        this.scrollToBottom();
      },
      sendMessage() {
        if (this.newMessage.trim() === '' || !this.selectedContact) return;
  
        // 添加用户消息
        this.messages[this.selectedContact] = this.messages[this.selectedContact] || [];
        this.messages[this.selectedContact].push({
          type: 'user',
          sender: '我',
          avatar: 'https://picsum.photos/40/40?random=10',
          time: this.formatTime(),
          text: this.newMessage
        });
  
        // 清空输入框
        this.newMessage = '';
        this.$refs.messageInput.focus();
  
        // 模拟回复
        setTimeout(() => {
          const contact = this.contacts.find(c => c.id === this.selectedContact);
          if (contact) {
            this.messages[this.selectedContact].push({
              type: 'assistant',
              sender: contact.name,
              avatar: contact.avatar,
              time: this.formatTime(),
              text: '感谢您的消息！我正在处理您的请求...'
            });
          }
        }, 1000);
  
        // 滚动到底部
        this.scrollToBottom();
      },
      formatTime() {
        const now = new Date();
        const hours = now.getHours().toString().padStart(2, '0');
        const minutes = now.getMinutes().toString().padStart(2, '0');
        return `${hours}:${minutes}`;
      },
      scrollToBottom() {
        this.$nextTick(() => {
          if (this.$refs.messageList) {
            this.$refs.messageList.scrollTop = this.$refs.messageList.scrollHeight;
          }
        });
      }
    },
    mounted() {
      // 默认选择第一个联系人
      if (this.contacts.length > 0) {
        this.selectContact(this.contacts[0].id);
      }
    }
  };
  </script>
  
  <style scoped>
  .messaging-container {
    display: flex;
    flex-direction: column;
    height: 100vh;
    background: #f8f9fa;
  }
  
  .main-content {
    display: flex;
    flex: 1;
    overflow: hidden;
  }
  
  .contact-list {
    width: 300px;
    background: white;
    border-right: 1px solid #e9ecef;
    padding: 20px;
    overflow-y: auto;
  }
  
  .search-contact {
    display: flex;
    margin-bottom: 20px;
  }
  
  .search-contact input {
    flex: 1;
    padding: 8px 12px;
    border: 1px solid #e9ecef;
    border-radius: 20px 0 0 20px;
    outline: none;
  }
  
  .search-icon {
    background: #f8f9fa;
    border: 1px solid #e9ecef;
    border-left: none;
    border-radius: 0 20px 20px 0;
    padding: 8px 12px;
    cursor: pointer;
  }
  
  .recent-contacts h3 {
    margin-top: 0;
    margin-bottom: 15px;
    color: #666;
    font-size: 14px;
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
  
  .unread-count {
    color: #ff4d4f;
    font-size: 12px;
  }
  
  .arrow {
    font-size: 12px;
    cursor: pointer;
  }
  
  .contact-item {
    display: flex;
    padding: 12px 0;
    border-bottom: 1px solid #f8f9fa;
    cursor: pointer;
    transition: all 0.3s ease;
  }
  
  .contact-item:hover {
    background: #f8f9fa;
  }
  
  .contact-item.active {
    background: #f0f2f5;
  }
  
  .contact-avatar {
    position: relative;
    margin-right: 12px;
  }
  
  .contact-avatar img {
    width: 40px;
    height: 40px;
    border-radius: 50%;
    object-fit: cover;
  }
  
  .unread-badge {
    position: absolute;
    bottom: 0;
    right: 0;
    background: #ff4d4f;
    color: white;
    border-radius: 50%;
    width: 18px;
    height: 18px;
    font-size: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
  }
  
  .contact-info {
    flex: 1;
  }
  
  .contact-name {
    font-weight: 500;
    margin-bottom: 4px;
  }
  
  .contact-preview {
    color: #999;
    font-size: 12px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }
  
  .contact-time {
    color: #999;
    font-size: 12px;
    white-space: nowrap;
  }
  
  .chat-window {
    flex: 1;
    display: flex;
    flex-direction: column;
    background: #f8f9fa;
    overflow: hidden;
  }
  
  .chat-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 15px 20px;
    background: white;
    border-bottom: 1px solid #e9ecef;
  }
  
  .chat-header h2 {
    margin: 0;
    font-size: 16px;
  }
  
  .chat-actions {
    display: flex;
    gap: 10px;
  }
  
  .chat-action-btn {
    background: transparent;
    border: none;
    cursor: pointer;
    color: #666;
  }
  
  .message-list {
    flex: 1;
    overflow-y: auto;
    padding: 20px;
  }
  
  .message-item {
    margin-bottom: 15px;
  }
  
  .message-avatar img {
    width: 40px;
    height: 40px;
    border-radius: 50%;
    object-fit: cover;
  }
  
  .message-bubble {
    background: white;
    border-radius: 12px;
    padding: 12px 16px;
    max-width: 70%;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  }
  
  .message-header {
    display: flex;
    justify-content: space-between;
    margin-bottom: 6px;
    font-size: 12px;
    color: #666;
  }
  
  .message-sender {
    font-weight: 500;
  }
  
  .message-time {
    color: #999;
  }
  
  .message-text {
    line-height: 1.5;
    color: #333;
  }
  
  .my-message {
    display: flex;
    justify-content: flex-end;
    align-items: flex-end;
  }
  
  .my-message .message-bubble {
    background: #e3f2fd;
    color: #333;
    margin-right: 12px;
  }
  
  .my-message .message-avatar {
    margin-left: 12px;
    margin-right: 0;
  }
  
  .assistant-message {
    display: flex;
    align-items: flex-start;
  }
  
  .system-message .message-bubble {
    background: #f1f1f1;
    color: #666;
  }
  
  .chat-input {
    display: flex;
    padding: 15px 20px;
    background: white;
    border-top: 1px solid #e9ecef;
  }
  
  .input-area {
    flex: 1;
  }
  
  textarea {
    width: 100%;
    border: 1px solid #e9ecef;
    border-radius: 20px;
    padding: 12px 16px;
    resize: none;
    outline: none;
    transition: all 0.3s ease;
    font-family: inherit;
    font-size: 14px;
  }
  
  textarea:focus {
    border-color: #0066ff;
    box-shadow: 0 0 0 2px rgba(0, 102, 255, 0.1);
  }
  
  .input-actions {
    display: flex;
    align-items: center;
    margin-left: 10px;
  }
  
  .send-btn {
    background: #0066ff;
    border: none;
    width: 40px;
    height: 40px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
    cursor: pointer;
    transition: all 0.3s ease;
  }
  
  .send-btn:hover {
    background: #0052cc;
  }
  </style>