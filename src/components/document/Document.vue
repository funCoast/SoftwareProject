<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import WorkflowIntro from './manual/workflow/WorkflowIntro.vue'
import WorkflowOrchestration from './manual/workflow/WorkflowOrchestration.vue'
import WorkflowTest from './manual/workflow/WorkflowTest.vue'
import BasicFAQ from "@/components/document/manual/FAQ/BasicFAQ.vue"
import UseFAQ from "@/components/document/manual/FAQ/UseFAQ.vue"
import OtherFAQ from "@/components/document/manual/FAQ/OtherFAQ.vue"
import Product from "@/components/document/manual/introduction/Product.vue"
import AviationQA from "@/components/document/manual/lab/AviationQA.vue"
import RecommendAssistant from "@/components/document/manual/lab/RecommendAssistant.vue"
import WeatherSuit from "@/components/document/manual/lab/WeatherSuit.vue"
import Agent from "@/components/document/manual/workflow/nodes/Agent.vue"
import Classifier from "@/components/document/manual/workflow/nodes/Classifier.vue"
import Code from "@/components/document/manual/workflow/nodes/Code.vue"
import Condition from "@/components/document/manual/workflow/nodes/Condition.vue"
import End from "@/components/document/manual/workflow/nodes/End.vue"
import Knowledge from "@/components/document/manual/workflow/nodes/Knowledge.vue"
import Model from "@/components/document/manual/workflow/nodes/Model.vue"
import Para from "@/components/document/manual/workflow/nodes/Para.vue"
import Start from "@/components/document/manual/workflow/nodes/Start.vue"
import Weather from "@/components/document/manual/workflow/nodes/Weather.vue"
import Web from "@/components/document/manual/workflow/nodes/Web.vue"
import DialogueDebug from "@/components/document/manual/agent/DialogueDebug.vue"
import AgentIntro from "@/components/document/manual/agent/AgentIntro.vue"
import ConfigTool from "@/components/document/manual/agent/ConfigTool.vue"
import Publish from "@/components/document/manual/agent/Publish.vue"
import KBIntro from "@/components/document/manual/kb/KBIntro.vue"
import KBManage from "@/components/document/manual/kb/KBManage.vue"
import KBUse from "@/components/document/manual/kb/KBUse.vue"

const router = useRouter()
const expandedSections = ref<string[]>(['workflow', 'kb', 'agent'])
const currentSection = ref('product')

interface NavItem {
  id: string;
  label: string;
  component?: any;
  children?: NavItem[];
}

const navItems: NavItem[] = [
  {
    id: 'introduction',
    label: '简介',
    children: [
      {
        id: 'product',
        label: '产品简介',
        component: Product
      }
    ]
  },
  {
    id: 'manual',
    label: '使用手册',
    children: [
      {
        id: 'kb',
        label: '知识库',
        component: KBIntro,
        children: [
          { id: 'kb-intro', label: '简介', component: KBIntro },
          { id: 'kb-management', label: '管理', component: KBManage },
          { id: 'kb-usage', label: '使用', component: KBUse }
        ]
      },
      {
        id: 'workflow',
        label: '工作流',
        component: WorkflowIntro,
        children: [
          { id: 'workflow-intro', label: '简介', component: WorkflowIntro },
          {
            id: 'workflow-nodes',
            label: '节点说明',
            component: Start,
            children: [
              {
                id: 'start',
                label: '开始',
                component: Start
              },
              {
                id: 'end',
                label: '结束',
                component: End
              },
              {
                id: 'model',
                label: '大模型',
                component: Model
              },
              {
                id: 'code',
                label: '代码',
                component: Code
              },
              {
                id: 'condition',
                label: '条件分支',
                component: Condition
              },
              {
                id: 'classifier',
                label: '问题分类器',
                component: Classifier
              },
              {
                id: 'knowledge',
                label: '知识库检索',
                component: Knowledge
              },
              {
                id: 'weather',
                label: '天气查询',
                component: Weather
              },
              {
                id: 'para',
                label: '参数提取器',
                component: Para
              },
              {
                id: 'web',
                label: '网页爬取',
                component: Web
              },
              {
                id: 'agent_node',
                label: '智能体',
                component: Agent
              }
            ]
          },
          { id: 'workflow-orchestration', label: '编排节点', component: WorkflowOrchestration },
          { id: 'workflow-test', label: '试运行', component: WorkflowTest }
        ]
      },
      {
        id: 'agent',
        label: '智能体',
        component: AgentIntro,
        children: [
          { id: 'agent-intro', label: '简介', component: AgentIntro },
          { id: 'agent-config', label: '配置工具', component: ConfigTool },
          { id: 'agent-debug', label: '对话调试', component: DialogueDebug },
          { id: 'agent-publish', label: '发布与下架', component: Publish }
        ]
      }
    ]
  },
  // {
  //   id: 'lab',
  //   label: '动手实验室',
  //   children: [
  //     {
  //       id: 'aviation',
  //       label: '航概问答助手',
  //       component: AviationQA
  //     },
  //     {
  //       id: 'recommend',
  //       label: '影视音乐推荐助手',
  //       component: RecommendAssistant
  //     },
  //     {
  //       id: 'suit',
  //       label: '天气穿搭助手',
  //       component: WeatherSuit
  //     }
  //   ]
  // },
  {
    id: 'faq',
    label: '常见问题',
    children: [
      {
        id: 'basic',
        label: '基础问题',
        component: BasicFAQ
      },
      {
        id: 'user',
        label: '使用问题',
        component: UseFAQ
      },
      {
        id: 'other',
        label: '其他问题',
        component: OtherFAQ
      },
    ]
  },
]

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

  return findComponent(navItems) || Product
})

function handleNavClick(item: any) {
  currentSection.value = item.id
  if (item.children) {
    const index = expandedSections.value.indexOf(item.id);
    if (index > -1) {
      expandedSections.value.splice(index, 1); // 收起
    } else {
      expandedSections.value.push(item.id); // 展开
    }
  }
  window.scrollTo({ top: 0, behavior: 'smooth' });
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
          <!-- 一级菜单 -->
          <div 
            :class="['nav-item']"
            @click="handleNavClick(item)"
          >
            <span>{{ item.label }}</span>
          </div>

          <div v-if="item.children" class="nav-children">
            <div 
              v-for="(child, childIndex) in item.children"
              :key="childIndex"
            >
              <!-- 二级菜单 -->
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
                  >
                </div>

              <!-- 三级菜单 -->
              <div 
                v-if="child.children && expandedSections.includes(child.id)"
                class="nav-grandchildren"
              >
                <div
                  v-for="(grandChild, grandChildIndex) in child.children"
                  :key="grandChildIndex"
                >
                  <div 
                    :class="['nav-grandchild', { active: currentSection === grandChild.id }]"
                    @click="handleNavClick(grandChild)"
                  >
                    {{ grandChild.label }}
                    <img
                        v-if="grandChild.children"
                        :src="expandedSections.includes(grandChild.id) ?
                          'https://api.iconify.design/material-symbols:expand-less.svg' :
                          'https://api.iconify.design/material-symbols:expand-more.svg'"
                        class="expand-icon"
                    >
                  </div>

                  <!-- 四级菜单 -->
                  <div 
                    v-if="grandChild.children && expandedSections.includes(grandChild.id)"
                    class="nav-great-grandchildren"
                  >
                    <div
                      v-for="(greatGrandChild, greatGrandChildIndex) in grandChild.children"
                      :key="greatGrandChildIndex"
                      :class="['nav-great-grandchild', { active: currentSection === greatGrandChild.id }]"
                      @click="handleNavClick(greatGrandChild)"
                    >
                      {{ greatGrandChild.label }}
                    </div>
                  </div>
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
  position: relative;
}

.back-button {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  color: #606266;
  transition: color 0.3s;
  position: absolute;
  left: 24px;
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
  flex: 1;
  text-align: center;
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
  border-radius: 4px;
  color: #606266;
  font-weight: 500;
}

.nav-children {
  margin-left: 16px;
  margin-top: 8px;
}

.nav-child-wrapper {
  margin-bottom: 4px;
}

.nav-child-container,
.nav-grandchild-container {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.nav-child, .nav-grandchild {
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

.expand-button {
  background: none;
  border: none;
  padding: 4px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-left: 8px;
}

.expand-button:hover {
  opacity: 0.8;
}

.expand-icon {
  width: 20px;
  height: 20px;
  opacity: 0.6;
  transition: opacity 0.3s;
}

.nav-grandchildren {
  margin-left: 16px;
  margin-top: 4px;
}

.nav-grandchild:hover {
  background: #f5f7fa;
  color: #409eff;
}

.nav-grandchild.active {
  background: #ecf5ff;
  color: #409eff;
}

.nav-great-grandchildren {
  margin-left: 16px;
  margin-top: 4px;
}

.nav-great-grandchild {
  padding: 6px 16px;
  cursor: pointer;
  border-radius: 4px;
  color: #606266;
  transition: all 0.3s;
  font-size: 13px;
}

.nav-great-grandchild:hover {
  background: #f5f7fa;
  color: #409eff;
}

.nav-great-grandchild.active {
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