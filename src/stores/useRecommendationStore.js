import { defineStore } from "pinia";

export const useRecommendationStore = defineStore("recommendations", {
  state: () => ({
    displayedGameIds: new Set(),
  }),
  actions: {
    /**
     * Registers games that are currently being displayed.
     * @param {Array} games Array of game objects
     */
    registerDisplayed(games) {
      if (!games) return;
      games.forEach(game => {
        if (game && game.id) {
          this.displayedGameIds.add(game.id);
        }
      });
    },

    /**
     * Filters a list of games, returning only those that haven't been displayed yet.
     * Optionally registers the filtered games so they won't be shown again.
     * @param {Array} games Array of game objects to filter
     * @param {Boolean} autoRegister Whether to automatically register the returned games
     * @returns {Array} Filtered list of unique games
     */
    filterAndRegister(games, autoRegister = true) {
      if (!games) return [];
      const uniqueGames = games.filter(game => !this.displayedGameIds.has(game.id));
      
      if (autoRegister) {
        this.registerDisplayed(uniqueGames);
      }
      
      return uniqueGames;
    },

    /**
     * Clears the displayed games registry.
     * Useful when navigating to a new page or refreshing the feed.
     */
    reset() {
      this.displayedGameIds.clear();
    }
  }
});
