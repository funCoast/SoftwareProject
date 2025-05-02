<script setup lang="ts">
import { ref } from "vue";
import router from "../../router";

interface RowData {
  [key: string]: any; // 动态字段
}

const tableData = ref<RowData[]>([]); // 表格数据
const tableColumns = ref<{ prop: string; label: string; width?: number }[]>([]); // 表格列配置
let originalValue = ""; // 用于存储单元格的原始值

// 模拟从后端获取数据
const fetchTableData = () => {
  // 模拟后端返回的列配置
  tableColumns.value = [
    { prop: "id", label: "ID", width: 50 },
    { prop: "name", label: "名称" },
    { prop: "description", label: "描述" },
    { prop: "createdAt", label: "创建时间", width: 150 },
    { prop: "updatedAt", label: "更新时间", width: 150 },
  ];

  // 模拟后端返回的表格数据
  tableData.value = [
    { id: 1, name: "行1", description: "这是第一行的描述", createdAt: "2023-10-01", updatedAt: "2023-10-02" },
    { id: 2, name: "行2", description: "这是第二行的描述", createdAt: "2023-10-03", updatedAt: "2023-10-04" },
    { id: 3, name: "行3", description: "这是第三行的描述", createdAt: "2023-10-05", updatedAt: "2023-10-06" },
    { id: 4, name: "行4", description: "这是第四行的描述", createdAt: "2023-10-07", updatedAt: "2023-10-08" },
    { id: 5, name: "行5", description: "这是第五行的描述", createdAt: "2023-10-09", updatedAt: "2023-10-10" },
  ];
};

// 记录单元格的原始值
const handleFocus = (value: string) => {
  originalValue = value;
};

// 处理失去焦点事件
const handleBlur = (row: RowData, prop: string, index: number) => {
  const newValue = row[prop];
  if (originalValue !== newValue) {
    updateBackend(row, prop, index);
  }
};

// 模拟更新到后端的方法
const updateBackend = (row: RowData, prop: string, index: number) => {
  console.log(`更新第 ${index + 1} 行，字段 ${prop} 的值为：${row[prop]}`);
  // 在这里调用后端接口，例如：
  // axios.post('/api/update', { rowIndex: index, id: row.id, field: prop, value: row[prop] });
};

// 初始化数据
fetchTableData();
</script>

<template>
  <div class="content">
    <!-- 顶部标题栏 -->
    <div class="topBar">
      <img src="../../assets/icons/Back.svg" alt="返回" class="backIcon" @click="router.push('/workspace/resourcelibrary')" />
      <h2>表格知识库</h2>
      <p class="subtitle">行数量：{{ tableData.length }}</p>
      <button class="add-btn" type="button" @click="router.push('/workspace/createPicture')">
        添加数据
      </button>
    </div>

    <!-- 表格展示区域 -->
    <el-table :data="tableData" stripe class="data-table">
      <!-- 动态生成表格列 -->
      <el-table-column
          v-for="column in tableColumns"
          :key="column.prop"
          :prop="column.prop"
          :label="column.label"
          :width="column.width"
      >
        <!-- 可编辑单元格 -->
        <template #default="scope">
          <input
              v-model="scope.row[column.prop]"
              type="text"
              class="editable-input"
              placeholder="请输入内容"
              @focus="handleFocus(scope.row[column.prop])"
              @blur="handleBlur(scope.row, column.prop, scope.$index)"
          />
        </template>
      </el-table-column>
    </el-table>
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

.data-table {
  margin-top: 20px;
  width: 100%;
  overflow: hidden;
}

/* 可编辑输入框样式 */
.editable-input {
  border: none;
  background: transparent;
  width: 100%;
  padding: 0;
  font-size: 14px;
  color: #333;
}

.editable-input:focus {
  outline: none;
  border-bottom: 1px solid #ccc;
}
</style>