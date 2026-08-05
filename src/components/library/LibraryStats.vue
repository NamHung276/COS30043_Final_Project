<script setup>
import { computed } from 'vue';
import { Bar } from 'vue-chartjs';
import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend } from 'chart.js';

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend);

const props = defineProps({
  purchase: {
    type: Object,
    required: true
  }
});

const formatDuration = (seconds) => {
  if (!seconds) return '0m';
  const d = Math.floor(seconds / 86400);
  const h = Math.floor((seconds % 86400) / 3600);
  const m = Math.floor((seconds % 3600) / 60);
  if (d > 0) return `${d}d ${h}h ${m}m`;
  if (h > 0) return `${h}h ${m}m`;
  return `${m}m`;
};

const formatDate = (ts) => {
  if (!ts) return 'Never';
  const date = ts.seconds ? new Date(ts.seconds * 1000) : new Date(ts);
  return date.toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' });
};

const totalPlaytime = computed(() => props.purchase.playtime || 0);
const sessions = computed(() => props.purchase.sessions || []);
const sessionCount = computed(() => sessions.value.length);
const avgSession = computed(() => sessionCount.value ? Math.floor(totalPlaytime.value / sessionCount.value) : 0);

// Chart Data (Last 7 Sessions)
const chartData = computed(() => {
  const recent = [...sessions.value].slice(0, 7).reverse();
  return {
    labels: recent.map(s => new Date(s.startTime).toLocaleDateString(undefined, { weekday: 'short' })),
    datasets: [{
      label: 'Minutes Played',
      backgroundColor: 'rgba(56, 189, 248, 0.8)',
      borderColor: '#38bdf8',
      borderWidth: 1,
      borderRadius: 4,
      data: recent.map(s => Math.round(s.duration / 60))
    }]
  };
});

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: { display: false },
    tooltip: {
      backgroundColor: 'rgba(15, 23, 42, 0.9)',
      titleColor: '#fff',
      bodyColor: '#e2e8f0',
      padding: 10,
      cornerRadius: 8
    }
  },
  scales: {
    y: {
      beginAtZero: true,
      grid: { color: 'rgba(255, 255, 255, 0.05)' },
      ticks: { color: '#94a3b8' }
    },
    x: {
      grid: { display: false },
      ticks: { color: '#94a3b8' }
    }
  }
};
</script>

<template>
  <div class="library-stats">
    
    <!-- Top Stat Cards -->
    <div class="row g-3 mb-4">
      <div class="col-md-3 col-6">
        <div class="stat-card bg-dark bg-opacity-50 p-3 rounded-4 border border-secondary border-opacity-25 h-100 d-flex flex-column justify-content-center">
          <span class="text-muted text-uppercase fw-bold mb-1" style="font-size: 0.75rem; letter-spacing: 1px;">Total Playtime</span>
          <span class="fs-3 fw-bold text-white">{{ formatDuration(totalPlaytime) }}</span>
        </div>
      </div>
      <div class="col-md-3 col-6">
        <div class="stat-card bg-dark bg-opacity-50 p-3 rounded-4 border border-secondary border-opacity-25 h-100 d-flex flex-column justify-content-center">
          <span class="text-muted text-uppercase fw-bold mb-1" style="font-size: 0.75rem; letter-spacing: 1px;">Sessions</span>
          <span class="fs-3 fw-bold text-info">{{ sessionCount }}</span>
        </div>
      </div>
      <div class="col-md-3 col-6">
        <div class="stat-card bg-dark bg-opacity-50 p-3 rounded-4 border border-secondary border-opacity-25 h-100 d-flex flex-column justify-content-center">
          <span class="text-muted text-uppercase fw-bold mb-1" style="font-size: 0.75rem; letter-spacing: 1px;">Avg Session</span>
          <span class="fs-3 fw-bold text-warning">{{ formatDuration(avgSession) }}</span>
        </div>
      </div>
      <div class="col-md-3 col-6">
        <div class="stat-card bg-dark bg-opacity-50 p-3 rounded-4 border border-secondary border-opacity-25 h-100 d-flex flex-column justify-content-center">
          <span class="text-muted text-uppercase fw-bold mb-1" style="font-size: 0.75rem; letter-spacing: 1px;">First Played</span>
          <span class="fs-5 fw-bold text-white mt-1">{{ sessions.length ? formatDate(sessions[sessions.length-1].startTime) : 'N/A' }}</span>
        </div>
      </div>
    </div>

    <!-- Chart & Timeline Row -->
    <div class="row g-4">
      
      <!-- Session Chart -->
      <div class="col-lg-7">
        <div class="bg-dark bg-opacity-25 rounded-4 p-4 border border-secondary border-opacity-25 h-100">
          <h5 class="fw-bold mb-4 d-flex align-items-center text-white">
            <i class="bi bi-bar-chart-fill text-primary me-2"></i> Playtime Trend (Last 7 Sessions)
          </h5>
          <div style="height: 250px;" v-if="sessions.length > 0">
            <Bar :data="chartData" :options="chartOptions" />
          </div>
          <div v-else class="h-100 d-flex flex-column align-items-center justify-content-center text-muted" style="min-height: 200px;">
            <i class="bi bi-journal-x fs-1 mb-2"></i>
            <p>No play sessions recorded yet.</p>
          </div>
        </div>
      </div>
      
      <!-- Visual Timeline -->
      <div class="col-lg-5">
        <div class="bg-dark bg-opacity-25 rounded-4 p-4 border border-secondary border-opacity-25 h-100">
          <h5 class="fw-bold mb-4 d-flex align-items-center text-white">
            <i class="bi bi-clock-history text-info me-2"></i> Activity Timeline
          </h5>
          
          <div class="timeline position-relative ps-4" v-if="sessions.length > 0">
            <div class="timeline-line position-absolute top-0 bottom-0 start-0 border-start border-secondary opacity-50 ms-2"></div>
            
            <div v-for="(session, i) in sessions.slice(0, 5)" :key="i" class="timeline-item position-relative mb-4">
              <div class="timeline-dot position-absolute bg-primary rounded-circle border border-dark" style="width: 12px; height: 12px; left: -22.5px; top: 6px;"></div>
              <div class="d-flex justify-content-between align-items-start">
                <div>
                  <h6 class="mb-1 text-white fw-bold">{{ formatDate(session.startTime) }}</h6>
                  <p class="mb-0 text-muted small"><i class="bi bi-play-fill me-1"></i> Played for {{ formatDuration(session.duration) }}</p>
                </div>
                <span class="text-secondary small">{{ new Date(session.startTime).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'}) }}</span>
              </div>
            </div>
          </div>
          
          <div v-else class="text-center text-muted py-4">
            <p>Play the game to start building your timeline!</p>
          </div>
        </div>
      </div>
      
    </div>
  </div>
</template>

<style scoped>
.stat-card {
  transition: transform 0.2s ease, background-color 0.2s ease;
}
.stat-card:hover {
  transform: translateY(-3px);
  background-color: rgba(255,255,255,0.05) !important;
}
.text-primary-var { color: #38bdf8; }
</style>
