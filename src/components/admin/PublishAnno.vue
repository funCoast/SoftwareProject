<script setup lang="ts">
import axios from 'axios'
import { ref, onMounted, computed } from 'vue'
import { ElMessage } from 'element-plus'
import moment from 'moment'

// 公告相关
const announcements = ref<{
  id: number
  title: string
  content: string
  time: Date
}[]>([])

const searchQuery = ref('')

const filteredAnnouncements = computed(() => {
  if (!searchQuery.value) return announcements.value
  const query = searchQuery.value.toLowerCase()
  return announcements.value.filter(anno => 
    anno.title.toLowerCase().includes(query) ||
    anno.content.toLowerCase().includes(query)
  )
})

const newAnnouncement = ref({
  title: '',
  content: ''
})

const editDialogVisible = ref(false)
const currentEditAnnouncement = ref({
  id: 0,
  title: '',
  content: ''
})

// 获取公告列表
async function fetchAnnouncements() {
  try {
    const response = await axios({
      method: 'get',
      url: 'anno/get',
      params: {
        uid: localStorage.getItem('LingXi_uid')
      }
    })
    if (response.data.code === 0) {
      announcements.value = response.data.announcements.sort((a, b) => {
        return new Date(b.time).getTime() - new Date(a.time).getTime()
      })
    } else {
      ElMessage.error('获取公告失败：' + response.data.message)
    }
  } catch (error) {
    console.error('获取公告失败:', error)
    ElMessage.error('获取公告失败')
  }
}

// 发布公告
async function publishAnnouncement() {
  if (!newAnnouncement.value.title.trim() || !newAnnouncement.value.content.trim()) {
    ElMessage.warning('请填写完整的公告信息')
    return
  }

  try {
    const response = await axios({
      method: 'post',
      url: 'anno/add',
      data: {
        uid: localStorage.getItem('LingXi_uid'),
        title: newAnnouncement.value.title,
        content: newAnnouncement.value.content
      }
    })
    if (response.data.code === 0) {
      ElMessage.success('公告发布成功')
      newAnnouncement.value = { title: '', content: '' }
      await fetchAnnouncements()
    } else {
      ElMessage.error('公告发布失败：' + response.data.message)
    }
  } catch (error) {
    console.error('公告发布失败:', error)
    ElMessage.error('公告发布失败')
  }
}

// 打开编辑对话框
function openEditDialog(announcement: any) {
  currentEditAnnouncement.value = {
    id: announcement.id,
    title: announcement.title,
    content: announcement.content
  }
  editDialogVisible.value = true
}

// 更新公告
async function updateAnnouncement() {
  if (!currentEditAnnouncement.value.title.trim() || !currentEditAnnouncement.value.content.trim()) {
    ElMessage.warning('请填写完整的公告信息')
    return
  }

  try {
    const response = await axios({
      method: 'put',
      url: 'anno/update',
      data: {
        id: currentEditAnnouncement.value.id,
        title: currentEditAnnouncement.value.title,
        content: currentEditAnnouncement.value.content
      }
    })
    if (response.data.code === 0) {
      ElMessage.success('公告更新成功')
      editDialogVisible.value = false
      await fetchAnnouncements()
    } else {
      ElMessage.error('公告更新失败：' + response.data.message)
    }
  } catch (error) {
    console.error('公告更新失败:', error)
    ElMessage.error('公告更新失败')
  }
}

// 删除公告
async function deleteAnnouncement(id: number) {
  try {
    const response = await axios({
      method: 'delete',
      url: 'anno/delete',
      data: {
        id: id
      }
    })
    if (response.data.code === 0) {
      ElMessage.success('公告删除成功')
      await fetchAnnouncements()
    } else {
      ElMessage.error('公告删除失败：' + response.data.message)
    }
  } catch (error) {
    console.error('公告删除失败:', error)
    ElMessage.error('公告删除失败')
  }
}

onMounted(() => {
  fetchAnnouncements()
})
</script>

<template>
  <div class="publish-anno">
    <div class="section-header">
      <h2>公告管理</h2>
      <div class="header-actions">
        <el-input
          v-model="searchQuery"
          placeholder="搜索公告..."
          prefix-icon="Search"
          class="search-input"
        />
        <el-button type="primary">
          <img src="https://api.iconify.design/material-symbols:refresh.svg" class="action-icon" />
          刷新
        </el-button>
      </div>
    </div>

    <div class="stats-cards">
      <div class="stat-card">
        <div class="stat-icon">
          <img src="https://api.iconify.design/material-symbols:campaign.svg" alt="total" />
        </div>
        <div class="stat-info">
          <h3>总公告数</h3>
          <p>{{ announcements.length }}</p>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon success">
          <img src="https://api.iconify.design/material-symbols:today.svg" alt="today" />
        </div>
        <div class="stat-info">
          <h3>今日发布</h3>
          <p>{{ announcements.filter(a => moment(a.time).isSame(moment(), 'day')).length }}</p>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon warning">
          <img src="https://api.iconify.design/material-symbols:history.svg" alt="week" />
        </div>
        <div class="stat-info">
          <h3>本周发布</h3>
          <p>{{ announcements.filter(a => moment(a.time).isSame(moment(), 'week')).length }}</p>
        </div>
      </div>
    </div>

    <div class="content-grid">
      <!-- 公告发布表单 -->
      <div class="publish-card">
        <div class="card-header">
          <h3>发布新公告</h3>
          <img src="https://api.iconify.design/material-symbols:edit-note.svg" class="header-icon" />
        </div>
        <div class="publish-form">
          <el-input
            v-model="newAnnouncement.title"
            placeholder="请输入公告标题"
            class="title-input"
          >
            <template #prefix>
              <img src="https://api.iconify.design/material-symbols:title.svg" class="input-icon" />
            </template>
          </el-input>
          <el-input
            v-model="newAnnouncement.content"
            type="textarea"
            :rows="6"
            placeholder="请输入公告内容"
            class="content-input"
          />
          <el-button type="primary" class="publish-btn" @click="publishAnnouncement">
            <img src="https://api.iconify.design/material-symbols:send.svg" class="button-icon" />
            发布公告
          </el-button>
        </div>
      </div>

      <!-- 公告列表 -->
      <div class="list-card">
        <div class="card-header">
          <h3>已发布公告</h3>
          <img src="https://api.iconify.design/material-symbols:list-alt.svg" class="header-icon" />
        </div>
        <div class="notice-list">
          <div v-for="announcement in filteredAnnouncements" :key="announcement.id" class="notice-item">
            <div class="notice-content">
              <div class="notice-header">
                <h4>{{ announcement.title }}</h4>
                <span class="notice-time">{{ moment(announcement.time).format('YYYY-MM-DD HH:mm:ss') }}</span>
              </div>
              <p class="notice-text">{{ announcement.content }}</p>
              <div class="notice-actions">
                <el-button type="primary" text @click="openEditDialog(announcement)">
                  <img src="https://api.iconify.design/material-symbols:edit.svg" class="action-icon" />
                  编辑
                </el-button>
                <el-button type="danger" text @click="deleteAnnouncement(announcement.id)">
                  <img src="https://api.iconify.design/material-symbols:delete.svg" class="action-icon" />
                  删除
                </el-button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 编辑公告对话框 -->
    <el-dialog
      v-model="editDialogVisible"
      title="编辑公告"
      width="50%"
      destroy-on-close
    >
      <el-form>
        <el-form-item label="标题">
          <el-input v-model="currentEditAnnouncement.title" />
        </el-form-item>
        <el-form-item label="内容">
          <el-input
            v-model="currentEditAnnouncement.content"
            type="textarea"
            :rows="6"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="editDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="updateAnnouncement">
            确认
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
.publish-anno {
  width: 100%;
  padding: 20px 20px 20px 4px;
  height: calc(100vh - 60px);
  overflow-y: auto;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.section-header h2 {
  margin: 0;
  font-size: 24px;
  color: #2c3e50;
}

.header-actions {
  display: flex;
  gap: 12px;
}

.search-input {
  width: 240px;
}

.action-icon {
  width: 18px;
  height: 18px;
  margin-right: 4px;
  vertical-align: middle;
}

.stats-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 20px;
  margin-bottom: 24px;
}

.stat-card {
  background: white;
  border-radius: 12px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  background: #ecf5ff;
  display: flex;
  align-items: center;
  justify-content: center;
}

.stat-icon img {
  width: 28px;
  height: 28px;
  color: #409EFF;
}

.stat-icon.success {
  background: #f0f9eb;
}

.stat-icon.success img {
  color: #67c23a;
}

.stat-icon.warning {
  background: #fdf6ec;
}

.stat-icon.warning img {
  color: #e6a23c;
}

.stat-info h3 {
  margin: 0;
  font-size: 14px;
  color: #666;
}

.stat-info p {
  margin: 4px 0 0;
  font-size: 24px;
  font-weight: bold;
  color: #2c3e50;
}

.content-grid {
  display: grid;
  grid-template-columns: 360px 1fr;
  gap: 24px;
  align-items: start;
}

.publish-card,
.list-card {
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 12px;
  border-bottom: 1px solid #eee;
}

.card-header h3 {
  margin: 0;
  font-size: 18px;
  color: #2c3e50;
}

.header-icon {
  width: 24px;
  height: 24px;
  color: #409EFF;
}

.publish-form {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.input-icon {
  width: 20px;
  height: 20px;
  color: #909399;
}

.button-icon {
  width: 18px;
  height: 18px;
  margin-right: 4px;
  vertical-align: middle;
}

.publish-btn {
  align-self: flex-end;
}

.notice-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
  max-height: calc(100vh - 400px);
  overflow-y: auto;
}

.notice-item {
  background: #f8f9fa;
  border-radius: 8px;
  padding: 16px;
  transition: all 0.3s ease;
}

.notice-item:hover {
  background: #f2f6fc;
}

.notice-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.notice-header h4 {
  margin: 0;
  font-size: 16px;
  color: #2c3e50;
}

.notice-time {
  font-size: 12px;
  color: #909399;
}

.notice-text {
  margin: 0;
  color: #606266;
  font-size: 14px;
  line-height: 1.6;
}

.notice-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 12px;
}

:deep(.el-dialog) {
  border-radius: 12px;
}

:deep(.el-dialog__header) {
  margin: 0;
  padding: 20px;
  border-bottom: 1px solid #eee;
}

:deep(.el-dialog__body) {
  padding: 20px;
}

:deep(.el-dialog__footer) {
  padding: 20px;
  border-top: 1px solid #eee;
}
</style>