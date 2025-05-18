<script setup lang="ts">
import { computed, ref } from "vue"
import axios from "axios"
import router from "../../router"

interface RowData {
  [key: string]: any // 动态字段
}

const tableData = ref<RowData[]>([]) // 表格数据
const tableColumns = ref<string[]>([]) // 表格列配置，只包含列名称
let originalValue = "" // 用于存储单元格的原始值
const selectedRows = ref<number[]>([]) // 存储选中行的索引
const haveSelected = computed(() => {
  return (selectedRows.value.length > 0)
}) // 判断是否有选中行
const newRowIndexes = ref<number[]>([]) // 用于存储新增行的序号

const getData = () => {
  axios({
    method: 'get',
    url: '/kb/getTables',
    params: {
      uid: localStorage.getItem('LingXi_uid'),
      kb_id: router.currentRoute.value.params.id,
    },
  }).then(function (response) {
    if (response.data.code === 0) {
      const table = response.data // 获取表格数据
      tableColumns.value = table.columns // 设置表格列配置
      tableData.value = table.data // 设置表格数据
    } else {
      console.log(response.data.message)
    }
  })
}

// 记录单元格的原始值
const handleFocus = (value: string) => {
  originalValue = value
}

// 处理失去焦点事件
const handleBlur = (row: RowData, prop: string, index: number) => {
  const newValue = row[prop]
  if (originalValue !== newValue) {
    if (newRowIndexes.value.includes(index)) {
      // 如果是新增行，调用新增接口
      uploadNewRow(row, index)
    } else {
      // 如果是已有行，调用更新接口
      updateTable(row, prop, index)
    }
  }
}

function goToUploadPage() {
  router.push(router.currentRoute.value.path + "/upload")
}

const updateTable = (row: RowData, prop: string, index: number) => {
  axios({
    method: 'post',
    url: '/kb/updateTable',
    data: {
      uid: localStorage.getItem('LingXi_uid'),
      kb_id: router.currentRoute.value.params.id,
      rowIndex: index,  // 更新的行索引
      prop: prop,       // 更新的字段
      value: row[prop], // 更新的值
    },
  }).then(function (response) {
    if (response.data.code === 0) {
      ElMessage.success("更新成功！")
    } else {
      ElMessage.error("更新失败！" + response.data.message)
    }
  })
}

// 新增一行空白数据
const addRow = () => {
  const newRow: RowData = {} // 创建一个空白行
  tableColumns.value.forEach((column) => {
    newRow[column] = "" // 初始化每列为空字符串
  })
  tableData.value.push(newRow) // 将新行添加到表格数据中
  newRowIndexes.value.push(tableData.value.length - 1) // 记录新增行的序号
  console.log("新增行序号：", newRowIndexes.value)
}

const uploadNewRow = (row: RowData, index: number) => {
  axios({
    method: "post",
    url: "/kb/addTableRow",
    data: {
      uid: localStorage.getItem('LingXi_uid'),
      kb_id: router.currentRoute.value.params.id,
      rowData: row, // 新增行的数据
    },
  }).then((response) => {
    if (response.data.code === 0) {
      ElMessage.success("新增行已上传！")
      newRowIndexes.value = newRowIndexes.value.filter((i) => i !== index) // 移除已上传的行序号
    } else {
      ElMessage.error("新增行上传失败！" + response.data.message)
    }
  })
}

const deleteSelectedRows = () => {
  axios({
    method: "post",
    url: "/kb/deleteTableRows",
    data: {
      uid: localStorage.getItem('LingXi_uid'),
      kb_id: router.currentRoute.value.params.id,
      rows: selectedRows.value, // 选中行的索引
    },
  }).then((response) => {
    if (response.data.code === 0) {
      ElMessage.success("删除成功！")
      selectedRows.value = []
      getData()
    } else {
      ElMessage.error("删除失败！" + response.data.message)
    }
  })
}

// 更新选中行的索引
const handleSelectionChange = (selectedRowsData: RowData[]) => {
  selectedRows.value = selectedRowsData.map((row) => tableData.value.indexOf(row))
}

// 初始化数据
getData()
</script>

<template>
  <div class="content">
    <!-- 顶部标题栏 -->
    <div class="topBar">
      <img src="../../assets/icons/Back.svg" alt="返回" class="backIcon" @click="router.push('/workspace/resourcelibrary')" />
      <h2>表格知识库</h2>
      <p class="subtitle">行数量：{{ tableData.length }}</p>
      <button class="add-btn" type="button" @click="goToUploadPage">
        添加数据
      </button>
    </div>

    <!-- 表格展示区域 -->
    <el-table
      :data="tableData"
      stripe
      class="data-table"
      @selection-change="handleSelectionChange"
    >
      <!-- 勾选框列 -->
      <el-table-column type="selection" width="55" />

      <!-- 动态生成表格列 -->
      <el-table-column
        v-for="column in tableColumns"
        :key="column"
        :prop="column"
        :label="column"
      >
        <!-- 可编辑单元格 -->
        <template #default="scope">
          <input
            v-model="scope.row[column]"
            type="text"
            class="editable-input"
            placeholder="请输入内容"
            @focus="handleFocus(scope.row[column])"
            @blur="handleBlur(scope.row, column, scope.$index)"
          />
        </template>
      </el-table-column>
    </el-table>

    <!-- 新增一行按钮 -->
    <div class="add-row-container">
      <el-button type="success" @click="addRow">新增一行</el-button>
      <el-button type="danger" @click="deleteSelectedRows" :disabled="!haveSelected">删除选中行</el-button>
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

/* 表格列标题自适应宽度 */
.el-table th .cell {
  white-space: nowrap; /* 防止列标题换行 */
  text-overflow: ellipsis; /* 超出部分显示省略号 */
  overflow: hidden;
}

.el-table td .cell {
  white-space: nowrap; /* 防止单元格内容换行 */
  text-overflow: ellipsis; /* 超出部分显示省略号 */
  overflow: hidden;
}

.add-row-container {
  display: flex;
  margin-top: 20px;
}

.add-row-btn {
  height: 40px;
  padding: 8px 16px;
  background: #4caf50;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
}

.add-row-btn:hover {
  background: #45a049;
}

.delete-row-btn {
  height: 40px;
  padding: 8px 16px;
  background: #f44336;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  margin-left: 10px;
}

.delete-row-btn:hover {
  background: #e53935;
}
</style>