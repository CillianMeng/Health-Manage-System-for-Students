# Vue.js API 调用示例文档

本文档提供了学生健康管理系统各个 API 接口的 Vue.js 调用示例，供前端开发人员参考使用。

## 基础配置

### Axios 配置

```javascript
// api/config.js
import axios from 'axios'

const apiClient = axios.create({
  baseURL: 'http://localhost:8000/api',
  withCredentials: true, // 支持Cookie认证
  headers: {
    'Content-Type': 'application/json',
  }
})

// 响应拦截器
apiClient.interceptors.response.use(
  response => response,
  error => {
    if (error.response?.status === 401) {
      // 未授权，跳转到登录页
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export default apiClient
```

### 错误处理

```javascript
// utils/errorHandler.js
export const handleApiError = (error) => {
  if (error.response) {
    const { status, data } = error.response
    switch (status) {
      case 400: return data.detail || '请求参数错误'
      case 401: return '请先登录'
      case 403: return '权限不足'
      case 404: return '资源不存在'
      case 500: return '服务器内部错误'
      default: return '请求失败'
    }
  }
  return '网络连接失败'
}
```

## 用户认证相关 API

### 1. 用户注册

```javascript
// api/auth.js
import apiClient from './config'
import { handleApiError } from '@/utils/errorHandler'

export const registerUser = async (userData) => {
  try {
    const response = await apiClient.post('/register/', {
      username: userData.username,
      email: userData.email,
      password: userData.password,
      first_name: userData.firstName,
      last_name: userData.lastName,
      student_id: userData.studentId,
      grade: userData.grade,
      major: userData.major,
      phone: userData.phone
    })
    return { success: true, data: response.data }
  } catch (error) {
    return { success: false, error: handleApiError(error) }
  }
}

// 使用示例
const result = await registerUser(formData)
if (result.success) {
  // 注册成功，处理返回的用户信息
  console.log('用户注册成功:', result.data)
} else {
  // 显示错误信息
  console.error('注册失败:', result.error)
}
```

### 2. 用户登录

```javascript
export const loginUser = async (username, password) => {
  try {
    const response = await apiClient.post('/login/', { username, password })
    return { success: true, data: response.data }
  } catch (error) {
    return { success: false, error: handleApiError(error) }
  }
}

// 使用示例
const result = await loginUser('username', 'password')
if (result.success) {
  console.log('登录成功:', result.data.message)
} else {
  console.error('登录失败:', result.error)
}
```

### 3. 用户登出

```javascript
export const logoutUser = async () => {
  try {
    const response = await apiClient.post('/logout/')
    return { success: true, data: response.data }
  } catch (error) {
    return { success: false, error: handleApiError(error) }
  }
}

// 使用示例
const result = await logoutUser()
if (result.success) {
  console.log('登出成功')
  // 跳转到登录页
} else {
  console.error('登出失败:', result.error)
}
```

### 4. 检查登录状态

```javascript
export const checkLoginStatus = async () => {
  try {
    const response = await apiClient.get('/check-login/')
    return { success: true, data: response.data }
  } catch (error) {
    return { success: false, error: handleApiError(error) }
  }
}

// 路由守卫使用示例
router.beforeEach(async (to, from, next) => {
  const publicPages = ['/login', '/register']
  const authRequired = !publicPages.includes(to.path)
  
  if (authRequired) {
    const result = await checkLoginStatus()
    if (!result.success) {
      next('/login')
    } else {
      next()
    }
  } else {
    next()
  }
})
```

## 睡眠记录相关 API

### 1. 获取睡眠记录列表

```javascript
// api/sleep.js
import apiClient from './config'
import { handleApiError } from '@/utils/errorHandler'

export const getSleepRecords = async (params = {}) => {
  try {
    const response = await apiClient.get('/sleep-records/', { params })
    return { success: true, data: response.data }
  } catch (error) {
    return { success: false, error: handleApiError(error) }
  }
}

// 使用示例 - 带筛选参数
const filters = {
  start_date: '2024-01-01',
  end_date: '2024-01-31'
}
const result = await getSleepRecords(filters)
if (result.success) {
  console.log('睡眠记录列表:', result.data)
} else {
  console.error('获取失败:', result.error)
}
```

### 2. 创建睡眠记录

```javascript
export const createSleepRecord = async (recordData) => {
  try {
    const response = await apiClient.post('/sleep-records/', {
      sleep_date: recordData.sleepDate,
      bedtime: recordData.bedtime,
      wake_time: recordData.wakeTime,
      quality: recordData.quality,
      notes: recordData.notes || ''
    })
    return { success: true, data: response.data }
  } catch (error) {
    return { success: false, error: handleApiError(error) }
  }
}

// 使用示例
const recordData = {
  sleepDate: '2024-01-15',
  bedtime: '23:30',
  wakeTime: '07:00',
  quality: 4,
  notes: '睡眠质量不错'
}
const result = await createSleepRecord(recordData)
if (result.success) {
  console.log('睡眠记录创建成功:', result.data)
} else {
  console.error('创建失败:', result.error)
}
```

### 3. 获取单个睡眠记录

```javascript
export const getSleepRecord = async (id) => {
  try {
    const response = await apiClient.get(`/sleep-records/${id}/`)
    return { success: true, data: response.data }
  } catch (error) {
    return { success: false, error: handleApiError(error) }
  }
}

// 使用示例
const result = await getSleepRecord(123)
if (result.success) {
  console.log('睡眠记录详情:', result.data)
} else {
  console.error('获取失败:', result.error)
}
```

### 4. 更新睡眠记录

```javascript
export const updateSleepRecord = async (id, recordData) => {
  try {
    const response = await apiClient.put(`/sleep-records/${id}/`, {
      sleep_date: recordData.sleepDate,
      bedtime: recordData.bedtime,
      wake_time: recordData.wakeTime,
      quality: recordData.quality,
      notes: recordData.notes || ''
    })
    return { success: true, data: response.data }
  } catch (error) {
    return { success: false, error: handleApiError(error) }
  }
}

// 使用示例
const updatedData = {
  sleepDate: '2024-01-15',
  bedtime: '23:00',
  wakeTime: '07:30',
  quality: 5,
  notes: '调整后睡眠质量很好'
}
const result = await updateSleepRecord(123, updatedData)
if (result.success) {
  console.log('睡眠记录更新成功:', result.data)
} else {
  console.error('更新失败:', result.error)
}
```

### 5. 删除睡眠记录

```javascript
export const deleteSleepRecord = async (id) => {
  try {
    await apiClient.delete(`/sleep-records/${id}/`)
    return { success: true }
  } catch (error) {
    return { success: false, error: handleApiError(error) }
  }
}

// 使用示例
const result = await deleteSleepRecord(123)
if (result.success) {
  console.log('睡眠记录删除成功')
} else {
  console.error('删除失败:', result.error)
}
```

### 6. 获取睡眠统计数据

```javascript
export const getSleepStats = async (params = {}) => {
  try {
    const response = await apiClient.get('/sleep-records/stats/', { params })
    return { success: true, data: response.data }
  } catch (error) {
    return { success: false, error: handleApiError(error) }
  }
}

// 使用示例 - 获取最近30天统计
const params = {
  start_date: '2024-01-01',
  end_date: '2024-01-31'
}
const result = await getSleepStats(params)
if (result.success) {
  console.log('睡眠统计数据:', result.data)
  // result.data 包含: average_duration, average_quality, total_records 等统计信息
} else {
  console.error('获取统计失败:', result.error)
}
```

## 运动记录相关 API

### 1. 获取运动记录列表

```javascript
// api/exercise.js
import apiClient from './config'
import { handleApiError } from '@/utils/errorHandler'

export const getExerciseRecords = async (params = {}) => {
  try {
    const response = await apiClient.get('/exercise-records/', { params })
    return { success: true, data: response.data }
  } catch (error) {
    return { success: false, error: handleApiError(error) }
  }
}

// 使用示例
const filters = {
  start_date: '2024-01-01',
  end_date: '2024-01-31',
  exercise_type: 'running'
}
const result = await getExerciseRecords(filters)
```

### 2. 创建运动记录

```javascript
export const createExerciseRecord = async (recordData) => {
  try {
    const response = await apiClient.post('/exercise-records/', {
      exercise_date: recordData.exerciseDate,
      exercise_type: recordData.exerciseType,
      duration: recordData.duration,
      intensity: recordData.intensity,
      calories_burned: recordData.caloriesBurned,
      notes: recordData.notes || ''
    })
    return { success: true, data: response.data }
  } catch (error) {
    return { success: false, error: handleApiError(error) }
  }
}

// 使用示例
const recordData = {
  exerciseDate: '2024-01-15',
  exerciseType: 'running',
  duration: 30,
  intensity: 'medium',
  caloriesBurned: 300,
  notes: '晨跑，天气不错'
}
const result = await createExerciseRecord(recordData)
```

### 3. 更新运动记录

```javascript
export const updateExerciseRecord = async (id, recordData) => {
  try {
    const response = await apiClient.put(`/exercise-records/${id}/`, {
      exercise_date: recordData.exerciseDate,
      exercise_type: recordData.exerciseType,
      duration: recordData.duration,
      intensity: recordData.intensity,
      calories_burned: recordData.caloriesBurned,
      notes: recordData.notes || ''
    })
    return { success: true, data: response.data }
  } catch (error) {
    return { success: false, error: handleApiError(error) }
  }
}
```

### 4. 删除运动记录

```javascript
export const deleteExerciseRecord = async (id) => {
  try {
    await apiClient.delete(`/exercise-records/${id}/`)
    return { success: true }
  } catch (error) {
    return { success: false, error: handleApiError(error) }
  }
}
```

### 5. 获取运动统计数据

```javascript
export const getExerciseStats = async (params = {}) => {
  try {
    const response = await apiClient.get('/exercise-records/stats/', { params })
    return { success: true, data: response.data }
  } catch (error) {
    return { success: false, error: handleApiError(error) }
  }
}

// 使用示例
const result = await getExerciseStats({ start_date: '2024-01-01', end_date: '2024-01-31' })
// result.data 包含: total_duration, total_calories, exercise_frequency 等统计信息
```

## 饮食记录相关 API

### 1. 获取食物列表

```javascript
// api/diet.js
import apiClient from './config'
import { handleApiError } from '@/utils/errorHandler'

export const getFoodItems = async (params = {}) => {
  try {
    const response = await apiClient.get('/food-items/', { params })
    return { success: true, data: response.data }
  } catch (error) {
    return { success: false, error: handleApiError(error) }
  }
}

// 使用示例 - 搜索食物
const result = await getFoodItems({ search: '米饭' })
```

### 2. 获取饮食记录列表

```javascript
export const getDietRecords = async (params = {}) => {
  try {
    const response = await apiClient.get('/diet-records/', { params })
    return { success: true, data: response.data }
  } catch (error) {
    return { success: false, error: handleApiError(error) }
  }
}

// 使用示例
const filters = {
  start_date: '2024-01-01',
  end_date: '2024-01-31',
  meal_type: 'breakfast'
}
const result = await getDietRecords(filters)
```

### 3. 创建饮食记录

```javascript
export const createDietRecord = async (recordData) => {
  try {
    const response = await apiClient.post('/diet-records/', {
      meal_date: recordData.mealDate,
      meal_type: recordData.mealType,
      food_item: recordData.foodItemId,
      quantity: recordData.quantity,
      notes: recordData.notes || ''
    })
    return { success: true, data: response.data }
  } catch (error) {
    return { success: false, error: handleApiError(error) }
  }
}

// 使用示例
const recordData = {
  mealDate: '2024-01-15',
  mealType: 'breakfast',
  foodItemId: 1,
  quantity: 150,
  notes: '早餐，白米粥'
}
const result = await createDietRecord(recordData)
```

### 4. 更新饮食记录

```javascript
export const updateDietRecord = async (id, recordData) => {
  try {
    const response = await apiClient.put(`/diet-records/${id}/`, {
      meal_date: recordData.mealDate,
      meal_type: recordData.mealType,
      food_item: recordData.foodItemId,
      quantity: recordData.quantity,
      notes: recordData.notes || ''
    })
    return { success: true, data: response.data }
  } catch (error) {
    return { success: false, error: handleApiError(error) }
  }
}
```

### 5. 删除饮食记录

```javascript
export const deleteDietRecord = async (id) => {
  try {
    await apiClient.delete(`/diet-records/${id}/`)
    return { success: true }
  } catch (error) {
    return { success: false, error: handleApiError(error) }
  }
}
```

### 6. 获取饮食统计数据

```javascript
export const getDietStats = async (params = {}) => {
  try {
    const response = await apiClient.get('/diet-records/stats/', { params })
    return { success: true, data: response.data }
  } catch (error) {
    return { success: false, error: handleApiError(error) }
  }
}

// 使用示例
const result = await getDietStats({ start_date: '2024-01-01', end_date: '2024-01-31' })
// result.data 包含: total_calories, avg_calories_per_day, nutrition_summary 等统计信息
```

## 通用工具函数

### 日期格式化

```javascript
// utils/dateUtils.js
export const formatDate = (date) => {
  return new Date(date).toLocaleDateString('zh-CN')
}

export const formatDateTime = (datetime) => {
  return new Date(datetime).toLocaleString('zh-CN')
}

export const formatDateForAPI = (date) => {
  return new Date(date).toISOString().split('T')[0]
}
```

### API 服务封装

```javascript
// services/api.js
import * as authAPI from '@/api/auth'
import * as sleepAPI from '@/api/sleep'
import * as exerciseAPI from '@/api/exercise'
import * as dietAPI from '@/api/diet'

export const apiService = {
  // 认证相关
  auth: authAPI,
  
  // 睡眠记录
  sleep: sleepAPI,
  
  // 运动记录
  exercise: exerciseAPI,
  
  // 饮食记录
  diet: dietAPI
}

// 使用示例
import { apiService } from '@/services/api'

// 登录
const loginResult = await apiService.auth.loginUser(username, password)

// 获取睡眠记录
const sleepRecords = await apiService.sleep.getSleepRecords()

// 创建运动记录
const exerciseResult = await apiService.exercise.createExerciseRecord(data)
```

---

## 总结

本文档提供了完整的 Vue.js API 调用示例，包括：

1. **用户认证**：注册、登录、登出、状态检查
2. **睡眠记录**：增删改查、统计分析
3. **运动记录**：增删改查、统计分析
4. **饮食记录**：增删改查、统计分析、食物搜索
5. **工具函数**：错误处理、日期格式化、API 服务封装

所有 API 调用都包含完整的错误处理和使用示例，可以直接在 Vue.js 项目中使用。
