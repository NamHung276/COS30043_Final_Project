/**
 * useWishlistStore.js — Single source of truth for the user's wishlist.
 *
 * Previously, every view (Games.vue, Deals.vue, GameDetails.vue, Home.vue)
 * maintained its own local `wishlisted: new Set()` and called Firestore
 * individually via addToWishlist/loadWishlist methods duplicated across files.
 * FreeToPlay.vue was the worst case: it never wrote to Firestore at all —
 * wishlist state was lost on every page refresh.
 *
 * This store:
 *   - Loads the wishlist once per user session, not per page visit.
 *   - Properly writes to Firestore on every add.
 *   - Handles both RAWG (premium) and FreeToGame (f2p) game types.
 *   - Sets the `source` field correctly so Favorites.vue can route correctly.
 *
 * Usage (Options API via mapState / mapActions):
 *   computed: { ...mapState(useWishlistStore, ['wishlistedIds']) }
 *   // In methods, access the store directly:
 *   const wishlistStore = useWishlistStore();
 *   await wishlistStore.addToWishlist(game, this.toast);
 */

import { defineStore } from "pinia";
import { auth, db } from "../firebase";
import {
  collection,
  query,
  where,
  getDocs,
  addDoc,
} from "firebase/firestore";

export const useWishlistStore = defineStore("wishlist", {
  state: () => ({
    /** @type {Set<string>} — Set of gameId strings for O(1) lookup */
    wishlistedIds: new Set(),
    /** UID of the user whose wishlist is currently loaded */
    loadedForUser: null,
  }),

  getters: {
    /**
     * Returns true if a game is in the wishlist.
     * Usage: wishlistStore.isWishlisted(game.id)
     * @param {object} state
     */
    isWishlisted: (state) => (gameId) =>
      state.wishlistedIds.has(String(gameId)),
  },

  actions: {
    /**
     * Loads the current user's wishlist from Firestore.
     * No-op if already loaded for the same user.
     * @param {string} userId — Firebase UID
     */
    async loadWishlist(userId) {
      if (!userId || this.loadedForUser === userId) return;
      try {
        const snap = await getDocs(
          query(collection(db, "favorites"), where("userId", "==", userId)),
        );
        this.wishlistedIds.clear();
        snap.forEach((d) => this.wishlistedIds.add(String(d.data().gameId)));
        this.loadedForUser = userId;
      } catch (err) {
        console.error("[WishlistStore] loadWishlist failed:", err);
      }
    },

    /**
     * Adds a game to the user's Firestore wishlist.
     * Handles both RAWG (premium) and FreeToGame (f2p) game objects.
     *
     * @param {object} game — Game object from any source
     * @param {object|null} toast — Injected toast reference for feedback
     * @returns {boolean} true if added, false if already in wishlist or error
     */
    async addToWishlist(game, toast = null) {
      if (!auth.currentUser) return false;

      const gameId = game.id ?? game.gameId;
      const gameIdStr = String(gameId);

      // Local duplicate check (fast path)
      if (this.wishlistedIds.has(gameIdStr)) return false;

      // Determine game type for correct routing in Favorites
      const isF2P =
        game.itemType === "f2p" ||
        game.source === "freetogame" ||
        // F2P games use `title` field; RAWG games use `name`
        (game.title && !game.name);

      try {
        // Firestore duplicate check (handles stale local state / cross-device)
        const snap = await getDocs(
          query(
            collection(db, "favorites"),
            where("userId", "==", auth.currentUser.uid),
            where("gameId", "==", gameId),
          ),
        );

        if (!snap.empty) {
          // Sync local state with Firestore truth
          this.wishlistedIds.add(gameIdStr);
          return false;
        }

        const title = game.name ?? game.title ?? "Unknown";

        await addDoc(collection(db, "favorites"), {
          userId: auth.currentUser.uid,
          gameId,
          title,
          thumbnail: game.background_image ?? game.thumbnail ?? null,
          genre: game.genres?.[0]?.name ?? game.genre ?? "",
          // 'source' field: used by Favorites.vue to build the correct route
          source: isF2P ? "freetogame" : "rawg",
          priority: "Interested",
          addedAt: new Date().toISOString(),
        });

        this.wishlistedIds.add(gameIdStr);
        toast?.show(`♥ "${title}" added to wishlist`, "success");
        return true;
      } catch (err) {
        console.error("[WishlistStore] addToWishlist failed:", err);
        toast?.show("Failed to add to wishlist", "error");
        return false;
      }
    },

    /**
     * Resets the store — called when user signs out.
     */
    reset() {
      this.wishlistedIds.clear();
      this.loadedForUser = null;
    },
  },
});
