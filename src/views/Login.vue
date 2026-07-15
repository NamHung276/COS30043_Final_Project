<script>
import { auth } from "../firebase";
import { signInWithEmailAndPassword } from "firebase/auth";

export default {
  data() {
    return {
      email: "",
      password: "",
      showPassword: false,
      error: "",
      loading: false,
    };
  },

  methods: {
    async login() {
      this.error = "";
      this.loading = true;

      try {
        await signInWithEmailAndPassword(auth, this.email, this.password);
        this.$router.push("/");
      } catch (error) {
        if (
          error.code === "auth/invalid-credential" ||
          error.code === "auth/wrong-password" ||
          error.code === "auth/user-not-found"
        ) {
          this.error = "Invalid email or password.";
        } else if (error.code === "auth/invalid-email") {
          this.error = "Invalid email address.";
        } else if (error.code === "auth/too-many-requests") {
          this.error = "Too many attempts. Please try again later.";
        } else {
          this.error = "Login failed. Please try again.";
        }
        console.error(error);
      } finally {
        this.loading = false;
      }
    },
  },
};
</script>

<template>
  <div class="auth-page">
    <!-- Ambient background -->
    <div class="auth-bg">
      <div class="auth-orb auth-orb-1"></div>
      <div class="auth-orb auth-orb-2"></div>
      <div class="auth-orb auth-orb-3"></div>
      <div class="auth-grid"></div>
    </div>

    <div class="auth-container">
      <!-- Brand -->
      <div class="auth-brand">
        <router-link to="/" class="auth-logo-link">
          <img src="/logo/gamepad.svg" width="24" height="24" alt="" aria-hidden="true" />
          <span>GameHub</span>
        </router-link>
      </div>

      <!-- Card -->
      <div class="auth-card">
        <div class="auth-card-header">
          <h1 class="auth-title">Welcome back</h1>
          <p class="auth-subtitle">Sign in to your account to continue</p>
        </div>

        <div v-if="error" class="auth-error">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
          {{ error }}
        </div>

        <form @submit.prevent="login" class="auth-form">
          <div class="auth-field">
            <label for="login-email" class="auth-label">Email</label>
            <div class="auth-input-wrapper">
              <svg class="auth-input-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/><polyline points="22,6 12,13 2,6"/></svg>
              <input
                id="login-email"
                v-model="email"
                type="email"
                class="auth-input"
                placeholder="your@email.com"
                required
                autocomplete="email"
              />
            </div>
          </div>

          <div class="auth-field">
            <label for="login-password" class="auth-label">Password</label>
            <div class="auth-input-wrapper">
              <svg class="auth-input-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><rect x="3" y="11" width="18" height="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0110 0v4"/></svg>
              <input
                id="login-password"
                v-model="password"
                :type="showPassword ? 'text' : 'password'"
                class="auth-input"
                placeholder="Enter your password"
                required
                autocomplete="current-password"
              />
              <button
                type="button"
                class="auth-eye-btn"
                @click="showPassword = !showPassword"
                :aria-label="showPassword ? 'Hide password' : 'Show password'"
              >
                <svg v-if="!showPassword" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>
                <svg v-else width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M17.94 17.94A10.07 10.07 0 0112 20c-7 0-11-8-11-8a18.45 18.45 0 015.06-5.94"/><path d="M9.9 4.24A9.12 9.12 0 0112 4c7 0 11 8 11 8a18.5 18.5 0 01-2.16 3.19"/><line x1="1" y1="1" x2="23" y2="23"/></svg>
              </button>
            </div>
          </div>

          <button
            id="login-submit-btn"
            type="submit"
            class="auth-submit-btn"
            :disabled="loading"
          >
            <span v-if="loading" class="auth-spinner"></span>
            <template v-else>
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" aria-hidden="true"><path d="M15 3h4a2 2 0 012 2v14a2 2 0 01-2 2h-4"/><polyline points="10 17 15 12 10 7"/><line x1="15" y1="12" x2="3" y2="12"/></svg>
              Sign In
            </template>
          </button>
        </form>

        <p class="auth-switch">
          New to GameHub?
          <router-link to="/register">Create a free account →</router-link>
        </p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.auth-page {
  min-height: calc(100vh - 60px);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
  position: relative;
  overflow: hidden;
}

.auth-bg {
  position: absolute;
  inset: 0;
  z-index: 0;
}

.auth-orb {
  position: absolute;
  border-radius: 50%;
  filter: blur(80px);
  opacity: 0.35;
}

.auth-orb-1 {
  width: 500px;
  height: 500px;
  background: radial-gradient(circle, #0ea5e9, transparent 70%);
  top: -200px;
  left: -100px;
  animation: orb-drift 8s ease-in-out infinite alternate;
}

.auth-orb-2 {
  width: 400px;
  height: 400px;
  background: radial-gradient(circle, #8b5cf6, transparent 70%);
  bottom: -150px;
  right: -100px;
  animation: orb-drift 10s ease-in-out infinite alternate-reverse;
}

.auth-orb-3 {
  width: 300px;
  height: 300px;
  background: radial-gradient(circle, #d946ef, transparent 70%);
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  opacity: 0.15;
  animation: orb-pulse 6s ease-in-out infinite;
}

@keyframes orb-drift {
  from { transform: translate(0, 0); }
  to { transform: translate(30px, 20px); }
}

@keyframes orb-pulse {
  0%, 100% { opacity: 0.1; transform: translate(-50%, -50%) scale(1); }
  50% { opacity: 0.2; transform: translate(-50%, -50%) scale(1.1); }
}

.auth-grid {
  position: absolute;
  inset: 0;
  background-image:
    linear-gradient(var(--border-subtle) 1px, transparent 1px),
    linear-gradient(90deg, var(--border-subtle) 1px, transparent 1px);
  background-size: 50px 50px;
}

.auth-container {
  position: relative;
  z-index: 1;
  width: 100%;
  max-width: 420px;
}

.auth-brand {
  text-align: center;
  margin-bottom: 28px;
}

.auth-logo-link {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  font-family: var(--font-display);
  font-size: 1.4rem;
  font-weight: 800;
  color: var(--primary);
  text-decoration: none;
  transition: opacity 0.2s;
}

.auth-logo-link:hover {
  opacity: 0.85;
  color: var(--primary);
}

.auth-logo-link img {
  filter: brightness(1.3);
}

.auth-card {
  background: var(--bg-glass);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid var(--border-glass);
  border-radius: 20px;
  padding: 36px 32px;
  box-shadow: 0 25px 60px rgba(0, 0, 0, 0.5), 0 0 0 1px var(--border-subtle) inset;
}

.auth-card-header {
  margin-bottom: 28px;
}

.auth-title {
  font-size: 1.6rem;
  font-weight: 800;
  color: var(--text-primary);
  margin-bottom: 6px;
}

.auth-subtitle {
  font-size: 0.9rem;
  color: var(--text-muted);
  margin: 0;
}

.auth-error {
  display: flex;
  align-items: center;
  gap: 8px;
  background: rgba(244, 63, 94, 0.12);
  border: 1px solid rgba(244, 63, 94, 0.3);
  border-radius: 10px;
  color: #fca5a5;
  font-size: 0.85rem;
  padding: 12px 14px;
  margin-bottom: 20px;
}

.auth-form {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.auth-field {
  display: flex;
  flex-direction: column;
  gap: 7px;
}

.auth-label {
  font-size: 0.83rem;
  font-weight: 600;
  color: var(--text-secondary);
  letter-spacing: 0.02em;
}

.auth-input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.auth-input-icon {
  position: absolute;
  left: 14px;
  color: var(--text-muted);
  pointer-events: none;
  z-index: 1;
}

.auth-input {
  width: 100%;
  background: var(--bg-surface);
  border: 1px solid var(--border-subtle);
  border-radius: 10px;
  color: var(--text-primary);
  font-family: var(--font-family);
  font-size: 0.9rem;
  padding: 11px 14px 11px 42px;
  outline: none;
  transition: all 0.2s ease;
}

.auth-input:focus {
  border-color: var(--primary);
  background: rgba(14, 165, 233, 0.06);
  box-shadow: 0 0 0 3px rgba(14, 165, 233, 0.12);
}

.auth-input::placeholder {
  color: var(--text-muted);
}

.auth-eye-btn {
  position: absolute;
  right: 12px;
  background: transparent;
  border: none;
  color: var(--text-muted);
  cursor: pointer;
  padding: 4px;
  display: flex;
  align-items: center;
  transition: color 0.2s;
}

.auth-eye-btn:hover {
  color: var(--text-primary);
}

.auth-submit-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  width: 100%;
  background: linear-gradient(135deg, var(--primary), #8b5cf6);
  border: none;
  border-radius: 10px;
  color: #fff;
  font-family: var(--font-display);
  font-size: 0.95rem;
  font-weight: 700;
  padding: 13px 20px;
  cursor: pointer;
  transition: all 0.25s ease;
  margin-top: 4px;
  letter-spacing: 0.02em;
}

.auth-submit-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(14, 165, 233, 0.35);
  filter: brightness(1.08);
}

.auth-submit-btn:active:not(:disabled) {
  transform: translateY(0);
}

.auth-submit-btn:disabled {
  opacity: 0.65;
  cursor: not-allowed;
}

.auth-spinner {
  width: 18px;
  height: 18px;
  border: 2px solid rgba(255,255,255,0.3);
  border-top-color: #fff;
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.auth-switch {
  text-align: center;
  margin: 22px 0 0;
  font-size: 0.875rem;
  color: var(--text-muted);
}

.auth-switch a {
  color: var(--primary-light);
  font-weight: 600;
  text-decoration: none;
  transition: color 0.2s;
}

.auth-switch a:hover {
  color: var(--primary);
}

</style>
