<script setup>
import { ref } from 'vue';

const username = ref('');
const password = ref('');
const errorMessage = ref('');
const isLoading = ref(false)

const login = async () => {
    // Handle login logic here
    if (!username.value || !password.value) {
        errorMessage.value = "用户名和密码不能为空";
        return;
    }

    try {
        isLoading.value = true;
        errorMe,sage.value = '';

        await new Promise(resolve => setTimeout(resolve, 1500));

    } catch (error) {
        errorMessage.value = '登录失败，请稍后再试';
    } finally {
        isLoading.value = false;
    }
};
</script>

<template>
    <div class = "login_container">
        <div class = "header">
            <h1>登录页面</h1>
        </div>
        <div class = "content">
            <input 
                v-model = "username"
                placeholder = "请输入用户名"
                class = "input"
                :disabled="isLoading"
            />
            <input
                type="password"
                v-model = password 
                placeholder="请输入密码"
                class = "input"
                :disabled="isLoading"
            />

            <div v-if="errorMessage" class="error-message">
                {{ errorMessage }}
            </div>

            <button 
                @click="login"
                :disabled="isLoading"
                class="login-button"
            >
                <span v-if="isLoading">登录中...</span>
                <span v-else>登录</span>
            </button>
        </div>
    </div>
</template>

<style scoped>
.login_container {
    max-width: 500px;
    margin: 50px auto;
    padding: 30px;
    border: 1px solid #ddd;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.header {
    text-align: center;
    margin-bottom: 200px;
}

.input {
    width: 100%;
    padding: 10px;
    margin-bottom: 15px;
    border: 1px solid #ddd;
    border-radius: 8px;
    box-sizing: border-box;
}

.input:focus {
    border-color: #4CAF50;
    outline: none;
}

.login-button{
  width: 100%;
  padding: 10px;
  background-color: #4CAF50;
  color: white;
  border: none;        /* 移除默认边框，看起来更现代 */
  border-radius: 4px;
  cursor: pointer;     /* 鼠标悬停时显示手形光标 */
  font-size: 16px;
  font-weight: 600;
  transition: all 0.3s ease;  /* 添加过渡动画 */
}

.login-button:hover {
  background-color: #308534;  /* 悬停时颜色变深 */
}

/* 禁用状态样式 */
.login-button:disabled {
  background-color: #cccccc;
  cursor: not-allowed;
  transform: none;
}

.login-button:disabled:hover {
  background-color: #cccccc;
}

/* 错误信息样式 */
.error-message {
    color: #ff4444;
    background-color: #ffebee;
    border: 1px solid #ffcdd2;
    padding: 10px;
    border-radius: 4px;
    margin-bottom: 15px;
    font-size: 14px;
    text-align: center;
}
</style>