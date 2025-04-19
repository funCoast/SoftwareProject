import { createApp } from 'vue'
import ElementPlus from 'element-plus'
import axios from 'axios'

import App from './App.vue'
import router from './router'

const app = createApp(App)
app.use(ElementPlus)
app.use(router)

sessionStorage.clear()

axios.defaults.baseURL = '/api/linksoul'

// 每次请求都带上token
axios.interceptors.request.use(function (config) {
        console.log('url:', config.url);
        const token = sessionStorage.getItem('token')
        if (token) {
            config.headers.token = token
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
            alert("请登录");
            router.push('/login');
            break;
        // 403: token过期,清除本地token,跳转登录页面
        case 403:
            alert("登录过期");
            sessionStorage.removeItem('token');
            router.push('/login');
            break;
        // 404: 请求不存在
        case 404:
            alert("请求不存在");
            break;
        // 其他错误，直接抛出错误提示
        default:
            alert(error.response.data.message);
    }
    return Promise.reject(error.response);
});

app.config.globalProperties.$http = axios

app.mount('#app')