<script setup lang="ts">
import {onMounted, ref} from 'vue'
import { useRouter } from 'vue-router';
import axios from 'axios'
import { ElMessage } from 'element-plus'

interface agent {
  id: number
  name: string
  description: string
  icon: string
  status: number
  publishedTime: string
  hover?: boolean
}
const agents = ref<agent[]> ([])
const isCreateAgentVisible = ref(false)
const router = useRouter();
const baseImageUrl = "http://122.9.33.84:8000"
const deleteDialog = ref(false);
const deleteTarget = ref<{ id: number, name: string } | null>(null);

// 表单数据
const agentForm = ref({
  name: '',
  description: '',
  icon: ''
})

const formData = new FormData()

function onCreateAgent() {
  isCreateAgentVisible.value = true
}

function offCreateAgent() {
  isCreateAgentVisible.value = false
  agentForm.value = {
    name: '',
    description: '',
    icon: ''
  }
  formData.delete('icon')
}

function handleImageUpload(event: Event) {
  const input = event.target as HTMLInputElement
  if (input.files && input.files[0]) {
    const file = input.files[0]
    // 验证文件大小和类型
    if (file.size > 2 * 1024 * 1024) {
      ElMessage.error('图片大小不能超过2MB')
      return
    }
    const reader = new FileReader()
    reader.onload = (e) => {
      agentForm.value.icon = e.target?.result as string
    }
    formData.append('icon', input.files[0])
    reader.readAsDataURL(file)
  }
}

async function fetchAgents() {
  try {
    const response = await axios({
      method: 'get',
      url: 'agent/fetchAll',
      params: {
        uid: sessionStorage.getItem('uid')
      }
    })
    if (response.data.code === 0) {
      agents.value = response.data.agents
      console.log(agents.value)
    } else {
      console.log('获取智能体失败：', response.data.message)
    }
  } catch (error) {
    console.error('获取智能体异常：', error)
  }
}

// 创建智能体
async function createAgent() {
  const formData = new FormData()
  if (!agentForm.value.name) {
    ElMessage.error('请输入智能体名称')
    return
  }
  formData.append('name', agentForm.value.name)
  formData.append('description', agentForm.value.description)
  formData.append('uid', sessionStorage.getItem('uid') as string)
  try {
    const response = await axios({
      method: 'post',
      url: '/agent/create',
      data: formData,
      headers: {
        'Content-Type': 'multipart/form-data',
      }
    })
    if (response.data.code === 0) {
      ElMessage.success('创建成功！')
      offCreateAgent()
      await goToAgentEdit(response.data.agent_id)
    } else {
      ElMessage.error(response.data.message)
    }
  } catch (error) {
    console.error('创建智能体失败:', error)
    ElMessage.error('创建失败')
  }
}

// 打开删除确认弹窗
function tryDelete(id: number) {
  deleteTarget.value = { id, name: agents.value.find(agent => agent.id === id)?.name || '' };
  deleteDialog.value = true;
}

// 确认删除智能体
function handleDelete() {
  if (!deleteTarget.value) return;

  axios({
    method: "post",
    url: "/agent/delete",
    data: {
      uid: sessionStorage.getItem("uid"),
      agent_id: deleteTarget.value.id,
    },
  }).then(function (response) {
    if (response.data.code === 0) {
      ElMessage.success("删除成功！")
      agents.value = agents.value.filter(agent => agent.id !== deleteTarget.value?.id)
      deleteDialog.value = false
      deleteTarget.value = null
    } else {
      ElMessage.error(response.data.message)
      deleteDialog.value = false
      deleteTarget.value = null
    }
  })
}

onMounted(() => {
  fetchAgents()
})

function goToAgentEdit(id: number) {
  router.push({
    path: `/agentEdit/${id}`,
    query: {
      uid: Number(sessionStorage.getItem('uid')),
    }
  })
}
</script>

<template>
  <div class="content">
    <!-- 顶部标题栏 -->
    <div class="header">
      <h1>智能体开发</h1>
      <button class="create-btn" @click="onCreateAgent">
        <svg viewBox="0 0 24 24" fill="currentColor" width="20" height="20">
          <path d="M19 13h-6v6h-2v-6H5v-2h6V5h2v6h6v2z"/>
        </svg>
        创建智能体
      </button>
    </div>

    <!-- 筛选栏 -->
    <div class="filter-bar">
      <select class="filter-select">
        <option value="create-time">按创建时间排序</option>
        <option value="name">按名称排序</option>
        <option value="modify-time">按修改时间排序</option>
      </select>
      <select class="filter-select">
        <option value="all">默认</option>
        <option value="published">已发布</option>
        <option value="unpublished">未发布</option>
      </select>
      <div class="search-box">
        <svg viewBox="0 0 24 24" fill="currentColor" width="16" height="16">
          <path d="M15.5 14h-.79l-.28-.27C15.41 12.59 16 11.11 16 9.5 16 5.91 13.09 3 9.5 3S3 5.91 3 9.5 5.91 16 9.5 16c1.61 0 3.09-.59 4.23-1.57l.27.28v.79l5 4.99L20.49 19l-4.99-5zm-6 0C7.01 14 5 11.99 5 9.5S7.01 5 9.5 5 14 7.01 14 9.5 11.99 14 9.5 14z"/>
        </svg>
        <input type="text" placeholder="搜索智能体...">
      </div>
    </div>

    <!-- 智能体列表 -->
    <div class="agent-list">
      <div
        v-for="agent in agents"
        :key="agent.id"
        class="agent-card"
        @mouseover="agent.hover = true"
        @mouseleave="agent.hover = false"
        @click="goToAgentEdit(agent.id)"
      >
        <div class="agent-image">
          <img :src="baseImageUrl + agent.icon" :alt="agent.name" />
          <div class="agent-status" :class="agent.status">
            {{ 
              agent.status === 0 ? '未发布' :
              agent.status === 1 ? '审核中' :
              '已发布' 
            }}
          </div>
        </div>
        <div class="agent-info">
          <h3>{{ agent.name }}</h3>
          <p>{{ agent.description }}</p>
<!--          <div class="agent-meta">-->
<!--            <span v-if="agent.status === 2">发布时间：{{ agent.publishedTime }}</span>-->
<!--          </div>-->
        </div>
        <!-- 删除图标 -->
        <div
          v-if="agent.hover"
          class="delete-icon"
          @click.stop="tryDelete(agent.id)"
        >
          <svg viewBox="0 0 24 24" fill="currentColor" width="20" height="20">
            <path d="M16 9v10H8V9h8m-1.5-6h-5l-1 1H5v2h14V4h-3.5l-1-1M18 7H6v12c0 1.1.9 2 2 2h8c1.1 0 2-.9 2-2V7z"/>
          </svg>
        </div>
      </div>
    </div>

    <!-- 创建智能体的弹窗 -->
    <el-dialog v-model="isCreateAgentVisible" title="创建智能体" width="500px" class="custom-dialog">
      <div class="dialog-body">
        <!-- 名称 -->
        <div class="form-row">
          <label class="form-label">名称 <span class="required">*</span></label>
          <el-input v-model="agentForm.name" placeholder="给智能体起一个独一无二的名字" maxlength="20" class="form-input" />
          <span class="char-count">{{ agentForm.name.length }}/20</span>
        </div>

        <!-- 描述 -->
        <div class="form-row">
          <label class="form-label">功能介绍</label>
          <el-input
            v-model="agentForm.description"
            type="textarea"
            placeholder="介绍智能体的功能，将会展示给智能体的用户"
            maxlength="500"
            :rows="4"
            class="form-input"
          />
          <span class="char-count">{{ agentForm.description.length }}/500</span>
        </div>

        <!-- 图片上传 -->
        <div class="form-row">
          <label class="form-label">图标</label>
          <div class="image-upload">
            <div class="upload-preview" v-if="agentForm.icon">
              <img :src="agentForm.icon" alt="预览图" />
            </div>
            <div class="upload-button" :class="{ 'has-image': agentForm.icon }">
              <input type="file" accept="image/*" @change="handleImageUpload" class="file-input" />
              <svg viewBox="0 0 24 24" fill="currentColor" width="24" height="24">
                <path d="M19 7v2.99s-1.99.01-2 0V7h-3s.01-1.99 0-2h3V2h2v3h3v2h-3zm-3 4V8h-3V5H5c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2v-8h-3zM5 19l3-4 2 3 3-4 4 5H5z"/>
              </svg>
              <span>{{ agentForm.icon ? '更换图片' : '上传图片' }}</span>
            </div>
          </div>
        </div>
      </div>

      <template #footer>
        <el-button @click="offCreateAgent">取消</el-button>
        <el-button type="primary" @click="createAgent">创建</el-button>
      </template>
    </el-dialog>

    <!-- 删除确认弹窗 -->
    <el-dialog v-model="deleteDialog" title="确认删除" width="400px" class="custom-dialog">
      <div class="dialog-body">
        <p>确定要删除"{{ deleteTarget?.name }}"吗？此操作不可撤销。</p>
      </div>
      <template #footer>
        <el-button @click="deleteDialog = false">取消</el-button>
        <el-button type="danger" @click="handleDelete">删除</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
.content {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.header h1 {
  margin: 0;
  color: #2c3e50;
  font-size: 24px;
}

.create-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background: #2c3e50;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.create-btn:hover {
  background: #34495e;
}

.filter-bar {
  display: flex;
  gap: 16px;
  margin-bottom: 20px;
  align-items: center;
}

.filter-select {
  padding: 8px 12px;
  border: 1px solid #e9ecef;
  border-radius: 6px;
  background: white;
  color: #2c3e50;
  cursor: pointer;
}

.search-box {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  background: white;
  border: 1px solid #e9ecef;
  border-radius: 6px;
  flex: 1;
  max-width: 300px;
}

.search-box input {
  border: none;
  outline: none;
  width: 100%;
  color: #2c3e50;
}

.agent-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
}

.agent-card {
  background: white;
  border-radius: 12px;
  padding: 16px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  transition: all 0.3s ease;
  display: flex;
  gap: 16px;
  cursor: pointer;
  position: relative;
}

.agent-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0,0,0,0.1);
}

.agent-image {
  position: relative;
  width: 80px;
  height: 80px;
  flex-shrink: 0;
}

.agent-image img {
  width: 100%;
  height: 100%;
  border-radius: 50%;
  object-fit: cover;
}

.agent-info {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
}

.agent-info h3 {
  margin: 0 0 8px 0;
  color: #2c3e50;
  font-size: 16px;
}

.agent-info p {
  margin: 0;
  color: #666;
  font-size: 13px;
  line-height: 1.5;
  display: -webkit-box;
  -webkit-box-orient: vertical;
  overflow: hidden;
  flex: 1;
}

.agent-meta {
  display: flex;
  justify-content: flex-end;
  margin-top: 8px;
}

.delete-icon {
  position: absolute;
  bottom: 8px;
  right: 8px;
  background: white;
  border-radius: 50%;
  padding: 4px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  cursor: pointer;
  transition: all 0.3s ease;
}

.delete-icon:hover {
  background: #f5f5f5;
}

.agent-status {
  position: absolute;
  bottom: 0;
  right: 0;
  background: #2c3e50;
  color: white;
  padding: 2px 6px;
  border-radius: 10px;
  font-size: 10px;
}

.agent-status.private {
  background: #95a5a6;
}

.agent-status.check {
  background: #f1c40f;
}

.agent-status.published {
  background: #2ecc71;
}

/* 自定义弹窗样式 */
.custom-dialog {
  border-radius: 12px;
  overflow: hidden;
}

.custom-dialog .el-dialog__header {
  background-color: #f5f7fa;
  border-bottom: 1px solid #ebeef5;
  font-size: 18px;
  font-weight: bold;
  color: #2c3e50;
}

.dialog-body {
  padding: 20px 24px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.form-row {
  display: flex;
  flex-direction: column;
}

.form-label {
  margin-bottom: 8px;
  font-size: 14px;
  color: #606266;
}

.required {
  color: red;
}

.form-input {
  width: 100%;
  border-radius: 6px;
}

.char-count {
  text-align: right;
  margin-top: 4px;
  font-size: 12px;
  color: #95a5a6;
}

.image-upload {
  display: flex;
  align-items: center;
  gap: 16px;
}

.upload-preview {
  width: 100px;
  height: 100px;
  border-radius: 8px;
  overflow: hidden;
  border: 1px solid #e9ecef;
}

.upload-preview img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.upload-button {
  position: relative;
  width: 120px;
  height: 100px;
  border: 2px dashed #e9ecef;
  border-radius: 8px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.upload-button:hover {
  border-color: #3498db;
  color: #3498db;
}

.upload-button.has-image {
  width: 100px;
}

.file-input {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  opacity: 0;
  cursor: pointer;
}

.upload-button svg {
  color: #95a5a6;
}

.upload-button:hover svg {
  color: #3498db;
}

.upload-button span {
  font-size: 12px;
  color: #95a5a6;
}

.upload-button:hover span {
  color: #3498db;
}
</style>