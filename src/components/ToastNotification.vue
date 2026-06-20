// src/components/ToastNotification.vue
<script>
export default {
  name: 'ToastNotification',

  data() {
    return {
      toasts: []
    }
  },

  methods: {
    /**
     * Show a toast notification.
     * @param {string} message - The message to display
     * @param {'success'|'error'|'info'|'warning'} type - Toast type
     * @param {number} duration - Auto-dismiss time in ms (default 3000)
     */
    show(message, type = 'info', duration = 3000) {
      const id = Date.now() + Math.random()

      this.toasts.push({ id, message, type, leaving: false })

      setTimeout(() => {
        this.dismiss(id)
      }, duration)
    },

    dismiss(id) {
      const toast = this.toasts.find(t => t.id === id)
      if (toast) {
        toast.leaving = true
        setTimeout(() => {
          this.toasts = this.toasts.filter(t => t.id !== id)
        }, 250)
      }
    }
  }
}
</script>

<template>
  <div class="toast-container">
    <div
      v-for="toast in toasts"
      :key="toast.id"
      class="toast-notification"
      :class="[
        `toast-${toast.type}`,
        { 'toast-leaving': toast.leaving }
      ]"
      @click="dismiss(toast.id)"
    >
      <span v-if="toast.type === 'success'">✅ </span>
      <span v-else-if="toast.type === 'error'">❌ </span>
      <span v-else-if="toast.type === 'warning'">⚠️ </span>
      <span v-else>ℹ️ </span>
      {{ toast.message }}
    </div>
  </div>
</template>
