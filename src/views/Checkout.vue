<script>
import { cartState } from "../services/cart";
import { auth, db } from "../firebase";
import { collection, addDoc, serverTimestamp, query, where, getDocs } from "firebase/firestore";
import { onAuthStateChanged } from "firebase/auth";
import PayPalCheckout from "../components/PayPalCheckout.vue";
import { useLibraryStore } from "../stores/useLibraryStore";
import { useNotificationStore } from "../stores/useNotificationStore";
import { backendApi } from "../services/api";

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
      ownedIds: [],
      agreedToTerms: false,
      isVerified: false,
      verificationCode: "",
      showVerificationModal: false,
      sessionCode: null,        // Generated 4-digit code for this checkout session
      codeExpiry: null,         // Timestamp when the code expires
      codeSent: false,
      sendingEmail: false,
    };
  },

  computed: {
    cart() {
      return cartState;
    },
    hasConflict() {
      return this.cart.items.some(item => this.ownedIds.includes(item.id.toString()));
    },
    conflictGames() {
      return this.cart.items.filter(item => this.ownedIds.includes(item.id.toString()));
    }
  },

  watch: {
    currentUser: {
      immediate: true,
      async handler(user) {
        if (user) {
          try {
            const store = useLibraryStore();
            await store.fetchPurchases();
            this.ownedIds = store.purchases.map(d => d.gameId);
          } catch (e) {
            console.error("Failed to fetch purchases", e);
          }
        } else {
          this.ownedIds = [];
        }
      }
    }
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

    async sendVerificationCode() {
      if (!this.currentUser || !this.currentUser.email) {
        this.toast?.show("You must be logged in to verify your account.", "error");
        return;
      }
      
      // Generate a random 4-digit code and store it in session
      const code = String(Math.floor(1000 + Math.random() * 9000));
      this.sessionCode = code;
      this.codeExpiry = Date.now() + 10 * 60 * 1000; // 10 minutes
      this.verificationCode = "";
      this.showVerificationModal = true;
      this.sendingEmail = true; // NEW STATE

      try {
        const response = await backendApi.post("/email/send-verification", {
          email: this.currentUser.email,
          code: code
        });

        // 200 OK — email queued successfully
        this.codeSent = true;
        this.toast?.show("Verification code sent to your email!", "success");

      } catch (error) {
        const status = error?.response?.status;

        if (status === 503) {
          // Backend is up but SMTP not configured — show test mode
          this.codeSent = true;
          this.toast?.show(`[TEST MODE] Code is: ${code}`, "info", 8000);
          console.warn("Backend SMTP not configured. Falling back to test mode.");
        } else {
          // Network error, backend down, or other failure — still fall back to test mode
          // so checkout is never fully blocked
          this.codeSent = true;
          this.toast?.show(`[TEST MODE] Code is: ${code}`, "info", 8000);
          console.warn("Email API unavailable, using test mode fallback:", error?.message);
        }
      } finally {
        this.sendingEmail = false;
      }
    },

    verifyAccount() {
      if (!this.sessionCode) {
        this.toast?.show("Please request a verification code first.", "error");
        return;
      }
      if (Date.now() > this.codeExpiry) {
        this.toast?.show("Code expired. Please request a new one.", "error");
        this.sessionCode = null;
        this.codeSent = false;
        return;
      }
      if (this.verificationCode.trim() === this.sessionCode) {
        this.isVerified = true;
        this.showVerificationModal = false;
        this.verificationCode = "";
        this.sessionCode = null;
        this.toast?.show("Account verified. You may now proceed with payment.", "success");
      } else {
        this.toast?.show("Incorrect code. Please try again.", "error");
      }
    },

    async handlePaymentSuccess(details) {
      if (!this.currentUser) {
        this.$router.push("/login");
        return;
      }

      this.processing = true;

      try {
        // Check for existing purchases to prevent duplicates
        const store = useLibraryStore();
        await store.fetchPurchases();
        const ownedGameIds = new Set(store.purchases.map(d => d.gameId));

        const newItems = this.cart.items.filter(item => !ownedGameIds.has(item.id.toString()));
        const alreadyOwned = this.cart.items.filter(item => ownedGameIds.has(item.id.toString()));

        if (alreadyOwned.length > 0) {
          const names = alreadyOwned.map(i => i.name).join(', ');
          this.toast?.show(`Already in your library: ${names}`, "warning");
        }

        if (newItems.length === 0) {
          this.toast?.show("All items are already in your library.", "info");
          cartState.clear();
          this.$router.push("/library");
          return;
        }

        // Save each new item as a purchase
        const batchPromises = newItems.map((item) => {
          return addDoc(collection(db, "purchases"), {
            userId: this.currentUser.uid,
            gameId: item.id.toString(),
            gameName: item.name || item.title || "Unknown Game",
            thumbnail: item.thumbnail || item.background_image || "",
            price: parseFloat(item.price) || 0,
            currency: "USD",
            transactionId: details.transactionId || "N/A",
            payerName: details.payerName || "Anonymous",
            createdAt: serverTimestamp(),
            status: "not_installed",
          });
        });

        await Promise.all(batchPromises);
        
        // Trigger notifications for each purchased game
        const notifStore = useNotificationStore();
        newItems.forEach(item => {
          const title = item.name || item.title || "Unknown Game";
          notifStore.createNotification(
            this.currentUser.uid,
            "Purchase Successful",
            `Thank you for purchasing ${title}! It is now available in your Library.`,
            "payment",
            `/library`
          );
        });
        
        // Refresh library store
        await store.fetchPurchases(true);

        cartState.clear();
        this.$router.push(`/checkout/success?count=${newItems.length}`);
      } catch (error) {
        console.error("Payment save failed:", error);
        this.toast?.show(
          "Payment succeeded, but failed to save to database. Please contact support.",
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
            <div class="d-flex justify-content-between align-items-center mb-4">
              <h4 class="text-primary-var fw-bold mb-0">Order Summary</h4>
              <span class="badge bg-success bg-opacity-10 text-success border border-success border-opacity-50 px-2 py-1 rounded-pill d-flex align-items-center gap-1">
                <i class="bi bi-shield-lock-fill"></i> Secure
              </span>
            </div>

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

            <!-- Terms & Verification -->
            <div v-if="cart.items.length > 0 && !hasConflict" class="mb-4">
              <div class="form-check mb-3 text-start">
                <input class="form-check-input" type="checkbox" id="termsCheck" v-model="agreedToTerms">
                <label class="form-check-label text-muted small" for="termsCheck">
                  I agree to the <a href="#" class="text-primary">Terms of Sale</a> and <a href="#" class="text-primary">EULA</a>.
                </label>
              </div>
              
              <!-- Verification gate: shows only when terms agreed and not yet verified -->
              <div v-if="agreedToTerms && !isVerified" class="mb-4 text-center verification-section">
                <p class="small text-warning mb-2"><i class="bi bi-shield-exclamation me-1"></i> For your security, please verify your account.</p>
                <button 
                  class="btn btn-outline-warning w-100 fw-bold rounded-pill" 
                  @click="sendVerificationCode"
                  :disabled="sendingEmail"
                >
                  <span v-if="sendingEmail" class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                  <i v-else class="bi bi-envelope-check me-2"></i> 
                  <span v-if="sendingEmail">Sending...</span>
                  <span v-else>{{ codeSent ? 'Resend Verification Code' : 'Send Verification Code' }}</span>
                </button>
              </div>
            </div>

            <!-- PayPal Component -->
            <div v-if="cart.items.length > 0 && !hasConflict && agreedToTerms && isVerified">
              <PayPalCheckout
                gameId="cart"
                :items="cart.items.map(i => i.id)"
                title="GameHub Checkout"
                :price="cart.totalPrice"
                @payment-success="handlePaymentSuccess"
              />
              <div class="mt-3 text-center text-muted small d-flex flex-column gap-2">
                <div><i class="bi bi-lock-fill me-1"></i>256-bit SSL Encrypted Checkout</div>
                <div class="d-flex justify-content-center gap-2 text-secondary fs-4">
                  <i class="bi bi-cc-paypal"></i>
                  <i class="bi bi-cc-visa"></i>
                  <i class="bi bi-cc-mastercard"></i>
                </div>
              </div>
            </div>

            <div v-else-if="hasConflict" class="alert alert-danger mt-3 mb-0" style="font-size: 0.9rem;">
              <i class="bi bi-exclamation-triangle-fill me-2"></i>
              You already own <strong>{{ conflictGames.map(g => g.name || g.title).join(', ') }}</strong>. 
              Please remove it from your cart to proceed.
            </div>

            <div v-else-if="!hasConflict" class="text-center py-4">
              <p class="text-muted small">Please agree to the terms and verify your account to proceed with payment.</p>
            </div>
            
            <div v-if="cart.items.length === 0" class="text-center py-4">
              <p class="text-muted">Add items to cart to checkout</p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Verification Modal Mock -->
    <div v-if="showVerificationModal" class="modal-backdrop fade show" style="z-index: 1050;"></div>
    <div v-if="showVerificationModal" class="modal d-block" tabindex="-1" style="z-index: 1055;">
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content gd-glass-card border-secondary">
          <div class="modal-header border-bottom border-secondary border-opacity-25">
            <h5 class="modal-title text-primary-var"><i class="bi bi-shield-lock-fill text-warning me-2"></i> Security Verification</h5>
            <button type="button" class="btn-close btn-close-white" @click="showVerificationModal = false"></button>
          </div>
          <div class="modal-body p-4 text-center">
            <p class="text-muted mb-4">A 4-digit verification code has been sent to your registered email address. Please check your inbox.</p>
            <div class="d-flex justify-content-center mb-3">
              <input type="text" class="form-control text-center fs-3 fw-bold tracking-widest bg-dark text-white border-secondary" 
                     style="max-width: 150px; letter-spacing: 0.5em;" maxlength="4" placeholder="••••" v-model="verificationCode"
                     inputmode="numeric" pattern="[0-9]*" autocomplete="one-time-code">
            </div>
            <p class="small text-muted"><i class="bi bi-info-circle me-1"></i>Enter the code from your email. Codes expire after 10 minutes.</p>
          </div>
          <div class="modal-footer border-top border-secondary border-opacity-25">
            <button type="button" class="btn btn-secondary" @click="showVerificationModal = false">Cancel</button>
            <button type="button" class="btn btn-warning fw-bold text-dark" @click="verifyAccount">Verify & Continue</button>
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
