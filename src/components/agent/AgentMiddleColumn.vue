<template>
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
        <div v-if="isDropdownVisible('skill', index)" class="dropdown-content">
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
        <div v-if="isDropdownVisible('memory', index)" class="dropdown-content">
          {{ memoryItem.explanation }}
        </div>
      </div>
    </div>
    <h2>对话体验</h2>
  </div>
</template>

<script>
export default {
  name: "App",
  data() {
    return {
      skillItems: [
        {
          name: "插件",
          explanation:
            "插件用于扩展SD动画框架的功能，可实现特定的动画效果或交互逻辑。",
        },
        {
          name: "工作流",
          explanation:
            "工作流用于组织和管理动画制作过程中的各个步骤，确保流程有序进行。",
        },
        {
          name: "触发器",
          explanation:
            "触发器可根据特定条件触发动画中的事件，如动画开始、节点点击等。",
        },
      ],
      knowledgeItems: [
        {
          name: "文本",
          explanation:
            "文本用于在动画中添加文字内容，可设置字体、颜色、位置等属性。",
        },
        {
          name: "表格",
          explanation: "表格可用于展示结构化数据，在动画中呈现信息列表。",
        },
        {
          name: "照片",
          explanation: "照片可作为动画中的素材，添加图像元素丰富动画内容。",
        },
      ],
      memoryItems: [
        {
          name: "变量",
          explanation:
            "变量用于存储动画中的数据，方便在代码中进行数据处理和逻辑判断。",
        },
        {
          name: "数据库",
          explanation:
            "数据库可用于存储动画相关的大量数据，便于数据的管理和调用。",
        },
        {
          name: "长期记忆",
          explanation: "长期记忆用于保存动画运行过程中的重要信息，供后续使用。",
        },
        {
          name: "文件盒子",
          explanation:
            "文件盒子用于管理动画制作过程中的文件，方便文件的存储和读取。",
        },
      ],
      dropdownStates: [],
    };
  },
  methods: {
    toggleDropdown(category, index) {
      const key = `${category}-${index}`;
      this.dropdownStates[key] = !this.dropdownStates[key];
    },
    isDropdownVisible(category, index) {
      const key = `${category}-${index}`;
      return this.dropdownStates[key] || false;
    },
  },
};
</script>

<style>
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
  display: flex;
  align-items: center;
}
.menu-item:last-child {
  border-bottom: 1px solid #ccc;
}
.dropdown-content {
  padding: 10px;
  background-color: #f9f9f9;
  border: 1px solid #ccc;
  border-top: none;
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
