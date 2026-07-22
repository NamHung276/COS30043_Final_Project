import { db, auth } from "../firebase";
import { collection, addDoc } from "firebase/firestore";

/**
 * Log a user action to the 'user_activity' collection for the recommendation engine.
 * @param {string} action - e.g., 'view'
 * @param {object} gameData - subset of game data (id, name, genres, tags)
 */
export async function trackUserActivity(action, gameData) {
  const user = auth.currentUser;
  if (!user) return; // Only track logged-in users

  try {
    const genres = (gameData.genres || []).map(g => g.slug || g.name);
    const tags = (gameData.tags || []).map(t => t.slug || t.name);

    await addDoc(collection(db, "user_activity"), {
      userId: user.uid,
      action: action,
      gameId: gameData.id,
      gameName: gameData.name,
      genres: genres,
      tags: tags,
      timestamp: new Date().toISOString()
    });
  } catch (error) {
    // Fail silently - analytics shouldn't break the app
    console.error("Failed to track activity:", error);
  }
}
