<template>
    <div class="health-goals">
        <!-- 页面标题 -->
        <div class="page-header">
            <h1 class="page-title">健康目标管理</h1>
            <button @click="showCreateForm = true" class="btn-primary">
                <span class="btn-icon">🎯</span>
                创建目标
            </button>
        </div>

        <!-- 目标统计概览 -->
        <div class="stats-overview">
            <div class="stat-card">
                <div class="stat-icon">📊</div>
                <div class="stat-content">
                    <h3 class="stat-number">{{ goalStats.total_goals || 0 }}</h3>
                    <p class="stat-label">总目标数</p>
                </div>
            </div>

            <div class="stat-card">
                <div class="stat-icon">🚀</div>
                <div class="stat-content">
                    <h3 class="stat-number">{{ goalStats.active_goals || 0 }}</h3>
                    <p class="stat-label">进行中</p>
                </div>
            </div>

            <div class="stat-card">
                <div class="stat-icon">✅</div>
                <div class="stat-content">
                    <h3 class="stat-number">{{ goalStats.completed_goals || 0 }}</h3>
                    <p class="stat-label">已完成</p>
                </div>
            </div>

            <div class="stat-card">
                <div class="stat-icon">📈</div>
                <div class="stat-content">
                    <h3 class="stat-number">{{ goalStats.average_progress || 0 }}%</h3>
                    <p class="stat-label">平均进度</p>
                </div>
            </div>
        </div>

        <!-- 目标筛选 -->
        <div class="filter-section">
            <div class="filter-group">
                <label>状态筛选:</label>
                <select v-model="filters.status" @change="loadGoals">
                    <option value="">全部状态</option>
                    <option value="active">进行中</option>
                    <option value="completed">已完成</option>
                </select>
            </div>

            <div class="filter-group">
                <label>类型筛选:</label>
                <select v-model="filters.type" @change="loadGoals">
                    <option value="">全部类型</option>
                    <option value="sleep">睡眠目标</option>
                    <option value="exercise">运动目标</option>
                    <option value="diet">饮食目标</option>
                    <option value="weight">体重目标</option>
                    <option value="custom">自定义目标</option>
                </select>
            </div>
        </div>

        <!-- 目标列表 -->
        <div class="goals-section">
            <div v-if="loading" class="loading">
                <div class="loading-spinner"></div>
                <p>加载中...</p>
            </div>

            <div v-else-if="goals.length === 0" class="empty-state">
                <div class="empty-icon">🎯</div>
                <h3>暂无健康目标</h3>
                <p>设定您的第一个健康目标，开始健康管理之旅</p>
                <button @click="showCreateForm = true" class="btn-primary">
                    创建目标
                </button>
            </div>

            <div v-else class="goals-grid">
                <div v-for="goal in goals" :key="goal.id" class="goal-card" :class="getGoalCardClass(goal)">
                    <!-- 目标头部 -->
                    <div class="goal-header">
                        <div class="goal-type-badge" :style="{ backgroundColor: getGoalTypeColor(goal.goal_type) }">
                            {{ getGoalTypeIcon(goal.goal_type) }} {{ getGoalTypeDisplay(goal.goal_type) }}
                        </div>
                        <div class="goal-status" :style="{ color: goal.status_color }">
                            {{ getGoalStatusDisplay(goal.status) }}
                        </div>
                    </div>

                    <!-- 目标标题和描述 -->
                    <div class="goal-content">
                        <h3 class="goal-title">{{ goal.title }}</h3>
                        <p v-if="goal.description" class="goal-description">{{ goal.description }}</p>
                    </div>

                    <!-- 进度条 -->
                    <div class="progress-section">
                        <div class="progress-info">
                            <span class="progress-text">
                                {{ goal.current_value }}/{{ goal.target_value }} {{ goal.unit }}
                            </span>
                            <span class="progress-percentage">{{ goal.progress_percentage.toFixed(1) }}%</span>
                        </div>
                        <div class="progress-bar">
                            <div class="progress-fill" :style="{
                                width: `${Math.min(100, goal.progress_percentage)}%`,
                                backgroundColor: goal.progress_color
                            }"></div>
                        </div>
                        <div class="achievement-level">{{ goal.achievement_level }}</div>
                    </div>

                    <!-- 目标信息 -->
                    <div class="goal-info">
                        <div class="info-item">
                            <span class="info-label">频率:</span>
                            <span class="info-value">{{ getFrequencyDisplay(goal.frequency) }}</span>
                        </div>
                        <div class="info-item">
                            <span class="info-label">剩余天数:</span>
                            <span class="info-value" :class="{ 'overdue': goal.is_overdue }">
                                {{ goal.is_overdue ? '已过期' : `${goal.days_remaining}天` }}
                            </span>
                        </div>
                    </div>

                    <!-- 操作按钮 -->
                    <div class="goal-actions">
                        <button @click="showProgressDialog(goal)" class="btn btn-sm btn-primary">
                            📈 更新进度
                        </button>
                        <button @click="editGoal(goal)" class="btn btn-sm btn-secondary">
                            ✏️ 编辑
                        </button>
                        <button @click="deleteGoal(goal)" class="btn btn-sm btn-danger">
                            🗑️ 删除
                        </button>
                    </div>
                </div>
            </div>
        </div>

        <!-- 创建/编辑目标对话框 -->
        <div v-if="showCreateForm" class="modal-overlay" @click.self="closeCreateForm">
            <div class="modal-content" @click.stop>
                <div class="modal-header">
                    <div class="header-icon">
                        <span class="form-icon">🎯</span>
                    </div>
                    <div class="header-text">
                        <h3 class="modal-title">{{ editingGoal ? '编辑健康目标' : '创建健康目标' }}</h3>
                        <p class="modal-subtitle">设定您的健康目标，追踪进度完成</p>
                    </div>
                    <button @click="closeCreateForm" class="modal-close-btn">✕</button>
                </div>

                <form @submit.prevent="submitGoal" class="goal-form">
                    <div class="form-group">
                        <label for="goalType" class="form-label">
                            <span class="label-icon">🏷️</span>
                            目标类型
                            <span class="required">*</span>
                        </label>
                        <select id="goalType" v-model="formData.goal_type" required class="form-input">
                            <option value="">请选择目标类型</option>
                            <option value="sleep">😴 睡眠目标</option>
                            <option value="exercise">🏃 运动目标</option>
                            <option value="diet">🥗 饮食目标</option>
                            <option value="weight">⚖️ 体重目标</option>
                            <option value="custom">🎯 自定义目标</option>
                        </select>
                    </div>

                    <div class="form-group">
                        <label for="goalTitle" class="form-label">
                            <span class="label-icon">📝</span>
                            目标标题
                            <span class="required">*</span>
                        </label>
                        <input id="goalTitle" type="text" v-model="formData.title" placeholder="例如：每天睡眠8小时" required
                            class="form-input" />
                    </div>

                    <div class="form-group">
                        <label for="goalDescription" class="form-label">
                            <span class="label-icon">📄</span>
                            目标描述
                        </label>
                        <textarea id="goalDescription" v-model="formData.description" placeholder="详细描述您的目标..." rows="3"
                            class="form-input form-textarea"></textarea>
                    </div>

                    <div class="form-row">
                        <div class="form-group">
                            <label for="targetValue" class="form-label">
                                <span class="label-icon">🎯</span>
                                目标数值
                                <span class="required">*</span>
                            </label>
                            <input id="targetValue" type="number" step="0.1" min="0" v-model="formData.target_value"
                                required class="form-input" />
                        </div>
                        <div class="form-group">
                            <label for="unit" class="form-label">
                                <span class="label-icon">📏</span>
                                单位
                                <span class="required">*</span>
                            </label>
                            <input id="unit" type="text" v-model="formData.unit" placeholder="小时、次、公斤等" required
                                class="form-input" />
                        </div>
                    </div>

                    <div class="form-group">
                        <label for="frequency" class="form-label">
                            <span class="label-icon">🔄</span>
                            完成频率
                            <span class="required">*</span>
                        </label>
                        <select id="frequency" v-model="formData.frequency" required class="form-input">
                            <option value="">请选择频率</option>
                            <option value="daily">📅 每日</option>
                            <option value="weekly">📆 每周</option>
                            <option value="monthly">🗓️ 每月</option>
                            <option value="total">📊 总计</option>
                        </select>
                    </div>

                    <div class="form-row">
                        <div class="form-group">
                            <label for="startDate" class="form-label">
                                <span class="label-icon">🚀</span>
                                开始日期
                                <span class="required">*</span>
                            </label>
                            <input id="startDate" type="date" v-model="formData.start_date" required
                                class="form-input date-input" />
                        </div>
                        <div class="form-group">
                            <label for="endDate" class="form-label">
                                <span class="label-icon">🏁</span>
                                结束日期
                                <span class="required">*</span>
                            </label>
                            <input id="endDate" type="date" v-model="formData.end_date" required
                                class="form-input date-input" />
                        </div>
                    </div>

                    <div class="form-group">
                        <label class="checkbox-label">
                            <input type="checkbox" v-model="formData.reminder_enabled" class="form-checkbox" />
                            <span class="label-icon">🔔</span>
                            启用提醒
                        </label>
                    </div>

                    <div v-if="formData.reminder_enabled" class="form-group">
                        <label for="reminderTime" class="form-label">
                            <span class="label-icon">⏰</span>
                            提醒时间
                        </label>
                        <input id="reminderTime" type="time" v-model="formData.reminder_time"
                            class="form-input time-input" />
                    </div>

                    <div v-if="formError" class="error-message">
                        <span class="error-icon">⚠️</span>
                        {{ formError }}
                    </div>

                    <div class="form-actions">
                        <button type="button" @click="closeCreateForm" class="btn btn-secondary btn-lg">
                            <span class="btn-icon">↩️</span>
                            取消
                        </button>
                        <button type="submit" :disabled="submitting" class="btn-primary btn-lg">
                            <span v-if="submitting">⏳ 提交中...</span>
                            <span v-else>
                                <span class="btn-icon">{{ editingGoal ? '💾' : '✨' }}</span>
                                {{ editingGoal ? '更新目标' : '创建目标' }}
                            </span>
                        </button>
                    </div>
                </form>
            </div>
        </div>

        <!-- 进度更新对话框 -->
        <div v-if="showProgressForm" class="modal-overlay" @click.self="closeProgressForm">
            <div class="modal-content progress-modal" @click.stop>
                <div class="modal-header progress-header">
                    <div class="header-icon">
                        <span class="form-icon">📈</span>
                    </div>
                    <div class="header-text">
                        <h3 class="modal-title">更新进度</h3>
                        <p class="modal-subtitle">{{ currentGoal?.title }}</p>
                    </div>
                    <button @click="closeProgressForm" class="modal-close-btn">✕</button>
                </div>

                <form @submit.prevent="submitProgress" class="progress-form">
                    <div class="current-progress">
                        <div class="progress-info">
                            <span>当前进度: {{ currentGoal?.current_value }}/{{ currentGoal?.target_value }} {{
                                currentGoal?.unit }}</span>
                            <span class="progress-percentage">{{ currentGoal?.progress_percentage.toFixed(1) }}%</span>
                        </div>
                        <div class="progress-bar">
                            <div class="progress-fill" :style="{
                                width: `${Math.min(100, currentGoal?.progress_percentage || 0)}%`,
                                backgroundColor: currentGoal?.progress_color
                            }"></div>
                        </div>
                    </div>

                    <div class="form-group">
                        <label for="progressValue" class="form-label">
                            <span class="label-icon">📊</span>
                            今日进度值
                            <span class="required">*</span>
                        </label>
                        <input id="progressValue" type="number" step="0.1" min="0" v-model="progressData.value"
                            :placeholder="`输入今日的${currentGoal?.unit}数`" required class="form-input" />
                    </div>

                    <div class="form-group">
                        <label for="progressDate" class="form-label">
                            <span class="label-icon">📅</span>
                            日期
                        </label>
                        <input id="progressDate" type="date" v-model="progressData.date"
                            class="form-input date-input" />
                    </div>

                    <div class="form-group">
                        <label for="progressNotes" class="form-label">
                            <span class="label-icon">📝</span>
                            备注
                        </label>
                        <textarea id="progressNotes" v-model="progressData.notes" placeholder="记录今日的心得体会..." rows="3"
                            class="form-input form-textarea"></textarea>
                    </div>

                    <div v-if="progressError" class="error-message">
                        <span class="error-icon">⚠️</span>
                        {{ progressError }}
                    </div>

                    <div class="form-actions">
                        <button type="button" @click="closeProgressForm" class="btn-secondary btn-lg">
                            <span class="btn-icon">↩️</span>
                            取消
                        </button>
                        <button type="submit" :disabled="submittingProgress" class="btn-primary btn-lg">
                            <span v-if="submittingProgress">⏳ 更新中...</span>
                            <span v-else>
                                <span class="btn-icon">💾</span>
                                更新进度
                            </span>
                        </button>
                    </div>
                </form>
            </div>
        </div>

        <!-- 删除确认对话框 -->
        <div v-if="showDeleteConfirm" class="modal-overlay" @click="cancelDelete">
            <div class="modal-content delete-modal" @click.stop>
                <div class="modal-header delete-header">
                    <div class="delete-icon">
                        <span class="warning-icon">⚠️</span>
                    </div>
                    <h3 class="delete-title">确认删除健康目标</h3>
                    <button @click="cancelDelete" class="modal-close">✕</button>
                </div>

                <div class="modal-body delete-body">
                    <div class="delete-warning">
                        <p class="delete-message">您确定要删除这个健康目标吗？此操作无法撤销。</p>
                    </div>

                    <div class="delete-record-info">
                        <div class="record-detail-card">
                            <div class="detail-row">
                                <span class="detail-label">🎯 目标标题</span>
                                <span class="detail-value highlight">{{ deletingGoal?.title }}</span>
                            </div>
                            <div class="detail-row">
                                <span class="detail-label">🏷️ 目标类型</span>
                                <span class="detail-value">{{ getGoalTypeIcon(deletingGoal?.goal_type) }} {{
                                    getGoalTypeDisplay(deletingGoal?.goal_type) }}</span>
                            </div>
                            <div class="detail-row">
                                <span class="detail-label">📊 目标进度</span>
                                <span class="detail-value progress-value">{{ deletingGoal?.current_value }}/{{
                                    deletingGoal?.target_value }} {{ deletingGoal?.unit }} ({{
                                        deletingGoal?.progress_percentage.toFixed(1) }}%)</span>
                            </div>
                            <div class="detail-row">
                                <span class="detail-label">🔄 完成频率</span>
                                <span class="detail-value">{{ getFrequencyDisplay(deletingGoal?.frequency) }}</span>
                            </div>
                            <div class="detail-row">
                                <span class="detail-label">📅 目标期间</span>
                                <span class="detail-value">{{ deletingGoal?.start_date }} 至 {{ deletingGoal?.end_date
                                }}</span>
                            </div>
                            <div class="detail-row" v-if="deletingGoal?.description">
                                <span class="detail-label">📝 目标描述</span>
                                <span class="detail-value notes-text">{{ deletingGoal?.description }}</span>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="form-actions delete-actions">
                    <button @click="cancelDelete" class="btn-secondary cancel-btn">
                        <span class="btn-icon">↩️</span>
                        取消
                    </button>
                    <button @click="confirmDelete" :disabled="deleting" class="btn-danger delete-btn">
                        <span class="btn-icon">🗑️</span>
                        {{ deleting ? '删除中...' : '确认删除' }}
                    </button>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import tokenAuthService from '../utils/csrf-auth.js'

// API调用辅助函数
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

        console.error('API调用失败:', error);
        throw error;
    }
}

// 响应式数据
const loading = ref(true)
const goals = ref([])
const goalStats = ref({})
const showCreateForm = ref(false)
const showProgressForm = ref(false)
const showDeleteConfirm = ref(false)
const editingGoal = ref(null)
const currentGoal = ref(null)
const deletingGoal = ref(null)
const submitting = ref(false)
const submittingProgress = ref(false)
const deleting = ref(false)
const formError = ref('')
const progressError = ref('')

// 筛选条件
const filters = reactive({
    status: '',
    type: ''
})

// 表单数据
const formData = reactive({
    goal_type: '',
    title: '',
    description: '',
    target_value: '',
    unit: '',
    frequency: '',
    start_date: '',
    end_date: '',
    reminder_enabled: false,
    reminder_time: null  // 初始值设为 null
})

// 进度数据
const progressData = reactive({
    value: '',
    date: new Date().toISOString().split('T')[0],
    notes: ''
})

// 组件挂载时加载数据
onMounted(async () => {
    await Promise.all([
        loadGoals(),
        loadGoalStats()
    ])
    loading.value = false
})

// 加载目标列表
async function loadGoals() {
    try {
        const params = new URLSearchParams()
        if (filters.status) params.append('status', filters.status)
        if (filters.type) params.append('type', filters.type)

        const data = await apiCall(`/health-goals/?${params.toString()}`)
        goals.value = data.goals || []
    } catch (error) {
        console.error('加载目标列表失败:', error)
    }
}

// 加载目标统计
async function loadGoalStats() {
    try {
        const data = await apiCall('/health-goals/stats/')
        goalStats.value = data.stats || {}
    } catch (error) {
        console.error('加载目标统计失败:', error)
    }
}

// 显示创建表单
function showCreateDialog() {
    resetForm()
    showCreateForm.value = true
}

// 关闭创建表单
function closeCreateForm() {
    showCreateForm.value = false
    editingGoal.value = null
    resetForm()
}

// 重置表单
function resetForm() {
    // 重置所有字段为空字符串
    Object.keys(formData).forEach(key => {
        if (key === 'reminder_enabled') {
            formData[key] = false
        } else if (key === 'reminder_time') {
            formData[key] = null  // 设置为 null 而不是空字符串
        } else {
            formData[key] = ''
        }
    })
    formError.value = ''
}

// 编辑目标
function editGoal(goal) {
    editingGoal.value = goal
    Object.keys(formData).forEach(key => {
        if (goal[key] !== undefined) {
            formData[key] = goal[key]
        }
    })
    showCreateForm.value = true
}

// 提交目标
async function submitGoal() {
    if (!validateForm()) return

    try {
        submitting.value = true
        formError.value = ''

        // 准备提交数据，处理 reminder_time 字段
        const submitData = { ...formData }

        // 如果没有启用提醒或提醒时间为空，将 reminder_time 设为 null
        if (!submitData.reminder_enabled || !submitData.reminder_time || submitData.reminder_time.trim() === '') {
            submitData.reminder_time = null
        }

        let response
        if (editingGoal.value) {
            response = await apiCall(`/health-goals/${editingGoal.value.id}/`, {
                method: 'PUT',
                body: JSON.stringify(submitData)
            })
        } else {
            response = await apiCall('/health-goals/', {
                method: 'POST',
                body: JSON.stringify(submitData)
            })
        }

        if (response.success) {
            await Promise.all([loadGoals(), loadGoalStats()])
            closeCreateForm()
        } else {
            formError.value = response.message || '操作失败'
        }
    } catch (error) {
        console.error('提交目标失败:', error)
        formError.value = '提交失败，请重试'
    } finally {
        submitting.value = false
    }
}

// 表单验证
function validateForm() {
    if (!formData.goal_type) {
        formError.value = '请选择目标类型'
        return false
    }
    if (!formData.title.trim()) {
        formError.value = '请输入目标标题'
        return false
    }
    if (!formData.target_value || formData.target_value <= 0) {
        formError.value = '请输入有效的目标数值'
        return false
    }
    if (!formData.unit.trim()) {
        formError.value = '请输入单位'
        return false
    }
    if (!formData.frequency) {
        formError.value = '请选择完成频率'
        return false
    }
    if (!formData.start_date || !formData.end_date) {
        formError.value = '请选择开始和结束日期'
        return false
    }
    if (new Date(formData.end_date) <= new Date(formData.start_date)) {
        formError.value = '结束日期必须晚于开始日期'
        return false
    }
    if (formData.reminder_enabled && (!formData.reminder_time || formData.reminder_time.trim() === '')) {
        formError.value = '启用提醒时必须设置提醒时间'
        return false
    }
    return true
}

// 显示进度对话框
function showProgressDialog(goal) {
    currentGoal.value = goal
    progressData.value = ''
    progressData.date = new Date().toISOString().split('T')[0]
    progressData.notes = ''
    progressError.value = ''
    showProgressForm.value = true
}

// 关闭进度表单
function closeProgressForm() {
    showProgressForm.value = false
    currentGoal.value = null
}

// 提交进度
async function submitProgress() {
    if (!progressData.value || progressData.value < 0) {
        progressError.value = '请输入有效的进度值'
        return
    }

    try {
        submittingProgress.value = true
        progressError.value = ''

        const response = await apiCall(`/health-goals/${currentGoal.value.id}/progress/`, {
            method: 'POST',
            body: JSON.stringify(progressData)
        })

        if (response.success) {
            await Promise.all([loadGoals(), loadGoalStats()])
            closeProgressForm()
        } else {
            progressError.value = response.message || '更新进度失败'
        }
    } catch (error) {
        console.error('更新进度失败:', error)
        progressError.value = '更新失败，请重试'
    } finally {
        submittingProgress.value = false
    }
}

// 删除目标
function deleteGoal(goal) {
    deletingGoal.value = goal
    showDeleteConfirm.value = true
}

// 取消删除
function cancelDelete() {
    showDeleteConfirm.value = false
    deletingGoal.value = null
}

// 确认删除
async function confirmDelete() {
    if (!deletingGoal.value) return

    try {
        deleting.value = true
        const response = await apiCall(`/health-goals/${deletingGoal.value.id}/`, {
            method: 'DELETE'
        })

        await Promise.all([loadGoals(), loadGoalStats()])
        showDeleteConfirm.value = false
        deletingGoal.value = null
    } catch (error) {
        console.error('删除目标失败:', error)
        alert('删除失败，请重试')
    } finally {
        deleting.value = false
    }
}

// 工具函数
function getGoalTypeIcon(type) {
    const icons = {
        sleep: '😴',
        exercise: '🏃',
        diet: '🥗',
        weight: '⚖️',
        custom: '🎯'
    }
    return icons[type] || '🎯'
}

function getGoalTypeDisplay(type) {
    const displays = {
        sleep: '睡眠目标',
        exercise: '运动目标',
        diet: '饮食目标',
        weight: '体重目标',
        custom: '自定义目标'
    }
    return displays[type] || '未知类型'
}

function getGoalTypeColor(type) {
    const colors = {
        sleep: '#3b82f6',
        exercise: '#ef4444',
        diet: '#22c55e',
        weight: '#f59e0b',
        custom: '#8b5cf6'
    }
    return colors[type] || '#6b7280'
}

function getGoalStatusDisplay(status) {
    const displays = {
        active: '进行中',
        completed: '已完成',
        paused: '已暂停',
        cancelled: '已取消'
    }
    return displays[status] || '未知状态'
}

function getFrequencyDisplay(frequency) {
    const displays = {
        daily: '每日',
        weekly: '每周',
        monthly: '每月',
        total: '总计'
    }
    return displays[frequency] || '未知频率'
}

function getGoalCardClass(goal) {
    if (goal.status === 'completed') return 'goal-completed'
    if (goal.is_overdue) return 'goal-overdue'
    if (goal.progress_percentage >= 75) return 'goal-near-complete'
    return ''
}
</script>

<style scoped>
.health-goals {
    padding: 24px;
    max-width: 1200px;
    margin: 0 auto;
}

.page-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 32px;
}

.btn-primary {
    color: white;
    border: none;
    padding: 12px 24px;
    border-radius: 12px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.3s ease;
    display: flex;
    align-items: center;
    gap: 8px;
}

.btn-primary:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 20px rgba(102, 126, 234, 0.3);
}

.btn-icon {
    font-size: 1.1em;
}

/* 统计概览样式 */
.stats-overview {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 24px;
    margin-bottom: 32px;
}

.stat-card {
    background: white;
    padding: 24px;
    border-radius: 16px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
    border: 1px solid #f1f5f9;
    display: flex;
    align-items: center;
    gap: 16px;
    transition: transform 0.3s ease;
}

.stat-card:hover {
    transform: translateY(-4px);
}

.stat-icon {
    font-size: 2.5rem;
    /* 移除背景渐变效果，让图标正常显示 */
}

.stat-number {
    font-size: 2rem;
    font-weight: 700;
    color: #1e293b;
    margin: 0 0 4px 0;
}

.stat-label {
    color: #64748b;
    font-size: 0.9rem;
    margin: 0;
}

/* 筛选部分样式 */
.filter-section {
    background: white;
    padding: 20px;
    border-radius: 16px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
    margin-bottom: 24px;
    display: flex;
    gap: 24px;
    align-items: center;
}

.filter-group {
    display: flex;
    align-items: center;
    gap: 8px;
}

.filter-group label {
    font-weight: 600;
    color: #374151;
}

.filter-group select {
    padding: 8px 12px;
    border: 2px solid #e5e7eb;
    border-radius: 8px;
    font-size: 0.9rem;
    transition: border-color 0.3s ease;
}

.filter-group select:focus {
    outline: none;
    border-color: #667eea;
}

/* 目标列表样式 */
.goals-section {
    margin-top: 24px;
}

.loading {
    text-align: center;
    padding: 40px;
}

.loading-spinner {
    width: 40px;
    height: 40px;
    border: 4px solid #f3f4f6;
    border-top: 4px solid #667eea;
    border-radius: 50%;
    animation: spin 1s linear infinite;
    margin: 0 auto 16px;
}

@keyframes spin {
    0% {
        transform: rotate(0deg);
    }

    100% {
        transform: rotate(360deg);
    }
}

.empty-state {
    text-align: center;
    padding: 60px 20px;
    background: white;
    border-radius: 16px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
}

.empty-icon {
    font-size: 4rem;
    margin-bottom: 16px;
}

.empty-state h3 {
    color: #374151;
    margin-bottom: 8px;
}

.empty-state p {
    color: #6b7280;
    margin-bottom: 24px;
}

/* 目标网格样式 */
.goals-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(360px, 1fr));
    gap: 24px;
}

.goal-card {
    background: white;
    border-radius: 16px;
    padding: 24px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
    border: 1px solid #f1f5f9;
    transition: all 0.3s ease;
    position: relative;
    overflow: hidden;
}

.goal-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 8px 30px rgba(0, 0, 0, 0.12);
}

.goal-card.goal-completed {
    border-left: 4px solid #22c55e;
    background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%);
}

.goal-card.goal-overdue {
    border-left: 4px solid #ef4444;
    background: linear-gradient(135deg, #fef2f2 0%, #fee2e2 100%);
}

.goal-card.goal-near-complete {
    border-left: 4px solid #3b82f6;
    background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%);
}

.goal-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 16px;
}

.goal-type-badge {
    padding: 6px 12px;
    border-radius: 20px;
    color: white;
    font-size: 0.85rem;
    font-weight: 600;
}

.goal-status {
    font-size: 0.9rem;
    font-weight: 600;
}

.goal-content {
    margin-bottom: 20px;
}

.goal-title {
    font-size: 1.2rem;
    font-weight: 700;
    color: #1e293b;
    margin: 0 0 8px 0;
}

.goal-description {
    color: #64748b;
    line-height: 1.5;
    margin: 0;
}

/* 进度条样式 */
.progress-section {
    margin-bottom: 20px;
}

.progress-info {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 8px;
}

.progress-text {
    font-weight: 600;
    color: #374151;
}

.progress-percentage {
    font-weight: 700;
    color: #1e293b;
}

.progress-bar {
    width: 100%;
    height: 8px;
    background: #f1f5f9;
    border-radius: 4px;
    overflow: hidden;
    margin-bottom: 8px;
}

.progress-fill {
    height: 100%;
    border-radius: 4px;
    transition: width 0.3s ease;
}

.achievement-level {
    font-size: 0.9rem;
    font-weight: 600;
    color: #667eea;
    text-align: center;
}

/* 目标信息样式 */
.goal-info {
    display: flex;
    justify-content: space-between;
    margin-bottom: 20px;
    padding: 12px;
    background: #f8fafc;
    border-radius: 8px;
}

.info-item {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 4px;
}

.info-label {
    font-size: 0.8rem;
    color: #64748b;
}

.info-value {
    font-weight: 600;
    color: #374151;
}

.info-value.overdue {
    color: #ef4444;
}

/* 操作按钮样式 */
.goal-actions {
    display: flex;
    gap: 8px;
    flex-wrap: wrap;
}

/* .btn {
    padding: 8px 12px;
    border: none;
    border-radius: 8px;
    font-size: 0.85rem;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.3s ease;
    flex: 1;
    min-width: 0;
} */

.btn-sm {
    padding: 6px 10px;
    font-size: 0.8rem;
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

.btn-danger {
    background: #fef2f2;
    color: #dc2626;
}

.btn-danger:hover {
    background: #fee2e2;
    color: #b91c1c;
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
    padding: 20px;
}

.modal-content {
    background: white;
    border-radius: 16px;
    max-width: 600px;
    width: 100%;
    max-height: 90vh;
    overflow: hidden;
    box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
    color: #1f2937;
    display: flex;
    flex-direction: column;
}

.modal-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 20px 24px;
    border-bottom: 1px solid #e5e7eb;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    border-radius: 16px 16px 0 0;
    flex-shrink: 0;
}

.modal-header h2 {
    font-size: 1.5rem;
    font-weight: 700;
    color: white;
    margin: 0;
}

.close-btn {
    background: none;
    border: none;
    font-size: 1.5rem;
    color: #6b7280;
    cursor: pointer;
    padding: 4px;
    transition: color 0.3s ease;
}

.close-btn:hover {
    color: #374151;
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
  margin-left: 16px;
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

/* 表单样式 */
.goal-form,
.progress-form {
    padding: 24px;
    overflow-y: auto;
    flex: 1;
    max-height: calc(90vh - 140px);
}

/* 自定义滚动条样式 */
.goal-form::-webkit-scrollbar,
.progress-form::-webkit-scrollbar {
    width: 8px;
}

.goal-form::-webkit-scrollbar-track,
.progress-form::-webkit-scrollbar-track {
    background: #f1f5f9;
    border-radius: 4px;
}

.goal-form::-webkit-scrollbar-thumb,
.progress-form::-webkit-scrollbar-thumb {
    background: #cbd5e1;
    border-radius: 4px;
}

.goal-form::-webkit-scrollbar-thumb:hover,
.progress-form::-webkit-scrollbar-thumb:hover {
    background: #94a3b8;
}

.form-group {
    margin-bottom: 20px;
}

.form-row {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 16px;
}

.form-group label {
    display: block;
    font-weight: 600;
    color: #374151;
    margin-bottom: 6px;
}

.required {
    color: #ef4444;
    margin-left: 4px;
    font-weight: 700;
    font-size: 1.1em;
    transition: all 0.3s ease;
}

.form-label:hover .required {
    color: #dc2626;
    text-shadow: 0 0 4px rgba(239, 68, 68, 0.5);
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

.form-input::placeholder {
    color: #999;
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

.form-group input,
.form-group select,
.form-group textarea {
    width: 100%;
    padding: 12px 16px;
    border: 2px solid #e5e7eb;
    border-radius: 8px;
    font-size: 14px;
    transition: border-color 0.3s ease;
    box-sizing: border-box;
    background: white;
    color: #999;
}

.form-group input:focus,
.form-group select:focus,
.form-group textarea:focus {
    outline: none;
    border-color: #667eea;
    background: white;
}

.checkbox-label {
    display: flex !important;
    align-items: center;
    gap: 8px;
    cursor: pointer;
}

.checkbox-label input[type="checkbox"] {
    width: auto;
    margin: 0;
}

.current-progress {
    background: #f8fafc;
    padding: 20px;
    border-radius: 12px;
    margin-bottom: 24px;
}

.error-message {
    background: #fef2f2;
    color: #dc2626;
    padding: 12px 16px;
    border-radius: 8px;
    margin-bottom: 16px;
    border-left: 4px solid #dc2626;
}

.form-actions {
    display: flex;
    gap: 12px;
    justify-content: flex-end;
    padding: 20px 24px;
    border-top: 1px solid #e5e7eb;
    background: white;
    border-radius: 0 0 16px 16px;
    flex-shrink: 0;
}

.form-actions .btn-secondary,
.form-actions .btn-primary {
    padding: 12px 24px;
    font-size: 1rem;
}

/* 响应式设计 */
@media (max-width: 768px) {
    .health-goals {
        padding: 16px;
    }

    .page-header {
        flex-direction: column;
        gap: 16px;
        text-align: center;
    }

    .stats-overview {
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 16px;
    }

    .filter-section {
        flex-direction: column;
        gap: 16px;
        align-items: stretch;
    }

    .goals-grid {
        grid-template-columns: 1fr;
        gap: 16px;
    }

    .goal-actions {
        flex-direction: column;
    }

    .form-row {
        grid-template-columns: 1fr;
    }

    .form-actions {
        flex-direction: column;
    }

    .modal-content {
        margin: 10px;
        max-height: 95vh;
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
    background: white;
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

    0%,
    100% {
        transform: scale(1);
    }

    50% {
        transform: scale(1.1);
    }
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

.detail-value.progress-value {
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
</style>
