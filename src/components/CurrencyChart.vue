<script setup>
import { ref, watch, onMounted } from 'vue';
import { backendApi } from '../services/api';
import { Line } from 'vue-chartjs';
import { Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend, Filler } from 'chart.js';

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend, Filler);

const props = defineProps({
  from: String,
  to: String
});

const chartData = ref({
  labels: [],
  datasets: []
});
const chartOptions = ref({
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      display: false
    },
    tooltip: {
      mode: 'index',
      intersect: false,
      backgroundColor: 'rgba(0, 0, 0, 0.8)',
      titleColor: '#fff',
      bodyColor: '#fff',
      borderColor: 'rgba(255, 255, 255, 0.1)',
      borderWidth: 1,
    }
  },
  scales: {
    x: {
      grid: {
        color: 'rgba(255, 255, 255, 0.05)'
      },
      ticks: {
        color: '#aaa',
        maxTicksLimit: 8
      }
    },
    y: {
      grid: {
        color: 'rgba(255, 255, 255, 0.05)'
      },
      ticks: {
        color: '#aaa'
      }
    }
  },
  interaction: {
    mode: 'nearest',
    axis: 'x',
    intersect: false
  }
});

const loading = ref(false);
const error = ref(null);
const trendText = ref('');
const trendClass = ref('');

const fetchHistory = async () => {
  if (!props.from || !props.to) return;
  if (props.from === props.to) {
    error.value = "Cannot compare the same currency.";
    return;
  }
  
  loading.value = true;
  error.value = null;
  
  try {
    const res = await backendApi.get('/currency/history', {
      params: {
        from_curr: props.from,
        to_curr: props.to,
        days: 30
      }
    });
    
    if (res.data && res.data.rates) {
      const dates = Object.keys(res.data.rates);
      const values = dates.map(date => res.data.rates[date][props.to]);
      
      chartData.value = {
        labels: dates,
        datasets: [
          {
            label: `${props.from} to ${props.to}`,
            data: values,
            borderColor: '#6366f1',
            backgroundColor: 'rgba(99, 102, 241, 0.1)',
            borderWidth: 2,
            pointRadius: 0,
            pointHoverRadius: 4,
            fill: true,
            tension: 0.3
          }
        ]
      };
      
      if (values.length >= 2) {
        const first = values[0];
        const last = values[values.length - 1];
        const diff = last - first;
        const pct = (diff / first) * 100;
        
        if (diff > 0) {
          trendText.value = `+${diff.toFixed(4)} (+${pct.toFixed(2)}%)`;
          trendClass.value = 'text-success';
        } else {
          trendText.value = `${diff.toFixed(4)} (${pct.toFixed(2)}%)`;
          trendClass.value = 'text-danger';
        }
      } else {
        trendText.value = '';
      }
    }
  } catch (err) {
    console.error("Chart fetch err", err);
    error.value = "Failed to load historical data.";
  } finally {
    loading.value = false;
  }
};

watch(() => [props.from, props.to], () => {
  fetchHistory();
});

onMounted(() => {
  fetchHistory();
});
</script>

<template>
  <div class="currency-chart-container mt-4">
    <div class="chart-header d-flex justify-content-between align-items-center mb-3">
      <div>
        <h5 class="mb-0 text-white">30-Day History</h5>
        <small class="text-muted">{{ from }} vs {{ to }}</small>
      </div>
      <div v-if="trendText && !error" :class="trendClass" class="fw-bold">
        <i :class="trendClass === 'text-success' ? 'bi bi-arrow-up-right' : 'bi bi-arrow-down-right'"></i>
        {{ trendText }}
      </div>
    </div>
    
    <div class="chart-wrapper">
      <div v-if="loading" class="chart-loading skeleton"></div>
      <div v-else-if="error" class="chart-error text-danger">{{ error }}</div>
      <Line v-else :data="chartData" :options="chartOptions" />
    </div>
  </div>
</template>

<style scoped>
.currency-chart-container {
  background: var(--bg-surface, #1e1e24);
  border: 1px solid var(--border-color, rgba(255, 255, 255, 0.1));
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.2);
  width: 100%;
}

.chart-wrapper {
  height: 250px;
  width: 100%;
  position: relative;
}

.chart-loading {
  width: 100%;
  height: 100%;
  border-radius: 8px;
  background: var(--overlay-light, rgba(255, 255, 255, 0.05));
}

.chart-error {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  text-align: center;
}
</style>
