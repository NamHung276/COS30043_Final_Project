// src/components/ToastNotification.vue
<script>
export default {
  name: 'ToastNotification',

  data() {
    return {
      toasts: [],
      maxVisible: 5,
      queue: []
    }
  },

  methods: {
    show(message, type = 'info', duration = 3000, action = null) {
      // 1. Prevent duplicate toasts
      const existing = this.toasts.find(
        t => t.message === message && t.type === type
      )
      if (existing) return
      
      const existingInQueue = this.queue.find(
        t => t.message === message && t.type === type
      )
      if (existingInQueue) return

      // 6 & 12. Move icons into data
      const icons = {
        success: '/logo/check_mark.png',
        error: '/logo/cross_mark.png',
        warning: '/logo/warning_sign.png',
        info: '/logo/information_logo.png'
      }

      // 4. Better ID generation
      const id = (window.crypto && crypto.randomUUID)
        ? crypto.randomUUID() 
        : Date.now() + Math.random()

      const newToast = {
        id,
        message,
        type,
        icon: icons[type] || icons.info,
        duration,
        action,
        remainingTime: duration,
        timerId: null,
        lastTick: null
      }

      // 5 & 10. Queue system
      if (this.toasts.length >= this.maxVisible) {
        this.queue.push(newToast)
      } else {
        this.addToast(newToast)
      }
    },

    addToast(toast) {
      this.toasts.push(toast)
      this.startTimer(toast)
    },

    // 2. Pause timer while hovering & 3. Progress bar logic
    startTimer(toast) {
      if (toast.duration <= 0) return // 0 means indefinite
      toast.lastTick = Date.now()
      toast.timerId = setInterval(() => {
        const now = Date.now()
        toast.remainingTime -= (now - toast.lastTick)
        toast.lastTick = now

        if (toast.remainingTime <= 0) {
          this.dismiss(toast.id)
        }
      }, 16) // ~60fps for smooth progress bar
    },

    pauseTimer(toast) {
      if (toast.timerId) {
        clearInterval(toast.timerId)
        toast.timerId = null
      }
    },

    resumeTimer(toast) {
      if (toast.duration > 0 && !toast.timerId) {
        toast.lastTick = Date.now()
        this.startTimer(toast)
      }
    },

    dismiss(id) {
      const index = this.toasts.findIndex(t => t.id === id)
      if (index !== -1) {
        const toast = this.toasts[index]
        if (toast.timerId) clearInterval(toast.timerId)
        
        this.toasts.splice(index, 1)

        // Process queue
        if (this.queue.length > 0) {
          setTimeout(() => {
            const nextToast = this.queue.shift()
            this.addToast(nextToast)
          }, 300) // slight delay before next one appears
        }
      }
    },

    handleAction(toast) {
      if (toast.action && typeof toast.action.callback === 'function') {
        toast.action.callback()
      }
      this.dismiss(toast.id)
    },

    // 8. Keyboard support
    handleKeydown(e) {
      if (e.key === 'Escape' && this.toasts.length > 0) {
        // Dismiss the most recent toast
        this.dismiss(this.toasts[this.toasts.length - 1].id)
      }
    }
  },

  mounted() {
    window.addEventListener('keydown', this.handleKeydown)
  },

  beforeUnmount() {
    window.removeEventListener('keydown', this.handleKeydown)
    this.toasts.forEach(toast => {
      if (toast.timerId) clearInterval(toast.timerId)
    })
  }
}
</script>

<template>
  <!-- 7. Accessibility roles -->
  <div class="toast-container" aria-live="polite" role="region" aria-label="Notifications">
    <!-- 9. Use TransitionGroup -->
    <TransitionGroup name="toast">
      <div
        v-for="toast in toasts"
        :key="toast.id"
        class="toast-notification"
        :class="[`toast-${toast.type}`]"
        @mouseenter="pauseTimer(toast)"
        @mouseleave="resumeTimer(toast)"
        role="alert"
      >
        <div class="toast-content" @click="dismiss(toast.id)">
          <img :src="toast.icon" alt="" class="toast-custom-icon" />
          <span class="toast-message">{{ toast.message }}</span>
        </div>
        
        <!-- 11. Optional action button -->
        <button 
          v-if="toast.action" 
          class="toast-action-btn"
          @click="handleAction(toast)"
        >
          {{ toast.action.label }}
        </button>

        <button class="toast-close" @click="dismiss(toast.id)" aria-label="Close">
          <i class="bi bi-x"></i>
        </button>

        <!-- 3. Progress bar -->
        <div class="toast-progress-track">
          <div 
            class="toast-progress-bar" 
            :style="{ width: Math.max(0, (toast.remainingTime / toast.duration * 100)) + '%' }"
          ></div>
        </div>
      </div>
    </TransitionGroup>
  </div>
</template>

<style scoped>
/* Container styling */
.toast-container {
  position: fixed;
  bottom: 36px;
  right: 36px;
  z-index: 9999;
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 12px;
  pointer-events: none;
  width: max-content;
  max-width: calc(100vw - 32px);
}

/* Responsive centering on mobile */
@media (max-width: 768px) {
  .toast-container {
    left: 50%;
    transform: translateX(-50%);
    bottom: 24px;
    align-items: center;
  }
}

/* 9. TransitionGroup animations */
.toast-enter-active,
.toast-leave-active,
.toast-move {
  transition: all 0.35s cubic-bezier(0.23, 1, 0.32, 1);
}

.toast-enter-from {
  opacity: 0;
  transform: translateX(40px) scale(0.95);
}

@media (max-width: 768px) {
  .toast-enter-from {
    transform: translateY(30px) scale(0.95);
  }
}

.toast-leave-to {
  opacity: 0;
  transform: scale(0.9);
}

/* Ensure leaving items are taken out of layout flow so moving works */
.toast-leave-active {
  position: absolute;
  right: 0;
}

@media (max-width: 768px) {
  .toast-leave-active {
    left: 0;
    right: auto;
  }
}

/* Toast styling */
.toast-notification {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  background: var(--bg-glass, rgba(15, 23, 42, 0.85));
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border-radius: 12px;
  padding: 16px 20px;
  color: #fff;
  min-width: 300px;
  max-width: 420px;
  box-shadow: 0 12px 32px rgba(0, 0, 0, 0.4), inset 0 1px 0 rgba(255,255,255,0.1);
  pointer-events: auto;
  overflow: hidden; /* for progress bar */
  font-size: 0.95rem;
  z-index: 100;
}

.toast-content {
  display: flex;
  align-items: center;
  gap: 12px;
  flex: 1;
  cursor: pointer;
}

.toast-custom-icon {
  width: 20px;
  height: 20px;
  object-fit: contain;
  flex-shrink: 0;
}

.toast-message {
  font-weight: 500;
  line-height: 1.4;
}

/* Colors and icons */
.toast-notification.toast-success { border-left: 4px solid #10b981; }
.toast-notification.toast-error   { border-left: 4px solid #ef4444; }
.toast-notification.toast-warning { border-left: 4px solid #f59e0b; }
.toast-notification.toast-info    { border-left: 4px solid #3b82f6; }

/* Buttons */
.toast-close {
  background: transparent;
  border: none;
  color: rgba(255,255,255,0.5);
  cursor: pointer;
  padding: 0;
  font-size: 1.25rem;
  display: flex;
  transition: color 0.2s;
  flex-shrink: 0;
}

.toast-close:hover {
  color: #fff;
}

.toast-action-btn {
  background: rgba(255,255,255,0.1);
  border: 1px solid rgba(255,255,255,0.2);
  color: #fff;
  border-radius: 6px;
  padding: 4px 12px;
  font-size: 0.8rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  flex-shrink: 0;
}

.toast-action-btn:hover {
  background: rgba(255,255,255,0.2);
}

/* Progress bar */
.toast-progress-track {
  position: absolute;
  bottom: 0;
  left: 0;
  width: 100%;
  height: 4px;
  background: rgba(255,255,255,0.05);
}

.toast-progress-bar {
  height: 100%;
  background: rgba(255,255,255,0.25);
}

.toast-success .toast-progress-bar { background: #10b981; }
.toast-error .toast-progress-bar   { background: #ef4444; }
.toast-warning .toast-progress-bar { background: #f59e0b; }
.toast-info .toast-progress-bar    { background: #3b82f6; }
</style>
