<!-- src/components/TrailerModal.vue -->
<!-- Reusable trailer modal: supports YouTube embed ID or direct video URL -->
<template>
  <teleport to="body">
    <transition name="trailer-modal">
      <div
        v-if="show"
        class="tm-backdrop"
        @click.self="$emit('close')"
        role="dialog"
        aria-modal="true"
        :aria-label="`${title} trailer`"
      >
        <div class="tm-container">
          <!-- Header -->
          <div class="tm-header">
            <div class="tm-title-row">
              <span class="tm-play-icon">▶</span>
              <span class="tm-title">{{ title || "Game Trailer" }}</span>
              <span v-if="isYoutubeFallback" class="tm-yt-badge" title="Trailer sourced from YouTube">
                <svg viewBox="0 0 24 24" fill="currentColor" width="14" height="14"><path d="M23.498 6.186a3.016 3.016 0 0 0-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 0 0 .502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 0 0 2.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 0 0 2.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814zM9.545 15.568V8.432L15.818 12l-6.273 3.568z"/></svg>
                via YouTube
              </span>
            </div>
            <button
              class="tm-close"
              @click="$emit('close')"
              aria-label="Close trailer"
            >
              ✕
            </button>
          </div>

          <!-- YouTube embed -->
          <div class="tm-video-wrap" v-if="youtubeId">
            <iframe
              :src="`https://www.youtube.com/embed/${youtubeId}?autoplay=1&rel=0&modestbranding=1`"
              frameborder="0"
              allow="
                accelerometer;
                autoplay;
                clipboard-write;
                encrypted-media;
                gyroscope;
                picture-in-picture;
              "
              allowfullscreen
              class="tm-iframe"
              :title="`${title} trailer`"
            ></iframe>
          </div>

          <!-- Direct video URL -->
          <div class="tm-video-wrap" v-else-if="videoUrl">
            <video
              :src="videoUrl"
              :poster="posterUrl"
              controls
              autoplay
              class="tm-video"
            ></video>
          </div>

          <!-- Fallback -->
          <div v-else class="tm-no-trailer">
            <span>🎬</span>
            <p>No trailer available for this game.</p>
          </div>
        </div>
      </div>
    </transition>
  </teleport>
</template>

<script>
export default {
  name: "TrailerModal",
  emits: ["close"],

  props: {
    show: {
      type: Boolean,
      default: false,
    },
    youtubeId: {
      type: String,
      default: null,
    },
    videoUrl: {
      type: String,
      default: null,
    },
    posterUrl: {
      type: String,
      default: null,
    },
    title: {
      type: String,
      default: "",
    },
    /** When true, shows a 'via YouTube' badge in the header to indicate this is a fallback */
    isYoutubeFallback: {
      type: Boolean,
      default: false,
    },
  },

  watch: {
    show(val) {
      if (val) {
        document.addEventListener("keydown", this.onKeydown);
        document.body.style.overflow = "hidden";
      } else {
        document.removeEventListener("keydown", this.onKeydown);
        document.body.style.overflow = "";
      }
    },
  },

  methods: {
    onKeydown(e) {
      if (e.key === "Escape") this.$emit("close");
    },
  },

  beforeUnmount() {
    document.removeEventListener("keydown", this.onKeydown);
    document.body.style.overflow = "";
  },
};
</script>

<style scoped>
.tm-backdrop {
  position: fixed;
  inset: 0;
  z-index: 9999;
  background: rgba(0, 0, 0, 0.92);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
  backdrop-filter: blur(6px);
}

.tm-container {
  width: 100%;
  max-width: 900px;
  background: #0d1117;
  border-radius: 16px;
  overflow: hidden;
  border: 1px solid var(--overlay-medium);
  box-shadow: 0 40px 120px rgba(0, 0, 0, 0.9);
}

.tm-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px;
  background: var(--overlay-light);
  border-bottom: 1px solid var(--overlay-medium);
}

.tm-title-row {
  display: flex;
  align-items: center;
  gap: 10px;
}

.tm-play-icon {
  width: 28px;
  height: 28px;
  background: linear-gradient(135deg, #7c3aed, #06b6d4);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.7rem;
  color: white;
  flex-shrink: 0;
}

.tm-title {
  font-size: 0.95rem;
  font-weight: 700;
  color: var(--text-primary);
  letter-spacing: 0.02em;
}

.tm-yt-badge {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  background: rgba(255, 0, 0, 0.15);
  border: 1px solid rgba(255, 0, 0, 0.3);
  color: #ff6b6b;
  font-size: 0.65rem;
  font-weight: 600;
  padding: 2px 7px;
  border-radius: 10px;
  white-space: nowrap;
}

.tm-close {
  width: 32px;
  height: 32px;
  border: none;
  background: var(--overlay-medium);
  color: var(--overlay-text);
  border-radius: 8px;
  cursor: pointer;
  font-size: 0.85rem;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
}
.tm-close:hover {
  background: rgba(239, 68, 68, 0.3);
  color: var(--text-primary);
}

.tm-video-wrap {
  position: relative;
  width: 100%;
  aspect-ratio: 16 / 9;
  background: #000;
}

.tm-iframe,
.tm-video {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.tm-no-trailer {
  padding: 60px 20px;
  text-align: center;
  color: var(--overlay-text-muted);
}
.tm-no-trailer span {
  font-size: 3rem;
  display: block;
  margin-bottom: 12px;
}
.tm-no-trailer p {
  margin: 0;
  font-size: 0.95rem;
}

/* Transition */
.trailer-modal-enter-active,
.trailer-modal-leave-active {
  transition: opacity 0.25s ease;
}
.trailer-modal-enter-active .tm-container,
.trailer-modal-leave-active .tm-container {
  transition:
    transform 0.3s cubic-bezier(0.34, 1.56, 0.64, 1),
    opacity 0.25s;
}
.trailer-modal-enter-from {
  opacity: 0;
}
.trailer-modal-enter-from .tm-container {
  transform: scale(0.92);
  opacity: 0;
}
.trailer-modal-leave-to {
  opacity: 0;
}
.trailer-modal-leave-to .tm-container {
  transform: scale(0.95);
  opacity: 0;
}
</style>
