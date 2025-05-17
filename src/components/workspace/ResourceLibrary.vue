<script setup lang="ts">
import { onMounted, ref, computed, watch } from 'vue'
import router from '../../router'
import axios from "axios";

interface resource {
  id: number
  type: string
  name: string
  description: string
  icon: string
  createTime: string
  updateTime: string
  hover?: boolean
}

const resources = ref<resource[]> ([])
const KBDialog = ref(false) // 控制弹窗显示
const WFDialog = ref(false); // 控制工作流弹窗显示
const editDialog = ref(false); // 控制编辑弹窗显示

const KBForm = ref({
  type: "text", // 默认类型
  name: "",
  description: "",
  icon: null as File | null,
  iconPreview: ''
})

const WFForm = ref({
  name: '',
  description: '',
  icon: null as File | null,
  iconPreview: ''
})

const editForm = ref({
  id: 0,
  type: '',
  name: '',
  description: '',
  icon: null as File | null,
  iconPreview: ''
})

const defaultIcons = {
  text: 'http://122.9.33.84:8000/media/kb_icons/Text.svg', // 文本知识库默认图标
  table: 'http://122.9.33.84:8000/media/kb_icons/Table.svg', // 表格知识库默认图标
  picture: 'http://122.9.33.84:8000/media/kb_icons/Picture.svg', // 图像知识库默认图标
  workflow: 'http://122.9.33.84:8000/media/workflow_icons/defaultWorkFlow.svg'
}

onMounted(() => {
  getKnowledgeBases()
  getWorkflows()
})

function getKnowledgeBases() {
  axios({
    method: 'get',
    url: '/rl/getKnowledgeBases',
    params: {
      uid: localStorage.getItem('LingXi_uid')
    },
  }).then(function (response) {
    if (response.data.code === 0) {
      resources.value = resources.value.concat(response.data.knowledgeBases)
    } else {
      console.log(response.data.message)
    }
  })
}

async function getWorkflows() {
  try {
    const uid = localStorage.getItem('LingXi_uid')
    if (!uid) {
      console.error('用户ID不存在')
      return
    }
    const response = await axios({
      method: 'get',
      url: '/workflow/fetchAll',
      params: {
        uid
      }
    })
    if (response.data.code === 0) {
      resources.value = resources.value.concat(
          response.data.workflows.map((item: any) => ({
            id: item.id,
            type: 'workflow',
            name: item.name,
            description: item.description,
            icon: item.icon,
            updateTime: item.updateTime,
            hover: false
          }))
      )
    } else {
      console.log(response.data.message)
    }
  } catch (error) {
    console.error('获取工作流列表失败:', error)
  }
}

function createKB() {
  KBDialog.value = true
  if (!KBForm.value.iconPreview) {
    KBForm.value.iconPreview = defaultIcons[KBForm.value.type as keyof typeof defaultIcons]
  }
}

// 监听知识库类型变化，动态设置iconPreview
watch(
  () => KBForm.value.type,
  (newType) => {
    // 仅当用户未上传图片时才切换预览
    if (!KBForm.value.icon) {
      KBForm.value.iconPreview = defaultIcons[newType as keyof typeof defaultIcons]
    }
  }
)

function handleKBIcon(event: Event) {
  const input = event.target as HTMLInputElement
  if (input.files && input.files[0]) {
    const file = input.files[0]

    // 验证文件大小和类型
    if (file.size > 5 * 1024 * 1024) {
      ElMessage.warning("图片大小不能超过5MB")
      return
    }

    const reader = new FileReader()
    reader.onload = (e) => {
      KBForm.value.iconPreview = e.target?.result as string // 设置预览 URL
    }
    KBForm.value.icon = file // 将文件存储到 baseInfo.icon
    reader.readAsDataURL(file) // 读取文件内容
  }
}

function submitKB() {
  if (!KBForm.value.name) {
    ElMessage.warning('知识库名称不能为空')
    return
  }
  const formData = new FormData()
  formData.append("uid", localStorage.getItem('LingXi_uid') as string)
  formData.append("kb_type", KBForm.value.type)
  formData.append("kb_name", KBForm.value.name)
  formData.append("kb_description", KBForm.value.description)
  if (KBForm.value.icon) {
    formData.append("kb_icon", KBForm.value.icon)
  }

  axios({
    method: "post",
    url: "/kb/create",
    data: formData,
    headers: {
      "Content-Type": "multipart/form-data",
    },
  }).then(function (response) {
    if (response.data.code === 0) {
      ElMessage.success(response.data.message)
      router.push("/workspace/" + KBForm.value.type + 'Base/' + response.data.kb_id)
    } else {
      ElMessage.error(response.data.message)
    }
  })
  KBDialog.value = false // 关闭弹窗
}

function goToResource(resource: resource) {
  router.push({
    path: `/workspace/${resource.type}/${resource.id}`,
    query: {
      uid: localStorage.getItem('LingXi_uid'),
    }
  })
}

function createWF() {
  WFForm.value.iconPreview = defaultIcons.workflow
  WFDialog.value = true;
}

function handleWFIcon(event: Event) {
  const input = event.target as HTMLInputElement
  if (input.files && input.files[0]) {
    const file = input.files[0]
    // 验证文件大小和类型
    if (file.size > 2 * 1024 * 1024) {
      ElMessage.warning('图片大小不能超过2MB')
      return;
    }
    const reader = new FileReader()
    reader.onload = (e) => {
      WFForm.value.iconPreview = e.target?.result as string
    }
    WFForm.value.icon = file
    reader.readAsDataURL(file)
  }
}

async function submitWF() {
  if (!WFForm.value.name) {
    ElMessage.warning('工作流名称不能为空')
    return
  }
  const formData = new FormData()
  if (WFForm.value.icon) {
    formData.append('icon', WFForm.value.icon)
  }
  formData.append('description', WFForm.value.description)
  formData.append('name', WFForm.value.name)
  formData.append('uid', localStorage.getItem('LingXi_uid') as string)
  try {
    const response = await axios({
      method: 'post',
      url: 'workflow/create',
      data: formData,
      headers: {
        'Content-Type': 'multipart/form-data',
      }
    })
    if (response.data.code === 0) {
      console.log(response.data)
      const workflow_id = response.data.workflow_id
      localStorage.removeItem('workflowNodes')
      localStorage.removeItem('connections')
      WFForm.value.icon = null
      await router.push({
        path: `/workspace/workflow/${workflow_id}`,
        query: {
          uid: localStorage.getItem('LingXi_uid'),
        }
      })
    } else {
      console.log(response.data.message)
    }
  } catch (error) {
    console.error("Error:", error)
  }
}

const deleteDialog = ref(false); // 控制删除确认弹窗显示
const deleteTarget = ref<{ id: number; type: string , name: string} | null>(null); // 待删除的资源信息

// 打开删除确认弹窗
function openDeleteDialog(id: number, resourceType: string) {
  deleteTarget.value = { id, type: resourceType, name: resources.value.find(resource => resource.id === id)?.name || '' };
  deleteDialog.value = true;
}

// 确认删除资源
function handleDelete() {
  if (!deleteTarget.value) return;

  axios({
    method: "post",
    url: "/rl/delete",
    data: {
      uid: localStorage.getItem('LingXi_uid'),
      resource_id: deleteTarget.value.id,
      resource_type: deleteTarget.value.type,
    },
  }).then(function (response) {
    if (response.data.code === 0) {
      ElMessage.success(response.data.message)
      resources.value = []
      getKnowledgeBases()
      getWorkflows()
      deleteDialog.value = false
      deleteTarget.value = null
    } else {
      ElMessage.error(response.data.message)
      deleteDialog.value = false
      deleteTarget.value = null
    }
  })
}

// 打开编辑弹窗
function openEditDialog(resource: resource) {
  editForm.value.id = resource.id;
  editForm.value.type = resource.type;
  editForm.value.name = resource.name;
  editForm.value.description = resource.description;
  editForm.value.iconPreview = 'http://122.9.33.84:8000' + resource.icon;
  editForm.value.icon = null;
  editDialog.value = true;
}

// 处理编辑图标上传
function handleEditIcon(event: Event) {
  const input = event.target as HTMLInputElement;
  if (input.files && input.files[0]) {
    const file = input.files[0];

    // 验证文件大小和类型
    if (file.size > 5 * 1024 * 1024) {
      ElMessage.warning("图片大小不能超过5MB");
      return;
    }

    const reader = new FileReader();
    reader.onload = (e) => {
      editForm.value.iconPreview = e.target?.result as string; // 设置预览 URL
    };
    editForm.value.icon = file; // 将文件存储到 editForm.icon
    reader.readAsDataURL(file); // 读取文件内容
  }
}

// 提交编辑表单
function submitEdit() {
  const formData = new FormData();
  formData.append("uid", localStorage.getItem('LingXi_uid') as string);
  formData.append("resource_id", editForm.value.id.toString());
  formData.append("resource_type", resources.value.find(resource => resource.id === editForm.value.id)?.type || '');
  formData.append("name", editForm.value.name);
  formData.append("description", editForm.value.description);
  if (editForm.value.icon) {
    formData.append("icon", editForm.value.icon);
  }
  axios({
    method: "post",
    url: "/rl/edit",
    data: formData,
    headers: {
      "Content-Type": "multipart/form-data",
    },
  }).then(function (response) {
    if (response.data.code === 0) {
      ElMessage.success(response.data.message);
      resources.value = [];
      getKnowledgeBases();
      getWorkflows();
      editDialog.value = false;
    } else {
      ElMessage.error(response.data.message);
    }
  });
}

const filterCriteria = ref({
  sortBy: "name", // 排序方式
  type: "all", // 资源类型
  search: "", // 搜索关键字
})

// 筛选资源
const filteredResources = computed(() => {
  let filtered = [...resources.value];

  // 按类型筛选
  if (filterCriteria.value.type !== "all") {
    if (filterCriteria.value.type === "knowledgeBase") {
      filtered = filtered.filter(
          (resource) =>
              resource.type === "textBase" ||
              resource.type === "tableBase" ||
              resource.type === "pictureBase"
      );
    } else {
      filtered = filtered.filter(
          (resource) => resource.type === filterCriteria.value.type
      );
    }
  }

  // 按搜索关键字筛选
  if (filterCriteria.value.search.trim() !== "") {
    filtered = filtered.filter((resource) =>
        resource.name.toLowerCase().includes(filterCriteria.value.search.trim().toLowerCase())
    );
  }

  // 按排序方式排序
  if (filterCriteria.value.sortBy === "updateTime") {
    filtered.sort((a, b) => new Date(b.updateTime).getTime() - new Date(a.updateTime).getTime());
  } else if (filterCriteria.value.sortBy === "createTime") {
    filtered.sort((a, b) => new Date(a.createTime).getTime() - new Date(b.createTime).getTime());
  } else if (filterCriteria.value.sortBy === "name") {
    filtered.sort((a, b) => a.name.localeCompare(b.name));
  }

  return filtered;
})
</script>

<template>
  <div class="content">
    <!-- 顶部标题栏 -->
    <div class="header">
      <h2>资源库</h2>
      <el-dropdown>
        <button class="create-btn">
          <svg viewBox="0 0 24 24" fill="currentColor" width="20" height="20">
            <path d="M19 13h-6v6h-2v-6H5v-2h6V5h2v6h6v2z"/>
          </svg>
          创建资源
        </button>
        <template #dropdown>
          <el-dropdown-menu>
            <div>
              <el-dropdown-item class="dropdown-item" @click="createWF">
                <svg viewBox="0 0 24 24" fill="currentColor" width="16" height="16">
                  <path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm0 16H5V5h14v14zM7 10h2v7H7zm4-3h2v10h-2zm4 6h2v4h-2z"/>
                </svg>
                <span>工作流</span>
              </el-dropdown-item>
            </div>
            <el-dropdown-item @click="createKB">
              <svg viewBox="0 0 24 24" fill="currentColor" width="16" height="16">
                <path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm0 16H5V5h14v14zM7 10h2v7H7zm4-3h2v10h-2zm4 6h2v4h-2z"/>
              </svg>
              <span>知识库</span>
            </el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>
    </div>

    <!-- 筛选栏 -->
    <div class="filter-bar">
      <select class="filter-select" v-model="filterCriteria.sortBy">
        <option value="name">按名称排序</option>
        <option value="updateTime">按编辑时间排序</option>
        <option value="createTime">按创建时间排序</option>
      </select>
      <select class="filter-select" v-model="filterCriteria.type">
        <option value="all">全部</option>
        <option value="workflow">工作流</option>
        <option value="knowledgeBase">知识库</option>
      </select>
      <div class="search-box">
        <svg viewBox="0 0 24 24" fill="currentColor" width="16" height="16">
          <path d="M15.5 14h-.79l-.28-.27C15.41 12.59 16 11.11 16 9.5 16 5.91 13.09 3 9.5 3S3 5.91 3 9.5 5.91 16 9.5 16c1.61 0 3.09-.59 4.23-1.57l.27.28v.79l5 4.99L20.49 19l-4.99-5zm-6 0C7.01 14 5 11.99 5 9.5S7.01 5 9.5 5 14 7.01 14 9.5 11.99 14 9.5 14z"/>
        </svg>
        <input type="text" placeholder="搜索资源..." v-model="filterCriteria.search" />
      </div>
    </div>

    <!-- 资源列表 -->
    <div class="resource-list">
      <div
          v-for="resource in filteredResources"
          :key="resource.id"
          class="resource-card"
          @click="goToResource(resource)"
          @mouseover="resource.hover = true"
          @mouseleave="resource.hover = false"
      >
        <div class="resource-icon">
          <img :src="'http://122.9.33.84:8000' + resource.icon" :alt="resource.name">
          <div class="resource-type">{{ resource.type }}</div>
        </div>
        <div class="resource-info">
          <h3>{{ resource.name }}</h3>
          <p>{{ resource.description }}</p>
          <div class="resource-meta">
            <span class="update-time">
              {{ filterCriteria.sortBy === 'createTime' ? '创建时间：' : '编辑时间：' }}
              {{ filterCriteria.sortBy === 'createTime' ? resource.createTime : resource.updateTime }}
            </span>
          </div>
        </div>
        <!-- 编辑按钮 -->
        <div
          v-if="resource.hover"
          class="edit-icon"
          @click.stop="openEditDialog(resource)"
          title="编辑"
        >
          <svg viewBox="0 0 24 24" fill="currentColor" width="20" height="20">
            <path d="M3 17.25V21h3.75l11.06-11.06-3.75-3.75L3 17.25zM20.71 7.04a1.003 1.003 0 0 0 0-1.42l-2.34-2.34a1.003 1.003 0 0 0-1.42 0l-1.83 1.83 3.75 3.75 1.84-1.82z"/>
          </svg>
        </div>
        <!-- 删除按钮 -->
        <div
            v-if="resource.hover"
            class="delete-icon"
            @click.stop="openDeleteDialog(resource.id, resource.type)"
            title="删除"
        >
          <svg viewBox="0 0 24 24" fill="currentColor" width="20" height="20">
            <path d="M16 9v10H8V9h8m-1.5-6h-5l-1 1H5v2h14V4h-3.5l-1-1M18 7H6v12c0 1.1.9 2 2 2h8c1.1 0 2-.9 2-2V7z"/>
          </svg>
        </div>
      </div>
    </div>

    <!-- 知识库创建弹窗 -->
    <el-dialog v-model="KBDialog" title="创建知识库" width="500px" class="custom-dialog">
      <div class="dialog-body">
        <!-- 类型 -->
        <div class="form-row">
          <label class="form-label">类型</label>
          <el-select v-model="KBForm.type" placeholder="请选择类型" class="form-input">
            <el-option label="文本" value="text"></el-option>
            <el-option label="表格" value="table"></el-option>
            <el-option label="图像" value="picture"></el-option>
          </el-select>
        </div>

        <!-- 名称 -->
        <div class="form-row">
          <label class="form-label">名称 <span class="required">*</span></label>
          <el-input v-model="KBForm.name" placeholder="请输入知识库名称" class="form-input" />
          <span class="char-count">{{ KBForm.name.length }}/20</span>
        </div>

        <!-- 描述 -->
        <div class="form-row">
          <label class="form-label">描述</label>
          <el-input
              v-model="KBForm.description"
              type="textarea"
              placeholder="请输入知识库描述"
              rows="4"
              maxlength="200"
              show-word-limit
              class="form-input"
          />
        </div>

        <!-- 上传图标 -->
        <div class="form-row">
          <label class="form-label">图标</label>
          <div class="image-upload">
            <div class="upload-preview" v-if="KBForm.iconPreview">
              <img :src="KBForm.iconPreview" alt="预览图" />
            </div>
            <div class="upload-button" :class="{ 'has-image': WFForm.icon }">
              <input type="file" accept="image/*" @change="handleKBIcon" class="file-input" />
              <svg viewBox="0 0 24 24" fill="currentColor" width="24" height="24">
                <path d="M19 7v2.99s-1.99.01-2 0V7h-3s.01-1.99 0-2h3V2h2v3h3v2h-3zm-3 4V8h-3V5H5c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2v-8h-3zM5 19l3-4 2 3 3-4 4 5H5z"/>
              </svg>
              <span>更换图标</span>
            </div>
          </div>
        </div>
      </div>

      <template #footer>
        <el-button @click="KBDialog = false">取消</el-button>
        <el-button type="primary" @click="submitKB">创建</el-button>
      </template>
    </el-dialog>

    <!-- 工作流创建弹窗 -->
    <el-dialog v-model="WFDialog" title="创建工作流" width="500px" class="custom-dialog">
      <div class="dialog-body">
        <!-- 名称 -->
        <div class="form-row">
          <label class="form-label">名称 <span class="required">*</span></label>
          <el-input v-model="WFForm.name" placeholder="给工作流起一个独一无二的名字" maxlength="20" class="form-input" />
          <span class="char-count">{{ WFForm.name.length }}/20</span>
        </div>

        <!-- 描述 -->
        <div class="form-row">
          <label class="form-label">功能介绍</label>
          <el-input
            v-model="WFForm.description"
            type="textarea"
            placeholder="介绍工作流的功能，将会展示给工作流的用户"
            maxlength="200"
            show-word-limit
            :rows="4"
            class="form-input"
          />
        </div>

        <!-- 图片上传 -->
        <div class="form-row">
          <label class="form-label">图标</label>
          <div class="image-upload">
            <div class="upload-preview" v-if="WFForm.iconPreview">
              <img :src="WFForm.iconPreview" alt="预览图" />
            </div>
            <div class="upload-button" :class="{ 'has-image': WFForm.icon }">
              <input type="file" accept="image/*" @change="handleWFIcon" class="file-input" />
              <svg viewBox="0 0 24 24" fill="currentColor" width="24" height="24">
                <path d="M19 7v2.99s-1.99.01-2 0V7h-3s.01-1.99 0-2h3V2h2v3h3v2h-3zm-3 4V8h-3V5H5c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2v-8h-3zM5 19l3-4 2 3 3-4 4 5H5z"/>
              </svg>
              <span>更换图标</span>
            </div>
          </div>
        </div>
      </div>

      <template #footer>
        <el-button @click="WFDialog = false">取消</el-button>
        <el-button type="primary" @click="submitWF">创建</el-button>
      </template>
    </el-dialog>

    <!-- 删除确认弹窗 -->
    <el-dialog v-model="deleteDialog" title="确认删除" width="400px" class="custom-dialog">
      <div class="dialog-body">
        <p>确定要删除"{{ deleteTarget?.name }}"吗？此操作不可撤销。</p>
      </div>
      <template #footer>
        <el-button @click="deleteDialog = false">取消</el-button>
        <el-button type="danger" @click="handleDelete">删除</el-button>
      </template>
    </el-dialog>

    <!-- 编辑资源弹窗 -->
    <el-dialog v-model="editDialog" title="编辑资源" width="500px" class="custom-dialog">
      <div class="dialog-body">
        <div class="form-row">
          <label class="form-label">名称 <span class="required">*</span></label>
          <el-input v-model="editForm.name" placeholder="请输入资源名称" maxlength="20" class="form-input" />
          <span class="char-count">{{ editForm.name.length }}/20</span>
        </div>
        <div class="form-row">
          <label class="form-label">描述</label>
          <el-input
            v-model="editForm.description"
            type="textarea"
            placeholder="请输入资源描述"
            maxlength="200"
            show-word-limit
            rows="4"
            class="form-input"
          />
        </div>
        <div class="form-row">
          <label class="form-label">图标</label>
          <div class="image-upload">
            <div class="upload-preview" v-if="editForm.iconPreview">
              <img :src="editForm.iconPreview" alt="图标预览" />
            </div>
            <div class="upload-button" :class="{ 'has-image': editForm.iconPreview }">
              <input type="file" accept="image/*" @change="handleEditIcon" class="file-input"/>
              <svg viewBox="0 0 24 24" fill="currentColor" width="24" height="24">
                <path d="M19 7v2.99s-1.99.01-2 0V7h-3s.01-1.99 0-2h3V2h2v3h3v2h-3zm-3 4V8h-3V5H5c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2v-8h-3zM5 19l3-4 2 3 3-4 4 5H5z"/>
              </svg>
              <span>更换图标</span>
            </div>
          </div>
        </div>
      </div>
      <template #footer>
        <el-button @click="editDialog = false">取消</el-button>
        <el-button type="primary" @click="submitEdit">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
.content {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.header h2 {
  margin: 0;
  color: #2c3e50;
  font-size: 24px;
}

.create-dropdown {
  position: relative;
}

.create-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background: #2c3e50;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.create-btn:hover {
  background: #34495e;
}

.filter-bar {
  display: flex;
  gap: 16px;
  margin-bottom: 20px;
  align-items: center;
}

.filter-select {
  padding: 8px 12px;
  border: 1px solid #e9ecef;
  border-radius: 6px;
  background: white;
  color: #2c3e50;
  cursor: pointer;
}

.search-box {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  background: white;
  border: 1px solid #e9ecef;
  border-radius: 6px;
  flex: 1;
  max-width: 300px;
}

.search-box input {
  border: none;
  outline: none;
  width: 100%;
  color: #2c3e50;
}

.resource-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
}

.resource-card {
  height: 120px;
  background: white;
  border-radius: 12px;
  padding: 16px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  transition: all 0.3s ease;
  display: flex;
  gap: 16px;
  cursor: pointer;
  position: relative;
  /* 新增：为底部绝对定位留空间 */
  overflow: visible;
}

.resource-icon {
  position: relative;
  width: 80px;
  height: 80px;
  flex-shrink: 0;
}

.resource-icon img {
  width: 100%;
  height: 100%;
  border-radius: 50%;
  object-fit: cover;
}

.resource-type {
  position: absolute;
  bottom: 0;
  right: 0;
  background: #2c3e50;
  color: white;
  padding: 2px 6px;
  border-radius: 10px;
  font-size: 10px;
}

.resource-info {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  /* 新增：为底部留空间 */
  position: relative;
  height: 100%;
}

.resource-info h3 {
  margin: 0 0 8px 0;
  color: #2c3e50;
  font-size: 16px;
}

.resource-info p {
  margin: 0;
  color: #666;
  font-size: 13px;
  line-height: 1.5;
  display: -webkit-box;
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-overflow: ellipsis;
  -webkit-line-clamp: 3; /* 限制描述显示三行 */
  line-clamp: 3; /* Standard property for compatibility */
}

.resource-meta {
  display: flex;
  justify-content: flex-end;
  /* 固定在底部 */
  position: absolute;
  left: 0;
  right: 0;
  bottom: 0;
  margin-top: 0;
  background: transparent;
}

.update-time {
  color: #95a5a6;
  font-size: 11px;
}

.delete-icon {
  position: absolute;
  bottom: 8px;
  right: 8px;
  background: white;
  border-radius: 50%;
  padding: 4px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  cursor: pointer;
  transition: all 0.3s ease;
}

.delete-icon:hover {
  background: #f5f5f5;
}

.edit-icon {
  position: absolute;
  bottom: 8px;
  right: 40px;
  background: white;
  border-radius: 50%;
  padding: 4px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  cursor: pointer;
  transition: all 0.3s ease;
}

.edit-icon:hover {
  background: #f5f5f5;
}

/* 自定义弹窗样式 */
.custom-dialog {
  border-radius: 12px;
  overflow: hidden;
}

.custom-dialog .el-dialog__header {
  background-color: #f5f7fa;
  border-bottom: 1px solid #ebeef5;
  font-size: 18px;
  font-weight: bold;
  color: #2c3e50;
}

.dialog-body {
  padding: 20px 24px;
  display: flex;
  flex-direction: column;
  gap: 16px; /* 表单项之间的间距 */
}

.form-row {
  display: flex;
  flex-direction: column;
}

.form-label {
  margin-bottom: 8px;
  font-size: 14px;
  color: #606266;
}

.form-input {
  width: 100%;
  border-radius: 6px;
}

.icon-upload {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
}

.icon-preview {
  width: 100px;
  height: 100px;
  border-radius: 50%;
  object-fit: cover;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.image-upload {
  display: flex;
  align-items: center;
  gap: 16px;
}

.upload-preview {
  width: 100px;
  height: 100px;
  border-radius: 8px;
  overflow: hidden;
  border: 1px solid #e9ecef;
}

.upload-preview img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.upload-button {
  position: relative;
  width: 120px;
  height: 100px;
  border: 2px dashed #e9ecef;
  border-radius: 8px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.upload-button:hover {
  border-color: #3498db;
  color: #3498db;
}

.upload-button.has-image {
  width: 100px;
}

.file-input {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  opacity: 0;
  cursor: pointer;
}

.upload-button svg {
  color: #95a5a6;
}

.upload-button:hover svg {
  color: #3498db;
}

.upload-button span {
  font-size: 12px;
  color: #95a5a6;
}

.upload-button:hover span {
  color: #3498db;
}

.required {
  color: red;
}

.char-count {
  text-align: right;
  margin-top: 4px;
  font-size: 12px;
  color: #95a5a6;
}

.file-input {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  opacity: 0;
  cursor: pointer;
}
</style>