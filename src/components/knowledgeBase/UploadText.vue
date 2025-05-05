<script setup lang="ts">
import { ref } from "vue"
import type { UploadInstance, UploadRequestOptions } from 'element-plus'
import { UploadFilled } from "@element-plus/icons-vue"
import axios from "axios"
import router from "../../router"

const uploadRef = ref<UploadInstance>()
const listLength = ref(0)
const segmentMode = ref("auto")
const dialogVisible = ref(false)

// 文件上传前的钩子，用于校验文件类型和大小
function handleChange(file: File, fileList: File[]) {
  const isLt5M = file.size / 1024 / 1024 < 20
  if (!isLt5M) {
    alert("文件大小不能超过 20MB！")
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

function uploadText(options: UploadRequestOptions) {
  const formData = new FormData()
  formData.append("file", options.file)
  formData.append("uid", sessionStorage.getItem("uid") as string)
  formData.append("kb_id", router.currentRoute.value.params.id as string)
  formData.append("segment_mode", segmentMode.value)

  axios({
    method: 'post',
    url: '/kb/uploadText',
    data: formData,
    headers: {
          'Content-Type': 'multipart/form-data',
    },
  }).then(function (response) {
    if (response.data.code === 0) {
      console.log(response.data.message)
      router.push('/workspace/textBase/' + router.currentRoute.value.params.id)
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
      <h2>上传文件</h2>
      <el-upload
        ref="uploadRef"
        class="upload-demo"
        action=""
        drag
        multiple
        :http-request="uploadText" 
        accept=".txt,.pdf,.doc,.docx,.md"
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
            支持 txt, pdf, doc, docx, md 格式文件，单个文件大小不超过 20MB
          </div>
        </template>
      </el-upload>

      <div class="actions">
        <el-button type="primary" :disabled="!listLength" @click="openDialog">选择分段模式</el-button>
        <el-button type="danger" :disabled="!listLength" @click="clear">清空列表</el-button>
      </div>
    </div>

    <!-- 弹窗 -->
    <el-dialog title="选择分段模式" v-model="dialogVisible" width="30%">
      <el-form>
        <el-form-item label="分段模式">
          <el-radio-group v-model="segmentMode">
            <el-radio value="auto">自动分段</el-radio>
            <el-radio value="custom">自定义分段（待完善）</el-radio>
            <el-radio value="hierarchical">按层级分段（待完善）</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>
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