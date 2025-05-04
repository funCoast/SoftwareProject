<script setup lang="ts">
import axios from 'axios'
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import moment from 'moment'

// 公告相关
const announcements = ref<{
  id: number
  title: string
  content: string
  time: Date
}[]>([])

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
        uid: sessionStorage.getItem('uid')
      }
    })
    if (response.data.code === 0) {
      announcements.value = response.data.announcements
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
        uid: sessionStorage.getItem('uid'),
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
    </div>
    <div class="notice-content">
      <!-- 公告发布表单 -->
      <div class="notice-form">
        <el-input
          v-model="newAnnouncement.title"
          placeholder="请输入公告标题"
          class="notice-title"
        />
        <el-input
          v-model="newAnnouncement.content"
          type="textarea"
          :rows="4"
          placeholder="请输入公告内容"
          class="notice-content-input"
        />
        <el-button type="primary" @click="publishAnnouncement">发布公告</el-button>
      </div>

      <!-- 公告列表 -->
      <div class="notice-list">
        <div v-for="announcement in announcements" :key="announcement.id" class="notice-item">
          <div class="notice-text">
            <div class="notice-header">
              <h4>{{ announcement.title }}</h4>
            </div>
            <p>{{ announcement.content }}</p>
            <div class="notice-footer">
              <span class="notice-time">{{ moment(announcement.time).format('YYYY-MM-DD hh:mm:ss') }}</span>
              <div class="notice-actions">
                <el-button type="primary" size="small" @click="openEditDialog(announcement)">
                  编辑
                </el-button>
                <el-button type="danger" size="small" @click="deleteAnnouncement(announcement.id)">
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
    >
      <el-form>
        <el-form-item label="标题">
          <el-input v-model="currentEditAnnouncement.title" />
        </el-form-item>
        <el-form-item label="内容">
          <el-input
            v-model="currentEditAnnouncement.content"
            type="textarea"
            :rows="4"
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
  padding: 20px;
  max-width: 800px;
  margin: 0 auto;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.section-header h2 {
  margin: 0;
  color: #2c3e50;
}

.notice-content {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.notice-form {
  margin-bottom: 20px;
  padding: 20px;
  background: #f8f9fa;
  border-radius: 8px;
}

.notice-title {
  margin-bottom: 10px;
}

.notice-content-input {
  margin-bottom: 10px;
}

.notice-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.notice-item {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  padding: 20px;
  border-radius: 8px;
  background-color: #f8f9fa;
  transition: all 0.3s ease;
  margin-bottom: 15px;
  position: relative;
}

.notice-item:hover {
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.notice-header {
  margin-bottom: 12px;
}

.notice-header h4 {
  margin: 0;
  font-size: 16px;
  color: #2c3e50;
}

.notice-text p {
  margin: 0 0 15px 0;
  color: #666;
  font-size: 14px;
  line-height: 1.6;
}

.notice-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 10px;
  padding-top: 10px;
  border-top: 1px solid #eee;
}

.notice-time {
  font-size: 12px;
  color: #999;
}

.notice-actions {
  display: flex;
  gap: 8px;
  position: absolute;
  bottom: 20px;
  right: 20px;
}

.notice-actions .el-button {
  padding: 6px 12px;
  font-size: 13px;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}
</style>