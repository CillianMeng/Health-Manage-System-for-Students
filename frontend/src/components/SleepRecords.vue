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
          🔄 刷新
        </button>
      </div>
      <SleepChart :weeklyData="weeklyStats" />
    </div>

    <!-- 睡眠记录列表 -->
    <div class="records-section">
      <div class="section-header">
        <h2>睡眠记录</h2>
        <button @click="refreshRecords" class="btn-secondary" :disabled="loading">
          🔄 刷新
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
              <button @click="editRecord(record)" class="btn-edit">✏️</button>
              <button @click="deleteRecord(record)" class="btn-delete">🗑️</button>
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
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>确认删除</h3>
          <button @click="deleteConfirm = null" class="modal-close">✕</button>
        </div>
        
        <div class="modal-body">
          <p>确定要删除这条睡眠记录吗？</p>
          <p class="delete-info">
            日期：{{ formatDate(deleteConfirm.sleep_date) }} | 
            睡眠时长：{{ deleteConfirm.sleep_duration_hours }}小时
          </p>
        </div>
        
        <div class="form-actions">
          <button @click="deleteConfirm = null" class="btn-secondary">取消</button>
          <button @click="confirmDelete" class="btn-danger" :disabled="submitting">
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
.sleep-records {
  padding: 24px;
  max-width: 1200px;
  margin: 0 auto;
}

/* 页面标题 */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.page-title {
  margin: 0;
  color: #1a365d;
  font-size: 28px;
  font-weight: 600;
}

/* 统计概览 */
.stats-overview {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
  margin-bottom: 32px;
}

.stat-card {
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  transition: transform 0.2s, box-shadow 0.2s;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.stat-icon {
  font-size: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 60px;
  height: 60px;
  background: #f7fafc;
  border-radius: 12px;
}

.stat-content {
  flex: 1;
}

.stat-number {
  margin: 0 0 4px 0;
  font-size: 24px;
  font-weight: 700;
  color: #2d3748;
}

.stat-label {
  margin: 0;
  font-size: 14px;
  color: #718096;
}

/* 章节标题 */
.chart-section,
.records-section {
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  padding: 24px;
  margin-bottom: 24px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.section-header h2 {
  margin: 0;
  color: #2d3748;
  font-size: 20px;
  font-weight: 600;
}

/* 按钮样式 */
.btn-primary,
.btn-secondary,
.btn-danger,
.btn-edit,
.btn-delete {
  padding: 8px 16px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.2s;
  display: inline-flex;
  align-items: center;
  gap: 8px;
}

.btn-primary {
  background: #3182ce;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: #2c5aa0;
}

.btn-secondary {
  background: #e2e8f0;
  color: #4a5568;
}

.btn-secondary:hover:not(:disabled) {
  background: #cbd5e0;
}

.btn-danger {
  background: #e53e3e;
  color: white;
}

.btn-danger:hover:not(:disabled) {
  background: #c53030;
}

.btn-edit,
.btn-delete {
  padding: 6px;
  font-size: 16px;
  background: transparent;
  border: 1px solid #e2e8f0;
  border-radius: 4px;
}

.btn-edit:hover {
  background: #f7fafc;
  border-color: #3182ce;
}

.btn-delete:hover {
  background: #fed7d7;
  border-color: #e53e3e;
}

/* 加载和空状态 */
.loading,
.empty-state {
  text-align: center;
  padding: 60px 20px;
  color: #718096;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #e2e8f0;
  border-top: 4px solid #3182ce;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 16px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.empty-icon {
  font-size: 64px;
  margin-bottom: 16px;
}

.empty-state h3 {
  margin: 0 0 8px 0;
  color: #4a5568;
}

/* 记录表格 */
.records-table {
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  overflow: hidden;
}

.table-header,
.table-row {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr 1fr 1fr 120px;
  gap: 16px;
  padding: 16px;
  align-items: center;
}

.table-header {
  background: #f7fafc;
  font-weight: 600;
  color: #4a5568;
  border-bottom: 1px solid #e2e8f0;
}

.table-row {
  border-bottom: 1px solid #f7fafc;
}

.table-row:last-child {
  border-bottom: none;
}

.table-row:hover {
  background: #f7fafc;
}

.quality-score {
  padding: 4px 8px;
  border-radius: 4px;
  font-weight: 500;
  font-size: 12px;
}

.quality-score.excellent {
  background: #c6f6d5;
  color: #22543d;
}

.quality-score.good {
  background: #bee3f8;
  color: #2a4365;
}

.quality-score.fair {
  background: #feebc8;
  color: #744210;
}

.quality-score.poor {
  background: #fed7d7;
  color: #742a2a;
}

.col-actions {
  display: flex;
  gap: 8px;
}

/* 模态框 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  border-radius: 12px;
  width: 90%;
  max-width: 500px;
  max-height: 90vh;
  overflow-y: auto;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 1px solid #e2e8f0;
}

.modal-header h3 {
  margin: 0;
  color: #2d3748;
}

.modal-close {
  background: none;
  border: none;
  font-size: 20px;
  cursor: pointer;
  color: #718096;
  padding: 4px;
}

.modal-body {
  padding: 20px 24px;
}

.delete-info {
  color: #718096;
  font-size: 14px;
  margin-top: 8px;
}

/* 表单 */
.record-form {
  padding: 20px 24px;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 6px;
  font-weight: 500;
  color: #4a5568;
}

.form-group input {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  font-size: 14px;
  transition: border-color 0.2s;
}

.form-group input:focus {
  outline: none;
  border-color: #3182ce;
  box-shadow: 0 0 0 3px rgba(49, 130, 206, 0.1);
}

.form-actions {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
  margin-top: 24px;
  padding-top: 20px;
  border-top: 1px solid #e2e8f0;
}

.error-message {
  background: #fed7d7;
  color: #742a2a;
  padding: 12px;
  border-radius: 6px;
  margin-bottom: 16px;
  font-size: 14px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .sleep-records {
    padding: 16px;
  }
  
  .page-header {
    flex-direction: column;
    gap: 16px;
    align-items: stretch;
  }
  
  .stats-overview {
    grid-template-columns: 1fr;
  }
  
  .table-header,
  .table-row {
    grid-template-columns: 1fr;
    gap: 8px;
    text-align: left;
  }
  
  .table-header {
    display: none;
  }
  
  .table-row {
    padding: 16px;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    margin-bottom: 8px;
    background: white;
  }
  
  .table-row > div:before {
    content: attr(class);
    font-weight: 600;
    color: #4a5568;
    text-transform: capitalize;
    display: block;
    margin-bottom: 4px;
  }
  
  .col-actions {
    justify-content: center;
    margin-top: 12px;
  }
}
</style>
