<script>
import { auth, db } from "../firebase";
import { onAuthStateChanged } from "firebase/auth";
import { collection, query, where, getDocs, updateDoc, deleteDoc, doc } from "firebase/firestore";
import SkeletonCard from "../components/SkeletonCard.vue";

export default {
  name: "Library",
  components: { SkeletonCard },

  data() {
    return {
      currentUser: null,
      purchases: [],
      loading: true,
      error: null,
      activeSessionTimer: null,
      now: Date.now(),
      // UI state
      viewMode: "grid",   // 'grid' | 'list'
      sortBy: "recent",   // 'recent' | 'playtime' | 'az' | 'status'
      searchQuery: "",
    };
  },

  computed: {
    // Total playtime across all games in seconds
    totalPlaytimeSeconds() {
      return this.purchases.reduce((sum, g) => sum + (g.playtime || 0), 0);
    },

    totalPlaytimeFormatted() {
      const total = this.totalPlaytimeSeconds;
      const h = Math.floor(total / 3600);
      const m = Math.floor((total % 3600) / 60);
      if (h > 0) return `${h}h ${m}m`;
      return `${m}m`;
    },

    installedCount() {
      return this.purchases.filter(g => g.status === 'installed' || g.status === 'playing').length;
    },

    currentlyPlaying() {
      return this.purchases.find(g => g.status === 'playing') || null;
    },

    // Recently played — games that have been played (have lastPlayed), sorted by recency
    recentlyPlayed() {
      return this.purchases
        .filter(g => g.lastPlayed)
        .sort((a, b) => {
          const tA = a.lastPlayed?.seconds || 0;
          const tB = b.lastPlayed?.seconds || 0;
          return tB - tA;
        })
        .slice(0, 6);
    },

    filteredAndSorted() {
      let list = [...this.purchases];

      // Search filter
      if (this.searchQuery.trim()) {
        const q = this.searchQuery.toLowerCase();
        list = list.filter(g => g.gameName?.toLowerCase().includes(q));
      }

      // Sort
      if (this.sortBy === 'recent') {
        list.sort((a, b) => (b.purchasedAt?.seconds || 0) - (a.purchasedAt?.seconds || 0));
      } else if (this.sortBy === 'playtime') {
        list.sort((a, b) => (b.playtime || 0) - (a.playtime || 0));
      } else if (this.sortBy === 'az') {
        list.sort((a, b) => (a.gameName || '').localeCompare(b.gameName || ''));
      } else if (this.sortBy === 'status') {
        const order = { playing: 0, installed: 1, not_installed: 2 };
        list.sort((a, b) => (order[a.status] ?? 2) - (order[b.status] ?? 2));
      }

      return list;
    },
  },

  mounted() {
    this.unsubscribe = onAuthStateChanged(auth, (user) => {
      this.currentUser = user;
      if (user) {
        this.fetchLibrary();
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
    async fetchLibrary() {
      this.loading = true;
      this.error = null;

      try {
        const q = query(
          collection(db, "purchases"),
          where("userId", "==", this.currentUser.uid),
        );
        const snap = await getDocs(q);

        const results = snap.docs.map((doc) => ({
          id: doc.id,
          ...doc.data(),
        }));

        this.purchases = results.sort((a, b) => {
          const tA = a.purchasedAt?.seconds || 0;
          const tB = b.purchasedAt?.seconds || 0;
          return tB - tA;
        });

        // Reset any hanging 'playing' states if page was reloaded
        this.purchases.forEach((g) => {
          if (g.status === 'playing') {
            g.status = 'installed';
            updateDoc(doc(db, "purchases", g.id), { status: 'installed' });
          }
        });
      } catch (err) {
        console.error("Failed to load library:", err);
        this.error = "Failed to load your library. Please try again later.";
      } finally {
        this.loading = false;
      }
    },

    formatPlaytime(seconds) {
      if (!seconds) return "0m";
      const h = Math.floor(seconds / 3600);
      const m = Math.floor((seconds % 3600) / 60);
      if (h > 0) return `${h}h ${m}m`;
      return `${m}m`;
    },

    formatSessionTime(game) {
      if (!game.sessionStart) return "00:00";
      const elapsed = Math.floor((this.now - game.sessionStart) / 1000);
      const h = Math.floor(elapsed / 3600);
      const m = Math.floor((elapsed % 3600) / 60).toString().padStart(2, '0');
      const s = (elapsed % 60).toString().padStart(2, '0');
      if (h > 0) return `${h}:${m}:${s}`;
      return `${m}:${s}`;
    },

    async installGame(game) {
      game.isInstalling = true;
      game.installProgress = 0;
      const interval = setInterval(async () => {
        game.installProgress += Math.random() * 10 + 5;
        if (game.installProgress >= 100) {
          game.installProgress = 100;
          clearInterval(interval);
          setTimeout(async () => {
            game.isInstalling = false;
            game.status = 'installed';
            await updateDoc(doc(db, "purchases", game.id), { status: 'installed' });
          }, 500);
        }
      }, 200);
    },

    async uninstallGame(game) {
      if (confirm(`Are you sure you want to uninstall ${game.gameName}?`)) {
        game.status = 'not_installed';
        await updateDoc(doc(db, "purchases", game.id), { status: 'not_installed' });
      }
    },

    async playGame(game) {
      // Stop any other game first
      for (const p of this.purchases) {
        if (p.status === 'playing' && p.id !== game.id) {
          await this.stopGame(p);
        }
      }
      game.status = 'playing';
      game.sessionStart = Date.now();
      await updateDoc(doc(db, "purchases", game.id), { status: 'playing', lastPlayed: new Date() });
    },

    async stopGame(game) {
      if (game.status !== 'playing') return;
      const elapsedSeconds = Math.floor((Date.now() - game.sessionStart) / 1000);
      const newPlaytime = (game.playtime || 0) + elapsedSeconds;

      game.status = 'installed';
      game.playtime = newPlaytime;
      game.sessionStart = null;

      await updateDoc(doc(db, "purchases", game.id), {
        status: 'installed',
        playtime: newPlaytime
      });
    },

    async refundGame(game) {
      if (confirm(`Are you sure you want to refund ${game.gameName}? This will remove it from your library permanently.`)) {
        try {
          await deleteDoc(doc(db, "purchases", game.id));
          this.purchases = this.purchases.filter(p => p.id !== game.id);
        } catch (e) {
          console.error("Refund failed", e);
        }
      }
    }
  },
};
</script>

<template>
  <div class="library-page pb-5">
    <!-- ── Hero Stats Bar ─────────────────────────── -->
    <div class="lib-hero">
      <div class="lib-hero-bg"></div>
      <div class="container lib-hero-inner">
        <div class="lib-hero-title">
          <h1>
            <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" style="vertical-align:-4px; margin-right:10px; color: var(--primary)">
              <rect x="2" y="3" width="20" height="14" rx="2"/>
              <path d="M8 21h8M12 17v4"/>
            </svg>
            My Library
          </h1>
          <p>Games you own</p>
        </div>

        <div class="lib-hero-stats">
          <div class="lib-stat">
            <span class="lib-stat-value">{{ purchases.length }}</span>
            <span class="lib-stat-label">Games Owned</span>
          </div>
          <div class="lib-stat-divider"></div>
          <div class="lib-stat">
            <span class="lib-stat-value">{{ installedCount }}</span>
            <span class="lib-stat-label">Installed</span>
          </div>
          <div class="lib-stat-divider"></div>
          <div class="lib-stat">
            <span class="lib-stat-value">{{ totalPlaytimeFormatted }}</span>
            <span class="lib-stat-label">Total Playtime</span>
          </div>
          <div class="lib-stat-divider" v-if="currentlyPlaying"></div>
          <div class="lib-stat lib-stat-playing" v-if="currentlyPlaying">
            <span class="lib-stat-playing-dot"></span>
            <span class="lib-stat-value" style="color: #10b981">Playing Now</span>
            <span class="lib-stat-label lib-stat-game-name">{{ currentlyPlaying.gameName }}</span>
          </div>
        </div>
      </div>
    </div>

    <div class="container pt-4">
      <!-- Error State -->
      <div v-if="error" class="alert alert-danger">
        {{ error }}
      </div>

      <!-- Loading State -->
      <div
        v-if="loading"
        class="row row-cols-1 row-cols-sm-2 row-cols-md-3 row-cols-lg-4 g-4"
      >
        <div v-for="i in 8" :key="i" class="col">
          <SkeletonCard />
        </div>
      </div>

      <template v-else>
        <!-- Empty State -->
        <div v-if="purchases.length === 0" class="lib-empty">
          <div class="lib-empty-icon">
            <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1" stroke-linecap="round" stroke-linejoin="round">
              <rect x="2" y="3" width="20" height="14" rx="2"/>
              <path d="M8 21h8M12 17v4"/>
            </svg>
          </div>
          <h3>Your library is empty</h3>
          <p>You haven't purchased any games yet. Head to the store to start your collection!</p>
          <router-link to="/games" class="btn lib-btn-primary px-5 py-3 fs-5 rounded-pill">
            Browse Store
          </router-link>
        </div>

        <template v-else>
          <!-- ── Recently Played Section ─────────────── -->
          <div v-if="recentlyPlayed.length" class="lib-section mb-5">
            <div class="lib-section-header mb-3">
              <h2 class="lib-section-title">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
                Recently Played
              </h2>
            </div>
            <div class="lib-recent-strip">
              <div
                v-for="game in recentlyPlayed"
                :key="'recent-' + game.id"
                class="lib-recent-card"
                :class="{ 'is-playing': game.status === 'playing' }"
                @click="game.status === 'installed' ? playGame(game) : (game.status === 'playing' ? stopGame(game) : null)"
              >
                <div class="lib-recent-img">
                  <img :src="game.thumbnail || '/placeholder.png'" :alt="game.gameName" />
                  <div class="lib-recent-overlay">
                    <div class="lib-recent-play-btn" v-if="game.status === 'installed'">
                      <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor"><polygon points="5 3 19 12 5 21 5 3"/></svg>
                    </div>
                    <div class="lib-recent-stop-btn" v-else-if="game.status === 'playing'">
                      <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor"><rect x="6" y="4" width="4" height="16"/><rect x="14" y="4" width="4" height="16"/></svg>
                    </div>
                  </div>
                  <div class="lib-recent-playing-badge" v-if="game.status === 'playing'">
                    <span class="lib-playing-dot"></span> Playing
                  </div>
                </div>
                <div class="lib-recent-name" :title="game.gameName">{{ game.gameName }}</div>
                <div class="lib-recent-playtime">
                  <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
                  {{ formatPlaytime(game.playtime || 0) }}
                </div>
              </div>
            </div>
          </div>

          <!-- ── All Games Section ─────────────────── -->
          <div class="lib-section">
            <!-- Controls -->
            <div class="lib-controls mb-4">
              <h2 class="lib-section-title">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><rect x="2" y="3" width="20" height="14" rx="2"/><path d="M8 21h8M12 17v4"/></svg>
                All Games
                <span class="lib-count-badge">{{ filteredAndSorted.length }}</span>
              </h2>

              <div class="lib-controls-right">
                <!-- Search -->
                <div class="lib-search">
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" aria-hidden="true"><circle cx="11" cy="11" r="8"/><path d="M21 21l-4.35-4.35"/></svg>
                  <input
                    v-model="searchQuery"
                    type="text"
                    placeholder="Search library..."
                    class="lib-search-input"
                    aria-label="Search your library"
                  />
                </div>

                <!-- Sort -->
                <select v-model="sortBy" class="lib-sort-select" aria-label="Sort games">
                  <option value="recent">Recently Added</option>
                  <option value="playtime">Most Played</option>
                  <option value="az">A – Z</option>
                  <option value="status">By Status</option>
                </select>

                <!-- View Mode Toggle -->
                <div class="lib-view-toggle">
                  <button
                    class="lib-view-btn"
                    :class="{ active: viewMode === 'grid' }"
                    @click="viewMode = 'grid'"
                    aria-label="Grid view"
                    title="Grid view"
                  >
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor"><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/></svg>
                  </button>
                  <button
                    class="lib-view-btn"
                    :class="{ active: viewMode === 'list' }"
                    @click="viewMode = 'list'"
                    aria-label="List view"
                    title="List view"
                  >
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><line x1="3" y1="6" x2="21" y2="6"/><line x1="3" y1="12" x2="21" y2="12"/><line x1="3" y1="18" x2="21" y2="18"/></svg>
                  </button>
                </div>
              </div>
            </div>

            <!-- Grid View -->
            <div
              v-if="viewMode === 'grid'"
              class="row row-cols-1 row-cols-sm-2 row-cols-md-3 row-cols-lg-4 g-4"
            >
              <div
                v-for="(game, index) in filteredAndSorted"
                :key="game.id"
                class="col stagger-item"
                :style="{ animationDelay: index * 0.04 + 's' }"
              >
                <div class="library-card h-100 position-relative" :class="{'is-playing': game.status === 'playing'}">
                  <div class="library-card-img-wrapper">
                    <img
                      :src="game.thumbnail || '/placeholder.png'"
                      class="library-card-img"
                      alt="Game thumbnail"
                    />
                    <!-- Play Overlay (Only show if installed and not playing) -->
                    <div v-if="game.status === 'installed'" class="play-overlay" @click="playGame(game)">
                      <button class="btn-play-huge">
                        <svg width="22" height="22" viewBox="0 0 24 24" fill="currentColor"><polygon points="5 3 19 12 5 21 5 3"/></svg>
                      </button>
                    </div>
                    <!-- Playing badge -->
                    <div v-if="game.status === 'playing'" class="playing-badge">
                      <span class="playing-dot"></span> Playing
                    </div>
                  </div>

                  <div class="library-card-body p-3 d-flex flex-column" style="flex: 1;">
                    <h5 class="text-truncate mb-1" style="color: var(--text-primary)" :title="game.gameName">
                      {{ game.gameName }}
                    </h5>
                    <p class="text-muted small mb-3 d-flex justify-content-between align-items-center">
                      <span>
                        <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="vertical-align:-1px; margin-right:3px"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
                        {{ formatPlaytime(game.playtime || 0) }}
                      </span>
                      <span v-if="game.status === 'installed' || game.status === 'playing'" class="text-success small">
                        <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" style="vertical-align:-1px"><polyline points="20 6 9 17 4 12"/></svg>
                        Installed
                      </span>
                      <span v-else class="text-secondary small">Not Installed</span>
                    </p>

                    <div class="mt-auto pt-2">
                      <!-- NOT INSTALLED -->
                      <div v-if="!game.status || game.status === 'not_installed'">
                        <button v-if="!game.isInstalling" @click="installGame(game)" class="btn btn-outline-info w-100 btn-sm rounded-pill fw-bold">
                          <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" style="vertical-align:-1px; margin-right:4px"><path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>
                          Install
                        </button>
                        <div v-else class="progress mt-1" style="height: 31px; border-radius: 15.5px; background: rgba(255,255,255,0.1);">
                          <div class="progress-bar progress-bar-striped progress-bar-animated bg-info text-dark fw-bold" role="progressbar" :style="{ width: game.installProgress + '%' }">
                            Installing {{ Math.floor(game.installProgress) }}%
                          </div>
                        </div>
                      </div>

                      <!-- INSTALLED -->
                      <div v-else-if="game.status === 'installed'" class="d-flex gap-2">
                        <button @click="playGame(game)" class="btn btn-success flex-grow-1 btn-sm rounded-pill fw-bold">
                          <svg width="13" height="13" viewBox="0 0 24 24" fill="currentColor" style="vertical-align:-1px; margin-right:4px"><polygon points="5 3 19 12 5 21 5 3"/></svg>
                          Play
                        </button>
                        <div class="dropdown">
                          <button class="btn btn-outline-secondary btn-sm rounded-circle dropdown-toggle no-caret d-flex align-items-center justify-content-center" type="button" data-bs-toggle="dropdown" aria-expanded="false" style="width:31px; height:31px;">
                            <svg width="13" height="13" viewBox="0 0 24 24" fill="currentColor"><circle cx="12" cy="5" r="1.5"/><circle cx="12" cy="12" r="1.5"/><circle cx="12" cy="19" r="1.5"/></svg>
                          </button>
                          <ul class="dropdown-menu dropdown-menu-end shadow border-secondary">
                            <li><a class="dropdown-item text-danger" href="#" @click.prevent="uninstallGame(game)">
                              <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="vertical-align:-1px; margin-right:6px"><polyline points="3 6 5 6 21 6"/><path d="M19 6l-1 14a2 2 0 01-2 2H8a2 2 0 01-2-2L5 6"/><path d="M10 11v6M14 11v6"/></svg>
                              Uninstall
                            </a></li>
                            <li><hr class="dropdown-divider border-secondary"></li>
                            <li><a class="dropdown-item text-warning" href="#" @click.prevent="refundGame(game)">
                              <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="vertical-align:-1px; margin-right:6px"><polyline points="1 4 1 10 7 10"/><path d="M3.51 15a9 9 0 102.13-9.36L1 10"/></svg>
                              Refund
                            </a></li>
                          </ul>
                        </div>
                      </div>

                      <!-- PLAYING -->
                      <div v-else-if="game.status === 'playing'">
                        <button @click="stopGame(game)" class="btn btn-danger w-100 btn-sm rounded-pill fw-bold position-relative overflow-hidden playing-btn">
                          <div class="playing-pulse"></div>
                          <span class="position-relative z-1">
                            <svg width="11" height="11" viewBox="0 0 24 24" fill="currentColor" style="vertical-align:-1px; margin-right:4px"><rect x="6" y="4" width="4" height="16"/><rect x="14" y="4" width="4" height="16"/></svg>
                            Stop ({{ formatSessionTime(game) }})
                          </span>
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- List View -->
            <div v-else class="lib-list-view">
              <div
                v-for="(game, index) in filteredAndSorted"
                :key="game.id"
                class="lib-list-item stagger-item"
                :class="{ 'is-playing': game.status === 'playing' }"
                :style="{ animationDelay: index * 0.03 + 's' }"
              >
                <div class="lib-list-img">
                  <img :src="game.thumbnail || '/placeholder.png'" :alt="game.gameName" />
                  <div class="playing-badge-sm" v-if="game.status === 'playing'">
                    <span class="playing-dot"></span>
                  </div>
                </div>
                <div class="lib-list-info">
                  <span class="lib-list-name" :title="game.gameName">{{ game.gameName }}</span>
                  <span class="lib-list-playtime">
                    <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="vertical-align:-1px; margin-right:3px"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
                    {{ formatPlaytime(game.playtime || 0) }}
                  </span>
                </div>
                <div class="lib-list-status">
                  <span v-if="game.status === 'playing'" class="lib-status-chip playing">Playing</span>
                  <span v-else-if="game.status === 'installed'" class="lib-status-chip installed">Installed</span>
                  <span v-else class="lib-status-chip not-installed">Not Installed</span>
                </div>
                <div class="lib-list-actions">
                  <!-- NOT INSTALLED -->
                  <button v-if="!game.status || game.status === 'not_installed'" @click="installGame(game)" class="btn btn-outline-info btn-sm rounded-pill">
                    <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" style="vertical-align:-1px; margin-right:3px"><path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>
                    Install
                  </button>
                  <!-- INSTALLED -->
                  <button v-else-if="game.status === 'installed'" @click="playGame(game)" class="btn btn-success btn-sm rounded-pill">
                    <svg width="12" height="12" viewBox="0 0 24 24" fill="currentColor" style="vertical-align:-1px; margin-right:3px"><polygon points="5 3 19 12 5 21 5 3"/></svg>
                    Play
                  </button>
                  <!-- PLAYING -->
                  <button v-else-if="game.status === 'playing'" @click="stopGame(game)" class="btn btn-danger btn-sm rounded-pill">
                    <svg width="11" height="11" viewBox="0 0 24 24" fill="currentColor" style="vertical-align:-1px; margin-right:3px"><rect x="6" y="4" width="4" height="16"/><rect x="14" y="4" width="4" height="16"/></svg>
                    Stop ({{ formatSessionTime(game) }})
                  </button>
                </div>
              </div>

              <div v-if="filteredAndSorted.length === 0 && searchQuery" class="text-center py-5 text-muted">
                No games match "{{ searchQuery }}"
              </div>
            </div>

          </div>
        </template>
      </template>
    </div>
  </div>
</template>

<style scoped>
/* ── Hero Stats Bar ─────────────────────────────── */
.lib-hero {
  position: relative;
  padding: 40px 0 32px;
  margin-bottom: 0;
  overflow: hidden;
}

.lib-hero-bg {
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, rgba(14,165,233,0.08) 0%, rgba(139,92,246,0.06) 50%, transparent 100%);
  border-bottom: 1px solid rgba(255,255,255,0.06);
}

.lib-hero-inner {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 24px;
}

.lib-hero-title h1 {
  font-size: 1.85rem;
  font-weight: 800;
  color: var(--text-primary);
  margin-bottom: 4px;
}

.lib-hero-title p {
  color: var(--text-muted);
  margin: 0;
  font-size: 0.9rem;
}

.lib-hero-stats {
  display: flex;
  align-items: center;
  gap: 24px;
  background: rgba(255,255,255,0.04);
  border: 1px solid rgba(255,255,255,0.07);
  border-radius: 14px;
  padding: 16px 24px;
}

.lib-stat {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
}

.lib-stat-playing {
  flex-direction: row;
  align-items: center;
  gap: 8px;
}

.lib-stat-value {
  font-family: var(--font-display);
  font-size: 1.3rem;
  font-weight: 800;
  color: var(--text-primary);
  line-height: 1.2;
}

.lib-stat-label {
  font-size: 0.72rem;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.06em;
  font-weight: 600;
}

.lib-stat-game-name {
  font-size: 0.75rem;
  text-transform: none;
  letter-spacing: 0;
  color: var(--text-secondary);
}

.lib-stat-divider {
  width: 1px;
  height: 36px;
  background: rgba(255,255,255,0.08);
}

.lib-stat-playing-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #10b981;
  box-shadow: 0 0 10px rgba(16,185,129,0.6);
  animation: pulse-dot 1.5s infinite;
  flex-shrink: 0;
}

@keyframes pulse-dot {
  0%, 100% { box-shadow: 0 0 6px rgba(16,185,129,0.5); }
  50% { box-shadow: 0 0 16px rgba(16,185,129,0.9); }
}

@media (max-width: 768px) {
  .lib-hero-inner { flex-direction: column; align-items: flex-start; }
  .lib-hero-stats { width: 100%; justify-content: space-around; flex-wrap: wrap; }
}

/* ── Section headers ────────────────────────────── */
.lib-section-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 1.1rem;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0;
}

.lib-section-title svg {
  color: var(--primary);
}

.lib-count-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 22px;
  height: 22px;
  background: rgba(14,165,233,0.15);
  border: 1px solid rgba(14,165,233,0.25);
  border-radius: 999px;
  font-size: 0.72rem;
  font-weight: 700;
  color: var(--primary);
  padding: 0 6px;
}

/* ── Recently Played Strip ──────────────────────── */
.lib-section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.lib-recent-strip {
  display: flex;
  gap: 16px;
  overflow-x: auto;
  padding-bottom: 8px;
  scrollbar-width: none;
}
.lib-recent-strip::-webkit-scrollbar { display: none; }

.lib-recent-card {
  flex: 0 0 160px;
  width: 160px;
  border-radius: 10px;
  overflow: hidden;
  background: var(--bg-glass);
  border: 1px solid var(--border-glass);
  cursor: pointer;
  transition: all 0.25s ease;
}

.lib-recent-card:hover {
  transform: translateY(-4px);
  border-color: rgba(14,165,233,0.3);
  box-shadow: 0 10px 25px rgba(0,0,0,0.3);
}

.lib-recent-card.is-playing {
  border-color: rgba(16,185,129,0.5);
  box-shadow: 0 0 20px rgba(16,185,129,0.15);
}

.lib-recent-img {
  position: relative;
  height: 100px;
  overflow: hidden;
}

.lib-recent-img img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s ease;
}

.lib-recent-card:hover .lib-recent-img img {
  transform: scale(1.05);
}

.lib-recent-overlay {
  position: absolute;
  inset: 0;
  background: rgba(0,0,0,0.4);
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.2s ease;
}

.lib-recent-card:hover .lib-recent-overlay {
  opacity: 1;
}

.lib-recent-play-btn,
.lib-recent-stop-btn {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: rgba(16,185,129,0.9);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 0 20px rgba(16,185,129,0.6);
  transition: transform 0.2s cubic-bezier(0.34,1.56,0.64,1);
}

.lib-recent-stop-btn {
  background: rgba(239,68,68,0.9);
  box-shadow: 0 0 20px rgba(239,68,68,0.6);
}

.lib-recent-card:hover .lib-recent-play-btn,
.lib-recent-card:hover .lib-recent-stop-btn {
  transform: scale(1.1);
}

.lib-recent-playing-badge {
  position: absolute;
  top: 6px;
  left: 6px;
  background: rgba(16,185,129,0.9);
  color: #fff;
  font-size: 0.68rem;
  font-weight: 700;
  padding: 2px 8px;
  border-radius: 999px;
  display: flex;
  align-items: center;
  gap: 5px;
  backdrop-filter: blur(4px);
}

.lib-recent-name {
  font-size: 0.8rem;
  font-weight: 600;
  color: var(--text-primary);
  padding: 8px 10px 2px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.lib-recent-playtime {
  font-size: 0.72rem;
  color: var(--text-muted);
  padding: 0 10px 8px;
  display: flex;
  align-items: center;
  gap: 4px;
}

/* ── Controls Bar ───────────────────────────────── */
.lib-controls {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 12px;
}

.lib-controls-right {
  display: flex;
  align-items: center;
  gap: 10px;
}

.lib-search {
  display: flex;
  align-items: center;
  gap: 8px;
  background: rgba(255,255,255,0.05);
  border: 1px solid rgba(255,255,255,0.09);
  border-radius: 8px;
  padding: 6px 12px;
  color: var(--text-muted);
}

.lib-search:focus-within {
  border-color: var(--primary);
  background: rgba(255,255,255,0.08);
}

.lib-search-input {
  background: transparent;
  border: none;
  outline: none;
  color: var(--text-primary);
  font-size: 0.83rem;
  font-family: var(--font-family);
  width: 180px;
}

.lib-search-input::placeholder {
  color: var(--text-muted);
}

.lib-sort-select {
  background: rgba(255,255,255,0.05);
  border: 1px solid rgba(255,255,255,0.09);
  border-radius: 8px;
  color: var(--text-primary);
  font-size: 0.83rem;
  font-family: var(--font-family);
  padding: 6px 10px;
  outline: none;
  cursor: pointer;
  transition: border-color 0.2s;
}

.lib-sort-select:focus {
  border-color: var(--primary);
}

.lib-view-toggle {
  display: flex;
  background: rgba(255,255,255,0.04);
  border: 1px solid rgba(255,255,255,0.08);
  border-radius: 8px;
  overflow: hidden;
}

.lib-view-btn {
  background: transparent;
  border: none;
  color: var(--text-muted);
  padding: 7px 11px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.18s ease;
}

.lib-view-btn.active {
  background: rgba(14,165,233,0.15);
  color: var(--primary);
}

.lib-view-btn:hover:not(.active) {
  background: rgba(255,255,255,0.06);
  color: var(--text-primary);
}

/* ── Library Grid Cards ─────────────────────────── */
.library-card {
  background: var(--bg-glass);
  border: 1px solid var(--border-glass);
  border-radius: 16px;
  overflow: hidden;
  transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
  display: flex;
  flex-direction: column;
}

.library-card:hover {
  transform: translateY(-8px);
  box-shadow: 0 15px 30px rgba(124, 58, 237, 0.2);
  border-color: rgba(124, 58, 237, 0.4);
}

.library-card.is-playing {
  border-color: rgba(16,185,129,0.5) !important;
  box-shadow: 0 0 25px rgba(16,185,129,0.2) !important;
}

.library-card-img-wrapper {
  position: relative;
  width: 100%;
  height: 200px;
  overflow: hidden;
  flex-shrink: 0;
}

.library-card-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.5s ease;
}

.library-card:hover .library-card-img {
  transform: scale(1.05);
}

.play-overlay {
  position: absolute;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.3s ease;
  backdrop-filter: blur(2px);
  cursor: pointer;
}

.library-card:hover .play-overlay {
  opacity: 1;
}

.btn-play-huge {
  width: 64px;
  height: 64px;
  border-radius: 50%;
  background: #10b981;
  color: white;
  border: none;
  display: flex;
  align-items: center;
  justify-content: center;
  transform: scale(0.8);
  transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
  box-shadow: 0 0 20px rgba(16, 185, 129, 0.6);
  cursor: pointer;
}

.library-card:hover .btn-play-huge {
  transform: scale(1);
}

.btn-play-huge:hover {
  background: white;
  color: #10b981;
  box-shadow: 0 0 30px rgba(255, 255, 255, 0.8);
}

.playing-badge {
  position: absolute;
  top: 8px;
  left: 8px;
  background: rgba(16,185,129,0.9);
  color: #fff;
  font-size: 0.68rem;
  font-weight: 700;
  padding: 3px 10px;
  border-radius: 999px;
  display: flex;
  align-items: center;
  gap: 5px;
  backdrop-filter: blur(4px);
}

.playing-dot, .lib-playing-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: #fff;
  display: inline-block;
  animation: blink-dot 1s infinite;
}

@keyframes blink-dot {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.3; }
}

.library-card-body {
  display: flex;
  flex-direction: column;
}

/* ── List View ──────────────────────────────────── */
.lib-list-view {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.lib-list-item {
  display: flex;
  align-items: center;
  gap: 16px;
  background: var(--bg-glass);
  border: 1px solid var(--border-glass);
  border-radius: 12px;
  padding: 12px 16px;
  transition: all 0.2s ease;
}

.lib-list-item:hover {
  border-color: rgba(14,165,233,0.25);
  background: var(--bg-glass-hover);
}

.lib-list-item.is-playing {
  border-color: rgba(16,185,129,0.4);
  background: rgba(16,185,129,0.04);
}

.lib-list-img {
  width: 72px;
  height: 45px;
  border-radius: 7px;
  overflow: hidden;
  flex-shrink: 0;
  position: relative;
}

.lib-list-img img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

.playing-badge-sm {
  position: absolute;
  top: 4px;
  left: 4px;
}

.lib-list-info {
  flex: 1;
  min-width: 0;
}

.lib-list-name {
  display: block;
  font-size: 0.9rem;
  font-weight: 600;
  color: var(--text-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.lib-list-playtime {
  display: flex;
  align-items: center;
  font-size: 0.75rem;
  color: var(--text-muted);
  margin-top: 2px;
}

.lib-list-status {
  flex-shrink: 0;
}

.lib-status-chip {
  display: inline-flex;
  align-items: center;
  padding: 3px 10px;
  border-radius: 999px;
  font-size: 0.72rem;
  font-weight: 600;
}

.lib-status-chip.playing {
  background: rgba(16,185,129,0.15);
  color: #10b981;
  border: 1px solid rgba(16,185,129,0.3);
}

.lib-status-chip.installed {
  background: rgba(14,165,233,0.1);
  color: var(--primary);
  border: 1px solid rgba(14,165,233,0.2);
}

.lib-status-chip.not-installed {
  background: rgba(255,255,255,0.05);
  color: var(--text-muted);
  border: 1px solid rgba(255,255,255,0.08);
}

.lib-list-actions {
  flex-shrink: 0;
}

/* ── Empty State ────────────────────────────────── */
.lib-empty {
  text-align: center;
  padding: 80px 20px;
}

.lib-empty-icon {
  color: rgba(255,255,255,0.1);
  margin-bottom: 24px;
}

.lib-empty h3 {
  color: var(--text-primary);
  margin-bottom: 12px;
}

.lib-empty p {
  color: var(--text-secondary);
  font-size: 1.05rem;
  margin-bottom: 32px;
  max-width: 460px;
  margin-left: auto;
  margin-right: auto;
}

.lib-btn-primary {
  background: linear-gradient(135deg, #7c3aed, #4aa3ff);
  color: white;
  border: none;
  font-weight: 700;
  transition: transform 0.2s ease, box-shadow 0.2s ease, filter 0.2s ease;
}

.lib-btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(124, 58, 237, 0.4);
  filter: brightness(1.1);
  color: white;
}

/* ── Animations ─────────────────────────────────── */
.stagger-item {
  opacity: 0;
  animation: fadeUp 0.6s cubic-bezier(0.16, 1, 0.3, 1) forwards;
}

@keyframes fadeUp {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

.playing-btn {
  background: #ef4444;
  border: none;
}

.playing-pulse {
  position: absolute;
  top: 0; left: 0; right: 0; bottom: 0;
  background: linear-gradient(90deg, rgba(255,255,255,0) 0%, rgba(255,255,255,0.2) 50%, rgba(255,255,255,0) 100%);
  animation: pulse-slide 1.5s infinite linear;
  background-size: 200% 100%;
}

@keyframes pulse-slide {
  0% { background-position: -200% 0; }
  100% { background-position: 200% 0; }
}

.no-caret::after {
  display: none !important;
}

.dropdown-menu {
  z-index: 1050;
}
</style>
