<script>
import { auth, db } from "../firebase";
import { collection, query, where, getDocs, doc, setDoc, deleteDoc } from "firebase/firestore";
import { onAuthStateChanged } from "firebase/auth";
import { backendApi } from "../services/api";

export default {
  name: "CryptoMarket",
  inject: ["toast"],
  data() {
    return {
      coins: [],
      loading: true,
      error: null,
      currentUser: null,
      bookmarks: new Set(),
      submitting: false,
    };
  },
  mounted() {
    this.fetchMarketData();
    this.unsubscribe = onAuthStateChanged(auth, (user) => {
      this.currentUser = user;
      if (user) {
        this.fetchBookmarks();
      } else {
        this.bookmarks.clear();
      }
    });
  },
  beforeUnmount() {
    if (this.unsubscribe) {
      this.unsubscribe();
    }
  },
  methods: {
    async fetchMarketData() {
      this.loading = true;
      try {
        const res = await backendApi.get("/crypto/market");
        this.coins = res.data.coins || [];
      } catch (err) {
        console.error("CryptoMarket Error:", err);
        this.error = "Could not load gaming crypto market data.";
      } finally {
        this.loading = false;
      }
    },
    async fetchBookmarks() {
      if (!this.currentUser) return;
      try {
        const q = query(
          collection(db, "crypto_bookmarks"),
          where("userId", "==", this.currentUser.uid)
        );
        const snapshot = await getDocs(q);
        const savedIds = new Set();
        snapshot.forEach(doc => {
          savedIds.add(doc.data().coinId);
        });
        this.bookmarks = savedIds;
      } catch (error) {
        console.error("Error fetching bookmarks:", error);
      }
    },
    async toggleBookmark(coinId) {
      if (!this.currentUser) {
        this.toast?.show("Please login to bookmark coins.", "warning");
        return;
      }
      if (this.submitting) return;
      this.submitting = true;

      const docId = `${this.currentUser.uid}_${coinId}`;
      const docRef = doc(db, "crypto_bookmarks", docId);

      try {
        if (this.bookmarks.has(coinId)) {
          // Remove bookmark
          await deleteDoc(docRef);
          this.bookmarks.delete(coinId);
          this.toast?.show("Removed from watchlist", "success");
        } else {
          // Add bookmark
          await setDoc(docRef, {
            userId: this.currentUser.uid,
            coinId: coinId,
            addedAt: new Date().toISOString()
          });
          this.bookmarks.add(coinId);
          this.toast?.show("Added to watchlist", "success");
        }
      } catch (err) {
        console.error("Bookmark toggle error:", err);
        this.toast?.show("Failed to update watchlist.", "error");
      } finally {
        this.submitting = false;
      }
    },
    formatPrice(val) {
      if (val === null || val === undefined) return "N/A";
      if (val < 0.01) return "$" + Number(val).toPrecision(4);
      return "$" + Number(val).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 });
    },
    formatCap(val) {
      if (!val) return "N/A";
      if (val >= 1e9) return "$" + (val / 1e9).toFixed(2) + "B";
      if (val >= 1e6) return "$" + (val / 1e6).toFixed(2) + "M";
      return "$" + val.toLocaleString();
    }
  }
};
</script>

<template>
  <div class="crypto-market-section py-5">
    <div class="container">
      <div class="d-flex justify-content-between align-items-center mb-4">
        <div>
          <h2 class="text-primary-var fw-bold mb-1">
            <i class="bi bi-currency-bitcoin me-2"></i> Gaming Crypto Market
          </h2>
          <p class="text-muted mb-0">Track top gaming tokens and Metaverse projects in real-time.</p>
        </div>
      </div>

      <div v-if="error" class="alert alert-danger" role="alert">
        {{ error }}
      </div>

      <div v-if="loading" class="row g-4">
        <div v-for="n in 4" :key="n" class="col-12 col-md-6 col-lg-3">
          <div class="crypto-card skeleton-card">
            <div class="skeleton" style="height: 40px; width: 40px; border-radius: 50%;"></div>
            <div class="skeleton mt-3" style="height: 20px; width: 60%;"></div>
            <div class="skeleton mt-2" style="height: 28px; width: 40%;"></div>
          </div>
        </div>
      </div>

      <div v-else class="row g-4">
        <div v-for="coin in coins.slice(0, 8)" :key="coin.id" class="col-12 col-md-6 col-lg-3">
          <div class="crypto-card p-4 gd-glass-card position-relative">
            <!-- Bookmark Button -->
            <button 
              class="bookmark-btn" 
              @click="toggleBookmark(coin.id)"
              :class="{ 'active': bookmarks.has(coin.id) }"
              aria-label="Toggle Watchlist"
            >
              <i :class="bookmarks.has(coin.id) ? 'bi bi-star-fill text-warning' : 'bi bi-star'"></i>
            </button>

            <div class="d-flex align-items-center mb-3">
              <img :src="coin.image" :alt="coin.name" class="crypto-logo me-3" />
              <div>
                <h5 class="mb-0 text-white fw-bold">{{ coin.name }}</h5>
                <span class="text-muted text-uppercase small">{{ coin.symbol }}</span>
              </div>
            </div>
            
            <div class="d-flex justify-content-between align-items-end mt-4">
              <div>
                <div class="text-muted small mb-1">Price</div>
                <h4 class="mb-0 text-white fw-bold">{{ formatPrice(coin.current_price) }}</h4>
              </div>
              <div class="text-end">
                <div class="text-muted small mb-1">24h Change</div>
                <div 
                  class="fw-bold d-flex align-items-center justify-content-end"
                  :class="coin.price_change_percentage_24h >= 0 ? 'text-success' : 'text-danger'"
                >
                  <i :class="coin.price_change_percentage_24h >= 0 ? 'bi bi-arrow-up-short' : 'bi bi-arrow-down-short'"></i>
                  {{ Math.abs(coin.price_change_percentage_24h || 0).toFixed(2) }}%
                </div>
              </div>
            </div>

            <div class="mt-3 pt-3 border-top border-secondary border-opacity-50 d-flex justify-content-between small">
              <span class="text-muted">Market Cap</span>
              <span class="text-light">{{ formatCap(coin.market_cap) }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.crypto-market-section {
  position: relative;
  z-index: 5;
}

.gd-glass-card {
  background: rgba(20, 20, 25, 0.7);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 16px;
  backdrop-filter: blur(12px);
  transition: transform 0.3s ease, box-shadow 0.3s ease, border-color 0.3s ease;
}

.gd-glass-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 15px 35px rgba(0, 0, 0, 0.4);
  border-color: rgba(124, 58, 237, 0.4);
}

.crypto-logo {
  width: 42px;
  height: 42px;
  border-radius: 50%;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.3);
}

.bookmark-btn {
  position: absolute;
  top: 16px;
  right: 16px;
  background: transparent;
  border: none;
  color: rgba(255, 255, 255, 0.5);
  font-size: 1.2rem;
  transition: all 0.2s ease;
  z-index: 2;
}

.bookmark-btn:hover {
  color: white;
  transform: scale(1.1);
}

.bookmark-btn.active {
  color: #ffc107;
}

.skeleton-card {
  background: rgba(255, 255, 255, 0.03);
  border-radius: 16px;
  padding: 24px;
  min-height: 180px;
}
</style>
