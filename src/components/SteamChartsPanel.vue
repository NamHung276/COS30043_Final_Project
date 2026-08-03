<script>
/**
 * SteamChartsPanel.vue — Live player count sidebar card powered by SteamCharts.
 *
 * Shows:
 *   - Current players online (with animated live indicator)
 *   - 24-hour peak
 *   - All-time peak
 *
 * This data is completely ADDITIVE — RAWG has no live player count data.
 * Hides itself when steamchartsData is null.
 */
export default {
  name: "SteamChartsPanel",

  props: {
    /** SteamCharts data object from the aggregated backend response. */
    steamchartsData: {
      type: Object,
      default: null,
    },
    /** Show skeleton loaders while data is loading */
    loading: {
      type: Boolean,
      default: false,
    },
  },

  methods: {
    formatNum(n) {
      if (n == null) return "—";
      if (n >= 1_000_000) return (n / 1_000_000).toFixed(1) + "M";
      if (n >= 1_000) return n.toLocaleString();
      return String(n);
    },
  },
};
</script>

<template>
  <!-- Skeleton while loading -->
  <div
    v-if="loading"
    class="scp-card profile-glass-card p-4 rounded-4 mt-4"
    aria-busy="true"
    aria-label="Loading player counts"
  >
    <div class="scp-skeleton-header mb-4"></div>
    <div class="scp-skeleton-stat mb-3"></div>
    <div class="scp-skeleton-stat mb-3"></div>
    <div class="scp-skeleton-stat"></div>
  </div>

  <!-- Populated card -->
  <div
    v-else-if="steamchartsData"
    class="scp-card profile-glass-card p-4 rounded-4 mt-4"
  >
    <!-- Header -->
    <div class="d-flex align-items-center justify-content-between mb-4">
      <h5 class="scp-heading mb-0">
        <i class="bi bi-bar-chart-fill me-2 text-info"></i>
        Live Player Counts
      </h5>
      <a
        v-if="steamchartsData.source_url"
        :href="steamchartsData.source_url"
        target="_blank"
        rel="noopener noreferrer"
        class="scp-source-link"
        aria-label="View on SteamCharts"
      >
        SteamCharts <i class="bi bi-box-arrow-up-right ms-1"></i>
      </a>
    </div>

    <!-- Current Players (highlighted) -->
    <div class="scp-current-block mb-4">
      <div class="d-flex align-items-center gap-2 mb-1">
        <span class="scp-live-dot" aria-hidden="true"></span>
        <span class="scp-current-label">Currently Playing</span>
      </div>
      <div class="scp-current-num">{{ formatNum(steamchartsData.live) }}</div>
    </div>

    <!-- Divider -->
    <div class="scp-divider mb-3"></div>

    <!-- Peak Stats -->
    <div class="d-flex flex-column gap-3">
      <div class="scp-stat-row">
        <div class="scp-stat-label">
          <i class="bi bi-clock-history me-2 text-muted"></i>24h Peak
        </div>
        <span class="scp-stat-value">{{ formatNum(steamchartsData.peak_24h) }}</span>
      </div>
      <div class="scp-stat-row">
        <div class="scp-stat-label">
          <i class="bi bi-trophy me-2 text-warning"></i>All-Time Peak
        </div>
        <span class="scp-stat-value scp-alltime">{{ formatNum(steamchartsData.peak_all_time) }}</span>
      </div>
    </div>
  </div>
</template>

<style scoped>
.scp-card {
  background: var(--bg-surface, #1a1a2e);
  border: 1px solid rgba(255, 255, 255, 0.08);
  transition: border-color 0.2s ease;
}
.scp-card:hover {
  border-color: rgba(50, 200, 255, 0.25);
}

.scp-heading {
  font-size: 0.95rem;
  font-weight: 700;
  color: var(--text-primary, #e8eaf6);
}

.scp-source-link {
  font-size: 0.72rem;
  color: #66c8ff;
  text-decoration: none;
  transition: color 0.2s;
}
.scp-source-link:hover { color: #99daff; }

/* Current players */
.scp-current-block {
  background: rgba(50, 200, 255, 0.06);
  border: 1px solid rgba(50, 200, 255, 0.15);
  border-radius: 10px;
  padding: 12px 16px;
}
.scp-current-label {
  font-size: 0.72rem;
  font-weight: 700;
  color: #66c8ff;
  text-transform: uppercase;
  letter-spacing: 0.08em;
}
.scp-current-num {
  font-size: 2rem;
  font-weight: 800;
  color: #fff;
  line-height: 1.1;
  font-variant-numeric: tabular-nums;
}

/* Live dot */
.scp-live-dot {
  width: 8px;
  height: 8px;
  background: #5eff91;
  border-radius: 50%;
  display: inline-block;
  box-shadow: 0 0 6px #5eff91;
  animation: scp-pulse 2s ease-in-out infinite;
  flex-shrink: 0;
}
@keyframes scp-pulse {
  0%, 100% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.5; transform: scale(0.8); }
}

.scp-divider {
  border-top: 1px solid rgba(255, 255, 255, 0.08);
}

/* Stat rows */
.scp-stat-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.scp-stat-label {
  font-size: 0.82rem;
  color: var(--text-muted, #9e9e9e);
}
.scp-stat-value {
  font-size: 1rem;
  font-weight: 700;
  color: var(--text-primary, #e8eaf6);
  font-variant-numeric: tabular-nums;
}
.scp-alltime {
  color: #ffd86e;
}

/* Skeleton */
.scp-skeleton-header {
  height: 16px;
  width: 55%;
  background: linear-gradient(90deg, rgba(255,255,255,0.06) 25%, rgba(255,255,255,0.12) 50%, rgba(255,255,255,0.06) 75%);
  background-size: 200% 100%;
  animation: scp-shimmer 1.4s infinite;
  border-radius: 6px;
}
.scp-skeleton-stat {
  height: 28px;
  background: linear-gradient(90deg, rgba(255,255,255,0.05) 25%, rgba(255,255,255,0.10) 50%, rgba(255,255,255,0.05) 75%);
  background-size: 200% 100%;
  animation: scp-shimmer 1.4s infinite;
  border-radius: 6px;
}
@keyframes scp-shimmer {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}
</style>
