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

  // Compute fake price
  let price = 0;
  if (!isFree) {
    price = (game.id % 40) + 10 + 0.99;
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
