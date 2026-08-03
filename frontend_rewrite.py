import re

with open(r'c:\Users\hungt\Documents\GitHub\COS30043_Final_Project\src\views\GameDetails_backup.vue', 'r', encoding='utf-8') as f:
    text = f.read()

# 1. game.name -> game.title
text = text.replace('game.name', 'game.title')

# 2. game.description_raw -> game.description
text = text.replace('game.description_raw', 'game.description')
text = text.replace('!game.description_raw', '!game.description')
text = text.replace('game.description_raw || game.description', 'game.description')

# 3. game.background_image -> game.cover_image
text = text.replace('game.background_image', 'game.cover_image')
text = text.replace('game.background_image_additional', 'game.hero_image')

# 4. screenshots logic
text = text.replace('shot.image', 'shot')

# 5. Remove Steam/ITAD/SteamCharts fetches from fetchData
fetch_block_old = """
        // Fetch supplemental data independently (non-blocking)
        this.fetchSupplementalData(id, detailData);
"""
text = text.replace(fetch_block_old, '')

# Remove fetchSupplementalData function entirely
text = re.sub(r'async fetchSupplementalData.*?}\s*},', '', text, flags=re.DOTALL)

# 6. Computed properties simplified
dev_old = """    developerNames() {
      return (this.game?.developers || []).map((d) => d.name).join(", ") || "—";
    },"""
dev_new = """    developerNames() {
      return (this.game?.developers || []).join(", ") || "—";
    },"""
text = text.replace(dev_old, dev_new)

pub_old = """    publisherNames() {
      return (this.game?.publishers || []).map((p) => p.name).join(", ") || "—";
    },"""
pub_new = """    publisherNames() {
      return (this.game?.publishers || []).join(", ") || "—";
    },"""
text = text.replace(pub_old, pub_new)

genre_old = """    genreNames() {
      return (this.game?.genres || []).map((g) => g.name);
    },"""
genre_new = """    genreNames() {
      return this.game?.genres || [];
    },"""
text = text.replace(genre_old, genre_new)

hero_old = """    heroImage() {
      if (this.screenshots.length && this.screenshots[this.activeShot]) {
        return this.screenshots[this.activeShot].image;
      }
      return this.game?.cover_image;
    },"""
hero_new = """    heroImage() {
      if (this.game?.screenshots?.length && this.game.screenshots[this.activeShot]) {
        return this.game.screenshots[this.activeShot];
      }
      return this.game?.hero_image || this.game?.cover_image;
    },"""
text = text.replace(hero_old, hero_new)

plat_old = """    platforms() {
      const allPlatforms = (this.game?.platforms || []).map((p) => ({
        name: p.platform.name,
        icon: this.platformIcon(p.platform.name),
      }));
      const unique = [];
      const seen = new Set();
      for (const p of allPlatforms) {
        if (!seen.has(p.icon)) {
          seen.add(p.icon);
          unique.push(p);
        }
      }
      return unique;
    },"""
plat_new = """    platforms() {
      const allPlatforms = (this.game?.platforms || []).map((p) => ({
        name: p,
        icon: this.platformIcon(p),
      }));
      const unique = [];
      const seen = new Set();
      for (const p of allPlatforms) {
        if (!seen.has(p.icon)) {
          seen.add(p.icon);
          unique.push(p);
        }
      }
      return unique;
    },"""
text = text.replace(plat_old, plat_new)

plat_grouped_old = """        const name = p.platform?.name || "";"""
plat_grouped_new = """        const name = p || "";"""
text = text.replace(plat_grouped_old, plat_grouped_new)

# 7. Trailer logic simplification
trailer_old = """    trailerYoutubeId() {
      // Try RAWG movies first (clip url) — RAWG always has priority
      if (this.trailers.length > 0) {
        const t = this.trailers[0];
        if (t.data?.max) return null; // direct mp4, use videoUrl
        const m = (t.preview || "").match(
          /(?:youtu\.be\/|youtube\.com\/(?:embed\/|v\/|watch\?v=))([\w-]{11})/,
        );
        if (m) return m[1];
      }
      // Try game.clip
      if (this.game?.clip?.video) {
        const m = this.game.clip.video.match(
          /(?:youtu\.be\/|youtube\.com\/(?:embed\/|v\/|watch\?v=))([\w-]{11})/,
        );
        if (m) return m[1];
      }
      return null;
    },

    /**
     * effectiveYoutubeId — YouTube fallback trailer ID.
     * Only used when RAWG provides NO trailer at all.
     * RAWG trailer always takes priority.
     */
    effectiveYoutubeId() {
      if (this.hasTrailer) return null; // RAWG trailer takes priority — never override
      return this.youtubeTrailerId || null;
    },

    /** True if any trailer is available (RAWG or YouTube fallback) */
    hasAnyTrailer() {
      return this.hasTrailer || !!this.effectiveYoutubeId;
    },

    trailerVideoUrl() {
      if (this.trailers.length > 0 && this.trailers[0].data?.max) {
        return this.trailers[0].data.max;
      }
      return this.game?.clip?.clips?.full || this.game?.clip?.clip || null;
    },

    trailerPoster() {
      return this.trailers[0]?.preview || this.game?.cover_image || null;
    },

    hasTrailer() {
      return !!(this.trailerYoutubeId || this.trailerVideoUrl);
    },"""
trailer_new = """    trailerYoutubeId() {
      if (this.game?.trailer?.is_youtube_fallback) {
        const match = this.game.trailer.url.match(/embed\/([^?]+)/);
        return match ? match[1] : null;
      }
      return null;
    },
    effectiveYoutubeId() {
      return this.trailerYoutubeId;
    },
    hasAnyTrailer() {
      return !!this.game?.trailer;
    },
    trailerVideoUrl() {
      return this.game?.trailer?.is_youtube_fallback ? null : this.game?.trailer?.url;
    },
    trailerPoster() {
      return this.game?.trailer?.poster || this.game?.cover_image || null;
    },
    hasTrailer() {
      return !!this.game?.trailer && !this.game?.trailer?.is_youtube_fallback;
    },"""
text = text.replace(trailer_old, trailer_new)

# 8. Data refs removals
data_old = """      // ── Gen 3 enrichment state ────────────────────────────────────────────
      steamData: null,
      steamLoading: false,
      steamchartsData: null,
      steamchartsLoading: false,
      youtubeTrailerId: null,
      itadDeals: null,
      itadLoading: false,"""
text = text.replace(data_old, '')

# 9. Change references to steamData, steamchartsData, itadDeals in template
text = text.replace('steamData', 'game')
text = text.replace('steamchartsData', 'game.players')
text = text.replace('itadDeals', 'game')

# 10. Fix template properties
text = text.replace('game.steam_url', 'game.steam_url')

with open(r'c:\Users\hungt\Documents\GitHub\COS30043_Final_Project\src\views\GameDetails.vue', 'w', encoding='utf-8') as f:
    f.write(text)

print("Replaced GameDetails.vue successfully!")
