import { reactive, watch } from "vue";

const getInitialCart = () => {
  try {
    const saved = localStorage.getItem("gamehub_cart");
    if (saved) {
      return JSON.parse(saved);
    }
  } catch (e) {
    console.error("Failed to parse cart from local storage", e);
  }
  return [];
};

export const cartState = reactive({
  items: getInitialCart(),

  get totalItems() {
    return this.items.length;
  },

  get totalPrice() {
    return this.items.reduce(
      (total, item) => total + (parseFloat(item.price) || 0),
      0,
    );
  },

  add(game) {
    // Prevent duplicates
    const cleanId = String(game.id).replace(/^steam-/, "");
    if (!this.items.some((item) => String(item.id).replace(/^steam-/, "") === cleanId)) {
      this.items.push(game);
    }
  },

  remove(gameId) {
    const cleanId = String(gameId).replace(/^steam-/, "");
    this.items = this.items.filter(
      (item) => String(item.id).replace(/^steam-/, "") !== cleanId
    );
  },

  clear() {
    this.items = [];
  },

  has(gameId) {
    const cleanId = String(gameId).replace(/^steam-/, "");
    return this.items.some((item) => String(item.id).replace(/^steam-/, "") === cleanId);
  },
});

// Persist cart to local storage whenever it changes
watch(
  () => cartState.items,
  (newItems) => {
    localStorage.setItem("gamehub_cart", JSON.stringify(newItems));
  },
  { deep: true },
);
