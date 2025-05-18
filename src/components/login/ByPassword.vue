<script setup lang="ts">
import { ref } from 'vue'
import { Message, Lock } from '@element-plus/icons-vue'
import axios from 'axios'
import router from '../../router'
import './login.css'

const account = ref('')
const password = ref('')

function login() {
  axios({
    method: 'post',
    url: 'user/loginByPassword',
    data: {
      account: account.value,
      password: password.value
    }
  }).then(function (response) {
    if (response.data.code === 0) {
      // 将 token,uid 存入 localStorage
      localStorage.setItem('LingXi_token', response.data.token);
      localStorage.setItem('LingXi_uid', response.data.id);
      router.push('/home');
    } else {
      ElMessage.error(response.data.message)
    }
  })
}
</script>

<template>
  <div class="form">
    <el-input
      v-model="account"
      placeholder="请输入邮箱/用户名"
      :prefix-icon="Message"
      clearable
      class="input"
    />
    <el-input
      v-model="password"
      placeholder="请输入密码"
      :prefix-icon="Lock"
      type="password"
      show-password
      clearable
      class="input"
    />
    <div class="hint">
      <span>初次使用请选择</span>
      <span class="highlight">验证码登录</span>
      <span>进行注册</span>
    </div>
    <el-button
      type="primary"
      class="submit-button"
      :disabled="!account || !password"
      @click="login()"
    >
      登录
    </el-button>
  </div>
</template>
