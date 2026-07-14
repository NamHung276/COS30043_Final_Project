// src/services/cart.js
import { reactive, watch } from 'vue'

const getInitialCart = () => {
  try {
    const saved = localStorage.getItem('gamehub_cart')
    if (saved) {
      return JSON.parse(saved)
    }
  } catch (e) {
    console.error('Failed to parse cart from local storage', e)
  }
  return []
}

export const cartState = reactive({
  items: getInitialCart(),
  
  get totalItems() {
    return this.items.length
  },
  
  get totalPrice() {
    return this.items.reduce((total, item) => total + (item.price || 0), 0)
  },
  
  add(game) {
    // Prevent duplicates
    if (!this.items.some(item => item.id === game.id)) {
      this.items.push(game)
    }
  },
  
  remove(gameId) {
    this.items = this.items.filter(item => item.id !== gameId)
  },
  
  clear() {
    this.items = []
  },
  
  has(gameId) {
    return this.items.some(item => item.id === gameId)
  }
})

// Persist cart to local storage whenever it changes
watch(() => cartState.items, (newItems) => {
  localStorage.setItem('gamehub_cart', JSON.stringify(newItems))
}, { deep: true })
