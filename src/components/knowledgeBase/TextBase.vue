<script setup lang="ts">
import { ref, computed, onMounted } from "vue";
import { Search } from '@element-plus/icons-vue';
import router from "../../router";

interface Text {
  id: number;
  name: string;
  url: string;
  description: string;
}

const texts = ref<Text[]>([
  { id: 1, name: "格林童话", url: "https://img.picui.cn/free/2024/07/18/66987f69a1089.jpg", description: 
  "在这张照片中，一只小黑猪正在吃一块饼干。在这张照片中，一只小黑猪正在吃一块饼干。在这张照片中，一只小黑猪正在吃一块饼干。"+
  "在这张照片中，一只小黑猪正在吃一块饼干。在这张照片中，一只小黑猪正在吃一块饼干。在这张照片中，一只小黑猪正在吃一块饼干。" },
  { id: 2, name: "安徒生童话", url: "https://img.picui.cn/free/2024/07/18/66987f69a1089.jpg", description: "示例图像2" },
  { id: 3, name: "一千零一夜", url: "https://img.picui.cn/free/2024/07/18/66987f69a1089.jpg", description: "示例图像3" },
]);

const searchQuery = ref(""); // 搜索框绑定的值
const selectedText = ref<Text | null>(null); // 存储选中的文本

// 计算属性：根据搜索框的输入过滤文本列表
const filteredTexts = computed(() => {
  return texts.value.filter(text => 
    text.name.includes(searchQuery.value)
  );
});

// 处理文本项点击事件
const selectText = (text: Text) => {
  selectedText.value = text;
};

// 在组件加载时默认选中第一个文本
onMounted(() => {
  if (texts.value.length > 0) {
    selectedText.value = texts.value[0];
  }
});
</script>

<template>
  <div class="content">
    <!-- 顶部标题栏 -->
    <div class="topBar">
      <img src="../../assets/icons/Back.svg" alt="返回" class="backIcon" @click="router.push('/workspace/resourcelibrary')">
      <h2>文本知识库</h2>
      <p class="subtitle">文本数量：{{ texts.length }}</p>
      <button class="add-btn" type="button" @click="router.push('/workspace/createPicture')">
        添加文本
      </button>
    </div>
    <el-container class="show-area">
        <el-aside class="left-area">
          <el-input class="search-box" v-model="searchQuery" type="text" placeholder="搜索" :prefix-icon="Search" clearable>
          </el-input>
          <p class="list-title">文本列表</p>
          <ul class="text-list">
            <li 
              v-for="text in filteredTexts" 
              :key="text.id" 
              class="text-item" 
              @click="selectText(text)">
              {{ text.name }}
            </li>
          </ul>
        </el-aside>
        <el-container>
          <!-- 显示选中的文本标题 -->
          <el-header>
            {{ selectedText ? selectedText.name : "请选择一个文本" }}
          </el-header>
          <el-main>Main</el-main>
        </el-container>
    </el-container>
  </div>
</template>

<style scoped>
.content {
  display: flex;
  flex-direction: column;
  flex: 1;
  height: 100vh;
  padding: 0 20px;
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

.show-area {
  flex: 1; 
  overflow: auto;
  margin-bottom: 15px;
  border: 1px solid #ccc;
  border-radius: 6px;
}

.left-area {
  width: 180px;
  height: 100%;
  border-right: 1px solid #ccc;
  display: flex;
  flex-direction: column;
}

.search-box {
  width: auto;
  height: 30px;
  margin: 10px;
}

.list-title {
  margin-left: 10px;
  margin-top: 0;
  margin-bottom: 5px;
  font-size: 10px;
  color: #666;
}

.text-list {
  list-style: none;
  padding: 0;
  margin: 0px 5px 0 5px;
}

.text-item {
  padding: 5px 10px;
  border-bottom: 1px solid #ccc;
  cursor: pointer;
}

.text-item:hover {
  background-color: #f5f5f5;
}
</style>