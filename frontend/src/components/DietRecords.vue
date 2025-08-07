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
              <div class="progress-fill" :class="getAchievementClass(targetAchievement)"
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
      <div class="filters-header">
        <div class="filters-title">
          <span class="filters-icon">🔍</span>
          <h3>筛选条件</h3>
        </div>
        <button @click="clearFilters" class="btn btn-outline btn-sm clear-btn">
          <span class="btn-icon">🗑️</span>
          清除筛选
        </button>
      </div>
      
      <div class="filters-content">
        <div class="filter-group">
          <label class="filter-label">
            <span class="label-icon">📅</span>
            日期范围
          </label>
          <div class="date-range">
            <input 
              v-model="filters.startDate" 
              type="date" 
              class="filter-input date-input"
              placeholder="开始日期"
            >
            <span class="date-separator">至</span>
            <input 
              v-model="filters.endDate" 
              type="date" 
              class="filter-input date-input"
              placeholder="结束日期"
            >
          </div>
        </div>
        
        <div class="filter-group">
          <label class="filter-label">
            <span class="label-icon">🍴</span>
            餐次类型
          </label>
          <select v-model="filters.mealType" class="filter-select">
            <option value="">全部餐次</option>
            <option value="breakfast">🌅 早餐</option>
            <option value="lunch">☀️ 午餐</option>
            <option value="dinner">🌙 晚餐</option>
            <option value="snack">🍎 加餐</option>
          </select>
        </div>
        
        <div class="filter-actions">
          <button @click="applyFilters" class="btn btn-primary filter-apply-btn">
            <span class="btn-icon">🔍</span>
            应用筛选
          </button>
        </div>
      </div>
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
                      <button @click="editRecord(record)" class="btn btn-sm" title="编辑">
                        ✏️
                      </button>
                      <button @click="deleteRecord(record)" class="btn btn-sm btn-danger" title="删除">
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
      <div class="modal-content diet-modal" @click.stop>
        <div class="modal-header diet-header">
          <div class="header-icon">
            <span class="form-icon">🍽️</span>
          </div>
          <div class="header-text">
            <h3 class="modal-title">{{ editingRecord ? '编辑饮食记录' : '添加饮食记录' }}</h3>
            <p class="modal-subtitle">记录您的饮食数据，追踪营养摄入</p>
          </div>
          <button @click="closeForm" class="modal-close-btn">✕</button>
        </div>

        <form @submit.prevent="submitForm" class="diet-form">
          <div class="form-row">
            <div class="form-group">
              <label for="diet_date" class="form-label">
                <span class="label-icon">📅</span>
                日期
                <span class="required">*</span>
              </label>
              <input 
                id="diet_date" 
                v-model="form.diet_date" 
                type="date" 
                required 
                :max="today" 
                class="form-input date-input"
              >
            </div>

            <div class="form-group">
              <label for="meal_type" class="form-label">
                <span class="label-icon">🍴</span>
                餐次
                <span class="required">*</span>
              </label>
              <select id="meal_type" v-model="form.meal_type" required class="form-input form-select">
                <option value="" disabled>请选择餐次</option>
                <option value="breakfast">🌅 早餐</option>
                <option value="lunch">☀️ 午餐</option>
                <option value="dinner">🌙 晚餐</option>
                <option value="snack">🍎 加餐</option>
              </select>
            </div>
          </div>

          <div class="form-group">
            <label for="food_name" class="form-label">
              <span class="label-icon">🥗</span>
              食物名称
              <span class="required">*</span>
            </label>
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
                <div v-for="food in foodSuggestions" :key="food.id" @click="selectFood(food)" class="suggestion-item">
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
              <label for="portion_size" class="form-label">
                <span class="label-icon">⚖️</span>
                分量 (克/毫升)
                <span class="required">*</span>
              </label>
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
              <label for="calories_per_100g" class="form-label">
                <span class="label-icon">🔥</span>
                每100g卡路里
                <span class="required">*</span>
              </label>
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
            <label class="form-label">
              <span class="label-icon">📊</span>
              预计总卡路里
            </label>
            <div class="calculated-calories">
              {{ calculatedCalories }} kcal
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
              v-model="form.notes" 
              placeholder="可选的备注信息..." 
              class="form-input form-textarea"
              rows="3"
            ></textarea>
            <div class="textarea-counter">
              {{ form.notes?.length || 0 }}/200
            </div>
          </div>

          <div class="form-actions">
            <button type="button" @click="closeForm" class="btn btn-secondary btn-lg">
              <span class="btn-icon">↩️</span>
              取消
            </button>
            <button type="submit" :disabled="submitting" class="btn btn-primary btn-lg submit-btn">
              <span v-if="submitting" class="loading-content">
                <span class="loading-spinner"></span>
                保存中...
              </span>
              <span v-else class="submit-content">
                <span class="btn-icon">{{ editingRecord ? '💾' : '➕' }}</span>
                {{ submitting ? '保存中...' : (editingRecord ? '更新' : '添加') }}
              </span>
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- 删除确认对话框 -->
    <div v-if="deletingRecord" class="modal-overlay" @click="cancelDelete">
      <div class="modal-content delete-modal" @click.stop>
        <div class="modal-header delete-header">
          <div class="delete-icon">
            <span class="warning-icon">⚠️</span>
          </div>
          <h3 class="delete-title">确认删除饮食记录</h3>
          <button @click="cancelDelete" class="modal-close">✕</button>
        </div>
        
        <div class="modal-body delete-body">
          <div class="delete-warning">
            <p class="delete-message">您确定要删除这条饮食记录吗？此操作无法撤销。</p>
          </div>
          
          <div class="delete-record-info">
            <div class="record-detail-card">
              <div class="detail-row">
                <span class="detail-label">📅 饮食日期</span>
                <span class="detail-value">{{ formatDate(deletingRecord.diet_date) }}</span>
              </div>
              <div class="detail-row">
                <span class="detail-label">🍴 餐次类型</span>
                <span class="detail-value">{{ getMealIcon(deletingRecord.meal_type) }} {{ getMealTypeName(deletingRecord.meal_type) }}</span>
              </div>
              <div class="detail-row">
                <span class="detail-label">🥗 食物名称</span>
                <span class="detail-value highlight">{{ deletingRecord.food_name }}</span>
              </div>
              <div class="detail-row">
                <span class="detail-label">⚖️ 食用分量</span>
                <span class="detail-value">{{ deletingRecord.portion_size }} 克</span>
              </div>
              <div class="detail-row">
                <span class="detail-label">🔥 摄入卡路里</span>
                <span class="detail-value calories-value">{{ deletingRecord.total_calories }} 卡</span>
              </div>
              <div class="detail-row">
                <span class="detail-label">📊 单位热量</span>
                <span class="detail-value">{{ deletingRecord.calories_per_100g }} 卡/100g</span>
              </div>
              <div class="detail-row" v-if="deletingRecord.notes">
                <span class="detail-label">📝 备注信息</span>
                <span class="detail-value notes-text">{{ deletingRecord.notes }}</span>
              </div>
            </div>
          </div>
        </div>
        
        <div class="form-actions delete-actions">
          <button @click="cancelDelete" class="btn-secondary cancel-btn">
            <span class="btn-icon">↩️</span>
            取消
          </button>
          <button @click="confirmDelete" :disabled="submitting" class="btn-danger delete-btn">
            <span class="btn-icon">🗑️</span>
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
@import '../styles/components/diet-records.css';

/* 饮食记录表单美化样式 */
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
  padding: 20px;
  overflow-y: auto;
}

.diet-modal {
  max-width: 600px;
  width: 100%;
  max-height: 90vh;
  border-radius: 20px;
  overflow: hidden;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
  animation: modalSlideIn 0.3s ease-out;
  margin: auto;
  display: flex;
  flex-direction: column;
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

.diet-header {
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
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

.diet-form {
  padding: 28px;
  background: white;
  overflow-y: auto;
  flex: 1;
  max-height: calc(90vh - 100px);
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
}

.form-input:focus {
  outline: none;
  border-color: #10b981;
  background: white;
  box-shadow: 0 0 0 4px rgba(16, 185, 129, 0.1);
  transform: translateY(-1px);
}

.form-input:hover:not(:focus) {
  border-color: #d1d5db;
  background: white;
}

.date-input, .form-select {
  cursor: pointer;
}

.form-select {
  appearance: none;
  background-image: url("data:image/svg+xml,%3csvg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 20 20'%3e%3cpath stroke='%236b7280' stroke-linecap='round' stroke-linejoin='round' stroke-width='1.5' d='m6 8 4 4 4-4'/%3e%3c/svg%3e");
  background-position: right 12px center;
  background-repeat: no-repeat;
  background-size: 16px;
  padding-right: 40px;
}

.food-search-container {
  position: relative;
}

.food-suggestions {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  background: white;
  border: 2px solid #e5e7eb;
  border-top: none;
  border-radius: 0 0 12px 12px;
  max-height: 200px;
  overflow-y: auto;
  z-index: 1000;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
}

.suggestion-item {
  padding: 12px 16px;
  cursor: pointer;
  border-bottom: 1px solid #f3f4f6;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.suggestion-item:hover {
  background: #f9fafb;
}

.suggestion-item:last-child {
  border-bottom: none;
}

.suggestion-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.suggestion-name {
  font-weight: 500;
  color: #374151;
}

.suggestion-category {
  font-size: 12px;
  color: #6b7280;
}

.suggestion-calories {
  font-size: 12px;
  color: #10b981;
  font-weight: 600;
}

.calculated-calories {
  padding: 12px 16px;
  background: linear-gradient(135deg, #ecfdf5 0%, #d1fae5 100%);
  border: 2px solid #10b981;
  border-radius: 12px;
  font-size: 18px;
  font-weight: 600;
  color: #059669;
  text-align: center;
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

.btn-lg {
  padding: 12px 24px;
  font-size: 16px;
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

.btn-primary {
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  color: white;
  border: 2px solid #10b981;
}

.btn-primary:hover:not(:disabled) {
  background: linear-gradient(135deg, #059669 0%, #047857 100%);
  border-color: #059669;
  transform: translateY(-1px);
}

.submit-btn {
  min-width: 140px;
  position: relative;
}

.submit-btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
  transform: none;
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

/* 筛选器美化样式 */
.filters {
  background: white;
  border-radius: 16px;
  padding: 24px;
  margin-bottom: 24px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
  border: 1px solid #e5e7eb;
}

.filters-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 1px solid #f3f4f6;
}

.filters-title {
  display: flex;
  align-items: center;
  gap: 12px;
}

.filters-icon {
  font-size: 20px;
}

.filters-title h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #374151;
}

.clear-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  font-size: 14px;
  border-radius: 8px;
  transition: all 0.2s ease;
}

.filters-content {
  display: grid;
  grid-template-columns: 1fr 1fr auto;
  gap: 24px;
  align-items: end;
}

.filter-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.filter-label {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  font-weight: 600;
  color: #374151;
  margin-bottom: 4px;
}

.label-icon {
  font-size: 16px;
}

.date-range {
  display: flex;
  align-items: center;
  gap: 12px;
}

.date-separator {
  color: #6b7280;
  font-size: 14px;
  font-weight: 500;
  white-space: nowrap;
}

.filter-input {
  padding: 10px 14px;
  border: 2px solid #e5e7eb;
  border-radius: 10px;
  font-size: 14px;
  transition: all 0.2s ease;
  background: #fafafa;
  min-width: 140px;
}

.filter-input:focus {
  outline: none;
  border-color: #10b981;
  background: white;
  box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.1);
}

.filter-input:hover:not(:focus) {
  border-color: #d1d5db;
  background: white;
}

.filter-select {
  padding: 10px 14px;
  border: 2px solid #e5e7eb;
  border-radius: 10px;
  font-size: 14px;
  transition: all 0.2s ease;
  background: #fafafa;
  cursor: pointer;
  appearance: none;
  background-image: url("data:image/svg+xml,%3csvg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 20 20'%3e%3cpath stroke='%236b7280' stroke-linecap='round' stroke-linejoin='round' stroke-width='1.5' d='m6 8 4 4 4-4'/%3e%3c/svg%3e");
  background-position: right 12px center;
  background-repeat: no-repeat;
  background-size: 16px;
  padding-right: 40px;
  min-width: 180px;
}

.filter-select:focus {
  outline: none;
  border-color: #10b981;
  background-color: white;
  box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.1);
}

.filter-select:hover:not(:focus) {
  border-color: #d1d5db;
  background-color: white;
}

.filter-actions {
  display: flex;
  gap: 12px;
}

.filter-apply-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  font-size: 14px;
  font-weight: 600;
  border-radius: 10px;
  white-space: nowrap;
}

.btn-sm {
  padding: 6px 12px;
  font-size: 13px;
}

.btn-outline {
  background: transparent;
  color: #6b7280;
  border: 2px solid #e5e7eb;
}

.btn-outline:hover {
  background: #f9fafb;
  color: #374151;
  border-color: #d1d5db;
}

/* 响应式筛选器 */
@media (max-width: 768px) {
  .filters {
    padding: 20px;
    margin-bottom: 20px;
  }
  
  .filters-header {
    flex-direction: column;
    gap: 16px;
    align-items: stretch;
  }
  
  .filters-content {
    grid-template-columns: 1fr;
    gap: 20px;
  }
  
  .date-range {
    flex-direction: column;
    gap: 8px;
  }
  
  .date-separator {
    display: none;
  }
  
  .filter-input,
  .filter-select {
    min-width: unset;
    width: 100%;
  }
  
  .filter-actions {
    justify-content: stretch;
  }
  
  .filter-apply-btn {
    width: 100%;
    justify-content: center;
  }
}

/* 响应式设计 */
@media (max-width: 768px) {
  .modal-overlay {
    padding: 10px;
    align-items: flex-start;
  }
  
  .diet-modal {
    max-width: 100%;
    max-height: 95vh;
    margin-top: 10px;
    border-radius: 16px;
  }
  
  .diet-header {
    padding: 20px;
    flex-direction: column;
    text-align: center;
    gap: 12px;
    flex-shrink: 0;
  }
  
  .header-text {
    order: 1;
  }
  
  .modal-close-btn {
    position: absolute;
    top: 16px;
    right: 16px;
  }
  
  .diet-form {
    padding: 20px;
    max-height: calc(95vh - 120px);
  }
  
  .form-row {
    grid-template-columns: 1fr;
    gap: 16px;
    margin-bottom: 16px;
  }
  
  .form-actions {
    flex-direction: column;
    gap: 12px;
    margin-top: 24px;
    padding-top: 20px;
    flex-shrink: 0;
  }
  
  .form-actions .btn {
    width: 100%;
  }
}

/* 删除确认模态框样式 */
.delete-modal {
  max-width: 480px;
  width: 100%;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
  animation: modalSlideIn 0.3s ease-out;
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
  margin-top: 16px;
}

.record-detail-card {
  background: #f9fafb;
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  padding: 20px;
}

.detail-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
  border-bottom: 1px solid #f3f4f6;
}

.detail-row:last-child {
  border-bottom: none;
}

.detail-label {
  font-size: 14px;
  color: #6b7280;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 6px;
}

.detail-value {
  font-size: 14px;
  color: #374151;
  font-weight: 600;
  text-align: right;
  max-width: 60%;
  word-break: break-word;
}

.detail-value.highlight {
  color: #10b981;
  font-weight: 700;
}

.detail-value.calories-value {
  color: #f59e0b;
  font-weight: 700;
}

.detail-value.notes-text {
  color: #6b7280;
  font-weight: 400;
  font-style: italic;
  max-width: 65%;
}

.delete-actions {
  padding: 20px 24px;
  background: #f9fafb;
  border-top: 1px solid #e5e7eb;
  display: flex;
  gap: 12px;
  justify-content: flex-end;
}

.cancel-btn {
  padding: 10px 20px;
  background: #f3f4f6;
  color: #374151;
  border: 2px solid #e5e7eb;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  gap: 6px;
}

.cancel-btn:hover {
  background: #e5e7eb;
  border-color: #d1d5db;
  color: #374151;
  transform: translateY(-1px);
}

.delete-btn {
  padding: 10px 20px;
  background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
  color: white;
  border: 2px solid #ef4444;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  gap: 6px;
  min-width: 120px;
  justify-content: center;
}

.delete-btn:hover:not(:disabled) {
  background: linear-gradient(135deg, #dc2626 0%, #b91c1c 100%);
  border-color: #dc2626;
  color: white;
  transform: translateY(-1px);
}

.delete-btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
  transform: none;
  color: white;
}

/* 深色模式支持 */
@media (prefers-color-scheme: dark) {
  .diet-form {
    background: #1f2937;
  }
  
  .form-label {
    color: #f3f4f6;
  }
  
  .form-input {
    background: #374151;
    border-color: #4b5563;
    color: #f3f4f6;
  }
  
  .form-input:focus {
    background: #4b5563;
    border-color: #10b981;
  }
  
  .form-input:hover:not(:focus) {
    background: #4b5563;
    border-color: #6b7280;
  }
  
  .food-suggestions {
    background: #374151;
    border-color: #4b5563;
  }
  
  .suggestion-item {
    border-bottom-color: #4b5563;
  }
  
  .suggestion-item:hover {
    background: #4b5563;
  }
  
  .suggestion-name {
    color: #f3f4f6;
  }
  
  .suggestion-category {
    color: #9ca3af;
  }
  
  .calculated-calories {
    background: linear-gradient(135deg, #064e3b 0%, #065f46 100%);
    border-color: #10b981;
    color: #6ee7b7;
  }
  
  .textarea-counter {
    color: #9ca3af;
  }
  
  /* 只在添加/编辑表单中应用深色模式的按钮样式 */
  .diet-form .btn-secondary {
    background: #374151;
    color: #f3f4f6;
    border-color: #4b5563;
  }
  
  .diet-form .btn-secondary:hover {
    background: #4b5563;
    border-color: #6b7280;
  }
}
</style>