<script>
import { backendApi } from "../services/api";

export default {
  name: "SystemHealth",
  inject: ["toast"],
  data() {
    return {
      loading: true,
      healthData: null,
      error: false,
      refreshInterval: null,
      countdown: 60,
      countdownInterval: null
    };
  },
  async mounted() {
    await this.fetchHealth();
    this.startAutoRefresh();
  },
  beforeUnmount() {
    if (this.refreshInterval) clearInterval(this.refreshInterval);
    if (this.countdownInterval) clearInterval(this.countdownInterval);
  },
  methods: {
    async fetchHealth() {
      this.loading = true;
      this.error = false;
      this.countdown = 60; // Reset countdown at the START of each fetch
      try {
        // Pass a unique timestamp to bypass the Axios in-memory GET cache.
        // Without this, manual Refresh would silently return stale data for 3 minutes.
        const { data } = await backendApi.get("/health/system", {
          params: { _t: Date.now() }
        });
        this.healthData = data;
      } catch (err) {
        console.error("Failed to fetch system health:", err);
        this.error = true;
      } finally {
        this.loading = false;
      }
    },
    startAutoRefresh() {
      this.refreshInterval = setInterval(() => {
        this.fetchHealth();
      }, 60000);
      
      this.countdownInterval = setInterval(() => {
        if (this.countdown > 0) this.countdown--;
      }, 1000);
    },
    getStatusColor(status) {
      if (!status) return "secondary";
      const s = status.toLowerCase();
      if (s === "healthy" || s === "online" || s === "connected") return "success";
      if (s === "warning") return "warning";
      if (s === "offline" || s === "disconnected" || s === "error") return "danger";
      return "secondary";
    },
    getStatusIcon(status) {
      const color = this.getStatusColor(status);
      if (color === "success") return "🟢";
      if (color === "warning") return "🟡";
      if (color === "danger") return "🔴";
      return "⚪";
    },
    formatName(key) {
      const names = {
        steam: "Steam Store API",
        rawg: "RAWG",
        cheapshark: "CheapShark",
        itad: "ITAD",
        newsapi: "NewsAPI",
        coingecko: "CoinGecko",
        frankfurter: "Frankfurter",
        paypal: "PayPal"
      };
      return names[key] || key;
    },
    formatDate(isoString) {
      if (!isoString) return "Unknown";
      const date = new Date(isoString);
      return date.toLocaleString();
    }
  }
};
</script>

<template>
  <div class="system-health-container">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <div>
        <h3 class="pane-title m-0">System Health Overview</h3>
        <p class="text-muted small m-0">
          Monitoring operational status of internal application services and external API dependencies.
        </p>
      </div>
      <div class="d-flex align-items-center gap-3">
        <span class="text-muted small" v-if="!loading && !error">
          Auto-refresh in {{ countdown }}s
        </span>
        <button class="btn btn-outline-primary btn-sm rounded-pill px-3" @click="fetchHealth" :disabled="loading">
          <i class="bi bi-arrow-clockwise me-1" :class="{'spin-icon': loading}"></i> 
          {{ loading ? 'Refreshing...' : 'Refresh' }}
        </button>
      </div>
    </div>

    <div v-if="error" class="alert alert-danger d-flex align-items-center mb-4" role="alert">
      <i class="bi bi-exclamation-triangle-fill me-3 fs-4"></i>
      <div>
        <strong>Connection Error</strong><br>
        Unable to retrieve system health data. The backend might be offline or unreachable.
      </div>
    </div>

    <div v-if="healthData" class="row g-4">
      <!-- Core Infrastructure -->
      <div class="col-md-6">
        <div class="gh-widget h-100">
          <div class="widget-header">
            <h5 class="mb-0 fw-bold"><i class="bi bi-server me-2 text-primary"></i> Application Core</h5>
          </div>
          <div class="widget-body">
            <ul class="list-group list-group-flush bg-transparent">
              <li class="list-group-item bg-transparent text-light border-secondary d-flex justify-content-between align-items-center px-0">
                <span>Frontend</span>
                <span class="badge" :class="'bg-' + getStatusColor(healthData.frontend) + '-subtle text-' + getStatusColor(healthData.frontend)">
                  {{ getStatusIcon(healthData.frontend) }} {{ healthData.frontend.toUpperCase() }}
                </span>
              </li>
              <li class="list-group-item bg-transparent text-light border-secondary d-flex justify-content-between align-items-center px-0">
                <span>Backend Server</span>
                <span class="badge" :class="'bg-' + getStatusColor(healthData.backend) + '-subtle text-' + getStatusColor(healthData.backend)">
                  {{ getStatusIcon(healthData.backend) }} {{ healthData.backend.toUpperCase() }}
                </span>
              </li>
              <li class="list-group-item bg-transparent text-light border-secondary d-flex justify-content-between align-items-center px-0">
                <span>Firebase Auth</span>
                <span class="badge" :class="'bg-' + getStatusColor(healthData.firebase?.authentication) + '-subtle text-' + getStatusColor(healthData.firebase?.authentication)">
                  {{ getStatusIcon(healthData.firebase?.authentication) }} {{ (healthData.firebase?.authentication || 'Unknown').toUpperCase() }}
                </span>
              </li>
              <li class="list-group-item bg-transparent text-light border-secondary d-flex justify-content-between align-items-center px-0 border-0">
                <span>Firestore Database</span>
                <span class="badge" :class="'bg-' + getStatusColor(healthData.firebase?.firestore) + '-subtle text-' + getStatusColor(healthData.firebase?.firestore)">
                  {{ getStatusIcon(healthData.firebase?.firestore) }} {{ (healthData.firebase?.firestore || 'Unknown').toUpperCase() }}
                </span>
              </li>
            </ul>
          </div>
        </div>
      </div>

      <!-- External APIs -->
      <div class="col-md-6">
        <div class="gh-widget h-100">
          <div class="widget-header">
            <h5 class="mb-0 fw-bold"><i class="bi bi-globe me-2 text-info"></i> External APIs</h5>
          </div>
          <div class="widget-body p-0">
            <ul class="list-group list-group-flush bg-transparent">
              <li v-for="(status, api) in healthData.apis" :key="api" class="list-group-item bg-transparent text-light border-secondary d-flex justify-content-between align-items-center px-3 py-3">
                <span class="fw-medium">{{ formatName(api) }}</span>
                <div class="d-flex align-items-center gap-2">
                  <span v-if="healthData.fallback && healthData.fallback[api]" class="badge bg-info text-dark me-1 fw-bold" title="Fallback Active">
                    <i class="bi bi-info-circle-fill me-1"></i> Fallback Active: {{ healthData.fallback[api] }}
                  </span>
                  
                  <span class="badge rounded-pill px-3" :class="'bg-' + getStatusColor(status)">
                    {{ getStatusIcon(status) }} {{ (status || 'Unknown').toUpperCase() }}
                  </span>
                </div>
              </li>
            </ul>
          </div>
        </div>
      </div>
      
      <div class="col-12 text-end text-muted small mt-3">
        Last Checked: {{ formatDate(healthData.lastCheck) }}
      </div>
    </div>
    
    <div v-else-if="loading && !healthData" class="d-flex justify-content-center py-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
    </div>
  </div>
</template>

<style scoped>
.system-health-container {
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

.spin-icon {
  animation: spin 1s linear infinite;
  display: inline-block;
}

@keyframes spin {
  100% { transform: rotate(360deg); }
}

.gh-widget {
  background: var(--gh-card-bg, rgba(20, 20, 25, 0.7));
  border: 1px solid var(--gh-border, rgba(255, 255, 255, 0.1));
  border-radius: 12px;
  backdrop-filter: blur(10px);
  overflow: hidden;
}

.widget-header {
  padding: 1rem 1.25rem;
  border-bottom: 1px solid var(--gh-border, rgba(255, 255, 255, 0.1));
  background: rgba(0, 0, 0, 0.2);
}

.widget-body {
  padding: 1.25rem;
}

.list-group-item {
  color: var(--gh-text, #e9ecef);
}

.bg-success-subtle {
  background-color: rgba(25, 135, 84, 0.1) !important;
}

.bg-warning-subtle {
  background-color: rgba(255, 193, 7, 0.1) !important;
}

.bg-danger-subtle {
  background-color: rgba(220, 53, 69, 0.1) !important;
}
</style>
