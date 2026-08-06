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
  computed: {
    overallStatus() {
      if (!this.healthData) return null;
      
      const statuses = [
        this.healthData.frontend,
        this.healthData.backend,
        this.healthData.firebase?.authentication,
        this.healthData.firebase?.firestore,
        ...Object.values(this.healthData.apis || {})
      ].map(s => this.getStatusColor(s));
      
      if (statuses.includes("danger")) return "danger";
      if (statuses.includes("warning")) return "warning";
      return "success";
    },
    overallMessage() {
      if (this.overallStatus === "success") return { title: "All Systems Operational", desc: "We are not aware of any issues affecting GameHub." };
      if (this.overallStatus === "warning") return { title: "Degraded Performance", desc: "Some non-critical systems are experiencing issues." };
      return { title: "Partial System Outage", desc: "One or more services are currently experiencing an outage." };
    }
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
      if (s === "healthy" || s === "online" || s === "connected" || s === "success") return "success";
      if (s === "warning") return "warning";
      if (s === "offline" || s === "disconnected" || s === "error" || s === "danger") return "danger";
      return "secondary";
    },
    getStatusIconClass(status) {
      const color = this.getStatusColor(status);
      if (color === "success") return "bi bi-check-circle-fill";
      if (color === "warning") return "bi bi-exclamation-circle-fill";
      if (color === "danger") return "bi bi-x-circle-fill";
      return "bi bi-question-circle-fill";
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
        <h3 class="pane-title m-0 fw-bold">System Status</h3>
      </div>
      <div class="d-flex align-items-center gap-3">
        <span class="text-muted small" v-if="!loading && !error">
          Auto-refresh in {{ countdown }}s
        </span>
        <button class="btn btn-gh-text btn-sm" @click="fetchHealth" :disabled="loading">
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

    <div v-if="healthData">
      
      <!-- OpenAI-style Status Banner -->
      <div class="status-banner mb-4" :class="'status-banner-' + overallStatus">
        <div class="d-flex align-items-center gap-3">
          <i :class="getStatusIconClass(overallStatus)" class="fs-4 banner-icon"></i>
          <div>
            <h5 class="mb-1 fw-bold">{{ overallMessage.title }}</h5>
            <p class="mb-0 banner-desc">{{ overallMessage.desc }}</p>
          </div>
        </div>
      </div>

      <div class="row g-4">
        <!-- Core Infrastructure -->
        <div class="col-md-6">
          <div class="gh-widget h-100">
            <div class="widget-header">
              <h5 class="mb-0 fw-bold text-light">Application Core</h5>
            </div>
            <div class="widget-body p-0">
              <ul class="list-group list-group-flush bg-transparent">
                <li class="list-group-item bg-transparent text-light border-secondary d-flex justify-content-between align-items-center px-4 py-3">
                  <span class="fw-medium">Frontend</span>
                  <span class="status-indicator fw-bold" :class="'text-' + getStatusColor(healthData.frontend)">
                    <i :class="getStatusIconClass(healthData.frontend)" class="me-1"></i> {{ healthData.frontend.toUpperCase() }}
                  </span>
                </li>
                <li class="list-group-item bg-transparent text-light border-secondary d-flex justify-content-between align-items-center px-4 py-3">
                  <span class="fw-medium">Backend Server</span>
                  <span class="status-indicator fw-bold" :class="'text-' + getStatusColor(healthData.backend)">
                    <i :class="getStatusIconClass(healthData.backend)" class="me-1"></i> {{ healthData.backend.toUpperCase() }}
                  </span>
                </li>
                <li class="list-group-item bg-transparent text-light border-secondary d-flex justify-content-between align-items-center px-4 py-3">
                  <span class="fw-medium">Firebase Auth</span>
                  <span class="status-indicator fw-bold" :class="'text-' + getStatusColor(healthData.firebase?.authentication)">
                    <i :class="getStatusIconClass(healthData.firebase?.authentication)" class="me-1"></i> {{ (healthData.firebase?.authentication || 'Unknown').toUpperCase() }}
                  </span>
                </li>
                <li class="list-group-item bg-transparent text-light border-secondary d-flex justify-content-between align-items-center px-4 py-3 border-0">
                  <span class="fw-medium">Firestore Database</span>
                  <span class="status-indicator fw-bold" :class="'text-' + getStatusColor(healthData.firebase?.firestore)">
                    <i :class="getStatusIconClass(healthData.firebase?.firestore)" class="me-1"></i> {{ (healthData.firebase?.firestore || 'Unknown').toUpperCase() }}
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
              <h5 class="mb-0 fw-bold text-light">External APIs</h5>
            </div>
            <div class="widget-body p-0">
              <ul class="list-group list-group-flush bg-transparent">
                <li v-for="(status, api) in healthData.apis" :key="api" class="list-group-item bg-transparent text-light border-secondary d-flex justify-content-between align-items-center px-4 py-3">
                  <span class="fw-medium">{{ formatName(api) }}</span>
                  <div class="d-flex align-items-center gap-3">
                    <span v-if="healthData.fallback && healthData.fallback[api]" class="badge bg-info text-dark rounded-pill px-3 py-1" title="Fallback Active">
                      <i class="bi bi-info-circle-fill me-1"></i> Fallback: {{ healthData.fallback[api] }}
                    </span>
                    
                    <span class="status-indicator fw-bold" :class="'text-' + getStatusColor(status)">
                      <i :class="getStatusIconClass(status)" class="me-1"></i> {{ (status || 'Unknown').toUpperCase() }}
                    </span>
                  </div>
                </li>
              </ul>
            </div>
          </div>
        </div>
        
        <div class="col-12 text-end text-muted small mt-2">
          Last updated: {{ formatDate(healthData.lastCheck) }}
        </div>
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
  overflow: hidden;
}

.widget-header {
  padding: 1.25rem 1.5rem;
  border-bottom: 1px solid var(--gh-border, rgba(255, 255, 255, 0.1));
  background: rgba(0, 0, 0, 0.3);
}

.list-group-item {
  color: var(--gh-text, #e9ecef);
  font-size: 0.95rem;
}

.status-indicator {
  font-size: 0.85rem;
  letter-spacing: 0.5px;
  display: flex;
  align-items: center;
}

/* OpenAI Style Banner */
.status-banner {
  border-radius: 12px;
  padding: 1.25rem 1.5rem;
  border: 1px solid transparent;
}

.status-banner-success {
  background-color: rgba(25, 135, 84, 0.1);
  border-color: rgba(25, 135, 84, 0.3);
  color: #75b798;
}
.status-banner-success .banner-icon { color: #198754; }

.status-banner-warning {
  background-color: rgba(255, 193, 7, 0.1);
  border-color: rgba(255, 193, 7, 0.3);
  color: #ffda6a;
}
.status-banner-warning .banner-icon { color: #ffc107; }

.status-banner-danger {
  background-color: rgba(220, 53, 69, 0.1);
  border-color: rgba(220, 53, 69, 0.3);
  color: #ea868f;
}
.status-banner-danger .banner-icon { color: #dc3545; }

.banner-desc {
  font-size: 0.95rem;
  opacity: 0.9;
}
</style>
