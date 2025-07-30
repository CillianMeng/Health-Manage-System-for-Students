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
            <li class="nav-item active">
              <a href="#" class="nav-link">
                <span class="nav-icon">📊</span>
                <span class="nav-text">数据总览</span>
              </a>
            </li>
            <li class="nav-item">
              <a href="#" class="nav-link">
                <span class="nav-icon">🏥</span>
                <span class="nav-text">体检记录</span>
              </a>
            </li>
            <li class="nav-item">
              <a href="#" class="nav-link">
                <span class="nav-icon">💊</span>
                <span class="nav-text">用药管理</span>
              </a>
            </li>
            <li class="nav-item">
              <a href="#" class="nav-link">
                <span class="nav-icon">📋</span>
                <span class="nav-text">健康档案</span>
              </a>
            </li>
          </ul>
        </div>
        
        <div class="nav-section">
          <h3 class="nav-title">设置</h3>
          <ul class="nav-list">
            <li class="nav-item">
              <a href="#" class="nav-link">
                <span class="nav-icon">⚙️</span>
                <span class="nav-text">系统设置</span>
              </a>
            </li>
            <li class="nav-item">
              <a href="#" class="nav-link">
                <span class="nav-icon">❓</span>
                <span class="nav-text">帮助中心</span>
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
          <h1>数据总览</h1>
          <p>欢迎回来，{{ currentUser?.userName || '用户' }}！</p>
        </div>
        
        <div class="top-bar-actions">
          <button class="action-btn">
            <span class="action-icon">🔔</span>
          </button>
          <div class="user-menu">
            <div class="user-avatar">
              {{ (currentUser?.userName || 'U').charAt(0).toUpperCase() }}
            </div>
            <div class="user-info">
              <span class="user-name">{{ currentUser?.userName || '用户' }}</span>
              <button @click="logout" class="logout-btn">退出登录</button>
            </div>
          </div>
        </div>
      </header>

      <!-- 内容区域 -->
      <div class="content-area">
        <!-- 统计卡片 -->
        <div class="stats-grid">
          <div class="stat-card">
            <div class="stat-icon primary">📊</div>
            <div class="stat-content">
              <h3 class="stat-number">24</h3>
              <p class="stat-label">体检记录</p>
              <span class="stat-change positive">+2 本月</span>
            </div>
          </div>
          
          <div class="stat-card">
            <div class="stat-icon success">💊</div>
            <div class="stat-content">
              <h3 class="stat-number">12</h3>
              <p class="stat-label">用药提醒</p>
              <span class="stat-change neutral">今日待服用</span>
            </div>
          </div>
          
          <div class="stat-card">
            <div class="stat-icon warning">⚠️</div>
            <div class="stat-content">
              <h3 class="stat-number">3</h3>
              <p class="stat-label">异常指标</p>
              <span class="stat-change negative">需要关注</span>
            </div>
          </div>
          
          <div class="stat-card">
            <div class="stat-icon info">📈</div>
            <div class="stat-content">
              <h3 class="stat-number">89%</h3>
              <p class="stat-label">健康评分</p>
              <span class="stat-change positive">+5% 本周</span>
            </div>
          </div>
        </div>

        <!-- 主要内容块 -->
        <div class="content-grid">
          <!-- 最近活动 -->
          <div class="content-card">
            <div class="card-header">
              <h3 class="card-title">最近活动</h3>
              <button class="card-action">查看全部</button>
            </div>
            <div class="card-content">
              <div class="activity-list">
                <div class="activity-item">
                  <div class="activity-icon">🏥</div>
                  <div class="activity-content">
                    <p class="activity-title">完成年度体检</p>
                    <p class="activity-time">2小时前</p>
                  </div>
                </div>
                <div class="activity-item">
                  <div class="activity-icon">💊</div>
                  <div class="activity-content">
                    <p class="activity-title">服用维生素D</p>
                    <p class="activity-time">6小时前</p>
                  </div>
                </div>
                <div class="activity-item">
                  <div class="activity-icon">📊</div>
                  <div class="activity-content">
                    <p class="activity-title">更新健康数据</p>
                    <p class="activity-time">1天前</p>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- 健康趋势 -->
          <div class="content-card">
            <div class="card-header">
              <h3 class="card-title">健康趋势</h3>
              <select class="card-select">
                <option>最近7天</option>
                <option>最近30天</option>
                <option>最近3个月</option>
              </select>
            </div>
            <div class="card-content">
              <div class="chart-placeholder">
                <div class="chart-icon">📈</div>
                <p>健康数据图表</p>
                <small>（图表功能开发中）</small>
              </div>
            </div>
          </div>

          <!-- 快速操作 -->
          <div class="content-card">
            <div class="card-header">
              <h3 class="card-title">快速操作</h3>
            </div>
            <div class="card-content">
              <div class="quick-actions">
                <button class="quick-action-btn">
                  <span class="action-icon">📝</span>
                  <span class="action-text">记录数据</span>
                </button>
                <button class="quick-action-btn">
                  <span class="action-icon">📅</span>
                  <span class="action-text">预约体检</span>
                </button>
                <button class="quick-action-btn">
                  <span class="action-icon">💊</span>
                  <span class="action-text">设置提醒</span>
                </button>
                <button class="quick-action-btn">
                  <span class="action-icon">📊</span>
                  <span class="action-text">生成报告</span>
                </button>
              </div>
            </div>
          </div>

          <!-- 健康建议 -->
          <div class="content-card">
            <div class="card-header">
              <h3 class="card-title">健康建议</h3>
            </div>
            <div class="card-content">
              <div class="suggestions">
                <div class="suggestion-item">
                  <div class="suggestion-icon">💧</div>
                  <div class="suggestion-text">
                    <p><strong>多喝水</strong></p>
                    <p>建议每日饮水量：2000ml</p>
                  </div>
                </div>
                <div class="suggestion-item">
                  <div class="suggestion-icon">🚶</div>
                  <div class="suggestion-text">
                    <p><strong>适量运动</strong></p>
                    <p>建议每日步行：8000步</p>
                  </div>
                </div>
                <div class="suggestion-item">
                  <div class="suggestion-icon">😴</div>
                  <div class="suggestion-text">
                    <p><strong>充足睡眠</strong></p>
                    <p>建议睡眠时长：7-8小时</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
const props = defineProps({
  currentUser: {
    type: Object,
    default: null
  }
});

const emit = defineEmits(['logout']);

const logout = () => {
  emit('logout');
};
</script>

<style scoped>
/* 全屏布局 */
.dashboard {
  display: flex;
  min-height: 100vh;
  background: #f8fafc;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
}

/* 侧边栏 */
.sidebar {
  width: 280px;
  background: white;
  border-right: 1px solid #e5e7eb;
  display: flex;
  flex-direction: column;
  position: fixed;
  height: 100vh;
  overflow-y: auto;
}

.sidebar-header {
  padding: 24px;
  border-bottom: 1px solid #e5e7eb;
}

.logo {
  display: flex;
  align-items: center;
  gap: 12px;
}

.logo-icon {
  font-size: 32px;
}

.logo-text {
  font-size: 20px;
  font-weight: 700;
  color: #1f2937;
  margin: 0;
}

.sidebar-nav {
  flex: 1;
  padding: 24px 0;
}

.nav-section {
  margin-bottom: 32px;
}

.nav-title {
  font-size: 12px;
  font-weight: 600;
  color: #6b7280;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin: 0 0 16px 24px;
}

.nav-list {
  list-style: none;
  margin: 0;
  padding: 0;
}

.nav-item {
  margin-bottom: 4px;
}

.nav-link {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 24px;
  color: #6b7280;
  text-decoration: none;
  transition: all 0.2s ease;
  border-right: 3px solid transparent;
}

.nav-item.active .nav-link,
.nav-link:hover {
  background: #f3f4f6;
  color: #1f2937;
  border-right-color: #3b82f6;
}

.nav-icon {
  font-size: 18px;
}

.nav-text {
  font-size: 14px;
  font-weight: 500;
}

/* 主内容区域 */
.main-content {
  flex: 1;
  margin-left: 280px;
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

/* 顶部栏 */
.top-bar {
  background: white;
  border-bottom: 1px solid #e5e7eb;
  padding: 24px 32px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.page-title h1 {
  font-size: 24px;
  font-weight: 700;
  color: #1f2937;
  margin: 0 0 4px 0;
}

.page-title p {
  font-size: 14px;
  color: #6b7280;
  margin: 0;
}

.top-bar-actions {
  display: flex;
  align-items: center;
  gap: 16px;
}

.action-btn {
  background: #f3f4f6;
  border: none;
  border-radius: 8px;
  padding: 10px;
  cursor: pointer;
  transition: background 0.2s ease;
}

.action-btn:hover {
  background: #e5e7eb;
}

.action-icon {
  font-size: 18px;
}

.user-menu {
  display: flex;
  align-items: center;
  gap: 12px;
}

.user-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: #3b82f6;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
}

.user-info {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
}

.user-name {
  font-size: 14px;
  font-weight: 500;
  color: #1f2937;
}

.logout-btn {
  background: none;
  border: none;
  color: #6b7280;
  font-size: 12px;
  cursor: pointer;
  padding: 0;
  transition: color 0.2s ease;
}

.logout-btn:hover {
  color: #ef4444;
}

/* 内容区域 */
.content-area {
  flex: 1;
  padding: 32px;
  overflow-y: auto;
}

/* 统计卡片网格 */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 24px;
  margin-bottom: 32px;
}

.stat-card {
  background: white;
  border-radius: 12px;
  padding: 24px;
  border: 1px solid #e5e7eb;
  display: flex;
  align-items: center;
  gap: 16px;
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  color: white;
}

.stat-icon.primary { background: #3b82f6; }
.stat-icon.success { background: #10b981; }
.stat-icon.warning { background: #f59e0b; }
.stat-icon.info { background: #8b5cf6; }

.stat-content {
  flex: 1;
}

.stat-number {
  font-size: 24px;
  font-weight: 700;
  color: #1f2937;
  margin: 0 0 4px 0;
}

.stat-label {
  font-size: 14px;
  color: #6b7280;
  margin: 0 0 8px 0;
}

.stat-change {
  font-size: 12px;
  font-weight: 500;
  padding: 2px 8px;
  border-radius: 4px;
}

.stat-change.positive {
  background: #dcfce7;
  color: #16a34a;
}

.stat-change.negative {
  background: #fee2e2;
  color: #dc2626;
}

.stat-change.neutral {
  background: #f3f4f6;
  color: #6b7280;
}

/* 内容网格 */
.content-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 24px;
}

/* 内容卡片 */
.content-card {
  background: white;
  border-radius: 12px;
  border: 1px solid #e5e7eb;
  overflow: hidden;
}

.card-header {
  padding: 20px 24px;
  border-bottom: 1px solid #e5e7eb;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-title {
  font-size: 16px;
  font-weight: 600;
  color: #1f2937;
  margin: 0;
}

.card-action {
  background: none;
  border: none;
  color: #3b82f6;
  font-size: 14px;
  cursor: pointer;
  transition: color 0.2s ease;
}

.card-action:hover {
  color: #2563eb;
}

.card-select {
  border: 1px solid #d1d5db;
  border-radius: 6px;
  padding: 6px 12px;
  font-size: 14px;
  background: white;
}

.card-content {
  padding: 24px;
}

/* 活动列表 */
.activity-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.activity-item {
  display: flex;
  align-items: center;
  gap: 12px;
}

.activity-icon {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  background: #f3f4f6;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
}

.activity-content {
  flex: 1;
}

.activity-title {
  font-size: 14px;
  font-weight: 500;
  color: #1f2937;
  margin: 0 0 4px 0;
}

.activity-time {
  font-size: 12px;
  color: #6b7280;
  margin: 0;
}

/* 图表占位符 */
.chart-placeholder {
  text-align: center;
  padding: 60px 20px;
  color: #6b7280;
}

.chart-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

/* 快速操作 */
.quick-actions {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}

.quick-action-btn {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding: 20px;
  background: #f8fafc;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.quick-action-btn:hover {
  background: #f1f5f9;
  border-color: #3b82f6;
}

.quick-action-btn .action-icon {
  font-size: 24px;
}

.quick-action-btn .action-text {
  font-size: 12px;
  font-weight: 500;
  color: #374151;
}

/* 建议列表 */
.suggestions {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.suggestion-item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
}

.suggestion-icon {
  font-size: 20px;
  margin-top: 2px;
}

.suggestion-text p {
  margin: 0 0 4px 0;
  font-size: 14px;
  color: #374151;
}

.suggestion-text p:last-child {
  color: #6b7280;
  font-size: 13px;
}

/* 响应式设计 */
@media (max-width: 1024px) {
  .sidebar {
    width: 240px;
  }
  
  .main-content {
    margin-left: 240px;
  }
  
  .content-area {
    padding: 24px;
  }
  
  .stats-grid {
    grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  }
  
  .content-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .sidebar {
    display: none;
  }
  
  .main-content {
    margin-left: 0;
  }
  
  .top-bar {
    padding: 16px 20px;
  }
  
  .content-area {
    padding: 20px;
  }
  
  .stats-grid {
    grid-template-columns: 1fr;
    gap: 16px;
  }
  
  .quick-actions {
    grid-template-columns: 1fr;
  }
}
</style>
