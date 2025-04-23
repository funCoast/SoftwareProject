<script setup lang="ts">
import { ref } from "vue";
import { ElMessage } from "element-plus";
import { UploadFilled } from "@element-plus/icons-vue";

// 上传文件列表
const fileList = ref<File[]>([]);

// 文件上传前的钩子，用于校验文件类型和大小
const beforeUpload = (file: File) => {
  const isImage = file.type.startsWith("image/");
  const isLt2M = file.size / 1024 / 1024 < 2;

  if (!isImage) {
    ElMessage.error("只能上传图片文件！");
  }
  if (!isLt2M) {
    ElMessage.error("图片大小不能超过 2MB！");
  }

  return isImage && isLt2M;
};

// 上传图片到服务器
function submitUpload() {
  if (fileList.value.length === 0) {
    ElMessage.warning("请先选择图片！");
    return;
  }

  // 模拟上传逻辑
  const formData = new FormData();
  fileList.value.forEach((file) => {
    formData.append("pictures", file);
  });
  
  // 上传
};
</script>

<template>
  <div class="content">
    <div class="upload-container">
      <h2>上传图片</h2>
      <el-upload
        ref="upload"
        class="upload-demo"
        drag
        multiple
        action=""
        accept="image/*"
        :auto-upload="false"
        :beforeUpload="beforeUpload"
      >
        <el-icon class="el-icon--upload"><UploadFilled /></el-icon>
        <div class="el-upload__text">
          将图片拖到此处或 <em>点击上传</em>
        </div>
        <template #tip>
          <div class="el-upload__tip">
            jpg/png 格式文件， 单个文件大小不超过5MB
          </div>
        </template>
      </el-upload>

      <div class="actions">
        <el-button type="primary" @click="submitUpload">确认上传</el-button>
        <el-button @click="fileList = []">清空选择</el-button>
      </div>
    </div>
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