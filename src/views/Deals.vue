// src/views/Deals.vue
<script>
import { cheapSharkApi } from '../api'
import SkeletonCard from '../components/SkeletonCard.vue'

// Map CheapShark storeID → store name
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

      // Filters
      sortBy: 'DealRating',
      maxPrice: 20,
      minSavings: 0,
      selectedStore: '',
      searchTerm: '',

      // Pagination
      currentPage: 1,
      itemsPerPage: 12,

      // Store list for filter dropdown
      stores: Object.entries(STORE_NAMES).map(([id, name]) => ({ id, name }))
    }
  },

  computed: {
    filteredDeals() {
      const term = this.searchTerm.toLowerCase()
      return this.deals.filter(deal => {
        const matchesSearch = !term || deal.title.toLowerCase().includes(term)
        const matchesStore = !this.selectedStore || deal.storeID === this.selectedStore
        return matchesSearch && matchesStore
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
    selectedStore() { this.currentPage = 1 }
  },

  methods: {
    storeName(storeID) {
      return STORE_NAMES[storeID] || `Store #${storeID}`
    },

    savingsInt(savings) {
      return Math.round(parseFloat(savings))
    },

    ratingClass(pct) {
      const n = parseInt(pct)
      if (n >= 80) return 'rating-positive'
      if (n >= 60) return 'rating-mixed'
      return 'rating-negative'
    },

    dealUrl(dealID) {
      return `https://www.cheapshark.com/redirect?dealID=${dealID}`
    },

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
          params: {
            sortBy: this.sortBy,
            upperPrice: this.maxPrice,
            lowerPrice: 0,
            pageSize: 60,
            onSale: 1
          }
        })
        this.deals = data.filter(d => this.savingsInt(d.savings) >= this.minSavings)
        this.currentPage = 1
      } catch (err) {
        console.error(err)
        this.error = 'Failed to load deals. Please try again later.'
      } finally {
        this.loading = false
      }
    }
  },

  async mounted() {
    await this.fetchDeals()
  }
}
</script>

<template>
  <div class="container py-4">

    <!-- Header -->
    <div class="section-header">
      <span class="section-icon">💰</span>
      <h1 class="mb-0">Game Deals</h1>
    </div>
    <p class="text-muted mb-4">
      Live discounts on PC games across Steam, Epic, GOG &amp; more.
      <span style="opacity: 0.6;">(Powered by CheapShark)</span>
    </p>

    <!-- Filters -->
    <div class="deals-filters card mb-4">
      <div class="card-body">
        <div class="row g-3 align-items-end">

          <!-- Search -->
          <div class="col-md-4">
            <label class="form-label text-muted" style="font-size:0.8rem;">Search</label>
            <input
              v-model="searchTerm"
              type="text"
              class="form-control"
              placeholder="🔍 Search deals..."
            >
          </div>

          <!-- Sort -->
          <div class="col-md-2">
            <label class="form-label text-muted" style="font-size:0.8rem;">Sort By</label>
            <select v-model="sortBy" class="form-select" @change="fetchDeals">
              <option value="DealRating">Best Rating</option>
              <option value="Savings">Most Savings</option>
              <option value="Price">Lowest Price</option>
              <option value="Metacritic">Metacritic</option>
              <option value="Reviews">Steam Reviews</option>
              <option value="Recent">Most Recent</option>
            </select>
          </div>

          <!-- Max Price -->
          <div class="col-md-3">
            <label class="form-label text-muted" style="font-size:0.8rem;">
              Max Price: <strong style="color:var(--accent-primary);">${{ maxPrice === 60 ? '60+' : maxPrice }}</strong>
            </label>
            <input
              v-model.number="maxPrice"
              type="range"
              class="form-range"
              min="0" max="60" step="5"
              @change="fetchDeals"
            >
          </div>

          <!-- Min Savings -->
          <div class="col-md-2">
            <label class="form-label text-muted" style="font-size:0.8rem;">
              Min Savings: <strong style="color:#4ade80;">{{ minSavings }}%</strong>
            </label>
            <input
              v-model.number="minSavings"
              type="range"
              class="form-range"
              min="0" max="90" step="10"
            >
          </div>

          <!-- Store Filter -->
          <div class="col-md-1">
            <label class="form-label text-muted" style="font-size:0.8rem;">Store</label>
            <select v-model="selectedStore" class="form-select">
              <option value="">All</option>
              <option v-for="s in stores" :key="s.id" :value="s.id">{{ s.name }}</option>
            </select>
          </div>

        </div>
      </div>
    </div>

    <!-- Stats bar -->
    <div class="d-flex align-items-center gap-3 mb-3 flex-wrap" v-if="!loading">
      <span class="badge" style="background: var(--gradient-primary);">
        {{ filteredDeals.length }} deals found
      </span>
      <span class="text-muted" style="font-size:0.82rem;">
        Page {{ currentPage }} of {{ computedTotalPages }}
      </span>
    </div>

    <!-- Skeleton Loading -->
    <div v-if="loading" class="row">
      <div class="col-md-4 mb-4" v-for="n in 12" :key="n">
        <SkeletonCard />
      </div>
    </div>

    <!-- Error -->
    <div v-else-if="error" class="alert alert-danger">{{ error }}</div>

    <!-- Empty -->
    <div v-else-if="filteredDeals.length === 0" class="empty-state">
      <div class="empty-state-icon">💸</div>
      <h3>No deals found</h3>
      <p>Try adjusting the filters or increasing the max price.</p>
    </div>

    <!-- Deals Grid -->
    <div v-else class="row">
      <div
        class="col-md-4 mb-4"
        v-for="(deal, index) in paginatedDeals"
        :key="deal.dealID"
      >
        <div
          class="card h-100 deal-card stagger-item"
          :style="{ animationDelay: `${(index % 12) * 0.04}s` }"
        >
          <!-- Thumbnail -->
          <div style="position:relative; overflow:hidden;">
            <img
              v-if="deal.thumb"
              :src="deal.thumb"
              :alt="deal.title"
              class="card-img-top"
              style="height:160px; object-fit:cover;"
              loading="lazy"
            >
            <div
              v-else
              class="d-flex align-items-center justify-content-center"
              style="height:160px; background:var(--bg-glass);"
            >
              <span style="font-size:2rem;">🎮</span>
            </div>

            <!-- Savings badge -->
            <div class="deal-savings-badge">
              -{{ savingsInt(deal.savings) }}%
            </div>

            <!-- Store badge -->
            <span
              class="badge"
              style="position:absolute; bottom:8px; left:8px; background:rgba(0,0,0,0.7); font-size:0.7rem;"
            >
              {{ storeName(deal.storeID) }}
            </span>
          </div>

          <div class="card-body d-flex flex-column">

            <h6 class="card-title mb-2" style="font-size:0.9rem; line-height:1.35;">
              {{ deal.title }}
            </h6>

            <!-- Price row -->
            <div class="d-flex align-items-center gap-2 mb-2">
              <span class="deal-original-price">${{ deal.normalPrice }}</span>
              <span class="deal-sale-price">${{ deal.salePrice }}</span>
              <span v-if="deal.salePrice === '0.00'" class="badge bg-success ms-auto">FREE</span>
            </div>

            <!-- Ratings -->
            <div class="d-flex gap-2 flex-wrap mb-3">
              <span
                v-if="deal.metacriticScore && deal.metacriticScore !== '0'"
                class="badge"
                :class="parseInt(deal.metacriticScore) >= 75 ? 'bg-success' : parseInt(deal.metacriticScore) >= 50 ? 'bg-warning text-dark' : 'bg-danger'"
                style="font-size:0.72rem;"
              >
                MC {{ deal.metacriticScore }}
              </span>

              <span
                v-if="deal.steamRatingText"
                class="deal-steam-rating"
                :class="ratingClass(deal.steamRatingPercent)"
                style="font-size:0.72rem;"
              >
                ★ {{ deal.steamRatingText }} ({{ deal.steamRatingPercent }}%)
              </span>
            </div>

            <!-- CTA -->
            <a
              :href="dealUrl(deal.dealID)"
              target="_blank"
              rel="noopener noreferrer"
              class="btn btn-primary btn-sm mt-auto"
            >
              Get Deal →
            </a>

          </div>
        </div>
      </div>
    </div>

    <!-- Pagination -->
    <nav v-if="!loading && computedTotalPages > 1">
      <ul class="pagination justify-content-center">
        <li class="page-item" :class="{ disabled: currentPage === 1 }">
          <button class="page-link" @click="goToPage(currentPage - 1)">← Previous</button>
        </li>
        <li
          v-for="(page, i) in visiblePages"
          :key="i"
          class="page-item"
          :class="{ active: currentPage === page }"
        >
          <span v-if="page === '...'" class="page-link">...</span>
          <button v-else class="page-link" @click="goToPage(page)">{{ page }}</button>
        </li>
        <li class="page-item" :class="{ disabled: currentPage === computedTotalPages }">
          <button class="page-link" @click="goToPage(currentPage + 1)">Next →</button>
        </li>
      </ul>
    </nav>

  </div>
</template>

<style scoped>
.deal-card {
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}
.deal-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 40px rgba(0,0,0,0.35);
}

.deal-savings-badge {
  position: absolute;
  top: 10px;
  right: 10px;
  background: linear-gradient(135deg, #16a34a, #15803d);
  color: #fff;
  font-weight: 700;
  font-size: 0.85rem;
  padding: 4px 10px;
  border-radius: 20px;
  letter-spacing: 0.5px;
  box-shadow: 0 2px 8px rgba(22,163,74,0.5);
}

.deal-original-price {
  text-decoration: line-through;
  color: var(--text-muted, #888);
  font-size: 0.85rem;
}

.deal-sale-price {
  font-weight: 700;
  font-size: 1.1rem;
  color: #4ade80;
}

.deal-steam-rating {
  border-radius: 4px;
  padding: 2px 8px;
  font-weight: 600;
}
.rating-positive { background: rgba(34,197,94,0.15); color: #86efac; }
.rating-mixed    { background: rgba(234,179,8,0.15);  color: #fde047; }
.rating-negative { background: rgba(239,68,68,0.15);  color: #fca5a5; }

.deals-filters {
  border: 1px solid var(--border-glass, rgba(255,255,255,0.1));
}
</style>
