<script>
import { cartState } from "../services/cart";
import { auth, db } from "../firebase";
import { collection, addDoc, serverTimestamp } from "firebase/firestore";
import { onAuthStateChanged } from "firebase/auth";
import PayPalCheckout from "../components/PayPalCheckout.vue";

export default {
  name: "Checkout",
  components: {
    PayPalCheckout,
  },
  inject: ["toast"],

  data() {
    return {
      currentUser: null,
      processing: false,
    };
  },

  computed: {
    cart() {
      return cartState;
    },
  },

  beforeUnmount() {
    if (this.unsubscribe) {
      this.unsubscribe();
    }
  },

  mounted() {
    this.unsubscribe = onAuthStateChanged(auth, (user) => {
      this.currentUser = user;
    });
  },

  methods: {
    removeFromCart(id) {
      cartState.remove(id);
    },

    async handlePaymentSuccess(details) {
      if (!this.currentUser) {
        this.$router.push("/login");
        return;
      }

      this.processing = true;

      try {
        // Save each item as a purchase
        const batchPromises = this.cart.items.map((item) => {
          return addDoc(collection(db, "purchases"), {
            userId: this.currentUser.uid,
            gameId: item.id.toString(),
            title: item.name || item.title || "Unknown Game",
            thumbnail: item.thumbnail || item.background_image || "",
            price: parseFloat(item.price) || 0,
            currency: "USD",
            transactionId: details.transactionId || "N/A",
            payerName: details.payerName || "Anonymous",
            createdAt: serverTimestamp(),
            status: "completed",
          });
        });

        await Promise.all(batchPromises);

        this.toast?.show(
          "Payment Successful! Games added to your library.",
          "success"
        );
        cartState.clear();

        // Redirect to purchase history or library
        this.$router.push("/purchase-history");
      } catch (error) {
        console.error("Payment save failed:", error);
        this.toast?.show(
          "Payment succeeded, but failed to save to database.",
          "error"
        );
      } finally {
        this.processing = false;
      }
    },
  },
};
</script>

<template>
  <div class="checkout-page pt-5 pb-5">
    <div class="container">
      <div class="row g-5">
        <!-- Cart Items -->
        <div class="col-lg-7">
          <h2 class="text-primary-var fw-bold mb-4">
            Your Cart
            <span class="text-muted ms-2 fs-4">({{ cart.totalItems }})</span>
          </h2>

          <div
            v-if="cart.items.length === 0"
            class="gd-glass-card p-5 text-center"
          >
            <i class="bi bi-cart-x display-1 text-primary-var-50 mb-3"></i>
            <h4 class="text-primary-var">Your cart is empty</h4>
            <p class="text-muted mb-4">
              Looks like you haven't added any games yet.
            </p>
            <router-link to="/games" class="btn gd-btn-primary px-4 py-2"
              >Browse Games</router-link
            >
          </div>

          <div v-else class="cart-items-container">
            <div
              v-for="item in cart.items"
              :key="item.id"
              class="gd-glass-card mb-3 p-3 d-flex align-items-center gap-3 cart-item-anim"
            >
              <img
                :src="
                  item.thumbnail || item.background_image || '/placeholder.png'
                "
                class="cart-item-img rounded"
                alt="Game thumbnail"
              />
              <div class="flex-grow-1">
                <h5 class="text-primary-var mb-1">{{ item.name || item.title }}</h5>
                <span class="text-muted small">Digital Download</span>
              </div>
              <div class="text-end d-flex flex-column align-items-end gap-2">
                <div class="d-flex flex-column align-items-end">
                  <div v-if="item.originalPrice && item.originalPrice !== item.price" class="text-muted text-decoration-line-through small">
                    ${{ (parseFloat(item.originalPrice) || 0).toFixed(2) }}
                  </div>
                  <div class="text-primary-var fw-bold fs-5">
                    ${{ (parseFloat(item.price) || 0).toFixed(2) }}
                  </div>
                </div>
                <button
                  class="btn btn-outline-danger btn-sm px-3 rounded-pill"
                  @click="removeFromCart(item.id)"
                  aria-label="Remove item"
                >
                  <i class="bi bi-trash3 me-1"></i> Remove
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- Checkout Summary & Fake Payment -->
        <div class="col-lg-5">
          <div class="gd-glass-card p-4 checkout-summary">
            <h4 class="text-primary-var fw-bold mb-4">Order Summary</h4>

            <div class="d-flex justify-content-between mb-2">
              <span class="text-muted">Subtotal</span>
              <span class="text-primary-var">${{ cart.totalPrice.toFixed(2) }}</span>
            </div>
            <div
              class="d-flex justify-content-between mb-3 pb-3 border-bottom border-secondary border-opacity-50"
            >
              <span class="text-muted">Taxes</span>
              <span class="text-primary-var">$0.00</span>
            </div>
            <div class="d-flex justify-content-between mb-4">
              <strong class="text-primary-var fs-5">Total</strong>
              <strong class="text-warning fs-4"
                >${{ cart.totalPrice.toFixed(2) }}</strong
              >
            </div>

            <!-- PayPal Component -->
            <div v-if="cart.items.length > 0">
              <PayPalCheckout
                gameId="cart"
                title="GameHub Checkout"
                :price="cart.totalPrice"
                @payment-success="handlePaymentSuccess"
              />
            </div>

            <div v-else class="text-center py-4">
              <p class="text-muted">Add items to cart to checkout</p>
            </div>
          </div>
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

.cart-item-img {
  width: 120px;
  height: 68px;
  object-fit: cover;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.3);
}

.cart-item-anim {
  animation: fadeSlideRight 0.4s ease forwards;
}

@keyframes fadeSlideRight {
  from {
    opacity: 0;
    transform: translateX(-20px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

.gd-checkout-input {
  width: 100%;
  background: rgba(0, 0, 0, 0.2);
  border: 1px solid var(--border-glass);
  color: var(--text-primary);
  border-radius: 8px;
  padding: 12px 16px;
  transition: all 0.3s ease;
}
.gd-checkout-input:focus {
  outline: none;
  border-color: #7c3aed;
  background: rgba(0, 0, 0, 0.4);
  box-shadow: 0 0 0 3px rgba(124, 58, 237, 0.15);
}
.gd-checkout-input:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.letter-spacing-1 {
  letter-spacing: 0.05em;
}

.gd-btn-primary {
  background: linear-gradient(135deg, #7c3aed, #4aa3ff);
  color: white;
  border: none;
  border-radius: 12px;
  font-weight: 700;
  transition:
    transform 0.2s ease,
    box-shadow 0.2s ease,
    filter 0.2s ease;
}
.gd-btn-primary:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(124, 58, 237, 0.4);
  filter: brightness(1.1);
  color: white;
}
.gd-btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

.btn-icon-danger {
  background: transparent;
  border: none;
  color: #ef4444;
  width: 36px;
  height: 36px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
}
.btn-icon-danger:hover {
  background: rgba(239, 68, 68, 0.15);
  box-shadow: 0 4px 12px rgba(239, 68, 68, 0.2);
  transform: scale(1.1);
}

.checkout-summary {
  position: sticky;
  top: 100px;
}
</style>
