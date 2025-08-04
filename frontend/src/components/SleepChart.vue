<template>
  <div class="sleep-chart">
    <div v-if="!hasData" class="no-data">
      <div class="no-data-icon">📊</div>
      <h3>暂无数据</h3>
      <p>需要至少一条睡眠记录才能显示图表</p>
    </div>
    
    <div v-else class="chart-container">
      <!-- 睡眠时长趋势图 -->
      <div class="chart-item">
        <h3 class="chart-title">睡眠时长趋势</h3>
        <canvas ref="sleepDurationChart" class="chart-canvas"></canvas>
      </div>
      
      <!-- 睡眠质量评分 -->
      <div class="chart-item">
        <h3 class="chart-title">睡眠质量评分</h3>
        <canvas ref="sleepQualityChart" class="chart-canvas"></canvas>
      </div>
      
      <!-- 睡眠建议 -->
      <div v-if="weeklyData.recommendations && weeklyData.recommendations.length > 0" class="recommendations">
        <h3 class="recommendations-title">健康建议</h3>
        <ul class="recommendations-list">
          <li v-for="(recommendation, index) in weeklyData.recommendations" :key="index">
            {{ recommendation }}
          </li>
        </ul>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, nextTick } from 'vue';
import { Chart, registerables } from 'chart.js';

// 注册Chart.js组件
Chart.register(...registerables);

// Props
const props = defineProps({
  weeklyData: {
    type: Object,
    default: () => ({})
  }
});

// 模板引用
const sleepDurationChart = ref(null);
const sleepQualityChart = ref(null);

// Chart实例
let durationChart = null;
let qualityChart = null;

// 计算属性
const hasData = computed(() => {
  return props.weeklyData.records && props.weeklyData.records.length > 0;
});

// 监听数据变化
watch(() => props.weeklyData, () => {
  nextTick(() => {
    updateCharts();
  });
}, { deep: true });

// 生命周期
onMounted(() => {
  nextTick(() => {
    initCharts();
  });
});

// 初始化图表
function initCharts() {
  if (!hasData.value) return;
  
  createSleepDurationChart();
  createSleepQualityChart();
}

// 更新图表
function updateCharts() {
  if (!hasData.value) {
    destroyCharts();
    return;
  }
  
  if (durationChart) {
    updateSleepDurationChart();
  } else {
    createSleepDurationChart();
  }
  
  if (qualityChart) {
    updateSleepQualityChart();
  } else {
    createSleepQualityChart();
  }
}

// 销毁图表
function destroyCharts() {
  if (durationChart) {
    durationChart.destroy();
    durationChart = null;
  }
  if (qualityChart) {
    qualityChart.destroy();
    qualityChart = null;
  }
}

// 创建睡眠时长趋势图
function createSleepDurationChart() {
  if (!sleepDurationChart.value || !hasData.value) return;
  
  const chartData = prepareDurationChartData();
  
  durationChart = new Chart(sleepDurationChart.value, {
    type: 'line',
    data: chartData,
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          display: false
        },
        tooltip: {
          backgroundColor: '#1a365d',
          titleColor: '#ffffff',
          bodyColor: '#ffffff',
          cornerRadius: 8,
          callbacks: {
            label: function(context) {
              return `睡眠时长: ${context.parsed.y}小时`;
            }
          }
        }
      },
      scales: {
        x: {
          title: {
            display: true,
            text: '日期',
            color: '#4a5568',
            font: {
              size: 12,
              weight: 'bold'
            }
          },
          grid: {
            color: '#e2e8f0'
          },
          ticks: {
            color: '#718096'
          }
        },
        y: {
          title: {
            display: true,
            text: '睡眠时长 (小时)',
            color: '#4a5568',
            font: {
              size: 12,
              weight: 'bold'
            }
          },
          min: 0,
          max: 12,
          grid: {
            color: '#e2e8f0'
          },
          ticks: {
            color: '#718096',
            stepSize: 1
          }
        }
      },
      elements: {
        point: {
          radius: 6,
          hoverRadius: 8,
          backgroundColor: '#3182ce',
          borderColor: '#ffffff',
          borderWidth: 2
        },
        line: {
          borderColor: '#3182ce',
          borderWidth: 3,
          tension: 0.4
        }
      }
    }
  });
}

// 创建睡眠质量评分图
function createSleepQualityChart() {
  if (!sleepQualityChart.value || !hasData.value) return;
  
  const chartData = prepareQualityChartData();
  
  qualityChart = new Chart(sleepQualityChart.value, {
    type: 'bar',
    data: chartData,
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          display: false
        },
        tooltip: {
          backgroundColor: '#1a365d',
          titleColor: '#ffffff',
          bodyColor: '#ffffff',
          cornerRadius: 8,
          callbacks: {
            label: function(context) {
              return `质量评分: ${context.parsed.y}分`;
            }
          }
        }
      },
      scales: {
        x: {
          title: {
            display: true,
            text: '日期',
            color: '#4a5568',
            font: {
              size: 12,
              weight: 'bold'
            }
          },
          grid: {
            color: '#e2e8f0'
          },
          ticks: {
            color: '#718096'
          }
        },
        y: {
          title: {
            display: true,
            text: '质量评分',
            color: '#4a5568',
            font: {
              size: 12,
              weight: 'bold'
            }
          },
          min: 0,
          max: 100,
          grid: {
            color: '#e2e8f0'
          },
          ticks: {
            color: '#718096',
            stepSize: 20
          }
        }
      }
    }
  });
}

// 更新睡眠时长图表数据
function updateSleepDurationChart() {
  if (!durationChart) return;
  
  const chartData = prepareDurationChartData();
  durationChart.data = chartData;
  durationChart.update();
}

// 更新睡眠质量图表数据
function updateSleepQualityChart() {
  if (!qualityChart) return;
  
  const chartData = prepareQualityChartData();
  qualityChart.data = chartData;
  qualityChart.update();
}

// 准备睡眠时长图表数据
function prepareDurationChartData() {
  const records = props.weeklyData.records || [];
  
  // 按日期排序
  const sortedRecords = [...records].sort((a, b) => new Date(a.sleep_date) - new Date(b.sleep_date));
  
  const labels = sortedRecords.map(record => formatDateForChart(record.sleep_date));
  const data = sortedRecords.map(record => record.sleep_duration_hours);
  
  return {
    labels,
    datasets: [{
      label: '睡眠时长',
      data,
      backgroundColor: 'rgba(49, 130, 206, 0.1)',
      borderColor: '#3182ce',
      fill: true
    }]
  };
}

// 准备睡眠质量图表数据
function prepareQualityChartData() {
  const records = props.weeklyData.records || [];
  
  // 按日期排序
  const sortedRecords = [...records].sort((a, b) => new Date(a.sleep_date) - new Date(b.sleep_date));
  
  const labels = sortedRecords.map(record => formatDateForChart(record.sleep_date));
  const data = sortedRecords.map(record => record.sleep_quality_score);
  
  // 根据质量评分设置不同颜色
  const backgroundColors = data.map(score => {
    if (score >= 90) return '#48bb78'; // 优秀 - 绿色
    if (score >= 75) return '#3182ce'; // 良好 - 蓝色
    if (score >= 60) return '#ed8936'; // 一般 - 橙色
    return '#e53e3e'; // 较差 - 红色
  });
  
  return {
    labels,
    datasets: [{
      label: '睡眠质量',
      data,
      backgroundColor: backgroundColors,
      borderColor: backgroundColors,
      borderWidth: 1
    }]
  };
}

// 格式化日期用于图表显示
function formatDateForChart(dateString) {
  const date = new Date(dateString);
  return date.toLocaleDateString('zh-CN', {
    month: '2-digit',
    day: '2-digit'
  });
}

// 组件销毁时清理图表
import { onBeforeUnmount, computed } from 'vue';

onBeforeUnmount(() => {
  destroyCharts();
});
</script>