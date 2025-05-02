<script setup lang="ts">
import { ref } from "vue"
import type { UploadInstance, UploadRequestOptions } from 'element-plus'
import { UploadFilled } from "@element-plus/icons-vue"
import axios from "axios"
import router from "../../router"

const uploadRef = ref<UploadInstance>()
const listLength = ref(0)
const dialogVisible = ref(false)

// 文件上传前的钩子，用于校验文件类型和大小
function handleChange(file: File, fileList: File[]) {
  const isLt5M = file.size / 1024 / 1024 < 5
  if (!isLt5M) {
    alert("图片大小不能超过 5MB！")
    fileList.splice(fileList.indexOf(file), 1)
  }
  listLength.value = fileList.length
}

function handleRemove(fileList: File[]) {
  listLength.value = fileList.length
}

function openDialog() {
  dialogVisible.value = true
}

function uploadPicture(options: UploadRequestOptions) {
  const formData = new FormData()
  formData.append("file", options.file)
  formData.append("uid", sessionStorage.getItem("uid") as string)
  formData.append("kb_id", router.currentRoute.value.params.id as string)

  axios({
    method: 'post',
    url: '/kb/uploadPicture',
    data: formData,
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  }).then(function (response) {
    if (response.data.code === 0) {
      console.log(response.data.message)
      router.push('/workspace/pictureBase/' + router.currentRoute.value.params.id)
    } else {
      console.log(response.data.message)
    }
  }).catch(function (error) {
    console.error(error)
  })
}

// 上传文件到服务器
function submitUpload() {
  uploadRef.value!.submit()
}

function clear() {
  uploadRef.value!.clearFiles()
  listLength.value = 0
}
</script>

<template>
  <div class="content">
    <div class="upload-container">
      <h2>上传图像</h2>
      <el-upload
          ref="uploadRef"
          class="upload-demo"
          action=""
          drag
          multiple
          :http-request="uploadPicture"
          accept="image/*"
          :auto-upload="false"
          :on-change="handleChange"
          :on-remove="handleRemove"
      >
        <el-icon class="el-icon--upload"><UploadFilled /></el-icon>
        <div class="el-upload__text">
          将文件拖到此处或 <em>点击上传</em>
        </div>
        <template #tip>
          <div class="el-upload__tip">
            支持 jpg、png、jpeg 等格式的图像，单张图像大小不超过 5MB
          </div>
        </template>
      </el-upload>

      <div class="actions">
        <el-button type="primary" :disabled="!listLength" @click="openDialog">上传</el-button>
        <el-button type="danger" :disabled="!listLength" @click="clear">清空列表</el-button>
      </div>
    </div>

    <!-- 弹窗 -->
    <el-dialog title="上传图片" v-model="dialogVisible" width="30%">
      <el-text>上传后将自动对图片进行标注，之后您可以对标注内容进行修改</el-text>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitUpload">确认上传</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
.content {
  flex: 1;
  padding: 20px;
  height: 100%;
  overflow-y: auto;
}

.upload-container {
  padding: 20px;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.upload-container h2 {
  margin-bottom: 20px;
  font-size: 18px;
  color: #333;
}

.upload-demo {
  margin-bottom: 20px;
}

.actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}
</style>