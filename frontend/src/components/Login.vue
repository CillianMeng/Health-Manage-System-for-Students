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

<style scoped>
/* 全屏布局 */
.login-page {
  display: flex;
  min-height: 100vh;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
}

/* 左侧装饰区域 */
.login-sidebar {
  flex: 1;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
  position: relative;
  overflow: hidden;
}

.login-sidebar::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><defs><pattern id="grid" width="10" height="10" patternUnits="userSpaceOnUse"><path d="M 10 0 L 0 0 0 10" fill="none" stroke="rgba(255,255,255,0.1)" stroke-width="0.5"/></pattern></defs><rect width="100" height="100" fill="url(%23grid)"/></svg>');
  opacity: 0.3;
}

.sidebar-content {
  position: relative;
  z-index: 1;
  color: white;
  text-align: center;
  max-width: 400px;
}

.brand-section {
  margin-bottom: 60px;
}

.brand-icon {
  font-size: 60px;
  margin-bottom: 20px;
  display: block;
}

.brand-title {
  font-size: 36px;
  font-weight: 700;
  margin: 0 0 16px 0;
  line-height: 1.2;
}

.brand-subtitle {
  font-size: 18px;
  opacity: 0.9;
  margin: 0;
  line-height: 1.5;
}

.feature-list {
  display: flex;
  flex-direction: column;
  gap: 32px;
}

.feature-item {
  display: flex;
  align-items: flex-start;
  text-align: left;
  gap: 20px;
}

.feature-item .feature-icon {
  font-size: 32px;
  flex-shrink: 0;
  background: rgba(255, 255, 255, 0.15);
  border-radius: 12px;
  padding: 12px;
  backdrop-filter: blur(10px);
}

.feature-content h3 {
  font-size: 18px;
  font-weight: 600;
  margin: 0 0 8px 0;
}

.feature-content p {
  font-size: 14px;
  opacity: 0.8;
  margin: 0;
  line-height: 1.4;
}

/* 右侧登录区域 */
.login-main {
  flex: 1;
  background: #fafafa;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}

.login-container {
  width: 100%;
  max-width: 420px;
}

.login-form-wrapper {
  background: white;
  border-radius: 16px;
  padding: 48px;
  box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
  border: 1px solid #e5e7eb;
}

.login-header {
  text-align: center;
  margin-bottom: 40px;
}

.login-header h2 {
  font-size: 28px;
  font-weight: 700;
  color: #1f2937;
  margin: 0 0 8px 0;
}

.login-header p {
  font-size: 16px;
  color: #6b7280;
  margin: 0;
}

/* 表单样式 */
.login-form {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-label {
  font-size: 14px;
  font-weight: 500;
  color: #374151;
}

.form-input {
  padding: 12px 16px;
  border: 2px solid #e5e7eb;
  border-radius: 8px;
  font-size: 16px;
  transition: all 0.2s ease;
  background: white;
}

.form-input:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.form-input:disabled {
  background: #f9fafb;
  color: #9ca3af;
  cursor: not-allowed;
}

/* 错误信息 */
.error-message {
  display: flex;
  align-items: center;
  gap: 8px;
  background: #fef2f2;
  color: #dc2626;
  padding: 12px 16px;
  border-radius: 8px;
  border: 1px solid #fecaca;
  font-size: 14px;
}

.error-icon {
  width: 16px;
  height: 16px;
  flex-shrink: 0;
}

/* 登录按钮 */
.login-button {
  background: #667eea;
  color: white;
  border: none;
  padding: 14px 24px;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  min-height: 48px;
}

.login-button:hover:not(:disabled) {
  background: #5a67d8;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.login-button:disabled {
  background: #d1d5db;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

/* 加载状态 */
.loading-content {
  display: flex;
  align-items: center;
  gap: 8px;
}

.loading-spinner {
  width: 16px;
  height: 16px;
  border: 2px solid transparent;
  border-top: 2px solid currentColor;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

.initializing-message {
  text-align: center;
  padding: 40px 20px;
  color: #6b7280;
}

.initializing-message .loading-spinner {
  width: 24px;
  height: 24px;
  margin-bottom: 12px;
}

/* 页脚 */
.login-footer {
  margin-top: 32px;
  text-align: center;
}

.help-links {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  margin-bottom: 16px;
}

.help-link {
  background: none;
  border: none;
  color: #667eea;
  font-size: 14px;
  cursor: pointer;
  text-decoration: none;
  transition: color 0.2s ease;
}

.help-link:hover {
  color: #5a67d8;
  text-decoration: underline;
}

.separator {
  color: #d1d5db;
  font-size: 14px;
}

.csrf-status {
  font-size: 12px;
  color: #9ca3af;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.debug-btn {
  background: none;
  border: none;
  cursor: pointer;
  font-size: 12px;
  padding: 2px 4px;
  border-radius: 4px;
  transition: background 0.2s ease;
}

.debug-btn:hover {
  background: #f3f4f6;
}

/* 动画 */
@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

/* 响应式设计 */
@media (max-width: 1024px) {
  .login-sidebar {
    display: none;
  }
  
  .login-main {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  }
  
  .login-form-wrapper {
    margin: 20px;
  }
}

@media (max-width: 768px) {
  .login-main {
    padding: 20px;
  }
  
  .login-form-wrapper {
    padding: 32px 24px;
    margin: 0;
  }
  
  .login-header h2 {
    font-size: 24px;
  }
}

@media (max-width: 480px) {
  .login-form-wrapper {
    padding: 24px 20px;
  }
  
  .login-header h2 {
    font-size: 22px;
  }
}
</style>

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

<style scoped>
/* 全屏布局 */
.login-page {
  display: flex;
  min-height: 100vh;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
}

/* 左侧装饰区域 */
.login-sidebar {
  flex: 1;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
  position: relative;
  overflow: hidden;
}

.login-sidebar::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><defs><pattern id="grid" width="10" height="10" patternUnits="userSpaceOnUse"><path d="M 10 0 L 0 0 0 10" fill="none" stroke="rgba(255,255,255,0.1)" stroke-width="0.5"/></pattern></defs><rect width="100" height="100" fill="url(%23grid)"/></svg>');
  opacity: 0.3;
}

.sidebar-content {
  position: relative;
  z-index: 1;
  color: white;
  text-align: center;
  max-width: 400px;
}

.brand-section {
  margin-bottom: 60px;
}

.brand-icon {
  font-size: 60px;
  margin-bottom: 20px;
  display: block;
}

.brand-title {
  font-size: 36px;
  font-weight: 700;
  margin: 0 0 16px 0;
  line-height: 1.2;
}

.brand-subtitle {
  font-size: 18px;
  opacity: 0.9;
  margin: 0;
  line-height: 1.5;
}

.feature-list {
  display: flex;
  flex-direction: column;
  gap: 32px;
}

.feature-item {
  display: flex;
  align-items: flex-start;
  text-align: left;
  gap: 20px;
}

.feature-item .feature-icon {
  font-size: 32px;
  flex-shrink: 0;
  background: rgba(255, 255, 255, 0.15);
  border-radius: 12px;
  padding: 12px;
  backdrop-filter: blur(10px);
}

.feature-content h3 {
  font-size: 18px;
  font-weight: 600;
  margin: 0 0 8px 0;
}

.feature-content p {
  font-size: 14px;
  opacity: 0.8;
  margin: 0;
  line-height: 1.4;
}

/* 右侧登录区域 */
.login-main {
  flex: 1;
  background: #fafafa;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}

.login-container {
  width: 100%;
  max-width: 420px;
}

.login-form-wrapper {
  background: white;
  border-radius: 16px;
  padding: 48px;
  box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
  border: 1px solid #e5e7eb;
}

.login-header {
  text-align: center;
  margin-bottom: 40px;
}

.login-header h2 {
  font-size: 28px;
  font-weight: 700;
  color: #1f2937;
  margin: 0 0 8px 0;
}

.login-header p {
  font-size: 16px;
  color: #6b7280;
  margin: 0;
}

/* 表单样式 */
.login-form {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-label {
  font-size: 14px;
  font-weight: 500;
  color: #374151;
}

.form-input {
  padding: 12px 16px;
  border: 2px solid #e5e7eb;
  border-radius: 8px;
  font-size: 16px;
  transition: all 0.2s ease;
  background: white;
}

.form-input:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.form-input:disabled {
  background: #f9fafb;
  color: #9ca3af;
  cursor: not-allowed;
}

/* 错误信息 */
.error-message {
  display: flex;
  align-items: center;
  gap: 8px;
  background: #fef2f2;
  color: #dc2626;
  padding: 12px 16px;
  border-radius: 8px;
  border: 1px solid #fecaca;
  font-size: 14px;
}

.error-icon {
  width: 16px;
  height: 16px;
  flex-shrink: 0;
}

/* 登录按钮 */
.login-button {
  background: #667eea;
  color: white;
  border: none;
  padding: 14px 24px;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  min-height: 48px;
}

.login-button:hover:not(:disabled) {
  background: #5a67d8;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.login-button:disabled {
  background: #d1d5db;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

/* 加载状态 */
.loading-content {
  display: flex;
  align-items: center;
  gap: 8px;
}

.loading-spinner {
  width: 16px;
  height: 16px;
  border: 2px solid transparent;
  border-top: 2px solid currentColor;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

.initializing-message {
  text-align: center;
  padding: 40px 20px;
  color: #6b7280;
}

.initializing-message .loading-spinner {
  width: 24px;
  height: 24px;
  margin-bottom: 12px;
}

/* 页脚 */
.login-footer {
  margin-top: 32px;
  text-align: center;
}

.help-links {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  margin-bottom: 16px;
}

.help-link {
  background: none;
  border: none;
  color: #667eea;
  font-size: 14px;
  cursor: pointer;
  text-decoration: none;
  transition: color 0.2s ease;
}

.help-link:hover {
  color: #5a67d8;
  text-decoration: underline;
}

.separator {
  color: #d1d5db;
  font-size: 14px;
}

.csrf-status {
  font-size: 12px;
  color: #9ca3af;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.debug-btn {
  background: none;
  border: none;
  cursor: pointer;
  font-size: 12px;
  padding: 2px 4px;
  border-radius: 4px;
  transition: background 0.2s ease;
}

.debug-btn:hover {
  background: #f3f4f6;
}

/* 动画 */
@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

/* 响应式设计 */
@media (max-width: 1024px) {
  .login-sidebar {
    display: none;
  }
  
  .login-main {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  }
  
  .login-form-wrapper {
    margin: 20px;
  }
}

@media (max-width: 768px) {
  .login-main {
    padding: 20px;
  }
  
  .login-form-wrapper {
    padding: 32px 24px;
    margin: 0;
  }
  
  .login-header h2 {
    font-size: 24px;
  }
}

@media (max-width: 480px) {
  .login-form-wrapper {
    padding: 24px 20px;
  }
  
  .login-header h2 {
    font-size: 22px;
  }
}
</style>
