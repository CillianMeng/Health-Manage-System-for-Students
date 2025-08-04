<script setup>
import { ref } from 'vue';
import csrfAuthService from '../utils/csrf-auth.js';

const formData = ref({
  username: '',
  password: '',
  confirmPassword: ''
});

const errors = ref({});
const isLoading = ref(false);
const passwordStrength = ref(0);
const successMessage = ref('');

// 定义emit事件
const emit = defineEmits(['register-success', 'show-login']);

// 密码强度检查
const checkPasswordStrength = (password) => {
  let strength = 0;
  if (password.length >= 8) strength += 25;
  if (password.match(/[a-z]/)) strength += 25;
  if (password.match(/[A-Z]/)) strength += 25;  
  if (password.match(/[0-9]/)) strength += 25;
  return strength;
};

// 监听密码变化
const onPasswordChange = () => {
  passwordStrength.value = checkPasswordStrength(formData.value.password);
  if (errors.value.password) {
    delete errors.value.password;
  }
  // 清除通用错误信息
  if (errors.value.general) {
    errors.value.general = '';
  }
};

// 清除错误信息的通用函数
const clearErrors = (fieldName) => {
  if (fieldName && errors.value[fieldName]) {
    delete errors.value[fieldName];
  }
  // 清除通用错误
  if (errors.value.general) {
    errors.value.general = '';
  }
};

// 表单验证
const validateForm = () => {
  const newErrors = {};
  
  if (!formData.value.username.trim()) {
    newErrors.username = '用户名不能为空';
  } else if (formData.value.username.length < 3) {
    newErrors.username = '用户名至少需要3个字符';
  } else if (formData.value.username.length > 20) {
    newErrors.username = '用户名不能超过20个字符';
  }
  
  if (!formData.value.password) {
    newErrors.password = '密码不能为空';
  } else if (formData.value.password.length < 6) {
    newErrors.password = '密码至少需要6个字符';
  }
  
  if (formData.value.password !== formData.value.confirmPassword) {
    newErrors.confirmPassword = '两次输入的密码不一致';
  }
  
  errors.value = newErrors;
  // 清除之前的成功消息
  if (Object.keys(newErrors).length > 0) {
    successMessage.value = '';
  }
  
  return Object.keys(newErrors).length === 0;
};

// 注册处理
const handleRegister = async () => {
  if (!validateForm()) {
    return;
  }
  
  try {
    isLoading.value = true;
    // 清除之前的消息
    errors.value = {};
    successMessage.value = '';
    
    // 初始化CSRF服务
    await csrfAuthService.initialize();
    
    const result = await csrfAuthService.register(
      formData.value.username,
      formData.value.password
    );
    
    if (result.success) {
      // 显示成功消息
      successMessage.value = '注册成功！正在跳转到登录页面...';
      
      // 清空表单
      formData.value = {
        username: '',
        password: '',
        confirmPassword: ''
      };
      errors.value = {};
      passwordStrength.value = 0;
      
      // 延迟2秒后发射事件和跳转
      setTimeout(() => {
        emit('register-success', result.data);
        successMessage.value = '';
      }, 2000);
    } else {
      // 处理服务器返回的错误
      if (result.error) {
        if (typeof result.error === 'object') {
          // 处理字段特定的错误
          errors.value = result.error;
          
          // 如果有用户名相关错误，给出友好提示
          if (result.error.userName || result.error.username) {
            const userError = result.error.userName || result.error.username;
            if (Array.isArray(userError)) {
              errors.value.username = userError[0];
            } else {
              errors.value.username = userError;
            }
          }
          
          // 如果有密码相关错误
          if (result.error.password) {
            if (Array.isArray(result.error.password)) {
              errors.value.password = result.error.password[0];
            } else {
              errors.value.password = result.error.password;
            }
          }
          
          // 如果没有具体的字段错误，显示通用错误
          if (!result.error.userName && !result.error.username && !result.error.password && !result.error.general) {
            errors.value.general = '注册失败，请检查输入信息';
          }
        } else {
          errors.value = { general: result.error };
        }
      } else {
        errors.value = { general: '注册失败，请稍后重试' };
      }
    }
  } catch (error) {
    console.error('注册失败:', error);
    
    errors.value = { general: errorMessage };
    successMessage.value = '';  // 清除成功消息
  } finally {
    isLoading.value = false;
  }
};

// 获取密码强度文本和颜色
const getPasswordStrengthInfo = () => {
  if (passwordStrength.value === 0) return { text: '', color: '' };
  if (passwordStrength.value < 50) return { text: '弱', color: '#ef4444' };
  if (passwordStrength.value < 75) return { text: '中等', color: '#f59e0b' };
  return { text: '强', color: '#10b981' };
};
</script>

<template>
  <div class="register-page">
    <!-- 左侧装饰区域 -->
    <div class="register-sidebar">
      <div class="sidebar-content">
        <div class="brand-section">
          <div class="brand-icon">🏥</div>
          <h1 class="brand-title">注册账户</h1>
        </div>
      </div>
    </div>

    <!-- 右侧注册区域 -->
    <div class="register-main">
      <div class="register-container">
        <div class="register-form-wrapper">
          <div class="register-header">
            <h2>注册</h2>
          </div>

          <form @submit.prevent="handleRegister" class="register-form">
            <div class="form-group">
              <label for="username" class="form-label">用户名</label>
              <input
                id="username"
                v-model="formData.username"
                type="text"
                placeholder="请输入用户名（3-20个字符）"
                class="form-input"
                :class="{ 'error': errors.username }"
                :disabled="isLoading"
                @input="clearErrors('username')"
                required
              />
              <div v-if="errors.username" class="field-error">
                {{ errors.username }}
              </div>
            </div>

            <div class="form-group">
              <label for="password" class="form-label">密码</label>
              <input
                id="password"
                v-model="formData.password"
                type="password"
                placeholder="请输入密码（至少6个字符）"
                class="form-input"
                :class="{ 'error': errors.password }"
                :disabled="isLoading"
                @input="onPasswordChange"
                required
              />
              <div v-if="errors.password" class="field-error">
                {{ errors.password }}
              </div>
              
              <!-- 密码强度指示器 -->
              <div v-if="formData.password" class="password-strength">
                <div class="strength-bar">
                  <div 
                    class="strength-fill" 
                    :style="{ 
                      width: passwordStrength + '%', 
                      backgroundColor: getPasswordStrengthInfo().color 
                    }"
                  ></div>
                </div>
                <span 
                  class="strength-text"
                  :style="{ color: getPasswordStrengthInfo().color }"
                >
                  密码强度: {{ getPasswordStrengthInfo().text }}
                </span>
              </div>
            </div>

            <div class="form-group">
              <label for="confirmPassword" class="form-label">确认密码</label>
              <input
                id="confirmPassword"
                v-model="formData.confirmPassword"
                type="password"
                placeholder="请再次输入密码"
                class="form-input"
                :class="{ 'error': errors.confirmPassword }"
                :disabled="isLoading"
                @input="clearErrors('confirmPassword')"
                required
              />
              <div v-if="errors.confirmPassword" class="field-error">
                {{ errors.confirmPassword }}
              </div>
            </div>

            <div v-if="successMessage" class="success-message">
              <svg class="success-icon" viewBox="0 0 20 20" fill="currentColor">
                <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.857-9.809a.75.75 0 00-1.214-.882l-3.236 4.53L8.035 10.48a.75.75 0 00-1.07 1.04l2.5 2.5a.75.75 0 001.132-.071l3.5-4.898z" clip-rule="evenodd" />
              </svg>
              {{ successMessage }}
            </div>

            <div v-if="errors.general" class="error-message">
              <svg class="error-icon" viewBox="0 0 20 20" fill="currentColor">
                <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.28 7.22a.75.75 0 00-1.06 1.06L8.94 10l-1.72 1.72a.75.75 0 101.06 1.06L10 11.06l1.72 1.72a.75.75 0 101.06-1.06L11.06 10l1.72-1.72a.75.75 0 00-1.06-1.06L10 8.94 8.28 7.22z" clip-rule="evenodd" />
              </svg>
              <div class="error-content">
                <div class="error-title">注册失败</div>
                <div class="error-description">{{ errors.general }}</div>
              </div>
            </div>

            <button 
              type="submit" 
              class="register-button"
              :disabled="isLoading"
            >
              <span v-if="isLoading" class="loading-content">
                <div class="loading-spinner"></div>
                注册中...
              </span>
              <span v-else>创建账户</span>
            </button>
          </form>
          
          <div class="register-footer">
            <div class="login-link">
              <span>已有账户？</span>
              <button class="link-button" @click="$emit('show-login')">
                立即登录
              </button>
            </div>
            
            <p class="terms-text">
              创建账户即表示您同意我们的服务条款和隐私政策
            </p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* 全屏布局 */
.register-page {
  display: flex;
  min-height: 100vh;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
}

/* 左侧装饰区域 */
.register-sidebar {
  flex: 1;
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
  position: relative;
  overflow: hidden;
}

.register-sidebar::before {
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

/* 右侧注册区域 */
.register-main {
  flex: 1;
  background: #fafafa;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}

.register-container {
  width: 100%;
  max-width: 420px;
}

.register-form-wrapper {
  background: white;
  border-radius: 16px;
  padding: 48px;
  box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
  border: 1px solid #e5e7eb;
}

.register-header {
  text-align: center;
  margin-bottom: 40px;
}

.register-header h2 {
  font-size: 28px;
  font-weight: 700;
  color: #1f2937;
  margin: 0 0 8px 0;
}

.register-header p {
  font-size: 16px;
  color: #6b7280;
  margin: 0;
}

/* 表单样式 */
.register-form {
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
  color: #1f2937;           /* 明确设置深灰色文字 */
}

.form-input:focus {
  outline: none;
  border-color: #10b981;
  box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.1);
}

.form-input.error {
  border-color: #ef4444;
}

.form-input:disabled {
  background: #f9fafb;
  color: #9ca3af;
  cursor: not-allowed;
}

.field-error {
  font-size: 12px;
  color: #ef4444;
  margin-top: 4px;
}

/* 密码强度指示器 */
.password-strength {
  margin-top: 8px;
}

.strength-bar {
  width: 100%;
  height: 4px;
  background: #e5e7eb;
  border-radius: 2px;
  overflow: hidden;
  margin-bottom: 4px;
}

.strength-fill {
  height: 100%;
  transition: all 0.3s ease;
}

.strength-text {
  font-size: 12px;
  font-weight: 500;
}

/* 成功消息 */
.success-message {
  display: flex;
  align-items: center;
  gap: 8px;
  background: #f0fdf4;
  color: #15803d;
  padding: 12px 16px;
  border-radius: 8px;
  border: 1px solid #bbf7d0;
  font-size: 14px;
  animation: slideInSuccess 0.3s ease-out;
}

.success-icon {
  width: 16px;
  height: 16px;
  flex-shrink: 0;
}

@keyframes slideInSuccess {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 错误信息 */
.error-message {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  background: #fef2f2;
  color: #dc2626;
  padding: 16px;
  border-radius: 8px;
  border: 1px solid #fecaca;
  font-size: 14px;
  animation: slideInError 0.3s ease-out;
}

.error-icon {
  width: 20px;
  height: 20px;
  flex-shrink: 0;
  margin-top: 2px;
}

.error-content {
  flex: 1;
}

.error-title {
  font-weight: 600;
  margin-bottom: 4px;
  font-size: 14px;
}

.error-description {
  font-size: 13px;
  line-height: 1.4;
  opacity: 0.9;
}

@keyframes slideInError {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 注册按钮 */
.register-button {
  background: #10b981;
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

.register-button:hover:not(:disabled) {
  background: #059669;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(16, 185, 129, 0.4);
}

.register-button:disabled {
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

/* 页脚 */
.register-footer {
  margin-top: 32px;
  text-align: center;
}

.login-link {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  margin-bottom: 16px;
  font-size: 14px;
  color: #6b7280;
}

.link-button {
  background: none;
  border: none;
  color: #10b981;
  font-size: 14px;
  cursor: pointer;
  text-decoration: none;
  transition: color 0.2s ease;
  font-weight: 500;
}

.link-button:hover {
  color: #059669;
  text-decoration: underline;
}

.terms-text {
  font-size: 12px;
  color: #9ca3af;
  margin: 0;
  line-height: 1.4;
}

/* 动画 */
@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

/* 响应式设计 */
@media (max-width: 1024px) {
  .register-sidebar {
    display: none;
  }
  
  .register-main {
    background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  }
  
  .register-form-wrapper {
    margin: 20px;
  }
}

@media (max-width: 768px) {
  .register-main {
    padding: 20px;
  }
  
  .register-form-wrapper {
    padding: 32px 24px;
    margin: 0;
  }
  
  .register-header h2 {
    font-size: 24px;
  }
}

@media (max-width: 480px) {
  .register-form-wrapper {
    padding: 24px 20px;
  }
  
  .register-header h2 {
    font-size: 22px;
  }
}
</style>
