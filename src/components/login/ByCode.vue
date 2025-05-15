<script setup lang="ts">
import { ref, onBeforeMount } from 'vue'
import { Message, CircleCheckFilled} from '@element-plus/icons-vue';
import axios from 'axios';
import router from '../../router';
import "./login.css"

const email = ref('')
const code = ref('')
const disable = ref(false)
const text = ref('发送验证码')

onBeforeMount(() => {
  const time = ref(0)
  if (localStorage.getItem('time')) {
    time.value = Number(localStorage.getItem('time'))
  }
  if (time.value > 0) {
      count(time.value)
  } else {
    localStorage.removeItem('time')
  }
})

function count(time:number) {
  disable.value = true
  text.value = time + "s后重新发送"
  const timer = setInterval(() => {
    if (time > 0) {
      time--
      text.value = time + "s后重新发送"
      localStorage.setItem('time', time.toString())
    } else {
      clearInterval(timer);
      disable.value = false
      text.value = '重新发送'
    }
  }, 1000)
}

function sendCode() {
  const reg =  /^([A-Za-z0-9_\.\-])+\@([A-Za-z0-9_\.\-])+\.([A-Za-z]{2,4})$/
  if (!reg.test(email.value)) {
    ElMessage.warning("请输入正确的邮箱")
    return
  }
  axios({
    method: 'post',
    url: 'user/sendCode', 
    data: {
      email: email.value
    }
  }).then(function (response) {
      if(response.data.code === 0) {
        ElMessage.success("验证码已发送")
      } else {
        ElMessage.error(response.data.message)
      }
      count(60)
  })
}

function login() {
  axios({
    method: 'post',
    url: 'user/loginByCode',
    data: {
      email: email.value,
      code: code.value
    }
  }).then(function (response) {
    if (response.data.code === 0) {
      // 将 token,character,name,uid 存入 sessionStorage
      sessionStorage.setItem('token', response.data.token);
      sessionStorage.setItem('uid', response.data.id);
      console.log(sessionStorage)
      if(response.data.is_new_user) {
        router.push('/editProfile');
        ElMessage.warning("初始密码为123456，请及时修改")
      } else {
        router.push('/home');
      }
    } else {
      ElMessage.error(response.data.message)
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
      <el-button class="send_code" :disabled="disable" @click="sendCode()">{{text}}</el-button>
  </el-row>
  <el-row class="row">
      <el-text class="tip">未注册的用户输入验证码后将</el-text>
      <el-text class="tip blue">自动注册</el-text>
      <el-text class="tip">, 验证码有效时间为5分钟</el-text>
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
