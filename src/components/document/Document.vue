<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import Introduction from './Introduction.vue'
import Lab from './Lab.vue'
import FAQ from './FAQ.vue'
import WorkflowIntro from './manual/workflow/WorkflowIntro.vue'
import WorkflowNodes from './manual/workflow/WorkflowNodes.vue'
import WorkflowOrchestration from './manual/workflow/WorkflowOrchestration.vue'
import WorkflowTest from './manual/workflow/WorkflowTest.vue'

const router = useRouter()
const expandedSections = ref<string[]>([])

const navItems = [
  {
    id: 'introduction',
    label: '平台简介',
    component: Introduction
  },
  {
    id: 'manual',
    label: '使用手册',
    children: [
      {
        id: 'kb',
        label: '知识库',
        children: [
          { id: 'kb-intro', label: '简介', component: Introduction },
          { id: 'kb-management', label: '管理', component: Introduction },
          { id: 'kb-usage', label: '使用', component: Introduction }
        ]
      },
      {
        id: 'workflow',
        label: '工作流',
        children: [
          { id: 'workflow-intro', label: '简介', component: WorkflowIntro },
          { id: 'workflow-nodes', label: '节点说明', component: WorkflowNodes },
          { id: 'workflow-orchestration', label: '编排节点', component: WorkflowOrchestration },
          { id: 'workflow-test', label: '试运行', component: WorkflowTest }
        ]
      },
      {
        id: 'agent',
        label: '智能体',
        children: [
          { id: 'agent-intro', label: '简介', component: Introduction },
          { id: 'agent-config', label: '配置工具', component: Introduction },
          { id: 'agent-debug', label: '对话调试', component: Introduction },
          { id: 'agent-publish', label: '发布与下架', component: Introduction }
        ]
      }
    ]
  },
  {
    id: 'lab',
    label: '动手实验室',
    component: Lab
  },
  {
    id: 'faq',
    label: '常见问题',
    component: FAQ
  }
]

const currentSection = ref('introduction')

const currentComponent = computed(() => {
  const findComponent = (items: any[]): any => {
    for (const item of items) {
      if (item.id === currentSection.value) {
        return item.component
      }
      if (item.children) {
        const found = findComponent(item.children)
        if (found) return found
      }
    }
    return null
  }

  return findComponent(navItems) || Introduction
})

function handleNavClick(item: any) {
  currentSection.value = item.id
  if (item.children) {
    toggleExpand(item.id)
  }
}

function toggleExpand(id: string) {
  const index = expandedSections.value.indexOf(id)
  if (index === -1) {
    expandedSections.value.push(id)
  } else {
    expandedSections.value.splice(index, 1)
  }
}

function goBack() {
  router.back()
}
</script>

<template>
  <div class="document-container">
    <div class="document-header">
      <div class="back-button" @click="goBack">
        <img src="https://api.iconify.design/material-symbols:arrow-back.svg" alt="返回" class="back-icon">
        <span>返回</span>
      </div>
      <h1>使用文档</h1>
    </div>

    <div class="document-content">
      <div class="document-nav">
        <div 
          v-for="(item, index) in navItems" 
          :key="index"
          class="nav-section"
        >
          <div 
            :class="['nav-item', { 
              active: currentSection === item.id,
              'nav-item-disabled': item.id === 'manual'
            }]"
            @click="item.id !== 'manual' && handleNavClick(item)"
          >
            {{ item.label }}
          </div>
          <div v-if="item.children" class="nav-children">
            <div 
              v-for="(child, childIndex) in item.children"
              :key="childIndex"
              class="nav-child-wrapper"
            >
              <div 
                :class="['nav-child', { active: currentSection === child.id }]"
                @click="handleNavClick(child)"
              >
                {{ child.label }}
                <img 
                  v-if="child.children"
                  :src="expandedSections.includes(child.id) ? 
                    'https://api.iconify.design/material-symbols:expand-less.svg' : 
                    'https://api.iconify.design/material-symbols:expand-more.svg'"
                  class="expand-icon"
                  @click.stop="toggleExpand(child.id)"
                >
              </div>
              <div 
                v-if="child.children && expandedSections.includes(child.id)"
                class="nav-grandchildren"
              >
                <div 
                  v-for="(grandChild, grandChildIndex) in child.children"
                  :key="grandChildIndex"
                  :class="['nav-grandchild', { active: currentSection === grandChild.id }]"
                  @click="handleNavClick(grandChild)"
                >
                  {{ grandChild.label }}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="document-main">
        <component :is="currentComponent"></component>
      </div>
    </div>
  </div>
</template>

<style scoped>
.document-container {
  min-height: 100vh;
  background-color: #f5f7fa;
}

.document-header {
  background: white;
  padding: 16px 24px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  display: flex;
  align-items: center;
  gap: 24px;
}

.back-button {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  color: #606266;
  transition: color 0.3s;
}

.back-button:hover {
  color: #409eff;
}

.back-icon {
  width: 24px;
  height: 24px;
}

h1 {
  margin: 0;
  color: #2c3e50;
  font-size: 24px;
}

.document-content {
  max-width: 1200px;
  margin: 24px auto;
  display: flex;
  gap: 24px;
  padding: 0 24px;
}

.document-nav {
  width: 240px;
  background: white;
  border-radius: 8px;
  padding: 16px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}

.nav-section {
  margin-bottom: 16px;
}

.nav-item {
  padding: 12px 16px;
  cursor: pointer;
  border-radius: 4px;
  color: #606266;
  transition: all 0.3s;
  font-weight: 500;
}

.nav-item:hover {
  background: #f5f7fa;
  color: #409eff;
}

.nav-item.active {
  background: #ecf5ff;
  color: #409eff;
}

.nav-item-disabled {
  cursor: default;
  color: #2c3e50;
  font-weight: 600;
}

.nav-item-disabled:hover {
  background: none;
  color: #2c3e50;
}

.nav-children {
  margin-left: 16px;
  margin-top: 8px;
}

.nav-child-wrapper {
  margin-bottom: 4px;
}

.nav-child {
  padding: 8px 16px;
  cursor: pointer;
  border-radius: 4px;
  color: #606266;
  transition: all 0.3s;
  font-size: 14px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.nav-child:hover {
  background: #f5f7fa;
  color: #409eff;
}

.nav-child.active {
  background: #ecf5ff;
  color: #409eff;
}

.expand-icon {
  width: 20px;
  height: 20px;
  opacity: 0.6;
  transition: transform 0.3s;
}

.nav-grandchildren {
  margin-left: 16px;
  margin-top: 4px;
}

.nav-grandchild {
  padding: 6px 16px;
  cursor: pointer;
  border-radius: 4px;
  color: #606266;
  transition: all 0.3s;
  font-size: 13px;
}

.nav-grandchild:hover {
  background: #f5f7fa;
  color: #409eff;
}

.nav-grandchild.active {
  background: #ecf5ff;
  color: #409eff;
}

.document-main {
  flex: 1;
  background: white;
  border-radius: 8px;
  padding: 24px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}
</style>