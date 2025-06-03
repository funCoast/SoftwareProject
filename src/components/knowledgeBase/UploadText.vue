<script setup lang="ts">
import { ref } from "vue"
import type { UploadInstance, UploadRequestOptions } from 'element-plus'
import { ElLoading } from "element-plus"
import { UploadFilled } from "@element-plus/icons-vue"
import axios from "axios"
import router from "@/router"


const uploadRef = ref<UploadInstance>()
const listLength = ref(0)
const segmentMode = ref("auto")
const dialogVisible = ref(false)
const chunkSize = ref(800)

// 文件上传前的钩子，用于校验文件类型和大小
function handleChange(file: File, fileList: File[]) {
  const isLt20M = file.size / 1024 / 1024 < 20
  if (!isLt20M) {
    ElMessage.warning("文件大小不能超过 20MB！")
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
  // 层级分段时校验文件类型
  if (segmentMode.value === 'hierarchical') {
    const file = options.file
    if (!file.name.endsWith('.md')) {
      ElMessage.error("按层级分段仅支持 Markdown (.md) 文件！")
      dialogVisible.value = false
      return
    }
  }

  const formData = new FormData()
  formData.append("file", options.file)
  formData.append("uid", localStorage.getItem('LingXi_uid') as string)
  formData.append("kb_id", router.currentRoute.value.params.id as string)
  formData.append("segment_mode", segmentMode.value)
  if (segmentMode.value === 'custom') {
    formData.append("chunk_size", chunkSize.value.toString())
  }

  let loadingInstance = ElLoading.service({
    lock: true,
    text: '正在上传，请稍候...',
    background: 'rgba(255, 255, 255, 0.7)'
  })

  axios({
    method: 'post',
    url: '/kb/uploadText',
    data: formData,
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  }).then(function (response) {
    loadingInstance.close()
    if (response.data.code === 0) {
      console.log(response.data.message)
      router.push('/workspace/textBase/' + router.currentRoute.value.params.id)
    } else {
      ElMessage.error("上传失败！" + response.data.message)
    }
  }).catch(function (error) {
    loadingInstance.close()
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

function goBack() {  
  router.push(router.currentRoute.value.path.replace('/upload', ''));
}
</script>

<template>
  <div class="content">
    <div class="upload-container">
      <div class="topBar">
        <img src="../../assets/icons/Back.svg" alt="返回" class="backIcon" @click="goBack" />
        <h2>上传文件</h2>
      </div>
      <el-upload
        ref="uploadRef"
        class="upload-demo"
        action=""
        drag
        multiple
        :http-request="uploadText" 
        accept=".txt,.pdf,.docx,.md"
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
            支持 txt, pdf, docx, md 格式文件，单个文件大小不超过 20MB
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
            <el-radio value="custom">自定义分段</el-radio>
            <el-radio value="hierarchical">按层级分段</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item
          v-if="segmentMode === 'custom'"
          label="最大分段长度"
          required
        >
          <el-input-number
            v-model="chunkSize"
            :min="100"
            :max="1500"
            :step="1"
            style="width: 180px"
            controls-position="right"
            placeholder="请输入最大分段长度"
          />
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
  padding: 10px 20px 20px 20px;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.topBar {
  display: flex;
  margin-bottom: 10px;
}

.topBar h2 {
  font-size: 18px;
  color: #333;
}

.backIcon {
  width: 20px;
  height: 20px;
  cursor: pointer;
  color: #333;
  margin: auto 10px auto 0;
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