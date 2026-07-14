// src/views/Library.vue
<script>
import { auth, db } from '../firebase'
import { onAuthStateChanged } from 'firebase/auth'
import { collection, query, where, getDocs, orderBy } from 'firebase/firestore'
import SkeletonCard from '../components/SkeletonCard.vue'

export default {
  name: 'Library',
  components: { SkeletonCard },

  data() {
    return {
      currentUser: null,
      purchases: [],
      loading: true,
      error: null
    }
  },

  mounted() {
    onAuthStateChanged(auth, user => {
      this.currentUser = user
      if (user) {
        this.fetchLibrary()
      } else {
        this.$router.push('/login')
      }
    })
  },

  methods: {
    async fetchLibrary() {
      this.loading = true
      this.error = null
      
      try {
        const q = query(
          collection(db, 'purchases'),
          where('userId', '==', this.currentUser.uid),
          orderBy('purchasedAt', 'desc')
        )
        const snap = await getDocs(q)
        
        this.purchases = snap.docs.map(doc => ({
          id: doc.id,
          ...doc.data()
        }))
        
      } catch (err) {
        console.error('Failed to load library:', err)
        // If index is missing or other firestore error occurs, gracefully fallback
        if (err.message && err.message.includes('index')) {
          console.warn('Firestore index missing for orderBy. Falling back to client-side sort.')
          await this.fetchLibraryWithoutSort()
        } else {
          this.error = 'Failed to load your library. Please try again later.'
        }
      } finally {
        this.loading = false
      }
    },
    
    async fetchLibraryWithoutSort() {
      try {
        const q = query(
          collection(db, 'purchases'),
          where('userId', '==', this.currentUser.uid)
        )
        const snap = await getDocs(q)
        
        const results = snap.docs.map(doc => ({
          id: doc.id,
          ...doc.data()
        }))
        
        // Client side sort
        this.purchases = results.sort((a, b) => {
          const tA = a.purchasedAt?.seconds || 0
          const tB = b.purchasedAt?.seconds || 0
          return tB - tA
        })
      } catch (err) {
        console.error(err)
        this.error = 'Failed to load your library. Please try again later.'
      }
    }
  }
}
</script>

<template>
  <div class="library-page pt-5 pb-5 min-vh-100">
    <div class="container">
      
      <div class="d-flex justify-content-between align-items-end mb-5">
        <div>
          <h1 class="display-5 text-white fw-bold mb-2">My Library</h1>
          <p class="text-muted fs-5 mb-0">Games you own and can play right now.</p>
        </div>
        <div class="text-end">
          <span class="badge bg-primary fs-6 px-3 py-2 rounded-pill">{{ purchases.length }} Games</span>
        </div>
      </div>

      <!-- Error State -->
      <div v-if="error" class="alert alert-danger">
        {{ error }}
      </div>

      <!-- Loading State -->
      <div v-if="loading" class="row row-cols-1 row-cols-sm-2 row-cols-md-3 row-cols-lg-4 g-4">
        <div v-for="i in 8" :key="i" class="col">
          <SkeletonCard />
        </div>
      </div>

      <!-- Empty State -->
      <div v-else-if="purchases.length === 0" class="text-center py-5">
        <div class="empty-library-icon mb-4">
          <i class="bi bi-controller text-white-50 display-1"></i>
        </div>
        <h3 class="text-white">Your library is empty</h3>
        <p class="text-muted fs-5 mb-4">You haven't purchased any games yet. Head to the store to start your collection!</p>
        <router-link to="/games" class="btn gd-btn-primary px-5 py-3 fs-5 rounded-pill">Browse Store</router-link>
      </div>

      <!-- Library Grid -->
      <div v-else class="row row-cols-1 row-cols-sm-2 row-cols-md-3 row-cols-lg-4 g-4">
        <div 
          v-for="(game, index) in purchases" 
          :key="game.id" 
          class="col stagger-item"
          :style="{ animationDelay: (index * 0.05) + 's' }"
        >
          <div class="library-card h-100 position-relative">
            <div class="library-card-img-wrapper">
              <img 
                :src="game.thumbnail || '/placeholder.png'" 
                class="library-card-img" 
                alt="Game thumbnail"
              >
              <!-- Play Overlay -->
              <div class="play-overlay">
                <button class="btn btn-play-huge">
                  <i class="bi bi-play-fill"></i>
                </button>
              </div>
            </div>
            <div class="library-card-body p-3">
              <h5 class="text-white text-truncate mb-1" :title="game.gameName">{{ game.gameName }}</h5>
              <p class="text-muted small mb-3">
                <i class="bi bi-clock me-1"></i> 
                Purchased {{ new Date(game.purchasedAt?.seconds * 1000).toLocaleDateString() }}
              </p>
              <button class="btn btn-outline-light w-100 btn-sm rounded-pill fw-bold">
                Play Now
              </button>
            </div>
          </div>
        </div>
      </div>

    </div>
  </div>
</template>

<style scoped>
.library-card {
  background: var(--bg-glass);
  border: 1px solid var(--border-glass);
  border-radius: 16px;
  overflow: hidden;
  transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
  box-shadow: 0 4px 15px rgba(0,0,0,0.2);
}

.library-card:hover {
  transform: translateY(-8px);
  box-shadow: 0 15px 30px rgba(124, 58, 237, 0.2);
  border-color: rgba(124, 58, 237, 0.4);
}

.library-card-img-wrapper {
  position: relative;
  width: 100%;
  height: 200px;
  overflow: hidden;
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
  background: rgba(0,0,0,0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.3s ease;
  backdrop-filter: blur(2px);
}

.library-card:hover .play-overlay {
  opacity: 1;
}

.btn-play-huge {
  width: 64px;
  height: 64px;
  border-radius: 50%;
  background: #7c3aed;
  color: white;
  border: none;
  font-size: 2rem;
  display: flex;
  align-items: center;
  justify-content: center;
  transform: scale(0.8);
  transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
  box-shadow: 0 0 20px rgba(124, 58, 237, 0.6);
}

.btn-play-huge i {
  margin-left: 4px; /* visually center play icon */
}

.library-card:hover .btn-play-huge {
  transform: scale(1);
}

.btn-play-huge:hover {
  background: white;
  color: #7c3aed;
  box-shadow: 0 0 30px rgba(255, 255, 255, 0.8);
}

.gd-btn-primary {
  background: linear-gradient(135deg, #7c3aed, #4aa3ff);
  color: white;
  border: none;
  font-weight: 700;
  transition: transform 0.2s ease, box-shadow 0.2s ease, filter 0.2s ease;
}
.gd-btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(124,58,237,0.4);
  filter: brightness(1.1);
  color: white;
}

.stagger-item {
  opacity: 0;
  animation: fadeUp 0.6s cubic-bezier(0.16, 1, 0.3, 1) forwards;
}

@keyframes fadeUp {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>
