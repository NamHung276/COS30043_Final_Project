<script>
import { auth, db } from "../firebase";
import { onAuthStateChanged } from "firebase/auth";
import { doc, getDoc, updateDoc, setDoc } from "firebase/firestore";
import { backendApi } from "../services/api";

// Import new dashboard components
import LibraryHero from "../components/library/LibraryHero.vue";
import LibraryStats from "../components/library/LibraryStats.vue";
import LibraryAchievements from "../components/library/LibraryAchievements.vue";
import LibraryGallery from "../components/library/LibraryGallery.vue";
import LibraryNotesAndGoals from "../components/library/LibraryNotesAndGoals.vue";
import LibraryCommunity from "../components/library/LibraryCommunity.vue";
import LibrarySidebar from "../components/library/LibrarySidebar.vue";

export default {
  name: "LibraryDetails",
  components: {
    LibraryHero,
    LibraryStats,
    LibraryAchievements,
    LibraryGallery,
    LibraryNotesAndGoals,
    LibraryCommunity,
    LibrarySidebar
  },
  data() {
    return {
      currentUser: null,
      purchaseId: this.$route.params.id,
      purchase: null,
      game: null,
      loading: true,
      error: null,
      now: Date.now(),
      activeSessionTimer: null,
      achievements: []
    };
  },

  mounted() {
    this.unsubscribe = onAuthStateChanged(auth, (user) => {
      this.currentUser = user;
      if (user) {
        this.fetchData();
      }
    });

    this.activeSessionTimer = setInterval(() => {
      this.now = Date.now();
    }, 1000);
  },

  beforeUnmount() {
    if (this.unsubscribe) this.unsubscribe();
    if (this.activeSessionTimer) clearInterval(this.activeSessionTimer);
  },

  methods: {
    async fetchData() {
      this.loading = true;
      try {
        const docRef = doc(db, "purchases", this.purchaseId);
        const snap = await getDoc(docRef);
        
        if (!snap.exists() || snap.data().userId !== this.currentUser.uid) {
          this.error = "Game not found in your library.";
          return;
        }

        this.purchase = { id: snap.id, ...snap.data() };

        // Seed visual history if none exists — in-memory only, not saved to Firebase
        let displaySessions = this.purchase.sessions || [];
        if (!displaySessions.length) {
          const nowTime = Date.now();
          displaySessions = [
            { startTime: nowTime - 86400000, duration: 2100 },
            { startTime: nowTime - 86400000 * 3, duration: 7200 },
            { startTime: nowTime - 86400000 * 5, duration: 2880 }
          ];
          // Attach to purchase for template rendering only — NOT written to Firestore
          this.purchase = { ...this.purchase, sessions: displaySessions };
        }

        if (!this.purchase.status) this.purchase.status = 'not_installed';

        // Fetch RAWG or FreeToGame game data
        if (this.purchase.gameId) {
          let res;
          if (this.purchase.source === "freetogame") {
            res = await backendApi.get(`/free-games/${this.purchase.gameId}`);
            this.game = res.data;
            this.game.name = this.game.title;
            this.game.background_image = this.game.thumbnail;
            this.game.released = this.game.release_date;
            this.game.developers = [{ name: this.game.developer }];
            this.game.publishers = [{ name: this.game.publisher }];
            this.game.parent_platforms = [{ platform: { name: this.game.platform } }];
            
            if (this.game.genre) {
              this.game.genres = [{ name: this.game.genre }];
            }
          } else {
            res = await backendApi.get(`/games/${this.purchase.gameId}`);
            const data = res.data;
            this.game = {
              ...data,
              name: data.title,
              background_image: data.hero_image || data.cover_image,
              developers: (data.developers || []).map(d => ({ name: d })),
              publishers: (data.publishers || []).map(p => ({ name: p })),
              genres: (data.genres || []).map(g => ({ name: g })),
              parent_platforms: (data.platforms || []).map(p => ({ 
                platform: { name: p, slug: p.toLowerCase() } 
              }))
            };
          }

          // Generate genre-based achievements
          const genres = this.game.genres?.map(g => g.name.toLowerCase()) || [];
          let achs = [];
          if (genres.includes('action') || genres.includes('shooter')) {
            achs = [
              { id: 1, title: "First Blood", unlocked: true },
              { id: 2, title: "Sharpshooter", unlocked: true },
              { id: 3, title: "Untouchable", unlocked: false },
              { id: 4, title: "Master of Arms", unlocked: false }
            ];
          } else if (genres.includes('rpg') || genres.includes('adventure')) {
            achs = [
              { id: 1, title: "A New Journey", unlocked: true },
              { id: 2, title: "First Camp", unlocked: true },
              { id: 3, title: "Legend of the Realm", unlocked: false },
              { id: 4, title: "Hero's Path", unlocked: false }
            ];
          } else {
            achs = [
              { id: 1, title: "Getting Started", unlocked: true },
              { id: 2, title: "Halfway There", unlocked: true },
              { id: 3, title: "Perfectionist", unlocked: false },
              { id: 4, title: "Mastery", unlocked: false }
            ];
          }
          achs[0].title = `${this.game.name} Beginner`;
          this.achievements = achs;
        }

      } catch (err) {
        console.error(err);
        this.error = "Failed to load game details.";
      } finally {
        this.loading = false;
      }
    },

    async updateStatus(newStatus) {
      this.purchase.status = newStatus;
      try {
        await setDoc(doc(db, "purchases", this.purchaseId), { status: newStatus }, { merge: true });
      } catch (e) {
        console.error("Failed to update status", e);
      }
    },

    async playGame() {
      this.purchase.status = 'playing';
      this.purchase.sessionStart = Date.now();
      await setDoc(doc(db, "purchases", this.purchaseId), { 
        status: 'playing', 
        lastPlayed: new Date(),
        sessionStart: this.purchase.sessionStart
      }, { merge: true });
    },

    async stopGame() {
      if (this.purchase.status !== 'playing') return;
      
      const elapsedSeconds = Math.floor((Date.now() - this.purchase.sessionStart) / 1000);
      const newPlaytime = (this.purchase.playtime || 0) + elapsedSeconds;

      const newSession = {
        startTime: this.purchase.sessionStart,
        duration: elapsedSeconds
      };
      
      const sessions = this.purchase.sessions || [];
      sessions.unshift(newSession);

      this.purchase.status = 'installed';
      this.purchase.playtime = newPlaytime;
      this.purchase.sessionStart = null;
      this.purchase.sessions = sessions;

      await setDoc(doc(db, "purchases", this.purchaseId), {
        status: 'installed',
        playtime: newPlaytime,
        sessionStart: null,
        sessions: sessions
      }, { merge: true });
    },

    // Handlers for child components
    async handleUpdateNotes(newNotes) {
      this.purchase.notes = newNotes;
      await setDoc(doc(db, "purchases", this.purchaseId), { notes: newNotes }, { merge: true });
    },

    async handleUpdateGoals(newGoals) {
      this.purchase.goals = newGoals;
      await setDoc(doc(db, "purchases", this.purchaseId), { goals: newGoals }, { merge: true });
    },

    async handleAddScreenshot(url) {
      const screenshots = this.purchase.screenshots || [];
      screenshots.push(url);
      this.purchase.screenshots = screenshots;
      await setDoc(doc(db, "purchases", this.purchaseId), { screenshots }, { merge: true });
    },

    async handleRemoveScreenshot(url) {
      let screenshots = this.purchase.screenshots || [];
      screenshots = screenshots.filter(s => s !== url);
      this.purchase.screenshots = screenshots;
      await setDoc(doc(db, "purchases", this.purchaseId), { screenshots }, { merge: true });
    },

    // Toast/Alert triggers for Sidebar QoL
    triggerAction(actionName) {
      if (actionName === 'launch') {
        this.playGame();
      } else {
        alert(`${actionName} triggered! (Feature in development)`);
      }
    }
  }
};
</script>

<template>
  <div class="library-details-dashboard bg-main" v-if="!loading && purchase && game">
    
    <LibraryHero 
      :game="game" 
      :purchase="purchase" 
      @update-status="updateStatus" 
    />

    <div class="container mt-4 pb-5">
      <div class="row g-4">
        
        <!-- Main Content Area -->
        <div class="col-lg-8 d-flex flex-column gap-4">
          <LibraryStats :purchase="purchase" />
          
          <LibraryGallery 
            :game="game" 
            :purchase="purchase"
            @add-screenshot="handleAddScreenshot"
            @remove-screenshot="handleRemoveScreenshot"
          />
          
          <LibraryNotesAndGoals 
            :purchase="purchase" 
            @update-notes="handleUpdateNotes"
            @update-goals="handleUpdateGoals"
          />
          
          <LibraryCommunity 
            :game="game" 
            :purchase="purchase" 
          />
        </div>

        <!-- Sidebar Area -->
        <div class="col-lg-4 d-flex flex-column gap-4">
          <!-- Play action logic is currently inside Sidebar or Hero. I'll pass launch to playGame -->
          
          <div v-if="purchase.status === 'playing'" class="bg-success bg-opacity-25 border border-success rounded-4 p-4 text-center shadow-lg mb-2">
            <h4 class="text-white fw-bold mb-3"><i class="bi bi-controller me-2"></i>Game Running</h4>
            <button @click="stopGame" class="btn btn-danger btn-lg rounded-pill px-5 fw-bold shadow">
              <i class="bi bi-stop-fill me-2"></i> Stop Session
            </button>
          </div>
          <div v-else-if="purchase.status === 'installed' || purchase.status === 'completed'" class="bg-dark bg-opacity-50 border border-secondary border-opacity-25 rounded-4 p-4 text-center shadow-lg mb-2">
            <button @click="playGame" class="btn btn-success btn-lg w-100 rounded-pill fw-bold shadow" style="background: linear-gradient(180deg, #10b981 0%, #059669 100%);">
              <i class="bi bi-play-fill me-2 fs-4"></i> <span class="fs-4">PLAY</span>
            </button>
          </div>
          <div v-else class="bg-dark bg-opacity-50 border border-secondary border-opacity-25 rounded-4 p-4 text-center shadow-lg mb-2">
            <button @click="updateStatus('installed')" class="btn btn-info btn-lg w-100 rounded-pill fw-bold shadow text-dark">
              <i class="bi bi-download me-2 fs-4"></i> <span class="fs-4">INSTALL</span>
            </button>
          </div>

          <LibraryAchievements :achievements="achievements" />
          
          <LibrarySidebar 
            :game="game" 
            :purchase="purchase" 
            @launch="playGame"
            @verify="triggerAction('Verify Files')"
            @reinstall="triggerAction('Reinstall')"
            @hide="triggerAction('Hide Game')"
            @archive="triggerAction('Archive')"
            @export-notes="triggerAction('Export Notes')"
          />
        </div>

      </div>
    </div>
  </div>

  <div v-else-if="loading" class="d-flex justify-content-center align-items-center" style="height: 60vh;">
    <div class="spinner-border text-primary" role="status" style="width: 3rem; height: 3rem;"></div>
  </div>
  
  <div v-else-if="error" class="container mt-5 pt-5 text-center">
    <div class="alert alert-danger d-inline-block shadow-lg rounded-4 p-4">
      <i class="bi bi-exclamation-triangle-fill fs-1 d-block mb-3"></i>
      <h4 class="fw-bold">{{ error }}</h4>
      <router-link to="/library" class="btn btn-outline-danger mt-3 rounded-pill px-4">Back to Library</router-link>
    </div>
  </div>
</template>

<style scoped>
.bg-main {
  background-color: var(--bg-main);
  min-height: 100vh;
}
</style>
