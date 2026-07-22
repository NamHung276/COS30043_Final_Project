<script>
import { auth, db } from "../firebase";
import { collection, query, where, orderBy, getDocs } from "firebase/firestore";
import { onAuthStateChanged } from "firebase/auth";

export default {
  name: "PurchaseHistory",
  data() {
    return {
      purchases: [],
      loading: true,
      currentUser: null,
    };
  },
  mounted() {
    this.unsubscribe = onAuthStateChanged(auth, (user) => {
      if (user) {
        this.currentUser = user;
        this.fetchPurchases();
      } else {
        this.loading = false;
        this.$router.push("/login");
      }
    });
  },
  beforeUnmount() {
    if (this.unsubscribe) {
      this.unsubscribe();
    }
  },
  methods: {
    async fetchPurchases() {
      try {
        const q = query(
          collection(db, "purchases"),
          where("userId", "==", this.currentUser.uid),
          orderBy("createdAt", "desc")
        );
        const snapshot = await getDocs(q);
        this.purchases = snapshot.docs.map(doc => ({
          id: doc.id,
          ...doc.data()
        }));
      } catch (error) {
        console.error("Error fetching purchases:", error);
      } finally {
        this.loading = false;
      }
    },
    formatDate(timestamp) {
      if (!timestamp) return "N/A";
      // Firebase timestamp has toDate()
      const date = timestamp.toDate ? timestamp.toDate() : new Date(timestamp);
      return date.toLocaleDateString(undefined, {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
      });
    }
  }
};
</script>

<template>
  <div class="purchase-history-page pt-5 pb-5 min-vh-100">
    <div class="container">
      <h2 class="text-primary-var fw-bold mb-4">
        Purchase History
      </h2>
      
      <div v-if="loading" class="text-center py-5">
        <div class="spinner-border text-primary-var" role="status"></div>
      </div>
      
      <div v-else-if="purchases.length === 0" class="gd-glass-card p-5 text-center">
        <i class="bi bi-receipt display-1 text-primary-var-50 mb-3"></i>
        <h4 class="text-primary-var">No purchases yet</h4>
        <p class="text-muted mb-4">
          When you buy games, your receipt and transaction details will appear here.
        </p>
        <router-link to="/games" class="btn gd-btn-primary px-4 py-2">
          Browse Games
        </router-link>
      </div>

      <div v-else class="gd-glass-card overflow-hidden">
        <div class="table-responsive">
          <table class="table table-dark table-hover mb-0 align-middle gd-table">
            <thead>
              <tr>
                <th scope="col" class="text-uppercase text-muted fw-bold small py-3 ps-4">Game</th>
                <th scope="col" class="text-uppercase text-muted fw-bold small py-3">Date</th>
                <th scope="col" class="text-uppercase text-muted fw-bold small py-3">Transaction ID</th>
                <th scope="col" class="text-uppercase text-muted fw-bold small py-3 text-end pe-4">Amount</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="purchase in purchases" :key="purchase.id">
                <td class="ps-4 py-3">
                  <div class="d-flex align-items-center gap-3">
                    <img :src="purchase.thumbnail || '/placeholder.png'" class="game-thumbnail rounded" alt="Thumbnail" />
                    <span class="fw-bold text-white">{{ purchase.title }}</span>
                  </div>
                </td>
                <td class="py-3 text-light">{{ formatDate(purchase.createdAt) }}</td>
                <td class="py-3 text-muted font-monospace small">{{ purchase.transactionId || 'N/A' }}</td>
                <td class="py-3 text-end pe-4 fw-bold text-warning">${{ parseFloat(purchase.price).toFixed(2) }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.gd-glass-card {
  background: var(--bg-glass);
  border: 1px solid var(--border-glass);
  border-radius: 16px;
  backdrop-filter: blur(12px);
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.15);
}

.gd-table {
  background: transparent;
  --bs-table-bg: transparent;
  --bs-table-hover-bg: rgba(255, 255, 255, 0.05);
  --bs-table-border-color: rgba(255, 255, 255, 0.1);
}

.game-thumbnail {
  width: 60px;
  height: 34px;
  object-fit: cover;
}

.gd-btn-primary {
  background: linear-gradient(135deg, #7c3aed, #4aa3ff);
  color: white;
  border: none;
  border-radius: 12px;
  font-weight: 700;
  transition: transform 0.2s ease, box-shadow 0.2s ease, filter 0.2s ease;
}
.gd-btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(124, 58, 237, 0.4);
  filter: brightness(1.1);
  color: white;
}
</style>
