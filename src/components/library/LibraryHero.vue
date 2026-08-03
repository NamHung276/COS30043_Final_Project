<script>
export default {
  name: "LibraryHero",
  props: {
    game: {
      type: Object,
      required: true
    },
    purchase: {
      type: Object,
      required: true
    }
  },
  computed: {
    releaseYear() {
      if (!this.game.released) return "Unknown";
      return new Date(this.game.released).getFullYear();
    },
    developerName() {
      if (this.game.developers && this.game.developers.length > 0) {
        return this.game.developers[0].name;
      }
      return "Unknown Developer";
    },
    platformIcons() {
      if (!this.game.parent_platforms) return [];
      const iconMap = {
        pc: "bi-windows",
        playstation: "bi-playstation",
        xbox: "bi-xbox",
        nintendo: "bi-nintendo-switch",
        mac: "bi-apple",
        linux: "bi-ubuntu"
      };
      return this.game.parent_platforms.map(p => ({
        name: p.platform.name,
        icon: iconMap[p.platform.slug] || "bi-controller"
      }));
    }
  },
  methods: {
    updateStatus(status) {
      this.$emit('update-status', status);
    },
    shareGame() {
      if (navigator.share) {
        navigator.share({
          title: this.game.name,
          text: `Check out ${this.game.name} on GameHub!`,
          url: window.location.href
        });
      } else {
        navigator.clipboard.writeText(window.location.href);
        alert("Link copied to clipboard!");
      }
    }
  }
};
</script>

<template>
  <div class="library-hero position-relative overflow-hidden">
    <!-- Blurred Background Image -->
    <div class="hero-bg position-absolute w-100 h-100 top-0 start-0">
      <img :src="game.background_image" class="w-100 h-100 object-fit-cover" alt="Background" />
      <div class="hero-gradient position-absolute w-100 h-100 top-0 start-0"></div>
    </div>
    
    <!-- Hero Content -->
    <div class="container position-relative z-2 hero-content d-flex flex-column justify-content-end pb-4">
      <div class="row align-items-end g-4">
        
        <!-- Thumbnail -->
        <div class="col-auto">
          <div class="hero-thumbnail rounded-4 overflow-hidden shadow-lg border border-secondary border-opacity-25 position-relative group">
            <img :src="game.background_image" class="w-100 h-100 object-fit-cover" alt="Thumbnail" />
            <div class="thumbnail-overlay position-absolute top-0 start-0 w-100 h-100 d-flex align-items-center justify-content-center opacity-0 transition-all">
              <button class="btn btn-primary rounded-circle p-3 shadow-lg"><i class="bi bi-play-fill fs-3"></i></button>
            </div>
          </div>
        </div>
        
        <!-- Info -->
        <div class="col">
          <div class="d-flex align-items-center gap-3 mb-2">
            <span v-for="plat in platformIcons" :key="plat.name" class="text-white opacity-75" :title="plat.name">
              <i class="fs-5" :class="plat.icon"></i>
            </span>
            <span class="text-white opacity-50 px-2">•</span>
            <span class="badge bg-dark border border-secondary text-light px-3 py-2 rounded-pill">{{ releaseYear }}</span>
            <span class="text-white opacity-50 px-2">•</span>
            <span class="text-white opacity-75 fw-medium">{{ developerName }}</span>
          </div>
          
          <h1 class="hero-title fw-black text-white mb-3" style="text-shadow: 0 10px 30px rgba(0,0,0,0.8); font-size: 3.5rem; letter-spacing: -1px;">
            {{ game.name }}
          </h1>
          
          <div class="d-flex align-items-center gap-2 flex-wrap mb-4">
            <span v-for="genre in game.genres" :key="genre.name" class="badge bg-primary bg-opacity-25 text-primary-var border border-primary border-opacity-25 px-3 py-2 rounded-pill">
              {{ genre.name }}
            </span>
            <span v-if="game.esrb_rating" class="badge bg-dark bg-opacity-75 text-white border border-secondary px-3 py-2 rounded-pill ms-2">
              {{ game.esrb_rating.name }}
            </span>
          </div>
          
          <div class="d-flex align-items-center gap-3">
            <div class="dropdown">
              <button class="btn btn-dark border border-secondary dropdown-toggle rounded-pill px-4 py-2 d-flex align-items-center gap-2 shadow-lg hover-lift" type="button" data-bs-toggle="dropdown">
                <i class="bi bi-controller text-primary-var"></i>
                <span class="fw-bold">
                  <span v-if="purchase.status === 'playing'" class="text-success">Playing Now</span>
                  <span v-else-if="purchase.status === 'installed'" class="text-info">Installed</span>
                  <span v-else-if="purchase.status === 'completed'" class="text-warning">Completed</span>
                  <span v-else-if="purchase.status === 'backlog'" class="text-secondary">Backlog</span>
                  <span v-else class="text-muted">Not Installed</span>
                </span>
              </button>
              <ul class="dropdown-menu dropdown-menu-dark shadow border-secondary rounded-3">
                <li><a class="dropdown-item py-2" href="#" @click.prevent="updateStatus('installed')"><i class="bi bi-hdd-fill me-2 text-info"></i> Installed</a></li>
                <li><a class="dropdown-item py-2" href="#" @click.prevent="updateStatus('completed')"><i class="bi bi-trophy-fill me-2 text-warning"></i> Completed</a></li>
                <li><a class="dropdown-item py-2" href="#" @click.prevent="updateStatus('backlog')"><i class="bi bi-archive-fill me-2 text-secondary"></i> Backlog</a></li>
                <li><hr class="dropdown-divider border-secondary opacity-25"></li>
                <li><a class="dropdown-item py-2 text-danger" href="#" @click.prevent="updateStatus('not_installed')"><i class="bi bi-trash-fill me-2"></i> Uninstall</a></li>
              </ul>
            </div>
            
            <button class="btn btn-dark border border-secondary rounded-circle p-2 px-3 shadow-lg hover-lift" title="Favorite">
              <i class="bi bi-heart"></i>
            </button>
            <button @click="shareGame" class="btn btn-dark border border-secondary rounded-circle p-2 px-3 shadow-lg hover-lift" title="Share">
              <i class="bi bi-share"></i>
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.library-hero {
  min-height: 450px;
  background-color: var(--bg-main);
  border-bottom: 1px solid rgba(255,255,255,0.05);
}

.hero-bg img {
  filter: blur(20px) saturate(1.5) brightness(0.5);
  transform: scale(1.1); /* Prevent blur edges */
}

.hero-gradient {
  background: linear-gradient(
    to bottom,
    rgba(15, 23, 42, 0.1) 0%,
    rgba(15, 23, 42, 0.7) 60%,
    var(--bg-main) 100%
  );
}

.hero-content {
  padding-top: 200px;
}

.hero-thumbnail {
  width: 220px;
  aspect-ratio: 16/9;
  border-radius: 16px;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.hero-thumbnail:hover {
  transform: translateY(-5px) scale(1.02);
  box-shadow: 0 20px 40px rgba(0,0,0,0.5) !important;
}

.hero-thumbnail:hover .thumbnail-overlay {
  opacity: 1 !important;
  background: rgba(0,0,0,0.4);
  backdrop-filter: blur(2px);
}

.hover-lift {
  transition: transform 0.2s ease, background-color 0.2s ease;
}
.hover-lift:hover {
  transform: translateY(-3px);
  background-color: rgba(255,255,255,0.1) !important;
}

.fw-black {
  font-weight: 900;
}
</style>
