<template>
  <div id="app">
    <div class="header">
      <span class="title">预览与调试</span>
      <div class="tools">
        <i class="icon-more"></i>
        <i class="icon-settings"></i>
      </div>
    </div>
    <div class="code-section">
      <div class="code-title">代码说明</div>
      <div class="code-content">
        <p>
          1. 数据解析模块：<code>parseInputFile</code>
          函数用于读取输入文件并解析剧情节<br />点信息，构建适合
          <code>sd.Tree</code>
          使用的数据结构。这里假设输入文件为<br />JSON格式，实际需根据真实数据格式调整。
        </p>
        <p>
          2. 动画初始化模块：<code>initAnimation</code>
          函数根据解析后的数据构建<br /><code>sd.Tree</code>
          剧情选择树，并初始化
          <code>sd.Button</code>
          按钮。在构建树时，<br />为每个节点创建圆形和文本，并使用线条连接节点。
        </p>
        <p>
          3. 交互事件处理模块：<code>handleInteractions</code>
          函数监听节点和按钮的点<br />击事件。点击节点时，检查节点是否已走过，未走过则应用<br /><code
            >sd.Focus</code
          >
          效果并将经过的节点和树枝涂成灰色；点击按钮时，遍历<br />树的所有节点和树枝，将颜色恢复为黑色。
        </p>
        <p>
          4. 主程序：<code>main</code>
          函数调用上述模块完成动画的初始化和交互逻辑设<br />置。在
          <code>sd.init</code> 中启动主程序。
        </p>
        <p>注意：代码中的</p>
      </div>
    </div>
    <div class="info-section">
      <div class="info-item">
        <span class="info-label">29.9s</span> |
        <span class="info-label">6709 Tokens</span>
      </div>
      <div class="info-item">
        <i class="icon-copy"></i>
        <span class="info-label">66</span>
        <i class="icon-refresh"></i>
        <i class="icon-delete"></i>
      </div>
    </div>
    <div class="question-section">
      <div v-for="question in questions" class="question">
        <span>{{ question }}</span>
      </div>
    </div>
    <div class="chat-section">
      <div style="padding: 8px 20px">
        <input
          type="text"
          placeholder="继续对话..."
          style="width: 100%; height: 100%"
        />
      </div>
      <div class="chat-tools">
        <i class="icon-add"></i>
        <i class="icon-voice"></i>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: "AgentRightColumn",
  data() {
    return {
      questions: [
        "实现一个函数，用于在点击剧情节时更新剧情选择树的显示。",
        "如何使用 `sd.Focus` 效果突出显示剧情节节点？",
        "除了 `sd.Tree` 和 `sd.Button`，还有哪些常用的SD动画组件？",
      ],
    };
  },
};
</script>

<style scoped>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: Arial, sans-serif;
  background-color: #f9f9f9;
}

#app {
  width: 600px;
  margin: 0 auto;
  padding: 20px;
  background-color: #fff;
  box-shadow: 0 0 5px rgba(0, 0, 0, 0.1);
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.title {
  font-size: 18px;
  font-weight: bold;
}

.tools i {
  margin-left: 10px;
  font-size: 20px;
  cursor: pointer;
}

.code-section {
  background-color: #f4f4f4;
  padding: 20px;
  margin-bottom: 20px;
}

.code-title {
  font-size: 16px;
  font-weight: bold;
  margin-bottom: 10px;
}

.code-content p {
  margin-bottom: 10px;
  line-height: 1.5;
}

.code-content code {
  background-color: #eaeaea;
  padding: 2px 5px;
  border-radius: 3px;
}

.info-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  font-size: 14px;
}

.info-item {
  display: flex;
  align-items: center;
}

.info-label {
  margin-left: 5px;
}

.question-section input {
  width: 100%;
  padding: 10px;
  margin-bottom: 10px;
  border: 1px solid #ddd;
  border-radius: 5px;
}

.chat-section input {
  flex: 1;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 5px;
}

.chat-tools i {
  margin-left: 10px;
  font-size: 20px;
  cursor: pointer;
}

.question {
  cursor: pointer;
  border: 1px solid rgba(68, 83, 130, 0.25);
  padding: 6px 16px;
  border-radius: 8px;
  margin-bottom: 8px;
}
.question:hover {
  background-color: #eee;
}
.question > span {
  color: rgba(15, 21, 40, 0.82);
}
</style>
