<script setup lang="ts">
import { ref, computed, onMounted, inject, type Ref } from 'vue'
import axios from "axios"
import router from '@/router'
import { useRoute }from 'vue-router'
import { ElMessage } from 'element-plus'
import type { UploadProps } from 'element-plus'

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


function uploadAvatar() {
  const uid = localStorage.getItem('LingXi_uid') || ''
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
      refreshAvatar('http://101.201.208.165' + response.data.avatar + '?' + Date.now())
      newAvatar.value = ''
      ElMessage.success(response.data.message)
    } else {
      ElMessage.error(response.data.message)
    }
  })
}

// 处理头像更改
const handleAvatarChange: UploadProps['onChange'] = (uploadFile) => {
  const file = uploadFile.raw
  if (!file) return
  
  // 验证文件大小和类型
  if (file.size > 5 * 1024 * 1024) {
    ElMessage.warning('图片大小不能超过5MB')
    return
  }
  
  const reader = new FileReader()
  reader.onload = (e) => {
    newAvatar.value = e.target?.result as string
  }
  formData.delete('avatar') // 清除之前的文件
  formData.append('avatar', file)
  reader.readAsDataURL(file)
}

function updateBasicInfo() {
  console.log(localStorage.getItem('LingXi_uid'))
  axios({
    method: 'post',
    url: 'user/updateBasicInfo',
    data: {
      uid: localStorage.getItem('LingXi_uid'),
      name: name.value,
      description: description.value
    }
  }).then(function (response) {
    if (response.data.code === 0) {
      ElMessage.success(response.data.message)
    } else {
      ElMessage.error(response.data.message)
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
      uid: localStorage.getItem('LingXi_uid'),
      oldPwd: oldPwd.value,
      newPwd: newPwd.value
    }
  }).then(function (response) {
    if (response.data.code === 0) {
      ElMessage.success(response.data.message)
      oldPwd.value = ''
      newPwd.value = ''
      confirmPwd.value = ''
      dialogVisible.value = false
    } else {
      ElMessage.error(response.data.message)
    }
  })
}

// 返回个人资料页面
function goBack() {
  router.push(`/profile/${localStorage.getItem('LingXi_uid')}`);
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
            <el-upload
              class="avatar-uploader"
              :show-file-list="false"
              :auto-upload="false"
              accept="image/*"
              @change="handleAvatarChange"
            >
              <el-button class="upload-btn select">选择头像</el-button>
            </el-upload>
            <el-button 
              class="upload-btn upload" 
              @click="uploadAvatar" 
              :disabled="!newAvatar"
            >上传头像</el-button>
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
          <el-input class="input" v-model="oldPwd" type="password" placeholder="原密码（初始密码为123456）" maxlength="25"/>
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
  background: white;
  padding: 24px;
  border-radius: 16px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  border: 1px solid rgba(79, 175, 255, 0.1);
}

.edit-header h2 {
  font-size: 28px;
  font-weight: 600;
  color: #2c3e50;
  margin: 0;
  position: relative;
}

.edit-header h2::after {
  content: '';
  position: absolute;
  bottom: -6px;
  left: 0;
  width: 100%;
  height: 3px;
  background: #4FAFFF;
  border-radius: 2px;
}

.back-button {
  display: flex;
  align-items: center;
  color: #4FAFFF;
  cursor: pointer;
  transition: all 0.3s ease;
  padding: 10px 20px;
  border-radius: 12px;
  background: rgba(79, 175, 255, 0.1);
}

.back-button:hover {
  transform: translateY(-2px);
  background: rgba(79, 175, 255, 0.2);
}

.back-button svg {
  margin-right: 8px;
}

.edit-form {
  background: white;
  border-radius: 16px;
  padding: 32px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  border: 1px solid rgba(79, 175, 255, 0.1);
}

.form-section {
  margin-bottom: 32px;
}

.form-section label {
  display: block;
  font-weight: 600;
  margin-bottom: 12px;
  color: #2c3e50;
  font-size: 16px;
}

.form-input, .form-textarea {
  width: 80%;
  padding: 12px 16px;
  border: 2px solid #e2e8f0;
  border-radius: 12px;
  font-size: 15px;
  transition: all 0.3s ease;
  color: #2c3e50;
  background: #f8fafc;
}

.form-input:focus, .form-textarea:focus {
  border-color: #4FAFFF;
  outline: none;
  box-shadow: 0 0 0 3px rgba(79, 175, 255, 0.2);
  background: white;
}

.form-textarea {
  resize: vertical;
  min-height: 120px;
}

.avatar-section {
  margin-bottom: 40px;
  padding-bottom: 32px;
  border-bottom: 1px solid #e2e8f0;
}

.avatar-upload {
  display: flex;
  align-items: flex-start;
  gap: 32px;
}

.current-avatar {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  object-fit: cover;
  border: 4px solid white;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
}

.current-avatar:hover {
  transform: scale(1.05);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.15);
}

.upload-controls {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding-top: 8px;
  width: 200px;
}

.avatar-uploader {
  display: inline-block;
}

.upload-btn {
  width: 200px !important;
  text-align: center !important;
  justify-content: center !important;
  display: flex !important;
  align-items: center !important;
  padding: 12px 24px !important;
  border-radius: 12px !important;
  font-weight: 500 !important;
  transition: all 0.3s ease !important;
}

.upload-btn.select {
  background: #ffffff !important;
  color: #4FAFFF !important;
  border: 2px solid #4FAFFF !important;
}

.upload-btn.upload {
  background: #4FAFFF !important;
  color: white !important;
  border: none !important;
}

.upload-btn:hover {
  transform: translateY(-2px) !important;
  box-shadow: 0 4px 12px rgba(79, 175, 255, 0.25) !important;
}

.upload-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

.upload-hint {
  font-size: 13px;
  color: #94a3b8;
  margin-top: 4px;
  line-height: 1.5;
  flex-basis: 100%;
}

.error-message {
  color: #e74c3c;
  font-size: 14px;
  margin-top: 8px;
  padding: 8px 12px;
  background: rgba(231, 76, 60, 0.1);
  border-radius: 8px;
  border-left: 4px solid #e74c3c;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 16px;
  margin-top: 32px;
  padding-top: 24px;
  border-top: 1px solid #e2e8f0;
}

.el-button {
  padding: 12px 28px;
  border-radius: 12px;
  font-size: 15px;
  font-weight: 500;
  transition: all 0.3s ease;
}

.el-button:hover {
  transform: translateY(-2px);
}

.el-button--primary {
  background: linear-gradient(135deg, #4FAFFF 0%, #2b95ff 100%);
  border: none;
  box-shadow: 0 2px 8px rgba(79, 175, 255, 0.25);
}

.el-button--primary:hover {
  box-shadow: 0 4px 12px rgba(79, 175, 255, 0.35);
}

.row {
  min-height: 15px;
  width: 100%;
  margin: 16px auto;
}

.input {
  width: 100%;
  margin-bottom: 16px;
}

.el-dialog {
  border-radius: 16px;
  overflow: hidden;
}

.el-dialog__header {
  background: #f8fafc;
  padding: 20px 24px;
  margin: 0;
}

.el-dialog__title {
  font-size: 20px;
  font-weight: 600;
  color: #2c3e50;
}

.el-dialog__body {
  padding: 24px;
}

.el-dialog__footer {
  padding: 16px 24px;
  background: #f8fafc;
  border-top: 1px solid #e2e8f0;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
}

.el-input__inner {
  border-radius: 12px;
  padding: 12px 16px;
  border: 2px solid #e2e8f0;
  transition: all 0.3s ease;
}

.el-input__inner:focus {
  border-color: #4FAFFF;
  box-shadow: 0 0 0 3px rgba(79, 175, 255, 0.2);
}
</style>