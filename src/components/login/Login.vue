<template>
  <div class="login-page">
    <div class="login-panel">
      <div class="brand-row">
        <img src="../../assets/icons/Agent.svg" class="logo" />
        <h1 class="title">灵犀</h1>
      </div>

      <p class="subtitle">AI智能体低代码开发平台</p>

      <div class="auth-tabs">
        <div :class="['tab', byEmail ? 'active' : '']" @click="byEmail = true">
          验证码登录
        </div>
        <div :class="['tab', !byEmail ? 'active' : '']" @click="byEmail = false">
          密码登录
        </div>
      </div>

      <div class="auth-content">
        <component :is="ByEmail" v-if="byEmail" />
        <component :is="ByPassword" v-else />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import ByEmail from './ByCode.vue'
import ByPassword from './ByPassword.vue'

const byEmail = ref(true)
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  background: linear-gradient(135deg, #f0f4f8, #d9e4f5);
}

.login-panel {
  background: #ffffff;
  border-radius: 12px;                 /* ✅ 更柔和的圆角 */
  padding: 32px 28px;                  /* ✅ 缩小内边距 */
  width: 360px;                        /* ✅ 从 400px 缩小 */
  box-shadow: 0 6px 18px rgba(0, 0, 0, 0.08);  /* ✅ 更轻柔的阴影 */
  text-align: center;
}

.brand {
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 24px;
}

.logo {
  height: 36px; /* 原来24px，放大一档 */
}

.brand-row {
  display: flex;
  align-items: center;
  justify-content: center;  /* ✅ 重点：水平居中 */
  gap: 10px;
  margin-bottom: 16px;
}

.brand-name {
  font-size: 20px;
  font-weight: 600;
  color: #409eff;
}

.title {
  font-size: 32px;
  font-weight: bold;
  color: #409eff;
  margin-bottom: 8px;
}

.subtitle {
  font-size: 16px;
  color: #333;
  font-weight: 500;
  margin-bottom: 24px;
}


.auth-tabs {
  display: flex;
  justify-content: center;
  margin-bottom: 20px;
}

.tab {
  font-size: 14px;
  padding: 6px 16px;
  cursor: pointer;
  border-bottom: 2px solid transparent;
  color: #606266;
}

.tab.active {
  color: #409eff;
  font-weight: 600;
  border-bottom: 2px solid #409eff;
}

.auth-content {
  margin-top: 10px;
}
</style>
