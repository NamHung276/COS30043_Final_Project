import logging
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
            # Gather data from Firestore
            # We'll use synchronous Firestore calls since firebase-admin is synchronous
            genre_scores = defaultdict(int)
            tag_scores = defaultdict(int)
            seen_game_ids = set()

            # 1. Purchases (Weight: 3)
            # Just to populate seen_game_ids so we don't recommend already bought games.
            purchases_ref = db.collection("purchases").where("userId", "==", user_id).stream()
            for doc in purchases_ref:
                data = doc.to_dict()
                seen_game_ids.add(data.get("gameId"))

            # 2. Favorites (Weight: 2)
            favorites_ref = db.collection("favorites").where("userId", "==", user_id).stream()
            for doc in favorites_ref:
                data = doc.to_dict()
                seen_game_ids.add(data.get("gameId"))
                genre = data.get("genre")
                if genre:
                    genre_scores[genre.lower()] += 2

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

            # Get Top 3 Genres and Top 3 Tags
            top_genres = sorted(genre_scores.items(), key=lambda x: x[1], reverse=True)[:3]
            top_tags = sorted(tag_scores.items(), key=lambda x: x[1], reverse=True)[:3]

            genre_slugs = ",".join([g[0] for g in top_genres])
            tag_slugs = ",".join([t[0] for t in top_tags])

            # Query RAWG
            rawg_data = await get_games(
                page=1,
                page_size=30,
                ordering="-rating",
                genres=genre_slugs if genre_slugs else None,
                tags=tag_slugs if tag_slugs else None
            )

            # Filter out seen games
            results = rawg_data.get("results", [])
            filtered_results = [g for g in results if g.get("id") not in seen_game_ids]

            # Return top 10
            return {"results": filtered_results[:10]}

        except Exception as e:
            logger.error(f"Error generating recommendations for user {user_id}: {e}")
            return await self._get_generic_recommendations()

    async def _get_generic_recommendations(self):
        # Fallback to popular games
        return await get_games(page=1, page_size=10, ordering="-added")

recommendation_service = RecommendationService()
