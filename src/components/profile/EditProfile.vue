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
          <img :src="formData.avatar" alt="用户头像" class="current-avatar">
          <div class="upload-controls">
            <button class="upload-btn" @click="triggerFileInput">更换头像</button>
            <input 
              type="file" 
              ref="fileInput" 
              style="display: none" 
              accept="image/*"
              @change="handleAvatarChange"
            >
            <p class="upload-hint">支持 JPG、PNG 格式，文件小于 2MB</p>
          </div>
        </div>
      </div>
      
      <div class="form-section">
        <label for="name">昵称</label>
        <input 
          type="text" 
          id="name" 
          v-model="formData.name" 
          class="form-input"
          placeholder="请输入昵称"
        >
      </div>
      
      <div class="form-section">
        <label for="password">密码</label>
        <input 
          type="password" 
          id="password" 
          v-model="formData.password" 
          class="form-input"
          placeholder="设置新密码（不修改请留空）"
        >
      </div>
      
      <div class="form-section">
        <label for="confirmPassword">确认密码</label>
        <input 
          type="password" 
          id="confirmPassword" 
          v-model="formData.confirmPassword" 
          class="form-input"
          placeholder="确认新密码"
          :disabled="!formData.password"
        >
        <p class="error-message" v-if="passwordError">{{ passwordError }}</p>
      </div>
      
      <div class="form-section">
        <label for="description">个人描述</label>
        <textarea 
          id="description" 
          v-model="formData.description" 
          class="form-textarea"
          placeholder="介绍一下自己吧"
          rows="4"
        ></textarea>
      </div>
      
      <div class="form-actions">
        <button class="cancel-btn" @click="goBack">取消</button>
        <button class="save-btn" @click="saveProfile" :disabled="!isFormValid">保存</button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useRoute } from 'vue-router';
import axios from "axios";

const router = useRouter();
const route = useRoute();
const fileInput = ref<HTMLInputElement | null>(null);

// 表单数据
const formData = reactive({
  avatar: '',
  name: '',
  password: '',
  confirmPassword: '',
  description: '',
  uid: null as number
});

// 密码验证错误信息
const passwordError = computed(() => {
  if (formData.password && formData.confirmPassword && 
      formData.password !== formData.confirmPassword) {
    return '两次输入的密码不一致';
  }
  return '';
});

// 表单验证
const isFormValid = computed(() => {
  if (!formData.name) return false;
  if (formData.password && !formData.confirmPassword) return false;
  if (passwordError.value) return false;
  return true;
});

onMounted(() => {
  formData.name = route.query.name as string || '';
  formData.avatar = route.query.avatar as string || '';
  formData.description = route.query.description as string || '';
  formData.uid = route.query.uid as number || null as number;
});

// 触发文件选择
function triggerFileInput() {
  fileInput.value?.click();
}

// 处理头像更改
function handleAvatarChange(event: Event) {
  const input = event.target as HTMLInputElement;
  if (input.files && input.files[0]) {
    const file = input.files[0];
    
    // 验证文件大小和类型
    if (file.size > 2 * 1024 * 1024) {
      alert('图片大小不能超过2MB');
      return;
    }
    
    const reader = new FileReader();
    reader.onload = (e) => {
      formData.avatar = e.target?.result as string;
    };
    reader.readAsDataURL(file);
  }
}

// 返回个人资料页面
function goBack() {
  router.push('/profile');
}

// 保存个人资料
function saveProfile() {
  if (!isFormValid.value) return;
  console.log("avatar: ", formData.avatar)
  axios({
    method: 'post',
    url: '/user/updateProfile',
    data: {
      uid: formData.uid,
      name: formData.name,
      avatar: formData.avatar,
      description: formData.description,
      password: formData.password
    }
  }).then(function (response) {
    if (response.data.code === 0) {
      alert('个人资料已更新');
      router.push('/profile');
    } else {
      alert('更新失败，请稍后重试');
    }
  }).catch(function (error) {
    console.error('请求失败:', error);
    alert('更新失败，请稍后重试');
  });
}
</script>

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
  border: none;
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
</style> 