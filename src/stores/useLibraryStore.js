import { defineStore } from "pinia";
import { auth, db } from "../firebase";
import { collection, query, where, getDocs, doc, setDoc } from "firebase/firestore";

export const useLibraryStore = defineStore("library", {
  state: () => ({
    favorites: [],
    purchases: [],
    loadingFavorites: false,
    loadingPurchases: false,
    favoritesLoaded: false,
    purchasesLoaded: false,
  }),
  
  getters: {
    isFavorite: (state) => (gameId) => {
      return state.favorites.some(f => String(f.gameId) === String(gameId));
    },
    hasPurchased: (state) => (gameId) => {
      return state.purchases.some(p => String(p.gameId) === String(gameId));
    }
  },

  actions: {
    async fetchFavorites(force = false) {
      if (!auth.currentUser) return;
      if (this.favoritesLoaded && !force) return;
      
      this.loadingFavorites = true;
      try {
        const q = query(
          collection(db, "favorites"),
          where("userId", "==", auth.currentUser.uid)
        );
        const snapshot = await getDocs(q);
        this.favorites = snapshot.docs.map(doc => ({
          id: doc.id,
          docId: doc.id,
          ...doc.data()
        }));
        this.favoritesLoaded = true;
      } catch (err) {
        console.error("Error fetching favorites:", err);
      } finally {
        this.loadingFavorites = false;
      }
    },

    async fetchPurchases(force = false) {
      if (!auth.currentUser) return;
      if (this.purchasesLoaded && !force) return;

      this.loadingPurchases = true;
      try {
        const q = query(
          collection(db, "purchases"),
          where("userId", "==", auth.currentUser.uid)
        );
        const snapshot = await getDocs(q);
        this.purchases = snapshot.docs.map(doc => {
          const data = doc.data();
          return {
            id: doc.id,
            docId: doc.id,
            ...data,
            status: data.status || 'not_installed',
            gameName: data.gameName || data.title || "Unknown Game"
          };
        });
        this.purchasesLoaded = true;
      } catch (err) {
        console.error("Error fetching purchases:", err);
      } finally {
        this.loadingPurchases = false;
      }
    },
    
    clearStore() {
      this.favorites = [];
      this.purchases = [];
      this.favoritesLoaded = false;
      this.purchasesLoaded = false;
    }
  }
});
