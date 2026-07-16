<script>
import { cheapSharkApi } from "../services/api";
import SkeletonCard from "../components/SkeletonCard.vue";
import { inject } from "vue";
import { auth, db } from "../firebase";
import { onAuthStateChanged } from "firebase/auth";
import { collection, query, where, getDocs, addDoc } from "firebase/firestore";

const STORE_NAMES = {
  1: "Steam",
  2: "GamersGate",
  3: "GreenManGaming",
  7: "GOG",
  8: "Origin",
  11: "Humble Store",
  13: "Uplay",
  15: "Fanatical",
  21: "WinGameStore",
  23: "GameBillet",
  24: "Voidu",
  25: "Epic Games",
  27: "Games Planet",
  28: "Games Tradera",
  29: "Games Republic",
  30: "Silagrastore",
  31: "Allyouplay",
  32: "DLGamer",
  33: "Noctre",
  34: "DreamGame",
};

export default {
  components: { SkeletonCard },
  setup() {
    const toast = inject("toast");
    return { toast };
  },

  data() {
    return {
      deals: [],
      loading: true,
      error: null,
      sortBy: "DealRating",
      viewMode: "grid",
      maxPrice: 20,
      minSavings: 0,
      selectedStore: "",
      searchTerm: "",
      searchTerm: "",
      currentPage: 1,
      itemsPerPage: 12,
      stores: Object.entries(STORE_NAMES).map(([id, name]) => ({ id, name })),
      // Auth / Wishlist
      currentUser: null,
      wishlisted: new Set(),
    };
  },

  computed: {
    filteredDeals() {
      const term = this.searchTerm.toLowerCase();
      return this.deals.filter((deal) => {
        const matchesSearch = !term || deal.title.toLowerCase().includes(term);
        const matchesStore =
          !this.selectedStore || deal.storeID === this.selectedStore;
        const matchesSavings = this.savingsInt(deal.savings) >= this.minSavings;
        return matchesSearch && matchesStore && matchesSavings;
      });
    },
    paginatedDeals() {
      const start = (this.currentPage - 1) * this.itemsPerPage;
      return this.filteredDeals.slice(start, start + this.itemsPerPage);
    },
    computedTotalPages() {
      return Math.ceil(this.filteredDeals.length / this.itemsPerPage);
    },
    visiblePages() {
      const total = this.computedTotalPages;
      const pages = [];
      if (total <= 7) {
        for (let i = 1; i <= total; i++) pages.push(i);
      } else {
        pages.push(1);
        if (this.currentPage > 4) pages.push("...");
        const start = Math.max(2, this.currentPage - 1);
        const end = Math.min(total - 1, this.currentPage + 1);
        for (let i = start; i <= end; i++) pages.push(i);
        if (this.currentPage < total - 3) pages.push("...");
        pages.push(total);
      }
      return pages;
    },
  },

  watch: {
    searchTerm() {
      this.currentPage = 1;
    },
    selectedStore() {
      this.currentPage = 1;
    },
    minSavings() {
      this.currentPage = 1;
    },
  },

  methods: {
    storeName(storeID) {
      return STORE_NAMES[storeID] || `Store #${storeID}`;
    },
    savingsInt(savings) {
      return Math.round(parseFloat(savings));
    },
    ratingClass(pct) {
      const n = parseInt(pct);
      if (n >= 80) return "rating-positive";
      if (n >= 60) return "rating-mixed";
      return "rating-negative";
    },
    ratingStars(pct) {
      const p = parseInt(pct) || 0;
      const stars = [];
      const rating = p / 20; // 100% = 5 stars
      for (let i = 1; i <= 5; i++) {
        if (rating >= i) stars.push("full");
        else if (rating >= i - 0.5) stars.push("half");
        else stars.push("empty");
      }
      return stars;
    },
    dealUrl(dealID) {
      return `https://www.cheapshark.com/redirect?dealID=${dealID}`;
    },
    async addToWishlist(deal, e) {
      e.preventDefault();
      e.stopPropagation();
      if (!this.currentUser) {
        this.toast?.show("Please log in", "warning");
        this.$router.push("/login");
        return;
      }
      // Deal items use deal.gameID instead of RAWG id
      const id = String(deal.gameID || deal.dealID);
      if (this.wishlisted.has(id)) {
        this.toast?.show("Already in wishlist!", "info");
        return;
      }
      try {
        const snap = await getDocs(
          query(
            collection(db, "favorites"),
            where("userId", "==", this.currentUser.uid),
            where("gameId", "==", deal.gameID),
          ),
        );
        if (!snap.empty) {
          this.wishlisted.add(id);
          return;
        }
        await addDoc(collection(db, "favorites"), {
          userId: this.currentUser.uid,
          gameId: deal.gameID,
          title: deal.title,
          thumbnail: deal.thumb,
          genre: "Deal",
          priority: "Interested",
          addedAt: new Date().toISOString(),
        });
        this.wishlisted.add(id);
        this.toast?.show(`♥ "${deal.title}" added to wishlist`, "success");
      } catch {
        this.toast?.show("Failed to add to wishlist", "error");
      }
    },
    async loadWishlist() {
      if (!this.currentUser) return;
      try {
        const snap = await getDocs(
          query(
            collection(db, "favorites"),
            where("userId", "==", this.currentUser.uid),
          ),
        );
        snap.forEach((d) => this.wishlisted.add(String(d.data().gameId)));
      } catch {}
    },
    goToPage(page) {
      if (page >= 1 && page <= this.computedTotalPages) {
        this.currentPage = page;
        window.scrollTo({ top: 0, behavior: "smooth" });
      }
    },
    async fetchDeals() {
      this.loading = true;
      this.error = null;
      try {
        const { data } = await cheapSharkApi.get("/deals", {
          params: {
            sortBy: this.sortBy,
            upperPrice: this.maxPrice,
            lowerPrice: 0,
            pageSize: 60,
            onSale: 1,
          },
        });
        this.deals = data;
        this.currentPage = 1;
      } catch (err) {
        console.error(err);
        this.error = "Failed to load deals. Please try again later.";
      } finally {
        this.loading = false;
      }
    },
  },

  beforeUnmount() {
    if (this.unsubscribe) {
      this.unsubscribe();
    }
  },

  async mounted() {
    this.unsubscribe = onAuthStateChanged(auth, async (user) => {
      this.currentUser = user;
      if (user) await this.loadWishlist();
    });
    await this.fetchDeals();
  },
};
</script>

<template>
  <div class="deals-page">
    <!-- ══ Page Header ══ -->
    <div class="deals-page-header">
      <div class="deals-header-bg" aria-hidden="true"></div>
      <div class="container deals-header-content">
        <div class="deals-title-row">
          <span class="deals-title-icon" aria-hidden="true">
            <svg
              width="26"
              height="26"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
              stroke-linecap="round"
              stroke-linejoin="round"
              aria-hidden="true"
            >
              <path
                d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"
              />
            </svg>
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
              <img
                src="/logo/search.svg"
                class="deals-search-icon"
                width="16"
                height="16"
                alt=""
                aria-hidden="true"
              />
              <input
                v-model="searchTerm"
                type="text"
                class="deals-input"
                placeholder="Search deals…"
                aria-label="Search deals"
              />
            </div>

            <!-- Sort -->
            <div class="deals-select-group">
              <label class="deals-filter-label" for="deals-sort">Sort By</label>
              <select
                id="deals-sort"
                v-model="sortBy"
                class="deals-select"
                @change="fetchDeals"
                aria-label="Sort deals"
              >
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
              <select
                id="deals-store"
                v-model="selectedStore"
                class="deals-select"
                aria-label="Filter by store"
              >
                <option value="">All Stores</option>
                <option v-for="s in stores" :key="s.id" :value="s.id">
                  {{ s.name }}
                </option>
              </select>
            </div>
          </div>

          <!-- Row 2: Price slider + Savings slider -->
          <div class="deals-filter-row deals-sliders-row">
            <div class="deals-slider-group">
              <label class="deals-filter-label">
                Max Price:
                <strong class="deals-slider-val deals-slider-val-price"
                  >${{ maxPrice }}</strong
                >
              </label>
              <div class="deals-slider-track">
                <input
                  v-model.number="maxPrice"
                  type="range"
                  class="deals-range"
                  min="0"
                  max="60"
                  step="5"
                  @change="fetchDeals"
                  aria-label="Maximum price filter"
                />
                <div
                  class="deals-range-fill"
                  :style="{ width: (maxPrice / 60) * 100 + '%' }"
                ></div>
              </div>
            </div>

            <div class="deals-slider-group">
              <label class="deals-slider-label">
                Min Savings:
                <span class="deals-slider-val deals-slider-val-savings"
                  >{{ minSavings }}%</span
                >
              </label>
              <div class="deals-slider-track">
                <input
                  type="range"
                  min="0"
                  max="100"
                  v-model="minSavings"
                  class="deals-range deals-range-green"
                  aria-label="Minimum savings slider"
                />
                <div
                  class="deals-range-fill deals-range-fill-green"
                  :style="{ width: `${minSavings}%` }"
                ></div>
              </div>
            </div>

            <!-- View toggle -->
            <div class="view-toggle" style="margin-left: auto">
              <button
                class="view-btn"
                :class="{ active: viewMode === 'grid' }"
                @click="viewMode = 'grid'"
                aria-label="Grid view"
                title="Grid view"
              >
                ⊞
              </button>
              <button
                class="view-btn"
                :class="{ active: viewMode === 'list' }"
                @click="viewMode = 'list'"
                aria-label="List view"
                title="List view"
              >
                ≡
              </button>
            </div>
          </div>
        </div>

        <!-- Summary row -->
        <div class="deals-summary-row">
          <span class="deals-summary-text"
            >{{ filteredDeals.length }} deals · Page {{ currentPage }} of
            {{ computedTotalPages || 1 }}</span
          >
          <span v-if="!loading" class="deals-results-badge"
            >{{ filteredDeals.length }} results</span
          >
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
        <svg
          width="48"
          height="48"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="1.5"
          aria-hidden="true"
        >
          <circle cx="12" cy="12" r="10" />
          <path d="M12 8v4m0 4h.01" />
        </svg>
        <h3>Failed to load deals</h3>
        <p>{{ error }}</p>
        <button class="deals-primary-btn" @click="fetchDeals">Try Again</button>
      </div>

      <!-- Empty -->
      <div v-else-if="filteredDeals.length === 0" class="deals-state">
        <svg
          width="56"
          height="56"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="1.2"
          aria-hidden="true"
          style="opacity: 0.3"
        >
          <path d="M20 12V22H4V12" />
          <path d="M22 7H2v5h20V7z" />
          <path d="M12 22V7" />
          <path d="M12 7H7.5a2.5 2.5 0 010-5C11 2 12 7 12 7z" />
          <path d="M12 7h4.5a2.5 2.5 0 000-5C13 2 12 7 12 7z" />
        </svg>
        <h3>No deals found</h3>
        <p>Try adjusting the max price or min savings slider.</p>
      </div>

      <!-- Deals Grid -->
      <!-- Deals Grid -->
      <!-- Deals Grid -->
      <div v-else-if="viewMode === 'grid'" class="games-grid">
        <a
          v-for="(deal, index) in paginatedDeals"
          :key="deal.dealID"
          :href="dealUrl(deal.dealID)"
          target="_blank"
          rel="noopener noreferrer"
          class="game-card stagger-item"
          :style="{ animationDelay: `${(index % 12) * 0.04}s` }"
          :aria-label="`Get deal for ${deal.title}`"
        >
          <!-- Cover Image -->
          <div class="game-card-img-wrap">
            <img
              v-if="deal.thumb"
              :src="deal.thumb"
              class="game-card-img"
              :alt="`${deal.title} cover art`"
            />
            <div v-else class="game-card-img-placeholder">
              <img
                src="/logo/gamepad.svg"
                width="36"
                height="36"
                alt=""
                aria-hidden="true"
                style="opacity: 0.4"
              />
            </div>
            <div class="game-card-img-overlay" aria-hidden="true"></div>

            <div class="game-card-hover" aria-hidden="true">
              <div class="hover-content">
                <span class="hover-action">Get Deal</span>
              </div>
            </div>

            <!-- Floating action buttons -->
            <div class="card-float-actions">
              <!-- Wishlist button -->
              <button
                class="card-float-btn wishlist-btn"
                :class="{
                  wishlisted: wishlisted.has(
                    String(deal.gameID || deal.dealID),
                  ),
                }"
                @click.prevent="addToWishlist(deal, $event)"
                :title="
                  wishlisted.has(String(deal.gameID || deal.dealID))
                    ? 'In Wishlist'
                    : 'Add to Wishlist'
                "
                :aria-label="
                  wishlisted.has(String(deal.gameID || deal.dealID))
                    ? 'In Wishlist'
                    : 'Add to Wishlist'
                "
              >
                {{
                  wishlisted.has(String(deal.gameID || deal.dealID)) ? "♥" : "♡"
                }}
              </button>
            </div>

            <!-- Genre Ribbon (Store instead) -->
            <div class="genre-ribbon">
              {{ storeName(deal.storeID) }}
            </div>

            <!-- Metacritic badge -->
            <span
              v-if="deal.metacriticScore && deal.metacriticScore !== '0'"
              class="mc-badge"
              :class="
                parseInt(deal.metacriticScore) >= 75
                  ? 'mc-green'
                  : parseInt(deal.metacriticScore) >= 50
                    ? 'mc-yellow'
                    : 'mc-red'
              "
              :title="`Metacritic: ${deal.metacriticScore}`"
            >
              {{ deal.metacriticScore }}
            </span>
          </div>

          <!-- Card Body -->
          <div class="game-card-body">
            <div class="game-card-header">
              <h3 class="game-card-title">{{ deal.title }}</h3>
              <span class="game-type premium">DEAL</span>
            </div>

            <!-- Star Rating -->
            <div
              class="game-card-stars"
              v-if="deal.steamRatingPercent && deal.steamRatingPercent !== '0'"
            >
              <span
                v-for="(star, si) in ratingStars(deal.steamRatingPercent)"
                :key="si"
                class="star-icon"
                :class="star"
              >
                {{ star === "full" ? "★" : star === "half" ? "⯨" : "☆" }}
              </span>
              <span class="rating-label"
                >{{ deal.steamRatingText }} ({{
                  deal.steamRatingPercent
                }}%)</span
              >
            </div>

            <!-- Price row -->
            <div class="game-card-price-row">
              <template v-if="deal.salePrice === '0.00'">
                <span class="price-current">FREE</span>
              </template>
              <template v-else>
                <span class="price-discount-badge"
                  >-{{ savingsInt(deal.savings) }}%</span
                >
                <span class="price-original">${{ deal.normalPrice }}</span>
                <span class="price-current">${{ deal.salePrice }}</span>
              </template>
              <span class="game-source-pill">CheapShark</span>
            </div>
          </div>
        </a>
      </div>

      <!-- Games List -->
      <div v-else class="games-list">
        <a
          v-for="(deal, index) in paginatedDeals"
          :key="deal.dealID"
          :href="dealUrl(deal.dealID)"
          target="_blank"
          rel="noopener noreferrer"
          class="game-list-row stagger-item"
          :style="{ animationDelay: `${(index % 12) * 0.03}s` }"
        >
          <div class="glr-thumb-wrap">
            <img
              v-if="deal.thumb"
              :src="deal.thumb"
              :alt="deal.title"
              class="glr-thumb"
            />
            <div v-else class="glr-thumb-placeholder"></div>
            <span
              v-if="deal.metacriticScore && deal.metacriticScore !== '0'"
              class="glr-mc"
              :class="
                parseInt(deal.metacriticScore) >= 75
                  ? 'mc-green'
                  : parseInt(deal.metacriticScore) >= 50
                    ? 'mc-yellow'
                    : 'mc-red'
              "
            >
              {{ deal.metacriticScore }}
            </span>
          </div>
          <div class="glr-info">
            <div class="glr-title">{{ deal.title }}</div>
            <div class="glr-meta">
              <span class="game-genre-tag">{{ storeName(deal.storeID) }}</span>
            </div>
            <div
              class="glr-stars"
              v-if="deal.steamRatingPercent && deal.steamRatingPercent !== '0'"
            >
              <span
                v-for="(s, si) in ratingStars(deal.steamRatingPercent)"
                :key="si"
                class="star-icon"
                :class="s"
              >
                {{ s === "full" ? "★" : s === "half" ? "⯨" : "☆" }}
              </span>
              <span class="rating-label">{{ deal.steamRatingText }}</span>
            </div>
          </div>
          <div class="glr-right">
            <div class="glr-price">
              <template v-if="deal.salePrice === '0.00'">
                <span class="price-free">FREE</span>
              </template>
              <template v-else>
                <span class="price-discount-badge"
                  >-{{ savingsInt(deal.savings) }}%</span
                >
                <span class="price-original">${{ deal.normalPrice }}</span>
                <span class="price-current">${{ deal.salePrice }}</span>
              </template>
            </div>
            <div class="glr-actions">
              <button
                class="glr-btn wishlist"
                :class="{
                  active: wishlisted.has(String(deal.gameID || deal.dealID)),
                }"
                @click="addToWishlist(deal, $event)"
                :aria-label="
                  wishlisted.has(String(deal.gameID || deal.dealID))
                    ? 'In Wishlist'
                    : 'Wishlist'
                "
              >
                {{
                  wishlisted.has(String(deal.gameID || deal.dealID)) ? "♥" : "♡"
                }}
              </button>
            </div>
          </div>
        </a>
      </div>

      <!-- Pagination -->
      <nav
        v-if="!loading && computedTotalPages > 1"
        class="deals-pagination"
        aria-label="Deals pagination"
      >
        <button
          class="deals-page-btn"
          :disabled="currentPage === 1"
          @click="goToPage(currentPage - 1)"
        >
          <img
            src="/logo/arrow-left.svg"
            width="15"
            height="15"
            alt=""
            aria-hidden="true"
          />
          Previous
        </button>
        <div class="deals-page-numbers">
          <template v-for="(page, i) in visiblePages" :key="i">
            <span v-if="page === '...'" class="deals-page-ellipsis"
              >&#8230;</span
            >
            <button
              v-else
              class="deals-page-num"
              :class="{ active: currentPage === page }"
              @click="goToPage(page)"
            >
              {{ page }}
            </button>
          </template>
        </div>
        <button
          class="deals-page-btn"
          :disabled="currentPage === computedTotalPages"
          @click="goToPage(currentPage + 1)"
        >
          Next
          <img
            src="/logo/arrow-right.svg"
            width="15"
            height="15"
            alt=""
            aria-hidden="true"
          />
        </button>
      </nav>
    </div>
  </div>
</template>

<style scoped>
/* ── Page ─────────────────────────────────── */
.deals-page {
  min-height: 100vh;
  background: var(--bg-deep);
}

/* ── Header ───────────────────────────────── */
.deals-page-header {
  position: relative;
  background: var(--bg-base);
  border-bottom: 1px solid var(--border-glass);
  overflow: hidden;
}
.deals-header-bg {
  position: absolute;
  inset: 0;
  background:
    radial-gradient(
      ellipse 65% 120% at 90% 50%,
      rgba(234, 179, 8, 0.06) 0%,
      transparent 60%
    ),
    radial-gradient(
      ellipse 50% 80% at 10% 80%,
      rgba(124, 58, 237, 0.07) 0%,
      transparent 60%
    );
  pointer-events: none;
}
.deals-header-content {
  position: relative;
  z-index: 1;
  padding-top: 40px;
  padding-bottom: 0;
}

/* Title row */
.deals-title-row {
  display: flex;
  align-items: center;
  gap: 18px;
  margin-bottom: 20px;
}
.deals-title-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 54px;
  height: 54px;
  border-radius: 16px;
  background: linear-gradient(135deg, #b45309, #f59e0b);
  color: #fff;
  flex-shrink: 0;
  box-shadow: 0 4px 20px rgba(245, 158, 11, 0.4);
}
.deals-title {
  font-size: 2.1rem;
  font-weight: 800;
  color: var(--text-primary) !important;
  margin: 0 0 4px;
  line-height: 1;
}
.deals-subtitle {
  font-size: 0.85rem;
  color: var(--text-secondary) !important;
  margin: 0;
}
.deals-powered {
  opacity: 0.55;
}

/* ── Filter Panel ─────────────────────────── */
.deals-filter-panel {
  background: var(--bg-surface);
  border: 1px solid var(--border-glass);
  border-bottom: none;
  border-radius: 14px 14px 0 0;
  padding: 20px 24px 16px;
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
}
.deals-filter-row {
  display: flex;
  align-items: flex-end;
  gap: 14px;
  flex-wrap: wrap;
  margin-bottom: 16px;
}
.deals-filter-row:last-child {
  margin-bottom: 0;
}
.deals-filter-label {
  display: block;
  font-size: 0.72rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.6px;
  color: var(--text-muted) !important;
  margin-bottom: 6px;
}

/* Search */
.deals-search-wrap {
  flex: 1;
  min-width: 200px;
  position: relative;
}
.deals-search-icon {
  position: absolute;
  left: 13px;
  top: 50%;
  transform: translateY(-50%);
  pointer-events: none;
  opacity: 0.6;
}
.deals-input {
  width: 100%;
  background: var(--bg-glass);
  border: 1px solid var(--border-glass);
  border-radius: var(--radius-sm);
  color: var(--text-primary) !important;
  padding: 10px 14px 10px 38px;
  font-size: 0.88rem;
  font-family: var(--font-family);
  outline: none;
  transition: border-color 0.2s;
}
.deals-input::placeholder {
  color: var(--text-muted);
}
.deals-input:focus {
  border-color: var(--primary-light);
}

/* Select groups */
.deals-select-group {
  display: flex;
  flex-direction: column;
}
.deals-select {
  background: var(--bg-glass);
  border: 1px solid var(--border-glass);
  border-radius: var(--radius-sm);
  color: var(--text-primary) !important;
  padding: 9px 14px;
  font-size: 0.88rem;
  font-family: var(--font-family);
  outline: none;
  cursor: pointer;
  min-width: 140px;
}
.deals-select:focus {
  border-color: var(--primary-light);
}

/* Sliders */
.deals-sliders-row {
  align-items: flex-start;
}
.deals-slider-group {
  flex: 1;
  min-width: 200px;
}
.deals-slider-val {
  font-size: 0.88rem;
}
.deals-slider-val-price {
  color: #a78bfa !important;
}
.deals-slider-val-savings {
  color: #4ade80 !important;
}
.deals-slider-track {
  position: relative;
  padding-bottom: 8px;
}
.deals-range {
  width: 100%;
  -webkit-appearance: none;
  appearance: none;
  height: 4px;
  border-radius: 2px;
  background: var(--border-glass);
  outline: none;
  cursor: pointer;
  position: relative;
  z-index: 2;
}
.deals-range::-webkit-slider-thumb {
  -webkit-appearance: none;
  appearance: none;
  width: 16px;
  height: 16px;
  border-radius: 50%;
  background: #7c3aed;
  cursor: pointer;
  box-shadow: 0 0 0 3px rgba(124, 58, 237, 0.25);
  transition: box-shadow 0.2s;
}
.deals-range::-webkit-slider-thumb:hover {
  box-shadow: 0 0 0 5px rgba(124, 58, 237, 0.3);
}
.deals-range-green::-webkit-slider-thumb {
  background: #16a34a;
  box-shadow: 0 0 0 3px rgba(22, 163, 74, 0.25);
}
.deals-range-green::-webkit-slider-thumb:hover {
  box-shadow: 0 0 0 5px rgba(22, 163, 74, 0.3);
}
.deals-range-fill {
  position: absolute;
  top: 0;
  left: 0;
  height: 4px;
  border-radius: 2px;
  background: var(--gradient-primary);
  pointer-events: none;
}
.deals-range-fill-green {
  background: linear-gradient(90deg, #16a34a, #4ade80);
}

/* Summary row */
.deals-summary-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 24px;
  background: var(--bg-surface);
  border: 1px solid var(--border-glass);
  border-top: none;
}
.deals-summary-text {
  font-size: 0.78rem;
  color: var(--text-muted) !important;
  font-style: italic;
}
.deals-results-badge {
  font-size: 0.72rem;
  font-weight: 700;
  padding: 3px 12px;
  border-radius: 20px;
  background: linear-gradient(135deg, #b45309, #f59e0b);
  color: #fff !important;
}

/* ── Content ──────────────────────────────── */
.deals-content {
  padding-top: 28px;
  padding-bottom: 60px;
}

/* ── GRID ── */
.games-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 24px;
  padding-top: 10px;
}

.game-card {
  display: flex;
  flex-direction: column;
  background: var(--bg-glass);
  border: 1px solid var(--border-glass);
  border-radius: 12px;
  overflow: hidden;
  text-decoration: none;
  transition: all 0.3s ease;
  position: relative;
}
.game-card:hover {
  transform: translateY(-5px);
  box-shadow:
    0 12px 30px rgba(0, 0, 0, 0.4),
    0 0 0 1px rgba(245, 158, 11, 0.3);
}

/* Image */
.game-card-img-wrap {
  position: relative;
  overflow: hidden;
  height: 180px;
  flex-shrink: 0;
  background: rgba(10, 15, 30, 0.5);
}
.game-card-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
  transition: transform 0.4s ease;
}
.game-card:hover .game-card-img {
  transform: scale(1.05);
}
.game-card-img-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg-glass);
  color: var(--text-muted);
}
.game-card-img-overlay {
  position: absolute;
  inset: 0;
  background: linear-gradient(
    to bottom,
    transparent 40%,
    rgba(5, 7, 15, 0.65) 75%,
    rgba(5, 7, 15, 0.95) 100%
  );
  pointer-events: none;
}

.game-card-hover {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(5, 8, 18, 0.72);
  opacity: 0;
  transition: 0.28s ease;
  z-index: 3;
}
.game-card:hover .game-card-hover {
  opacity: 1;
}
.hover-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
}
.hover-action {
  padding: 12px 26px;
  background: var(--gradient-primary);
  border-radius: 999px;
  font-weight: 700;
  transition: 0.25s;
}
.game-card:hover .hover-action {
  transform: translateY(0);
  color: #fff;
}

.genre-ribbon {
  position: absolute;
  left: 12px;
  top: 12px;
  z-index: 3;
  padding: 6px 12px;
  border-radius: 999px;
  background: rgba(12, 17, 29, 0.82);
  backdrop-filter: blur(10px);
  font-size: 0.72rem;
  font-weight: 700;
  color: white;
  border: 1px solid rgba(255, 255, 255, 0.08);
}

/* Metacritic */
.mc-badge {
  position: absolute;
  top: 10px;
  right: 10px;
  font-size: 0.78rem;
  font-weight: 800;
  padding: 4px 9px;
  border-radius: 7px;
  min-width: 38px;
  text-align: center;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.5);
  letter-spacing: 0.02em;
  z-index: 2;
}
.mc-green {
  background: #15803d;
  color: #d1fae5;
  border: 1px solid rgba(21, 128, 61, 0.4);
}
.mc-yellow {
  background: #92400e;
  color: #fde68a;
  border: 1px solid rgba(146, 64, 14, 0.4);
}
.mc-red {
  background: #991b1b;
  color: #fee2e2;
  border: 1px solid rgba(153, 27, 27, 0.4);
}
.mc-none {
  display: none;
}

/* Platform icons */
.game-card-platforms {
  position: absolute;
  bottom: 10px;
  right: 10px;
  display: flex;
  gap: 5px;
  z-index: 2;
}
.platform-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 26px;
  height: 26px;
  border-radius: 6px;
  background: var(--bg-glass);
  color: var(--text-primary);
  backdrop-filter: blur(6px);
  border: 1px solid var(--border-glass);
  transition:
    background 0.2s,
    color 0.2s;
}
.game-card:hover .platform-icon {
  background: var(--primary);
  color: #fff;
}

/* Card body */
.game-card-body {
  padding: 16px 18px 18px;
  display: flex;
  flex-direction: column;
  gap: 10px;
  flex: 1;
}
.game-card-title {
  font-size: 0.97rem;
  font-weight: 700;
  line-height: 1.4;
  color: var(--text-primary) !important;
  margin: 0;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.game-card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 10px;
}
.game-type {
  font-size: 0.65rem;
  font-weight: 800;
  padding: 5px 8px;
  border-radius: 999px;
  letter-spacing: 0.08em;
  flex-shrink: 0;
}
.game-type.free {
  background: #16a34a;
  color: white;
}
.game-type.premium {
  background: #f59e0b;
  color: #111;
}

/* Genre tags */
.game-card-genres {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}
.game-genre-tag {
  font-size: 0.68rem;
  font-weight: 600;
  padding: 3px 10px;
  border-radius: 20px;
  background: rgba(14, 165, 233, 0.15);
  color: var(--primary-light);
  border: 1px solid rgba(14, 165, 233, 0.28);
  letter-spacing: 0.02em;
  transition: background 0.2s;
}
.game-card:hover .game-genre-tag {
  background: rgba(14, 165, 233, 0.3);
  color: #fff;
}

/* Float action buttons on card image */
.card-float-actions {
  position: absolute;
  bottom: 45px;
  right: 10px;
  z-index: 5;
  display: flex;
  flex-direction: row;
  gap: 6px;
  opacity: 0;
  transform: translateY(6px);
  transition:
    opacity 0.25s,
    transform 0.25s;
}
.game-card:hover .card-float-actions {
  opacity: 1;
  transform: translateY(0);
}
.card-float-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border-radius: 8px;
  border: none;
  font-size: 0.85rem;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s;
  backdrop-filter: blur(6px);
}
.wishlist-btn {
  background: rgba(0, 0, 0, 0.6);
  color: #fff;
  border: 1px solid rgba(255, 255, 255, 0.1);
}
.wishlist-btn.wishlisted {
  background: rgba(239, 68, 68, 0.8);
  border-color: transparent;
}
.wishlist-btn:hover {
  background: rgba(239, 68, 68, 0.9);
  border-color: transparent;
}

/* Stars */
.game-card-stars {
  display: flex;
  align-items: center;
  gap: 3px;
  margin-top: auto;
}
.star-icon {
  font-size: 0.85rem;
  line-height: 1;
}
.star-icon.full {
  color: #f59e0b;
}
.star-icon.half {
  color: #f59e0b;
  opacity: 0.7;
}
.star-icon.empty {
  color: rgba(255, 255, 255, 0.15);
}
.rating-label {
  font-size: 0.68rem;
  color: var(--text-muted);
  margin-left: 5px;
}

/* Price row */
.game-card-price-row {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 2px;
  padding-top: 10px;
  border-top: 1px solid rgba(255, 255, 255, 0.05);
}
.price-discount-badge {
  font-size: 0.72rem;
  font-weight: 800;
  color: #fff;
  background: #22c55e;
  padding: 2px 7px;
  border-radius: 5px;
}
.price-original {
  font-size: 0.78rem;
  color: var(--text-muted);
  text-decoration: line-through;
}
.price-current {
  font-size: 0.95rem;
  font-weight: 800;
  color: var(--text-primary);
}
.game-source-pill {
  margin-left: auto;
  font-size: 0.62rem;
  font-weight: 700;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  color: var(--text-secondary);
  opacity: 0.7;
}
.deal-rating-label {
  font-size: 0.65rem;
  color: var(--text-muted);
  margin-left: 4px;
  white-space: nowrap;
}

/* ── List view additions ── */
.games-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
  padding-top: 8px;
}
.game-list-row {
  display: flex;
  align-items: center;
  gap: 16px;
  background: var(--bg-glass);
  border: 1px solid var(--border-glass);
  border-radius: 12px;
  padding: 12px 16px;
  text-decoration: none;
  color: var(--text-primary);
  transition: all 0.2s;
}
.game-list-row:hover {
  border-color: rgba(245, 158, 11, 0.35);
  background: var(--bg-glass-hover);
  transform: translateX(4px);
  color: var(--text-primary);
}
.glr-thumb-wrap {
  position: relative;
  flex-shrink: 0;
}
.glr-thumb {
  width: 100px;
  height: 60px;
  object-fit: cover;
  border-radius: 8px;
  display: block;
}
.glr-thumb-placeholder {
  width: 100px;
  height: 60px;
  border-radius: 8px;
  background: var(--bg-glass);
}
.glr-mc {
  position: absolute;
  top: -5px;
  right: -5px;
  font-size: 0.65rem;
  font-weight: 800;
  padding: 2px 5px;
  border-radius: 4px;
}
.glr-info {
  flex: 1;
  min-width: 0;
}
.glr-title {
  font-size: 0.9rem;
  font-weight: 700;
  color: var(--text-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  margin-bottom: 5px;
}
.glr-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
  margin-bottom: 5px;
}
.game-genre-tag {
  font-size: 0.68rem;
  font-weight: 600;
  padding: 2px 6px;
  border-radius: 4px;
  background: var(--border-glass);
  color: var(--text-secondary);
}
.glr-year {
  font-size: 0.72rem;
  color: var(--text-muted);
}
.glr-stars {
  display: flex;
  align-items: center;
  gap: 3px;
}
.star-icon {
  font-size: 0.8rem;
  line-height: 1;
}
.star-icon.full {
  color: #f59e0b;
}
.star-icon.half {
  color: #f59e0b;
  opacity: 0.7;
}
.star-icon.empty {
  color: var(--border-glass);
}
.rating-label {
  font-size: 0.65rem;
  color: var(--text-muted);
  margin-left: 4px;
  white-space: nowrap;
}
.glr-right {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 8px;
  flex-shrink: 0;
}
.glr-price {
  display: flex;
  align-items: center;
  gap: 6px;
}
.price-discount-badge {
  font-size: 0.72rem;
  font-weight: 800;
  color: #fff;
  background: #22c55e;
  padding: 2px 7px;
  border-radius: 5px;
}
.price-original {
  font-size: 0.78rem;
  color: var(--text-muted);
  text-decoration: line-through;
}
.price-current {
  font-size: 0.95rem;
  font-weight: 800;
  color: var(--text-primary);
}
.price-free {
  font-size: 0.88rem;
  font-weight: 700;
  color: #34d399;
}
.glr-actions {
  display: flex;
  gap: 6px;
}
.glr-btn {
  width: 32px;
  height: 32px;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 0.85rem;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
}
.glr-btn.wishlist {
  background: var(--bg-surface);
  color: var(--text-muted);
  border: 1px solid var(--border-glass);
}
.glr-btn.wishlist:hover,
.glr-btn.wishlist.active {
  color: #f43f5e;
  border-color: #f43f5e;
  background: rgba(244, 63, 94, 0.12);
}

/* View toggle */
.view-toggle {
  display: flex;
  border: 1px solid var(--border-glass);
  border-radius: 8px;
  overflow: hidden;
}
.view-btn {
  padding: 8px 12px;
  border: none;
  background: transparent;
  color: var(--text-muted);
  cursor: pointer;
  font-size: 1rem;
  transition: all 0.2s;
}
.view-btn.active {
  background: rgba(245, 158, 11, 0.3);
  color: #fbbf24;
}
.view-btn:hover:not(.active) {
  background: var(--bg-surface);
  color: var(--text-secondary);
}
</style>
