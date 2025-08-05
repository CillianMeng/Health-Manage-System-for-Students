<template>
  <div class="diet-chart">
    <div class="chart-header">
      <h3>饮食统计分析</h3>
      <div class="chart-tabs">
        <button 
          :class="['tab-btn', { active: activeTab === 'calories' }]"
          @click="activeTab = 'calories'"
        >
          卡路里趋势
        </button>
        <button 
          :class="['tab-btn', { active: activeTab === 'nutrition' }]"
          @click="activeTab = 'nutrition'"
        >
          营养分析
        </button>
        <button 
          :class="['tab-btn', { active: activeTab === 'meals' }]"
          @click="activeTab = 'meals'"
        >
          餐次分布
        </button>
      </div>
    </div>

    <div class="chart-content">
      <!-- 卡路里趋势图 -->
      <div v-if="activeTab === 'calories'" class="chart-panel">
        <div class="chart-stats">
          <div class="stat-item">
            <span class="stat-label">平均摄入</span>
            <span class="stat-value">{{ averageCalories }} kcal/天</span>
          </div>
          <div class="stat-item">
            <span class="stat-label">目标完成</span>
            <span class="stat-value">{{ targetCompletion }}%</span>
          </div>
          <div class="stat-item">
            <span class="stat-label">最高摄入</span>
            <span class="stat-value">{{ maxCalories }} kcal</span>
          </div>
        </div>
        
        <div class="chart-container">
          <canvas ref="caloriesChart" width="400" height="200"></canvas>
        </div>
        
        <div class="chart-legend">
          <div class="legend-item">
            <span class="legend-color calories"></span>
            <span class="legend-text">实际摄入</span>
          </div>
          <div class="legend-item">
            <span class="legend-color target"></span>
            <span class="legend-text">目标线 (2000 kcal)</span>
          </div>
        </div>
      </div>

      <!-- 营养分析图 -->
      <div v-if="activeTab === 'nutrition'" class="chart-panel">
        <div class="nutrition-summary">
          <div class="nutrition-score">
            <div class="score-circle" :style="{ background: getScoreColor(nutritionScore) }">
              <span class="score-text">{{ nutritionScore }}</span>
              <span class="score-label">营养均衡</span>
            </div>
          </div>
          
          <div class="nutrition-tips">
            <h4>营养建议</h4>
            <ul class="tip-list">
              <li v-for="tip in nutritionTips" :key="tip" class="tip-item">
                {{ tip }}
              </li>
            </ul>
          </div>
        </div>
        
        <div class="nutrition-breakdown">
          <h4>营养成分分析</h4>
          <div class="nutrition-bars">
            <div class="nutrition-bar">
              <div class="bar-header">
                <span class="bar-label">碳水化合物</span>
                <span class="bar-value">{{ nutritionData.carbs }}%</span>
              </div>
              <div class="bar-track">
                <div class="bar-fill carbs" :style="{ width: nutritionData.carbs + '%' }"></div>
              </div>
            </div>
            
            <div class="nutrition-bar">
              <div class="bar-header">
                <span class="bar-label">蛋白质</span>
                <span class="bar-value">{{ nutritionData.protein }}%</span>
              </div>
              <div class="bar-track">
                <div class="bar-fill protein" :style="{ width: nutritionData.protein + '%' }"></div>
              </div>
            </div>
            
            <div class="nutrition-bar">
              <div class="bar-header">
                <span class="bar-label">脂肪</span>
                <span class="bar-value">{{ nutritionData.fat }}%</span>
              </div>
              <div class="bar-track">
                <div class="bar-fill fat" :style="{ width: nutritionData.fat + '%' }"></div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 餐次分布图 -->
      <div v-if="activeTab === 'meals'" class="chart-panel">
        <div class="meals-summary">
          <div class="meal-stats">
            <div v-for="(meal, type) in mealDistribution" :key="type" class="meal-stat">
              <div class="meal-icon">{{ getMealIcon(type) }}</div>
              <div class="meal-info">
                <div class="meal-name">{{ getMealTypeName(type) }}</div>
                <div class="meal-calories">{{ meal.calories }} kcal</div>
                <div class="meal-percentage">{{ meal.percentage }}%</div>
              </div>
            </div>
          </div>
        </div>
        
        <div class="chart-container">
          <canvas ref="mealsChart" width="300" height="300"></canvas>
        </div>
        
        <div class="meals-analysis">
          <h4>餐次建议</h4>
          <div class="analysis-grid">
            <div class="analysis-item">
              <span class="analysis-icon">🌅</span>
              <div class="analysis-content">
                <div class="analysis-title">早餐</div>
                <div class="analysis-text">占总热量的25-30%</div>
                <div class="analysis-status" :class="getAnalysisStatus('breakfast')">
                  {{ getAnalysisText('breakfast') }}
                </div>
              </div>
            </div>
            
            <div class="analysis-item">
              <span class="analysis-icon">☀️</span>
              <div class="analysis-content">
                <div class="analysis-title">午餐</div>
                <div class="analysis-text">占总热量的35-40%</div>
                <div class="analysis-status" :class="getAnalysisStatus('lunch')">
                  {{ getAnalysisText('lunch') }}
                </div>
              </div>
            </div>
            
            <div class="analysis-item">
              <span class="analysis-icon">🌙</span>
              <div class="analysis-content">
                <div class="analysis-title">晚餐</div>
                <div class="analysis-text">占总热量的25-30%</div>
                <div class="analysis-status" :class="getAnalysisStatus('dinner')">
                  {{ getAnalysisText('dinner') }}
                </div>
              </div>
            </div>
            
            <div class="analysis-item">
              <span class="analysis-icon">🍎</span>
              <div class="analysis-content">
                <div class="analysis-title">加餐</div>
                <div class="analysis-text">占总热量的5-10%</div>
                <div class="analysis-status" :class="getAnalysisStatus('snack')">
                  {{ getAnalysisText('snack') }}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick, watch } from 'vue'

const props = defineProps({
  weeklyStats: {
    type: Object,
    default: () => ({})
  }
})

const activeTab = ref('calories')
const caloriesChart = ref(null)
const mealsChart = ref(null)

// 计算属性
const averageCalories = computed(() => {
  return Math.round(props.weeklyStats.average_daily_calories || 0)
})

const maxCalories = computed(() => {
  // 从记录中找出最高单日摄入
  const records = props.weeklyStats.records || []
  if (records.length === 0) return 0
  
  // 按日期分组计算每日总摄入
  const dailyTotals = {}
  records.forEach(record => {
    const date = record.diet_date
    if (!dailyTotals[date]) {
      dailyTotals[date] = 0
    }
    dailyTotals[date] += record.total_calories || 0
  })
  
  const maxDaily = Math.max(...Object.values(dailyTotals), 0)
  return Math.round(maxDaily)
})

const targetCompletion = computed(() => {
  const target = 2000
  return Math.round(props.weeklyStats.target_achievement_rate || 0)
})

const nutritionScore = computed(() => {
  const data = nutritionData.value
  
  // 如果没有数据，返回0
  if (data.carbs === 0 && data.protein === 0 && data.fat === 0) {
    return 0
  }
  
  // 理想的营养成分比例 (基于中国居民膳食指南)
  const idealRatios = {
    carbs: { min: 50, max: 65, ideal: 55 },     // 碳水化合物: 50-65%，理想55%
    protein: { min: 15, max: 20, ideal: 18 },   // 蛋白质: 15-20%，理想18%
    fat: { min: 20, max: 30, ideal: 25 }        // 脂肪: 20-30%，理想25%
  }
  
  let score = 100
  
  // 计算每个营养成分的得分
  Object.entries(idealRatios).forEach(([nutrient, range]) => {
    const actual = data[nutrient]
    
    if (actual >= range.min && actual <= range.max) {
      // 在正常范围内，根据与理想值的距离计算得分
      const deviation = Math.abs(actual - range.ideal)
      const maxDeviation = Math.max(range.ideal - range.min, range.max - range.ideal)
      const deduction = (deviation / maxDeviation) * 10 // 最多扣10分
      score -= deduction
    } else if (actual < range.min) {
      // 低于最低值，根据偏差程度扣分
      const deficit = range.min - actual
      score -= Math.min(deficit * 2, 30) // 每低1%扣2分，最多扣30分
    } else {
      // 高于最高值，根据超出程度扣分
      const excess = actual - range.max
      score -= Math.min(excess * 2, 30) // 每高1%扣2分，最多扣30分
    }
  })
  
  const finalScore = Math.max(Math.round(score), 0)
  
  return finalScore
})

const nutritionData = computed(() => {
  // 从记录中计算实际营养成分
  const records = props.weeklyStats.records || []
  if (records.length === 0) {
    return { carbs: 0, protein: 0, fat: 0 }
  }
  
  let totalCarbs = 0
  let totalProtein = 0
  let totalFat = 0
  let totalCalories = 0
  
  records.forEach(record => {
    const calories = record.total_calories || 0
    totalCalories += calories
    
    // 根据食物类型估算营养成分
    const foodName = record.food_name?.toLowerCase() || ''
    
    if (foodName.includes('米饭') || foodName.includes('面条') || foodName.includes('馒头') || 
        foodName.includes('面包') || foodName.includes('土豆') || foodName.includes('红薯')) {
      // 碳水化合物丰富的食物：70%碳水，10%蛋白质，5%脂肪
      totalCarbs += calories * 0.7
      totalProtein += calories * 0.1
      totalFat += calories * 0.05
    } else if (foodName.includes('鸡肉') || foodName.includes('牛肉') || foodName.includes('猪肉') || 
               foodName.includes('鱼') || foodName.includes('鸡蛋') || foodName.includes('豆腐')) {
      // 蛋白质丰富的食物：15%碳水，60%蛋白质，25%脂肪
      totalCarbs += calories * 0.15
      totalProtein += calories * 0.6
      totalFat += calories * 0.25
    } else if (foodName.includes('油') || foodName.includes('坚果') || foodName.includes('奶酪')) {
      // 脂肪丰富的食物：5%碳水，15%蛋白质，80%脂肪
      totalCarbs += calories * 0.05
      totalProtein += calories * 0.15
      totalFat += calories * 0.8
    } else {
      // 其他食物：标准分布 50%碳水，25%蛋白质，25%脂肪
      totalCarbs += calories * 0.5
      totalProtein += calories * 0.25
      totalFat += calories * 0.25
    }
  })
  
  if (totalCalories === 0) {
    return { carbs: 0, protein: 0, fat: 0 }
  }
  
  const result = {
    carbs: Math.round((totalCarbs / totalCalories) * 100),
    protein: Math.round((totalProtein / totalCalories) * 100),
    fat: Math.round((totalFat / totalCalories) * 100)
  }
  
  return result
})

const nutritionTips = computed(() => {
  const tips = []
  const data = nutritionData.value
  const score = nutritionScore.value
  
  // 基于更准确的营养指南提供建议
  if (data.carbs < 50) {
    tips.push('碳水化合物摄入偏低，建议增加全谷物、蔬菜和水果')
  } else if (data.carbs > 65) {
    tips.push('碳水化合物摄入过高，建议减少精制糖和加工食品')
  } else if (data.carbs >= 50 && data.carbs <= 65) {
    tips.push('✓ 碳水化合物摄入合理')
  }
  
  if (data.protein < 15) {
    tips.push('蛋白质摄入不足，建议增加瘦肉、鱼类、蛋类、豆制品')
  } else if (data.protein > 20) {
    tips.push('蛋白质摄入略高，可适当调整为其他营养素')
  } else {
    tips.push('✓ 蛋白质摄入适宜')
  }
  
  if (data.fat < 20) {
    tips.push('脂肪摄入偏低，适量补充坚果、橄榄油等健康脂肪')
  } else if (data.fat > 30) {
    tips.push('脂肪摄入过高，减少油炸食品和高脂肪食物')
  } else {
    tips.push('✓ 脂肪摄入合理')
  }
  
  // 根据总体评分给出综合建议
  if (score >= 85) {
    tips.push('🎉 营养搭配优秀，继续保持！')
  } else if (score >= 70) {
    tips.push('👍 营养搭配良好，稍作调整会更完美')
  } else if (score >= 50) {
    tips.push('⚠️ 营养搭配需要改善，建议多样化饮食')
  } else {
    tips.push('❗ 营养搭配有待优化，建议咨询营养师')
  }
  
  return tips
})

const mealDistribution = computed(() => {
  const meals = props.weeklyStats.meal_distribution || {}
  const total = Object.values(meals).reduce((sum, calories) => sum + calories, 0)
  
  const distribution = {}
  Object.entries(meals).forEach(([type, calories]) => {
    distribution[type] = {
      calories: Math.round(calories),
      percentage: total > 0 ? Math.round((calories / total) * 100) : 0
    }
  })
  
  return distribution
})

// 工具函数
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

const getScoreColor = (score) => {
  if (score >= 80) return 'linear-gradient(135deg, #00b894, #00cec9)'
  if (score >= 60) return 'linear-gradient(135deg, #fdcb6e, #f39c12)'
  return 'linear-gradient(135deg, #ff7675, #fd79a8)'
}

const getAnalysisStatus = (mealType) => {
  const meal = mealDistribution.value[mealType]
  if (!meal) return 'missing'
  
  const percentage = meal.percentage
  const ranges = {
    breakfast: [25, 30],
    lunch: [35, 40],
    dinner: [25, 30],
    snack: [5, 10]
  }
  
  const [min, max] = ranges[mealType] || [0, 100]
  
  if (percentage >= min && percentage <= max) return 'good'
  if (percentage < min) return 'low'
  return 'high'
}

const getAnalysisText = (mealType) => {
  const status = getAnalysisStatus(mealType)
  const texts = {
    good: '✓ 合理',
    low: '↓ 偏低',
    high: '↑ 偏高',
    missing: '- 无数据'
  }
  return texts[status] || ''
}

// 图表绘制函数
const drawCaloriesChart = () => {
  const canvas = caloriesChart.value
  if (!canvas) return
  
  const ctx = canvas.getContext('2d')
  const { width, height } = canvas
  
  // 清空画布
  ctx.clearRect(0, 0, width, height)
  
  // 从记录中提取每日数据
  const records = props.weeklyStats.records || []
  if (records.length === 0) {
    // 绘制无数据提示
    ctx.fillStyle = '#7f8c8d'
    ctx.font = '16px Arial'
    ctx.textAlign = 'center'
    ctx.fillText('暂无数据', width / 2, height / 2)
    return
  }
  
  // 按日期分组汇总每日摄入
  const dailyData = {}
  const today = new Date()
  
  // 初始化最近7天的数据
  for (let i = 6; i >= 0; i--) {
    const date = new Date(today)
    date.setDate(date.getDate() - i)
    const dateStr = date.toISOString().split('T')[0]
    dailyData[dateStr] = { date: dateStr, total_calories: 0, label: `${date.getMonth() + 1}/${date.getDate()}` }
  }
  
  // 填入实际数据
  records.forEach(record => {
    if (dailyData[record.diet_date]) {
      dailyData[record.diet_date].total_calories += record.total_calories || 0
    }
  })
  
  const daily = Object.values(dailyData).sort((a, b) => a.date.localeCompare(b.date))
  
  // 图表设置
  const padding = 40
  const chartWidth = width - padding * 2
  const chartHeight = height - padding * 2
  const maxValue = Math.max(...daily.map(d => d.total_calories), 2000)
  const minValue = 0
  
  // 绘制背景网格
  ctx.strokeStyle = '#f8f9fa'
  ctx.lineWidth = 1
  
  // 水平网格线
  for (let i = 0; i <= 5; i++) {
    const y = padding + (chartHeight / 5) * i
    ctx.beginPath()
    ctx.moveTo(padding, y)
    ctx.lineTo(width - padding, y)
    ctx.stroke()
  }
  
  // 垂直网格线
  for (let i = 0; i <= daily.length - 1; i++) {
    const x = padding + (chartWidth / (daily.length - 1)) * i
    ctx.beginPath()
    ctx.moveTo(x, padding)
    ctx.lineTo(x, height - padding)
    ctx.stroke()
  }
  
  // 绘制目标线
  const targetY = padding + chartHeight - ((2000 - minValue) / (maxValue - minValue)) * chartHeight
  ctx.strokeStyle = '#e74c3c'
  ctx.lineWidth = 2
  ctx.setLineDash([5, 5])
  ctx.beginPath()
  ctx.moveTo(padding, targetY)
  ctx.lineTo(width - padding, targetY)
  ctx.stroke()
  ctx.setLineDash([])
  
  // 绘制数据线
  ctx.strokeStyle = '#3498db'
  ctx.lineWidth = 3
  ctx.beginPath()
  
  daily.forEach((day, index) => {
    const x = padding + (chartWidth / (daily.length - 1)) * index
    const y = padding + chartHeight - ((day.total_calories - minValue) / (maxValue - minValue)) * chartHeight
    
    if (index === 0) {
      ctx.moveTo(x, y)
    } else {
      ctx.lineTo(x, y)
    }
  })
  
  ctx.stroke()
  
  // 绘制数据点
  ctx.fillStyle = '#3498db'
  daily.forEach((day, index) => {
    const x = padding + (chartWidth / (daily.length - 1)) * index
    const y = padding + chartHeight - ((day.total_calories - minValue) / (maxValue - minValue)) * chartHeight
    
    ctx.beginPath()
    ctx.arc(x, y, 4, 0, Math.PI * 2)
    ctx.fill()
  })
  
  // 绘制坐标轴标签
  ctx.fillStyle = '#7f8c8d'
  ctx.font = '12px Arial'
  ctx.textAlign = 'center'
  
  // X轴标签（日期）
  daily.forEach((day, index) => {
    const x = padding + (chartWidth / (daily.length - 1)) * index
    const date = new Date(day.date)
    const label = `${date.getMonth() + 1}/${date.getDate()}`
    ctx.fillText(label, x, height - 10)
  })
  
  // Y轴标签（卡路里）
  ctx.textAlign = 'right'
  for (let i = 0; i <= 5; i++) {
    const y = padding + (chartHeight / 5) * i
    const value = Math.round(maxValue - (maxValue - minValue) * (i / 5))
    ctx.fillText(value + '', padding - 10, y + 4)
  }
}

const drawMealsChart = () => {
  const canvas = mealsChart.value
  if (!canvas) return
  
  const ctx = canvas.getContext('2d')
  const { width, height } = canvas
  
  // 清空画布
  ctx.clearRect(0, 0, width, height)
  
  const meals = Object.entries(mealDistribution.value)
  if (meals.length === 0) {
    // 绘制无数据提示
    ctx.fillStyle = '#7f8c8d'
    ctx.font = '16px Arial'
    ctx.textAlign = 'center'
    ctx.fillText('暂无数据', width / 2, height / 2)
    return
  }
  
  // 饼图设置
  const centerX = width / 2
  const centerY = height / 2
  const radius = Math.min(width, height) / 2 - 30
  
  const colors = {
    breakfast: '#ff7675',
    lunch: '#74b9ff',
    dinner: '#fd79a8',
    snack: '#fdcb6e'
  }
  
  let currentAngle = -Math.PI / 2
  
  meals.forEach(([type, meal]) => {
    const percentage = meal.percentage
    const sliceAngle = (percentage / 100) * Math.PI * 2
    
    // 绘制扇形
    ctx.fillStyle = colors[type] || '#95a5a6'
    ctx.beginPath()
    ctx.moveTo(centerX, centerY)
    ctx.arc(centerX, centerY, radius, currentAngle, currentAngle + sliceAngle)
    ctx.closePath()
    ctx.fill()
    
    // 绘制标签
    const labelAngle = currentAngle + sliceAngle / 2
    const labelX = centerX + Math.cos(labelAngle) * (radius * 0.7)
    const labelY = centerY + Math.sin(labelAngle) * (radius * 0.7)
    
    ctx.fillStyle = 'white'
    ctx.font = 'bold 14px Arial'
    ctx.textAlign = 'center'
    ctx.fillText(`${percentage}%`, labelX, labelY)
    
    currentAngle += sliceAngle
  })
  
  // 绘制中心圆
  ctx.fillStyle = 'white'
  ctx.beginPath()
  ctx.arc(centerX, centerY, radius * 0.4, 0, Math.PI * 2)
  ctx.fill()
  
  // 绘制中心文字
  ctx.fillStyle = '#2c3e50'
  ctx.font = 'bold 16px Arial'
  ctx.textAlign = 'center'
  ctx.fillText('餐次', centerX, centerY - 5)
  ctx.font = '12px Arial'
  ctx.fillText('分布', centerX, centerY + 10)
}

// 监听器
watch(() => props.weeklyStats, () => {
  nextTick(() => {
    if (activeTab.value === 'calories') {
      drawCaloriesChart()
    } else if (activeTab.value === 'meals') {
      drawMealsChart()
    }
  })
}, { deep: true })

watch(activeTab, (newTab) => {
  nextTick(() => {
    if (newTab === 'calories') {
      drawCaloriesChart()
    } else if (newTab === 'meals') {
      drawMealsChart()
    }
  })
})

// 生命周期
onMounted(() => {
  nextTick(() => {
    drawCaloriesChart()
    drawMealsChart()
  })
})
</script>

<style scoped>
@import '../styles/components/diet-chart.css';
</style>