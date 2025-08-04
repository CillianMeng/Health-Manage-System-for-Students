<template>
  <div class="exercise-records">
    <!-- 页面头部 -->
    <div class="page-header">
      <h2>运动记录管理</h2>
      <p class="page-description">记录每日运动情况，追踪健身进度</p>
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

    <!-- 操作区域 -->
    <div class="actions-section">
      <button @click="showAddForm = true" class="add-btn">
        <span class="btn-icon">➕</span>
        添加运动记录
      </button>
      
      <div class="filters">
        <select v-model="filterType" @change="loadExerciseRecords" class="filter-select">
          <option value="">所有运动类型</option>
          <option v-for="type in exerciseTypes" :key="type.value" :value="type.value">
            {{ type.label }}
          </option>
        </select>
        
        <input 
          type="date" 
          v-model="filterDate" 
          @change="loadExerciseRecords"
          class="filter-date"
        />
        
        <button @click="clearFilters" class="clear-filters-btn">清除筛选</button>
      </div>
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
        <button @click="showAddForm = true" class="empty-action-btn">添加首条记录</button>
      </div>
      
      <div v-else class="records-list">
        <div class="records-header">
          <h3>运动记录列表</h3>
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
                  class="action-btn edit-btn"
                  title="编辑"
                >
                  ✏️
                </button>
                <button 
                  @click="deleteRecord(record)" 
                  class="action-btn delete-btn"
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
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>{{ showAddForm ? '添加运动记录' : '编辑运动记录' }}</h3>
          <button @click="closeModal" class="modal-close-btn">✕</button>
        </div>
        
        <form @submit.prevent="saveRecord" class="exercise-form">
          <div class="form-group">
            <label for="exercise-date">运动日期 *</label>
            <input 
              type="date" 
              id="exercise-date"
              v-model="formData.exercise_date" 
              :max="today"
              required 
              class="form-input"
            />
          </div>
          
          <div class="form-group">
            <label for="exercise-type">运动类型 *</label>
            <select 
              id="exercise-type"
              v-model="formData.exercise_type" 
              required 
              class="form-input"
            >
              <option value="">请选择运动类型</option>
              <option v-for="type in exerciseTypes" :key="type.value" :value="type.value">
                {{ type.icon }} {{ type.label }}
              </option>
            </select>
          </div>
          
          <div class="form-group">
            <label for="duration">运动时长 (分钟) *</label>
            <div class="duration-input-group">
              <input 
                type="number" 
                id="duration"
                v-model.number="formData.duration_minutes" 
                min="1" 
                max="480" 
                required 
                class="form-input"
                placeholder="请输入运动时长"
              />
              <div class="quick-duration">
                <button 
                  type="button" 
                  v-for="duration in quickDurations" 
                  :key="duration"
                  @click="formData.duration_minutes = duration"
                  class="quick-btn"
                >
                  {{ duration }}分钟
                </button>
              </div>
            </div>
          </div>
          
          <div class="form-group">
            <label for="notes">备注</label>
            <textarea 
              id="notes"
              v-model="formData.notes" 
              rows="3" 
              class="form-input"
              placeholder="记录运动感受、地点等信息（可选）"
            ></textarea>
          </div>
          
          <div class="form-actions">
            <button type="button" @click="closeModal" class="cancel-btn">取消</button>
            <button type="submit" :disabled="saving" class="save-btn">
              <span v-if="saving">保存中...</span>
              <span v-else>{{ showAddForm ? '添加记录' : '保存修改' }}</span>
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- 删除确认模态框 -->
    <div v-if="showDeleteModal" class="modal-overlay" @click="closeDeleteModal">
      <div class="modal-content delete-modal" @click.stop>
        <div class="modal-header">
          <h3>确认删除</h3>
          <button @click="closeDeleteModal" class="modal-close-btn">✕</button>
        </div>
        
        <div class="delete-content">
          <div class="delete-icon">⚠️</div>
          <p>确定要删除这条运动记录吗？</p>
          <div class="delete-details">
            <p><strong>日期：</strong>{{ formatDate(recordToDelete?.exercise_date) }}</p>
            <p><strong>运动：</strong>{{ recordToDelete?.exercise_type_display }}</p>
            <p><strong>时长：</strong>{{ recordToDelete?.duration_minutes }} 分钟</p>
          </div>
          <p class="delete-warning">此操作无法撤销！</p>
        </div>
        
        <div class="form-actions">
          <button @click="closeDeleteModal" class="cancel-btn">取消</button>
          <button @click="confirmDelete" :disabled="deleting" class="delete-confirm-btn">
            <span v-if="deleting">删除中...</span>
            <span v-else>确认删除</span>
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
    
    alert(showAddForm.value ? '运动记录添加成功！' : '运动记录更新成功！');
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
    
    alert('运动记录删除成功！');
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
.exercise-records {
  padding: 24px;
  max-width: 1200px;
  margin: 0 auto;
}

.page-header {
  margin-bottom: 32px;
}

.page-header h2 {
  font-size: 28px;
  color: #2c3e50;
  margin: 0 0 8px 0;
}

.page-description {
  color: #7f8c8d;
  font-size: 16px;
  margin: 0;
}

/* 统计概览样式 */
.stats-overview {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
  margin-bottom: 32px;
}

.stat-card {
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  display: flex;
  align-items: center;
  gap: 16px;
  transition: transform 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-2px);
}

.stat-icon {
  font-size: 32px;
  width: 60px;
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 50%;
  filter: grayscale(0);
}

.stat-content h3 {
  font-size: 24px;
  font-weight: bold;
  color: #2c3e50;
  margin: 0 0 4px 0;
}

.stat-label {
  color: #7f8c8d;
  font-size: 14px;
  margin: 0;
}

/* 图表区域 */
.chart-section {
  margin-bottom: 32px;
}

/* 操作区域样式 */
.actions-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  flex-wrap: wrap;
  gap: 16px;
}

.add-btn {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 8px;
}

.add-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.filters {
  display: flex;
  gap: 12px;
  align-items: center;
}

.filter-select,
.filter-date {
  padding: 8px 12px;
  border: 2px solid #e9ecef;
  border-radius: 6px;
  font-size: 14px;
  transition: border-color 0.3s ease;
}

.filter-select:focus,
.filter-date:focus {
  outline: none;
  border-color: #667eea;
}

.clear-filters-btn {
  padding: 8px 16px;
  background: #f8f9fa;
  border: 1px solid #dee2e6;
  border-radius: 6px;
  color: #6c757d;
  cursor: pointer;
  transition: all 0.3s ease;
}

.clear-filters-btn:hover {
  background: #e9ecef;
}

/* 记录列表样式 */
.records-section {
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.loading-state,
.empty-state {
  padding: 60px 20px;
  text-align: center;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #667eea;
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
  color: #2c3e50;
  margin-bottom: 8px;
}

.empty-state p {
  color: #7f8c8d;
  margin-bottom: 24px;
}

.empty-action-btn {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.records-header {
  padding: 20px 24px;
  border-bottom: 1px solid #e9ecef;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.records-header h3 {
  color: #2c3e50;
  margin: 0;
}

.records-count {
  color: #7f8c8d;
  font-size: 14px;
}

/* 表格样式 */
.records-table {
  width: 100%;
}

.table-header,
.table-row {
  display: grid;
  grid-template-columns: 120px 140px 100px 100px 100px 120px;
  align-items: center;
  padding: 16px 24px;
  gap: 16px;
}

.table-header {
  background: #f8f9fa;
  font-weight: 600;
  color: #495057;
  border-bottom: 1px solid #e9ecef;
}

.table-row {
  border-bottom: 1px solid #f8f9fa;
  transition: background-color 0.3s ease;
}

.table-row:hover {
  background: #f8f9fa;
}

.exercise-type {
  display: flex;
  align-items: center;
  gap: 8px;
}

.type-icon {
  font-size: 18px;
}

.intensity-badge {
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
}

.intensity-badge.low {
  background: #d4edda;
  color: #155724;
}

.intensity-badge.medium {
  background: #fff3cd;
  color: #856404;
}

.intensity-badge.high {
  background: #f8d7da;
  color: #721c24;
}

.action-btn {
  background: none;
  border: none;
  padding: 8px;
  cursor: pointer;
  border-radius: 4px;
  transition: background-color 0.3s ease;
  font-size: 16px;
}

.action-btn:hover {
  background: #e9ecef;
}

.delete-btn:hover {
  background: #f8d7da;
}

/* 模态框样式 */
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
  max-width: 500px;
  width: 90vw;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
}

.modal-header {
  padding: 20px 24px;
  border-bottom: 1px solid #e9ecef;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.modal-header h3 {
  margin: 0;
  color: #2c3e50;
}

.modal-close-btn {
  background: none;
  border: none;
  font-size: 20px;
  cursor: pointer;
  color: #6c757d;
  padding: 4px;
  border-radius: 4px;
}

.modal-close-btn:hover {
  background: #f8f9fa;
}

/* 表单样式 */
.exercise-form {
  padding: 24px;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 6px;
  color: #495057;
  font-weight: 500;
}

.form-input {
  width: 100%;
  padding: 10px 12px;
  border: 2px solid #e9ecef;
  border-radius: 6px;
  font-size: 14px;
  transition: border-color 0.3s ease;
  box-sizing: border-box;
}

.form-input:focus {
  outline: none;
  border-color: #667eea;
}

.duration-input-group {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.quick-duration {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.quick-btn {
  padding: 6px 12px;
  background: #f8f9fa;
  border: 1px solid #dee2e6;
  border-radius: 4px;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.quick-btn:hover {
  background: #667eea;
  color: white;
  border-color: #667eea;
}

.form-actions {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
  margin-top: 24px;
}

.cancel-btn {
  padding: 10px 20px;
  background: #f8f9fa;
  color: #6c757d;
  border: 1px solid #dee2e6;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.cancel-btn:hover {
  background: #e9ecef;
}

.save-btn {
  padding: 10px 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.save-btn:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 4px 8px rgba(102, 126, 234, 0.3);
}

.save-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* 删除模态框样式 */
.delete-modal {
  max-width: 400px;
}

.delete-content {
  padding: 24px;
  text-align: center;
}

.delete-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

.delete-details {
  background: #f8f9fa;
  padding: 16px;
  border-radius: 8px;
  margin: 16px 0;
  text-align: left;
}

.delete-details p {
  margin: 4px 0;
  font-size: 14px;
}

.delete-warning {
  color: #dc3545;
  font-weight: 500;
  margin-top: 16px;
}

.delete-confirm-btn {
  padding: 10px 20px;
  background: #dc3545;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.delete-confirm-btn:hover:not(:disabled) {
  background: #c82333;
}

.delete-confirm-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .exercise-records {
    padding: 16px;
  }
  
  .stats-overview {
    grid-template-columns: 1fr;
  }
  
  .actions-section {
    flex-direction: column;
    align-items: stretch;
  }
  
  .filters {
    justify-content: center;
  }
  
  .table-header,
  .table-row {
    grid-template-columns: 1fr;
    gap: 8px;
  }
  
  .modal-content {
    margin: 20px;
    width: calc(100vw - 40px);
  }
}
</style>
