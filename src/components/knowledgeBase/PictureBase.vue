<script setup lang="ts">
import { ref } from "vue";
import router from "../../router";

const id = router.currentRoute.value.params.id; // 获取路由参数id
interface Picture {
  id: number;
  name: string;
  url: string;
  description: string;
}

const pictures = ref<Picture[]>([
  {
    id: 1,
    name: "图片1",
    url: "https://img.picui.cn/free/2024/07/18/66987f69a1089.jpg",
    description:
      "在这张照片中，一只小黑猪正在吃一块饼干。在这张照片中，一只小黑猪正在吃一块饼干。在这张照片中，一只小黑猪正在吃一块饼干。" +
      "在这张照片中，一只小黑猪正在吃一块饼干。在这张照片中，一只小黑猪正在吃一块饼干。在这张照片中，一只小黑猪正在吃一块饼干。",
  },
  { id: 2, name: "图片2", url: "https://img.picui.cn/free/2024/07/18/66987f69a1089.jpg", description: "示例图像2" },
  { id: 3, name: "图片3", url: "https://img.picui.cn/free/2024/07/18/66987f69a1089.jpg", description: "示例图像3" },
]);

// 跳转到图像上传界面
function goToUploadPage() {
  router.push("/workspace/uploadPicture/" + id);
};
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
      <div v-for="picture in pictures" :key="picture.id" class="picture-card">
        <div class="picture-image">
          <img :src="picture.url" :alt="picture.name" />
        </div>
        <div class="picture-info">
          <h3>{{ picture.name }}</h3>
          <p>{{ picture.description }}</p>
        </div>
      </div>
    </div>
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
</style>