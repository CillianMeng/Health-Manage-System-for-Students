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
  return Object.keys(newErrors).length === 0;
};

// 注册处理
const handleRegister = async () => {
  if (!validateForm()) {
    return;
  }
  
  try {
    isLoading.value = true;
    
    // 初始化CSRF服务
    await csrfAuthService.initialize();
    
    const result = await csrfAuthService.register(
      formData.value.username,
      formData.value.password
    );
    
    if (result.success) {
      emit('register-success', result.data);
      
      // 清空表单
      formData.value = {
        username: '',
        password: '',
        confirmPassword: ''
      };
      errors.value = {};
      passwordStrength.value = 0;
    } else {
      // 处理服务器返回的错误
      if (result.error) {
        if (typeof result.error === 'object') {
          errors.value = result.error;
        } else {
          errors.value = { general: result.error };
        }
      }
    }
  } catch (error) {
    console.error('注册失败:', error);
    errors.value = { general: '网络错误，请稍后重试' };
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
                required
              />
              <div v-if="errors.confirmPassword" class="field-error">
                {{ errors.confirmPassword }}
              </div>
            </div>

            <div v-if="errors.general" class="error-message">
              <svg class="error-icon" viewBox="0 0 20 20" fill="currentColor">
                <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.28 7.22a.75.75 0 00-1.06 1.06L8.94 10l-1.72 1.72a.75.75 0 101.06 1.06L10 11.06l1.72 1.72a.75.75 0 101.06-1.06L11.06 10l1.72-1.72a.75.75 0 00-1.06-1.06L10 8.94 8.28 7.22z" clip-rule="evenodd" />
              </svg>
              {{ errors.general }}
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
