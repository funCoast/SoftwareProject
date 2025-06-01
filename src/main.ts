import { createApp } from 'vue'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'

import axios from 'axios'

import App from './App.vue'
import router from './router'

import { ElMessage } from 'element-plus'

const app = createApp(App)
app.use(ElementPlus)
app.use(router)

sessionStorage.clear()

axios.defaults.baseURL = '/api/linksoul'

// 每次请求都带上token
axios.interceptors.request.use(function (config) {
    const token = localStorage.getItem('LingXi_token')
    const uid = localStorage.getItem('LingXi_uid')
    const role = localStorage.getItem('LingXi_role')
    if (token) {
        config.headers.token = token
        config.headers.uid = uid
        config.headers.role = role
    }
    return config
}, function (error) {
    return Promise.reject(error)
}
)

axios.interceptors.response.use(function (response) {
    if (response.status === 200) {
        return Promise.resolve(response);
    }
    else {
        return Promise.reject(response);
    }
}, function (error) {
    switch (error.response.status) {
        // 401: 未登录,跳转登录界面
        case 401:
            ElMessage.error('用户未登录，请登录')
            router.push('/login');
            break;
        // 403: token过期,清除本地token,跳转登录页面
        case 403:
            ElMessage.error('登录过期，请重新登录')
            localStorage.removeItem('LingXi_token');
            router.push('/login');
            break;
        // 404: 请求不存在
        case 404:
            ElMessage.error('请求不存在')
            break;
        // 其他错误，直接抛出错误提示
        default:
            ElMessage.error(error.response.data.message)
    }
    return Promise.reject(error.response);
});

app.config.globalProperties.$http = axios

app.mount('#app')