<script setup lang="ts">
import { ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'

const router = useRouter()
const route = useRoute()

const menuItems = [
  {
    title: '用户管理',
    icon: 'https://api.iconify.design/material-symbols:manage-accounts.svg',
    path: '/admin/userManage'
  },
  {
    title: '智能体审核',
    icon: 'https://api.iconify.design/material-symbols:rate-review.svg',
    path: '/admin/reviewAgent'
  },
  {
    title: '举报处理',
    icon: 'https://api.iconify.design/material-symbols:report.svg',
    path: '/admin/reportAgent'
  },
  {
    title: '公告发布',
    icon: 'https://api.iconify.design/material-symbols:campaign.svg',
    path: '/admin/publishAnno'
  }
]

const isCollapsed = ref(false)
</script>

<template>
  <div class="admin-layout">
    <router-view></router-view>
  </div>
</template>

<style scoped>
.admin-layout {
  flex: 1;
  background: #f5f7fa;
  padding: 20px;
  overflow-y: auto;
}

/* 滚动条样式 */
::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}

::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}
</style> 