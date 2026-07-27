<script>
export default {
  name: "CheckoutSuccess",
  computed: {
    count() {
      return parseInt(this.$route.query.count) || 1;
    },
  },
};
</script>

<template>
  <div class="cs-page">
    <div class="cs-bg">
      <div class="cs-orb cs-orb-1"></div>
      <div class="cs-orb cs-orb-2"></div>
    </div>

    <div class="cs-content">
      <!-- Success icon -->
      <div class="cs-icon-ring">
        <div class="cs-icon-pulse"></div>
        <svg class="cs-check-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" aria-hidden="true">
          <polyline points="20 6 9 17 4 12"/>
        </svg>
      </div>

      <h1 class="cs-title">Payment Successful!</h1>
      <p class="cs-sub">
        {{ count }} {{ count === 1 ? 'game has' : 'games have' }} been added to your Library.
        They're ready to play right now.
      </p>

      <div class="cs-receipt">
        <div class="cs-receipt-row">
          <span class="text-muted">Status</span>
          <span class="cs-status-badge">Confirmed</span>
        </div>
        <div class="cs-receipt-row">
          <span class="text-muted">Games Added</span>
          <span class="text-white fw-bold">{{ count }}</span>
        </div>
        <div class="cs-receipt-row">
          <span class="text-muted">Available</span>
          <span class="text-success fw-bold">Immediately</span>
        </div>
      </div>

      <div class="cs-actions">
        <router-link to="/library" class="cs-btn-primary">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" aria-hidden="true">
            <rect x="2" y="3" width="20" height="14" rx="2"/><line x1="8" y1="21" x2="16" y2="21"/><line x1="12" y1="17" x2="12" y2="21"/>
          </svg>
          Open My Library
        </router-link>
        <router-link to="/games" class="cs-btn-secondary">Continue Shopping</router-link>
      </div>
    </div>
  </div>
</template>

<style scoped>
.cs-page {
  min-height: calc(100vh - 70px);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
  position: relative;
  overflow: hidden;
}
.cs-bg {
  position: absolute;
  inset: 0;
  z-index: 0;
  pointer-events: none;
}
.cs-orb {
  position: absolute;
  border-radius: 50%;
  filter: blur(80px);
  opacity: 0.2;
}
.cs-orb-1 {
  width: 500px;
  height: 500px;
  background: radial-gradient(circle, #10b981, transparent);
  top: -100px;
  right: -100px;
  animation: orbFloat 8s ease-in-out infinite;
}
.cs-orb-2 {
  width: 400px;
  height: 400px;
  background: radial-gradient(circle, #0ea5e9, transparent);
  bottom: -80px;
  left: -100px;
  animation: orbFloat 10s ease-in-out infinite reverse;
}
@keyframes orbFloat {
  0%, 100% { transform: translateY(0px); }
  50% { transform: translateY(-30px); }
}
.cs-content {
  position: relative;
  z-index: 1;
  text-align: center;
  max-width: 460px;
  width: 100%;
}
.cs-icon-ring {
  width: 90px;
  height: 90px;
  border-radius: 50%;
  background: rgba(16, 185, 129, 0.12);
  border: 2px solid rgba(16, 185, 129, 0.4);
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 28px;
  position: relative;
}
.cs-icon-pulse {
  position: absolute;
  inset: -8px;
  border-radius: 50%;
  background: transparent;
  border: 2px solid rgba(16, 185, 129, 0.2);
  animation: pulse 2s ease-out infinite;
}
@keyframes pulse {
  0% { transform: scale(1); opacity: 1; }
  100% { transform: scale(1.4); opacity: 0; }
}
.cs-check-icon {
  width: 40px;
  height: 40px;
  stroke: #10b981;
  stroke-dasharray: 40;
  stroke-dashoffset: 40;
  animation: drawCheck 0.6s ease-out 0.2s forwards;
}
@keyframes drawCheck {
  to { stroke-dashoffset: 0; }
}
.cs-title {
  font-size: 2rem;
  font-weight: 800;
  color: var(--text-primary);
  margin: 0 0 12px;
}
.cs-sub {
  color: var(--text-secondary);
  font-size: 1rem;
  line-height: 1.6;
  margin: 0 0 28px;
}
.cs-receipt {
  background: rgba(255,255,255,0.04);
  border: 1px solid rgba(255,255,255,0.08);
  border-radius: 16px;
  padding: 20px 24px;
  margin-bottom: 28px;
  display: flex;
  flex-direction: column;
  gap: 14px;
}
.cs-receipt-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.9rem;
}
.cs-status-badge {
  background: rgba(16,185,129,0.15);
  color: #10b981;
  border: 1px solid rgba(16,185,129,0.3);
  padding: 3px 12px;
  border-radius: 50px;
  font-size: 0.8rem;
  font-weight: 600;
}
.cs-actions {
  display: flex;
  gap: 12px;
  justify-content: center;
  flex-wrap: wrap;
}
.cs-btn-primary {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 13px 28px;
  background: linear-gradient(135deg, #10b981, #059669);
  color: #fff;
  border-radius: 50px;
  font-weight: 700;
  text-decoration: none;
  font-size: 0.95rem;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}
.cs-btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(16, 185, 129, 0.4);
  color: #fff;
}
.cs-btn-secondary {
  display: inline-flex;
  align-items: center;
  padding: 13px 28px;
  background: rgba(255,255,255,0.06);
  color: var(--text-primary);
  border: 1px solid rgba(255,255,255,0.1);
  border-radius: 50px;
  font-weight: 600;
  text-decoration: none;
  font-size: 0.95rem;
  transition: background 0.2s ease, transform 0.2s ease;
}
.cs-btn-secondary:hover {
  background: rgba(255,255,255,0.12);
  transform: translateY(-2px);
  color: var(--text-primary);
}
</style>
