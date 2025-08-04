<script setup>
import { ref, onMounted } from 'vue';
import tokenAuthService from '../utils/csrf-auth.js';

const username = ref('');
const password = ref('');
const errorMessage = ref('');
const isLoading = ref(false);
const isInitializing = ref(true);
const csrfToken = ref('');

// 定义emit事件
const emit = defineEmits(['login-success', 'show-register']);

// 初始化Token
onMounted(async () => {
    try {
        await tokenAuthService.initialize();
        csrfToken.value = tokenAuthService.csrfToken || '未获取';
        
        // 检查是否已经登录
        const statusResult = await tokenAuthService.checkLoginStatus();
        if (statusResult.success && statusResult.data.is_authenticated) {
            emit('login-success', {
                user: tokenAuthService.currentUser,
                data: statusResult.data
            });
        }
    } catch (error) {
        console.error('初始化失败:', error);
        errorMessage.value = '初始化失败，请刷新页面重试';
    } finally {
        isInitializing.value = false;
    }
});

const login = async () => {
    // 验证输入
    if (!username.value || !password.value) {
        errorMessage.value = "用户名和密码不能为空";
        return;
    }

    try {
        isLoading.value = true;
        errorMessage.value = '';

        console.log('开始登录流程...');

        // 使用Token认证服务登录
        const result = await tokenAuthService.login(username.value, password.value);

        if (result.success) {
            console.log('登录成功:', result.data);
            
            // 触发登录成功事件，传递用户信息给父组件
            emit('login-success', {
                user: tokenAuthService.currentUser,
                data: result.data
            });
            
            // 清空表单
            username.value = '';
            password.value = '';
            
        } else {
            console.log('登录失败:', result.error);
            
            // 处理不同类型的错误
            if (result.error.userName) {
                errorMessage.value = result.error.userName[0];
            } else if (result.error.password) {
                errorMessage.value = result.error.password[0];
            } else if (result.error.non_field_errors) {
                errorMessage.value = result.error.non_field_errors[0];
            } else if (result.error.message) {
                errorMessage.value = result.error.message;
            } else if (result.error.error) {
                errorMessage.value = result.error.error;
            } else {
                errorMessage.value = '登录失败，请检查用户名和密码';
            }
        }

    } catch (error) {
        console.error('❌ 登录过程中发生错误:', error);
        errorMessage.value = '网络连接错误，请稍后再试';
    } finally {
        isLoading.value = false;
    }
};

// 支持回车键登录
const handleKeyPress = (event) => {
    if (event.key === 'Enter' && !isLoading.value && username.value && password.value) {
        login();
    }
};

// 清除错误信息
const clearError = () => {
    errorMessage.value = '';
};

// 调试功能
const debugAuth = async () => {
    try {
        const debugResult = await csrfAuthService.debugSession();
        console.log('🔧 调试信息:', debugResult);
        
        if (debugResult.success) {
            console.log('Session详情:', debugResult.data);
        }
    } catch (error) {
        console.error('调试失败:', error);
    }
};
</script>

<template>
  <div class="login-page">
    <!-- 左侧装饰区域 -->
    <div class="login-sidebar">
      <div class="sidebar-content">
        <div class="brand-section">
          <div class="brand-icon">🏥</div>
          <h1 class="brand-title">学生健康管理系统</h1>
        </div>
      </div>
    </div>

    <!-- 右侧登录区域 -->
    <div class="login-main">
      <div class="login-container">
        <div class="login-form-wrapper">
          <div class="login-header">
            <h2>登录</h2>
          </div>

          <!-- 初始化状态显示 -->
          <div v-if="isInitializing" class="initializing-message">
            <div class="loading-content">
              <div class="loading-spinner"></div>
              <span>正在初始化认证系统...</span>
            </div>
          </div>

          <form v-if="!isInitializing" @submit.prevent="login" class="login-form">
            <div class="form-group">
              <label for="username" class="form-label">用户名</label>
              <input
                id="username"
                v-model="username"
                type="text"
                placeholder="请输入用户名"
                class="form-input"
                :disabled="isLoading"
                @keypress="handleKeyPress"
                @input="clearError"
                autocomplete="username"
                required
              />
            </div>
            
            <div class="form-group">
              <label for="password" class="form-label">密码</label>
              <input
                id="password"
                v-model="password"
                type="password"
                placeholder="请输入密码"
                class="form-input"
                :disabled="isLoading"
                @keypress="handleKeyPress"
                @input="clearError"
                autocomplete="current-password"
                required
              />
            </div>

            <div v-if="errorMessage" class="error-message">
              <svg class="error-icon" viewBox="0 0 20 20" fill="currentColor">
                <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.28 7.22a.75.75 0 00-1.06 1.06L8.94 10l-1.72 1.72a.75.75 0 101.06 1.06L10 11.06l1.72 1.72a.75.75 0 101.06-1.06L11.06 10l1.72-1.72a.75.75 0 00-1.06-1.06L10 8.94 8.28 7.22z" clip-rule="evenodd" />
              </svg>
              {{ errorMessage }}
            </div>

            <button 
              type="submit" 
              class="login-button"
              :disabled="isLoading || !username || !password"
            >
              <span v-if="isLoading" class="loading-content">
                <div class="loading-spinner"></div>
                登录中...
              </span>
              <span v-else>登录</span>
            </button>
          </form>
          
          <div class="login-footer">
            <div class="help-links">
              <button class="help-link" @click.prevent="">忘记密码？</button>
              <span class="separator">·</span>
              <button class="help-link" @click.prevent="$emit('show-register')">创建账户</button>
            </div>
            
            <!-- CSRF状态显示（开发环境） -->
            <div v-if="!isInitializing" class="csrf-status">
              <small>
                🔐 CSRF保护: {{ csrfToken ? '已启用' : '未启用' }}
                <button v-if="csrfToken" @click="debugAuth" class="debug-btn" type="button">🔧</button>
              </small>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>


