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
import {
  onAuthStateChanged,
  signOut,
  GoogleAuthProvider,
  signInWithPopup,
} from "firebase/auth";
import { doc, getDoc, setDoc, serverTimestamp } from "firebase/firestore";

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
    },

    /**
     * Sign in with Google using a popup.
     * - First-time users: creates a Firestore user doc.
     * - Returning users: merges non-destructive fields only (preserves role, etc.).
     * - Popup-closed-by-user is treated as a silent cancel (no error thrown).
     * @returns {{ ok: boolean, error?: string }}
     */
    async signInWithGoogle() {
      const provider = new GoogleAuthProvider();
      // Request the user's email scope so it is always available
      provider.addScope("email");
      provider.addScope("profile");

      try {
        const { user } = await signInWithPopup(auth, provider);

        // Build / update Firestore user document
        const userRef = doc(db, "users", user.uid);
        const snap = await getDoc(userRef);

        if (!snap.exists()) {
          // First-ever Google login → create full document
          await setDoc(userRef, {
            uid: user.uid,
            displayName: user.displayName || user.email.split("@")[0],
            email: user.email,
            photoURL: user.photoURL || null,
            provider: "google",
            role: "user",
            createdAt: serverTimestamp(),
          });
        } else {
          // Returning user → safely refresh photoURL / displayName only
          // role, status, and all other fields are preserved unchanged
          await setDoc(
            userRef,
            {
              photoURL: user.photoURL || null,
              displayName: user.displayName || snap.data().displayName,
              lastLoginAt: serverTimestamp(),
            },
            { merge: true },
          );

          // Check ban status the same way email/password login does
          if (snap.data().status === "Banned") {
            await signOut(auth);
            return { ok: false, error: "Your account has been suspended by an administrator." };
          }
        }

        return { ok: true };
      } catch (err) {
        // User closed the popup — not an error
        if (
          err.code === "auth/popup-closed-by-user" ||
          err.code === "auth/cancelled-popup-request"
        ) {
          return { ok: false, error: null };
        }
        console.error("[AuthStore] Google sign-in failed:", err);
        return { ok: false, error: "Google sign-in failed. Please try again." };
      }
    },
  },
});
