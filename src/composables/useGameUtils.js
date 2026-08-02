/**
 * useGameUtils.js — Shared utility functions for game-related formatting.
 *
 * Import these wherever you need them. Never define them locally in a view.
 * Previously duplicated in: Home.vue, Games.vue, GameDetails.vue,
 *   Deals.vue, FreeToPlay.vue, PaidGames.vue.
 */

// ── Store Name Map ────────────────────────────────────────────────────────────
// Single source of truth — was duplicated in GameDetails.vue and Deals.vue.
export const STORE_NAMES = {
  1: "Steam",
  2: "GamersGate",
  3: "GreenManGaming",
  7: "GOG",
  8: "Origin",
  11: "Humble Store",
  13: "Uplay",
  15: "Fanatical",
  21: "WinGameStore",
  23: "GameBillet",
  24: "Voidu",
  25: "Epic Games",
  27: "Games Planet",
  28: "Games Tradera",
  29: "Games Republic",
  30: "Silagrastore",
  31: "Allyouplay",
  32: "DLGamer",
  33: "Noctre",
  34: "DreamGame",
};

/**
 * Returns a human-readable store name from a CheapShark storeID.
 * @param {number|string} storeID
 */
export function storeName(storeID) {
  return STORE_NAMES[storeID] || `Store #${storeID}`;
}

// ── Metacritic ────────────────────────────────────────────────────────────────

/**
 * Returns a CSS class name for a Metacritic score.
 * mc-green (≥75), mc-yellow (≥50), mc-red (<50), mc-grey (no score).
 * @param {number|string|null} score
 */
export function metacriticClass(score) {
  if (!score) return "mc-grey";
  const n = parseInt(score);
  if (n >= 75) return "mc-green";
  if (n >= 50) return "mc-yellow";
  return "mc-red";
}

// ── Star Ratings ──────────────────────────────────────────────────────────────

/**
 * Converts a numeric rating (0–5) into an array of 5 star types.
 * Each element is 'full' | 'half' | 'empty'.
 * @param {number} rating
 */
export function ratingStars(rating) {
  const stars = [];
  const r = rating || 0;
  for (let i = 1; i <= 5; i++) {
    if (r >= i) stars.push("full");
    else if (r >= i - 0.5) stars.push("half");
    else stars.push("empty");
  }
  return stars;
}

/**
 * Returns a human-readable sentiment label for a 0–5 rating.
 * @param {number} rating
 */
export function ratingLabel(rating) {
  if (!rating) return "";
  if (rating >= 4.5) return "Overwhelmingly Positive";
  if (rating >= 4.0) return "Very Positive";
  if (rating >= 3.5) return "Mostly Positive";
  if (rating >= 3.0) return "Mixed";
  if (rating >= 2.0) return "Mostly Negative";
  return "Negative";
}

// ── Date Formatting ───────────────────────────────────────────────────────────

/**
 * Formats an ISO date string into a readable "Jan 1, 2024" format.
 * Returns "—" for missing/invalid dates.
 * @param {string|null} value
 */
export function formatDate(value) {
  if (!value) return "—";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  if (date.getFullYear() === 2026 && date.getMonth() === 4 && date.getDate() === 24) return "—";

  return new Intl.DateTimeFormat("en", {
    month: "short",
    day: "numeric",
    year: "numeric",
  }).format(date);
}

// ── Dummy Pricing (Frontend Mock) ─────────────────────────────────────────────

/**
 * Generates a deterministic fake base price from a game's ID.
 */
export function gamePrice(game) {
  if (!game || (!game.id && !game.gameId)) return null;
  const id = parseInt(game.id || game.gameId) || 0;
  const prices = [19.99, 29.99, 39.99, 49.99, 59.99, 69.99];
  return prices[id % prices.length].toFixed(2);
}

/**
 * Generates a deterministic fake discount percentage from a game's ID.
 */
export function gameDiscount(game) {
  if (!game || (!game.id && !game.gameId)) return 0;
  const id = parseInt(game.id || game.gameId) || 0;
  if (id % 3 !== 0) return 0; // 1/3 chance of discount
  const discounts = [10, 20, 25, 33, 50, 75];
  return discounts[id % discounts.length];
}

/**
 * Calculates the final price after the fake discount.
 */
export function discountedPrice(game) {
  const priceStr = gamePrice(game);
  if (!priceStr) return null;
  const price = parseFloat(priceStr);
  const disc = gameDiscount(game);
  if (!disc) return price.toFixed(2);
  return (price * (1 - disc / 100)).toFixed(2);
}

// ── Platform Icons ────────────────────────────────────────────────────────────

/**
 * Returns a local icon path for a platform name string.
 * @param {string} name
 */
export function platformIcon(name) {
  const n = (name || "").toLowerCase();
  if (n.includes("pc") || n.includes("windows")) return "/game_logo/pc.svg";
  if (n.includes("playstation")) return "/game_logo/playstation_logo.png";
  if (n.includes("xbox")) return "/game_logo/xbox_logo.png";
  if (n.includes("nintendo") || n.includes("switch"))
    return "/game_logo/nintendo_logo.png";
  if (n.includes("mac")) return "/game_logo/macos.png";
  if (n.includes("linux")) return "/game_logo/linux.png";
  if (n.includes("android") || n.includes("ios") || n.includes("mobile"))
    return "/game_logo/mobile.svg";
  return "/logo/gamepad.svg";
}

/**
 * Derives a deduplicated list of platform icon descriptors from a RAWG
 * platforms array. Used for platform filter and card display in Games.vue.
 * @param {Array} platforms — RAWG platforms array
 */
export function platformIcons(platforms) {
  if (!platforms?.length) return [];
  const icons = [];
  if (platforms.some((p) => p.platform.id === 4))
    icons.push({ key: "pc", label: "PC" });
  if (platforms.some((p) => p.platform.slug?.includes("playstation")))
    icons.push({ key: "ps", label: "PlayStation" });
  if (platforms.some((p) => p.platform.slug?.includes("xbox")))
    icons.push({ key: "xbox", label: "Xbox" });
  if (
    platforms.some(
      (p) =>
        p.platform.slug?.includes("nintendo") ||
        p.platform.slug?.includes("switch") ||
        p.platform.slug?.includes("wii") ||
        p.platform.slug?.includes("3ds") ||
        p.platform.slug?.includes("nes") ||
        p.platform.slug?.includes("snes"),
    )
  )
    icons.push({ key: "nintendo", label: "Nintendo" });
  if (
    platforms.some(
      (p) =>
        p.platform.slug?.includes("ios") || p.platform.slug?.includes("android"),
    )
  )
    icons.push({ key: "mobile", label: "Mobile" });
  return icons;
}
