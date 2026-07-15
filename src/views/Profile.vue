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
  name: "ProfileView",

  inject: ["toast"],

  data() {
    return {
      currentUser: null,
      statsLoading: true,

      reviews: [],
      favorites: [],
      posts: [],
      purchases: [],

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

      unsubscribe: null,
    };
  },

  computed: {
    userInitial() {
      if (!this.currentUser) return "?";
      const name = this.currentUser.displayName || this.currentUser.email;
      return name.charAt(0).toUpperCase();
    },

    memberSince() {
      if (!this.currentUser?.metadata?.creationTime) return "—";
      return new Date(this.currentUser.metadata.creationTime).getFullYear();
    },

    memberSinceFull() {
      if (!this.currentUser?.metadata?.creationTime) return "—";
      return new Date(
        this.currentUser.metadata.creationTime,
      ).toLocaleDateString("en-AU", {
        year: "numeric",
        month: "long",
        day: "numeric",
      });
    },

    totalFavorites() {
      return this.favorites.length;
    },

    totalReviews() {
      return this.reviews.length;
    },

    averageRating() {
      if (this.reviews.length === 0) return "0.0";
      const total = this.reviews.reduce((sum, r) => sum + r.rating, 0);
      return (total / this.reviews.length).toFixed(1);
    },

    combinedActivity() {
      const activities = [];

      this.reviews.forEach((r) => {
        activities.push({
          type: "review",
          id: `rev_${r.id}`,
          item: r,
          date: r.createdAt?.seconds || 0,
        });
      });

      this.favorites.forEach((f) => {
        activities.push({
          type: "favorite",
          id: `fav_${f.id}`,
          item: f,
          date: f.createdAt?.seconds || 0,
        });
      });

      this.posts.forEach((p) => {
        let time = p.createdAt?.seconds;
        if (!time && p.date) {
          time = Math.floor(new Date(p.date).getTime() / 1000);
        } else if (!time) {
          time = 0;
        }
        activities.push({
          type: "post",
          id: `post_${p.id}`,
          item: p,
          date: time,
        });
      });

      return activities.sort((a, b) => b.date - a.date).slice(0, 8);
    },

    profileTitle() {
      if (this.totalFavorites >= 10) return "🏆 Game Collector";
      if (this.totalReviews >= 5) return "⭐ Community Reviewer";
      return "🎮 GameHub Member";
    },

    bannerStyle() {
      const newestFav = [...this.favorites]
        .filter((f) => f.thumbnail)
        .sort(
          (a, b) => (b.createdAt?.seconds || 0) - (a.createdAt?.seconds || 0),
        )[0];

      if (newestFav) {
        return {
          backgroundImage: `radial-gradient(circle at 70% 30%, rgba(124, 58, 237, 0.4) 0%, transparent 50%), radial-gradient(circle at 20% 80%, rgba(6, 182, 212, 0.3) 0%, transparent 50%), url('${newestFav.thumbnail}')`,
        };
      }
      return {}; // Fallback to default CSS background
    },

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
      } else {
        this.$router.push("/login");
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
        const reviewsQuery = query(
          collection(db, "reviews"),
          where("userId", "==", uid),
        );
        const favsQuery = query(
          collection(db, "favorites"),
          where("userId", "==", uid),
        );
        const postsQuery = query(
          collection(db, "news"),
          where("userId", "==", uid),
        );
        const purchasesQuery = query(
          collection(db, "purchases"),
          where("userId", "==", uid),
        );

        // Fetch individually to prevent one failing collection (e.g., missing permissions) from breaking everything
        try {
          const reviewsSnap = await getDocs(reviewsQuery);
          this.reviews = reviewsSnap.docs.map((d) => ({
            id: d.id,
            ...d.data(),
          }));
        } catch (e) {
          console.warn("Failed to fetch reviews", e);
        }

        try {
          const favsSnap = await getDocs(favsQuery);
          this.favorites = favsSnap.docs.map((d) => ({
            id: d.id,
            ...d.data(),
          }));
        } catch (e) {
          console.warn("Failed to fetch favorites", e);
        }

        try {
          const postsSnap = await getDocs(postsQuery);
          this.posts = postsSnap.docs.map((d) => ({ id: d.id, ...d.data() }));
        } catch (e) {
          console.warn("Failed to fetch posts", e);
        }

        try {
          const purchasesSnap = await getDocs(purchasesQuery);
          const rawPurchases = purchasesSnap.docs.map((d) => ({
            id: d.id,
            ...d.data(),
          }));
          this.purchases = rawPurchases.sort(
            (a, b) =>
              (b.purchasedAt?.seconds || 0) - (a.purchasedAt?.seconds || 0),
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

    timeAgo(seconds) {
      if (!seconds) return "Just now";
      const now = Math.floor(Date.now() / 1000);
      const diff = now - seconds;

      if (diff < 60) return "Just now";
      if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
      if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`;
      if (diff < 2592000) return `${Math.floor(diff / 86400)}d ago`;
      if (diff < 31536000) return `${Math.floor(diff / 2592000)}mo ago`;
      return `${Math.floor(diff / 31536000)}y ago`;
    },

    getGameName(gameId) {
      const fav = this.favorites.find(
        (f) => String(f.gameId) === String(gameId),
      );
      return fav ? fav.title : `Game #${gameId}`;
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
          this.currentPassword,
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
            "warning",
          );
        } else {
          this.toast.show(
            "Failed to change password. Please try again.",
            "error",
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
  <div class="profile-page" v-if="currentUser">
    <!-- Hero Banner (Steam style) -->
    <div class="profile-banner">
      <div class="profile-banner-bg" :style="bannerStyle"></div>
      <div
        class="container position-relative h-100 d-flex align-items-end pb-4"
      >
        <div class="d-flex align-items-end gap-4 w-100 banner-content-wrap">
          <div class="profile-avatar-banner">
            {{ userInitial }}
          </div>

          <div class="pb-2 flex-grow-1">
            <h1 class="display-4 fw-bold text-white mb-1 profile-name">
              {{ currentUser.displayName || "Gamer" }}
            </h1>
            <div
              class="d-flex align-items-center gap-3 text-muted-light flex-wrap"
            >
              <span class="badge-explorer">{{ profileTitle }}</span>
              <span>Joined {{ memberSince }}</span>
            </div>
          </div>

          <div class="pb-2 d-none d-md-flex gap-4">
            <div class="text-center">
              <div class="fs-4 fw-bold text-white">{{ totalFavorites }}</div>
              <div
                class="text-uppercase text-muted-light"
                style="font-size: 0.75rem; letter-spacing: 1px"
              >
                Wishlisted
              </div>
            </div>
            <div class="text-center">
              <div class="fs-4 fw-bold text-white">{{ totalReviews }}</div>
              <div
                class="text-uppercase text-muted-light"
                style="font-size: 0.75rem; letter-spacing: 1px"
              >
                Reviews
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="container py-5">
      <div class="row g-5">
        <!-- Left Sidebar (Stats & Settings) -->
        <div class="col-lg-4">
          <!-- Game Statistics Card -->
          <div class="card profile-glass-card mb-4">
            <div class="card-body p-4">
              <h5
                class="card-title text-white mb-4 d-flex align-items-center gap-2"
              >
                <i class="bi bi-bar-chart-fill text-primary"></i> Game
                Statistics
              </h5>

              <div v-if="statsLoading" class="text-center py-3">
                <div
                  class="spinner-border spinner-border-sm text-primary"
                  role="status"
                ></div>
              </div>
              <div v-else>
                <div class="stat-row">
                  <span class="stat-label"
                    ><i class="bi bi-star-fill text-warning me-2"></i>
                    Wishlist</span
                  >
                  <span class="stat-value text-white fw-bold">{{
                    totalFavorites
                  }}</span>
                </div>
                <hr class="border-secondary opacity-25 my-3" />
                <div class="stat-row">
                  <span class="stat-label"
                    ><i class="bi bi-star-fill text-warning me-2"></i>
                    Reviews</span
                  >
                  <span class="stat-value text-white fw-bold">{{
                    totalReviews
                  }}</span>
                </div>
                <hr class="border-secondary opacity-25 my-3" />
                <div class="stat-row">
                  <span class="stat-label"
                    ><i class="bi bi-calculator-fill text-info me-2"></i> Avg
                    Rating Given</span
                  >
                  <span class="stat-value text-white fw-bold">{{
                    averageRating
                  }}</span>
                </div>
                <hr class="border-secondary opacity-25 my-3" />
                <div class="stat-row">
                  <span class="stat-label"
                    ><i class="bi bi-calendar-check-fill text-success me-2"></i>
                    Member Since</span
                  >
                  <span class="stat-value text-white">{{ memberSince }}</span>
                </div>
              </div>
            </div>
          </div>

          <!-- Account Information Card -->
          <div class="card profile-glass-card mb-4">
            <div class="card-body p-4">
              <h5
                class="card-title text-white mb-4 d-flex align-items-center gap-2"
              >
                <i class="bi bi-person-badge-fill text-primary"></i> Account
                Information
              </h5>

              <div class="stat-row mb-3">
                <span class="stat-label">Email</span>
                <span class="stat-value text-white text-break text-end">{{
                  currentUser.email
                }}</span>
              </div>
              <div class="stat-row mb-3">
                <span class="stat-label">Status</span>
                <span
                  v-if="currentUser.emailVerified"
                  class="stat-value text-success"
                  ><i class="bi bi-patch-check-fill me-1"></i> Verified</span
                >
                <span v-else class="stat-value text-warning"
                  ><i class="bi bi-exclamation-triangle-fill me-1"></i> Email
                  not verified</span
                >
              </div>
              <div class="stat-row">
                <span class="stat-label">Joined</span>
                <span class="stat-value text-white">{{ memberSinceFull }}</span>
              </div>
            </div>
          </div>

          <!-- Settings Accordion -->
          <div class="accordion profile-accordion" id="settingsAccordion">
            <div class="accordion-item bg-transparent border-0 mb-3">
              <h2 class="accordion-header">
                <button
                  class="accordion-button collapsed profile-glass-card text-white py-3"
                  type="button"
                  data-bs-toggle="collapse"
                  data-bs-target="#collapseName"
                >
                  <i class="bi bi-pencil-square me-2 text-primary"></i> Edit
                  Profile
                </button>
              </h2>
              <div
                id="collapseName"
                class="accordion-collapse collapse"
                data-bs-parent="#settingsAccordion"
              >
                <div class="accordion-body profile-glass-card mt-2 p-4">
                  <form @submit.prevent="saveName">
                    <div class="mb-3">
                      <label
                        for="profileName"
                        class="form-label text-muted-light small text-uppercase"
                        >Display Name</label
                      >
                      <input
                        id="profileName"
                        v-model="newName"
                        type="text"
                        class="form-control gd-input"
                        :class="{
                          'is-invalid': nameError,
                          'is-valid':
                            nameTouched && !nameError && !nameUnchanged,
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
                      class="btn btn-primary w-100"
                      :disabled="nameLoading || nameUnchanged || !!nameError"
                    >
                      <span
                        v-if="nameLoading"
                        class="spinner-border spinner-border-sm me-2"
                      ></span>
                      Save Changes
                    </button>
                  </form>
                </div>
              </div>
            </div>

            <div class="accordion-item bg-transparent border-0">
              <h2 class="accordion-header">
                <button
                  class="accordion-button collapsed profile-glass-card text-white py-3"
                  type="button"
                  data-bs-toggle="collapse"
                  data-bs-target="#collapsePassword"
                >
                  <i class="bi bi-shield-lock-fill me-2 text-primary"></i>
                  Change Password
                </button>
              </h2>
              <div
                id="collapsePassword"
                class="accordion-collapse collapse"
                data-bs-parent="#settingsAccordion"
              >
                <div class="accordion-body profile-glass-card mt-2 p-4">
                  <form @submit.prevent="changePassword">
                    <div class="mb-3">
                      <label
                        class="form-label text-muted-light small text-uppercase"
                        >Current Password</label
                      >
                      <input
                        v-model="currentPassword"
                        type="password"
                        class="form-control gd-input"
                        :class="{
                          'is-invalid': currentPasswordError,
                          'is-valid':
                            pwTouched.currentPassword && !currentPasswordError,
                        }"
                        @blur="touchPw('currentPassword')"
                      />
                      <div
                        v-if="currentPasswordError"
                        class="invalid-feedback mt-1"
                      >
                        {{ currentPasswordError }}
                      </div>
                    </div>
                    <div class="mb-3">
                      <label
                        class="form-label text-muted-light small text-uppercase"
                        >New Password</label
                      >
                      <input
                        v-model="newPassword"
                        type="password"
                        class="form-control gd-input"
                        :class="{
                          'is-invalid': newPasswordError,
                          'is-valid':
                            pwTouched.newPassword && !newPasswordError,
                        }"
                        @blur="touchPw('newPassword')"
                      />

                      <!-- Password Strength Meter -->
                      <div class="mt-2" v-if="newPassword">
                        <div
                          class="d-flex justify-content-between align-items-center mb-1"
                        >
                          <small
                            class="text-muted-light"
                            style="font-size: 0.75rem"
                            >Password Strength</small
                          >
                          <small
                            :style="{ color: strengthColor }"
                            class="fw-bold"
                            style="font-size: 0.75rem"
                            >{{ strengthLabel }}</small
                          >
                        </div>
                        <div class="d-flex gap-1" style="height: 4px">
                          <div
                            v-for="n in 5"
                            :key="n"
                            class="flex-grow-1 rounded-pill"
                            :style="{
                              background:
                                n <= passwordStrength
                                  ? strengthColor
                                  : 'rgba(255,255,255,0.1)',
                              transition: 'background 0.3s',
                            }"
                          ></div>
                        </div>
                      </div>

                      <div
                        v-if="newPasswordError"
                        class="invalid-feedback mt-1"
                      >
                        {{ newPasswordError }}
                      </div>
                    </div>
                    <div class="mb-4">
                      <label
                        class="form-label text-muted-light small text-uppercase"
                        >Confirm Password</label
                      >
                      <input
                        v-model="confirmNewPassword"
                        type="password"
                        class="form-control gd-input"
                        :class="{
                          'is-invalid': confirmNewPasswordError,
                          'is-valid':
                            pwTouched.confirmNewPassword &&
                            !confirmNewPasswordError,
                        }"
                        @blur="touchPw('confirmNewPassword')"
                      />
                      <div
                        v-if="confirmNewPasswordError"
                        class="invalid-feedback mt-1"
                      >
                        {{ confirmNewPasswordError }}
                      </div>
                    </div>
                    <button
                      type="submit"
                      class="btn btn-primary w-100"
                      :disabled="!isPwFormValid || pwLoading"
                    >
                      <span
                        v-if="pwLoading"
                        class="spinner-border spinner-border-sm me-2"
                      ></span>
                      Update Password
                    </button>
                  </form>
                </div>
              </div>
            </div>
            <div class="accordion-item bg-transparent border-0">
              <h2 class="accordion-header">
                <button
                  class="accordion-button collapsed profile-glass-card text-white py-3"
                  type="button"
                  data-bs-toggle="collapse"
                  data-bs-target="#collapsePurchases"
                >
                  <i class="bi bi-receipt me-2 text-primary"></i> Purchase
                  History
                </button>
              </h2>
              <div
                id="collapsePurchases"
                class="accordion-collapse collapse"
                data-bs-parent="#settingsAccordion"
              >
                <div class="accordion-body profile-glass-card mt-2 p-4">
                  <div v-if="statsLoading" class="text-center py-3">
                    <span
                      class="spinner-border spinner-border-sm text-primary"
                    ></span>
                  </div>
                  <div
                    v-else-if="purchases.length === 0"
                    class="text-center py-3 text-muted-light"
                  >
                    No purchases found.
                  </div>
                  <div v-else>
                    <div
                      v-for="purchase in purchases"
                      :key="purchase.id"
                      class="d-flex justify-content-between align-items-center mb-3 pb-3 border-bottom border-secondary border-opacity-25"
                    >
                      <div>
                        <div class="text-white fw-bold">
                          {{ purchase.gameName }}
                        </div>
                        <div class="text-muted-light small">
                          {{
                            new Date(
                              purchase.purchasedAt?.seconds * 1000,
                            ).toLocaleDateString()
                          }}
                        </div>
                      </div>
                      <div class="text-end">
                        <div class="text-white">
                          ${{ (purchase.price || 0).toFixed(2) }}
                        </div>
                        <div class="text-success small">
                          <i class="bi bi-check-circle-fill me-1"></i
                          >{{ purchase.status || "Completed" }}
                        </div>
                      </div>
                    </div>
                    <router-link
                      to="/library"
                      class="btn btn-outline-primary w-100 mt-2"
                      >View Library</router-link
                    >
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Right Main Content (Activity & Favorites) -->
        <div class="col-lg-8">
          <!-- Wishlist Preview -->
          <div
            class="d-flex justify-content-between align-items-end mb-4 mt-4 mt-lg-0"
          >
            <h3 class="text-white mb-0 fw-bold">Wishlist</h3>
            <router-link
              to="/favorites"
              class="text-primary text-decoration-none d-flex align-items-center gap-1"
            >
              View All <i class="bi bi-arrow-right"></i>
            </router-link>
          </div>

          <div v-if="statsLoading" class="text-center py-5">
            <div class="spinner-border text-primary" role="status"></div>
          </div>

          <div
            v-else-if="favorites.length === 0"
            class="profile-glass-card p-5 text-center mb-5"
          >
            <i
              class="bi bi-star fs-1 text-secondary mb-3 d-block"
              aria-hidden="true"
            ></i>
            <h5 class="text-white">Your wishlist is empty.</h5>
            <p class="text-muted-light mb-4">
              Start discovering games to build your wishlist.
            </p>
            <router-link to="/games" class="btn btn-primary px-4"
              >Browse Games</router-link
            >
          </div>

          <div v-else class="row g-4 mb-5">
            <div
              v-for="fav in favorites.slice(0, 3)"
              :key="fav.id"
              class="col-md-4 col-sm-6"
            >
              <router-link
                :to="
                  fav.source === 'freetogame'
                    ? `/free-to-play/${fav.gameId}`
                    : `/games/${fav.gameId}`
                "
                class="text-decoration-none"
              >
                <div class="fav-mini-card">
                  <div class="fav-img-wrap">
                    <img
                      v-lazy-img="fav.thumbnail"
                      :alt="fav.title"
                      class="fav-img"
                    />
                    <div class="fav-overlay"></div>
                  </div>
                  <div class="fav-content">
                    <h6 class="text-white text-truncate mb-1">
                      {{ fav.title }}
                    </h6>
                    <small class="text-muted-light">{{ fav.genre }}</small>
                  </div>
                </div>
              </router-link>
            </div>
          </div>

          <!-- Combined Activity Feed -->
          <h3 class="text-white mb-4 fw-bold">Recent Activity</h3>

          <div v-if="statsLoading" class="text-center py-5">
            <div class="spinner-border text-primary" role="status"></div>
          </div>

          <div
            v-else-if="combinedActivity.length === 0"
            class="profile-glass-card p-5 text-center"
          >
            <i
              class="bi bi-activity fs-1 text-secondary mb-3 d-block"
              aria-hidden="true"
            ></i>
            <h5 class="text-white">No activity yet</h5>
            <p class="text-muted-light">
              Review games, write news, or save favorites to see them here.
            </p>
          </div>

          <div v-else class="d-flex flex-column gap-3">
            <div
              v-for="act in combinedActivity"
              :key="act.id"
              class="profile-glass-card p-4"
            >
              <!-- Review Activity -->
              <template v-if="act.type === 'review'">
                <div
                  class="d-flex justify-content-between align-items-center mb-3"
                >
                  <div class="d-flex align-items-center gap-2">
                    <span class="badge bg-secondary bg-opacity-25 text-white"
                      >⭐ Review</span
                    >
                  </div>
                  <span class="text-muted-light small">{{
                    timeAgo(act.date)
                  }}</span>
                </div>
                <div class="d-flex align-items-center gap-2 mb-2">
                  <span class="text-warning">
                    <template v-for="s in act.item.rating" :key="'r' + s"
                      ><i class="bi bi-star-fill" aria-hidden="true"></i
                    ></template>
                    <template v-for="s in 5 - act.item.rating" :key="'e' + s"
                      ><i class="bi bi-star" aria-hidden="true"></i
                    ></template>
                  </span>
                  <span class="text-white fw-bold"
                    >Reviewed
                    {{
                      act.item.gameName || getGameName(act.item.gameId)
                    }}</span
                  >
                </div>
                <p class="text-muted-light mb-3 review-comment">
                  "{{ act.item.comment }}"
                </p>
                <div
                  class="d-flex justify-content-end pt-2 border-top border-secondary border-opacity-25 mt-2"
                >
                  <router-link
                    :to="`/games/${act.item.gameId}`"
                    class="btn btn-sm btn-outline-primary rounded-pill px-3"
                    >View Game</router-link
                  >
                </div>
              </template>

              <!-- Favorite Activity -->
              <template v-else-if="act.type === 'favorite'">
                <div
                  class="d-flex justify-content-between align-items-center mb-3"
                >
                  <div class="d-flex align-items-center gap-2">
                    <span class="badge bg-danger bg-opacity-25 text-danger"
                      >❤️ Favorite</span
                    >
                  </div>
                  <span class="text-muted-light small">{{
                    timeAgo(act.date)
                  }}</span>
                </div>
                <div class="d-flex align-items-center gap-2 mb-3">
                  <h6 class="text-white fw-bold mb-0">
                    Added {{ act.item.title }} to collection
                  </h6>
                </div>
                <div
                  class="d-flex justify-content-end pt-2 border-top border-secondary border-opacity-25 mt-2"
                >
                  <router-link
                    :to="
                      act.item.source === 'freetogame'
                        ? `/free-to-play/${act.item.gameId}`
                        : `/games/${act.item.gameId}`
                    "
                    class="btn btn-sm btn-outline-danger rounded-pill px-3"
                    >View Game</router-link
                  >
                </div>
              </template>

              <!-- Post/News Activity -->
              <template v-else-if="act.type === 'post'">
                <div
                  class="d-flex justify-content-between align-items-center mb-3"
                >
                  <div class="d-flex align-items-center gap-2">
                    <span class="badge bg-info bg-opacity-25 text-info"
                      >📰 Post</span
                    >
                  </div>
                  <span class="text-muted-light small">{{
                    timeAgo(act.date)
                  }}</span>
                </div>
                <div class="d-flex align-items-center gap-2 mb-3">
                  <h6 class="text-white fw-bold mb-0">
                    Published "{{ act.item.title }}"
                  </h6>
                </div>
                <div
                  class="d-flex justify-content-end pt-2 border-top border-secondary border-opacity-25 mt-2"
                >
                  <router-link
                    :to="`/gamehub-news/user/${act.item.id}`"
                    class="btn btn-sm btn-outline-info rounded-pill px-3"
                    >Read Post</router-link
                  >
                </div>
              </template>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- Global Loading state -->
  <div v-else class="text-center py-5 mt-5">
    <div
      class="spinner-border text-primary"
      style="width: 3rem; height: 3rem"
      role="status"
    ></div>
    <h4 class="text-white mt-4">Loading Profile...</h4>
  </div>
</template>

<style scoped>
.profile-page {
  min-height: 100vh;
  background: var(--bg-deep);
}

/* Banner */
.profile-banner {
  position: relative;
  height: 320px;
  background: #0f1016;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
  overflow: hidden;
}

.profile-banner-bg {
  position: absolute;
  inset: 0;
  background-image:
    radial-gradient(
      circle at 70% 30%,
      rgba(124, 58, 237, 0.4) 0%,
      transparent 50%
    ),
    radial-gradient(
      circle at 20% 80%,
      rgba(6, 182, 212, 0.3) 0%,
      transparent 50%
    ),
    url("https://images.unsplash.com/photo-1542751371-adc38448a05e?q=80&w=2070&auto=format&fit=crop");
  background-size: cover;
  background-position: center;
  filter: blur(2px) brightness(0.4);
  z-index: 0;
}

.banner-content-wrap {
  z-index: 1;
}

.profile-avatar-banner {
  width: 120px;
  height: 120px;
  border-radius: 20px;
  background: linear-gradient(135deg, #7c3aed, #06b6d4);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 3.5rem;
  font-weight: 800;
  color: white;
  border: 4px solid #1a1c23;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
  flex-shrink: 0;
}

.profile-name {
  text-shadow: 0 4px 10px rgba(0, 0, 0, 0.5);
}

.badge-explorer {
  background: rgba(124, 58, 237, 0.2);
  color: #c4b5fd;
  border: 1px solid rgba(124, 58, 237, 0.4);
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 0.8rem;
  font-weight: 600;
}

/* Cards */
.profile-glass-card {
  background: rgba(25, 27, 35, 0.6);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 16px;
  backdrop-filter: blur(16px);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
}

.stat-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.stat-label {
  color: var(--text-secondary);
  font-size: 0.95rem;
}

/* Forms */
.gd-input {
  background: rgba(0, 0, 0, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: white;
  border-radius: 10px;
  padding: 12px 16px;
  transition: all 0.3s;
}
.gd-input:focus {
  background: rgba(0, 0, 0, 0.3);
  border-color: var(--primary);
  box-shadow: 0 0 0 3px rgba(124, 58, 237, 0.2);
  color: white;
}
.gd-input::placeholder {
  color: rgba(255, 255, 255, 0.3);
}

.gd-input.is-invalid {
  border-color: #ef4444;
  background-image: none;
}
.gd-input.is-invalid:focus {
  box-shadow: 0 0 0 3px rgba(239, 68, 68, 0.2);
}
.gd-input.is-valid {
  border-color: #22c55e;
  background-image: none;
}
.gd-input.is-valid:focus {
  box-shadow: 0 0 0 3px rgba(34, 197, 94, 0.2);
}

/* Accordion Override */
.profile-accordion .accordion-button {
  background: transparent;
  box-shadow: none;
  font-weight: 600;
  border-radius: 16px !important;
  transition: all 0.2s;
}
.profile-accordion .accordion-button:not(.collapsed) {
  background: rgba(124, 58, 237, 0.1);
  color: white;
}
.profile-accordion .accordion-button::after {
  filter: invert(1);
}

/* Fav Mini Card */
.fav-mini-card {
  position: relative;
  border-radius: 12px;
  overflow: hidden;
  background: rgba(25, 27, 35, 0.8);
  border: 1px solid rgba(255, 255, 255, 0.08);
  transition:
    transform 0.3s,
    box-shadow 0.3s;
  height: 100%;
}
.fav-mini-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.3);
  border-color: rgba(124, 58, 237, 0.4);
}
.fav-img-wrap {
  position: relative;
  height: 120px;
}
.fav-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
.fav-overlay {
  position: absolute;
  inset: 0;
  background: linear-gradient(
    180deg,
    transparent 50%,
    rgba(15, 16, 22, 0.9) 100%
  );
}
.fav-content {
  padding: 12px 16px;
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
}

@media (max-width: 768px) {
  .profile-banner {
    height: auto;
    min-height: 280px;
    padding-top: 2rem;
  }
  .banner-content-wrap {
    flex-direction: column;
    align-items: center !important;
    text-align: center;
  }
}

.text-muted-light {
  color: rgba(255, 255, 255, 0.75) !important;
}

.review-comment {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  line-height: 1.6;
  font-size: 0.95rem;
}
</style>
