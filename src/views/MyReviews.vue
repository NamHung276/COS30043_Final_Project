<script>
import { inject } from "vue";
import { MessageSquare, Star, Trash2 } from "@lucide/vue";
import { auth, db } from "../firebase";
import { onAuthStateChanged } from "firebase/auth";
import {
  collection,
  query,
  where,
  getDocs,
  deleteDoc,
  doc,
} from "firebase/firestore";

export default {
  components: { MessageSquare, Star, Trash2 },
  setup() {
    const toast = inject("toast");
    return { toast };
  },

  data() {
    return {
      reviews: [],
      loading: true,
      currentUser: null,
      searchQuery: "",
      sortBy: "newest",
    };
  },

  computed: {
    filteredReviews() {
      let list = [...this.reviews];

      if (this.searchQuery.trim()) {
        const q = this.searchQuery.toLowerCase();
        list = list.filter(
          (r) =>
            r.gameName?.toLowerCase().includes(q) ||
            r.comment?.toLowerCase().includes(q)
        );
      }

      if (this.sortBy === "newest") {
        list.sort((a, b) => b.createdAt?.seconds - a.createdAt?.seconds);
      } else if (this.sortBy === "oldest") {
        list.sort((a, b) => a.createdAt?.seconds - b.createdAt?.seconds);
      } else if (this.sortBy === "highest") {
        list.sort((a, b) => b.rating - a.rating);
      } else if (this.sortBy === "lowest") {
        list.sort((a, b) => a.rating - b.rating);
      }

      return list;
    },

    totalCount() {
      return this.reviews.length;
    },

    filteredCount() {
      return this.filteredReviews.length;
    },

    averageRating() {
      if (this.reviews.length === 0) return "0.0";
      const total = this.reviews.reduce((sum, r) => sum + r.rating, 0);
      return (total / this.reviews.length).toFixed(1);
    },
  },

  methods: {
    timeAgo(seconds) {
      if (!seconds) return "Unknown date";
      const diff = Math.floor(Date.now() / 1000) - seconds;
      if (diff < 60) return "Just now";
      if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
      if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`;
      return `${Math.floor(diff / 86400)}d ago`;
    },

    async removeReview(reviewId, gameName) {
      if (!confirm(`Are you sure you want to delete your review for ${gameName}?`)) return;
      
      try {
        await deleteDoc(doc(db, "reviews", reviewId));
        this.reviews = this.reviews.filter((rev) => rev.id !== reviewId);
        this.toast.show(`Removed review for "${gameName}"`, "info");
      } catch (error) {
        console.error("Failed to remove review:", error);
        this.toast.show("Failed to remove review. Please try again.", "error");
      }
    },

    async loadReviews(user) {
      this.loading = true;
      try {
        const reviewsQuery = query(
          collection(db, "reviews"),
          where("userId", "==", user.uid)
        );
        const snapshot = await getDocs(reviewsQuery);
        const revs = snapshot.docs.map((docSnap) => ({
          id: docSnap.id,
          ...docSnap.data(),
        }));

        this.reviews = revs;
      } catch (e) {
        console.error("Failed to load reviews:", e);
        this.toast.show("Error loading reviews", "error");
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

  mounted() {
    this.unsubscribe = onAuthStateChanged(auth, (user) => {
      if (!user) {
        this.reviews = [];
        this.currentUser = null;
        return;
      }
      this.currentUser = user;
      this.loadReviews(user);
    });
  },
};
</script>

<template>
  <div class="fav-page">
    <!-- Hero Header -->
    <div class="fav-hero">
      <div class="fav-hero-bg"></div>
      <div class="fav-hero-content container">
        <div class="fav-hero-icon bg-info">
          <MessageSquare color="white" size="32" />
        </div>
        <div>
          <h1 class="fav-hero-title">My Reviews</h1>
          <p class="fav-hero-sub">
            Your personal game reviews and ratings
          </p>
        </div>
        <div class="fav-hero-stats ms-auto d-none d-md-flex">
          <div class="fav-stat">
            <span class="fav-stat-num">{{ totalCount }}</span>
            <span class="fav-stat-label">Reviews</span>
          </div>
          <div class="fav-stat-divider"></div>
          <div class="fav-stat">
            <span class="fav-stat-num text-warning d-flex align-items-center gap-1">
              {{ averageRating }} <Star fill="currentColor" size="20" class="mb-1" />
            </span>
            <span class="fav-stat-label">Avg Rating</span>
          </div>
        </div>
      </div>
    </div>

    <div class="container fav-body">
      <!-- Toolbar -->
      <div class="fav-toolbar" v-if="!loading && reviews.length > 0">
        <div class="fav-search-wrap flex-grow-1">
          <i class="bi bi-search fav-search-icon"></i>
          <input
            v-model="searchQuery"
            type="text"
            class="fav-search w-100"
            placeholder="Search your reviews by game or comment…"
            aria-label="Search reviews"
          />
          <button
            v-if="searchQuery"
            class="fav-search-clear"
            @click="searchQuery = ''"
            aria-label="Clear search"
          >
            <i class="bi bi-x-lg"></i>
          </button>
        </div>

        <div class="fav-toolbar-right">
          <select
            v-model="sortBy"
            class="fav-select"
            aria-label="Sort reviews"
          >
            <option value="newest">Newest First</option>
            <option value="oldest">Oldest First</option>
            <option value="highest">Highest Rating</option>
            <option value="lowest">Lowest Rating</option>
          </select>
        </div>
      </div>

      <!-- Result count -->
      <div v-if="!loading && reviews.length > 0" class="fav-result-count">
        Showing <strong>{{ filteredCount }}</strong> of
        <strong>{{ totalCount }}</strong> reviews
      </div>

      <!-- Loading Skeletons -->
      <div v-if="loading" class="d-flex flex-column gap-3">
        <div v-for="i in 3" :key="i" class="card profile-glass-card p-4">
          <div class="placeholder-glow w-25 mb-3"><span class="placeholder col-12"></span></div>
          <div class="placeholder-glow w-100 mb-2"><span class="placeholder col-12"></span></div>
          <div class="placeholder-glow w-75"><span class="placeholder col-12"></span></div>
        </div>
      </div>

      <!-- Empty State -->
      <div v-else-if="filteredCount === 0" class="fav-empty text-center">
        <MessageSquare size="64" class="text-muted opacity-50 mb-3" />
        <h3 class="profile-text">No reviews found</h3>
        <p class="text-muted-light" v-if="searchQuery">
          No reviews matched your search criteria.
        </p>
        <p class="text-muted-light" v-else>
          You haven't written any game reviews yet.
        </p>
        <router-link to="/games" class="btn btn-primary px-4 mt-3">Browse Games</router-link>
      </div>

      <!-- Reviews List -->
      <div v-else class="d-flex flex-column gap-3 mb-5">
        <div
          v-for="rev in filteredReviews"
          :key="rev.id"
          class="card profile-glass-card p-4"
        >
          <div class="d-flex justify-content-between align-items-center mb-3">
            <div class="d-flex align-items-center gap-2">
              <span class="text-warning">
                <template v-for="s in rev.rating" :key="'r' + s">
                  <Star fill="currentColor" size="16" />
                </template>
                <template v-for="s in 5 - rev.rating" :key="'e' + s">
                  <Star size="16" class="opacity-25" />
                </template>
              </span>
              <span class="profile-text fw-bold">
                {{ rev.gameName || 'Unknown Game' }}
              </span>
            </div>
            <div class="d-flex align-items-center gap-3">
              <span class="text-muted-light small">{{ timeAgo(rev.createdAt?.seconds) }}</span>
              <button
                class="btn btn-sm btn-outline-danger d-flex align-items-center gap-1 border-0"
                @click="removeReview(rev.id, rev.gameName)"
                title="Delete review"
              >
                <Trash2 size="16" />
              </button>
            </div>
          </div>
          <p class="text-muted-light mb-3">
            "{{ rev.comment }}"
          </p>
          <div class="d-flex justify-content-end pt-2 border-top border-secondary border-opacity-25 mt-2">
            <router-link
              :to="`/games/${rev.gameId}`"
              class="btn btn-sm btn-outline-primary rounded-pill px-3"
            >
              View Game
            </router-link>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.fav-page {
  min-height: 100vh;
  background: var(--bg-deep);
  padding-bottom: 3rem;
}

/* Hero Header */
.fav-hero {
  position: relative;
  padding: 48px 0;
  overflow: hidden;
  background: var(--bg-base);
  border-bottom: 1px solid var(--border-glass);
  margin-bottom: 32px;
}
.fav-hero-bg {
  position: absolute;
  inset: 0;
  background: radial-gradient(circle at 80% 20%, rgba(6, 182, 212, 0.15), transparent 40%),
              radial-gradient(circle at 20% 80%, rgba(124, 58, 237, 0.1), transparent 40%);
  pointer-events: none;
}
.fav-hero-content {
  position: relative;
  z-index: 1;
  display: flex;
  align-items: center;
  gap: 24px;
}
.fav-hero-icon {
  width: 72px;
  height: 72px;
  border-radius: 20px;
  background: var(--gradient-primary);
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 8px 32px rgba(124, 58, 237, 0.3);
  flex-shrink: 0;
}
.fav-hero-title {
  font-size: 2.2rem;
  font-weight: 800;
  color: var(--text-primary);
  margin: 0 0 4px;
}
.fav-hero-sub {
  font-size: 1.1rem;
  color: var(--text-muted);
  margin: 0;
}
.fav-hero-stats {
  display: flex;
  align-items: center;
  gap: 24px;
  background: var(--bg-glass);
  border: 1px solid var(--border-glass);
  padding: 16px 32px;
  border-radius: 20px;
  backdrop-filter: blur(12px);
}
.fav-stat {
  display: flex;
  flex-direction: column;
  align-items: center;
}
.fav-stat-num {
  font-size: 1.5rem;
  font-weight: 800;
  color: var(--text-primary);
  line-height: 1.2;
}
.fav-stat-label {
  font-size: 0.8rem;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: var(--text-muted);
  font-weight: 600;
}
.fav-stat-divider {
  width: 1px;
  height: 32px;
  background: var(--border-glass);
}

/* Toolbar */
.fav-toolbar {
  display: flex;
  gap: 16px;
  margin-bottom: 24px;
  flex-wrap: wrap;
}
.fav-search-wrap {
  position: relative;
  min-width: 250px;
}
.fav-search {
  background: var(--bg-glass);
  border: 1px solid var(--border-glass);
  color: var(--text-primary);
  border-radius: 12px;
  padding: 12px 16px 12px 42px;
  width: 100%;
  transition: all 0.3s ease;
}
.fav-search:focus {
  outline: none;
  background: var(--bg-glass-hover);
  border-color: rgba(124, 58, 237, 0.5);
  box-shadow: 0 0 0 3px rgba(124, 58, 237, 0.15);
}
.fav-search-icon {
  position: absolute;
  left: 14px;
  top: 50%;
  transform: translateY(-50%);
  color: var(--text-muted);
  pointer-events: none;
}
.fav-search-clear {
  position: absolute;
  right: 12px;
  top: 50%;
  transform: translateY(-50%);
  background: transparent;
  border: none;
  color: var(--text-muted);
  cursor: pointer;
  padding: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
}
.fav-search-clear:hover {
  background: rgba(255, 255, 255, 0.1);
  color: var(--text-primary);
}
.fav-toolbar-right {
  display: flex;
  gap: 12px;
  margin-left: auto;
}
.fav-select {
  background: var(--bg-glass);
  border: 1px solid var(--border-glass);
  color: var(--text-primary);
  border-radius: 12px;
  padding: 10px 16px;
  min-width: 160px;
  appearance: none;
  background-image: url("data:image/svg+xml;charset=US-ASCII,%3Csvg%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20width%3D%22292.4%22%20height%3D%22292.4%22%3E%3Cpath%20fill%3D%22%23a1a1aa%22%20d%3D%22M287%2069.4a17.6%2017.6%200%200%200-13-5.4H18.4c-5%200-9.3%201.8-12.9%205.4A17.6%2017.6%200%200%200%200%2082.2c0%205%201.8%209.3%205.4%2012.9l128%20127.9c3.6%203.6%207.8%205.4%2012.8%205.4s9.2-1.8%2012.8-5.4L287%2095c3.5-3.5%205.4-7.8%205.4-12.8%200-5-1.9-9.2-5.5-12.8z%22%2F%3E%3C%2Fsvg%3E");
  background-repeat: no-repeat;
  background-position: right 16px top 50%;
  background-size: 10px auto;
  transition: all 0.2s;
  cursor: pointer;
}
.fav-select:focus {
  outline: none;
  border-color: rgba(124, 58, 237, 0.5);
  box-shadow: 0 0 0 3px rgba(124, 58, 237, 0.15);
}

.fav-result-count {
  font-size: 0.9rem;
  color: var(--text-muted);
  margin-bottom: 24px;
}
.fav-result-count strong {
  color: var(--text-primary);
}

.fav-empty {
  padding: 80px 20px;
}

.profile-glass-card {
  background: var(--bg-glass);
  border: 1px solid var(--border-glass);
  border-radius: 16px;
  backdrop-filter: blur(16px);
  box-shadow: var(--shadow-sm);
}

@media (max-width: 768px) {
  .fav-toolbar {
    flex-direction: column;
  }
  .fav-toolbar-right {
    margin-left: 0;
    width: 100%;
  }
  .fav-select {
    width: 100%;
  }
}
</style>
