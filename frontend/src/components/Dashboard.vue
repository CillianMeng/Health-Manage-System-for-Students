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
            <li class="nav-item" :class="{ active: currentView === 'health-goals' }">
              <a href="#" @click.prevent="setCurrentView('health-goals')" class="nav-link">
                <span class="nav-icon">🎯</span>
                <span class="nav-text">健康目标</span>
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
                  <button @click="setCurrentView('health-goals')" class="quick-action-btn">
                    <span class="action-icon">🎯</span>
                    <span class="action-text">健康目标</span>
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
        
        <!-- 健康目标视图 -->
        <div v-else-if="currentView === 'health-goals'">
          <HealthGoals />
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
import HealthGoals from './HealthGoals.vue';

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
    diet: '饮食记录',
    'health-goals': '健康目标'
  };
  return titles[currentView.value] || '健康报告';
};

// 生成健康报告
const generateHealthReport = async () => {
  if (isGenerating.value) return;
  
  isGenerating.value = true;
  try {
    const token = localStorage.getItem('auth_token');
    console.log('Token from localStorage:', token); // 调试信息
    if (!token) {
      alert('请先登录');
      return;
    }

    const response = await fetch('http://127.0.0.1:8000/api/user/health-reports/generate/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({ period_type: 'weekly' })
    });

    console.log('Response status:', response.status); // 调试信息
    
    let data;
    try {
      data = await response.json();
    } catch (jsonError) {
      console.error('JSON解析错误:', jsonError);
      console.log('响应文本:', await response.text());
      alert('服务器响应格式错误');
      return;
    }
    
    console.log('Response data:', data); // 调试信息
    
    if (response.ok) {
      alert('健康报告生成成功！');
      await loadLatestReport();
    } else {
      alert(data.error || data.message || '生成健康报告失败');
    }
  } catch (error) {
    console.error('生成健康报告时发生错误:', error);
    console.error('错误详情:', {
      name: error.name,
      message: error.message,
      stack: error.stack
    });
    alert(`网络错误: ${error.message}，请检查后端服务器是否正常运行`);
  } finally {
    isGenerating.value = false;
  }
};

// 加载最新健康报告
const loadLatestReport = async () => {
  try {
    const token = localStorage.getItem('auth_token');
    if (!token) return;

    const response = await fetch('http://127.0.0.1:8000/api/user/health-reports/latest/', {
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

<style scoped>
.action-text {
  color: black;
}

/* 健康报告界面美化 */
.health-report-controls .content-card {
  background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
  border-radius: 16px;
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
  border: 1px solid #e2e8f0;
  overflow: hidden;
  margin-bottom: 24px;
}

.card-header {
  background: linear-gradient(135deg, #f1f5f9 0%, #e2e8f0 100%);
  padding: 24px;
  border-bottom: 1px solid #e2e8f0;
}

.card-title {
  margin: 0;
  font-size: 20px;
  font-weight: 700;
  color: #1e293b;
  display: flex;
  align-items: center;
  gap: 8px;
}

.card-title::before {
  content: '📋';
  font-size: 20px;
}

.card-content {
  padding: 24px;
}

.report-description {
  color: #64748b;
  line-height: 1.6;
  margin-bottom: 24px;
  font-size: 16px;
}

.generate-btn {
  background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
  color: white;
  border: none;
  padding: 14px 28px;
  border-radius: 12px;
  font-weight: 600;
  font-size: 16px;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(59, 130, 246, 0.3);
  position: relative;
  overflow: hidden;
}

.generate-btn:hover {
  background: linear-gradient(135deg, #1d4ed8 0%, #1e40af 100%);
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(59, 130, 246, 0.4);
}

.generate-btn:disabled {
  background: #94a3b8;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

/* 健康报告展示区域 */
.health-report-display {
  animation: fadeInUp 0.6s ease-out;
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 综合评分卡片 */
.overall-score-card {
  background: white;
  border-radius: 20px;
  padding: 32px;
  margin-bottom: 24px;
  display: flex;
  align-items: center;
  gap: 32px;
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.1);
  border: 1px solid #e2e8f0;
  position: relative;
  overflow: hidden;
}

.overall-score-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 5px;
  background: linear-gradient(90deg, #3b82f6, #8b5cf6, #06b6d4);
}

.score-circle {
  position: relative;
  width: 140px;
  height: 140px;
}

.score-progress {
  width: 100%;
  height: 100%;
  transform: rotate(-90deg);
}

.score-track {
  fill: none;
  stroke: #f1f5f9;
  stroke-width: 10;
}

.score-fill {
  fill: none;
  stroke-width: 10;
  stroke-linecap: round;
  transition: stroke-dasharray 1.2s ease;
}

.score-content {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  text-align: center;
}

.score-number {
  font-size: 32px;
  font-weight: 800;
  color: #1e293b;
  line-height: 1;
}

.score-label {
  font-size: 14px;
  color: #64748b;
  font-weight: 600;
  margin-top: 4px;
}

.score-info {
  flex: 1;
}

.score-grade {
  font-size: 28px;
  font-weight: 700;
  margin-bottom: 12px;
}

.score-trend {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 16px;
}

.trend-icon {
  font-size: 20px;
}

.trend-text {
  color: #64748b;
  font-weight: 500;
  font-size: 16px;
}

.report-period {
  color: #94a3b8;
  font-size: 14px;
}

/* 洞察和建议卡片 */
.insights-card, .recommendations-card {
  background: white;
  border-radius: 16px;
  margin-bottom: 24px;
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.08);
  border: 1px solid #e2e8f0;
  overflow: hidden;
}

/* 数据摘要和快速操作卡片 */
.data-summary-card, .quick-actions-card {
  background: white;
  border-radius: 16px;
  margin-bottom: 24px;
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.08);
  border: 1px solid #e2e8f0;
  overflow: hidden;
}

.insights-card .card-header::before {
  content: '💡';
}

.recommendations-card .card-header::before {
  content: '🎯';
}

.data-summary-card .card-header::before {
  content: '📊';
}

.quick-actions-card .card-header::before {
  content: '⚡';
}

.insights-list, .recommendations-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.insight-item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 18px;
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
  border-radius: 12px;
  border-left: 4px solid #3b82f6;
  transition: all 0.2s ease;
}

.insight-item:hover {
  transform: translateX(4px);
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.1);
}

.insight-icon {
  font-size: 18px;
  margin-top: 2px;
}

.insight-text {
  color: #475569;
  line-height: 1.6;
  font-weight: 500;
}

.recommendation-item {
  padding: 20px;
  border-radius: 12px;
  border-left: 4px solid #64748b;
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
  transition: all 0.2s ease;
}

.recommendation-item:hover {
  transform: translateX(4px);
}

.recommendation-item.high {
  border-left-color: #ef4444;
  background: linear-gradient(135deg, #fef2f2 0%, #fee2e2 100%);
}

.recommendation-item.medium {
  border-left-color: #f59e0b;
  background: linear-gradient(135deg, #fffbeb 0%, #fef3c7 100%);
}

.recommendation-item.low {
  border-left-color: #10b981;
  background: linear-gradient(135deg, #ecfdf5 0%, #d1fae5 100%);
}

.recommendation-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 10px;
}

.recommendation-category {
  font-size: 18px;
}

.recommendation-title {
  font-weight: 700;
  color: #1e293b;
  flex: 1;
  font-size: 16px;
}

.recommendation-priority {
  padding: 6px 12px;
  border-radius: 8px;
  font-size: 12px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.recommendation-priority.high {
  background: #ef4444;
  color: white;
}

.recommendation-priority.medium {
  background: #f59e0b;
  color: white;
}

.recommendation-priority.low {
  background: #10b981;
  color: white;
}

.recommendation-description {
  color: #64748b;
  line-height: 1.6;
  font-size: 15px;
}

/* 数据摘要样式 */
.summary-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
}

.summary-item {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px;
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
  border-radius: 12px;
  border: 1px solid #e2e8f0;
  transition: all 0.2s ease;
}

.summary-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.summary-icon {
  font-size: 24px;
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.summary-content {
  flex: 1;
}

.summary-value {
  font-size: 24px;
  font-weight: 700;
  color: #1e293b;
  line-height: 1;
}

.summary-label {
  font-size: 14px;
  color: #64748b;
  font-weight: 600;
  margin: 4px 0;
}

.summary-detail {
  font-size: 12px;
  color: #94a3b8;
}

/* 快速操作样式 */
.quick-actions {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
}

.quick-action-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 16px 20px;
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.2s ease;
  font-weight: 500;
  text-decoration: none;
  color: #475569;
  width: 100%;
  min-height: 60px;
  text-align: center;
}

.quick-action-btn:hover {
  background: linear-gradient(135deg, #e2e8f0 0%, #cbd5e1 100%);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.quick-action-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

.action-icon {
  font-size: 18px;
}

.action-text {
  font-weight: 600;
  color: #1e293b;
  white-space: nowrap;
}

/* 在较小屏幕上的响应式调整 */
@media (max-width: 768px) {
  .quick-actions {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 480px) {
  .quick-actions {
    grid-template-columns: 1fr;
  }
}
</style>
