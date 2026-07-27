<script>
export default {
  name: "NotFound",
};
</script>

<template>
  <div class="nf-page">
    <div class="nf-bg">
      <div class="nf-orb nf-orb-1"></div>
      <div class="nf-orb nf-orb-2"></div>
    </div>

    <div class="nf-content">
      <div class="nf-code">404</div>
      <h1 class="nf-title">Page Not Found</h1>
      <p class="nf-sub">
        This page has gone offline. Maybe it's a glitch in the simulation,
        or perhaps this level hasn't loaded yet.
      </p>

      <div class="nf-actions">
        <router-link to="/" class="nf-btn-primary">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" aria-hidden="true">
            <path d="M3 9l9-7 9 7v11a2 2 0 01-2 2H5a2 2 0 01-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/>
          </svg>
          Back to Home
        </router-link>
        <router-link to="/games" class="nf-btn-secondary">Browse Games</router-link>
      </div>
    </div>
  </div>
</template>

<style scoped>
.nf-page {
  min-height: calc(100vh - 70px);
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  overflow: hidden;
  padding: 40px 20px;
}
.nf-bg {
  position: absolute;
  inset: 0;
  z-index: 0;
  pointer-events: none;
}
.nf-orb {
  position: absolute;
  border-radius: 50%;
  filter: blur(80px);
  opacity: 0.15;
}
.nf-orb-1 {
  width: 500px;
  height: 500px;
  background: radial-gradient(circle, #8b5cf6, transparent);
  top: -100px;
  left: -150px;
  animation: orbFloat 8s ease-in-out infinite;
}
.nf-orb-2 {
  width: 400px;
  height: 400px;
  background: radial-gradient(circle, #0ea5e9, transparent);
  bottom: -80px;
  right: -100px;
  animation: orbFloat 10s ease-in-out infinite reverse;
}
@keyframes orbFloat {
  0%, 100% { transform: translateY(0px); }
  50% { transform: translateY(-30px); }
}
.nf-content {
  position: relative;
  z-index: 1;
  text-align: center;
  max-width: 500px;
}
.nf-code {
  font-family: 'Chakra Petch', 'Courier New', monospace;
  font-size: clamp(100px, 20vw, 160px);
  font-weight: 900;
  line-height: 1;
  background: linear-gradient(135deg, #8b5cf6, #0ea5e9);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  letter-spacing: -0.02em;
  animation: glitch 4s infinite;
}
@keyframes glitch {
  0%, 92%, 100% { transform: none; filter: none; }
  93% { transform: skewX(5deg); filter: hue-rotate(30deg); }
  94% { transform: skewX(-3deg); filter: hue-rotate(-30deg); }
  95% { transform: none; }
}
.nf-title {
  font-size: 1.8rem;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0 0 12px;
}
.nf-sub {
  color: var(--text-secondary);
  font-size: 1rem;
  line-height: 1.6;
  margin: 0 0 32px;
}
.nf-actions {
  display: flex;
  gap: 12px;
  justify-content: center;
  flex-wrap: wrap;
}
.nf-btn-primary {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 12px 24px;
  background: linear-gradient(135deg, #8b5cf6, #0ea5e9);
  color: #fff;
  border-radius: 50px;
  font-weight: 600;
  text-decoration: none;
  font-size: 0.95rem;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}
.nf-btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(139, 92, 246, 0.4);
  color: #fff;
}
.nf-btn-secondary {
  display: inline-flex;
  align-items: center;
  padding: 12px 24px;
  background: rgba(255,255,255,0.06);
  color: var(--text-primary);
  border: 1px solid rgba(255,255,255,0.1);
  border-radius: 50px;
  font-weight: 600;
  text-decoration: none;
  font-size: 0.95rem;
  transition: background 0.2s ease, transform 0.2s ease;
}
.nf-btn-secondary:hover {
  background: rgba(255,255,255,0.12);
  transform: translateY(-2px);
  color: var(--text-primary);
}
</style>
