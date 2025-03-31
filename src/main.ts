import { createApp } from 'vue'
import ElementPlus from 'element-plus'
import axios from 'axios'

import App from './App.vue'
import router from './router'

const app = createApp(App)
app.use(ElementPlus)
app.use(router)

sessionStorage.clear();

axios.defaults.baseURL = "/api";
app.config.globalProperties.$http = axios

app.mount('#app')