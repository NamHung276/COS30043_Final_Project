<script>
export default {
  name: "PayPalCheckout",
  props: {
    gameId: {
      type: String,
      required: true,
    },
    title: {
      type: String,
      required: true,
    },
    price: {
      type: Number,
      required: true,
    },
  },
  data() {
    return {
      scriptLoaded: false,
      error: null,
    };
  },
  mounted() {
    this.loadPayPalScript();
  },
  methods: {
    loadPayPalScript() {
      if (window.paypal) {
        this.scriptLoaded = true;
        this.renderButton();
        return;
      }
      
      const script = document.createElement("script");
      script.src = `https://www.paypal.com/sdk/js?client-id=${import.meta.env.VITE_PAYPAL_CLIENT_ID}&currency=USD`;
      script.addEventListener("load", () => {
        this.scriptLoaded = true;
        this.renderButton();
      });
      script.addEventListener("error", () => {
        this.error = "Failed to load PayPal SDK.";
      });
      document.body.appendChild(script);
    },
    renderButton() {
      window.paypal.Buttons({
        createOrder: async () => {
          try {
            const response = await fetch("http://localhost:8000/api/paypal/create-order", {
              method: "POST",
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify({
                gameId: this.gameId,
                title: this.title,
                price: this.price,
              }),
            });
            const data = await response.json();
            if (data.orderId) {
              return data.orderId;
            } else {
              throw new Error("No order ID returned");
            }
          } catch (err) {
            console.error("Create Order Error:", err);
            this.error = "Failed to create order.";
          }
        },
        onApprove: async (data) => {
          try {
            const response = await fetch("http://localhost:8000/api/paypal/capture-order", {
              method: "POST",
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify({
                orderId: data.orderID,
              }),
            });
            const captureData = await response.json();
            
            if (captureData.success) {
              this.$emit("payment-success", {
                transactionId: captureData.transaction_id,
                payerName: captureData.payer,
                amount: captureData.amount,
              });
            } else {
              this.error = "Payment capture failed.";
            }
          } catch (err) {
            console.error("Capture Order Error:", err);
            this.error = "Failed to capture payment.";
          }
        },
        onError: (err) => {
          console.error("PayPal Error:", err);
          this.error = "An error occurred with PayPal.";
        }
      }).render(this.$refs.paypalButtonContainer);
    },
  },
};
</script>

<template>
  <div class="paypal-checkout-container p-4 rounded border border-secondary border-opacity-50">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h4 class="mb-0 fw-bold text-primary-var">Buy Now</h4>
      <span class="badge bg-warning text-dark px-3 py-2 rounded-pill fw-bold">
        <i class="bi bi-shield-check me-1"></i> Sandbox
      </span>
    </div>
    
    <p class="text-muted mb-4">
      Pay securely with PayPal. This is a sandbox environment, no real money will be charged.
    </p>

    <div v-if="error" class="alert alert-danger" role="alert">
      {{ error }}
    </div>

    <div ref="paypalButtonContainer" class="paypal-button-wrapper w-100"></div>
    
    <div v-if="!scriptLoaded && !error" class="text-center text-muted py-3">
      <div class="spinner-border spinner-border-sm me-2" role="status"></div>
      Loading PayPal...
    </div>
  </div>
</template>

<style scoped>
.paypal-checkout-container {
  background: var(--bg-glass);
  backdrop-filter: blur(12px);
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.15);
}
.paypal-button-wrapper {
  min-height: 150px;
  position: relative;
  z-index: 1; /* Ensure button is clickable over glass effects */
}
</style>
