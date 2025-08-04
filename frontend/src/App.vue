<script setup>
import { ref, onMounted } from 'vue';
import Login from './components/Login.vue';
import Register from './components/Register.vue';
import Dashboard from './components/Dashboard.vue';
import tokenAuthService from './utils/csrf-auth.js';

const isLoggedIn = ref(false);
const currentUser = ref(null);
const showRegister = ref(false);
const isInitializing = ref(true);

// 应用启动时检查登录状态
onMounted(async () => {
  try {
    // 初始化Token服务
    await tokenAuthService.initialize();
    
    // 检查登录状态
    const statusResult = await tokenAuthService.checkLoginStatus();
    
    if (statusResult.success && statusResult.data.is_authenticated) {
      isLoggedIn.value = true;
      currentUser.value = tokenAuthService.currentUser || { 
        userName: statusResult.data.user_name || statusResult.data.username 
      };
    } else {
      isLoggedIn.value = false;
      currentUser.value = null;
    }
  } catch (error) {
    console.error('检查登录状态时发生异常:', error);
    isLoggedIn.value = false;
    currentUser.value = null;
  } finally {
    isInitializing.value = false;
  }
});

// 处理登录成功事件
const handleLoginSuccess = (loginData) => {
  isLoggedIn.value = true;
  currentUser.value = loginData.user || tokenAuthService.currentUser;
  showRegister.value = false;
};

// 处理注册成功事件
const handleRegisterSuccess = (registerData) => {
  console.log('App: 用户注册成功', registerData);
  // 注册成功后可以直接登录或显示登录界面
  showRegister.value = false;
  // 这里可以添加自动登录逻辑
};

// 处理登出
const handleLogout = async () => {
  try {
    const result = await tokenAuthService.logout();
    
    if (result.success) {
      isLoggedIn.value = false;
      currentUser.value = null;
    } else {
      console.error('登出失败', result.error);
      // 即使服务器端登出失败，也清除本地状态
      isLoggedIn.value = false;
      currentUser.value = null;
    }
  } catch (error) {
    console.error('登出过程中发生错误', error);
    // 发生错误时也清除本地状态
    isLoggedIn.value = false;
    currentUser.value = null;
  }
};

// 显示注册界面
const showRegisterForm = () => {
  showRegister.value = true;
};

// 显示登录界面
const showLoginForm = () => {
  showRegister.value = false;
};

// 处理导航
const handleNavigate = (route) => {
  console.log('导航到:', route);
  // 这里可以添加路由逻辑
};
</script>

<template>
  <div class="app">
    <!-- 初始化加载状态 -->
    <div v-if="isInitializing" class="loading-container">
      <div class="loading-spinner">
        <div class="spinner"></div>
        <p>正在验证登录状态...</p>
      </div>
    </div>

    <!-- 登录状态下显示仪表板 -->
    <div v-else-if="isLoggedIn" class="dashboard">
      <Dashboard 
        :current-user="currentUser" 
        @logout="handleLogout"
        @navigate="handleNavigate" 
      />
    </div>

    <!-- 未登录状态下显示登录或注册界面 -->
    <div v-else>
      <!-- 注册界面 -->
      <Register 
        v-if="showRegister"
        @show-login="showLoginForm"
        @register-success="handleRegisterSuccess"
      />
      
      <!-- 登录界面 -->
      <Login 
        v-else
        @login-success="handleLoginSuccess"
        @show-register="showRegisterForm"
      />
    </div>
  </div>
</template>

<style scoped>
.app {
  min-height: 100vh;
  width: 100%;
  background: #f7f7f8;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
}

.dashboard {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: #f7f7f8;
}

/* 加载状态样式 */
.loading-container {
  min-height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  background: #f7f7f8;
}

.loading-spinner {
  text-align: center;
  color: #666;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 3px solid #e1e5e9;
  border-top: 3px solid #007bff;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 20px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.loading-spinner p {
  margin: 0;
  font-size: 14px;
  color: #666;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .app {
    padding: 0;
  }
}

/* 暗色模式支持 */
@media (prefers-color-scheme: dark) {
  .app, .dashboard, .loading-container {
    background: #1f2937;
  }
  
  .loading-spinner p {
    color: #d1d5db;
  }
  
  .spinner {
    border-color: #374151;
    border-top-color: #3b82f6;
  }
}
</style>