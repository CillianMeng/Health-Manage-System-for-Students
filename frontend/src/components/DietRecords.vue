<template>
  <div class="diet-records">
    <div class="page-header">
      <h2>饮食记录管理</h2>
      <button @click="showAddForm = true" class="btn btn-primary">
        <span class="icon">+</span>
        添加饮食记录
      </button>
    </div>

    <!-- 统计概览卡片 -->
    <div class="stats-cards">
      <div class="stat-card">
        <div class="stat-icon calories">📊</div>
        <div class="stat-content">
          <div class="stat-label">今日摄入</div>
          <div class="stat-value">{{ todayCalories }} kcal</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon target">🎯</div>
        <div class="stat-content">
          <div class="stat-label">目标达成率</div>
          <div class="stat-value" :class="getAchievementClass(targetAchievement)">{{ targetAchievement }}%</div>
          <div class="stat-subtitle">
            已摄入 {{ todayCalories }} / 2000 kcal
          </div>
          <div class="achievement-indicator">
            <div class="progress-bar">
              <div class="progress-fill" 
                   :class="getAchievementClass(targetAchievement)"
                   :style="{ width: Math.min(targetAchievement, 100) + '%' }"></div>
            </div>
          </div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon balance">⚖️</div>
        <div class="stat-content">
          <div class="stat-label">营养均衡</div>
          <div class="stat-value">{{ nutritionScore }}分</div>
        </div>
      </div>
    </div>

    <!-- 筛选器 -->
    <div class="filters">
      <div class="filter-group">
        <label>日期范围:</label>
        <input v-model="filters.startDate" type="date" class="filter-input">
        <input v-model="filters.endDate" type="date" class="filter-input">
      </div>
      <div class="filter-group">
        <label>餐次:</label>
        <select v-model="filters.mealType" class="filter-select">
          <option value="">全部餐次</option>
          <option value="breakfast">早餐</option>
          <option value="lunch">午餐</option>
          <option value="dinner">晚餐</option>
          <option value="snack">加餐</option>
        </select>
      </div>
      <button @click="applyFilters" class="btn btn-secondary">筛选</button>
      <button @click="clearFilters" class="btn btn-outline">清除</button>
    </div>

    <!-- 饮食记录列表 -->
    <div class="records-section">
      <div v-if="loading" class="loading">
        <div class="spinner"></div>
        <p>加载中...</p>
      </div>

      <div v-else-if="groupedRecords.length === 0" class="empty-state">
        <div class="empty-icon">🍽️</div>
        <h3>暂无饮食记录</h3>
        <p>点击上方按钮添加您的第一条饮食记录</p>
      </div>

      <div v-else class="records-list">
        <div v-for="group in groupedRecords" :key="group.date" class="date-group">
          <div class="date-header">
            <h3>{{ formatDate(group.date) }}</h3>
            <div class="date-summary">
              <span class="total-calories">{{ group.totalCalories }} kcal</span>
              <span class="meal-count">{{ group.records.length }} 条记录</span>
            </div>
          </div>
          
          <div class="meal-groups">
            <div v-for="mealGroup in group.mealGroups" :key="mealGroup.mealType" class="meal-group">
              <div class="meal-header">
                <span class="meal-icon">{{ getMealIcon(mealGroup.mealType) }}</span>
                <span class="meal-name">{{ getMealTypeName(mealGroup.mealType) }}</span>
                <span class="meal-calories">{{ mealGroup.totalCalories }} kcal</span>
              </div>
              
              <div class="meal-records">
                <div v-for="record in mealGroup.records" :key="record.id" class="record-item">
                  <div class="record-content">
                    <div class="food-info">
                      <span class="food-name">{{ record.food_name }}</span>
                      <span class="food-details">
                        {{ record.portion_size }}g · {{ record.calories_per_100g }}kcal/100g
                      </span>
                    </div>
                    <div class="record-calories">{{ record.total_calories }} kcal</div>
                    <div class="record-actions">
                      <button @click="editRecord(record)" class="btn-icon edit" title="编辑">
                        ✏️
                      </button>
                      <button @click="deleteRecord(record)" class="btn-icon delete" title="删除">
                        🗑️
                      </button>
                    </div>
                  </div>
                  <div v-if="record.notes" class="record-notes">{{ record.notes }}</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 一周统计图表 -->
    <div class="chart-section">
      <DietChart :weeklyStats="weeklyStats" />
    </div>

    <!-- 添加/编辑表单模态框 -->
    <div v-if="showAddForm || editingRecord" class="modal-overlay" @click="closeForm">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>{{ editingRecord ? '编辑' : '添加' }}饮食记录</h3>
          <button @click="closeForm" class="btn-close">×</button>
        </div>
        
        <form @submit.prevent="submitForm" class="diet-form">
          <div class="form-group">
            <label for="diet_date">日期 *</label>
            <input 
              id="diet_date"
              v-model="form.diet_date" 
              type="date" 
              required 
              :max="today"
              class="form-input"
            >
          </div>

          <div class="form-group">
            <label for="meal_type">餐次 *</label>
            <select id="meal_type" v-model="form.meal_type" required class="form-select">
              <option value="">请选择餐次</option>
              <option value="breakfast">早餐</option>
              <option value="lunch">午餐</option>
              <option value="dinner">晚餐</option>
              <option value="snack">加餐</option>
            </select>
          </div>

          <div class="form-group">
            <label for="food_name">食物名称 *</label>
            <div class="food-search-container">
              <input 
                id="food_name"
                v-model="form.food_name" 
                type="text" 
                required 
                placeholder="搜索食物或手动输入"
                class="form-input"
                @input="searchFood"
                @focus="showFoodSuggestions = true"
                @blur="hideFoodSuggestions"
              >
              
              <!-- 食物搜索建议 -->
              <div v-if="showFoodSuggestions && form.food_name.length >= 2" class="food-suggestions">
                <div v-if="foodSuggestions.length === 0" class="suggestion-item no-results">
                  <span class="suggestion-info">
                    <span class="suggestion-name">未找到相关食物</span>
                    <span class="suggestion-category">您可以手动输入食物信息</span>
                  </span>
                </div>
                <div 
                  v-for="food in foodSuggestions" 
                  :key="food.id"
                  @click="selectFood(food)"
                  class="suggestion-item"
                >
                  <div class="suggestion-info">
                    <span class="suggestion-name">{{ food.food_name }}</span>
                    <span class="suggestion-category">{{ food.food_category_display }}</span>
                  </div>
                  <div class="suggestion-calories">{{ food.calories_per_100g }} kcal/100g</div>
                </div>
              </div>
            </div>
          </div>

          <div class="form-row">
            <div class="form-group">
              <label for="portion_size">分量 (克/毫升) *</label>
              <input 
                id="portion_size"
                v-model.number="form.portion_size" 
                type="number" 
                required 
                min="1" 
                max="2000"
                placeholder="例如: 150"
                class="form-input"
              >
            </div>

            <div class="form-group">
              <label for="calories_per_100g">每100g卡路里 *</label>
              <input 
                id="calories_per_100g"
                v-model.number="form.calories_per_100g" 
                type="number" 
                required 
                min="1" 
                max="900"
                placeholder="例如: 54"
                class="form-input"
              >
            </div>
          </div>

          <div class="form-group">
            <label>预计总卡路里</label>
            <div class="calculated-calories">
              {{ calculatedCalories }} kcal
            </div>
          </div>

          <div class="form-group">
            <label for="notes">备注</label>
            <textarea 
              id="notes"
              v-model="form.notes" 
              placeholder="可选的备注信息..."
              class="form-textarea"
              rows="3"
            ></textarea>
          </div>

          <div class="form-actions">
            <button type="button" @click="closeForm" class="btn btn-outline">取消</button>
            <button type="submit" :disabled="submitting" class="btn btn-primary">
              {{ submitting ? '保存中...' : (editingRecord ? '更新' : '添加') }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- 删除确认对话框 -->
    <div v-if="deletingRecord" class="modal-overlay" @click="cancelDelete">
      <div class="modal-content confirm-dialog" @click.stop>
        <div class="modal-header">
          <h3>确认删除</h3>
        </div>
        <div class="modal-body">
          <p>确定要删除这条饮食记录吗？</p>
          <div class="record-preview">
            <strong>{{ deletingRecord.food_name }}</strong><br>
            {{ getMealTypeName(deletingRecord.meal_type) }} · 
            {{ deletingRecord.portion_size }}g · 
            {{ deletingRecord.total_calories }}kcal
          </div>
        </div>
        <div class="form-actions">
          <button @click="cancelDelete" class="btn btn-outline">取消</button>
          <button @click="confirmDelete" :disabled="submitting" class="btn btn-danger">
            {{ submitting ? '删除中...' : '确认删除' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, watch } from 'vue'
import DietChart from './DietChart.vue'
import tokenAuthService from '../utils/csrf-auth.js'

// 响应式状态
const loading = ref(false)
const submitting = ref(false)
const showAddForm = ref(false)
const showFoodSuggestions = ref(false)
const editingRecord = ref(null)
const deletingRecord = ref(null)

const records = ref([])
const weeklyStats = ref({})
const foodSuggestions = ref([])

// 表单数据
const form = reactive({
  diet_date: '',
  meal_type: '',
  food_name: '',
  portion_size: '',
  calories_per_100g: '',
  notes: ''
})

// 筛选器
const filters = reactive({
  startDate: '',
  endDate: '',
  mealType: ''
})

// 计算属性
const today = computed(() => {
  return new Date().toISOString().split('T')[0]
})

const calculatedCalories = computed(() => {
  if (form.portion_size && form.calories_per_100g) {
    return Math.round(form.portion_size * form.calories_per_100g / 100)
  }
  return 0
})

const groupedRecords = computed(() => {
  const groups = {}
  
  records.value.forEach(record => {
    const date = record.diet_date
    if (!groups[date]) {
      groups[date] = {
        date,
        records: [],
        totalCalories: 0,
        mealGroups: {}
      }
    }
    
    groups[date].records.push(record)
    groups[date].totalCalories += record.total_calories
    
    // 按餐次分组
    const mealType = record.meal_type
    if (!groups[date].mealGroups[mealType]) {
      groups[date].mealGroups[mealType] = {
        mealType,
        records: [],
        totalCalories: 0
      }
    }
    
    groups[date].mealGroups[mealType].records.push(record)
    groups[date].mealGroups[mealType].totalCalories += record.total_calories
  })
  
  // 转换为数组并排序
  return Object.values(groups)
    .map(group => ({
      ...group,
      mealGroups: Object.values(group.mealGroups).sort((a, b) => {
        const order = { breakfast: 1, lunch: 2, dinner: 3, snack: 4 }
        return order[a.mealType] - order[b.mealType]
      })
    }))
    .sort((a, b) => new Date(b.date) - new Date(a.date))
})

const todayCalories = computed(() => {
  const today = new Date().toISOString().split('T')[0]
  const todayGroup = groupedRecords.value.find(group => group.date === today)
  return todayGroup ? todayGroup.totalCalories : 0
})

const targetAchievement = computed(() => {
  const target = 2000 // 每日目标卡路里
  return Math.round((todayCalories.value / target) * 100)
})

// 根据达成率返回样式类
const getAchievementClass = (rate) => {
  if (rate < 80) return 'achievement-low'
  if (rate > 120) return 'achievement-high'
  return 'achievement-good'
}

const nutritionScore = computed(() => {
  return weeklyStats.value.nutrition_balance_score || 0
})

// 工具函数
const formatDate = (dateStr) => {
  const date = new Date(dateStr)
  const today = new Date()
  const yesterday = new Date(today)
  yesterday.setDate(yesterday.getDate() - 1)
  
  if (dateStr === today.toISOString().split('T')[0]) {
    return '今天'
  } else if (dateStr === yesterday.toISOString().split('T')[0]) {
    return '昨天'
  } else {
    return date.toLocaleDateString('zh-CN', { 
      month: 'long', 
      day: 'numeric',
      weekday: 'short'
    })
  }
}

const getMealIcon = (mealType) => {
  const icons = {
    breakfast: '🌅',
    lunch: '☀️',
    dinner: '🌙',
    snack: '🍎'
  }
  return icons[mealType] || '🍽️'
}

const getMealTypeName = (mealType) => {
  const names = {
    breakfast: '早餐',
    lunch: '午餐',
    dinner: '晚餐',
    snack: '加餐'
  }
  return names[mealType] || mealType
}

// API 调用函数 (使用与睡眠记录相同的模式)
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

const loadRecords = async () => {
  try {
    loading.value = true
    
    // 构建查询参数
    const params = new URLSearchParams()
    if (filters.startDate) params.append('start_date', filters.startDate)
    if (filters.endDate) params.append('end_date', filters.endDate)
    if (filters.mealType) params.append('meal_type', filters.mealType)
    
    const url = `/diet-records/${params.toString() ? '?' + params.toString() : ''}`
    const data = await apiCall(url)
    records.value = data.records || []
  } catch (error) {
    console.error('加载饮食记录失败:', error)
    alert('加载饮食记录失败: ' + error.message)
  } finally {
    loading.value = false
  }
}

const loadWeeklyStats = async () => {
  try {
    const data = await apiCall('/diet-records/weekly/')
    weeklyStats.value = data
  } catch (error) {
    console.error('加载统计数据失败:', error)
  }
}

const searchFood = async () => {
  if (form.food_name.length < 2) {
    foodSuggestions.value = []
    return
  }
  
  try {
    console.log('搜索食物:', form.food_name) // 调试信息
    const data = await apiCall(`/food-calories/?q=${encodeURIComponent(form.food_name)}`)
    console.log('搜索结果:', data) // 调试信息
    
    if (data && data.foods) {
      foodSuggestions.value = data.foods.slice(0, 8) // 限制显示数量
    } else {
      foodSuggestions.value = []
    }
  } catch (error) {
    console.error('搜索食物失败:', error)
    foodSuggestions.value = []
  }
}

// 隐藏食物建议（延迟隐藏以允许点击选择）
const hideFoodSuggestions = () => {
  setTimeout(() => {
    showFoodSuggestions.value = false
  }, 200)
}

const selectFood = (food) => {
  form.food_name = food.food_name
  form.calories_per_100g = food.calories_per_100g
  foodSuggestions.value = []
  showFoodSuggestions.value = false
}

const submitForm = async () => {
  try {
    submitting.value = true
    
    const formData = {
      diet_date: form.diet_date,
      meal_type: form.meal_type,
      food_name: form.food_name,
      portion_size: form.portion_size,
      calories_per_100g: form.calories_per_100g,
      notes: form.notes
    }
    
    if (editingRecord.value) {
      await apiCall(`/diet-records/${editingRecord.value.id}/`, {
        method: 'PUT',
        body: JSON.stringify(formData)
      })
    } else {
      await apiCall('/diet-records/', {
        method: 'POST',
        body: JSON.stringify(formData)
      })
    }
    
    closeForm()
    await loadRecords()
    await loadWeeklyStats()
  } catch (error) {
    console.error('保存失败:', error)
    alert('保存失败: ' + error.message)
  } finally {
    submitting.value = false
  }
}

const editRecord = (record) => {
  editingRecord.value = record
  form.diet_date = record.diet_date
  form.meal_type = record.meal_type
  form.food_name = record.food_name
  form.portion_size = record.portion_size
  form.calories_per_100g = record.calories_per_100g
  form.notes = record.notes || ''
}

const deleteRecord = (record) => {
  deletingRecord.value = record
}

const confirmDelete = async () => {
  try {
    submitting.value = true
    await apiCall(`/diet-records/${deletingRecord.value.id}/`, {
      method: 'DELETE'
    })
    
    deletingRecord.value = null
    await loadRecords()
    await loadWeeklyStats()
  } catch (error) {
    console.error('删除失败:', error)
    alert('删除失败: ' + error.message)
  } finally {
    submitting.value = false
  }
}

const cancelDelete = () => {
  deletingRecord.value = null
}

const closeForm = () => {
  showAddForm.value = false
  editingRecord.value = null
  showFoodSuggestions.value = false
  
  // 重置表单
  Object.keys(form).forEach(key => {
    form[key] = ''
  })
  
  // 设置默认日期
  form.diet_date = today.value
}

const applyFilters = () => {
  loadRecords()
}

const clearFilters = () => {
  filters.startDate = ''
  filters.endDate = ''
  filters.mealType = ''
  loadRecords()
}

// 点击外部关闭建议
const handleClickOutside = () => {
  showFoodSuggestions.value = false
}

// 监听器
watch([() => form.portion_size, () => form.calories_per_100g], () => {
  // 当分量或卡路里改变时重新计算
})

// 生命周期
onMounted(async () => {
  // 确保认证服务已初始化
  await tokenAuthService.initialize();
  
  // 检查是否已登录
  if (!tokenAuthService.isLoggedIn()) {
    console.warn('用户未登录，无法加载饮食记录');
    alert('请先登录后再访问饮食记录页面');
    return;
  }
  
  form.diet_date = today.value
  loadRecords()
  loadWeeklyStats()
  
  // 添加全局点击事件监听
  document.addEventListener('click', handleClickOutside)
})
</script>

<style scoped>
.diet-records {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
}

.page-header h2 {
  margin: 0;
  color: #2c3e50;
  font-size: 28px;
  font-weight: 600;
}

/* 统计卡片 */
.stats-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.stat-card {
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  display: flex;
  align-items: center;
  gap: 15px;
}

.stat-icon {
  font-size: 32px;
  width: 50px;
  height: 50px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.stat-icon.calories {
  background: linear-gradient(135deg, #ff7675, #fd79a8);
}

.stat-icon.target {
  background: linear-gradient(135deg, #00b894, #00cec9);
}

.stat-icon.balance {
  background: linear-gradient(135deg, #fdcb6e, #f39c12);
}

.stat-content {
  flex: 1;
}

.stat-label {
  font-size: 14px;
  color: #7f8c8d;
  margin-bottom: 4px;
}

.stat-value {
  font-size: 24px;
  font-weight: 700;
  color: #2c3e50;
}

.stat-subtitle {
  font-size: 12px;
  color: #95a5a6;
  margin-top: 2px;
}

.achievement-indicator {
  margin-top: 8px;
}

.progress-bar {
  width: 100%;
  height: 6px;
  background-color: #ecf0f1;
  border-radius: 3px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  border-radius: 3px;
  transition: width 0.3s ease;
}

.progress-fill.achievement-low {
  background: linear-gradient(90deg, #e74c3c, #c0392b);
}

.progress-fill.achievement-good {
  background: linear-gradient(90deg, #27ae60, #2ecc71);
}

.progress-fill.achievement-high {
  background: linear-gradient(90deg, #f39c12, #e67e22);
}

.achievement-low {
  color: #e74c3c;
}

.achievement-good {
  color: #27ae60;
}

.achievement-high {
  color: #f39c12;
}

/* 筛选器 */
.filters {
  background: white;
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  display: flex;
  gap: 20px;
  align-items: center;
  flex-wrap: wrap;
}

.filter-group {
  display: flex;
  align-items: center;
  gap: 8px;
}

.filter-group label {
  font-weight: 500;
  color: #2c3e50;
  white-space: nowrap;
}

.filter-input,
.filter-select {
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 14px;
}

/* 记录列表 */
.records-section {
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  margin-bottom: 30px;
}

.loading {
  text-align: center;
  padding: 60px 20px;
  color: #7f8c8d;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #3498db;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 20px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.empty-state {
  text-align: center;
  padding: 60px 20px;
  color: #7f8c8d;
}

.empty-icon {
  font-size: 64px;
  margin-bottom: 20px;
}

.empty-state h3 {
  margin: 0 0 10px;
  color: #2c3e50;
}

.date-group {
  border-bottom: 1px solid #ecf0f1;
}

.date-group:last-child {
  border-bottom: none;
}

.date-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  background: #f8f9fa;
  border-bottom: 1px solid #ecf0f1;
}

.date-header h3 {
  margin: 0;
  color: #2c3e50;
  font-size: 18px;
}

.date-summary {
  display: flex;
  gap: 15px;
  font-size: 14px;
  color: #7f8c8d;
}

.total-calories {
  font-weight: 600;
  color: #e74c3c;
}

.meal-group {
  border-bottom: 1px solid #f8f9fa;
}

.meal-group:last-child {
  border-bottom: none;
}

.meal-header {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 15px 20px;
  background: #fdfdfd;
  border-bottom: 1px solid #f8f9fa;
}

.meal-icon {
  font-size: 20px;
}

.meal-name {
  font-weight: 500;
  color: #2c3e50;
  flex: 1;
}

.meal-calories {
  font-weight: 600;
  color: #27ae60;
  font-size: 14px;
}

.record-item {
  padding: 15px 20px;
  border-bottom: 1px solid #f8f9fa;
}

.record-item:last-child {
  border-bottom: none;
}

.record-content {
  display: flex;
  align-items: center;
  gap: 15px;
}

.food-info {
  flex: 1;
}

.food-name {
  font-weight: 500;
  color: #2c3e50;
  display: block;
  margin-bottom: 4px;
}

.food-details {
  font-size: 12px;
  color: #7f8c8d;
}

.record-calories {
  font-weight: 600;
  color: #e74c3c;
  font-size: 16px;
}

.record-actions {
  display: flex;
  gap: 8px;
}

.btn-icon {
  background: none;
  border: none;
  padding: 4px;
  cursor: pointer;
  border-radius: 4px;
  font-size: 16px;
  transition: background-color 0.2s;
}

.btn-icon:hover {
  background: #f8f9fa;
}

.record-notes {
  margin-top: 8px;
  padding: 8px 12px;
  background: #f8f9fa;
  border-radius: 6px;
  font-size: 14px;
  color: #7f8c8d;
  font-style: italic;
}

/* 图表区域 */
.chart-section {
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  padding: 20px;
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
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
  max-width: 500px;
  width: 90%;
  max-height: 90vh;
  overflow-y: auto;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  border-bottom: 1px solid #ecf0f1;
}

.modal-header h3 {
  margin: 0;
  color: #2c3e50;
}

.btn-close {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #7f8c8d;
  padding: 0;
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
}

.btn-close:hover {
  background: #f8f9fa;
}

/* 表单样式 */
.diet-form {
  padding: 20px;
}

.form-group {
  margin-bottom: 20px;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 15px;
}

.form-group label {
  display: block;
  margin-bottom: 6px;
  font-weight: 500;
  color: #2c3e50;
}

.form-input,
.form-select,
.form-textarea {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 14px;
  transition: border-color 0.2s;
}

.form-input:focus,
.form-select:focus,
.form-textarea:focus {
  outline: none;
  border-color: #3498db;
}

.form-textarea {
  resize: vertical;
  min-height: 80px;
}

/* 食物搜索 */
.food-search-container {
  position: relative;
}

.food-suggestions {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  background: white;
  border: 1px solid #ddd;
  border-top: none;
  border-radius: 0 0 6px 6px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  max-height: 200px;
  overflow-y: auto;
  z-index: 10;
}

.suggestion-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 12px;
  cursor: pointer;
  border-bottom: 1px solid #f8f9fa;
}

.suggestion-item:hover {
  background: #f8f9fa;
}

.suggestion-item:last-child {
  border-bottom: none;
}

.suggestion-item.no-results {
  color: #666;
  font-style: italic;
  cursor: default;
}

.suggestion-item.no-results:hover {
  background-color: transparent;
}

.suggestion-info {
  flex: 1;
}

.suggestion-name {
  font-weight: 500;
  color: #2c3e50;
  display: block;
}

.suggestion-category {
  font-size: 12px;
  color: #7f8c8d;
}

.suggestion-calories {
  font-size: 12px;
  color: #27ae60;
  font-weight: 500;
}

.calculated-calories {
  font-size: 18px;
  font-weight: 600;
  color: #e74c3c;
  padding: 10px 12px;
  background: #f8f9fa;
  border-radius: 6px;
  text-align: center;
}

.form-actions {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
  margin-top: 30px;
  padding-top: 20px;
  border-top: 1px solid #ecf0f1;
}

/* 确认对话框 */
.confirm-dialog {
  max-width: 400px;
}

.modal-body {
  padding: 20px;
}

.record-preview {
  background: #f8f9fa;
  padding: 15px;
  border-radius: 6px;
  margin-top: 15px;
  font-size: 14px;
  color: #2c3e50;
}

/* 按钮样式 */
.btn {
  padding: 10px 16px;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  display: inline-flex;
  align-items: center;
  gap: 6px;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-primary {
  background: #3498db;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: #2980b9;
}

.btn-secondary {
  background: #95a5a6;
  color: white;
}

.btn-secondary:hover:not(:disabled) {
  background: #7f8c8d;
}

.btn-outline {
  background: transparent;
  color: #7f8c8d;
  border: 1px solid #ddd;
}

.btn-outline:hover:not(:disabled) {
  background: #f8f9fa;
}

.btn-danger {
  background: #e74c3c;
  color: white;
}

.btn-danger:hover:not(:disabled) {
  background: #c0392b;
}

.icon {
  font-size: 16px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .diet-records {
    padding: 15px;
  }
  
  .page-header {
    flex-direction: column;
    gap: 15px;
    align-items: stretch;
  }
  
  .stats-cards {
    grid-template-columns: 1fr;
  }
  
  .filters {
    flex-direction: column;
    align-items: stretch;
    gap: 15px;
  }
  
  .filter-group {
    flex-direction: column;
    align-items: stretch;
    gap: 6px;
  }
  
  .date-header {
    flex-direction: column;
    gap: 10px;
    align-items: stretch;
  }
  
  .record-content {
    flex-direction: column;
    align-items: stretch;
    gap: 10px;
  }
  
  .record-actions {
    justify-content: center;
  }
  
  .form-row {
    grid-template-columns: 1fr;
  }
  
  .form-actions {
    flex-direction: column;
  }
  
  .modal-content {
    width: 95%;
    margin: 20px;
  }
}
</style>
