<script>
import { auth, db } from "../firebase";
import { onAuthStateChanged } from "firebase/auth";
import { doc, getDoc, updateDoc } from "firebase/firestore";
import { backendApi } from "../services/api";

export default {
  name: "LibraryDetails",
  data() {
    return {
      currentUser: null,
      purchaseId: this.$route.params.id,
      purchase: null,
      game: null,
      loading: true,
      error: null,
      notes: "",
      savingNotes: false,
      now: Date.now(),
      activeSessionTimer: null,
      achievements: [],
      activityFeed: [],
    };
  },

  computed: {
    liveTotalPlaytimeSeconds() {
        if (!this.purchase) return 0;
        let total = this.purchase.playtime || 0;
        if (this.purchase.status === 'playing' && this.purchase.sessionStart) {
            total += Math.floor((this.now - this.purchase.sessionStart) / 1000);
        }
        return total;
    },
    playtimeFormatted() {
      const total = this.liveTotalPlaytimeSeconds;
      const h = Math.floor(total / 3600);
      const m = Math.floor((total % 3600) / 60);
      if (h > 0) return `${h}h ${m}m`;
      return `${m}m`;
    },
    
    sessionTimeFormatted() {
      if (!this.purchase || !this.purchase.sessionStart) return "00:00";
      const elapsed = Math.floor((this.now - this.purchase.sessionStart) / 1000);
      const h = Math.floor(elapsed / 3600);
      const m = Math.floor((elapsed % 3600) / 60).toString().padStart(2, '0');
      const s = (elapsed % 60).toString().padStart(2, '0');
      if (h > 0) return `${h}:${m}:${s}`;
      return `${m}:${s}`;
    },

    completionPercentage() {
      if (!this.achievements.length) return 0;
      let baseCompletion = Math.round((this.achievements.filter(a => a.unlocked).length / this.achievements.length) * 100);
      
      // Dynamic tick while playing
      if (this.purchase && this.purchase.status === 'playing' && this.purchase.sessionStart) {
          const elapsedMins = Math.floor((this.now - this.purchase.sessionStart) / 60000);
          baseCompletion += (elapsedMins * 0.1);
      }
      return Math.min(baseCompletion.toFixed(1), 100);
    },

    lastPlayedFormatted() {
      if (!this.purchase) return "Never";
      if (this.purchase.status === 'playing') {
        const elapsedMins = Math.floor((this.now - this.purchase.sessionStart) / 60000);
        return elapsedMins > 0 ? `Started ${elapsedMins}m ago` : "Now";
      }
      return this.formatDate(this.purchase.lastPlayed);
    },

    simulatedInstallSize() {
      if (!this.game) return "50 GB";
      // Generate pseudo-random consistent size based on game id
      const size = (this.game.id % 100) + 20;
      return `${size} GB`;
    }
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
        this.notes = this.purchase.notes || "";

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

        // Ensure status handles completed fallback just in case
        if (!this.purchase.status) this.purchase.status = 'not_installed';

        // Fetch RAWG game data
        if (this.purchase.gameId) {
          const rawgRes = await backendApi.get(`/games/${this.purchase.gameId}`);
          this.game = rawgRes.data;

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

          // Build Activity Feed — use createdAt (the field Checkout.vue saves)
          const dateBought = this.purchase.createdAt?.seconds 
            ? new Date(this.purchase.createdAt.seconds * 1000) 
            : new Date(Date.now() - 86400000 * 10);
          this.activityFeed = [
            { icon: 'bi-download', text: 'Installed', time: dateBought },
            { icon: 'bi-cart-check', text: 'Purchased', time: dateBought },
          ];
          if (this.purchase.sessions && this.purchase.sessions.length > 0) {
              this.activityFeed.unshift({ icon: 'bi-play-fill', text: `Played ${this.formatSessionDuration(this.purchase.sessions[0].duration)}`, time: new Date(this.purchase.sessions[0].startTime) });
          }
          this.activityFeed.unshift({ icon: 'bi-trophy-fill', text: 'Achievement Unlocked: ' + achs[0].title, time: new Date(Date.now() - 3600000) });
        }

      } catch (err) {
        console.error(err);
        this.error = "Failed to load game details.";
      } finally {
        this.loading = false;
      }
    },

    async playGame() {
      this.purchase.status = 'playing';
      this.purchase.sessionStart = Date.now();
      await updateDoc(doc(db, "purchases", this.purchaseId), { 
        status: 'playing', 
        lastPlayed: new Date(),
        sessionStart: this.purchase.sessionStart
      });
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

      await updateDoc(doc(db, "purchases", this.purchaseId), {
        status: 'installed',
        playtime: newPlaytime,
        sessionStart: null,
        sessions: sessions
      });
    },

    async saveNotes() {
      this.savingNotes = true;
      try {
        await updateDoc(doc(db, "purchases", this.purchaseId), {
          notes: this.notes
        });
      } catch (err) {
        console.error(err);
      } finally {
        setTimeout(() => { this.savingNotes = false; }, 500);
      }
    },

    async updateStatus(newStatus) {
      this.purchase.status = newStatus;
      await updateDoc(doc(db, "purchases", this.purchaseId), {
        status: newStatus
      });
    },
    
    formatDate(timestamp) {
      if (!timestamp) return 'Never';
      // Handle Firestore timestamps
      const date = timestamp.seconds ? new Date(timestamp.seconds * 1000) : new Date(timestamp);
      return date.toLocaleDateString();
    },

    formatSessionDuration(seconds) {
      const h = Math.floor(seconds / 3600);
      const m = Math.floor((seconds % 3600) / 60);
      if (h > 0) return `${h}h ${m}m`;
      return `${m}m`;
    }
  }
};
</script>

<template>
  <div class="library-details-page pb-5" v-if="!loading && purchase && game">
    
    <!-- Hero Banner -->
    <div class="ld-hero position-relative">
      <img :src="game.background_image" class="ld-hero-bg w-100 h-100 object-fit-cover" alt="Banner" />
      <div class="ld-hero-overlay position-absolute top-0 start-0 w-100 h-100" style="background: linear-gradient(to top, var(--bg-main) 0%, rgba(15,23,42,0.3) 100%);"></div>
      
      <div class="container position-relative z-2" style="padding-top: 250px; padding-bottom: 40px;">
        <div class="d-flex align-items-end gap-4 flex-wrap">
          <img :src="game.background_image" class="ld-hero-thumb rounded-3 shadow-lg border border-secondary border-opacity-25" style="width: 180px; aspect-ratio: 16/9; object-fit: cover;" />
          <div class="ld-hero-info pb-2">
            <h1 class="display-4 fw-bold text-white mb-2" style="text-shadow: 0 4px 15px rgba(0,0,0,0.8);">{{ game.name }}</h1>
            
            <div class="d-flex align-items-center gap-3">
              <span class="badge bg-success bg-opacity-75 fs-6 py-2 px-3 rounded-pill">
                <i class="bi bi-check-circle-fill me-2"></i> Purchased
              </span>
              
              <div class="dropdown">
                <button class="btn btn-dark border border-secondary dropdown-toggle rounded-pill px-3" type="button" data-bs-toggle="dropdown">
                  Status: 
                  <span v-if="purchase.status === 'playing'" class="text-success fw-bold">Playing</span>
                  <span v-else-if="purchase.status === 'installed'" class="text-info fw-bold">Installed</span>
                  <span v-else-if="purchase.status === 'completed'" class="text-warning fw-bold">Completed</span>
                  <span v-else-if="purchase.status === 'backlog'" class="text-secondary fw-bold">Backlog</span>
                  <span v-else class="text-muted fw-bold">Not Installed</span>
                </button>
                <ul class="dropdown-menu dropdown-menu-dark shadow border-secondary">
                  <li><a class="dropdown-item" href="#" @click.prevent="updateStatus('installed')">Installed</a></li>
                  <li><a class="dropdown-item" href="#" @click.prevent="updateStatus('completed')">Completed</a></li>
                  <li><a class="dropdown-item" href="#" @click.prevent="updateStatus('backlog')">Backlog</a></li>
                  <li><a class="dropdown-item" href="#" @click.prevent="updateStatus('not_installed')">Not Installed</a></li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Main Content -->
    <div class="container mt-4">
      <div class="row g-4">
        
        <!-- LEFT COLUMN -->
        <div class="col-lg-8">
          
          <!-- Play / Install Actions -->
          <div class="ld-play-bar bg-dark bg-opacity-50 p-4 rounded-4 border border-secondary border-opacity-25 mb-4 d-flex align-items-center justify-content-between">
            <div>
              <small class="text-muted text-uppercase fw-bold d-block mb-1" style="letter-spacing: 0.1em;">Play Time</small>
              <span class="fs-4 fw-bold text-primary-var">{{ playtimeFormatted }}</span>
            </div>
            
            <div>
              <small class="text-muted text-uppercase fw-bold d-block mb-1" style="letter-spacing: 0.1em;">Last Played</small>
              <span class="fs-5 fw-bold text-white">{{ lastPlayedFormatted }}</span>
            </div>
            
            <div class="ld-play-action">
              <button v-if="purchase.status === 'playing'" @click="stopGame" class="btn btn-danger btn-lg px-5 rounded-pill fw-bold fs-5 position-relative overflow-hidden shadow-lg border border-danger">
                <i class="bi bi-stop-fill me-2"></i> Stop ({{ sessionTimeFormatted }})
              </button>
              
              <button v-else-if="purchase.status === 'installed' || purchase.status === 'completed'" @click="playGame" class="btn btn-success btn-lg px-5 rounded-pill fw-bold fs-5 shadow-lg border border-success" style="background: linear-gradient(180deg, #10b981 0%, #059669 100%);">
                <i class="bi bi-play-fill me-2"></i> Play
              </button>
              
              <button v-else @click="updateStatus('installed')" class="btn btn-info btn-lg px-5 rounded-pill fw-bold fs-5 shadow-lg text-dark">
                <i class="bi bi-download me-2"></i> Install
              </button>
            </div>
          </div>

          <!-- Play Session History -->
          <div class="ld-section mb-4">
            <h4 class="fw-bold mb-3"><i class="bi bi-clock-history text-primary me-2"></i>Play History</h4>
            <div class="bg-dark bg-opacity-25 rounded-4 p-4 border border-secondary border-opacity-25">
              <div v-if="purchase.sessions && purchase.sessions.length">
                <div class="ld-timeline">
                  <div v-for="(session, index) in purchase.sessions.slice(0, 5)" :key="index" class="ld-timeline-item d-flex justify-content-between align-items-center mb-3 pb-3 border-bottom border-secondary border-opacity-25 last-no-border">
                    <div>
                      <h6 class="mb-1 text-white">{{ formatDate(session.startTime) }}</h6>
                      <small class="text-muted">Started at {{ new Date(session.startTime).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'}) }}</small>
                    </div>
                    <span class="badge bg-primary bg-opacity-25 text-primary-var fs-6 px-3 py-2 rounded-pill">
                      {{ formatSessionDuration(session.duration) }}
                    </span>
                  </div>
                </div>
              </div>
              <div v-else class="text-center text-muted py-4">
                <i class="bi bi-journal-x fs-1 d-block mb-2"></i>
                No play sessions recorded yet. Hit Play to start tracking!
              </div>
            </div>
          </div>

          <!-- My Notes -->
          <div class="ld-section mb-4">
            <h4 class="fw-bold mb-3 d-flex justify-content-between align-items-center">
              <span><i class="bi bi-journal-text text-warning me-2"></i>My Notes</span>
              <span v-if="savingNotes" class="badge bg-success text-white">Saved</span>
            </h4>
            <textarea 
              v-model="notes" 
              @blur="saveNotes"
              class="form-control bg-dark bg-opacity-50 text-white border-secondary border-opacity-25 p-3 rounded-4" 
              rows="5" 
              placeholder="Jot down things to remember: where to go next, crafting recipes, strategies..."
              style="resize: none;"
            ></textarea>
          </div>

          <!-- Activity Feed -->
          <div class="ld-section mb-4">
            <h4 class="fw-bold mb-3"><i class="bi bi-activity text-info me-2"></i>Activity Feed</h4>
            <div class="bg-dark bg-opacity-25 rounded-4 p-4 border border-secondary border-opacity-25">
              <div v-for="(act, index) in activityFeed" :key="index" class="d-flex align-items-center mb-3 pb-3 border-bottom border-secondary border-opacity-25 last-no-border">
                <div class="bg-dark bg-opacity-50 p-2 rounded-circle me-3 border border-secondary">
                  <i class="bi fs-5 text-info" :class="act.icon"></i>
                </div>
                <div>
                  <h6 class="mb-0 text-white">{{ act.text }}</h6>
                  <small class="text-muted">{{ formatDate(act.time) }}</small>
                </div>
              </div>
            </div>
          </div>

          <!-- In-Game Showcase -->
          <div v-if="purchase.status === 'playing' && game.background_image_additional" class="ld-section mb-4">
            <h4 class="fw-bold mb-3 text-success">
              <span class="spinner-grow spinner-grow-sm me-2" role="status" aria-hidden="true"></span>
              Live Session
            </h4>
            <div class="position-relative rounded-4 overflow-hidden shadow-lg border border-success">
              <img :src="game.background_image_additional" class="w-100 object-fit-cover" style="height: 250px;" />
              <div class="position-absolute bottom-0 start-0 w-100 p-3" style="background: linear-gradient(to top, rgba(0,0,0,0.9), transparent);">
                <span class="badge bg-success mb-1"><i class="bi bi-camera-fill me-1"></i> Latest Screenshot</span>
                <h6 class="text-white mb-0">Captured just now</h6>
              </div>
            </div>
          </div>
          
        </div>

        <!-- RIGHT COLUMN -->
        <div class="col-lg-4">
          
          <!-- Progress & Achievements -->
          <div class="ld-stats-card bg-dark bg-opacity-50 rounded-4 p-4 mb-4 border border-secondary border-opacity-25">
            <h5 class="fw-bold mb-4"><i class="bi bi-trophy-fill text-warning me-2"></i>Game Progress</h5>
            
            <div class="d-flex align-items-center justify-content-between mb-4">
              <span class="text-muted fw-bold">Completion</span>
              <span class="fs-4 fw-bold text-white">{{ completionPercentage }}%</span>
            </div>
            
            <!-- Simulated Progress Ring/Bar -->
            <div class="progress mb-4 bg-secondary bg-opacity-25" style="height: 12px; border-radius: 6px;">
              <div class="progress-bar bg-warning" role="progressbar" :style="{ width: completionPercentage + '%' }"></div>
            </div>
            
            <h6 class="fw-bold mb-3 mt-4 text-muted">Achievements ({{ achievements.filter(a => a.unlocked).length }}/{{ achievements.length }})</h6>
            <div class="ld-achievements-list d-flex flex-column gap-2">
              <div v-for="ach in achievements" :key="ach.id" class="d-flex align-items-center gap-3 p-2 rounded-3 bg-black bg-opacity-25" :class="{'opacity-50': !ach.unlocked}">
                <i class="bi" :class="ach.unlocked ? 'bi-check-circle-fill text-success fs-5' : 'bi-circle text-secondary fs-5'"></i>
                <span class="text-white" :class="{'text-decoration-line-through text-muted': !ach.unlocked && false}">{{ ach.title }}</span>
              </div>
            </div>
          </div>
          
          <!-- Installation Info -->
          <div v-if="purchase.status === 'installed' || purchase.status === 'playing' || purchase.status === 'completed'" class="ld-stats-card bg-dark bg-opacity-50 rounded-4 p-4 border border-secondary border-opacity-25">
            <h5 class="fw-bold mb-4"><i class="bi bi-hdd-fill text-info me-2"></i>Installation Info</h5>
            
            <div class="d-flex flex-column gap-3">
              <div class="d-flex justify-content-between">
                <span class="text-muted">Install Size</span>
                <span class="text-white fw-bold">{{ simulatedInstallSize }}</span>
              </div>
              <div class="d-flex justify-content-between">
                <span class="text-muted">Cloud Save</span>
                <span class="text-success fw-bold"><i class="bi bi-cloud-check-fill me-1"></i> Enabled</span>
              </div>
              <div class="d-flex justify-content-between">
                <span class="text-muted">Version</span>
                <span class="text-white fw-bold">v1.2.4</span>
              </div>
              <hr class="border-secondary opacity-25">
              <div>
                <span class="text-muted d-block mb-1">Install Folder</span>
                <code class="d-block p-2 bg-black bg-opacity-50 rounded-2 text-info text-truncate">C:\GameHub\Games\{{ game?.slug || game?.name?.toLowerCase().replace(/\s+/g, '-') || 'game' }}</code>
              </div>
            </div>
          </div>

          <!-- Community Stats -->
          <div class="ld-stats-card bg-dark bg-opacity-50 rounded-4 p-4 mt-4 border border-secondary border-opacity-25">
            <h5 class="fw-bold mb-4"><i class="bi bi-people-fill text-primary me-2"></i>Community</h5>
            <div class="d-flex flex-column gap-3">
              <div class="d-flex justify-content-between">
                <span class="text-muted">Metacritic</span>
                <span class="text-white fw-bold" :class="{'text-success': game.metacritic >= 80, 'text-warning': game.metacritic >= 50 && game.metacritic < 80}">{{ game.metacritic || 'N/A' }}</span>
              </div>
              <div class="d-flex justify-content-between">
                <span class="text-muted">Ratings</span>
                <span class="text-white fw-bold">{{ game.ratings_count?.toLocaleString() || '0' }}</span>
              </div>
              <div class="d-flex justify-content-between">
                <span class="text-muted">Players Now</span>
                <span class="text-success fw-bold">{{ ((game.id % 500) * 100 + 4321).toLocaleString() }}</span>
              </div>
            </div>
          </div>
          
        </div>
        
      </div>
    </div>
  </div>
  
  <div v-else-if="loading" class="text-center py-5">
    <div class="spinner-border text-primary" role="status"></div>
    <p class="mt-3 text-muted">Loading Library Details...</p>
  </div>
  
  <div v-else class="text-center py-5">
    <h3 class="text-danger">{{ error }}</h3>
    <router-link to="/library" class="btn btn-outline-secondary mt-3">Back to Library</router-link>
  </div>
</template>

<style scoped>
.ld-hero {
  height: 400px;
  overflow: hidden;
  margin-top: -70px;
}
.ld-hero-bg {
  filter: blur(8px) brightness(0.6);
  transform: scale(1.05);
}
.last-no-border:last-child {
  border-bottom: none !important;
  margin-bottom: 0 !important;
  padding-bottom: 0 !important;
}
</style>
