<template>
  <div class="exercise-records">
    <!-- 页面头部 -->
    <div class="page-header">
      <h2 class="page-title">运动记录管理</h2>
      <p class="page-description">记录每日运动情况，追踪健身进度</p>

      <button @click="showAddForm = true" class="btn btn-primary">
        <span class="btn-icon">+</span>
        添加运动记录
      </button>
    </div>

    <!-- 统计概览卡片 -->
    <div class="stats-overview">
      <div class="stat-card">
        <div class="stat-icon">🏃‍♂️</div>
        <div class="stat-content">
          <h3 class="stat-number">{{ weeklyStats.total_duration_hours || 0 }}h</h3>
          <p class="stat-label">本周运动时长</p>
        </div>
      </div>
      
      <div class="stat-card">
        <div class="stat-icon">🔥</div>
        <div class="stat-content">
          <h3 class="stat-number">{{ weeklyStats.total_calories_burned || 0 }}</h3>
          <p class="stat-label">本周消耗卡路里</p>
        </div>
      </div>
      
      <div class="stat-card">
        <div class="stat-icon">⭐</div>
        <div class="stat-content">
          <h3 class="stat-number">{{ weeklyStats.fitness_score || 0 }}</h3>
          <p class="stat-label">健身评分</p>
        </div>
      </div>
      
      <div class="stat-card">
        <div class="stat-icon">🎯</div>
        <div class="stat-content">
          <h3 class="stat-number">{{ weeklyStats.most_frequent_exercise || '暂无' }}</h3>
          <p class="stat-label">最常运动</p>
        </div>
      </div>
    </div>

    <!-- 运动数据可视化 -->
    <div class="chart-section">
      <ExerciseChart :weeklyData="weeklyStats" />
    </div>

    <!-- 运动记录列表 -->
    <div class="records-section">
      <div v-if="loading" class="loading-state">
        <div class="loading-spinner"></div>
        <p>加载中...</p>
      </div>
      
      <div v-else-if="exerciseRecords.length === 0" class="empty-state">
        <div class="empty-icon">🏃‍♀️</div>
        <h3>暂无运动记录</h3>
        <p>开始记录您的运动数据，追踪健身进度吧！</p>
        <button @click="showAddForm = true" class="btn btn-primary">添加首条记录</button>
      </div>
      
      <div v-else class="records-list">
        <div class="records-header">
          <h2>运动记录列表</h2>
          <span class="records-count">共 {{ exerciseRecords.length }} 条记录</span>
        </div>
        
        <div class="records-table">
          <div class="table-header">
            <div class="col-date">日期</div>
            <div class="col-type">运动类型</div>
            <div class="col-duration">时长</div>
            <div class="col-calories">卡路里</div>
            <div class="col-intensity">强度</div>
            <div class="col-actions">操作</div>
          </div>
          
          <div class="table-body">
            <div 
              v-for="record in exerciseRecords" 
              :key="record.id" 
              class="table-row"
            >
              <div class="col-date">
                <span class="date-text">{{ formatDate(record.exercise_date) }}</span>
              </div>
              
              <div class="col-type">
                <div class="exercise-type">
                  <span class="type-icon">{{ getExerciseIcon(record.exercise_type) }}</span>
                  <span class="type-name">{{ record.exercise_type_display }}</span>
                </div>
              </div>
              
              <div class="col-duration">
                <span class="duration-text">{{ record.duration_minutes }} 分钟</span>
              </div>
              
              <div class="col-calories">
                <span class="calories-text">{{ record.calories_burned }} 卡</span>
              </div>
              
              <div class="col-intensity">
                <span 
                  class="intensity-badge" 
                  :class="getIntensityClass(record.exercise_intensity)"
                >
                  {{ record.exercise_intensity }}
                </span>
              </div>
              
              <div class="col-actions">
                <button 
                  @click="editRecord(record)" 
                  class="btn btn-sm"
                  title="编辑"
                >
                  ✏️
                </button>
                <button 
                  @click="deleteRecord(record)" 
                  class="btn btn-sm btn-danger"
                  title="删除"
                >
                  🗑️
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 添加/编辑表单模态框 -->
    <div v-if="showAddForm || showEditForm" class="modal-overlay" @click="closeModal">
      <div class="modal-content exercise-modal" @click.stop>
        <div class="modal-header exercise-header">
          <div class="header-icon">
            <span class="form-icon">🏃‍♂️</span>
          </div>
          <div class="header-text">
            <h3 class="modal-title">{{ showAddForm ? '添加运动记录' : '编辑运动记录' }}</h3>
            <p class="modal-subtitle">记录您的运动数据，追踪健身进度</p>
          </div>
          <button @click="closeModal" class="modal-close-btn">✕</button>
        </div>
        
        <form @submit.prevent="saveRecord" class="exercise-form">
          <div class="form-row">
            <div class="form-group">
              <label for="exercise-date" class="form-label">
                <span class="label-icon">📅</span>
                运动日期
                <span class="required">*</span>
              </label>
              <input 
                type="date" 
                id="exercise-date"
                v-model="formData.exercise_date" 
                :max="today"
                required 
                class="form-input date-input"
              />
            </div>
            
            <div class="form-group">
              <label for="exercise-type" class="form-label">
                <span class="label-icon">🏃‍♀️</span>
                运动类型
                <span class="required">*</span>
              </label>
              <select 
                id="exercise-type"
                v-model="formData.exercise_type" 
                required 
                class="form-input form-select"
              >
                <option value="" disabled>请选择运动类型</option>
                <option v-for="type in exerciseTypes" :key="type.value" :value="type.value" :style="{ color: 'black' }">
                  {{ type.icon }} {{ type.label }}
                </option>
              </select>
            </div>
          </div>
          
          <div class="form-group duration-group">
            <label for="duration" class="form-label">
              <span class="label-icon">⏱️</span>
              运动时长 (分钟)
              <span class="required">*</span>
            </label>
            <div class="duration-input-container">
              <input 
                type="number" 
                id="duration"
                v-model.number="formData.duration_minutes" 
                min="1" 
                max="480" 
                required 
                class="form-input duration-input"
                placeholder="请输入运动时长"
              />
              <span class="input-suffix">分钟</span>
            </div>
            <div class="quick-duration">
              <span class="quick-label">快速选择：</span>
              <div class="quick-buttons">
                <button 
                  type="button" 
                  v-for="duration in quickDurations" 
                  :key="duration"
                  @click="formData.duration_minutes = duration"
                  class="btn btn-sm btn-ghost quick-duration-btn"
                  :class="{ 'active': formData.duration_minutes === duration }"
                >
                  {{ duration }}分钟
                </button>
              </div>
            </div>
          </div>
          
          <div class="form-group">
            <label for="notes" class="form-label">
              <span class="label-icon">📝</span>
              备注
              <span class="optional">(可选)</span>
            </label>
            <textarea 
              id="notes"
              v-model="formData.notes" 
              rows="3" 
              class="form-input form-textarea"
              placeholder="记录运动感受、地点、强度等信息..."
            ></textarea>
            <div class="textarea-counter">
              {{ formData.notes?.length || 0 }}/200
            </div>
          </div>
          
          <div class="form-actions">
            <button type="button" @click="closeModal" class="btn-secondary">
              <span class="btn-icon">↩️</span>
              取消
            </button>
            <button type="submit" :disabled="saving" class="btn-primary">
              <span v-if="saving" class="loading-content">
                <span class="loading-spinner"></span>
                保存中...
              </span>
              <span v-else class="submit-content">
                <span class="btn-icon">{{ showAddForm ? '+' : '💾' }}</span>
                {{ showAddForm ? '添加记录' : '保存修改' }}
              </span>
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- 删除确认模态框 -->
    <div v-if="showDeleteModal" class="modal-overlay" @click="closeDeleteModal">
      <div class="modal-content delete-modal" @click.stop>
        <div class="modal-header delete-header">
          <div class="delete-icon">
            <span class="warning-icon">⚠️</span>
          </div>
          <h3 class="delete-title">确认删除运动记录</h3>
          <button @click="closeDeleteModal" class="modal-close">✕</button>
        </div>
        
        <div class="modal-body delete-body">
          <div class="delete-warning">
            <p class="delete-message">您确定要删除这条运动记录吗？此操作无法撤销。</p>
          </div>
          
          <div class="delete-record-info">
            <div class="record-detail-card">
              <div class="detail-row">
                <span class="detail-label">📅 运动日期</span>
                <span class="detail-value">{{ formatDate(recordToDelete?.exercise_date) }}</span>
              </div>
              <div class="detail-row">
                <span class="detail-label">🏃‍♂️ 运动类型</span>
                <span class="detail-value">{{ getExerciseIcon(recordToDelete?.exercise_type) }} {{ recordToDelete?.exercise_type_display }}</span>
              </div>
              <div class="detail-row">
                <span class="detail-label">⏱️ 运动时长</span>
                <span class="detail-value highlight">{{ recordToDelete?.duration_minutes }} 分钟</span>
              </div>
              <div class="detail-row">
                <span class="detail-label">🔥 消耗卡路里</span>
                <span class="detail-value calories-value">{{ recordToDelete?.calories_burned || '计算中' }} 卡</span>
              </div>
              <div class="detail-row" v-if="recordToDelete?.exercise_intensity">
                <span class="detail-label">💪 运动强度</span>
                <span class="detail-value intensity-badge" :class="getIntensityClass(recordToDelete?.exercise_intensity)">
                  {{ recordToDelete?.exercise_intensity }}
                </span>
              </div>
              <div class="detail-row" v-if="recordToDelete?.notes">
                <span class="detail-label">📝 备注信息</span>
                <span class="detail-value notes-text">{{ recordToDelete?.notes }}</span>
              </div>
            </div>
          </div>
        </div>
        
        <div class="form-actions delete-actions">
          <button @click="closeDeleteModal" class="btn-secondary cancel-btn">
            <span class="btn-icon">↩️</span>
            取消
          </button>
          <button @click="confirmDelete" class="btn-danger delete-btn" :disabled="deleting">
            <span class="btn-icon">🗑️</span>
            {{ deleting ? '删除中...' : '确认删除' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue';
import ExerciseChart from './ExerciseChart.vue';
import tokenAuthService from '../utils/csrf-auth.js';

// 响应式数据
const exerciseRecords = ref([]);
const weeklyStats = ref({});
const loading = ref(false);
const saving = ref(false);
const deleting = ref(false);

// 表单相关
const showAddForm = ref(false);
const showEditForm = ref(false);
const showDeleteModal = ref(false);
const recordToDelete = ref(null);
const editingRecord = ref(null);

// 筛选相关
const filterType = ref('');
const filterDate = ref('');

// 表单数据
const formData = reactive({
  exercise_date: '',
  exercise_type: '',
  duration_minutes: '',
  notes: ''
});

// 计算属性
const today = computed(() => {
  return new Date().toISOString().split('T')[0];
});

// 常量数据
const exerciseTypes = [
  { value: 'running', label: '跑步', icon: '🏃‍♂️' },
  { value: 'swimming', label: '游泳', icon: '🏊‍♀️' },
  { value: 'basketball', label: '篮球', icon: '🏀' },
  { value: 'football', label: '足球', icon: '⚽' },
  { value: 'tennis', label: '网球', icon: '🎾' },
  { value: 'badminton', label: '羽毛球', icon: '🏸' },
  { value: 'gym', label: '健身房', icon: '🏋️‍♀️' },
  { value: 'yoga', label: '瑜伽', icon: '🧘‍♀️' },
  { value: 'cycling', label: '骑行', icon: '🚴‍♂️' },
  { value: 'other', label: '其他', icon: '🏃‍♀️' }
];

const quickDurations = [15, 30, 45, 60, 90, 120];

// 生命周期
onMounted(async () => {
  // 初始化认证服务
  await tokenAuthService.initialize();
  
  // 检查登录状态
  if (!tokenAuthService.isLoggedIn()) {
    alert('请先登录');
    return;
  }
  
  loadExerciseRecords();
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

// 方法
const loadExerciseRecords = async () => {
  try {
    loading.value = true;
    const params = new URLSearchParams();
    
    if (filterType.value) {
      params.append('exercise_type', filterType.value);
    }
    
    if (filterDate.value) {
      params.append('exercise_date', filterDate.value);
    }
    
    const queryString = params.toString();
    const url = `/exercise-records/${queryString ? '?' + queryString : ''}`;
    
    const data = await apiCall(url);
    exerciseRecords.value = data.records || [];
  } catch (error) {
    console.error('加载运动记录失败:', error);
    alert('加载运动记录失败: ' + error.message);
    exerciseRecords.value = [];
  } finally {
    loading.value = false;
  }
};

const loadWeeklyStats = async () => {
  try {
    const data = await apiCall('/exercise-records/weekly/');
    weeklyStats.value = data || {};
  } catch (error) {
    console.error('加载一周统计失败:', error);
    weeklyStats.value = {};
  }
};

const saveRecord = async () => {
  try {
    saving.value = true;
    
    const recordData = {
      exercise_date: formData.exercise_date,
      exercise_type: formData.exercise_type,
      duration_minutes: formData.duration_minutes,
      notes: formData.notes || ''
    };
    
    if (showAddForm.value) {
      // 添加新记录
      await apiCall('/exercise-records/', {
        method: 'POST',
        body: JSON.stringify(recordData)
      });
    } else {
      // 编辑现有记录
      await apiCall(`/exercise-records/${editingRecord.value.id}/`, {
        method: 'PUT',
        body: JSON.stringify(recordData)
      });
    }
    closeModal();
    await loadExerciseRecords();
    await loadWeeklyStats();
  } catch (error) {
    console.error('保存运动记录失败:', error);
    alert('保存失败: ' + error.message);
  } finally {
    saving.value = false;
  }
};

const editRecord = (record) => {
  editingRecord.value = record;
  formData.exercise_date = record.exercise_date;
  formData.exercise_type = record.exercise_type;
  formData.duration_minutes = record.duration_minutes;
  formData.notes = record.notes || '';
  showEditForm.value = true;
};

const deleteRecord = (record) => {
  recordToDelete.value = record;
  showDeleteModal.value = true;
};

const confirmDelete = async () => {
  try {
    deleting.value = true;
    
    await apiCall(`/exercise-records/${recordToDelete.value.id}/`, {
      method: 'DELETE'
    });
    
    closeDeleteModal();
    await loadExerciseRecords();
    await loadWeeklyStats();
  } catch (error) {
    console.error('删除运动记录失败:', error);
    alert('删除失败: ' + error.message);
  } finally {
    deleting.value = false;
  }
};

const closeModal = () => {
  showAddForm.value = false;
  showEditForm.value = false;
  editingRecord.value = null;
  
  // 重置表单
  formData.exercise_date = '';
  formData.exercise_type = '';
  formData.duration_minutes = '';
  formData.notes = '';
};

const closeDeleteModal = () => {
  showDeleteModal.value = false;
  recordToDelete.value = null;
};

const clearFilters = () => {
  filterType.value = '';
  filterDate.value = '';
  loadExerciseRecords();
};

// 工具函数
const formatDate = (dateString) => {
  const date = new Date(dateString);
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit'
  });
};

const getExerciseIcon = (exerciseType) => {
  const type = exerciseTypes.find(t => t.value === exerciseType);
  return type ? type.icon : '🏃‍♀️';
};

const getIntensityClass = (intensity) => {
  const intensityMap = {
    '低强度': 'low',
    '中强度': 'medium',
    '高强度': 'high'
  };
  return intensityMap[intensity] || 'medium';
};
</script>

<style scoped>
.page-title {
  color: var(--color-text-primary);
}

/* 运动记录表单美化样式 */
.exercise-modal {
  max-width: 600px;
  border-radius: 20px;
  overflow: hidden;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
  animation: modalSlideIn 0.3s ease-out;
}

@keyframes modalSlideIn {
  from {
    opacity: 0;
    transform: translateY(-20px) scale(0.95);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

.exercise-header {
  background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
  padding: 24px 28px;
  color: white;
  display: flex;
  align-items: center;
  gap: 16px;
  position: relative;
}

.header-icon {
  background: rgba(255, 255, 255, 0.2);
  border-radius: 12px;
  padding: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.form-icon {
  font-size: 24px;
  display: block;
}

.header-text {
  flex: 1;
}

.modal-title {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
  line-height: 1.2;
}

.modal-subtitle {
  margin: 4px 0 0 0;
  font-size: 14px;
  opacity: 0.9;
  line-height: 1.4;
}

.modal-close-btn {
  background: rgba(255, 255, 255, 0.2);
  border: none;
  color: white;
  font-size: 18px;
  width: 32px;
  height: 32px;
  border-radius: 8px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
}

.modal-close-btn:hover {
  background: rgba(255, 255, 255, 0.3);
  transform: scale(1.1);
}

.exercise-form {
  padding: 28px;
  background: white;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  margin-bottom: 20px;
}

.form-group {
  margin-bottom: 24px;
}

.form-label {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  font-weight: 600;
  color: #374151;
  margin-bottom: 8px;
  line-height: 1.4;
}

.label-icon {
  font-size: 16px;
}

.required {
  color: #ef4444;
  font-weight: 700;
}

.optional {
  color: #6b7280;
  font-weight: 400;
  font-size: 12px;
}

.form-input {
  width: 100%;
  padding: 12px 16px;
  border: 2px solid #e5e7eb;
  border-radius: 12px;
  font-size: 14px;
  transition: all 0.2s ease;
  background: #fafafa;
  color: black;
}

.form-input::placeholder {
  color: #999;
}

.form-input:focus {
  outline: none;
  border-color: #3b82f6;
  background: white;
  box-shadow: 0 0 0 4px rgba(59, 130, 246, 0.1);
  transform: translateY(-1px);
}

.form-input:hover:not(:focus) {
  border-color: #d1d5db;
  background: white;
}

.date-input, .form-select {
  cursor: pointer;
  color: black
}

.form-select {
  appearance: none;
  background-image: url("data:image/svg+xml,%3csvg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 20 20'%3e%3cpath stroke='%236b7280' stroke-linecap='round' stroke-linejoin='round' stroke-width='1.5' d='m6 8 4 4 4-4'/%3e%3c/svg%3e");
  background-position: right 12px center;
  background-repeat: no-repeat;
  background-size: 16px;
  padding-right: 40px;
}

.form-select:has(option[value=""]:checked) {
  color: #999;
}

.form-select
option[value=""] {
  color: #999;
}

.duration-group {
  position: relative;
}

.duration-input-container {
  position: relative;
  display: flex;
  align-items: center;
}

.duration-input {
  padding-right: 60px;
}

.input-suffix {
  position: absolute;
  right: 16px;
  color: #6b7280;
  font-size: 14px;
  font-weight: 500;
  pointer-events: none;
}

.quick-duration {
  margin-top: 12px;
  padding: 16px;
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
  border-radius: 12px;
  border: 1px solid #e2e8f0;
}

.quick-label {
  font-size: 12px;
  color: #64748b;
  font-weight: 600;
  margin-bottom: 8px;
  display: block;
}

.quick-buttons {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.quick-duration-btn {
  padding: 6px 12px;
  font-size: 12px;
  border-radius: 8px;
  transition: all 0.2s ease;
  position: relative;
}

.quick-duration-btn.active {
  background: #3b82f6;
  color: white;
  border-color: #3b82f6;
  transform: scale(1.05);
  box-shadow: 0 4px 8px rgba(59, 130, 246, 0.3);
}

.quick-duration-btn:hover:not(.active) {
  background: #e2e8f0;
  border-color: #cbd5e1;
  transform: translateY(-1px);
}

.form-textarea {
  resize: vertical;
  min-height: 80px;
  font-family: inherit;
  line-height: 1.5;
}

.textarea-counter {
  text-align: right;
  font-size: 12px;
  color: #6b7280;
  margin-top: 4px;
}

.form-actions {
  display: flex;
  gap: 16px;
  justify-content: flex-end;
  margin-top: 32px;
  padding-top: 24px;
  border-top: 1px solid #f3f4f6;
}

.btn-primary {
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

.btn-secondary {
  background: #f3f4f6;
  color: #374151;
  border: 2px solid #e5e7eb;
}

.btn-secondary:hover {
  background: #e5e7eb;
  border-color: #d1d5db;
}

.loading-content, .submit-content {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.loading-spinner {
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top: 2px solid white;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.btn-icon {
  font-size: 14px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .exercise-modal {
    max-width: 95vw;
    margin: 20px;
    border-radius: 16px;
  }
  
  .exercise-header {
    padding: 20px;
    flex-direction: column;
    text-align: center;
    gap: 12px;
  }
  
  .header-text {
    order: 1;
  }
  
  .modal-close-btn {
    position: absolute;
    top: 16px;
    right: 16px;
  }
  
  .exercise-form {
    padding: 20px;
  }
  
  .form-row {
    grid-template-columns: 1fr;
    gap: 16px;
    margin-bottom: 16px;
  }
  
  .quick-buttons {
    justify-content: center;
  }
  
  .form-actions {
    flex-direction: column;
    gap: 12px;
  }
  
  .form-actions .btn {
    width: 100%;
  }
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
  text-align: center;
  width: 100%;
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

.detail-value.calories-value {
  color: #ea580c;
  background: #fed7aa;
  padding: 4px 8px;
  border-radius: 6px;
  font-size: 13px;
}

.detail-value.notes-text {
  color: #4b5563;
  font-weight: 400;
  font-style: italic;
  max-width: 200px;
  word-break: break-word;
}

.intensity-badge {
  padding: 4px 8px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 600;
}

.intensity-badge.low {
  background: #dcfce7;
  color: #166534;
}

.intensity-badge.medium {
  background: #fef3c7;
  color: #92400e;
}

.intensity-badge.high {
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

.modal-close {
  background: rgba(153, 27, 27, 0.1);
  border: none;
  color: #991b1b;
  font-size: 18px;
  width: 32px;
  height: 32px;
  border-radius: 8px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
  position: absolute;
  top: 16px;
  right: 16px;
}

.modal-close:hover {
  background: rgba(153, 27, 27, 0.2);
  transform: scale(1.1);
}

/* 按钮加载状态 */
.delete-btn:disabled .btn-icon {
  animation: spin 1s linear infinite;
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
  
  .detail-value.notes-text {
    max-width: 100%;
  }
}
</style>