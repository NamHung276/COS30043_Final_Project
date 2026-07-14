// src/views/Deals.vue
<script>
import { cheapSharkApi } from '../services/api'
import SkeletonCard from '../components/SkeletonCard.vue'

const STORE_NAMES = {
  1: 'Steam', 2: 'GamersGate', 3: 'GreenManGaming', 7: 'GOG',
  8: 'Origin', 11: 'Humble Store', 13: 'Uplay', 15: 'Fanatical',
  21: 'WinGameStore', 23: 'GameBillet', 24: 'Voidu', 25: 'Epic Games',
  27: 'Games Planet', 28: 'Games Tradera', 29: 'Games Republic',
  30: 'Silagrastore', 31: 'Allyouplay', 32: 'DLGamer',
  33: 'Noctre', 34: 'DreamGame'
}

export default {
  components: { SkeletonCard },

  data() {
    return {
      deals: [],
      loading: true,
      error: null,
      sortBy: 'DealRating',
      maxPrice: 20,
      minSavings: 0,
      selectedStore: '',
      searchTerm: '',
      currentPage: 1,
      itemsPerPage: 12,
      stores: Object.entries(STORE_NAMES).map(([id, name]) => ({ id, name }))
    }
  },

  computed: {
    filteredDeals() {
      const term = this.searchTerm.toLowerCase()
      return this.deals.filter(deal => {
        const matchesSearch = !term || deal.title.toLowerCase().includes(term)
        const matchesStore = !this.selectedStore || deal.storeID === this.selectedStore
        const matchesSavings = this.savingsInt(deal.savings) >= this.minSavings
        return matchesSearch && matchesStore && matchesSavings
      })
    },
    paginatedDeals() {
      const start = (this.currentPage - 1) * this.itemsPerPage
      return this.filteredDeals.slice(start, start + this.itemsPerPage)
    },
    computedTotalPages() {
      return Math.ceil(this.filteredDeals.length / this.itemsPerPage)
    },
    visiblePages() {
      const total = this.computedTotalPages
      const pages = []
      if (total <= 7) {
        for (let i = 1; i <= total; i++) pages.push(i)
      } else {
        pages.push(1)
        if (this.currentPage > 4) pages.push('...')
        const start = Math.max(2, this.currentPage - 1)
        const end = Math.min(total - 1, this.currentPage + 1)
        for (let i = start; i <= end; i++) pages.push(i)
        if (this.currentPage < total - 3) pages.push('...')
        pages.push(total)
      }
      return pages
    }
  },

  watch: {
    searchTerm() { this.currentPage = 1 },
    selectedStore() { this.currentPage = 1 },
    minSavings() { this.currentPage = 1 }
  },

  methods: {
    storeName(storeID) { return STORE_NAMES[storeID] || `Store #${storeID}` },
    savingsInt(savings) { return Math.round(parseFloat(savings)) },
    ratingClass(pct) {
      const n = parseInt(pct)
      if (n >= 80) return 'rating-positive'
      if (n >= 60) return 'rating-mixed'
      return 'rating-negative'
    },
    dealUrl(dealID) { return `https://www.cheapshark.com/redirect?dealID=${dealID}` },
    goToPage(page) {
      if (page >= 1 && page <= this.computedTotalPages) {
        this.currentPage = page
        window.scrollTo({ top: 0, behavior: 'smooth' })
      }
    },
    async fetchDeals() {
      this.loading = true
      this.error = null
      try {
        const { data } = await cheapSharkApi.get('/deals', {
          params: { sortBy: this.sortBy, upperPrice: this.maxPrice, lowerPrice: 0, pageSize: 60, onSale: 1 }
        })
        this.deals = data
        this.currentPage = 1
      } catch (err) {
        console.error(err)
        this.error = 'Failed to load deals. Please try again later.'
      } finally {
        this.loading = false
      }
    }
  },

  async mounted() { await this.fetchDeals() }
}
</script>

<template>
  <div class="deals-page">

    <!-- ══ Page Header ══ -->
    <div class="deals-page-header">
      <div class="deals-header-bg" aria-hidden="true"></div>
      <div class="container deals-header-content">

        <div class="deals-title-row">
          <span class="deals-title-icon" aria-hidden="true">
            <svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"/></svg>
          </span>
          <div>
            <h1 class="deals-title">Game Deals</h1>
            <p class="deals-subtitle">
              Live discounts on PC games across Steam, Epic, GOG &amp; more
              <span class="deals-powered">· Powered by CheapShark</span>
            </p>
          </div>
        </div>

        <!-- ══ Filter Panel ══ -->
        <div class="deals-filter-panel">

          <!-- Row 1: Search + Sort + Store -->
          <div class="deals-filter-row">
            <!-- Search -->
            <div class="deals-search-wrap">
              <img src="/logo/search.svg" class="deals-search-icon" width="16" height="16" alt="" aria-hidden="true">
              <input
                v-model="searchTerm"
                type="text"
                class="deals-input"
                placeholder="Search deals…"
                aria-label="Search deals"
              >
            </div>

            <!-- Sort -->
            <div class="deals-select-group">
              <label class="deals-filter-label" for="deals-sort">Sort By</label>
              <select id="deals-sort" v-model="sortBy" class="deals-select" @change="fetchDeals" aria-label="Sort deals">
                <option value="DealRating">Best Rating</option>
                <option value="Savings">Most Savings</option>
                <option value="Price">Lowest Price</option>
                <option value="Metacritic">Metacritic</option>
                <option value="Reviews">Steam Reviews</option>
                <option value="Recent">Most Recent</option>
              </select>
            </div>

            <!-- Store -->
            <div class="deals-select-group">
              <label class="deals-filter-label" for="deals-store">Store</label>
              <select id="deals-store" v-model="selectedStore" class="deals-select" aria-label="Filter by store">
                <option value="">All Stores</option>
                <option v-for="s in stores" :key="s.id" :value="s.id">{{ s.name }}</option>
              </select>
            </div>
          </div>

          <!-- Row 2: Price slider + Savings slider -->
          <div class="deals-filter-row deals-sliders-row">
            <div class="deals-slider-group">
              <label class="deals-filter-label">
                Max Price: <strong class="deals-slider-val deals-slider-val-price">${{ maxPrice }}</strong>
              </label>
              <div class="deals-slider-track">
                <input v-model.number="maxPrice" type="range" class="deals-range" min="0" max="60" step="5" @change="fetchDeals" aria-label="Maximum price filter">
                <div class="deals-range-fill" :style="{ width: (maxPrice / 60 * 100) + '%' }"></div>
              </div>
            </div>

            <div class="deals-slider-group">
              <label class="deals-filter-label">
                Min Savings: <strong class="deals-slider-val deals-slider-val-savings">{{ minSavings }}%</strong>
              </label>
              <div class="deals-slider-track">
                <input v-model.number="minSavings" type="range" class="deals-range deals-range-green" min="0" max="90" step="10" aria-label="Minimum savings percentage filter">
                <div class="deals-range-fill deals-range-fill-green" :style="{ width: (minSavings / 90 * 100) + '%' }"></div>
              </div>
            </div>
          </div>
        </div>

        <!-- Summary row -->
        <div class="deals-summary-row">
          <span class="deals-summary-text">{{ filteredDeals.length }} deals · Page {{ currentPage }} of {{ computedTotalPages || 1 }}</span>
          <span v-if="!loading" class="deals-results-badge">{{ filteredDeals.length }} results</span>
        </div>
      </div>
    </div>

    <!-- ══ Content ══ -->
    <div class="container deals-content">

      <!-- Skeleton -->
      <div v-if="loading" class="deals-grid">
        <SkeletonCard v-for="n in 12" :key="n" />
      </div>

      <!-- Error -->
      <div v-else-if="error" class="deals-state">
        <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" aria-hidden="true"><circle cx="12" cy="12" r="10"/><path d="M12 8v4m0 4h.01"/></svg>
        <h3>Failed to load deals</h3>
        <p>{{ error }}</p>
        <button class="deals-primary-btn" @click="fetchDeals">Try Again</button>
      </div>

      <!-- Empty -->
      <div v-else-if="filteredDeals.length === 0" class="deals-state">
        <svg width="56" height="56" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.2" aria-hidden="true" style="opacity:0.3"><path d="M20 12V22H4V12"/><path d="M22 7H2v5h20V7z"/><path d="M12 22V7"/><path d="M12 7H7.5a2.5 2.5 0 010-5C11 2 12 7 12 7z"/><path d="M12 7h4.5a2.5 2.5 0 000-5C13 2 12 7 12 7z"/></svg>
        <h3>No deals found</h3>
        <p>Try adjusting the max price or min savings slider.</p>
      </div>

      <!-- Deals Grid -->
      <div v-else class="deals-grid">
        <a
          v-for="(deal, index) in paginatedDeals"
          :key="deal.dealID"
          :href="dealUrl(deal.dealID)"
          target="_blank"
          rel="noopener noreferrer"
          class="deal-card stagger-item"
          :style="{ animationDelay: `${(index % 12) * 0.04}s` }"
          :aria-label="`Get deal for ${deal.title}`"
        >
          <!-- Image -->
          <div class="deal-card-img-wrap">
            <img
              v-if="deal.thumb"
              :src="deal.thumb"
              :alt="deal.title"
              class="deal-card-img"
              loading="lazy"
            >
            <div v-else class="deal-card-img-placeholder" aria-hidden="true">
              <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" aria-hidden="true"><path d="M21 16V8a2 2 0 00-1-1.73l-7-4a2 2 0 00-2 0l-7 4A2 2 0 003 8v8a2 2 0 001 1.73l7 4a2 2 0 002 0l7-4A2 2 0 0021 16z"/></svg>
            </div>
            <div class="deal-card-img-overlay" aria-hidden="true"></div>

            <!-- Savings badge -->
            <span class="deal-savings-badge">-{{ savingsInt(deal.savings) }}%</span>

            <!-- Store badge -->
            <span class="deal-store-badge">{{ storeName(deal.storeID) }}</span>

            <!-- FREE label -->
            <span v-if="deal.salePrice === '0.00'" class="deal-free-badge">FREE</span>
          </div>

          <!-- Body -->
          <div class="deal-card-body">
            <h3 class="deal-card-title">{{ deal.title }}</h3>

            <!-- Price -->
            <div class="deal-price-row">
              <span class="deal-original">${{ deal.normalPrice }}</span>
              <span class="deal-sale" :class="{ 'deal-sale-free': deal.salePrice === '0.00' }">
                {{ deal.salePrice === '0.00' ? 'FREE' : `$${deal.salePrice}` }}
              </span>
            </div>

            <!-- Ratings -->
            <div class="deal-ratings-row">
              <span
                v-if="deal.metacriticScore && deal.metacriticScore !== '0'"
                class="deal-mc-badge"
                :class="parseInt(deal.metacriticScore) >= 75 ? 'mc-green' : parseInt(deal.metacriticScore) >= 50 ? 'mc-yellow' : 'mc-red'"
              >
                MC {{ deal.metacriticScore }}
              </span>
              <span
                v-if="deal.steamRatingText"
                class="deal-steam-rating"
                :class="ratingClass(deal.steamRatingPercent)"
              >
                ★ {{ deal.steamRatingText }} ({{ deal.steamRatingPercent }}%)
              </span>
            </div>

            <!-- CTA -->
            <div class="deal-cta">
              <span class="deal-cta-text">Get Deal</span>
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" aria-hidden="true"><path d="M5 12h14M12 5l7 7-7 7"/></svg>
            </div>
          </div>
        </a>
      </div>

      <!-- Pagination -->
      <nav v-if="!loading && computedTotalPages > 1" class="deals-pagination" aria-label="Deals pagination">
        <button class="deals-page-btn" :disabled="currentPage === 1" @click="goToPage(currentPage - 1)">
          <img src="/logo/arrow-left.svg" width="15" height="15" alt="" aria-hidden="true">
          Previous
        </button>
        <div class="deals-page-numbers">
          <template v-for="(page, i) in visiblePages" :key="i">
            <span v-if="page === '...'" class="deals-page-ellipsis">&#8230;</span>
            <button v-else class="deals-page-num" :class="{ active: currentPage === page }" @click="goToPage(page)">{{ page }}</button>
          </template>
        </div>
        <button class="deals-page-btn" :disabled="currentPage === computedTotalPages" @click="goToPage(currentPage + 1)">
          Next
          <img src="/logo/arrow-right.svg" width="15" height="15" alt="" aria-hidden="true">
        </button>
      </nav>

    </div>
  </div>
</template>

<style scoped>
/* ── Page ─────────────────────────────────── */
.deals-page { min-height: 100vh; background: var(--bg-deep); }

/* ── Header ───────────────────────────────── */
.deals-page-header {
  position: relative;
  background: var(--bg-base);
  border-bottom: 1px solid var(--border-glass);
  overflow: hidden;
}
.deals-header-bg {
  position: absolute; inset: 0;
  background:
    radial-gradient(ellipse 65% 120% at 90% 50%, rgba(234,179,8,0.06) 0%, transparent 60%),
    radial-gradient(ellipse 50% 80% at 10% 80%, rgba(124,58,237,0.07) 0%, transparent 60%);
  pointer-events: none;
}
.deals-header-content { position: relative; z-index: 1; padding-top: 40px; padding-bottom: 0; }

/* Title row */
.deals-title-row { display: flex; align-items: center; gap: 18px; margin-bottom: 20px; }
.deals-title-icon {
  display: flex; align-items: center; justify-content: center;
  width: 54px; height: 54px; border-radius: 16px;
  background: linear-gradient(135deg, #b45309, #f59e0b);
  color: #fff;
  flex-shrink: 0;
  box-shadow: 0 4px 20px rgba(245,158,11,0.4);
}
.deals-title { font-size: 2.1rem; font-weight: 800; color: var(--text-primary) !important; margin: 0 0 4px; line-height: 1; }
.deals-subtitle { font-size: 0.85rem; color: #8b9cc8 !important; margin: 0; }
.deals-powered { opacity: 0.55; }

/* ── Filter Panel ─────────────────────────── */
.deals-filter-panel {
  background: rgba(15,23,42,0.6);
  border: 1px solid var(--border-glass);
  border-bottom: none;
  border-radius: 14px 14px 0 0;
  padding: 20px 24px 16px;
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
}
.deals-filter-row { display: flex; align-items: flex-end; gap: 14px; flex-wrap: wrap; margin-bottom: 16px; }
.deals-filter-row:last-child { margin-bottom: 0; }
.deals-filter-label { display: block; font-size: 0.72rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.6px; color: #6b7fa8 !important; margin-bottom: 6px; }

/* Search */
.deals-search-wrap { flex: 1; min-width: 200px; position: relative; }
.deals-search-icon { position: absolute; left: 13px; top: 50%; transform: translateY(-50%); pointer-events: none; opacity: 0.6; }
.deals-input {
  width: 100%; background: rgba(15,23,42,0.7); border: 1px solid var(--border-glass);
  border-radius: var(--radius-sm); color: var(--text-primary) !important; padding: 10px 14px 10px 38px;
  font-size: 0.88rem; font-family: var(--font-family); outline: none; transition: border-color 0.2s;
}
.deals-input::placeholder { color: #4a5580; }
.deals-input:focus { border-color: var(--primary-light); }

/* Select groups */
.deals-select-group { display: flex; flex-direction: column; }
.deals-select {
  background: rgba(15,23,42,0.7); border: 1px solid var(--border-glass);
  border-radius: var(--radius-sm); color: var(--text-primary) !important; padding: 9px 14px;
  font-size: 0.88rem; font-family: var(--font-family); outline: none; cursor: pointer; min-width: 140px;
}
.deals-select:focus { border-color: var(--primary-light); }

/* Sliders */
.deals-sliders-row { align-items: flex-start; }
.deals-slider-group { flex: 1; min-width: 200px; }
.deals-slider-val { font-size: 0.88rem; }
.deals-slider-val-price { color: #a78bfa !important; }
.deals-slider-val-savings { color: #4ade80 !important; }
.deals-slider-track { position: relative; padding-bottom: 8px; }
.deals-range {
  width: 100%; -webkit-appearance: none; appearance: none;
  height: 4px; border-radius: 2px; background: rgba(255,255,255,0.1);
  outline: none; cursor: pointer; position: relative; z-index: 2;
}
.deals-range::-webkit-slider-thumb {
  -webkit-appearance: none; appearance: none;
  width: 16px; height: 16px; border-radius: 50%;
  background: #7c3aed; cursor: pointer;
  box-shadow: 0 0 0 3px rgba(124,58,237,0.25);
  transition: box-shadow 0.2s;
}
.deals-range::-webkit-slider-thumb:hover { box-shadow: 0 0 0 5px rgba(124,58,237,0.3); }
.deals-range-green::-webkit-slider-thumb { background: #16a34a; box-shadow: 0 0 0 3px rgba(22,163,74,0.25); }
.deals-range-green::-webkit-slider-thumb:hover { box-shadow: 0 0 0 5px rgba(22,163,74,0.3); }
.deals-range-fill { position: absolute; top: 0; left: 0; height: 4px; border-radius: 2px; background: var(--gradient-primary); pointer-events: none; }
.deals-range-fill-green { background: linear-gradient(90deg, #16a34a, #4ade80); }

/* Summary row */
.deals-summary-row {
  display: flex; align-items: center; justify-content: space-between; padding: 10px 24px;
  background: rgba(15,23,42,0.4); border: 1px solid var(--border-glass); border-top: none;
}
.deals-summary-text { font-size: 0.78rem; color: #4a5580 !important; font-style: italic; }
.deals-results-badge {
  font-size: 0.72rem; font-weight: 700; padding: 3px 12px; border-radius: 20px;
  background: linear-gradient(135deg, #b45309, #f59e0b); color: #fff !important;
}

/* ── Content ──────────────────────────────── */
.deals-content { padding-top: 28px; padding-bottom: 60px; }

/* ── Grid ─────────────────────────────────── */
.deals-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 22px; }

/* ── Deal Card ────────────────────────────── */
.deal-card {
  display: flex; flex-direction: column;
  background: rgba(15,23,42,0.55); border: 1px solid rgba(255,255,255,0.07);
  border-radius: 14px; overflow: hidden; text-decoration: none;
  transition: transform 0.25s ease, box-shadow 0.25s ease, border-color 0.25s ease;
  backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px);
}
.deal-card:hover {
  transform: translateY(-6px) scale(1.01);
  box-shadow: 0 16px 48px rgba(245,158,11,0.15), 0 4px 20px rgba(0,0,0,0.4);
  border-color: rgba(245,158,11,0.3);
}

/* Image */
.deal-card-img-wrap { position: relative; overflow: hidden; height: 175px; flex-shrink: 0; }
.deal-card-img { width: 100%; height: 100%; object-fit: cover; display: block; transition: transform 0.35s ease; }
.deal-card:hover .deal-card-img { transform: scale(1.06); }
.deal-card-img-placeholder {
  width: 100%; height: 100%; display: flex; align-items: center; justify-content: center;
  background: rgba(15,23,42,0.8); color: rgba(255,255,255,0.2);
}
.deal-card-img-overlay {
  position: absolute; inset: 0;
  background: linear-gradient(to top, rgba(10,15,30,0.8) 0%, transparent 55%);
  pointer-events: none;
}

/* Savings badge */
.deal-savings-badge {
  position: absolute; top: 10px; right: 10px;
  background: linear-gradient(135deg, #15803d, #4ade80);
  color: #fff !important; font-weight: 800; font-size: 0.78rem;
  padding: 4px 10px; border-radius: 20px; letter-spacing: 0.5px;
  box-shadow: 0 2px 10px rgba(74,222,128,0.5);
}
/* Store badge */
.deal-store-badge {
  position: absolute; bottom: 10px; left: 10px;
  background: rgba(5,10,25,0.75); border: 1px solid rgba(255,255,255,0.1);
  backdrop-filter: blur(6px); color: rgba(255,255,255,0.85) !important;
  font-size: 0.67rem; font-weight: 600; padding: 3px 8px; border-radius: 20px;
}
/* FREE badge */
.deal-free-badge {
  position: absolute; top: 10px; left: 10px;
  background: linear-gradient(135deg, #059669, #10b981);
  color: #fff !important; font-weight: 800; font-size: 0.67rem;
  padding: 3px 10px; border-radius: 20px; letter-spacing: 1px;
  box-shadow: 0 2px 10px rgba(16,185,129,0.5);
}

/* Card body */
.deal-card-body { padding: 14px 16px 16px; display: flex; flex-direction: column; flex: 1; gap: 8px; }
.deal-card-title {
  font-size: 0.95rem; font-weight: 700; color: var(--text-primary) !important; margin: 0;
  line-height: 1.4; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden;
}

/* Price */
.deal-price-row { display: flex; align-items: center; gap: 10px; }
.deal-original { text-decoration: line-through; color: #4a5580 !important; font-size: 0.83rem; }
.deal-sale { font-weight: 800; font-size: 1.2rem; color: #4ade80 !important; }
.deal-sale-free { color: #34d399 !important; }

/* Ratings */
.deal-ratings-row { display: flex; flex-wrap: wrap; gap: 6px; min-height: 22px; }
.deal-mc-badge {
  font-size: 0.68rem; font-weight: 800; padding: 2px 8px;
  border-radius: 4px; letter-spacing: 0.3px;
}
.mc-green  { background: #15803d !important; color: #fff !important; }
.mc-yellow { background: #a16207 !important; color: #fff !important; }
.mc-red    { background: #b91c1c !important; color: #fff !important; }
.deal-steam-rating {
  font-size: 0.69rem; font-weight: 600; padding: 2px 8px; border-radius: 4px;
}
.rating-positive { background: rgba(34,197,94,0.15); color: #86efac !important; }
.rating-mixed    { background: rgba(234,179,8,0.15);  color: #fde047 !important; }
.rating-negative { background: rgba(239,68,68,0.15);  color: #fca5a5 !important; }

/* CTA */
.deal-cta {
  display: inline-flex; align-items: center; gap: 6px; margin-top: auto;
  font-size: 0.8rem; font-weight: 700; color: #8b9cc8 !important; transition: color 0.2s;
}
.deal-card:hover .deal-cta { color: #fbbf24 !important; }

/* ── State (empty/error) ──────────────────── */
.deals-state {
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  text-align: center; min-height: 280px; gap: 12px; color: #6b7fa8 !important;
}
.deals-state h3 { color: var(--text-primary) !important; font-size: 1.2rem; margin: 0; }
.deals-state p { color: #6b7fa8 !important; font-size: 0.88rem; margin: 0; }
.deals-primary-btn {
  margin-top: 8px; padding: 10px 24px; border-radius: 30px; border: none;
  background: var(--gradient-primary); color: #fff !important; font-size: 0.88rem;
  font-weight: 700; font-family: var(--font-family); cursor: pointer; transition: opacity 0.2s;
}
.deals-primary-btn:hover { opacity: 0.85; }

/* ── Pagination ───────────────────────────── */
.deals-pagination {
  display: flex; align-items: center; justify-content: center;
  gap: 8px; padding: 32px 0 8px; flex-wrap: wrap;
}
.deals-page-btn {
  display: inline-flex; align-items: center; gap: 6px; padding: 9px 18px;
  border-radius: 8px; border: 1px solid var(--border-glass);
  background: rgba(15,23,42,0.6); color: #8b9cc8 !important;
  font-size: 0.83rem; font-weight: 600; font-family: var(--font-family); cursor: pointer; transition: all 0.2s;
}
.deals-page-btn:disabled { opacity: 0.35; cursor: not-allowed; }
.deals-page-btn:not(:disabled):hover { border-color: rgba(245,158,11,0.4); color: #fbbf24 !important; }
.deals-page-numbers { display: flex; align-items: center; gap: 4px; }
.deals-page-num {
  width: 36px; height: 36px; border-radius: 8px; border: 1px solid var(--border-glass);
  background: rgba(15,23,42,0.5); color: #8b9cc8 !important;
  font-size: 0.83rem; font-weight: 600; font-family: var(--font-family); cursor: pointer; transition: all 0.18s;
}
.deals-page-num:hover { border-color: rgba(245,158,11,0.35); color: #fbbf24 !important; }
.deals-page-num.active {
  background: linear-gradient(135deg, #b45309, #f59e0b);
  border-color: transparent; color: #fff !important;
  box-shadow: 0 2px 12px rgba(245,158,11,0.4);
}
.deals-page-ellipsis { color: #4a5580 !important; padding: 0 4px; font-size: 0.88rem; }
</style>
