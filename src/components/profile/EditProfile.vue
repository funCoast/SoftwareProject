<script setup lang="ts">
import { ref, computed, onMounted, inject, type Ref } from 'vue'
import axios from "axios"
import router from '../../router'
import { useRoute }from 'vue-router'

const avatar = inject('avatar') as Ref
const refreshAvatar = inject('refreshAvatar') as Function
const newAvatar = ref('')

const showAvatar = computed(() => {
  if (newAvatar.value === '') {
    return avatar.value
  } else {
    return newAvatar.value
  }
})

const route = useRoute()
const fileInput = ref<HTMLInputElement | null>(null);

// 表单数据
const name = ref('')
const description = ref('')
const formData = new FormData()

const dialogVisible = ref(false)
const oldPwd = ref('')
const newPwd = ref('')
const confirmPwd = ref('')

onMounted(() => {
  name.value = route.query.name as string || ''
  description.value = route.query.description as string || ''
});

// 密码验证错误信息
const passwordError = computed(() => {
  if (newPwd.value && confirmPwd.value && newPwd.value !== confirmPwd.value) {
    return '两次输入的密码不一致'
  }
  return null
});

const pwdCheck = computed(() => {
  return !(newPwd.value && confirmPwd.value && newPwd.value === confirmPwd.value)
})

// 触发文件选择
function triggerFileInput() {
  fileInput.value?.click()
}

function uploadAvatar() {
  const uid = sessionStorage.getItem('uid') || ''
  formData.append('uid', uid)
  axios({
    method: 'post',
    url: '/user/updateAvatar',
    data: formData,
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  }).then(function (response) {
    if (response.data.code === 0) {
      refreshAvatar('http://122.9.33.84:8000' + response.data.avatar + '?' + Date.now())
      newAvatar.value = ''
      alert(response.data.message)
    } else {
      alert(response.data.message)
    }
  })
}

// 处理头像更改
function handleAvatarChange(event: Event) {
  const input = event.target as HTMLInputElement
  if (input.files && input.files[0]) {
    const file = input.files[0]
    
    // 验证文件大小和类型
    if (file.size > 2 * 1024 * 1024) {
      alert('图片大小不能超过2MB')
      return;
    }
    
    const reader = new FileReader()
    reader.onload = (e) => {
      newAvatar.value = e.target?.result as string
    }
    formData.append('avatar', input.files[0])
    reader.readAsDataURL(file)
  }
}

function updateBasicInfo() {
  console.log(sessionStorage.getItem('uid'))
  axios({
    method: 'post',
    url: 'user/updateProfile',
    data: {
      uid: sessionStorage.getItem('uid'),
      name: name.value,
      description: description.value
    }
  }).then(function (response) {
    if (response.data.code === 0) {
      alert(response.data.message)
    } else {
      alert(response.data.message)
    }
  })
}

function editPassword() {
  dialogVisible.value = true
}

function updatePwd() {
  axios({
    method: 'post',
    url: 'user/updatePassword',
    data: {
      uid: sessionStorage.getItem('uid'),
      oldPwd: oldPwd.value,
      newPwd: newPwd.value
    }
  }).then(function (response) {
    if (response.data.code === 0) {
      alert('修改成功')
      dialogVisible.value = false
    } else {
      alert(response.data.message)
    }
  })
}

// 返回个人资料页面
function goBack() {
  router.push(`/profile/${sessionStorage.getItem('uid')}`);
}
  
</script>

<template>
  <div class="edit-profile-container">
    <div class="edit-header">
      <h2>编辑个人资料</h2>
      <div class="back-button" @click="goBack">
        <svg viewBox="0 0 24 24" fill="currentColor" width="24" height="24">
          <path d="M20 11H7.83l5.59-5.59L12 4l-8 8 8 8 1.41-1.41L7.83 13H20v-2z"/>
        </svg>
        <span>返回</span>
      </div>
    </div>
    
    <div class="edit-form">
      <div class="form-section avatar-section">
        <label>头像</label>
        <div class="avatar-upload">
          <img :src="showAvatar" alt="用户头像" class="current-avatar">
          <div class="upload-controls">
            <el-button class="upload-btn" @click="triggerFileInput">选择头像</el-button>
            <el-button :v-if="fileInput?.value!=null" type="primary" @click="uploadAvatar" :disabled="!newAvatar">上传头像</el-button>
            <input type="file" ref="fileInput" style="display: none" accept="image/*" @change="handleAvatarChange"></input>
            <p class="upload-hint">支持 JPG、PNG 格式，文件小于 2MB</p>
          </div>
        </div>
      </div>
      
      <div class="form-section">
        <label for="name">昵称</label>
        <input 
          type="text" 
          id="name" 
          v-model="name" 
          class="form-input"
          placeholder="请输入昵称"
        >
      </div>
      
      <div class="form-section">
        <label for="description">个人描述</label>
        <textarea 
          id="description" 
          v-model="description" 
          class="form-textarea"
          placeholder="介绍一下自己吧"
          rows="4"
        ></textarea>
      </div>

      <div class="form-actions">
        <el-button type="primary" @click="updateBasicInfo">保存</el-button>
        <el-button style="background-color: #2c3e50; color: white;" @click="editPassword">修改密码</el-button>
      </div>

      <el-dialog v-model="dialogVisible" title="修改密码" width="500">
        <el-row class="row"> 
          <el-input class="input" v-model="oldPwd" type="password" placeholder="原密码（初次设置请留空）" maxlength="25"/>
        </el-row>  
        <el-row class="row">
          <el-input class="input" v-model="newPwd" type="password" placeholder="新密码" maxlength="25"/>
        </el-row>
        <el-row class="row">
          <el-input class="input" v-model="confirmPwd" type="password" placeholder="确认新密码" maxlength="25"/>
        </el-row>
        <p class="error-message" v-if="passwordError">{{ passwordError }}</p>
        <template #footer>
          <div class="dialog-footer">
            <el-button type="primary" @click="updatePwd" :disabled="pwdCheck">修改</el-button>
          </div>
        </template>
      </el-dialog>
  
    </div>
  </div>
</template>

<style scoped>
.edit-profile-container {
  max-width: 800px;
  margin: 0 auto;
  padding: 30px;
  background: #f8f9fa;
  min-height: 100vh;
}

.edit-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
}

.edit-header h2 {
  font-size: 24px;
  font-weight: bold;
  color: #2c3e50;
  margin: 0;
}

.back-button {
  display: flex;
  align-items: center;
  color: #2c3e50;
  cursor: pointer;
  transition: all 0.3s ease;
}

.back-button:hover {
  opacity: 0.8;
}

.back-button svg {
  margin-right: 5px;
}

.edit-form {
  background: white;
  border-radius: 8px;
  padding: 30px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.form-section {
  margin-bottom: 24px;
}

.form-section label {
  display: block;
  font-weight: bold;
  margin-bottom: 8px;
  color: #2c3e50;
}

.form-input, .form-textarea {
  width: 100%;
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 16px;
  transition: all 0.3s ease;
}

.form-input:focus, .form-textarea:focus {
  border-color: #2c3e50;
  outline: none;
  box-shadow: 0 0 0 2px rgba(44, 62, 80, 0.2);
}

.form-textarea {
  resize: vertical;
}

.avatar-section {
  margin-bottom: 30px;
}

.avatar-upload {
  display: flex;
  align-items: center;
  gap: 20px;
}

.current-avatar {
  width: 100px;
  height: 100px;
  border-radius: 50%;
  object-fit: cover;
}

.upload-controls {
  flex: 1;
}

.upload-btn {
  background: #2c3e50;
  color: white;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.upload-btn:hover {
  background: #1e2b38;
}

.upload-hint {
  font-size: 12px;
  color: #666;
  margin-top: 8px;
}

.error-message {
  color: #e74c3c;
  font-size: 14px;
  margin-top: 5px;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 20px;
}

.cancel-btn, .save-btn {
  padding: 10px 20px;
  border-radius: 4px;
  font-size: 16px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.cancel-btn {
  background: #f8f9fa;
  border: 1px solid #ddd;
  color: #2c3e50;
}

.cancel-btn:hover {
  background: #e9ecef;
}

.save-btn {
  background: #2c3e50;
  border: none;
  color: white;
}

.save-btn:hover:not(:disabled) {
  background: #1e2b38;
}

.save-btn:disabled {
  background: #a0aec0;
  cursor: not-allowed;
}

.row {
  min-height: 15px;
  width: 300px; 
  margin: 10px, auto;
}

.input {
  width: 300px;
  margin-left: auto;
  margin-right: auto;
  margin-bottom: 10px;
}
</style> 