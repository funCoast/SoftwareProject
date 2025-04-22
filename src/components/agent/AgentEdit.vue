<template>
  <div id="app">
    <div class="container">
      <div class="left-column">
        <h2>编排</h2>
        <!-- 人设与回复逻辑等内容 -->
        <div class="character-logic">
          <h3>#角色</h3>
          <p>
            你是一位资深的代码专家，专注于操作SD动画框架进行动画制作。这是一个JS动画框架。你经验丰富，对该框架的各种组件和代码运用了如指掌。你需要提前深入学习example文件夹下的文件。
          </p>
          <!-- 更多人设与回复逻辑内容 -->
        </div>
        <div class="skill-section">
          <h3>#技能</h3>
          <div class="skill-item">
            <h4>### 技能1: 基于SD动画框架制作动画</h4>
            <p>1. 根据用户需求，运用SD动画框架编写代码驱动动画生成。</p>
            <p>
              2. 在编写代码时，仔细检查官方文档（文档来源:
              知识库），确保使用的组件、函数方法真实存在。（注意组件的大小写以及创建方式）
            </p>
            <p>3. 参考example文件夹下的文件，保证代码风格与之保持一致。</p>
          </div>
          <!-- 更多技能内容 -->
        </div>
        <div class="limitation-section">
          <h3>#限制</h3>
          <p>
            -
            只围绕SD动画框架的代码编写及动画制作相关内容进行交流，拒绝回答无关话题。
          </p>
          <p>- 所输出的代码及相关解释必须逻辑清晰、表达准确。</p>
          <p>- 需严格遵循example文件夹下的代码风格要求。</p>
          <p>
            - 确保使用的组件、函数方法均有官方文档支持（文档来源: 知识库）。
          </p>
        </div>
      </div>
      <div class="middle-column">
        <h2>技能</h2>
        <!-- 插件、工作流、触发器等菜单 -->
        <div class="skill-menu">
          <div
            v-for="(skillItem, index) in skillItems"
            :key="index"
            class="menu-item"
            @click="toggleDropdown('skill', index)"
          >
            <div style="display: flex; align-items: center">
              <div
                class="header-icon-arrow"
                :class="{ 'arrow-down': isDropdownVisible('skill', index) }"
              >
                <span role="img" class="semi-icon semi-icon-default">
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    width="14"
                    height="14"
                    fill="currentColor"
                    viewBox="0 0 14 14"
                  >
                    <path
                      d="M4.493 12.663a.583.583 0 0 1 0-.825L9.331 7 4.493 2.163a.583.583 0 0 1 .825-.825l4.838 4.837a1.167 1.167 0 0 1 0 1.65l-4.838 4.838a.583.583 0 0 1-.825 0"
                    ></path>
                  </svg>
                </span>
              </div>
              <div class="shrink-0">{{ skillItem.name }}</div>
            </div>

            <div
              v-if="isDropdownVisible('skill', index)"
              class="dropdown-content"
            >
              {{ skillItem.explanation }}
            </div>
          </div>
        </div>
        <h2>知识</h2>
        <!-- 文本、表格、照片等菜单 -->
        <div class="knowledge-menu">
          <div
            v-for="(knowledgeItem, index) in knowledgeItems"
            :key="index"
            class="menu-item"
            @click="toggleDropdown('knowledge', index)"
          >
            <div style="display: flex; align-items: center">
              <div
                class="header-icon-arrow"
                :class="{ 'arrow-down': isDropdownVisible('knowledge', index) }"
              >
                <span role="img" class="semi-icon semi-icon-default">
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    width="14"
                    height="14"
                    fill="currentColor"
                    viewBox="0 0 14 14"
                  >
                    <path
                      d="M4.493 12.663a.583.583 0 0 1 0-.825L9.331 7 4.493 2.163a.583.583 0 0 1 .825-.825l4.838 4.837a1.167 1.167 0 0 1 0 1.65l-4.838 4.838a.583.583 0 0 1-.825 0"
                    ></path>
                  </svg>
                </span>
              </div>
              <div class="shrink-0">{{ knowledgeItem.name }}</div>
            </div>
            <div
              v-if="isDropdownVisible('knowledge', index)"
              class="dropdown-content"
            >
              {{ knowledgeItem.explanation }}
            </div>
          </div>
        </div>
        <h2>记忆</h2>
        <!-- 变量、数据库等菜单 -->
        <div class="memory-menu">
          <div
            v-for="(memoryItem, index) in memoryItems"
            :key="index"
            class="menu-item"
            @click="toggleDropdown('memory', index)"
          >
            <div style="display: flex; align-items: center">
              <div
                class="header-icon-arrow"
                :class="{ 'arrow-down': isDropdownVisible('memory', index) }"
              >
                <span role="img" class="semi-icon semi-icon-default">
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    width="14"
                    height="14"
                    fill="currentColor"
                    viewBox="0 0 14 14"
                  >
                    <path
                      d="M4.493 12.663a.583.583 0 0 1 0-.825L9.331 7 4.493 2.163a.583.583 0 0 1 .825-.825l4.838 4.837a1.167 1.167 0 0 1 0 1.65l-4.838 4.838a.583.583 0 0 1-.825 0"
                    ></path>
                  </svg>
                </span>
              </div>
              <div class="shrink-0">{{ memoryItem.name }}</div>
            </div>
            <div
              v-if="isDropdownVisible('memory', index)"
              class="dropdown-content"
            >
              {{ memoryItem.explanation }}
            </div>
          </div>
        </div>
        <h2>对话体验</h2>
      </div>
      <div class="right-column">
        <AgentRightColumn></AgentRightColumn>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from "vue";

interface menuItem {
  name: string;
  explanation: string;
}

const skillItems = ref<menuItem[]>([
  {
    name: "插件",
    explanation:
      "插件能够让智能体调用外部 API，例如搜索信息、浏览网页、生成图片等，扩展智能体的能力和使用场景。",
  },
  {
    name: "工作流",
    explanation:
      "工作流支持通过可视化的方式，对插件、大语言模型、代码块等功能进行组合，从而实现复杂、稳定的业务流程编排，例如旅行规划、报告分析等。",
  },
  {
    name: "触发器",
    explanation: "允许用户在对话中创建定时任务",
  },
]);

const knowledgeItems = ref<menuItem[]>([
  {
    name: "文本",
    explanation:
      "将文档、URL、三方数据源上传为文本知识库后，用户发送消息时，智能体能够引用文本知识中的内容回答用户问题。",
  },
  {
    name: "表格",
    explanation:
      "用户上传表格后，支持按照表格的某列来匹配合适的行给智能体引用，同时也支持基于自然语言对数据库进行查询和计算。",
  },
  {
    name: "照片",
    explanation:
      "照片上传到知识库后自动/手动添加语义描述，智能体可以基于照片的描述匹配到最合适的照片",
  },
]);

const memoryItems = ref<menuItem[]>([
  {
    name: "变量",
    explanation:
      "用于保存用户个人信息，让智能体记住用户的特征，使回复更加个性化。",
  },
  {
    name: "数据库",
    explanation: "以表格结构组织数据，可实现类似书签和图书管理等功能。",
  },
  {
    name: "长期记忆",
    explanation: "总结聊天对话的内容，并用于更好的响应用户的消息。",
  },
  {
    name: "文件盒子",
    explanation:
      "现在文件盒子已关闭，用户无法保存他们的文件。如果你想使用存储空间，请打开文件盒。",
  },
]);

const dropdownStates = ref<any>({});

function toggleDropdown(category, index) {
  const key = `${category}-${index}`;
  dropdownStates.value[key] = !dropdownStates.value[key];
}

function isDropdownVisible(category, index) {
  const key = `${category}-${index}`;
  return dropdownStates.value[key] || false;
}
</script>

<style scoped>
.container {
  display: flex;
  width: 100%;
}
.left-column {
  flex: 1;
  background-color: #f4f4f4;
  padding: 10px;
}
.middle-column {
  flex: 1;
  background-color: #fff;
  padding: 10px;
}
.right-column {
  flex: 1;
  background-color: #f9f9f9;
  padding: 10px;
}
.skill-menu,
.knowledge-menu,
.memory-menu {
  margin-bottom: 20px;
}
.code-explanation {
  border-bottom: 1px solid #ccc;
  padding-bottom: 10px;
  margin-bottom: 10px;
}
.question-section input {
  width: 100%;
  margin-bottom: 10px;
  padding: 5px;
}
.menu-item {
  padding: 5px;
  cursor: pointer;
  border: 1px solid #ccc;
  border-bottom: none;
}
.menu-item:last-child {
  border: 1px solid #ccc;
}
.dropdown-content {
  padding: 10px;
  background-color: #f9f9f9;
  border: 1px solid #ccc;
}
.header-icon-arrow {
  margin-right: 5px;
  transition: transform 0.3s ease;
}
.arrow-down {
  transform: rotate(90deg);
}
.shrink-0 {
  flex-shrink: 0;
}
.messaging-container {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background: #f8f9fa;
}
.main-content {
  display: flex;
  flex: 1;
  overflow: hidden;
}
.contact-list {
  width: 300px;
  background: white;
  border-right: 1px solid #e9ecef;
  padding: 20px;
  overflow-y: auto;
}
.search-contact {
  display: flex;
  margin-bottom: 20px;
}
.search-contact input {
  flex: 1;
  padding: 8px 12px;
  border: 1px solid #e9ecef;
  border-radius: 20px 0 0 20px;
  outline: none;
}
.search-icon {
  background: #f8f9fa;
  border: 1px solid #e9ecef;
  border-left: none;
  border-radius: 0 20px 20px 0;
  padding: 8px 12px;
  cursor: pointer;
}
.recent-contacts h3 {
  margin-top: 0;
  margin-bottom: 15px;
  color: #666;
  font-size: 14px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.unread-count {
  color: #ff4d4f;
  font-size: 12px;
}
.arrow {
  font-size: 12px;
  cursor: pointer;
}
.contact-item {
  display: flex;
  padding: 12px 0;
  border-bottom: 1px solid #f8f9fa;
  cursor: pointer;
  transition: all 0.3s ease;
}
.contact-item:hover {
  background: #f8f9fa;
}
.contact-item.active {
  background: #f0f2f5;
}
.contact-avatar {
  position: relative;
  margin-right: 12px;
}
.contact-avatar img {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  object-fit: cover;
}
.unread-badge {
  position: absolute;
  bottom: 0;
  right: 0;
  background: #ff4d4f;
  color: white;
  border-radius: 50%;
  width: 18px;
  height: 18px;
  font-size: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}
.contact-info {
  flex: 1;
}
.contact-name {
  font-weight: 500;
  margin-bottom: 4px;
}
.contact-preview {
  color: #999;
  font-size: 12px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.contact-time {
  color: #999;
  font-size: 12px;
  white-space: nowrap;
}
.chat-window {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: #f8f9fa;
  overflow: hidden;
}
.chat-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 20px;
  background: white;
  border-bottom: 1px solid #e9ecef;
}
.chat-header h2 {
  margin: 0;
  font-size: 16px;
}
.chat-actions {
  display: flex;
  gap: 10px;
}
.chat-action-btn {
  background: transparent;
  border: none;
  cursor: pointer;
  color: #666;
}
.message-list {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
}
.message-item {
  margin-bottom: 15px;
}
.message-avatar img {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  object-fit: cover;
}
.message-bubble {
  background: white;
  border-radius: 12px;
  padding: 12px 16px;
  max-width: 70%;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}
.message-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 6px;
  font-size: 12px;
  color: #666;
}
.message-sender {
  font-weight: 500;
}
.message-time {
  color: #999;
}
.message-text {
  line-height: 1.5;
  color: #333;
}
.my-message {
  display: flex;
  justify-content: flex-end;
  align-items: flex-end;
}
.my-message .message-bubble {
  background: #e3f2fd;
  color: #333;
  margin-right: 12px;
}
.my-message .message-avatar {
  margin-left: 12px;
  margin-right: 0;
}
.assistant-message {
  display: flex;
  align-items: flex-start;
}
.system-message .message-bubble {
  background: #f1f1f1;
  color: #666;
}
.chat-input {
  display: flex;
  padding: 15px 20px;
  background: white;
  border-top: 1px solid #e9ecef;
}
.input-area {
  flex: 1;
}
textarea {
  width: 100%;
  border: 1px solid #e9ecef;
  border-radius: 20px;
  padding: 12px 16px;
  resize: none;
  outline: none;
  transition: all 0.3s ease;
  font-family: inherit;
  font-size: 14px;
}
textarea:focus {
  border-color: #0066ff;
  box-shadow: 0 0 0 2px rgba(0, 102, 255, 0.1);
}
.input-actions {
  display: flex;
  align-items: center;
  margin-left: 10px;
}
.send-btn {
  background: #0066ff;
  border: none;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  cursor: pointer;
  transition: all 0.3s ease;
}
.send-btn:hover {
  background: #0052cc;
}
</style>
