<script setup lang="ts">
import { onMounted, ref } from "vue";
import axios from "axios";
import router from "../../router";

interface Picture {
  id: number
  name: string
  url: string
  description: string
  hover: boolean // 用于控制鼠标悬停状态
}

const pictures = ref<Picture[]>([])

onMounted(() => {
  getPictures(); // 获取图像列表
})

function getPictures() {
  axios({
    method: 'get',
    url: '/kb/getPictures',
    params: {
      uid: sessionStorage.getItem("uid"),
      kb_id: router.currentRoute.value.params.id,
    },
  }).then(function (response) {
    if (response.data.code === 0) {
      pictures.value = response.data.pictures
    } else {
      ElMessage.error(response.data.message)
    }
  }).catch(function (error) {
    console.error(error)
    ElMessage.error(error.message)
  })
}

// 跳转到图像上传界面
function goToUploadPage() {
  router.push(router.currentRoute.value.path + "/upload");
};

const editDialog = ref(false); // 控制编辑弹窗显示
const editTarget = ref<Picture | null>(null); // 待编辑的图像信息

// 打开编辑弹窗
function tryEdit(picture: Picture) {
  editTarget.value = { ...picture }; // 复制图像信息
  editDialog.value = true;
}

// 保存编辑后的图像信息
function updateEdit() {
  if (!editTarget.value) return;
  axios({
    method: "post",
    url: "/kb/updatePicture",
    data: {
      uid: sessionStorage.getItem("uid"),
      kb_id: router.currentRoute.value.params.id,
      picture_id: editTarget.value.id,
      description: editTarget.value.description,
    },
  }).then((response) => {
    if (response.data.code === 0) {
      ElMessage.success("编辑成功！")
      getPictures() // 重新获取图像列表
      editDialog.value = false // 关闭弹窗
    } else {
      ElMessage.error(response.data.message)
    }
  })
}

const deleteDialog = ref(false); // 控制删除确认弹窗显示
const deleteTarget = ref<Picture | null>(null); // 待删除的图像信息

// 打开删除确认弹窗
function tryDelete(picture: Picture) {
  deleteTarget.value = picture; // 设置待删除的图像信息
  deleteDialog.value = true; // 显示删除确认弹窗
}

// 确认删除图像
function confirmDelete() {
  if (!deleteTarget.value) return;
  axios({
    method: "post",
    url: "/kb/deletePicture",
    data: {
      uid: sessionStorage.getItem("uid"),
      kb_id: router.currentRoute.value.params.id,
      picture_id: deleteTarget.value.id,
    },
  }).then((response) => {
    if (response.data.code === 0) {
      ElMessage.success("删除成功！")
      getPictures() // 重新获取图像列表
      deleteDialog.value = false // 关闭弹窗
      deleteTarget.value = null // 清空待删除的图像信息
    } else {
      ElMessage.error(response.data.message)
      deleteDialog.value = false // 关闭弹窗
      deleteTarget.value = null // 清空待删除的图像信息
    }
  })
}
</script>

<template>
  <div class="content">
    <!-- 顶部标题栏 -->
    <div class="topBar">
      <img src="../../assets/icons/Back.svg" alt="返回" class="backIcon" @click="router.push('/workspace/resourcelibrary')" />
      <h2>图像知识库</h2>
      <p class="subtitle">图像数量：{{ pictures.length }}</p>
      <button class="add-btn" type="button" @click="goToUploadPage">
        添加图像
      </button>
    </div>
    <div class="picture-list">
      <div
        v-for="picture in pictures"
        :key="picture.id"
        class="picture-card"
        @mouseover="picture.hover = true"
        @mouseleave="picture.hover = false"
      >
        <div class="picture-image">
          <img :src="'http://122.9.33.84:8000' + picture.url" :alt="picture.name" />
        </div>
        <div class="picture-info">
          <h3>{{ picture.name }}</h3>
          <p>{{ picture.description }}</p>
        </div>
        <!-- 编辑和删除图标 -->
        <div v-if="picture.hover" class="picture-actions">
          <div class="action-icon edit-icon" @click.stop="tryEdit(picture)">
            <svg viewBox="0 0 24 24" fill="currentColor" width="20" height="20">
              <path d="M3 17.25V21h3.75L17.81 9.94l-3.75-3.75L3 17.25zM20.71 7.04c.39-.39.39-1.02 0-1.41l-2.34-2.34a.996.996 0 0 0-1.41 0l-1.83 1.83 3.75 3.75 1.83-1.83z"/>
            </svg>
          </div>
          <div class="action-icon delete-icon" @click.stop="tryDelete(picture)">
            <svg viewBox="0 0 24 24" fill="currentColor" width="20" height="20">
              <path d="M16 9v10H8V9h8m-1.5-6h-5l-1 1H5v2h14V4h-3.5l-1-1M18 7H6v12c0 1.1.9 2 2 2h8c1.1 0 2-.9 2-2V7z"/>
            </svg>
          </div>
        </div>
      </div>
    </div>

    <!-- 编辑弹窗 -->
    <el-dialog v-model="editDialog" title="编辑图像信息" width="600px">
  <div class="edit-dialog-content">
    <!-- 图片展示 -->
    <div class="image-preview-container">
      <img class="image-preview" :src="'http://122.9.33.84:8000' + editTarget!.url" alt="图像预览" />
    </div>

    <!-- 描述编辑 -->
    <el-input class="description-input" v-model="editTarget!.description" type="textarea" placeholder="请输入图像描述" 
      rows="4" maxlength="100" show-word-limit/>
  </div>
  <template #footer>
    <el-button @click="editDialog = false">取消</el-button>
    <el-button type="primary" @click="updateEdit">保存</el-button>
  </template>
</el-dialog>

    <!-- 删除确认弹窗 -->
    <el-dialog
      v-model="deleteDialog"
      title="确认删除"
      width="400px"
      class="delete-dialog"
    >
      <p>确定要删除图像“{{deleteTarget?.name}}”吗？</p>
      <template #footer>
        <el-button @click="deleteDialog = false">取消</el-button>
        <el-button type="danger" @click="confirmDelete">确认删除</el-button>
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

.topBar {
  display: flex;
  margin-bottom: 20px;
}

.topBar h2 {
  margin: auto 10px auto 0;
  color: #2c3e50;
  font-size: 20px;
}

.backIcon {
  width: 20px;
  height: 20px;
  cursor: pointer;
  color: #2c3e50;
  margin: auto 10px auto 0;
}

.add-btn {
  height: 40px;
  padding: 8px 16px;
  background: #0460bc;
  margin: auto 0 auto auto;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
}

.picture-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, 200px);
  gap: 20px;
}

.picture-card {
  background: white;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
}

.picture-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

.picture-image {
  position: relative;
  width: 100%;
  padding-top: 75%;
}

.picture-image img {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.picture-info {
  padding: 10px;
}

.picture-info h3 {
  margin: 0 0 8px 0;
  color: #2c3e50;
  font-size: 15px;
}

.picture-info p {
  margin: 0 0 12px 0;
  color: #666;
  font-size: 10px;
  line-height: 1.5;
  display: -webkit-box; /* Required for -webkit-line-clamp to work */
  -webkit-box-orient: vertical; /* Required for -webkit-line-clamp to work */
  -webkit-line-clamp: 2; /* WebKit-specific property */
  line-clamp: 2; /* Standard property for compatibility */
  overflow: hidden; /* Ensures content is clipped */
}

.picture-actions {
  position: absolute;
  bottom: 10px;
  right: 10px;
  display: flex;
  gap: 10px;
}

.action-icon {
  width: 30px;
  height: 30px;
  background: white;
  border-radius: 50%;
  display: flex;
  justify-content: center;
  align-items: center;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  cursor: pointer;
  transition: all 0.3s ease;
}

.action-icon:hover {
  background: #f5f5f5;
}

.edit-icon svg {
  color: #4caf50;
}

.delete-icon svg {
  color: #f44336;
}

.edit-dialog-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 20px;
}

.image-preview-container {
  display: flex;
  justify-content: center;
  align-items: center;
}

.image-preview {
  width: 300px;
  height: 300px;
  border-radius: 8px;
  object-fit: cover;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.description-input {
  width: 100%;
}
</style>