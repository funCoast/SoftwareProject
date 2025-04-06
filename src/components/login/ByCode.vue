<script setup lang="ts">
import { ref } from 'vue'
import { Message, CircleCheckFilled} from '@element-plus/icons-vue';
import axios from 'axios';
import router from '../../router';
import "./login.css"

const email = ref('');
const code = ref('');

function sendCode() {
  const reg =  /^([A-Za-z0-9_\.\-])+\@([A-Za-z0-9_\.\-])+\.([A-Za-z]{2,4})$/
  if (!reg.test(email.value)) {
    alert("请输入正确的邮箱")
    return
  }
  console.log(email)
  axios({
    method: 'post',
    url: '/api/user/sendCode',
    data: {
      email: email
    }
  }).then(function (response) {
    if(response.data.code === 0) {
      alert('验证码已发送')
    }
  })
}

function login() {
  axios({
    method: 'post',
    url: '/api/user/loginByCode',
    data: {
      email: email,
      code: code
    }
  }).then(function (response) {
    if (response.data.code === 0) {
      // 将 token,character,name,uid 存入 sessionStorage
      sessionStorage.setItem("token", response.data.token);
      sessionStorage.setItem('uid', response.data.uid);
      router.push('/home');
    } else {
      alert("验证码错误")
    }
  })
}
</script>

<template>
  <el-row class="row">
    <el-input class="input full" v-model="email" type="text" placeholder="请输入邮箱" maxlength="30" :prefix-icon="Message"/>
  </el-row>
  <el-row class="row">
      <el-input class="input code" v-model="code" type="text" placeholder="请输入验证码" maxlength="6" :prefix-icon="CircleCheckFilled"/>
      <el-button class="send_code" @click="sendCode()">发送验证码</el-button>
  </el-row>
  <el-row class="row">
      <el-text class="tip">未注册的用户输入验证码后将</el-text>
      <el-text class="tip blue">自动注册</el-text>
      <el-text class="tip">账户</el-text>
  </el-row>
  <el-row class="row">
    <el-button class="login_bt" type="primary" :disabled="!email || !code" @click="login()">登录/注册</el-button>
  </el-row>
</template>

<style scoped>
.input.code {
  width: 180px;
  margin-bottom: 5px;
}

.send_code {
  height: 30px;
  width: 100px;
  margin-left: auto;
  border-radius: 10px;
  font-weight: bold;
}
</style>
