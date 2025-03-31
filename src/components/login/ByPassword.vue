<script setup lang="ts">
import { ref } from 'vue'
import { Message, Lock} from '@element-plus/icons-vue';
import "./login.css"

const account = ref('');
const password = ref('');
</script>

<template>
  <el-row class="row">
    <el-input class="input full" v-model="account" type="text" placeholder="请输入邮箱/用户名" maxlength="11" :prefix-icon="Message"/>
  </el-row>
  <el-row class="row">
      <el-input class="input password" v-model="password" type="text" placeholder="请输入密码" maxlength="6" :prefix-icon="Lock"/>
  </el-row>
  <el-row class="row">
      <el-text class="tip">初次使用请选择</el-text>
      <el-text class="tip blue">验证码登录</el-text>
      <el-text class="tip">进行注册</el-text>
  </el-row>
  <el-row class="row">
    <el-button class="login_bt" type="primary">登录</el-button>
  </el-row>
</template>

<style scoped>
.input.password {
  width: 300px;
  margin-bottom: 5px;
}
</style>
