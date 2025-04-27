<script setup lang="ts">
import { ref, computed, onMounted } from "vue"
import { Search } from '@element-plus/icons-vue'
import router from "../../router"
import axios from "axios"

interface Text {
  id: number
  name: string
}

interface paragraph {
  id: number
  level: number
  content: string
}

const texts = ref<Text[]>([])
const searchQuery = ref("")
const selectedText = ref<Text>()  // 存储选中的文本
const content = ref<paragraph[]>([])  // 存储文本内容

// 计算属性：根据搜索框的输入过滤文本列表
const filteredTexts = computed(() => {
  return texts.value.filter(text => 
    text.name.includes(searchQuery.value)
  )
})

onMounted(async () => {
  await getTexts()  // 等待获取文本列表完成
  if (texts.value.length > 0) {
    selectedText.value = texts.value[0]  // 选中第一个文本
    await getTextContent(selectedText.value.id) // 获取文本内容
  }
})


async function getTexts() {
  return axios({
    method: 'get',
    url: '/kb/getTexts',
    params: {
      uid: sessionStorage.getItem("uid"),
      kb_id: router.currentRoute.value.params.id,
    },
  }).then(function (response) {
    if (response.data.code === 0) {
      texts.value = response.data.texts
    } else {
      console.log(response.data.message)
    }
  }).catch(function (error) {
    console.error(error)
    alert(error.message)
  })
}

// 处理文本项点击事件
function selectText(text: Text) {
  selectedText.value = text
  getTextContent(text.id)
}

async function getTextContent(id: number) {
  return axios({
    method: 'get',
    url: '/kb/getTextContent',
    params: {
      uid: sessionStorage.getItem("uid"),
      kb_id: router.currentRoute.value.params.id,
      text_id: id
    },
  }).then(function (response) {
    if (response.data.code === 0) {
      content.value = response.data.content
    } else {
      console.log(response.data.message)
    }
  }).catch(function (error) {
    console.error(error)
  })
}

function goToUploadPage() {
  router.push(router.currentRoute.value.path + "/upload")
}
</script>

<template>
  <div class="content">
    <!-- 顶部标题栏 -->
    <div class="topBar">
      <img src="../../assets/icons/Back.svg" alt="返回" class="backIcon" @click="router.push('/workspace/resourcelibrary')">
      <h2>文本知识库</h2>
      <p class="subtitle">文本数量：{{ texts.length }}</p>
      <button class="add-btn" type="button" @click="goToUploadPage">
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
        <!-- 选中文本标题 -->
        <el-header class="text-header">
          <div v-if="selectedText" class="text-title">
            <span class="text-icon">📄</span>
            <span class="text-name">{{ selectedText.name }}</span>
          </div>
          <div v-else class="text-placeholder">
            请选择一个文本
          </div>
        </el-header>
        <!-- 文本内容分段显示 -->
        <el-main class="text-content">
          <div v-if="selectedText">
            <div
              v-for="(paragraph, index) in content"
              :key="index"
              :class="['text-paragraph', `level-${paragraph.level}`]"
            >
              {{ paragraph.content }}
            </div>
          </div>
          <div v-else class="text-placeholder">
            请选择一个文本以查看内容
          </div>
        </el-main>
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
  width: 200px;
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
  font-size: 14px;
}

.text-item:hover {
  background-color: #f5f5f5;
}

/* 美化选中文本标题 */
.text-header {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 60px;
  background-color: #f5f5f5;
  border-bottom: 1px solid #ccc;
}

.text-title {
  display: flex;
  align-items: center;
  font-size: 16px;
  font-weight: bold;
  color: #333;
}

.text-icon {
  margin-right: 8px;
  font-size: 18px;
}

.text-name {
  font-size: 16px;
}

.text-placeholder {
  font-size: 14px;
  color: #999;
}

/* 文本内容样式 */
.text-content {
  padding: 20px;
  background-color: #fff;
  overflow-y: auto;
}

.text-paragraph {
  margin-bottom: 10px; /* 增加段落间距 */
  line-height: 1.8; /* 增加行高 */
  font-size: 15px; /* 调整字体大小 */
  color: #333;
  padding: 10px; /* 增加内边距 */
  border-left: 4px solid #409eff; /* 添加左侧边框 */
  background-color: #f9f9f9; /* 设置背景颜色 */
  border-radius: 4px; /* 添加圆角 */
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1); /* 添加阴影效果 */
}

.text-paragraph:hover {
  background-color: #e6f7ff; /* 段落悬停时背景变浅 */
  border-left-color: #66b1ff; /* 段落悬停时左侧边框颜色变化 */
}

/* Level 1 样式 */
.level-1 {
  font-size: 18px;
  font-weight: bold;
  color: #2c3e50;
  border-left-color: #409eff;
}

/* Level 2 样式 */
.level-2 {
  font-size: 16px;
  font-weight: 600;
  color: #3a8ee6;
  border-left-color: #66b1ff;
}

/* Level 3 样式 */
.level-3 {
  font-size: 14px;
  font-weight: 500;
  color: #5c6bc0;
  border-left-color: #8c9eff;
}

/* Level 4 样式 */
.level-4 {
  font-size: 13px;
  font-weight: 400;
  color: #8d6e63;
  border-left-color: #bcaaa4;
}
</style>