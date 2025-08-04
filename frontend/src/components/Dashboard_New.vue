<template>
  <div class="dashboard">
    <!-- 侧边栏 -->
    <aside class="sidebar">
      <div class="sidebar-header">
        <div class="logo">
          <div class="logo-icon">🏥</div>
          <h2 class="logo-text">健康管理</h2>
        </div>
      </div>
      
      <nav class="sidebar-nav">
        <div class="nav-section">
          <h3 class="nav-title">主要功能</h3>
          <ul class="nav-list">
            <li class="nav-item" :class="{ active: currentView === 'health-report' }">
              <a href="#" @click.prevent="setCurrentView('health-report')" class="nav-link">
                <span class="nav-icon">📋</span>
                <span class="nav-text">健康报告</span>
              </a>
            </li>
            <li class="nav-item" :class="{ active: currentView === 'sleep' }">
              <a href="#" @click.prevent="setCurrentView('sleep')" class="nav-link">
                <span class="nav-icon">😴</span>
                <span class="nav-text">睡眠记录</span>
              </a>
            </li>
            <li class="nav-item" :class="{ active: currentView === 'exercise' }">
              <a href="#" @click.prevent="setCurrentView('exercise')" class="nav-link">
                <span class="nav-icon">🏃‍♂️</span>
                <span class="nav-text">运动记录</span>
              </a>
            </li>
            <li class="nav-item" :class="{ active: currentView === 'diet' }">
              <a href="#" @click.prevent="setCurrentView('diet')" class="nav-link">
                <span class="nav-icon">🍽️</span>
                <span class="nav-text">饮食记录</span>
              </a>
            </li>
          </ul>
        </div>
        
        <div class="nav-section">
          <h3 class="nav-title">系统</h3>
          <ul class="nav-list">
            <li class="nav-item">
              <a href="#" @click.prevent="logout" class="nav-link">
                <span class="nav-icon">🚪</span>
                <span class="nav-text">退出登录</span>
              </a>
            </li>
          </ul>
        </div>
      </nav>
    </aside>

    <!-- 主内容区域 -->
    <main class="main-content">
      <!-- 顶部栏 -->
      <header class="top-bar">
        <div class="page-title">
          <h1>{{ getPageTitle() }}</h1>
        </div>
        
        <div class="top-bar-actions">
          <div class="user-menu">
            <span class="user-name">{{ currentUser?.userName || '用户' }}</span>
            <button @click="logout" class="logout-btn">退出登录</button>
          </div>
        </div>
      </header>

      <!-- 内容区域 -->
      <div class="content-area">
        <!-- 健康报告视图 -->
        <div v-if="currentView === 'health-report'">
          <!-- 报告生成控制 -->
          <div class="health-report-controls" v-if="!latestReport">
            <div class="content-card">
              <div class="card-header">
                <h3 class="card-title">生成健康报告</h3>
              </div>
              <div class="card-content">
                <p class="report-description">
                  基于您最近7天的睡眠、运动和饮食数据，为您生成个性化的健康报告和建议。
                </p>
                <button 
                  @click="generateHealthReport" 
                  :disabled="isGenerating"
                  class="generate-btn primary"
                >
                  <span v-if="isGenerating">正在生成...</span>
                  <span v-else>生成健康报告</span>
                </button>
              </div>
            </div>
          </div>

          <!-- 健康报告展示 -->
          <div v-if="latestReport" class="health-report-display">
            <!-- 综合评分卡片 -->
            <div class="overall-score-card">
              <div class="score-circle">
                <svg class="score-progress" viewBox="0 0 120 120">
                  <circle cx="60" cy="60" r="54" class="score-track"></circle>
                  <circle 
                    cx="60" 
                    cy="60" 
                    r="54" 
                    class="score-fill"
                    :style="{ 
                      strokeDasharray: latestReport ? `${latestReport.overall_score * 3.39} 339` : '0 339',
                      stroke: latestReport ? getScoreColor(latestReport.overall_score) : '#ddd'
                    }"
                  ></circle>
                </svg>
                <div class="score-content">
                  <div class="score-number">{{ latestReport?.overall_score || 0 }}</div>
                  <div class="score-label">综合评分</div>
                </div>
              </div>
              <div class="score-info">
                <div class="score-grade" :style="{ color: latestReport ? getScoreColor(latestReport.overall_score) : '#666' }">
                  {{ latestReport?.grade || 'N/A' }}
                </div>
                <div class="score-trend">
                  <span class="trend-icon" :class="latestReport?.trend">
                    {{ latestReport ? getTrendIcon(latestReport.trend) : '→' }}
                  </span>
                  <span class="trend-text">{{ latestReport ? getTrendText(latestReport.trend) : '暂无数据' }}</span>
                </div>
                <div class="report-period">
                  报告周期：{{ latestReport?.period || '暂无' }}
                </div>
              </div>
            </div>

            <!-- 关键洞察 -->
            <div class="insights-card">
              <div class="card-header">
                <h3 class="card-title">关键洞察</h3>
              </div>
              <div class="card-content">
                <div class="insights-list">
                  <div 
                    v-for="(insight, index) in latestReport.key_insights" 
                    :key="index"
                    class="insight-item"
                  >
                    <span class="insight-icon">💡</span>
                    <span class="insight-text">{{ insight }}</span>
                  </div>
                </div>
              </div>
            </div>

            <!-- 个性化建议 -->
            <div class="recommendations-card">
              <div class="card-header">
                <h3 class="card-title">健康建议</h3>
              </div>
              <div class="card-content">
                <div class="recommendations-list">
                  <div 
                    v-for="(recommendation, index) in latestReport.recommendations" 
                    :key="index"
                    class="recommendation-item"
                    :class="recommendation.priority"
                  >
                    <div class="recommendation-header">
                      <span class="recommendation-category">{{ getCategoryIcon(recommendation.category) }}</span>
                      <span class="recommendation-title">{{ recommendation.title }}</span>
                      <span class="recommendation-priority" :class="recommendation.priority">
                        {{ getPriorityText(recommendation.priority) }}
                      </span>
                    </div>
                    <div class="recommendation-description">
                      {{ recommendation.description }}
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- 数据摘要 -->
            <div class="data-summary-card">
              <div class="card-header">
                <h3 class="card-title">数据摘要</h3>
              </div>
              <div class="card-content">
                <div class="summary-grid">
                  <div class="summary-item">
                    <span class="summary-icon">😴</span>
                    <div class="summary-content">
                      <div class="summary-value">{{ latestReport.data_summary.sleep_days }}</div>
                      <div class="summary-label">睡眠记录天数</div>
                      <div class="summary-detail">平均 {{ latestReport.data_summary.avg_sleep_hours }}h</div>
                    </div>
                  </div>
                  <div class="summary-item">
                    <span class="summary-icon">🏃‍♂️</span>
                    <div class="summary-content">
                      <div class="summary-value">{{ latestReport.data_summary.exercise_days }}</div>
                      <div class="summary-label">运动记录天数</div>
                      <div class="summary-detail">消耗 {{ latestReport.data_summary.total_calories_burned }}卡</div>
                    </div>
                  </div>
                  <div class="summary-item">
                    <span class="summary-icon">🍽️</span>
                    <div class="summary-content">
                      <div class="summary-value">{{ latestReport.data_summary.diet_days }}</div>
                      <div class="summary-label">饮食记录天数</div>
                      <div class="summary-detail">平均 {{ latestReport.data_summary.avg_calories_intake }}卡</div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- 快速操作 -->
            <div class="quick-actions-card">
              <div class="card-header">
                <h3 class="card-title">快速操作</h3>
              </div>
              <div class="card-content">
                <div class="quick-actions">
                  <button @click="generateHealthReport" class="quick-action-btn" :disabled="isGenerating">
                    <span class="action-icon">🔄</span>
                    <span class="action-text">重新生成报告</span>
                  </button>
                  <button @click="setCurrentView('sleep')" class="quick-action-btn">
                    <span class="action-icon">😴</span>
                    <span class="action-text">睡眠记录</span>
                  </button>
                  <button @click="setCurrentView('exercise')" class="quick-action-btn">
                    <span class="action-icon">🏃‍♂️</span>
                    <span class="action-text">运动记录</span>
                  </button>
                  <button @click="setCurrentView('diet')" class="quick-action-btn">
                    <span class="action-icon">🍽️</span>
                    <span class="action-text">饮食记录</span>
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 睡眠记录视图 -->
        <div v-else-if="currentView === 'sleep'">
          <SleepRecords />
        </div>

        <!-- 运动记录视图 -->
        <div v-else-if="currentView === 'exercise'">
          <ExerciseRecords />
        </div>

        <!-- 饮食记录视图 -->
        <div v-else-if="currentView === 'diet'">
          <DietRecords />
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import SleepRecords from './SleepRecords.vue';
import ExerciseRecords from './ExerciseRecords.vue';
import DietRecords from './DietRecords.vue';

const props = defineProps({
  currentUser: {
    type: Object,
    default: null
  }
});

const emit = defineEmits(['logout']);

// 响应式数据
const currentView = ref('health-report');
const latestReport = ref(null);
const isGenerating = ref(false);

// 设置当前视图
const setCurrentView = (view) => {
  currentView.value = view;
  if (view === 'health-report' && !latestReport.value) {
    loadLatestReport();
  }
};

// 获取页面标题
const getPageTitle = () => {
  const titles = {
    'health-report': '健康报告',
    sleep: '睡眠记录',
    exercise: '运动记录',
    diet: '饮食记录'
  };
  return titles[currentView.value] || '健康报告';
};

// 生成健康报告
const generateHealthReport = async () => {
  if (isGenerating.value) return;
  
  isGenerating.value = true;
  try {
    const token = localStorage.getItem('authToken');
    if (!token) {
      alert('请先登录');
      return;
    }

    const response = await fetch('/api/user/health-reports/generate/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({ period_days: 7 })
    });

    const data = await response.json();
    
    if (response.ok && data.success) {
      alert('健康报告生成成功！');
      await loadLatestReport();
    } else {
      alert(data.message || '生成健康报告失败');
    }
  } catch (error) {
    console.error('生成健康报告时发生错误:', error);
    alert('网络错误，请稍后重试');
  } finally {
    isGenerating.value = false;
  }
};

// 加载最新健康报告
const loadLatestReport = async () => {
  try {
    const token = localStorage.getItem('authToken');
    if (!token) return;

    const response = await fetch('/api/user/health-reports/latest/', {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });

    if (response.ok) {
      const data = await response.json();
      latestReport.value = data;
    }
  } catch (error) {
    console.error('加载健康报告时发生错误:', error);
  }
};

// 获取评分颜色
const getScoreColor = (score) => {
  if (score >= 90) return '#22c55e';      // 绿色
  if (score >= 80) return '#84cc16';      // 浅绿色
  if (score >= 70) return '#eab308';      // 黄色
  if (score >= 60) return '#f97316';      // 橙色
  return '#ef4444';                       // 红色
};

// 获取趋势图标
const getTrendIcon = (trend) => {
  const icons = {
    improving: '📈',
    stable: '➡️',
    declining: '📉'
  };
  return icons[trend] || '➡️';
};

// 获取趋势文本
const getTrendText = (trend) => {
  const texts = {
    improving: '持续改善',
    stable: '保持稳定',
    declining: '需要关注'
  };
  return texts[trend] || '暂无数据';
};

// 获取分类图标
const getCategoryIcon = (category) => {
  const icons = {
    sleep: '😴',
    exercise: '🏃‍♂️',
    diet: '🍽️'
  };
  return icons[category] || '💡';
};

// 获取优先级文本
const getPriorityText = (priority) => {
  const texts = {
    high: '高优先级',
    medium: '中优先级',
    low: '低优先级'
  };
  return texts[priority] || '一般';
};

const logout = () => {
  emit('logout');
};

// 组件挂载时加载数据
onMounted(() => {
  loadLatestReport();
});
</script>
