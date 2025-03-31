<script setup lang="ts">
import { ref } from 'vue'
import { Message, CircleCheckFilled} from '@element-plus/icons-vue';
import "./login.css"

const email = ref('');
const code = ref('');

function sendCode() {
  const reg =  /^([A-Za-z0-9_\.\-])+\@([A-Za-z0-9_\.\-])+\.([A-Za-z]{2,4})$/
    if (!reg.test(email.value)) {
      alert("请输入正确的邮箱")
      return
    }
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
    <el-button class="login_bt" type="primary">登录/注册</el-button>
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
