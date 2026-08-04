export function getGameState(game) {
  if (!game) return { state: 'UNKNOWN' };

  const today = new Date();
  today.setHours(0, 0, 0, 0);

  let isTba = !game.released;
  let isComingSoon = false;
  let isReleased = false;

  if (!isTba) {
    const releaseDate = new Date(game.released);
    // If the release date is exactly today, it should be considered RELEASED
    // so we use releaseDate > today for COMING_SOON
    if (releaseDate > today) {
      isComingSoon = true;
    } else {
      isReleased = true;
    }
  }

  // Check if it's free-to-play based on tags
  let isFree = false;
  if (game.tags && Array.isArray(game.tags)) {
    isFree = game.tags.some(t => t.slug === 'free-to-play');
  }
  // Also sometimes RAWG returns 'free' or price is 0 if merged with CheapShark, but we'll stick to tags.

  let state = 'TBA';
  if (isFree && isReleased) {
    state = 'FREE';
  } else if (isReleased) {
    state = 'RELEASED';
  } else if (isComingSoon) {
    state = 'COMING_SOON';
  }

  // Compute real or tiered price
  let price = 0;
  if (!isFree) {
    if (game.price && game.price.final !== undefined) {
      // Steam fallback price
      price = parseFloat(game.price.final);
    } else if (game.ggdeals && game.ggdeals.prices && game.ggdeals.prices.currentRetail) {
      // GG.deals retail price
      price = parseFloat(game.ggdeals.prices.currentRetail);
    } else if (game.cheapest_deal_price) {
      // CheapShark price
      price = parseFloat(game.cheapest_deal_price);
    } else {
      // Create a realistic tier based on rating and release year
      const year = game.released ? new Date(game.released).getFullYear() : 2020;
      const score = game.metacritic || (game.rating ? game.rating * 20 : 70);
      
      if (year >= 2023 && score >= 80) price = 59.99;
      else if (year >= 2022 || score >= 85) price = 49.99;
      else if (year >= 2018 || score >= 75) price = 29.99;
      else if (year >= 2015) price = 19.99;
      else price = 9.99;
    }
  }

  // Calculate countdown days if coming soon
  let countdownDays = null;
  if (isComingSoon && game.released) {
    const releaseDate = new Date(game.released);
    const diffTime = releaseDate - today;
    countdownDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
  }

  return {
    state,
    price,
    formattedPrice: price > 0 ? price.toFixed(2) : '0.00',
    releaseDate: game.released,
    countdownDays,
    
    // Boolean flags for easy usage in templates
    isReleased: state === 'RELEASED',
    isFree: state === 'FREE',
    isComingSoon: state === 'COMING_SOON',
    isTba: state === 'TBA',
  };
}
