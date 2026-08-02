/**
 * useAuthStore.js — Single source of truth for Firebase authentication.
 *
 * Previously, every authenticated view registered its own onAuthStateChanged
 * listener independently. This created N parallel Firebase connections and N
 * Firestore user-doc reads on every page navigation.
 *
 * Usage:
 *   import { useAuthStore } from '../stores/useAuthStore';
 *   // In App.vue onMounted — registers exactly ONE listener for the whole app.
 *   const authStore = useAuthStore(); authStore.init();
 *   // In any view (Options API):
 *   computed: { ...mapState(useAuthStore, ['currentUser']) }
 */

import { defineStore } from "pinia";
import { auth, db } from "../firebase";
import { onAuthStateChanged } from "firebase/auth";
import { doc, getDoc } from "firebase/firestore";

export const useAuthStore = defineStore("auth", {
  state: () => ({
    /** @type {import('firebase/auth').User | null} */
    currentUser: null,
    /** True once the first onAuthStateChanged callback has fired. */
    ready: false,
    /** Guard against calling init() more than once. */
    _initialized: false,
    /** Cached user role from Firestore (e.g. "admin", "user") */
    userRole: null,
    /** Cached banned status from Firestore */
    isBanned: false,
  }),

  getters: {
    isAuthenticated: (state) => !!state.currentUser,
    uid: (state) => state.currentUser?.uid ?? null,
  },

  actions: {
    /**
     * Registers a single, app-wide Firebase auth listener.
     * Safe to call multiple times — subsequent calls are no-ops.
     * Call this once in App.vue's onMounted.
     */
    init() {
      if (this._initialized) return;
      this._initialized = true;

      onAuthStateChanged(auth, async (user) => {
        this.currentUser = user;
        if (user) {
          try {
            const snap = await getDoc(doc(db, "users", user.uid));
            if (snap.exists()) {
              this.userRole = snap.data().role || "user";
              this.isBanned = snap.data().status === "Banned";
            }
          } catch (e) {
            console.error("Failed to fetch user doc for auth store", e);
          }
        } else {
          this.userRole = null;
          this.isBanned = false;
        }
        this.ready = true;
      });
    },
    
    /**
     * Waits until the initial auth state is resolved.
     * Hard timeout of 10 s — resolves (never rejects) so navigation
     * always continues even when Firebase is slow or offline.
     */
    waitForReady() {
      if (this.ready) return Promise.resolve();
      return new Promise((resolve) => {
        const TIMEOUT_MS = 10_000;
        const POLL_MS = 50;
        let elapsed = 0;

        const poll = () => {
          if (this.ready || elapsed >= TIMEOUT_MS) {
            resolve();
            return;
          }
          elapsed += POLL_MS;
          setTimeout(poll, POLL_MS);
        };

        setTimeout(poll, POLL_MS);
      });
    }
  },
});
