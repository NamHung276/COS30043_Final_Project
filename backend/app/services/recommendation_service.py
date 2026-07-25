import logging
import asyncio
from collections import defaultdict
from app.services.firebase_service import get_firestore
from app.services.rawg_service import get_games

logger = logging.getLogger(__name__)

class RecommendationService:
    async def get_recommendations(self, user_id: str):
        db = get_firestore()
        if not db:
            logger.warning("Firestore not initialized. Returning generic recommendations.")
            return await self._get_generic_recommendations()

        try:
            genre_scores = defaultdict(int)
            tag_scores = defaultdict(int)
            seen_game_ids = set()

            # 1. Purchases (Weight: 3)
            purchases_ref = db.collection("purchases").where("userId", "==", user_id).stream()
            for doc in purchases_ref:
                data = doc.to_dict()
                seen_game_ids.add(data.get("gameId"))
                # If purchases save genre/genres, we extract them
                if data.get("genre"):
                    genre_scores[data.get("genre").lower()] += 3
                for g in data.get("genres", []):
                    genre_scores[g.lower()] += 3
                for t in data.get("tags", []):
                    tag_scores[t.lower()] += 3

            # 2. Favorites (Weight: 2)
            favorites_ref = db.collection("favorites").where("userId", "==", user_id).stream()
            for doc in favorites_ref:
                data = doc.to_dict()
                seen_game_ids.add(data.get("gameId"))
                if data.get("genre"):
                    genre_scores[data.get("genre").lower()] += 2
                for g in data.get("genres", []):
                    genre_scores[g.lower()] += 2
                for t in data.get("tags", []):
                    tag_scores[t.lower()] += 2

            # 3. User Activity (Weight: 1)
            activity_ref = db.collection("user_activity").where("userId", "==", user_id).stream()
            for doc in activity_ref:
                data = doc.to_dict()
                seen_game_ids.add(data.get("gameId"))
                for g in data.get("genres", []):
                    genre_scores[g.lower()] += 1
                for t in data.get("tags", []):
                    tag_scores[t.lower()] += 1

            if not genre_scores and not tag_scores:
                return await self._get_generic_recommendations()

            # Get Top Genres and Tags
            top_genres = sorted(genre_scores.items(), key=lambda x: x[1], reverse=True)
            top_tags = sorted(tag_scores.items(), key=lambda x: x[1], reverse=True)

            g1 = top_genres[0][0] if len(top_genres) > 0 else None
            g2 = top_genres[1][0] if len(top_genres) > 1 else None
            t1 = top_tags[0][0] if len(top_tags) > 0 else None

            # 4. Multi-Pool Fetching
            tasks = []
            if g1:
                tasks.append(get_games(page=1, page_size=20, ordering="-rating", genres=g1))
            if g2:
                tasks.append(get_games(page=1, page_size=20, ordering="-added", genres=g2))
            if t1:
                tasks.append(get_games(page=1, page_size=20, ordering="-metacritic", tags=t1))
            
            # Fallback if no tasks
            if not tasks:
                tasks.append(get_games(page=1, page_size=30, ordering="-rating"))

            pool_results = await asyncio.gather(*tasks)

            # 5. Smart Scoring & Ranking
            candidates = {}
            for res in pool_results:
                for game in res.get("results", []):
                    gid = game.get("id")
                    if gid in seen_game_ids or gid in candidates:
                        continue
                    
                    # Calculate match score
                    score = 0
                    for g in game.get("genres", []):
                        g_slug = g.get("slug", "").lower()
                        score += genre_scores.get(g_slug, 0)
                    for t in game.get("tags", []):
                        t_slug = t.get("slug", "").lower()
                        score += tag_scores.get(t_slug, 0)
                    
                    # Add rating weight
                    score += (game.get("rating", 0) * 5)
                    
                    # Store score alongside game
                    game["_match_score"] = score
                    candidates[gid] = game

            # Sort by match score descending
            ranked_games = sorted(candidates.values(), key=lambda x: x["_match_score"], reverse=True)

            return {"results": ranked_games[:10]}

        except Exception as e:
            logger.error(f"Error generating recommendations for user {user_id}: {e}")
            return await self._get_generic_recommendations()

    async def _get_generic_recommendations(self):
        return await get_games(page=1, page_size=10, ordering="-added")

recommendation_service = RecommendationService()
