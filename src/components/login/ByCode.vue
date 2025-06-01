<script setup lang="ts">
import { ref, onBeforeMount } from 'vue'
import { Message, CircleCheckFilled } from '@element-plus/icons-vue'
import axios from 'axios'
import router from '@/router'
import { ElMessageBox } from 'element-plus'
import './login.css'

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

function count(time: number) {
  disable.value = true
  text.value = time + 's后重新发送'
  const timer = setInterval(() => {
    if (time > 0) {
      time--
      text.value = time + 's后重新发送'
      localStorage.setItem('time', time.toString())
    } else {
      clearInterval(timer)
      disable.value = false
      text.value = '重新发送'
    }
  }, 1000)
}

function sendCode() {
  const reg =  /^([A-Za-z0-9_\.\-])+\@([A-Za-z0-9_\.\-])+\.([A-Za-z]{2,4})$/
  if (!reg.test(email.value)) {
    ElMessage.warning('请输入正确的邮箱')
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
      // 将 token,uid 存入 localStorage
      localStorage.setItem('LingXi_token', response.data.token)
      localStorage.setItem('LingXi_uid', response.data.id)
      localStorage.setItem('LingXi_role', response.data.role)
      if(response.data.is_new_user) {
        router.push('/editProfile');
        ElMessageBox.alert('初始密码为123456，请及时修改', '初次登录提示', {
          confirmButtonText: '好的'
        })
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
  <div class="form">
    <el-input
      v-model="email"
      placeholder="请输入邮箱"
      :prefix-icon="Message"
      clearable
      class="input"
    />
    <div class="code-row">
      <el-input
        v-model="code"
        placeholder="请输入验证码"
        :prefix-icon="CircleCheckFilled"
        clearable
        class="input code-input"
      />
      <el-button
        type="primary"
        :disabled="disable"
        class="code-button"
        @click="sendCode()"
      >
        {{ text }}
      </el-button>
    </div>
    <div class="hint">
      <span>未注册的用户输入验证码后将</span>
      <span class="highlight">自动注册</span>
      <span>，验证码有效时间为5分钟</span>
    </div>
    <el-button
      type="primary"
      class="submit-button"
      :disabled="!email || !code"
      @click="login()"
    >
      登录 / 注册
    </el-button>
  </div>
</template>
