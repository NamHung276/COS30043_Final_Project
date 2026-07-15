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
  border: 1px solid rgba(255, 255, 255, 0.1);
  box-shadow: 0 40px 120px rgba(0, 0, 0, 0.9);
}

.tm-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px;
  background: rgba(255, 255, 255, 0.04);
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
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
  color: #fff;
  letter-spacing: 0.02em;
}

.tm-close {
  width: 32px;
  height: 32px;
  border: none;
  background: rgba(255, 255, 255, 0.08);
  color: rgba(255, 255, 255, 0.7);
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
  color: #fff;
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
  color: rgba(255, 255, 255, 0.4);
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
