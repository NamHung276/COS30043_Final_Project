<script>
import { auth, db } from "../firebase";
import {
  onAuthStateChanged,
  updateProfile,
  updatePassword,
  reauthenticateWithCredential,
  EmailAuthProvider,
} from "firebase/auth";
import { collection, query, where, getDocs } from "firebase/firestore";

export default {
  name: "SettingsView",

  inject: ["toast"],

  data() {
    return {
      currentUser: null,
      activeTab: "profile", // profile, security, purchases, notifications, appearance
      
      // Edit name
      newName: "",
      nameLoading: false,
      nameTouched: false,

      // Change password
      currentPassword: "",
      newPassword: "",
      confirmNewPassword: "",
      pwLoading: false,
      pwTouched: {
        currentPassword: false,
        newPassword: false,
        confirmNewPassword: false,
      },

      // Purchases
      purchases: [],
      statsLoading: true,

      unsubscribe: null,
    };
  },

  computed: {
    // Name validation
    nameError() {
      if (!this.nameTouched) return "";
      if (!this.newName.trim()) return "Name cannot be empty.";
      if (this.newName.trim().length < 2)
        return "Name must be at least 2 characters.";
      return "";
    },

    nameUnchanged() {
      return this.newName.trim() === (this.currentUser?.displayName || "");
    },

    // Password validation
    currentPasswordError() {
      if (!this.pwTouched.currentPassword) return "";
      if (!this.currentPassword) return "Current password is required.";
      return "";
    },

    newPasswordError() {
      if (!this.pwTouched.newPassword) return "";
      if (!this.newPassword) return "New password is required.";
      if (this.newPassword.length < 6)
        return "Password must be at least 6 characters.";
      return "";
    },

    confirmNewPasswordError() {
      if (!this.pwTouched.confirmNewPassword) return "";
      if (!this.confirmNewPassword) return "Please confirm your new password.";
      if (this.newPassword !== this.confirmNewPassword)
        return "Passwords do not match.";
      return "";
    },

    isPwFormValid() {
      return (
        !this.currentPasswordError &&
        !this.newPasswordError &&
        !this.confirmNewPasswordError &&
        this.currentPassword &&
        this.newPassword &&
        this.confirmNewPassword
      );
    },

    passwordStrength() {
      if (!this.newPassword) return 0;
      let s = 0;
      if (this.newPassword.length >= 6) s++;
      if (this.newPassword.length >= 8) s++;
      if (/[A-Z]/.test(this.newPassword)) s++;
      if (/[0-9]/.test(this.newPassword)) s++;
      if (/[^A-Za-z0-9]/.test(this.newPassword)) s++;
      return s;
    },

    strengthLabel() {
      return (
        ["", "Weak", "Fair", "Good", "Strong", "Very Strong"][
          this.passwordStrength
        ] || ""
      );
    },

    strengthColor() {
      return (
        ["", "#ef4444", "#f59e0b", "#eab308", "#22c55e", "#06b6d4"][
          this.passwordStrength
        ] || ""
      );
    },
  },

  mounted() {
    this.unsubscribe = onAuthStateChanged(auth, async (user) => {
      this.currentUser = user;
      if (user) {
        this.newName = user.displayName || "";
        await this.fetchUserStats(user.uid);
      }
    });
  },

  beforeUnmount() {
    if (this.unsubscribe) this.unsubscribe();
  },

  methods: {
    async fetchUserStats(uid) {
      this.statsLoading = true;
      try {
        const purchasesQuery = query(
          collection(db, "purchases"),
          where("userId", "==", uid)
        );
        try {
          const purchasesSnap = await getDocs(purchasesQuery);
          const rawPurchases = purchasesSnap.docs.map((d) => ({
            id: d.id,
            ...d.data(),
          }));
          this.purchases = rawPurchases.sort(
            (a, b) =>
              (b.purchasedAt?.seconds || 0) - (a.purchasedAt?.seconds || 0)
          );
        } catch (e) {
          console.warn("Failed to fetch purchases", e);
        }
      } catch (err) {
        console.error("Failed to load stats", err);
      } finally {
        this.statsLoading = false;
      }
    },

    touchPw(field) {
      this.pwTouched[field] = true;
    },

    async saveName() {
      this.nameTouched = true;
      if (this.nameError || this.nameUnchanged || this.nameLoading) return;

      this.nameLoading = true;
      try {
        await updateProfile(this.currentUser, {
          displayName: this.newName.trim(),
        });
        await this.currentUser.reload();
        this.currentUser = auth.currentUser;
        this.toast.show("Display name updated! ✨", "success");
      } catch (err) {
        console.error(err);
        this.toast.show("Failed to update name. Please try again.", "error");
      } finally {
        this.nameLoading = false;
      }
    },

    async changePassword() {
      Object.keys(this.pwTouched).forEach((k) => (this.pwTouched[k] = true));
      if (!this.isPwFormValid || this.pwLoading) return;

      this.pwLoading = true;
      try {
        const credential = EmailAuthProvider.credential(
          this.currentUser.email,
          this.currentPassword
        );
        await reauthenticateWithCredential(this.currentUser, credential);
        await updatePassword(this.currentUser, this.newPassword);

        this.toast.show("Password changed successfully! 🔒", "success");

        this.currentPassword = "";
        this.newPassword = "";
        this.confirmNewPassword = "";
        Object.keys(this.pwTouched).forEach((k) => (this.pwTouched[k] = false));
      } catch (err) {
        console.error(err);
        if (
          err.code === "auth/wrong-password" ||
          err.code === "auth/invalid-credential"
        ) {
          this.toast.show("Current password is incorrect.", "error");
        } else if (err.code === "auth/too-many-requests") {
          this.toast.show(
            "Too many attempts. Please try again later.",
            "warning"
          );
        } else {
          this.toast.show(
            "Failed to change password. Please try again.",
            "error"
          );
        }
      } finally {
        this.pwLoading = false;
      }
    },
  },
};
</script>

<template>
  <div class="settings-page" v-if="currentUser">
    <div class="container py-5">
      <!-- Header -->
      <div class="mb-5">
        <h1 class="settings-page-title display-5 fw-bold mb-2">Settings & Privacy</h1>
        <p class="text-muted-light">Manage your account preferences, security, and activity.</p>
      </div>

      <div class="row g-4">
        <!-- Sidebar Navigation -->
        <div class="col-lg-3">
          <div class="settings-sidebar profile-glass-card p-3 h-100">
            
            <div class="settings-nav-group mb-4">
              <h6 class="settings-nav-header text-muted text-uppercase small fw-bold mb-3 px-3">Account Settings</h6>
              <button 
                class="settings-nav-btn" 
                :class="{ active: activeTab === 'profile' }"
                @click="activeTab = 'profile'"
              >
                <i class="bi bi-person-badge-fill me-3"></i> Profile Details
              </button>
              <button 
                class="settings-nav-btn" 
                :class="{ active: activeTab === 'security' }"
                @click="activeTab = 'security'"
              >
                <i class="bi bi-shield-lock-fill me-3"></i> Password & Security
              </button>
            </div>

            <div class="settings-nav-group mb-4">
              <h6 class="settings-nav-header text-muted text-uppercase small fw-bold mb-3 px-3">Your Activity</h6>
              <button 
                class="settings-nav-btn" 
                :class="{ active: activeTab === 'purchases' }"
                @click="activeTab = 'purchases'"
              >
                <i class="bi bi-receipt me-3"></i> Purchase History
              </button>
            </div>

            <div class="settings-nav-group">
              <h6 class="settings-nav-header text-muted text-uppercase small fw-bold mb-3 px-3">Preferences</h6>
              <button 
                class="settings-nav-btn" 
                :class="{ active: activeTab === 'appearance' }"
                @click="activeTab = 'appearance'"
              >
                <i class="bi bi-palette-fill me-3"></i> Appearance
              </button>
              <button 
                class="settings-nav-btn" 
                :class="{ active: activeTab === 'notifications' }"
                @click="activeTab = 'notifications'"
              >
                <i class="bi bi-bell-fill me-3"></i> Notifications
              </button>
            </div>

          </div>
        </div>

        <!-- Main Content Area -->
        <div class="col-lg-9">
          <!-- Profile Details Section -->
          <div v-if="activeTab === 'profile'" class="settings-content profile-glass-card p-4 p-md-5">
            <h3 class="settings-section-title mb-4">Profile Details</h3>
            <div class="settings-section-desc text-muted-light mb-5">
              Update your display name and view your registered email address. This name will be visible on your reviews and posts.
            </div>

            <div class="mb-4">
              <label class="form-label text-muted-light small text-uppercase fw-bold">Email Address</label>
              <input type="text" class="form-control gd-input opacity-75" :value="currentUser.email" disabled />
              <div class="form-text text-muted mt-2">
                <i class="bi" :class="currentUser.emailVerified ? 'bi-patch-check-fill text-success' : 'bi-exclamation-triangle-fill text-warning'"></i>
                {{ currentUser.emailVerified ? 'Email verified' : 'Email not verified' }}
              </div>
            </div>

            <form @submit.prevent="saveName">
              <div class="mb-4">
                <label for="profileName" class="form-label text-muted-light small text-uppercase fw-bold">Display Name</label>
                <input
                  id="profileName"
                  v-model="newName"
                  type="text"
                  class="form-control gd-input"
                  :class="{
                    'is-invalid': nameError,
                    'is-valid': nameTouched && !nameError && !nameUnchanged,
                  }"
                  placeholder="Your display name"
                  @blur="nameTouched = true"
                />
                <div v-if="nameError" class="invalid-feedback mt-1">
                  {{ nameError }}
                </div>
              </div>
              <button
                type="submit"
                class="btn btn-primary px-5"
                :disabled="nameLoading || nameUnchanged || !!nameError"
              >
                <span v-if="nameLoading" class="spinner-border spinner-border-sm me-2"></span>
                Save Changes
              </button>
            </form>
          </div>

          <!-- Password & Security Section -->
          <div v-if="activeTab === 'security'" class="settings-content profile-glass-card p-4 p-md-5">
            <h3 class="settings-section-title mb-4">Password & Security</h3>
            <div class="settings-section-desc text-muted-light mb-5">
              Ensure your account is using a long, random password to stay secure.
            </div>

            <form @submit.prevent="changePassword">
              <div class="mb-4">
                <label class="form-label text-muted-light small text-uppercase fw-bold">Current Password</label>
                <input
                  v-model="currentPassword"
                  type="password"
                  class="form-control gd-input"
                  :class="{
                    'is-invalid': currentPasswordError,
                    'is-valid': pwTouched.currentPassword && !currentPasswordError,
                  }"
                  @blur="touchPw('currentPassword')"
                />
                <div v-if="currentPasswordError" class="invalid-feedback mt-1">
                  {{ currentPasswordError }}
                </div>
              </div>

              <div class="mb-4">
                <label class="form-label text-muted-light small text-uppercase fw-bold">New Password</label>
                <input
                  v-model="newPassword"
                  type="password"
                  class="form-control gd-input"
                  :class="{
                    'is-invalid': newPasswordError,
                    'is-valid': pwTouched.newPassword && !newPasswordError,
                  }"
                  @blur="touchPw('newPassword')"
                />

                <!-- Password Strength Meter -->
                <div class="mt-3" v-if="newPassword">
                  <div class="d-flex justify-content-between align-items-center mb-2">
                    <small class="text-muted-light" style="font-size: 0.75rem">Password Strength</small>
                    <small :style="{ color: strengthColor }" class="fw-bold" style="font-size: 0.75rem">{{ strengthLabel }}</small>
                  </div>
                  <div class="d-flex gap-1" style="height: 4px">
                    <div
                      v-for="n in 5"
                      :key="n"
                      class="flex-grow-1 rounded-pill"
                      :style="{
                        background: n <= passwordStrength ? strengthColor : 'rgba(255,255,255,0.1)',
                        transition: 'background 0.3s',
                      }"
                    ></div>
                  </div>
                </div>

                <div v-if="newPasswordError" class="invalid-feedback mt-1">
                  {{ newPasswordError }}
                </div>
              </div>

              <div class="mb-5">
                <label class="form-label text-muted-light small text-uppercase fw-bold">Confirm New Password</label>
                <input
                  v-model="confirmNewPassword"
                  type="password"
                  class="form-control gd-input"
                  :class="{
                    'is-invalid': confirmNewPasswordError,
                    'is-valid': pwTouched.confirmNewPassword && !confirmNewPasswordError,
                  }"
                  @blur="touchPw('confirmNewPassword')"
                />
                <div v-if="confirmNewPasswordError" class="invalid-feedback mt-1">
                  {{ confirmNewPasswordError }}
                </div>
              </div>

              <button
                type="submit"
                class="btn btn-primary px-5"
                :disabled="!isPwFormValid || pwLoading"
              >
                <span v-if="pwLoading" class="spinner-border spinner-border-sm me-2"></span>
                Update Password
              </button>
            </form>
          </div>

          <!-- Purchase History Section -->
          <div v-if="activeTab === 'purchases'" class="settings-content profile-glass-card p-4 p-md-5">
            <h3 class="settings-section-title mb-4">Purchase History</h3>
            <div class="settings-section-desc text-muted-light mb-5">
              Review your past transactions and game library additions.
            </div>

            <div v-if="statsLoading" class="purchase-list">
              <div v-for="i in 3" :key="i" class="purchase-item p-4 mb-3 profile-glass-card gh-skeleton" style="height: 104px;"></div>
            </div>
            
            <div v-else-if="purchases.length === 0" class="text-center py-5">
              <i class="bi bi-receipt display-1 text-muted opacity-50 mb-4 d-block"></i>
              <h5 class="profile-text mb-3">No purchases yet</h5>
              <p class="text-muted-light mb-4">When you buy games or claim free titles, they will appear here.</p>
              <router-link to="/deals" class="btn btn-outline-primary px-4">Browse Deals</router-link>
            </div>

            <div v-else class="purchase-list">
              <div
                v-for="purchase in purchases"
                :key="purchase.id"
                class="purchase-item p-4 mb-3 profile-glass-card"
                style="background: rgba(255, 255, 255, 0.02); border-color: rgba(255, 255, 255, 0.05);"
              >
                <div class="d-flex justify-content-between align-items-center">
                  <div class="d-flex align-items-center gap-3">
                    <div class="purchase-icon" style="width: 48px; height: 48px; border-radius: 12px; background: rgba(124, 58, 237, 0.2); display: flex; align-items: center; justify-content: center; color: var(--primary-light);">
                      <i class="bi bi-controller fs-4"></i>
                    </div>
                    <div>
                      <div class="profile-text fw-bold fs-5 mb-1">{{ purchase.gameName }}</div>
                      <div class="text-muted-light small">
                        Order Date: {{ new Date(purchase.purchasedAt?.seconds * 1000).toLocaleDateString() }}
                      </div>
                    </div>
                  </div>
                  <div class="text-end">
                    <div class="profile-text fs-5 fw-bold mb-1">${{ (purchase.price || 0).toFixed(2) }}</div>
                    <div class="text-success small fw-bold">
                      <i class="bi bi-check-circle-fill me-1"></i>{{ purchase.status || "Completed" }}
                    </div>
                  </div>
                </div>
              </div>
              <div class="text-center mt-4">
                <router-link to="/library" class="btn btn-outline-primary px-5">Go to Library</router-link>
              </div>
            </div>
          </div>

          <!-- Placeholder Sections -->
          <div v-if="activeTab === 'appearance'" class="settings-content profile-glass-card p-4 p-md-5 text-center py-5">
             <i class="bi bi-palette-fill display-1 text-muted opacity-50 mb-4 d-block"></i>
             <h3 class="profile-text mb-3">Appearance Settings</h3>
             <p class="text-muted-light">Theme toggles and accessibility settings are coming soon.</p>
          </div>

          <div v-if="activeTab === 'notifications'" class="settings-content profile-glass-card p-4 p-md-5 text-center py-5">
             <i class="bi bi-bell-fill display-1 text-muted opacity-50 mb-4 d-block"></i>
             <h3 class="profile-text mb-3">Notification Preferences</h3>
             <p class="text-muted-light">Email and push notification settings are coming soon.</p>
          </div>

        </div>
      </div>
    </div>
  </div>

  <!-- Global Loading state -->
  <div v-else class="text-center py-5 mt-5">
    <div class="spinner-border text-primary" style="width: 3rem; height: 3rem" role="status"></div>
    <h4 class="profile-text mt-4">Loading Settings...</h4>
  </div>
</template>

<style scoped>
.settings-page {
  min-height: 100vh;
  background: var(--bg-deep);
  color: var(--text-primary);
}

.settings-page-title {
  color: var(--text-primary) !important;
}

.profile-text {
  color: var(--text-primary) !important;
}

.text-muted-light {
  color: rgba(255, 255, 255, 0.75) !important;
}

.profile-glass-card {
  background: var(--bg-glass);
  border: 1px solid var(--border-glass);
  border-radius: 16px;
  backdrop-filter: blur(16px);
  box-shadow: var(--shadow-sm);
}

.settings-sidebar {
  border-radius: 20px;
}

.settings-nav-btn {
  display: flex;
  align-items: center;
  width: 100%;
  padding: 12px 20px;
  background: transparent;
  border: none;
  border-radius: 12px;
  color: var(--text-primary);
  font-weight: 500;
  text-align: left;
  transition: all 0.2s ease;
  margin-bottom: 4px;
}

.settings-nav-btn i {
  font-size: 1.1rem;
  opacity: 0.7;
  transition: opacity 0.2s;
}

.settings-nav-btn:hover {
  background: rgba(255, 255, 255, 0.05);
}

.settings-nav-btn.active {
  background: rgba(124, 58, 237, 0.15);
  color: var(--primary-light);
  font-weight: 600;
}

.settings-nav-btn.active i {
  color: var(--primary-light);
  opacity: 1;
}

.gd-input {
  background: rgba(0, 0, 0, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: var(--text-primary);
  border-radius: 10px;
  padding: 12px 16px;
  transition: all 0.3s;
}

.gd-input:focus {
  background: rgba(0, 0, 0, 0.3);
  border-color: var(--primary-light);
  box-shadow: 0 0 0 3px rgba(124, 58, 237, 0.2);
  color: var(--text-primary);
}

.gd-input::placeholder {
  color: rgba(255, 255, 255, 0.4);
}

.gd-input.is-invalid {
  border-color: #ef4444;
  background-image: none;
}

.gd-input.is-valid {
  border-color: #22c55e;
  background-image: none;
}

.purchase-item {
  transition: transform 0.2s ease;
}

.purchase-item:hover {
  transform: translateY(-2px);
  background: rgba(255, 255, 255, 0.04) !important;
}

@media (max-width: 991.98px) {
  .settings-sidebar {
    display: flex;
    overflow-x: auto;
    padding: 10px !important;
    white-space: nowrap;
    scrollbar-width: none;
    margin-bottom: 20px;
  }
  .settings-sidebar::-webkit-scrollbar {
    display: none;
  }
  .settings-nav-group {
    display: flex;
    margin-bottom: 0 !important;
  }
  .settings-nav-header {
    display: none;
  }
  .settings-nav-btn {
    width: auto;
    margin-bottom: 0;
    margin-right: 8px;
    padding: 10px 16px;
  }
}
</style>
