import { createRouter, createWebHashHistory } from "vue-router";

const authRequired = true; // 是否需要登录

const routes = [
  {
    path: "/login",
    name: "Login",
    meta: { authReq: false },
    component: () => import("@/components/login/Login.vue"),
  },
  {
    path: "/document",
    name: "Document",
    meta: { authReq: authRequired },
    component: () => import("@/components/document/Document.vue")
  },
  {
    path: "/",
    name: "Main",
    redirect: "/home",
    meta: { authReq: authRequired },
    component: () => import("@/components/Main.vue"),
    children: [
      {
        path: "home",
        name: "Home",
        component: () => import("@/components/home/Home.vue"),
      },
      {
        path: "message",
        name: "Message",
        component: () => import("@/components/message/Message.vue"),
      },
      {
        path: "workspace",
        name: "Workspace",
        redirect: "/workspace/agentDevelopment",
        component: () => import("@/components/workspace/Workspace.vue"),
        children: [
          {
            path: "agentDevelopment",
            name: "AgentDevelopment",
            component: () =>
                import("@/components/workspace/AgentDevelopment.vue"),
          },
          {
            path: "resourceLibrary",
            name: "ResourceLibrary",
            component: () =>
                import("@/components/workspace/ResourceLibrary.vue"),
          },
          {
            path: "textBase/:id",
            name: "TextBase",
            component: () => import("@/components/knowledgeBase/TextBase.vue"),
            meta: { authReq: authRequired },
          },
          {
            path: 'textBase/:id/upload',
            name: 'UploadText',
            component: () => import('@/components/knowledgeBase/UploadText.vue'),
            meta: { authReq: authRequired },
          },
          {
            path: "pictureBase/:id",
            name: "PictureBase",
            component: () =>
                import("@/components/knowledgeBase/PictureBase.vue"),
            meta: { authReq: authRequired },
          },
          {
            path: 'pictureBase/:id/upload',
            name: 'UploadPicture',
            component: () => import('@/components/knowledgeBase/UploadPicture.vue'),
            meta: { authReq: authRequired },
          },
          {
            path: "tableBase/:id",
            name: "TableBase",
            component: () => import("@/components/knowledgeBase/TableBase.vue"),
            meta: { authReq: authRequired },
          },
          {
            path: 'tableBase/:id/upload',
            name: 'UploadTable',
            component: () => import('@/components/knowledgeBase/UploadTable.vue'),
            meta: { authReq: authRequired },
          },
          {
            path: "workflow/:id",
            name: "WorkflowCanvas",
            component: () => import("@/components/workflow/WorkflowCanvas.vue"),
          },
        ],
      },
      {
        path: "community",
        name: "Community",
        component: () => import("@/components/community/Community.vue"),
      },
      {
        path: "publish-anno",
        name: "PublishAnno",
        component: () => import("@/components/admin/PublishAnno.vue")
      },
      {
        path: "review-agent",
        name: "ReviewAgent",
        component: () => import("@/components/admin/ReviewAgent.vue")
      },
      {
        path: "report-agent",
        name: "ReportAgent",
        component: () => import("@/components/admin/ReportAgent.vue")
      },
      {
        path: "user-manage",
        name: "UserManage",
        component: () => import("@/components/admin/UserManage.vue")
      },
      {
        path: "agentDetail/:id",
        name: "AgentDetail",
        component: () => import("@/components/agent/AgentDetail.vue"),
      },
      {
        path: "profile/:id",
        name: "Profile",
        component: () => import("@/components/profile/Profile.vue"),
      },
      {
        path: "editProfile",
        name: "EditProfile",
        component: () => import("@/components/profile/EditProfile.vue"),
      },
      {
        path: "agentEdit/:id",
        name: "AgentEdit",
        component: () => import("@/components/agent/AgentEdit.vue"),
      },
    ],
  }
];

const router = createRouter({
  history: createWebHashHistory(),
  routes,
});

router.beforeEach((to, from, next) => {
  console.log("from:", from);
  console.log("to:", to);

  // 检查是否需要登录
  if (to.meta.authReq === true) {
    if (localStorage.getItem("LingXi_token")) {
      next();
    } else {
      next({ name: "Login" });
    }
  } else {
    next();
  }
});

export default router;