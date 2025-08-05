<template>
  <div class="exercise-chart">
    <div class="chart-header">
      <h3>运动数据可视化</h3>
      <p class="chart-description">最近一周的运动数据分析</p>
    </div>

      <!-- 趋势图表 -->
      <div class="chart-section">
        <div class="chart-container">
          <h4 class="chart-title">每日运动时长趋势</h4>
          <canvas ref="durationChart" class="chart-canvas"></canvas>
        </div>

        <div class="chart-container">
          <h4 class="chart-title">每日卡路里消耗趋势</h4>
          <canvas ref="caloriesChart" class="chart-canvas"></canvas>
        </div>
      </div>

      <!-- 运动类型分布 -->
      <div class="chart-section">
        <div class="chart-container">
          <h4 class="chart-title">运动类型分布</h4>
          <canvas ref="typeChart" class="chart-canvas pie-chart"></canvas>
        </div>
      </div>

      <!-- 健身分析 -->
      <div class="chart-section">
        <div class="analysis-container">
          <h4 class="chart-title">健身分析</h4>
          <div class="analysis-content">

            <!-- 健身评分 -->
            <div class="score-section">
              <div class="score-circle" :style="{ background: getScoreGradient(weeklyData.fitness_score) }">
                <span class="score-number">{{ weeklyData.fitness_score || 0 }}</span>
                <span class="score-label">健身评分</span>
              </div>
              <div class="score-description">
                <p class="score-text">{{ getScoreText(weeklyData.fitness_score) }}</p>
              </div>
            </div>

            <!-- 运动统计 -->
            <div class="stats-list">
              <div class="stat-item">
                <span class="stat-icon">⏱️</span>
                <div class="stat-info">
                  <header class="stat-header">总运动时长</header>
                  <span class="stat-value">{{ weeklyData.total_duration_hours || 0 }}小时</span>
                </div>
              </div>

              <div class="stat-item">
                <span class="stat-icon">🔥</span>
                <div class="stat-info">
                  <header class="stat-header">总卡路里消耗</header>
                  <span class="stat-value">{{ weeklyData.total_calories_burned || 0 }}卡路里</span>
                </div>
              </div>

              <div class="stat-item">
                <span class="stat-icon">📊</span>
                <div class="stat-info">
                  <header class="stat-header">运动次数</header>
                  <span class="stat-value">{{ (weeklyData.records || []).length }}次</span>
                </div>
              </div>
            </div>

            <!-- 推荐建议 -->
            <div class="recommendations">
              <h5>💡 健康建议</h5>
              <ul class="recommendation-list">
                <li v-for="recommendation in (weeklyData.recommendations || [])" :key="recommendation">
                  {{ recommendation }}
                </li>
                <li v-if="!weeklyData.recommendations || weeklyData.recommendations.length === 0">
                  开始运动吧！每天30分钟的运动有助于身体健康。
                </li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
</template>

<script setup>
import { ref, onMounted, watch, nextTick } from 'vue';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
  Filler
} from 'chart.js';

// 注册Chart.js组件
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend,
  Filler
);

// Props
const props = defineProps({
  weeklyData: {
    type: Object,
    default: () => ({})
  }
});

// 图表实例引用
const durationChart = ref(null);
const caloriesChart = ref(null);
const typeChart = ref(null);

// Chart.js 实例
let durationChartInstance = null;
let caloriesChartInstance = null;
let typeChartInstance = null;

// 生命周期
onMounted(async () => {
  console.log('ExerciseChart mounted, weeklyData:', props.weeklyData);
  await nextTick();
  console.log('Chart.js available, initializing charts...');
  initCharts();
});

// 监听数据变化
watch(() => props.weeklyData, (newData) => {
  console.log('WeeklyData changed:', newData);
  if (newData && Object.keys(newData).length > 0) {
    updateCharts();
  }
}, { deep: true });

// 初始化图表
const initCharts = () => {
  console.log('Initializing charts...');
  initDurationChart();
  initCaloriesChart();
  initTypeChart();
};

// 初始化运动时长趋势图
const initDurationChart = () => {
  console.log('Initializing duration chart...');
  if (!durationChart.value) {
    console.error('Duration chart canvas not found');
    return;
  }

  const ctx = durationChart.value.getContext('2d');
  const data = getDurationChartData();
  console.log('Duration chart data:', data);

  try {
    durationChartInstance = new ChartJS(ctx, {
      type: 'line',
      data: data,
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            display: false
          }
        },
        scales: {
          y: {
            beginAtZero: true,
            title: {
              display: true,
              text: '运动时长 (分钟)'
            }
          },
          x: {
            title: {
              display: true,
              text: '日期'
            }
          }
        },
        elements: {
          line: {
            tension: 0.4
          },
          point: {
            radius: 6,
            hoverRadius: 8
          }
        }
      }
    });
    console.log('Duration chart initialized successfully');
  } catch (error) {
    console.error('Failed to initialize duration chart:', error);
  }
};

// 初始化卡路里消耗趋势图
const initCaloriesChart = () => {
  console.log('Initializing calories chart...');
  if (!caloriesChart.value) {
    console.error('Calories chart canvas not found');
    return;
  }

  const ctx = caloriesChart.value.getContext('2d');
  const data = getCaloriesChartData();
  console.log('Calories chart data:', data);

  try {
    caloriesChartInstance = new ChartJS(ctx, {
      type: 'bar',
      data: data,
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            display: false
          }
        },
        scales: {
          y: {
            beginAtZero: true,
            title: {
              display: true,
              text: '卡路里 (千卡)'
            }
          },
          x: {
            title: {
              display: true,
              text: '日期'
            }
          }
        }
      }
    });
    console.log('Calories chart initialized successfully');
  } catch (error) {
    console.error('Failed to initialize calories chart:', error);
  }
};

// 初始化运动类型分布图
const initTypeChart = () => {
  console.log('Initializing type chart...');
  if (!typeChart.value) {
    console.error('Type chart canvas not found');
    return;
  }

  const ctx = typeChart.value.getContext('2d');
  const data = getTypeChartData();
  console.log('Type chart data:', data);

  try {
    typeChartInstance = new ChartJS(ctx, {
      type: 'doughnut',
      data: data,
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: 'right',
            labels: {
              usePointStyle: true,
              padding: 20
            }
          }
        }
      }
    });
    console.log('Type chart initialized successfully');
  } catch (error) {
    console.error('Failed to initialize type chart:', error);
  }
};

// 获取运动时长图表数据
const getDurationChartData = () => {
  const records = props.weeklyData.records || [];
  console.log('Processing duration chart data for records:', records);

  // 获取最近7天的日期
  const days = getLast7Days();

  // 按日期汇总运动时长
  const dailyDuration = {};
  days.forEach(day => {
    dailyDuration[day] = 0;
  });

  records.forEach(record => {
    const date = record.exercise_date;
    if (dailyDuration.hasOwnProperty(date)) {
      dailyDuration[date] += record.duration_minutes || 0;
    }
  });

  const labels = days.map(day => formatDateLabel(day));
  const data = days.map(day => dailyDuration[day]);

  console.log('Duration chart - labels:', labels, 'data:', data);

  return {
    labels: labels,
    datasets: [{
      label: '运动时长',
      data: data,
      borderColor: '#667eea',
      backgroundColor: 'rgba(102, 126, 234, 0.1)',
      fill: true
    }]
  };
};

// 获取卡路里消耗图表数据
const getCaloriesChartData = () => {
  const records = props.weeklyData.records || [];
  console.log('Processing calories chart data for records:', records);

  // 获取最近7天的日期
  const days = getLast7Days();

  // 按日期汇总卡路里消耗
  const dailyCalories = {};
  days.forEach(day => {
    dailyCalories[day] = 0;
  });

  records.forEach(record => {
    const date = record.exercise_date;
    if (dailyCalories.hasOwnProperty(date)) {
      dailyCalories[date] += record.calories_burned || 0;
    }
  });

  const labels = days.map(day => formatDateLabel(day));
  const data = days.map(day => dailyCalories[day]);

  console.log('Calories chart - labels:', labels, 'data:', data);

  return {
    labels: labels,
    datasets: [{
      label: '卡路里消耗',
      data: data,
      backgroundColor: [
        '#FF6384',
        '#36A2EB',
        '#FFCE56',
        '#4BC0C0',
        '#9966FF',
        '#FF9F40',
        '#FF6384'
      ]
    }]
  };
};

// 获取运动类型分布图表数据
const getTypeChartData = () => {
  const records = props.weeklyData.records || [];
  console.log('Processing type chart data for records:', records);

  // 统计各运动类型的次数
  const typeCount = {};
  records.forEach(record => {
    const type = record.exercise_type_display || record.exercise_type || '未知';
    typeCount[type] = (typeCount[type] || 0) + 1;
  });

  let labels = Object.keys(typeCount);
  let data = Object.values(typeCount);

  // 如果没有数据，提供默认数据
  if (labels.length === 0) {
    labels = ['暂无数据'];
    data = [1];
  }

  console.log('Type chart - labels:', labels, 'data:', data);

  const colors = [
    '#FF6384',
    '#36A2EB',
    '#FFCE56',
    '#4BC0C0',
    '#9966FF',
    '#FF9F40',
    '#C9CBCF',
    '#4BC0C0',
    '#FF6384',
    '#36A2EB'
  ];

  return {
    labels: labels,
    datasets: [{
      data: data,
      backgroundColor: colors.slice(0, labels.length),
      borderWidth: 2,
      borderColor: '#fff'
    }]
  };
};

// 更新图表
const updateCharts = () => {
  if (durationChartInstance) {
    durationChartInstance.data = getDurationChartData();
    durationChartInstance.update();
  }

  if (caloriesChartInstance) {
    caloriesChartInstance.data = getCaloriesChartData();
    caloriesChartInstance.update();
  }

  if (typeChartInstance) {
    typeChartInstance.data = getTypeChartData();
    typeChartInstance.update();
  }
};

// 工具函数
const getLast7Days = () => {
  const days = [];
  for (let i = 6; i >= 0; i--) {
    const date = new Date();
    date.setDate(date.getDate() - i);
    days.push(date.toISOString().split('T')[0]);
  }
  return days;
};

const formatDateLabel = (dateString) => {
  const date = new Date(dateString);
  return date.toLocaleDateString('zh-CN', {
    month: '2-digit',
    day: '2-digit'
  });
};

const getScoreGradient = (score) => {
  score = score || 0;
  if (score >= 80) {
    return 'conic-gradient(#4CAF50 0deg, #4CAF50 ' + (score * 3.6) + 'deg, #f0f0f0 ' + (score * 3.6) + 'deg)';
  } else if (score >= 60) {
    return 'conic-gradient(#FFC107 0deg, #FFC107 ' + (score * 3.6) + 'deg, #f0f0f0 ' + (score * 3.6) + 'deg)';
  } else {
    return 'conic-gradient(#FF5722 0deg, #FF5722 ' + (score * 3.6) + 'deg, #f0f0f0 ' + (score * 3.6) + 'deg)';
  }
};

const getScoreText = (score) => {
  score = score || 0;
  if (score >= 90) return '优秀！保持这个状态';
  if (score >= 80) return '良好，继续努力';
  if (score >= 60) return '还不错，可以再加把劲';
  if (score >= 40) return '需要增加运动量';
  return '建议制定运动计划';
};
</script>

<style scoped>
@import '../styles/components/exercise-chart.css';
</style>