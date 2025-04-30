import { createRouter, createWebHashHistory } from 'vue-router';

const authRequired = true; // 是否需要登录

const routes = [
    { 
        path: '/login',
        name: 'Login',
        meta: { authReq: false },
        component: () => import('./components/login/Login.vue'),
    },
    {
        path: '/',
        name: 'Main',
        redirect: '/home',
        meta: { authReq: authRequired },
        component: () => import('./components/Main.vue'),
        children: [
            {
                path: 'home',
                name: 'Home',
                component: () => import('./components/home/Home.vue'),
            },
            {
                path: 'workspace',
                name: 'Workspace',
                redirect: '/workspace/agentDevelopment',
                component: () => import('./components/workspace/Workspace.vue'),
                children: [
                    {
                        path: 'agentDevelopment',
                        name: 'AgentDevelopment',
                        component: () => import('./components/workspace/AgentDevelopment.vue'),
                    },
                    {
                        path: 'resourceLibrary',
                        name: 'ResourceLibrary',
                        component: () => import('./components/workspace/ResourceLibrary.vue'),
                    },
                    {
                        path: 'pictureBase/:id',
                        name: 'PictureBase',
                        component: () => import('./components/knowledgeBase/PictureBase.vue'),
                        meta: { authReq: authRequired },
                    },
                    {
                        path: 'textBase/:id',
                        name: 'TextBase',
                        component: () => import('./components/knowledgeBase/TextBase.vue'),
                        meta: { authReq: authRequired },
                    },
                    {
                        path: 'tableBase/:id',
                        name: 'TableBase',
                        component: () => import('./components/knowledgeBase/TableBase.vue'),
                        meta: { authReq: authRequired },
                    },
                    {
                        path: 'pictureBase/:id/upload',
                        name: 'UploadPicture',
                        component: () => import('./components/knowledgeBase/UploadPicture.vue'),
                        meta: { authReq: authRequired },
                    },
                    {
                        path: 'textBase/:id/upload',
                        name: 'UploadText',
                        component: () => import('./components/knowledgeBase/UploadText.vue'),
                        meta: { authReq: authRequired },
                    },
                    {
                        path: 'tableBase/:id/upload',
                        name: 'UploadTable',
                        component: () => import('./components/knowledgeBase/UploadTable.vue'),
                        meta: { authReq: authRequired },
                    }
                ],
            },
            {
                path: 'community',
                name: 'Community',
                component: () => import('./components/community/Community.vue'),
            },
            {
                path: 'agentDetail',
                name: 'AgentDetail',
                component: () => import('./components/agent/AgentDetail.vue'),
            },
            {
                path: 'profile',
                name: 'Profile',
                component: () => import('./components/profile/Profile.vue'),
            },
            {
                path: 'editProfile',
                name: 'EditProfile',
                component: () => import('./components/profile/EditProfile.vue'),
            },
        ],
    },
    {
        path: '/workflow',
        name: 'WorkflowCanvas',
        component: () => import('./components/workflow/WorkflowCanvas.vue'),
    },
];

const router = createRouter({
    history: createWebHashHistory(),
    routes,
});

router.beforeEach((to, from, next) => {
    console.log('from:', from);
    console.log('to:', to);

    // 检查是否需要登录
    if (to.meta.authReq === true) {
        if (sessionStorage.getItem('token')) {
            next();
        } else {
            alert("请登录！");
            next({ name: 'Login' });
        }
    } else {
        next();
    }
});

export default router;