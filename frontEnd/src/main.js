import { createApp } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'
import App from './App.vue'
import Home from './components/Home.vue'
import Workspace from './components/Workspace.vue'
import Community from './components/Community.vue'
import Profile from './components/Profile.vue'
import WorkflowCanvas from './components/WorkflowCanvas.vue'
import AgentDetail from './components/AgentDetail.vue'

const routes = [
  {
    path: '/',
    name: 'home',
    component: Home
  },
  {
    path: '/workspace',
    name: 'workspace',
    component: Workspace
  },
  {
    path: '/workspace/workflow',
    name: 'workflow',
    component: WorkflowCanvas
  },
  {
    path: '/community',
    name: 'community',
    component: Community
  },
  {
    path: '/agent-detail',
    name: 'AgentDetail',
    component: AgentDetail
  },
  {
    path: '/profile',
    name: 'profile',
    component: Profile
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

const app = createApp(App)
app.use(router)
app.mount('#app')
