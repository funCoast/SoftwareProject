<script setup lang="ts">
import { ref } from 'vue';
import ByEmail from './ByCode.vue';
import ByPassword from './ByPassword.vue';

const byEmail = ref(true);
</script>

<template>
  <div class="topBar">
    <img src="../../assets/icons/Agent.svg" class="logo">
    <el-text class="topFont" type="primary">
      灵犀
    </el-text>
  </div>

  <div class="box">
    <el-text class='title' tag="b">
      灵犀
    </el-text>
  </div>
  <div class="box">
    <el-text class="subtitle" tag="b">
      AI智能体低代码开发平台
    </el-text>
  </div>
  <div class="authBox">
    <el-row style="margin: 30px 0 30px">
      <el-col :offset="5" :span="7">
        <div :class="{auth_method_active:byEmail,auth_method:!byEmail}" @click="byEmail=true">
          <div>验证码登录</div>
          <div class="underline" v-if="byEmail"></div>  
        </div>
      </el-col>
      <el-col :span="7">
        <div :class="{auth_method_active:!byEmail, auth_method:byEmail}" @click="byEmail=false">
          <div>密码登录</div>
          <div class="underline" v-if="!byEmail"></div>
        </div>
      </el-col>
    </el-row>
    <component :is='ByEmail' v-if="byEmail"></component>
    <component :is='ByPassword' v-if="!byEmail"></component>
  </div>
</template>


<style scoped>
.topBar {
  padding: 5px;
  margin-bottom: 50px;
}

.box {
  text-align: center;
  margin: 10px 0 10px;
}

.authBox {
  height: 300px;
  width: 500px;
  margin: 20px auto 10px;
  padding: 10px;
  border: 0.5px solid #8da2bc;
  border-radius: 16px;
  box-shadow: 10px 10px 20px rgba(0, 0, 0, .15)
}

.logo {
  height: 20px;
  margin-left: 0em;
  vertical-align: middle;
}

.topFont {
  font-size: 15px;
  vertical-align: middle;
  text-align: center;
  font-family: 'Microsoft YaHei';
}

.title {
  font-size: 40px;
  font-family: 'Microsoft YaHei';
  color: #03b0fa;
}

.subtitle {
  font-size: 20px;
  font-family: 'Microsoft YaHei';
  color: #464c53;
}

.auth_method {
  height: 20px;
  width: 100px;
  margin: auto;
  text-align: center;
  cursor: pointer;
}

.auth_method_active {
  height: 20px;
  width: 100px;
  margin: auto;
  text-align: center;
  cursor: pointer;
  font-weight: bold;
  color: #02b1fc;
}

.underline {
  background-color: #02b1fc;
  border-top-left-radius: 3px;
  border-top-right-radius: 3px;
  height: 3px;
  
  left: -5px;
  right: -5px;
}
</style>
