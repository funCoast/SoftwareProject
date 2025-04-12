import Login from './components/login/Login.vue';
import Main from './components/Main.vue';
import { createRouter, createWebHashHistory } from 'vue-router'
import Home from './components/home/Home.vue';
import Workspace from './components/workspace/Workspace.vue';
import Community from './components/community/Community.vue';
import AgentDetail from './components/agent/AgentDetail.vue';
import Profile from './components/profile/Profile.vue';
import EditProfile from './components/profile/EditProfile.vue';
import WorkflowCanvas from './components/workflow/WorkflowCanvas.vue';
import AgentDevelopment from './components/workspace/AgentDevelopment.vue';
import ResourceLibrary from './components/workspace/ResourceLibrary.vue';

const authRequired = true
const routes = [
    { 
        path: '/login',
        name: 'Login',
        meta: {authReq: false},
        component: Login 
    },
    {
        path: '/',
        name: 'Main',
        redirect: '/home',
        meta: {authReq: authRequired},
        component: Main,
        children: [
        {
            path: 'home',
            name: 'Home',
            component: Home
        },
        {
            path: 'workspace',
            name: 'Workspace',
            redirect: '/workspace/agentDevelopment',
            component: Workspace,
            children: [
            {
                path: 'agentDevelopment',
                name: 'AgentDevelopment',
                component: AgentDevelopment
            },
            {
                path: 'resourceLibrary',
                name: 'ResourceLibrary',
                component: ResourceLibrary
            }
            ]
        },
        {
            path: 'community',
            name: 'Community',
            component: Community
        },
        {
            path: 'agentDetail',
            name: 'AgentDetail',
            component: AgentDetail
        },
        {
            path: 'profile',
            name: 'Profile',
            component: Profile
        },
        {
            path: 'editProfile',
            name: 'EditProfile',
            component: EditProfile
        }
        ]
    },
    {
        path: '/workflow',
        name: 'WorkflowCanvas',
        component: WorkflowCanvas
    }
];

const router = createRouter({
    history: createWebHashHistory(),
    routes,
});

router.beforeEach((to, from, next) => {
    console.log('from:');
    console.log(from);

    console.log('to:');
    console.log(to);
    // 此路由是否需要登录
    if (to.meta.authReq === true) {
        // 检查是否登录
        if (sessionStorage.getItem('token')) {
            next();
        } else {
            alert("请登录！");
            next({
                name: 'Login',
            })
        }
    } else next();
});

export default router;