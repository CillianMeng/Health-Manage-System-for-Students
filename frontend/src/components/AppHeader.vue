<template>
  <header class="header">
    <div class="header-content">
      <div class="brand">
        <div class="brand-icon">🏥</div>
        <h1 class="brand-title">学生健康管理系统</h1>
      </div>
      
      <div class="user-section">
        <div class="user-avatar">
          {{ userInitial }}
        </div>
        <div class="user-info">
          <div class="user-name">{{ currentUser?.userName || '用户' }}</div>
          <div class="user-role">学生</div>
        </div>
        <button @click="handleLogout" class="logout-btn">
          <span>🚪</span>
          <span>退出登录</span>
        </button>
      </div>
    </div>
  </header>
</template>

<script setup>
import { computed } from 'vue';

const props = defineProps({
  currentUser: {
    type: Object,
    default: null
  }
});

const emit = defineEmits(['logout']);

const userInitial = computed(() => {
  const name = props.currentUser?.userName || '用户';
  return name.charAt(0).toUpperCase();
});

const handleLogout = () => {
  emit('logout');
};
</script>