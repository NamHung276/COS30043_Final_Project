<script>
/**
 * SteamDataPanel.vue — Steam Store supplementary data sidebar card.
 *
 * Displays Steam-specific information that RAWG does not provide:
 *   - Steam price (current + discount if any)
 *   - Supported languages
 *   - Steam categories (Single-player, Co-op, etc.)
 *   - Achievement count
 *   - Direct Steam store link
 *
 * This component is ADDITIVE — it never replaces RAWG data.
 * It hides itself completely when game is null.
 */
export default {
  name: "ExtraDataPanel",

  props: {
    /** Steam data object from the aggregated backend response. Null = hide panel. */
    game: {
      type: Object,
      default: null,
    },
    /** Show skeleton loaders while data is loading */
    loading: {
      type: Boolean,
      default: false,
    },
  },

  computed: {
    hasPrice() {
      return this.game?.price && !this.game?.is_free;
    },

    hasDiscount() {
      return this.hasPrice && this.game.price.discount_percent > 0;
    },

    topLanguages() {
      return (this.game?.supported_languages || []).slice(0, 6);
    },

    remainingLangsCount() {
      const all = this.game?.supported_languages || [];
      return all.length > 6 ? all.length - 6 : 0;
    },

    topCategories() {
      return (this.game?.categories || []).slice(0, 6);
    },

    achievementsTotal() {
      return this.game?.achievements_total || 0;
    },
  },
};
</script>

<template>
  <!-- Skeleton while loading -->
  <div
    v-if="loading"
    class="sdp-card profile-glass-card p-4 rounded-4 mt-4"
    aria-busy="true"
    aria-label="Loading Steam data"
  >
    <div class="sdp-skeleton-header mb-3"></div>
    <div class="sdp-skeleton-line mb-2" style="width: 80%"></div>
    <div class="sdp-skeleton-line mb-2" style="width: 60%"></div>
    <div class="sdp-skeleton-line" style="width: 70%"></div>
  </div>

  <!-- Populated card -->
  <div
    v-else-if="game"
    class="sdp-card profile-glass-card p-4 rounded-4 mt-4"
  >
    <!-- Header -->
    <div class="d-flex align-items-center justify-content-between mb-4">
      <h5 class="sdp-heading mb-0">
        <svg class="sdp-steam-icon me-2" viewBox="0 0 24 24" fill="currentColor" width="18" height="18">
          <path d="M11.979 0C5.678 0 .511 4.86.022 11.037l6.432 2.658c.545-.371 1.203-.59 1.912-.59.063 0 .125.004.188.006l2.861-4.142V8.91c0-2.495 2.028-4.524 4.524-4.524 2.494 0 4.524 2.031 4.524 4.527s-2.03 4.525-4.524 4.525h-.105l-4.076 2.911c0 .052.004.105.004.159 0 1.875-1.515 3.396-3.39 3.396-1.635 0-3.016-1.173-3.331-2.727L.436 15.27C1.862 20.307 6.486 24 11.979 24c6.627 0 11.999-5.373 11.999-12S18.605 0 11.979 0zM7.54 18.21l-1.473-.61c.262.543.714.999 1.314 1.25 1.297.539 2.793-.076 3.332-1.375.263-.63.264-1.319.005-1.949s-.75-1.121-1.377-1.383c-.624-.26-1.29-.249-1.878-.03l1.523.63c.956.4 1.409 1.5 1.009 2.455-.397.957-1.497 1.41-2.454 1.012H7.54zm11.415-9.303c0-1.662-1.353-3.015-3.015-3.015-1.665 0-3.015 1.353-3.015 3.015 0 1.665 1.35 3.015 3.015 3.015 1.663 0 3.015-1.35 3.015-3.015zm-5.273-.005c0-1.252 1.013-2.266 2.265-2.266 1.249 0 2.266 1.014 2.266 2.266 0 1.251-1.017 2.265-2.266 2.265-1.252 0-2.265-1.014-2.265-2.265z"/>
        </svg>
        Steam Store
      </h5>
      <a
        :href="game.steam_url || game.price?.url"
        target="_blank"
        rel="noopener noreferrer"
        class="sdp-store-link"
        aria-label="View on Steam"
      >
        View on Steam <i class="bi bi-box-arrow-up-right ms-1"></i>
      </a>
    </div>

    <!-- Price -->
    <div v-if="game.price?.final === 0" class="sdp-price-block mb-4">
      <span class="sdp-price-free">Free to Play</span>
    </div>
    <div v-else-if="hasPrice" class="sdp-price-block mb-4">
      <div v-if="hasDiscount" class="d-flex align-items-center gap-2 flex-wrap">
        <span class="sdp-discount-badge">
          -{{ game.price.discount_percent }}%
        </span>
        <span class="sdp-price-current">{{ `$${this.game.price.final.toFixed(2)}` }}</span>
        <span class="sdp-price-original">{{ `$${this.game.price.initial.toFixed(2)}` }}</span>
      </div>
      <span v-else class="sdp-price-current">{{ `$${this.game.price.final.toFixed(2)}` }}</span>
      <div class="sdp-price-note">on {{ game.price?.store_name || "Store" }} ({{ game.price?.currency || "USD" }})</div>
    </div>

    <!-- Divider -->
    <div class="sdp-divider mb-3"></div>

    <!-- Categories -->
    <div v-if="topCategories.length" class="mb-3">
      <div class="sdp-label mb-2">
        <i class="bi bi-controller me-1"></i> Categories
      </div>
      <div class="d-flex flex-wrap gap-2">
        <span
          v-for="cat in topCategories"
          :key="cat"
          class="sdp-category-chip"
        >{{ cat }}</span>
      </div>
    </div>

    <!-- Achievements -->
    <div v-if="achievementsTotal > 0" class="sdp-achievement-row mb-3">
      <i class="bi bi-trophy-fill text-warning me-2"></i>
      <span class="sdp-achievement-text">
        <strong>{{ achievementsTotal.toLocaleString() }}</strong> achievements
      </span>
    </div>

    <!-- Languages -->
    <div v-if="topLanguages.length" class="mb-0">
      <div class="sdp-label mb-2">
        <i class="bi bi-translate me-1"></i> Supported Languages
      </div>
      <p class="sdp-langs mb-0">
        {{ topLanguages.join(", ") }}<span v-if="remainingLangsCount > 0" class="text-muted"> +{{ remainingLangsCount }} more</span>
      </p>
    </div>
  </div>
</template>

<style scoped>
.sdp-card {
  background: var(--bg-surface, #1a1a2e);
  border: 1px solid rgba(255, 255, 255, 0.08);
  transition: border-color 0.2s ease;
}
.sdp-card:hover {
  border-color: rgba(102, 161, 255, 0.25);
}

.sdp-heading {
  font-size: 0.95rem;
  font-weight: 700;
  color: var(--text-primary, #e8eaf6);
  letter-spacing: 0.03em;
}

/* Steam icon */
.sdp-steam-icon {
  opacity: 0.85;
  color: #c7d5e0;
  vertical-align: middle;
}

.sdp-store-link {
  font-size: 0.75rem;
  color: #66a1ff;
  text-decoration: none;
  transition: color 0.2s;
}
.sdp-store-link:hover { color: #99c2ff; }

/* Price */
.sdp-price-block { text-align: left; }
.sdp-price-current {
  font-size: 1.4rem;
  font-weight: 800;
  color: #5eff91;
  line-height: 1;
}
.sdp-price-original {
  font-size: 1rem;
  color: var(--text-muted, #9e9e9e);
  text-decoration: line-through;
}
.sdp-price-free {
  font-size: 1.3rem;
  font-weight: 800;
  color: #5eff91;
}
.sdp-price-note {
  font-size: 0.7rem;
  color: var(--text-muted, #9e9e9e);
  margin-top: 4px;
}
.sdp-discount-badge {
  background: #c94040;
  color: #fff;
  font-weight: 700;
  font-size: 0.75rem;
  padding: 3px 8px;
  border-radius: 4px;
}

.sdp-divider {
  border-top: 1px solid rgba(255,255,255,0.08);
}

/* Label */
.sdp-label {
  font-size: 0.72rem;
  font-weight: 700;
  color: var(--text-muted, #9e9e9e);
  text-transform: uppercase;
  letter-spacing: 0.08em;
}

/* Categories */
.sdp-category-chip {
  background: rgba(102, 161, 255, 0.1);
  border: 1px solid rgba(102, 161, 255, 0.2);
  color: #a8c7ff;
  font-size: 0.72rem;
  padding: 3px 10px;
  border-radius: 20px;
  white-space: nowrap;
}

/* Achievements */
.sdp-achievement-row {
  display: flex;
  align-items: center;
}
.sdp-achievement-text {
  font-size: 0.85rem;
  color: var(--text-primary, #e8eaf6);
}

/* Languages */
.sdp-langs {
  font-size: 0.8rem;
  color: var(--text-muted, #9e9e9e);
  line-height: 1.6;
}

/* Skeleton */
.sdp-skeleton-header {
  height: 16px;
  width: 50%;
  background: linear-gradient(90deg, rgba(255,255,255,0.06) 25%, rgba(255,255,255,0.12) 50%, rgba(255,255,255,0.06) 75%);
  background-size: 200% 100%;
  animation: sdp-shimmer 1.4s infinite;
  border-radius: 6px;
}
.sdp-skeleton-line {
  height: 12px;
  background: linear-gradient(90deg, rgba(255,255,255,0.05) 25%, rgba(255,255,255,0.10) 50%, rgba(255,255,255,0.05) 75%);
  background-size: 200% 100%;
  animation: sdp-shimmer 1.4s infinite;
  border-radius: 4px;
}
@keyframes sdp-shimmer {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}
</style>
