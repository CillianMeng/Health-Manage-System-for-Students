<template>
  <div class="sleep-records">
    <!-- 页面标题 -->
    <div class="page-header">
      <h1 class="page-title">睡眠记录管理</h1>
      <button @click="showAddForm = true" class="btn-primary">
        <span class="btn-icon">➕</span>
        添加记录
      </button>
    </div>

    <!-- 统计概览卡片 -->
    <div class="stats-overview">
      <div class="stat-card">
        <div class="stat-icon">😴</div>
        <div class="stat-content">
          <h3 class="stat-number">{{ weeklyStats.average_sleep_hours || 0 }}h</h3>
          <p class="stat-label">平均睡眠</p>
        </div>
      </div>
      
      <div class="stat-card">
        <div class="stat-icon">⭐</div>
        <div class="stat-content">
          <h3 class="stat-number">{{ weeklyStats.average_quality_score || 0 }}</h3>
          <p class="stat-label">平均质量</p>
        </div>
      </div>
      
      <div class="stat-card">
        <div class="stat-icon">📊</div>
        <div class="stat-content">
          <h3 class="stat-number">{{ weeklyStats.total_records || 0 }}</h3>
          <p class="stat-label">本周记录</p>
        </div>
      </div>
      
      <div class="stat-card">
        <div class="stat-icon">⏰</div>
        <div class="stat-content">
          <h3 class="stat-number">{{ weeklyStats.sleep_regularity || '暂无' }}</h3>
          <p class="stat-label">睡眠规律</p>
        </div>
      </div>
    </div>

    <!-- 一周睡眠趋势图表 -->
    <div class="chart-section">
      <div class="section-header">
        <h2>一周睡眠趋势</h2>
        <button @click="refreshWeeklyData" class="btn-secondary" :disabled="loading">
          刷新
        </button>
      </div>
      <SleepChart :weeklyData="weeklyStats" />
    </div>

    <!-- 睡眠记录列表 -->
    <div class="records-section">
      <div class="section-header">
        <h2>睡眠记录</h2>
        <button @click="refreshRecords" class="btn-secondary" :disabled="loading">
          刷新
        </button>
      </div>
      
      <div v-if="loading" class="loading">
        <div class="loading-spinner"></div>
        <p>加载中...</p>
      </div>
      
      <div v-else-if="records.length === 0" class="empty-state">
        <div class="empty-icon">😴</div>
        <h3>暂无睡眠记录</h3>
        <p>点击"添加记录"开始记录您的睡眠数据</p>
      </div>
      
      <div v-else class="records-table">
        <div class="table-header">
          <div class="col-date">日期</div>
          <div class="col-bedtime">入睡时间</div>
          <div class="col-waketime">起床时间</div>
          <div class="col-duration">睡眠时长</div>
          <div class="col-quality">质量评分</div>
          <div class="col-actions">操作</div>
        </div>
        
        <div class="table-body">
          <div v-for="record in records" :key="record.id" class="table-row">
            <div class="col-date">{{ formatDate(record.sleep_date) }}</div>
            <div class="col-bedtime">{{ record.bedtime }}</div>
            <div class="col-waketime">{{ record.wake_time }}</div>
            <div class="col-duration">{{ record.sleep_duration_hours }}h</div>
            <div class="col-quality">
              <span class="quality-score" :class="getQualityClass(record.sleep_quality_score)">
                {{ record.sleep_quality_score }}
              </span>
            </div>
            <div class="col-actions">
              <button @click="editRecord(record)" class="btn btn-sm">✏️</button>
              <button @click="deleteRecord(record)" class="btn btn-sm btn-danger">🗑️</button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 添加/编辑记录模态框 -->
    <div v-if="showAddForm || editingRecord" class="modal-overlay" @click="closeModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>{{ editingRecord ? '编辑睡眠记录' : '添加睡眠记录' }}</h3>
          <button @click="closeModal" class="modal-close">✕</button>
        </div>
        
        <form @submit.prevent="submitRecord" class="record-form">
          <div class="form-group">
            <label for="sleep_date">睡眠日期</label>
            <input 
              type="date" 
              id="sleep_date" 
              v-model="formData.sleep_date" 
              required
              :max="today"
            >
          </div>
          
          <div class="form-group">
            <label for="bedtime">入睡时间</label>
            <input 
              type="time" 
              id="bedtime" 
              v-model="formData.bedtime" 
              required
            >
          </div>
          
          <div class="form-group">
            <label for="wake_time">起床时间</label>
            <input 
              type="time" 
              id="wake_time" 
              v-model="formData.wake_time" 
              required
            >
          </div>
          
          <div v-if="formError" class="error-message">
            {{ formError }}
          </div>
          
          <div class="form-actions">
            <button type="button" @click="closeModal" class="btn-secondary">取消</button>
            <button type="submit" class="btn-primary" :disabled="submitting">
              {{ submitting ? '保存中...' : (editingRecord ? '更新' : '添加') }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- 删除确认模态框 -->
    <div v-if="deleteConfirm" class="modal-overlay" @click="deleteConfirm = null">
      <div class="modal-content delete-modal" @click.stop>
        <div class="modal-header delete-header">
          <div class="delete-icon">
            <span class="warning-icon">⚠️</span>
          </div>
          <h3 class="delete-title">确认删除睡眠记录</h3>
          <button @click="deleteConfirm = null" class="modal-close">✕</button>
        </div>
        
        <div class="modal-body delete-body">
          <div class="delete-warning">
            <p class="delete-message">您确定要删除这条睡眠记录吗？此操作无法撤销。</p>
          </div>
          
          <div class="delete-record-info">
            <div class="record-detail-card">
              <div class="detail-row">
                <span class="detail-label">📅 睡眠日期</span>
                <span class="detail-value">{{ formatDate(deleteConfirm.sleep_date) }}</span>
              </div>
              <div class="detail-row">
                <span class="detail-label">🛏️ 入睡时间</span>
                <span class="detail-value">{{ deleteConfirm.bedtime }}</span>
              </div>
              <div class="detail-row">
                <span class="detail-label">⏰ 起床时间</span>
                <span class="detail-value">{{ deleteConfirm.wake_time }}</span>
              </div>
              <div class="detail-row">
                <span class="detail-label">💤 睡眠时长</span>
                <span class="detail-value highlight">{{ deleteConfirm.sleep_duration_hours }}小时</span>
              </div>
              <div class="detail-row">
                <span class="detail-label">⭐ 质量评分</span>
                <span class="detail-value quality-badge" :class="getQualityClass(deleteConfirm.sleep_quality_score)">
                  {{ deleteConfirm.sleep_quality_score }}分
                </span>
              </div>
            </div>
          </div>
        </div>
        
        <div class="form-actions delete-actions">
          <button @click="deleteConfirm = null" class="btn-secondary cancel-btn">
            <span class="btn-icon">↩️</span>
            取消
          </button>
          <button @click="confirmDelete" class="btn-danger delete-btn" :disabled="submitting">
            <span class="btn-icon">🗑️</span>
            {{ submitting ? '删除中...' : '确认删除' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue';
import SleepChart from './SleepChart.vue';
import tokenAuthService from '../utils/csrf-auth.js';

// 响应式数据
const records = ref([]);
const weeklyStats = ref({});
const loading = ref(false);
const submitting = ref(false);
const showAddForm = ref(false);
const editingRecord = ref(null);
const deleteConfirm = ref(null);
const formError = ref('');

// 表单数据
const formData = reactive({
  sleep_date: '',
  bedtime: '',
  wake_time: ''
});

// 计算属性
const today = computed(() => {
  return new Date().toISOString().split('T')[0];
});

// 初始化
onMounted(async () => {
  // 确保认证服务已初始化
  await tokenAuthService.initialize();
  
  // 检查是否已登录
  if (!tokenAuthService.isLoggedIn()) {
    console.warn('用户未登录，无法加载睡眠记录');
    alert('请先登录后再访问睡眠记录页面');
    return;
  }
  
  loadRecords();
  loadWeeklyStats();
});

// API调用函数
async function apiCall(url, options = {}) {
  try {
    const response = await tokenAuthService.request(url, options);
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.message || errorData.detail || `HTTP ${response.status}: ${response.statusText}`);
    }
    
    // 如果是204 No Content，直接返回null而不解析JSON
    if (response.status === 204) {
      return null;
    }
    
    // 检查响应是否有内容
    const contentType = response.headers.get('content-type');
    if (contentType && contentType.includes('application/json')) {
      return response.json();
    } else {
      return null;
    }
  } catch (error) {
    // 如果是401或403错误，可能是token过期或无效，清除认证状态
    if (error.message.includes('401') || error.message.includes('403')) {
      tokenAuthService.setToken(null);
      tokenAuthService.isAuthenticated = false;
      tokenAuthService.currentUser = null;
      throw new Error('登录已过期，请重新登录');
    }
    throw error;
  }
}

// 加载睡眠记录列表
async function loadRecords() {
  try {
    loading.value = true;
    const data = await apiCall('/sleep-records/');
    records.value = data.records || [];
  } catch (error) {
    console.error('加载睡眠记录失败:', error);
    alert('加载睡眠记录失败: ' + error.message);
  } finally {
    loading.value = false;
  }
}

// 加载一周统计数据
async function loadWeeklyStats() {
  try {
    const data = await apiCall('/sleep-records/weekly/');
    weeklyStats.value = data;
  } catch (error) {
    console.error('加载一周统计数据失败:', error);
  }
}

// 刷新数据
async function refreshRecords() {
  await loadRecords();
}

async function refreshWeeklyData() {
  await loadWeeklyStats();
}

// 提交记录
async function submitRecord() {
  if (!validateForm()) return;
  
  try {
    submitting.value = true;
    formError.value = '';
    
    let responseData;
    
    if (editingRecord.value) {
      // 更新记录
      responseData = await apiCall(`/sleep-records/${editingRecord.value.id}/`, {
        method: 'PUT',
        body: JSON.stringify(formData)
      });
      
      // 直接更新前端列表中的记录
      const index = records.value.findIndex(r => r.id === editingRecord.value.id);
      if (index !== -1 && responseData.record) {
        records.value[index] = responseData.record;
      }
    } else {
      // 创建新记录
      responseData = await apiCall('/sleep-records/', {
        method: 'POST',
        body: JSON.stringify(formData)
      });
      
      // 将新记录添加到前端列表
      if (responseData && responseData.record) {
        records.value.unshift(responseData.record); // 添加到列表开头
      }
    }
    
    closeModal();
    // 更新统计数据
    await loadWeeklyStats();
    
    // 为了确保数据完全一致，重新加载所有数据
    setTimeout(async () => {
      await loadRecords();
      await loadWeeklyStats();
    }, 300);
    
    // 为了确保数据一致性，延迟一小段时间后再次刷新
    setTimeout(async () => {
      try {
        await loadRecords();
      } catch (e) {
        console.log('延迟刷新失败，但不影响用户操作');
      }
    }, 500);
  } catch (error) {
    console.error('保存记录失败:', error);
    formError.value = error.message;
  } finally {
    submitting.value = false;
  }
}

// 编辑记录
function editRecord(record) {
  editingRecord.value = record;
  formData.sleep_date = record.sleep_date;
  formData.bedtime = record.bedtime;
  formData.wake_time = record.wake_time;
}

// 删除记录
function deleteRecord(record) {
  deleteConfirm.value = record;
}

async function confirmDelete() {
  if (submitting.value) return; // 防止重复提交
  
  try {
    submitting.value = true;
    const recordId = deleteConfirm.value.id;
    
    // 立即清除确认对话框，防止重复删除
    deleteConfirm.value = null;
    
    // 调用删除API
    await apiCall(`/sleep-records/${recordId}/`, {
      method: 'DELETE'
    });
    
    // 删除成功后重新加载数据
    await loadRecords();
    await loadWeeklyStats();
    
  } catch (error) {
    console.error('删除记录失败:', error);
    alert('删除记录失败: ' + error.message);
  } finally {
    submitting.value = false;
  }
}

// 关闭模态框
function closeModal() {
  showAddForm.value = false;
  editingRecord.value = null;
  formError.value = '';
  resetForm();
}

// 重置表单
function resetForm() {
  formData.sleep_date = '';
  formData.bedtime = '';
  formData.wake_time = '';
}

// 表单验证
function validateForm() {
  if (!formData.sleep_date || !formData.bedtime || !formData.wake_time) {
    formError.value = '请填写所有必填字段';
    return false;
  }
  
  // 验证日期不能是未来
  if (formData.sleep_date > today.value) {
    formError.value = '睡眠日期不能是未来日期';
    return false;
  }
  
  return true;
}

// 工具函数
function formatDate(dateString) {
  const date = new Date(dateString);
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit'
  });
}

function getQualityClass(score) {
  if (score >= 90) return 'excellent';
  if (score >= 75) return 'good';
  if (score >= 60) return 'fair';
  return 'poor';
}
</script>

<style scoped>
.btn-secondary {
  background: var(--color-gray-100);
}

/* 删除模态框美化样式 */
.delete-modal {
  max-width: 480px;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
}

.delete-header {
  background: linear-gradient(135deg, #fef2f2 0%, #fee2e2 100%);
  border-bottom: 1px solid #fecaca;
  padding: 24px;
  text-align: center;
  position: relative;
}

.delete-icon {
  margin-bottom: 12px;
}

.warning-icon {
  font-size: 48px;
  display: inline-block;
  animation: warning-pulse 2s infinite;
}

@keyframes warning-pulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.1); }
}

.delete-title {
  color: #991b1b;
  font-size: 20px;
  font-weight: 600;
  margin: 0;
  letter-spacing: -0.025em;
}

.delete-body {
  padding: 24px;
  background: white;
}

.delete-warning {
  text-align: center;
  margin-bottom: 24px;
  padding: 16px;
  background: #fef7ff;
  border: 1px solid #f3e8ff;
  border-radius: 12px;
}

.delete-message {
  color: #6b21a8;
  font-size: 16px;
  font-weight: 500;
  margin: 0;
  line-height: 1.5;
}

.delete-record-info {
  margin-top: 20px;
}

.record-detail-card {
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  padding: 20px;
}

.detail-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 0;
  border-bottom: 1px solid #e2e8f0;
}

.detail-row:last-child {
  border-bottom: none;
}

.detail-label {
  font-size: 14px;
  color: #64748b;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 6px;
}

.detail-value {
  font-size: 14px;
  color: #1e293b;
  font-weight: 600;
}

.detail-value.highlight {
  color: #0f766e;
  background: #ccfbf1;
  padding: 4px 8px;
  border-radius: 6px;
  font-size: 13px;
}

.quality-badge {
  padding: 4px 8px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 600;
}

.quality-badge.excellent {
  background: #dcfce7;
  color: #166534;
}

.quality-badge.good {
  background: #dbeafe;
  color: #1e40af;
}

.quality-badge.fair {
  background: #fef3c7;
  color: #92400e;
}

.quality-badge.poor {
  background: #fee2e2;
  color: #991b1b;
}

.delete-actions {
  background: #f8fafc;
  border-top: 1px solid #e2e8f0;
  padding: 20px 24px;
  display: flex;
  gap: 12px;
  justify-content: flex-end;
}

.cancel-btn {
  background: white;
  color: #64748b;
  border: 1px solid #d1d5db;
  transition: all 0.2s ease;
}

.cancel-btn:hover:not(:disabled) {
  background: #f8fafc;
  border-color: #9ca3af;
  color: #374151;
  transform: translateY(-1px);
}

.delete-btn {
  background: linear-gradient(135deg, #dc2626 0%, #b91c1c 100%);
  color: white;
  border: none;
  transition: all 0.2s ease;
  box-shadow: 0 4px 6px -1px rgba(220, 38, 38, 0.3);
}

.delete-btn:hover:not(:disabled) {
  background: linear-gradient(135deg, #b91c1c 0%, #991b1b 100%);
  transform: translateY(-1px);
  box-shadow: 0 6px 8px -1px rgba(220, 38, 38, 0.4);
}

.delete-btn:disabled {
  opacity: 0.7;
  transform: none;
  box-shadow: none;
}

.btn-icon {
  font-size: 14px;
  margin-right: 6px;
}

/* 按钮加载状态 */
.delete-btn:disabled .btn-icon {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* 响应式设计 */
@media (max-width: 640px) {
  .delete-modal {
    max-width: 95vw;
    margin: 20px;
  }
  
  .delete-header {
    padding: 20px 16px;
  }
  
  .delete-body {
    padding: 20px 16px;
  }
  
  .delete-actions {
    padding: 16px;
    flex-direction: column;
  }
  
  .cancel-btn,
  .delete-btn {
    width: 100%;
    justify-content: center;
  }
  
  .detail-row {
    flex-direction: column;
    align-items: flex-start;
    gap: 4px;
  }
  
  .detail-value {
    font-size: 16px;
  }
}
</style>