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