<script>
/**
 * ITADDealsPanel.vue — IsThereAnyDeal (ITAD) deal comparison card.
 *
 * Displays:
 *   - Current best offer across official stores
 *   - All-time historical lowest price recorded by ITAD
 *   - Store price comparison list (Steam, GOG, Fanatical, Humble, Epic, etc.)
 *   - Direct links to ITAD & official store deals
 *
 * This component is ADDITIVE — works alongside CheapShark & GG.deals.
 * Hides itself completely when itadDeals is null.
 */
export default {
  name: "ITADDealsPanel",

  props: {
    /** ITAD deals object from aggregated backend response. Null = hidden */
    game: {
      type: Object,
      default: null,
    },
    loading: {
      type: Boolean,
      default: false,
    },
  },

  computed: {
    hasDeals() {
      return (
        this.game &&
        (this.game.price ||
          this.game.historical_low ||
          (this.game.store_deals && this.game.store_deals.length > 0))
      );
    },

    formatCurrency() {
      return (val) => {
        if (val == null) return "$0.00";
        return `$${Number(val).toFixed(2)}`;
      };
    },

    isAtHistoricalLow() {
      if (!this.itadDeals?.current_best || !this.itadDeals?.historical_low) return false;
      const cur = this.game.price.price;
      const low = this.game.historical_low.price;
      return cur <= low + 0.01;
    },

    formattedLowDate() {
      const ts = this.game?.historical_low?.date;
      if (!ts) return "";
      try {
        const d = isNaN(Number(ts)) ? new Date(ts) : new Date(ts * 1000);
        return d.toLocaleDateString(undefined, {
          year: "numeric",
          month: "short",
          day: "numeric",
        });
      } catch {
        return "";
      }
    },
  },
};
</script>

<template>
  <!-- Skeleton loader -->
  <div
    v-if="loading"
    class="itad-card profile-glass-card p-4 rounded-4 mt-4"
    aria-busy="true"
    aria-label="Loading deal comparisons"
  >
    <div class="itad-skeleton-header mb-3"></div>
    <div class="itad-skeleton-row mb-2"></div>
    <div class="itad-skeleton-row mb-2"></div>
    <div class="itad-skeleton-row"></div>
  </div>

  <!-- Populated panel -->
  <div
    v-else-if="hasDeals"
    class="itad-card profile-glass-card p-4 rounded-4 mt-4"
  >
    <!-- Header -->
    <div class="d-flex align-items-center justify-content-between mb-3">
      <h5 class="itad-heading mb-0">
        <i class="bi bi-tags-fill me-2 text-warning"></i>
        Deal Intelligence
      </h5>
      <a
        v-if="false"
        :href="itadDeals.itad_url"
        target="_blank"
        rel="noopener noreferrer"
        class="itad-link"
        aria-label="View on IsThereAnyDeal"
      >
        View on ITAD <i class="bi bi-box-arrow-up-right ms-1"></i>
      </a>
    </div>

    <!-- Smart Historical Low Banner -->
    <div
      v-if="isAtHistoricalLow"
      class="alert alert-success d-flex align-items-center gap-2 p-2 px-3 rounded-3 mb-3 border border-success border-opacity-30"
      style="font-size: 0.78rem;"
    >
      <i class="bi bi-fire text-warning fs-6"></i>
      <div>
        <strong>All-Time Historical Low!</strong>
        This game is currently matching its lowest price ever recorded.
      </div>
    </div>

    <!-- Highlights (Current Best & Historical Low) -->
    <div class="row g-2 mb-3">
      <!-- Current Best -->
      <div v-if="game.price" class="col-6">
        <div class="itad-highlight-box p-3 rounded-3 border border-success border-opacity-25 bg-success bg-opacity-10">
          <div class="itad-label text-success">Current Best</div>
          <div class="itad-price text-success">
            {{ formatCurrency(game.price.final) }}
            <span v-if="game.price.discount_percent > 0" class="badge bg-success ms-1">
              -{{ game.price.discount_percent }}%
            </span>
          </div>
          <div class="itad-subtext">@ {{ game.price.store_name }}</div>
        </div>
      </div>

      <!-- Historical Low -->
      <div v-if="game.historical_low" class="col-6">
        <div class="itad-highlight-box p-3 rounded-3 border border-warning border-opacity-25 bg-warning bg-opacity-10">
          <div class="itad-label text-warning">Historical Low</div>
          <div class="itad-price text-warning">
            {{ formatCurrency(game.historical_low.amount) }}
          </div>
          <div class="itad-subtext">
            @ {{ game.historical_low.store_name }}
            <span v-if="formattedLowDate" class="ms-1">({{ formattedLowDate }})</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Store Deals List -->
    <div v-if="game.store_deals && game.store_deals.length > 0">
      <div class="itad-list-title mb-2">Official Store Prices</div>
      <div class="d-flex flex-column gap-2">
        <a
          v-for="(deal, idx) in game.store_deals.slice(0, 6)"
          :key="idx"
          :href="deal.url"
          target="_blank"
          rel="noopener noreferrer"
          class="itad-deal-item p-2 px-3 rounded-3 d-flex align-items-center justify-content-between text-decoration-none"
        >
          <div class="d-flex align-items-center gap-2">
            <span class="itad-store-name text-light">{{ deal.store_name }}</span>
            <span v-if="deal.cut > 0" class="badge bg-danger bg-opacity-75" style="font-size: 0.65rem">
              -{{ deal.cut }}%
            </span>
          </div>
          <div class="d-flex align-items-center gap-2">
            <span v-if="deal.cut > 0" class="itad-regular-price text-muted text-decoration-line-through">
              {{ formatCurrency(deal.regular_price) }}
            </span>
            <span class="itad-current-price text-success fw-bold">
              {{ formatCurrency(deal.price) }}
            </span>
            <i class="bi bi-chevron-right text-muted small"></i>
          </div>
        </a>
      </div>
    </div>
  </div>
</template>

<style scoped>
.itad-card {
  background: var(--bg-surface, #1a1a2e);
  border: 1px solid rgba(255, 255, 255, 0.08);
  transition: border-color 0.2s ease;
}
.itad-card:hover {
  border-color: rgba(255, 193, 7, 0.25);
}

.itad-heading {
  font-size: 0.95rem;
  font-weight: 700;
  color: var(--text-primary, #e8eaf6);
}

.itad-link {
  font-size: 0.75rem;
  color: #ffc107;
  text-decoration: none;
  transition: color 0.2s;
}
.itad-link:hover { color: #ffdb6d; }

.itad-label {
  font-size: 0.68rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.itad-price {
  font-size: 1.1rem;
  font-weight: 800;
  line-height: 1.2;
}

.itad-subtext {
  font-size: 0.7rem;
  color: var(--text-muted, #9e9e9e);
  margin-top: 2px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.itad-list-title {
  font-size: 0.72rem;
  font-weight: 700;
  color: var(--text-muted, #9e9e9e);
  text-transform: uppercase;
  letter-spacing: 0.08em;
}

.itad-deal-item {
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.06);
  transition: all 0.2s ease;
}
.itad-deal-item:hover {
  background: rgba(255, 255, 255, 0.08);
  border-color: rgba(255, 193, 7, 0.3);
  transform: translateX(2px);
}

.itad-store-name {
  font-size: 0.82rem;
  font-weight: 600;
}

.itad-regular-price {
  font-size: 0.75rem;
}

.itad-current-price {
  font-size: 0.85rem;
}

/* Skeleton */
.itad-skeleton-header {
  height: 18px;
  width: 50%;
  background: linear-gradient(90deg, rgba(255,255,255,0.06) 25%, rgba(255,255,255,0.12) 50%, rgba(255,255,255,0.06) 75%);
  background-size: 200% 100%;
  animation: itad-shimmer 1.4s infinite;
  border-radius: 6px;
}
.itad-skeleton-row {
  height: 36px;
  background: linear-gradient(90deg, rgba(255,255,255,0.04) 25%, rgba(255,255,255,0.08) 50%, rgba(255,255,255,0.04) 75%);
  background-size: 200% 100%;
  animation: itad-shimmer 1.4s infinite;
  border-radius: 8px;
}
@keyframes itad-shimmer {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}
</style>
