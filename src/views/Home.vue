// src/views/Home.vue
<script>
import { rawgApi, freeToGameApi, cheapSharkApi } from '../api'

const GENRES = [
  { label: 'MMORPG',       icon: 'bi-shield-shaded', color: 'violet', cat: 'mmorpg',        link: '/free-to-play' },
  { label: 'Shooter',      icon: 'bi-crosshair',     color: 'coral',  cat: 'shooter',       link: '/free-to-play' },
  { label: 'Battle Royale',icon: 'bi-trophy',        color: 'gold',   cat: 'battle-royale', link: '/free-to-play' },
  { label: 'MOBA',         icon: 'bi-people-fill',   color: 'cyan',   cat: 'moba',          link: '/free-to-play' },
  { label: 'Strategy',     icon: 'bi-grid-3x3-gap',  color: 'green',  cat: 'strategy',      link: '/free-to-play' },
  { label: 'Racing',       icon: 'bi-speedometer2',  color: 'pink',   cat: 'racing',        link: '/free-to-play' },
  { label: 'Sports',       icon: 'bi-dribbble',      color: 'cyan',   cat: 'sports',        link: '/free-to-play' },
  { label: 'Anime',        icon: 'bi-stars',         color: 'pink',   cat: 'anime',         link: '/free-to-play' },
  { label: 'Survival',     icon: 'bi-tree',          color: 'green',  cat: 'survival',      link: '/free-to-play' },
  { label: 'Fantasy',      icon: 'bi-lightning',     color: 'violet', cat: 'fantasy',       link: '/free-to-play' },
  { label: 'Sci-Fi',       icon: 'bi-rocket',        color: 'cyan',   cat: 'sci-fi',        link: '/free-to-play' },
  { label: 'Horror',       icon: 'bi-eye-slash',     color: 'coral',  cat: 'horror',        link: '/free-to-play' },
]

export default {
  data() {
    return {
      // Featured carousel (FreeToGame)
      featuredGames: [],
      activeIndex: 0,
      autoplayTimer: null,
      isAnimating: false,
      direction: 'next',
      detailCache: {},

      // New Releases strip (RAWG)
      newReleases: [],

      // Loading states
      carouselLoading: true,
      releasesLoading: true,

      // Stats counter
      statsVisible: false,
      statsObserver: null,

      // Genres
      genres: GENRES,

      // Hot Deals (CheapShark)
      hotDeals: [],
      dealsLoading: true,
    }
  },

  computed: {
    currentGame() {
      return this.featuredGames[this.activeIndex] || null
    },
    currentDetail() {
      return this.currentGame ? this.detailCache[this.currentGame.id] : null
    },
    screenshots() {
      if (this.currentDetail?.screenshots?.length) {
        return this.currentDetail.screenshots.slice(0, 4).map(s => s.image)
      }
      return this.currentGame ? Array(4).fill(this.currentGame.thumbnail) : []
    },
    shortDesc() {
      return this.currentDetail?.short_description
        || `A free-to-play ${this.currentGame?.genre || ''} experience you won't want to miss.`
    }
  },

  watch: {
    activeIndex(newIdx) {
      const game = this.featuredGames[newIdx]
      if (game && !this.detailCache[game.id]) {
        this.fetchDetail(game.id)
      }
    }
  },

  async mounted() {
    // Load featured carousel + new releases in parallel
    await Promise.allSettled([
      this.loadFeatured(),
      this.loadNewReleases(),
      this.loadHotDeals(),
    ])

    // Setup stats intersection observer
    this.$nextTick(() => {
      const statsEl = document.getElementById('stats-section')
      if (statsEl && 'IntersectionObserver' in window) {
        this.statsObserver = new IntersectionObserver(
          ([entry]) => {
            if (entry.isIntersecting) {
              this.statsVisible = true
              this.statsObserver.disconnect()
            }
          },
          { threshold: 0.3 }
        )
        this.statsObserver.observe(statsEl)
      }
    })
  },

  beforeUnmount() {
    this.stopAutoplay()
    if (this.statsObserver) this.statsObserver.disconnect()
  },

  methods: {
    async loadFeatured() {
      try {
        const { data } = await freeToGameApi.get('/games', { params: { 'sort-by': 'popularity' } })
        this.featuredGames = data.sort(() => 0.5 - Math.random()).slice(0, 10)
        if (this.featuredGames.length) {
          this.fetchDetail(this.featuredGames[0].id)
          this.$nextTick(() => this.startAutoplay())
        }
      } catch (e) {
        console.error(e)
      } finally {
        this.carouselLoading = false
      }
    },

    async loadNewReleases() {
      try {
        const { data } = await rawgApi.get('/games', {
          params: { ordering: '-released', page_size: 20, dates: '2024-01-01,2099-01-01' }
        })
        this.newReleases = data.results || []
      } catch (e) {
        console.error(e)
      } finally {
        this.releasesLoading = false
      }
    },

    async loadHotDeals() {
      try {
        const { data } = await cheapSharkApi.get('/deals', {
          params: { sortBy: 'DealRating', pageSize: 12, onSale: 1, upperPrice: 30 }
        })
        this.hotDeals = (data || []).slice(0, 8)
      } catch (e) {
        console.error(e)
      } finally {
        this.dealsLoading = false
      }
    },

    async fetchDetail(id) {
      if (this.detailCache[id]) return
      try {
        const res = await fetch(`https://www.freetogame.com/api/game?id=${id}`)
        const data = await res.json()
        this.detailCache = { ...this.detailCache, [id]: data }
      } catch {}
    },

    goTo(index, dir = 'next') {
      if (this.isAnimating || index === this.activeIndex) return
      this.direction = dir
      this.isAnimating = true
      this.activeIndex = index
      setTimeout(() => { this.isAnimating = false }, 420)
      this.resetAutoplay()
    },
    next() {
      const idx = (this.activeIndex + 1) % this.featuredGames.length
      this.goTo(idx, 'next')
    },
    prev() {
      const idx = (this.activeIndex - 1 + this.featuredGames.length) % this.featuredGames.length
      this.goTo(idx, 'prev')
    },
    startAutoplay() { this.autoplayTimer = setInterval(() => this.next(), 6000) },
    stopAutoplay()  { clearInterval(this.autoplayTimer); this.autoplayTimer = null },
    resetAutoplay() { this.stopAutoplay(); this.startAutoplay() },

    metacriticClass(score) {
      if (!score) return 'mc-grey'
      const n = parseInt(score)
      return n >= 75 ? 'mc-green' : n >= 50 ? 'mc-yellow' : 'mc-red'
    }
    ,
    formatDate(value) {
      if (!value) return '—'
      const date = new Date(value)
      if (Number.isNaN(date.getTime())) return value
      return new Intl.DateTimeFormat('en', { month: 'short', day: 'numeric', year: 'numeric' }).format(date)
    }
  }
}
</script>

<template>
  <div>

    <!-- ══════════════════════════════════════
         HERO V2 — Immersive
         ══════════════════════════════════════ -->
    <section class="hero-v2" aria-label="GameHub hero banner">
      <!-- Animated floating orbs -->
      <div class="hero-orb hero-orb-1" aria-hidden="true"></div>
      <div class="hero-orb hero-orb-2" aria-hidden="true"></div>
      <div class="hero-orb hero-orb-3" aria-hidden="true"></div>

      <div class="hero-v2-content">
        <div class="hero-eyebrow"><i class="bi bi-controller me-2"></i>The Ultimate Gaming Hub</div>

        <h1 class="hero-v2-title">
          Discover Your<br>
          <span class="gradient-text">Next Adventure</span>
        </h1>

        <p class="hero-v2-sub">
          Browse 500,000+ games, catch live news, score the best deals
          — all in one place, completely free.
        </p>

        <div class="hero-v2-actions">
          <router-link to="/games" class="btn btn-primary hero-cta-primary" aria-label="Browse all games">
            <i class="bi bi-joystick me-1"></i>Browse Games
          </router-link>
          <router-link to="/free-to-play" class="btn btn-outline-light hero-cta-secondary" aria-label="Browse free to play games">
            <i class="bi bi-gift me-1"></i>Free to Play
          </router-link>
          <router-link to="/deals" class="btn btn-outline-light hero-cta-secondary" aria-label="View game deals">
            <i class="bi bi-tag me-1"></i>Game Deals
          </router-link>
        </div>

        <!-- Inline stats -->
        <div class="hero-stats">
          <div class="hero-stat">
            <span class="hero-stat-num">500K+</span>
            <span class="hero-stat-label">Games</span>
          </div>
          <div class="hero-stat-divider"></div>
          <div class="hero-stat">
            <span class="hero-stat-num">400+</span>
            <span class="hero-stat-label">Free to Play</span>
          </div>
          <div class="hero-stat-divider"></div>
          <div class="hero-stat">
            <span class="hero-stat-num">Live</span>
            <span class="hero-stat-label">Game News</span>
          </div>
          <div class="hero-stat-divider"></div>
          <div class="hero-stat">
            <span class="hero-stat-num">100%</span>
            <span class="hero-stat-label">Free</span>
          </div>
        </div>
      </div>
    </section>

    <div class="container py-5">

      <!-- ══════════════════════════════════════
           NEW RELEASES — Horizontal Scroll Strip
           ══════════════════════════════════════ -->
      <div class="mb-5">
        <div class="section-header mb-3">
          <span class="section-icon">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/></svg>
          </span>
          <h2 class="mb-0">New Releases</h2>
          <router-link
            to="/games"
            class="ms-auto btn btn-sm"
            style="background:rgba(124,58,237,0.15); border:1px solid rgba(124,58,237,0.3); color:var(--primary-light); font-size:0.8rem; border-radius:20px; padding:4px 16px;"
          >
            View All →
          </router-link>
        </div>

        <!-- Skeleton -->
        <div v-if="releasesLoading" class="h-scroll-strip">
          <div
            v-for="n in 10" :key="n"
            class="h-scroll-card"
            style="background: var(--bg-glass);"
          >
            <div class="skeleton" style="height:120px; width:100%;"></div>
            <div class="h-scroll-card-body">
              <div class="skeleton" style="height:12px; width:80%; border-radius:4px; margin-bottom:6px;"></div>
              <div class="skeleton" style="height:10px; width:50%; border-radius:4px;"></div>
            </div>
          </div>
        </div>

        <!-- Strip -->
        <div v-else class="h-scroll-strip">
          <router-link
            v-for="game in newReleases"
            :key="game.id"
            :to="`/games/${game.id}`"
            class="h-scroll-card stagger-item"
          >
            <div class="h-scroll-img-wrap">
              <img
                v-lazy-img="game.background_image"
                :alt="game.name"
              >
              <div class="h-card-badges">
                <span v-if="game.metacritic" class="h-badge h-badge-verified">
                  <img src="/logo/star.svg" alt="Verified">Verified
                </span>
                <span v-if="game.website" class="h-badge h-badge-official">
                  <img src="/logo/search.svg" alt="Official">Official
                </span>
              </div>
            </div>
            <div class="h-scroll-card-body">
              <p class="h-scroll-card-title">{{ game.name }}</p>
              <div class="h-scroll-card-meta">
                <span
                  v-if="game.metacritic"
                  class="badge"
                  :class="metacriticClass(game.metacritic)"
                  style="font-size:0.65rem; padding:2px 6px;"
                >
                  {{ game.metacritic }}
                </span>
                <span>{{ formatDate(game.released) }}</span>
              </div>
            </div>
          </router-link>
        </div>
      </div>

      <!-- ══════════════════════════════════════
           FEATURED & RECOMMENDED — Steam Carousel
           ══════════════════════════════════════ -->
      <div class="section-header mb-3">
        <span class="section-icon">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><polygon points="12,2 15.09,8.26 22,9.27 17,14.14 18.18,21.02 12,17.77 5.82,21.02 7,14.14 2,9.27 8.91,8.26"/></svg>
        </span>
        <h2 class="mb-0">Featured &amp; Recommended</h2>
      </div>

      <!-- Skeleton -->
      <div v-if="carouselLoading" class="steam-carousel-skeleton">
        <div class="scs-main skeleton"></div>
        <div class="scs-side">
          <div class="skeleton" style="height:28px; border-radius:6px; width:75%; margin-bottom:10px;"></div>
          <div class="skeleton" style="height:14px; border-radius:4px; width:45%; margin-bottom:20px;"></div>
          <div class="scs-thumb-grid">
            <div v-for="n in 4" :key="n" class="skeleton scs-thumb-item"></div>
          </div>
          <div style="margin-top:auto; padding-top:16px;">
            <div class="skeleton" style="height:44px; border-radius:8px;"></div>
          </div>
        </div>
      </div>

      <!-- Carousel -->
      <div
        v-else-if="featuredGames.length && currentGame"
        class="steam-carousel mb-5"
        @mouseenter="stopAutoplay"
        @mouseleave="startAutoplay"
      >
        <button class="steam-arrow steam-arrow-left" @click="prev" aria-label="Previous game">‹</button>

        <div class="steam-main-panel">
          <transition :name="direction === 'next' ? 'slide-left' : 'slide-right'" mode="out-in">
            <router-link :key="currentGame.id" :to="'/free-to-play/' + currentGame.id" class="steam-hero-link">
              <img :src="currentGame.thumbnail" :alt="currentGame.title" class="steam-hero-img">
              <div class="steam-hero-overlay"></div>
            </router-link>
          </transition>
        </div>

        <transition :name="direction === 'next' ? 'fade-up' : 'fade-down'" mode="out-in">
          <div class="steam-info-panel" :key="'info-' + currentGame.id">
            <div class="steam-info-top">
              <h3 class="steam-title">{{ currentGame.title }}</h3>
              <div class="steam-meta-row">
                <span class="steam-badge-genre">{{ currentGame.genre }}</span>
                <span class="steam-badge-free">Free to Play</span>
              </div>
              <p class="steam-desc">{{ shortDesc }}</p>
            </div>

            <div class="steam-screenshots-grid">
              <template v-if="screenshots.length">
                <div v-for="(src, i) in screenshots" :key="i" class="steam-screenshot">
                  <img :src="src" :alt="`${currentGame.title} screenshot ${i + 1}`">
                </div>
              </template>
              <template v-else>
                <div v-for="n in 4" :key="n" class="steam-screenshot skeleton"></div>
              </template>
            </div>

            <div class="steam-info-bottom">
              <div class="steam-dev-info" v-if="currentDetail?.developer">
                <span class="steam-dev-label">Developer</span>
                <span class="steam-dev-value">{{ currentDetail.developer }}</span>
              </div>
              <router-link :to="'/free-to-play/' + currentGame.id" class="btn steam-play-btn">
                View Game →
              </router-link>
            </div>
          </div>
        </transition>

        <button class="steam-arrow steam-arrow-right" @click="next" aria-label="Next game">›</button>

        <div class="steam-dots">
          <button
            v-for="(game, i) in featuredGames" :key="game.id"
            class="steam-dot"
            :class="{ active: i === activeIndex }"
            @click="goTo(i, i > activeIndex ? 'next' : 'prev')"
            :aria-label="`Go to ${game.title}`"
          ></button>
        </div>
      </div>

      <!-- ══════════════════════════════════════
           GENRE EXPLORER
           ══════════════════════════════════════ -->
      <div class="mb-5">
        <div class="section-header mb-4">
          <span class="section-icon">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/></svg>
          </span>
          <h2 class="mb-0">Explore by Genre</h2>
        </div>

        <div class="genre-explorer">
          <router-link
            v-for="(g, i) in genres"
            :key="g.label"
            :to="g.link"
            :class="['genre-tile', `genre-tile-${g.color}`, 'stagger-item']"
            :style="{ animationDelay: `${i * 0.04}s` }"
            :aria-label="`Browse ${g.label} games`"
          >
            <span class="genre-tile-icon"><i :class="['bi', g.icon]"></i></span>
            <span class="genre-tile-label">{{ g.label }}</span>
          </router-link>
        </div>
      </div>

      <!-- ══════════════════════════════════════
           HOT DEALS — Horizontal Scroll Strip
           ══════════════════════════════════════ -->
      <div class="mb-5">
        <div class="section-header mb-3">
          <span class="section-icon" style="background: linear-gradient(135deg, #92400e, #f59e0b); box-shadow: 0 4px 16px rgba(245,158,11,0.4);">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M20 12V22H4V12"/><path d="M22 7H2v5h20V7z"/><path d="M12 22V7"/><path d="M12 7H7.5a2.5 2.5 0 010-5C11 2 12 7 12 7z"/><path d="M12 7h4.5a2.5 2.5 0 000-5C13 2 12 7 12 7z"/></svg>
          </span>
          <h2 class="mb-0">Hot Deals</h2>
          <router-link
            to="/deals"
            class="ms-auto btn btn-sm"
            style="background:rgba(245,158,11,0.12); border:1px solid rgba(245,158,11,0.3); color:#fbbf24; font-size:0.8rem; border-radius:20px; padding:4px 16px;"
          >
            View All →
          </router-link>
        </div>

        <!-- Skeleton -->
        <div v-if="dealsLoading" class="h-scroll-strip">
          <div v-for="n in 8" :key="n" class="deal-scroll-card" style="background: var(--bg-glass);">
            <div class="skeleton" style="height:120px; width:100%;"></div>
            <div class="h-scroll-card-body">
              <div class="skeleton" style="height:12px; width:85%; border-radius:4px; margin-bottom:6px;"></div>
              <div class="skeleton" style="height:10px; width:50%; border-radius:4px;"></div>
            </div>
          </div>
        </div>

        <!-- Deals strip -->
        <div v-else class="h-scroll-strip">
          <a
            v-for="deal in hotDeals"
            :key="deal.dealID"
            :href="`https://www.cheapshark.com/redirect?dealID=${deal.dealID}`"
            target="_blank"
            rel="noopener noreferrer"
            class="deal-scroll-card stagger-item"
            :aria-label="`${deal.title} — ${deal.salePrice === '0.00' ? 'Free' : '$' + deal.salePrice}`"
          >
            <div class="deal-scroll-img-wrap">
              <img :src="deal.thumb" :alt="deal.title" loading="lazy">
              <div class="deal-scroll-overlay" aria-hidden="true"></div>
              <span class="deal-scroll-savings">-{{ Math.round(parseFloat(deal.savings)) }}%</span>
            </div>
            <div class="h-scroll-card-body">
              <p class="h-scroll-card-title">{{ deal.title }}</p>
              <div class="deal-scroll-price">
                <span class="deal-scroll-orig">${{ deal.normalPrice }}</span>
                <span class="deal-scroll-sale">{{ deal.salePrice === '0.00' ? 'FREE' : `$${deal.salePrice}` }}</span>
              </div>
            </div>
          </a>
        </div>
      </div>

      <!-- ══════════════════════════════════════
           STATS COUNTER
           ══════════════════════════════════════ -->
      <div class="stats-section" id="stats-section">
        <div class="row text-center">
          <div class="col-6 col-md-3">
            <div class="stat-item">
              <span class="stat-number">500K+</span>
              <span class="stat-label">Games in Library</span>
            </div>
          </div>
          <div class="col-6 col-md-3">
            <div class="stat-item">
              <span class="stat-number">400+</span>
              <span class="stat-label">Free-to-Play Titles</span>
            </div>
          </div>
          <div class="col-6 col-md-3">
            <div class="stat-item">
              <span class="stat-number">24/7</span>
              <span class="stat-label">Live News Updates</span>
            </div>
          </div>
          <div class="col-6 col-md-3">
            <div class="stat-item">
              <span class="stat-number">100%</span>
              <span class="stat-label">Free to Use</span>
            </div>
          </div>
        </div>
      </div>

      <!-- ══════════════════════════════════════
           WHY GAMEHUB — Premium Feature Cards
           ══════════════════════════════════════ -->
      <div class="mb-5">
        <div class="section-header mb-4">
          <span class="section-icon">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="10"/><path d="M12 8v4M12 16h.01"/></svg>
          </span>
          <h2 class="mb-0">Why Choose <span class="gradient-text">GameHub?</span></h2>
        </div>

        <div class="row g-4">
          <div class="col-md-4">
            <div class="feature-card fc-violet">
              <span class="feature-card-icon"><i class="bi bi-joystick"></i></span>
              <h5>Massive Library</h5>
              <p>
                Discover 500,000+ titles from RAWG's database plus 400+ free-to-play games across every genre and platform imaginable.
              </p>
            </div>
          </div>
          <div class="col-md-4">
            <div class="feature-card fc-cyan">
              <span class="feature-card-icon"><i class="bi bi-broadcast"></i></span>
              <h5>Live Gaming News</h5>
              <p>
                Stay ahead with real-time gaming news from NewsAPI alongside our own curated GameHub articles and community posts.
              </p>
            </div>
          </div>
          <div class="col-md-4">
            <div class="feature-card fc-coral">
              <span class="feature-card-icon"><i class="bi bi-tag"></i></span>
              <h5>Best Deals Finder</h5>
              <p>
                Never overpay again. Our CheapShark-powered Deals page tracks the lowest prices on Steam, Epic, GOG &amp; more.
              </p>
            </div>
          </div>
          <div class="col-md-4">
            <div class="feature-card fc-violet" style="--fc-gradient: linear-gradient(135deg, rgba(6,182,212,0.12), transparent); --fc-glow: rgba(6,182,212,0.6);">
              <span class="feature-card-icon"><i class="bi bi-bookmark-heart"></i></span>
              <h5>Personal Collection</h5>
              <p>
                Save any game to your favorites. Your collection is synced to the cloud and accessible from any device.
              </p>
            </div>
          </div>
          <div class="col-md-4">
            <div class="feature-card fc-cyan" style="--fc-gradient: linear-gradient(135deg, rgba(244,63,94,0.12), transparent); --fc-glow: rgba(244,63,94,0.6);">
              <span class="feature-card-icon"><i class="bi bi-pencil-square"></i></span>
              <h5>Write Reviews</h5>
              <p>
                Share your thoughts. Leave star-rated reviews on any game and read what other players have to say.
              </p>
            </div>
          </div>
          <div class="col-md-4">
            <div class="feature-card fc-coral" style="--fc-gradient: linear-gradient(135deg, rgba(124,58,237,0.12), transparent); --fc-glow: rgba(124,58,237,0.6);">
              <span class="feature-card-icon"><i class="bi bi-globe"></i></span>
              <h5>100% Free</h5>
              <p>
                No subscriptions, no paywalls, no ads. GameHub is a community-first platform built to be free for everyone.
              </p>
            </div>
          </div>
        </div>
      </div>

    </div>
  </div>
</template>

<style scoped>
.mc-green  { background: #15803d !important; color: #fff !important; }
.mc-yellow { background: #a16207 !important; color: #fff !important; }
.mc-red    { background: #b91c1c !important; color: #fff !important; }
.mc-grey   { background: var(--bg-glass) !important; color: var(--text-muted) !important; }
.h-scroll-strip { display:flex; gap:16px; overflow-x:auto; padding-bottom:8px; }
.h-scroll-card { width:220px; flex:0 0 220px; border-radius:12px; overflow:hidden; background:var(--bg-glass); border:1px solid var(--border-glass); text-decoration:none; color:inherit; }
.h-scroll-img-wrap { position:relative; height:120px; overflow:hidden; }
.h-scroll-img-wrap img { width:100%; height:100%; object-fit:cover; display:block; }
.h-card-badges { position:absolute; left:8px; top:8px; display:flex; gap:8px; }
.h-badge { display:inline-flex; align-items:center; gap:6px; font-size:0.72rem; padding:6px 8px; border-radius:999px; color:#fff; font-weight:700; backdrop-filter:blur(6px); }
.h-badge img { width:14px; height:14px; object-fit:contain; }
.h-badge-verified { background:linear-gradient(90deg,#f59e0b,#fbbf24); box-shadow:0 6px 20px rgba(251,191,36,0.12); }
.h-badge-official { background:rgba(59,130,246,0.95); }
.h-scroll-card-body { padding:12px 14px; }
.h-scroll-card-title { font-size:0.88rem; font-weight:700; margin:0 0 6px 0; color:var(--text-primary); overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }
.h-scroll-card-meta { display:flex; gap:8px; align-items:center; font-size:0.75rem; color:var(--text-muted); }

/* Deal scroll cards */
.deal-scroll-card { width:220px; flex:0 0 220px; border-radius:12px; overflow:hidden; background:var(--bg-glass); border:1px solid var(--border-glass); text-decoration:none; color:inherit; transition:transform 0.22s ease, box-shadow 0.22s ease, border-color 0.22s ease; }
.deal-scroll-card:hover { transform:translateY(-5px); box-shadow:0 12px 32px rgba(245,158,11,0.18); border-color:rgba(245,158,11,0.3); }
.deal-scroll-img-wrap { position:relative; height:120px; overflow:hidden; }
.deal-scroll-img-wrap img { width:100%; height:100%; object-fit:cover; display:block; transition:transform 0.3s ease; }
.deal-scroll-card:hover .deal-scroll-img-wrap img { transform:scale(1.06); }
.deal-scroll-overlay { position:absolute; inset:0; background:linear-gradient(to top, rgba(10,15,30,0.7) 0%, transparent 55%); pointer-events:none; }
.deal-scroll-savings { position:absolute; top:8px; right:8px; background:linear-gradient(135deg,#15803d,#4ade80); color:#fff; font-weight:800; font-size:0.68rem; padding:3px 8px; border-radius:20px; letter-spacing:0.4px; }
.deal-scroll-price { display:flex; align-items:center; gap:8px; margin-top:4px; }
.deal-scroll-orig { text-decoration:line-through; color:var(--text-muted); font-size:0.75rem; }
.deal-scroll-sale { font-weight:800; font-size:0.95rem; color:#fbbf24; }

</style>