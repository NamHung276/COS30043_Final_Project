<script>
import { auth, db } from "../firebase";
import { createUserWithEmailAndPassword, updateProfile, sendEmailVerification } from "firebase/auth";
import { doc, setDoc, serverTimestamp } from "firebase/firestore";
import { useAuthStore } from "../stores/useAuthStore";

export default {
  data() {
    return {
      name: "",
      email: "",
      password: "",
      confirmPassword: "",
      error: "",
      success: "",
      loading: false,
      googleLoading: false,
      googleError: "",
      touched: {
        name: false,
        email: false,
        password: false,
        confirmPassword: false,
      },
    };
  },

  computed: {
    nameError() {
      if (!this.touched.name) return "";
      if (!this.name) return "Name is required.";
      if (this.name.length < 2) return "Name must be at least 2 characters.";
      return "";
    },

    emailError() {
      if (!this.touched.email) return "";
      if (!this.email) return "Email is required.";
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      if (!emailRegex.test(this.email)) return "Please enter a valid email.";
      return "";
    },

    passwordError() {
      if (!this.touched.password) return "";
      if (!this.password) return "Password is required.";
      if (this.password.length < 6)
        return "Password must be at least 6 characters.";
      return "";
    },

    confirmPasswordError() {
      if (!this.touched.confirmPassword) return "";
      if (!this.confirmPassword) return "Please confirm your password.";
      if (this.password !== this.confirmPassword)
        return "Passwords do not match.";
      return "";
    },

    isFormValid() {
      return (
        !this.nameError &&
        !this.emailError &&
        !this.passwordError &&
        !this.confirmPasswordError &&
        this.name &&
        this.email &&
        this.password &&
        this.confirmPassword
      );
    },

    passwordStrength() {
      if (!this.password) return 0;
      let strength = 0;
      if (this.password.length >= 6) strength++;
      if (this.password.length >= 8) strength++;
      if (/[A-Z]/.test(this.password)) strength++;
      if (/[0-9]/.test(this.password)) strength++;
      if (/[^A-Za-z0-9]/.test(this.password)) strength++;
      return strength;
    },

    strengthLabel() {
      const labels = ["", "Weak", "Fair", "Good", "Strong", "Very Strong"];
      return labels[this.passwordStrength] || "";
    },

    strengthColor() {
      const colors = [
        "",
        "#ef4444",
        "#f59e0b",
        "#eab308",
        "#22c55e",
        "#06b6d4",
      ];
      return colors[this.passwordStrength] || "";
    },
  },

  methods: {
    touch(field) {
      this.touched[field] = true;
    },

    async register() {
      // Touch all fields to show all errors at once
      Object.keys(this.touched).forEach(
        (field) => (this.touched[field] = true),
      );

      this.error = "";
      this.success = "";

      if (!this.isFormValid) return;

      this.loading = true;

      try {
        const userCredential = await createUserWithEmailAndPassword(
          auth,
          this.email,
          this.password,
        );

        // Save the display name on the Firebase user profile
        await updateProfile(userCredential.user, {
          displayName: this.name,
        });

        // Create a Firestore user document with default role 'user'
        // Wrapped separately so a Firestore rules error doesn't mask
        // the successful account creation
        try {
          await setDoc(doc(db, "users", userCredential.user.uid), {
            displayName: this.name.trim(),
            email: this.email.trim().toLowerCase(),
            role: "user",
            createdAt: serverTimestamp(),
          });
        } catch (firestoreErr) {
          console.warn(
            "Account created but Firestore user doc failed (check security rules):",
            firestoreErr,
          );
        }

        // Send Email Verification
        try {
          await sendEmailVerification(userCredential.user);
        } catch (emailErr) {
          console.warn("Failed to send verification email:", emailErr);
        }

        this.success = "Registration successful! Please check your email to verify your account. Redirecting to login...";

        setTimeout(() => {
          this.$router.push("/login");
        }, 1500);
      } catch (error) {
        if (error.code === "auth/email-already-in-use") {
          this.error = "Email already registered.";
        } else if (error.code === "auth/invalid-email") {
          this.error = "Invalid email address.";
        } else if (error.code === "auth/weak-password") {
          this.error = "Password is too weak.";
        } else {
          this.error = "Registration failed. Please try again.";
        }
        console.error(error);
      } finally {
        this.loading = false;
      }
    },

    async loginWithGoogle() {
      this.googleError = "";
      this.googleLoading = true;
      try {
        const authStore = useAuthStore();
        const result = await authStore.signInWithGoogle();
        if (result.ok) {
          this.$router.push("/");
        } else if (result.error) {
          this.googleError = result.error;
        }
      } finally {
        this.googleLoading = false;
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
          <h1 class="auth-title">Create account</h1>
          <p class="auth-subtitle">Join the GameHub community — it's free</p>
        </div>

        <div v-if="error" class="auth-error">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
          {{ error }}
        </div>

        <div v-if="success" class="auth-success">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" aria-hidden="true"><polyline points="20 6 9 17 4 12"/></svg>
          {{ success }}
        </div>

        <form @submit.prevent="register" class="auth-form">
          <!-- Name -->
          <div class="auth-field">
            <label for="reg-name" class="auth-label">Display Name</label>
            <div class="auth-input-wrapper">
              <svg class="auth-input-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M20 21v-2a4 4 0 00-4-4H8a4 4 0 00-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
              <input
                id="reg-name"
                v-model="name"
                type="text"
                class="auth-input"
                :class="{ 'input-error': nameError, 'input-valid': touched.name && !nameError && name }"
                placeholder="Your display name"
                @blur="touch('name')"
                autocomplete="name"
              />
            </div>
            <span v-if="nameError" class="auth-field-error">{{ nameError }}</span>
          </div>

          <!-- Email -->
          <div class="auth-field">
            <label for="reg-email" class="auth-label">Email</label>
            <div class="auth-input-wrapper">
              <svg class="auth-input-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/><polyline points="22,6 12,13 2,6"/></svg>
              <input
                id="reg-email"
                v-model="email"
                type="email"
                class="auth-input"
                :class="{ 'input-error': emailError, 'input-valid': touched.email && !emailError && email }"
                placeholder="your@email.com"
                @blur="touch('email')"
                autocomplete="email"
              />
            </div>
            <span v-if="emailError" class="auth-field-error">{{ emailError }}</span>
          </div>

          <!-- Password -->
          <div class="auth-field">
            <label for="reg-password" class="auth-label">Password</label>
            <div class="auth-input-wrapper">
              <svg class="auth-input-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><rect x="3" y="11" width="18" height="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0110 0v4"/></svg>
              <input
                id="reg-password"
                v-model="password"
                type="password"
                class="auth-input"
                :class="{ 'input-error': passwordError, 'input-valid': touched.password && !passwordError && password }"
                placeholder="At least 6 characters"
                @blur="touch('password')"
                autocomplete="new-password"
              />
            </div>
            <span v-if="passwordError" class="auth-field-error">{{ passwordError }}</span>

            <!-- Password strength -->
            <div v-if="password && !passwordError" class="auth-strength">
              <div class="auth-strength-bar">
                <div
                  class="auth-strength-fill"
                  :style="{ width: (passwordStrength / 5) * 100 + '%', background: strengthColor }"
                ></div>
              </div>
              <span class="auth-strength-label" :style="{ color: strengthColor }">{{ strengthLabel }}</span>
            </div>
          </div>

          <!-- Confirm Password -->
          <div class="auth-field">
            <label for="reg-confirm" class="auth-label">Confirm Password</label>
            <div class="auth-input-wrapper">
              <svg class="auth-input-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><rect x="3" y="11" width="18" height="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0110 0v4"/></svg>
              <input
                id="reg-confirm"
                v-model="confirmPassword"
                type="password"
                class="auth-input"
                :class="{ 'input-error': confirmPasswordError, 'input-valid': touched.confirmPassword && !confirmPasswordError && confirmPassword }"
                placeholder="Repeat your password"
                @blur="touch('confirmPassword')"
                autocomplete="new-password"
              />
            </div>
            <span v-if="confirmPasswordError" class="auth-field-error">{{ confirmPasswordError }}</span>
          </div>

          <button
            id="register-submit-btn"
            type="submit"
            class="auth-submit-btn"
            :disabled="loading"
          >
            <span v-if="loading" class="auth-spinner"></span>
            <template v-else>
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" aria-hidden="true"><path d="M16 21v-2a4 4 0 00-4-4H6a4 4 0 00-4 4v2"/><circle cx="9" cy="7" r="4"/><line x1="19" y1="8" x2="19" y2="14"/><line x1="22" y1="11" x2="16" y2="11"/></svg>
              Create Account
            </template>
          </button>
        </form>

        <!-- Social Divider -->
        <div class="auth-divider">
          <span>or</span>
        </div>

        <!-- Google Sign-In -->
        <div v-if="googleError" class="auth-error" style="margin-bottom: 12px;">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
          {{ googleError }}
        </div>
        <button
          id="register-google-btn"
          type="button"
          class="auth-social-btn"
          :disabled="googleLoading || loading"
          @click="loginWithGoogle"
        >
          <span v-if="googleLoading" class="auth-spinner" style="width:18px;height:18px;"></span>
          <template v-else>
            <svg width="18" height="18" viewBox="0 0 48 48" aria-hidden="true">
              <path fill="#EA4335" d="M24 9.5c3.54 0 6.71 1.22 9.21 3.6l6.85-6.85C35.9 2.38 30.47 0 24 0 14.62 0 6.51 5.38 2.56 13.22l7.98 6.19C12.43 13.72 17.74 9.5 24 9.5z"/>
              <path fill="#4285F4" d="M46.98 24.55c0-1.57-.15-3.09-.38-4.55H24v9.02h12.94c-.58 2.96-2.26 5.48-4.78 7.18l7.73 6c4.51-4.18 7.09-10.36 7.09-17.65z"/>
              <path fill="#FBBC05" d="M10.53 28.59c-.48-1.45-.76-2.99-.76-4.59s.27-3.14.76-4.59l-7.98-6.19C.92 16.46 0 20.12 0 24c0 3.88.92 7.54 2.56 10.78l7.97-6.19z"/>
              <path fill="#34A853" d="M24 48c6.48 0 11.93-2.13 15.89-5.81l-7.73-6c-2.15 1.45-4.92 2.3-8.16 2.3-6.26 0-11.57-4.22-13.47-9.91l-7.98 6.19C6.51 42.62 14.62 48 24 48z"/>
            </svg>
            Continue with Google
          </template>
        </button>

        <p class="auth-switch">
          Already have an account?
          <router-link to="/login">Sign in →</router-link>
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
  background: radial-gradient(circle, #8b5cf6, transparent 70%);
  top: -200px;
  right: -100px;
  animation: orb-drift 9s ease-in-out infinite alternate;
}

.auth-orb-2 {
  width: 400px;
  height: 400px;
  background: radial-gradient(circle, #0ea5e9, transparent 70%);
  bottom: -150px;
  left: -100px;
  animation: orb-drift 11s ease-in-out infinite alternate-reverse;
}

.auth-orb-3 {
  width: 300px;
  height: 300px;
  background: radial-gradient(circle, #10b981, transparent 70%);
  top: 60%;
  left: 40%;
  opacity: 0.12;
  animation: orb-pulse 7s ease-in-out infinite;
}

@keyframes orb-drift {
  from { transform: translate(0, 0); }
  to { transform: translate(30px, 20px); }
}

@keyframes orb-pulse {
  0%, 100% { opacity: 0.08; transform: scale(1); }
  50% { opacity: 0.18; transform: scale(1.1); }
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

.auth-logo-link:hover { opacity: 0.85; color: var(--primary); }
.auth-logo-link img { filter: brightness(1.3); }

.auth-card {
  background: var(--bg-glass);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid var(--border-glass);
  border-radius: 20px;
  padding: 36px 32px;
  box-shadow: 0 25px 60px rgba(0, 0, 0, 0.5), 0 0 0 1px var(--border-subtle) inset;
}

.auth-card-header { margin-bottom: 24px; }

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
  margin-bottom: 18px;
}

.auth-success {
  display: flex;
  align-items: center;
  gap: 8px;
  background: rgba(16, 185, 129, 0.12);
  border: 1px solid rgba(16, 185, 129, 0.3);
  border-radius: 10px;
  color: #6ee7b7;
  font-size: 0.85rem;
  padding: 12px 14px;
  margin-bottom: 18px;
}

.auth-form {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.auth-field {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.auth-label {
  font-size: 0.83rem;
  font-weight: 600;
  color: var(--text-secondary);
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

.auth-input.input-error {
  border-color: rgba(244, 63, 94, 0.6);
  background: rgba(244, 63, 94, 0.05);
}

.auth-input.input-valid {
  border-color: rgba(16, 185, 129, 0.5);
}

.auth-input::placeholder { color: var(--text-muted); }

.auth-field-error {
  font-size: 0.78rem;
  color: #fca5a5;
  padding-left: 2px;
}

/* Password strength */
.auth-strength {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-top: 2px;
}

.auth-strength-bar {
  flex: 1;
  height: 4px;
  border-radius: 2px;
  background: var(--overlay-medium);
  overflow: hidden;
}

.auth-strength-fill {
  height: 100%;
  border-radius: 2px;
  transition: all 0.3s ease;
}

.auth-strength-label {
  font-size: 0.75rem;
  font-weight: 600;
  white-space: nowrap;
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
  color: var(--text-primary);
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

.auth-submit-btn:active:not(:disabled) { transform: translateY(0); }

.auth-submit-btn:disabled {
  opacity: 0.65;
  cursor: not-allowed;
}

.auth-spinner {
  width: 18px;
  height: 18px;
  border: 2px solid var(--overlay-heavy);
  border-top-color: var(--text-primary);
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
}

@keyframes spin { to { transform: rotate(360deg); } }

.auth-switch {
  text-align: center;
  margin: 20px 0 0;
  font-size: 0.875rem;
  color: var(--text-muted);
}

.auth-switch a {
  color: var(--primary-light);
  font-weight: 600;
  text-decoration: none;
  transition: color 0.2s;
}

.auth-switch a:hover { color: var(--primary); }

</style>

<style scoped>
/* Social OAuth styles — Register.vue */
.auth-divider {
  display: flex;
  align-items: center;
  gap: 12px;
  margin: 20px 0;
  color: var(--text-muted);
  font-size: 0.8rem;
  letter-spacing: 0.05em;
  text-transform: uppercase;
}

.auth-divider::before,
.auth-divider::after {
  content: "";
  flex: 1;
  height: 1px;
  background: rgba(255, 255, 255, 0.1);
}

.auth-social-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  width: 100%;
  padding: 11px 20px;
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.12);
  background: rgba(255, 255, 255, 0.05);
  color: var(--text-primary, #f1f5f9);
  font-size: 0.9rem;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s, border-color 0.2s, transform 0.15s;
  margin-bottom: 4px;
}

.auth-social-btn:hover:not(:disabled) {
  background: rgba(255, 255, 255, 0.1);
  border-color: rgba(255, 255, 255, 0.22);
  transform: translateY(-1px);
}

.auth-social-btn:active:not(:disabled) {
  transform: translateY(0);
}

.auth-social-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>


