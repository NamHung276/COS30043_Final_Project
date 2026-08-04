# GameHub

**GameHub** is a modern, community-driven platform for discovering games, saving favorites, and sharing reviews. It aims to provide a rich, visually stunning experience akin to platforms like Steam, RAWG, and Epic Games. 

Built as the final project for COS30043, this application leverages Vue 3 and Firebase to deliver a responsive and interactive user experience.

## 🚀 Technologies Used

*   **Frontend Core:** Vue 3 (Composition API), Vite, Vue Router, **Pinia** (State Management)
*   **Backend & API:** Python, FastAPI, Uvicorn (Handles server-side caching, external API proxying, and custom recommendation logic)
*   **Database & Auth:** Firebase Authentication, Firestore
*   **Styling:** Vanilla CSS (Glassmorphism, CSS Variables, Custom Gradients), Bootstrap 5 (for grid layout and utility classes), Bootstrap Icons
*   **Tooling:** npm, Git

## ✨ Platform Features

*   **Browse Games:** Explore 500k+ free-to-play and premium titles with genre filters.
*   **Smart Search:** Instant title search across the full game library.
*   **Favorites & Wishlists:** Cloud-saved personal collection via Firestore, supporting list/grid views, real-time search, sorting, and genre filtering (Cached locally using Pinia to eliminate N+1 queries).
*   **Community Reviews:** A robust review system allowing users to rate games out of 5 stars, write detailed feedback, and vote on other community members' reviews.
*   **Live News:** Real-time gaming news powered by NewsAPI.
*   **Auth System:** User registration & login with Firebase Auth (Protected Routes, Secure Sessions).
*   **Gamer Profiles:** A dynamic, Steam-inspired user profile displaying account statistics and recent community activity.
*   **Admin Dashboard:** A moderation panel for managing user accounts and community posts.
*   **Enterprise-Grade Security:** 100% of external API calls are securely proxied through the FastAPI backend, fully hiding sensitive API keys from the client-side.
*   **High Availability (Circuit Breaker):** Implements an auto-recovering Circuit Breaker pattern with a custom Steam API fallback layer, ensuring the catalog and checkout remain 100% operational even if the primary database (RAWG) goes down.
*   **Accessibility (WCAG 2.2.2):** Robust screen-reader support via `aria-live` regions and fully controllable pause/play elements.
*   **Modern Aesthetics:** Deep dark-mode design by default, utilizing glowing accents, glassmorphism cards, and micro-animations to ensure a premium look and feel.
*   **Responsive Design:** Optimised for desktop, tablet, and mobile viewing.

## 🔌 External APIs Integrated

GameHub aggregates data from multiple powerful gaming and news APIs to deliver a comprehensive experience:

*   **[RAWG Video Games Database API](https://rawg.io/apidocs):** Powers the main Games section with a massive library of 500,000+ games, rich metadata, ratings, genres, screenshots, and release information spanning all major gaming platforms.
*   **[FreeToGame API](https://www.freetogame.com/api-doc):** Provides access to 500+ free-to-play games with detailed information, genres, screenshots, system requirements, and platform availability. Drives the Free-to-Play section.
*   **[CheapShark Deals API](https://apidocs.cheapshark.com/):** Aggregates PC game deals and price comparisons from major stores like Steam, Epic, GOG, and more. Powers the Deals section to help gamers find the best prices on their favourite titles.
*   **[GG.deals API](https://gg.deals/api/):** Provides comprehensive PC game deals, historical pricing data, and discount information across multiple storefronts.
*   **[NewsAPI](https://newsapi.org/):** Delivers real-time gaming news and industry updates from multiple major gaming news outlets. Powers the Live News section with continuously updated articles from top gaming publications.
*   **[NewsData.io API](https://newsdata.io/):** Supplemental news source for expanded coverage of global gaming and technology news.
*   **[CoinGecko API](https://www.coingecko.com/en/api):** Provides live market data, prices, and 24-hour changes for top gaming and metaverse cryptocurrencies (e.g., FLOKI, Axie Infinity, Decentraland).
*   **[Google Gemini API](https://aistudio.google.com/):** Powers the AI chatbot features and intelligent game recommendations across the platform.

## 🧗 Challenges & Solutions

Building GameHub involved navigating several real-world technical hurdles:

*   **API Key Security:** Early iterations exposed API keys directly in the frontend. We resolved this by proxying **all** external API calls through the FastAPI backend, so the client never sees a single secret key.
*   **High Availability & API Outages:** When third-party APIs (like RAWG) experienced downtime, the app would freeze. We built a robust **Circuit Breaker** (`rawg_health.py`) that detects outages and automatically fails over to a custom Steam Store API adapter. This parallel fallback system seamlessly mimics the RAWG schema so the UI doesn't break, and gracefully self-heals when the primary API returns.
*   **N+1 Query Problem (Firestore):** When loading a user's wishlist, the app originally fired one Firestore read per game to fetch its details, causing severe slowdowns. We solved this using **Pinia** to cache the full wishlist in memory, and by batching reads with `getDocs` on startup instead of per-card.
*   **Rate Limiting from External APIs:** RAWG and other APIs have strict rate limits. We introduced a server-side **in-memory cache** (`backend/app/cache/memory_cache.py`) with TTL-based expiry so repeated requests are served from cache without hitting the upstream APIs.
*   **Vue Router Guard Timing:** Firebase Auth's `onAuthStateChanged` is asynchronous, which caused route guards to redirect users before auth state was resolved. We fixed this by implementing a `waitForReady()` promise in `useAuthStore` that blocks navigation until Firebase confirms the auth state.
*   **Custom Directive vs. Native Loading:** Achieving smooth, jank-free image loading required going beyond `loading="lazy"`. The custom `v-lazy-img` directive uses `IntersectionObserver`, `image.decode()`, and CSS transitions to eliminate layout shift and deliver a polished shimmer-to-image experience.

## 🚀 Future Roadmap

GameHub is continuously evolving. Planned enhancements include:

*   **Game Recommendation Engine:** AI-powered suggestions based on your favorites and play history.
*   **Advanced Search & Filtering:** Multi-tag filters, platform selection, and release date range.
*   **Social Features:** Follow friends, share collections, and compare libraries.
*   **Enhanced Admin Dashboard:** Advanced news management, analytics, and moderation tools.

## 📁 Project Structure

<details>
<summary>Click to expand</summary>

```text
├── .agents
│   └── AGENTS.md
├── .env
├── .env.example
├── .gitignore
├── .python-version
├── .vscode
│   ├── extensions.json
│   └── settings.json
├── PDF_Read Only
│   ├── Project.pdf
│   ├── cos30043-project_criteria - Sheet1.pdf
│   └── firebase_temp.txt
├── README.md
├── backend
│   ├── .env
│   ├── .env.example
│   ├── README.md
│   ├── app
│   │   ├── __init__.py
│   │   ├── cache
│   │   │   ├── __init__.py
│   │   │   └── memory_cache.py
│   │   ├── middleware
│   │   │   ├── __init__.py
│   │   │   ├── logging_middleware.py
│   │   │   └── rate_limit.py
│   │   ├── models
│   │   │   ├── __init__.py
│   │   │   └── user.py
│   │   ├── routers
│   │   │   ├── __init__.py
│   │   │   ├── admin_ai.py
│   │   │   ├── chatbot.py
│   │   │   ├── coingecko.py
│   │   │   ├── currency.py
│   │   │   ├── deals.py
│   │   │   ├── free_games.py
│   │   │   ├── games.py
│   │   │   ├── health.py
│   │   │   ├── news.py
│   │   │   ├── payments.py
│   │   │   ├── paypal.py
│   │   │   └── uploads.py
│   │   ├── schemas
│   │   │   ├── __init__.py
│   │   │   ├── common.py
│   │   │   ├── game.py
│   │   │   ├── news.py
│   │   │   └── payments.py
│   │   ├── services
│   │   │   ├── __init__.py
│   │   │   ├── ai_service.py
│   │   │   ├── cheapshark_service.py
│   │   │   ├── coingecko_service.py
│   │   │   ├── crypto_service.py
│   │   │   ├── currency_service.py
│   │   │   ├── firebase_service.py
│   │   │   ├── free_games_service.py
│   │   │   ├── ggdeals_service.py
│   │   │   ├── itad_service.py
│   │   │   ├── news_service.py
│   │   │   ├── payment_service.py
│   │   │   ├── paypal_service.py
│   │   │   ├── rawg_service.py
│   │   │   ├── recommendation_service.py
│   │   │   ├── steam_service.py
│   │   │   ├── steamcharts_service.py
│   │   │   └── youtube_service.py
│   │   └── utils
│   │       ├── __init__.py
│   │       ├── dependencies.py
│   │       ├── helpers.py
│   │       └── http_retry.py
│   ├── chatbot
│   │   ├── README.md
│   │   └── __init__.py
│   ├── config.py
│   ├── main.py
│   ├── requirements.txt
│   ├── tests
│   │   ├── __init__.py
│   │   ├── test_config_env.py
│   │   ├── test_health.py
│   │   ├── test_http_retry.py
│   │   └── test_payments.py
│   └── uploads
│       ├── 1785238030569_marvel-tokon-5120x2880-23540.jpg
│       └── 1785381490698_Screenshot_2026-07-24_195125.jpg
├── backend_rewrite.py
├── fix_games.py
├── frontend_rewrite.py
├── index.html
├── old_home.txt
├── package-lock.json
├── package.json
├── public
│   ├── favicon.svg
│   ├── game_icon
│   │   ├── anime.png
│   │   ├── battle_royale.png
│   │   ├── fantasy.png
│   │   ├── horror.png
│   │   ├── mmorpg.png
│   │   ├── moba.png
│   │   ├── racing.png
│   │   ├── sci-fi.png
│   │   ├── shooter.png
│   │   ├── sports.png
│   │   ├── strategy.png
│   │   └── survival.png
│   ├── game_logo
│   │   ├── linux.png
│   │   ├── macos.png
│   │   ├── mobile.svg
│   │   ├── nintendo_logo - dark.png
│   │   ├── nintendo_logo.png
│   │   ├── nintendo_logo_dark.png
│   │   ├── pc.svg
│   │   ├── playstation_logo.png
│   │   ├── playstation_logo_dark.png
│   │   ├── xbox_logo.png
│   │   └── xbox_logo_dark.png
│   ├── home
│   │   ├── game_home.jpg
│   │   └── gaming_community.jpg
│   ├── icons.svg
│   ├── logo
│   │   ├── arrow-left.svg
│   │   ├── arrow-right.svg
│   │   ├── check_mark.png
│   │   ├── cross_mark.png
│   │   ├── gamepad.svg
│   │   ├── information_logo.png
│   │   ├── menu_bar.png
│   │   ├── search.svg
│   │   ├── star.svg
│   │   └── warning_sign.png
│   └── news
│       ├── apex.jpg
│       ├── cs2.jpg
│       ├── diablo4.jpg
│       ├── dota2.jpg
│       ├── elden-ring.jpg
│       ├── fortnite.jpg
│       ├── genshin.jpg
│       ├── league-of-legends.jpg
│       ├── lostark.jpg
│       ├── overwatch2.jpg
│       ├── placeholder_wide.jpg
│       ├── poe2.jpg
│       ├── tft.jpg
│       ├── valorant.jpg
│       ├── warframe.jpg
│       └── wow.jpg
├── pyrefly.toml
├── src
│   ├── App.vue
│   ├── assets
│   │   └── hero.png
│   ├── components
│   │   ├── ChatbotWidget.vue
│   │   ├── CryptoMarket.vue
│   │   ├── CurrencyChart.vue
│   │   ├── CurrencyConverter.vue
│   │   ├── Footer.vue
│   │   ├── ITADDealsPanel.vue
│   │   ├── LikeButton.vue
│   │   ├── Navbar.vue
│   │   ├── PayPalCheckout.vue
│   │   ├── ReportModal.vue
│   │   ├── ReviewSection.vue
│   │   ├── ScrollToTop.vue
│   │   ├── SkeletonCard.vue
│   │   ├── SteamChartsPanel.vue
│   │   ├── SteamDataPanel.vue
│   │   ├── ToastNotification.vue
│   │   ├── TrailerModal.vue
│   │   └── library
│   │       ├── LibraryAchievements.vue
│   │       ├── LibraryCommunity.vue
│   │       ├── LibraryGallery.vue
│   │       ├── LibraryHero.vue
│   │       ├── LibraryNotesAndGoals.vue
│   │       ├── LibrarySidebar.vue
│   │       └── LibraryStats.vue
│   ├── composables
│   │   └── useGameUtils.js
│   ├── data
│   │   └── news.json
│   ├── directives
│   │   └── lazyImg.js
│   ├── firebase.js
│   ├── main.js
│   ├── router
│   │   └── index.js
│   ├── services
│   │   ├── api.js
│   │   ├── cart.js
│   │   ├── gameState.js
│   │   └── tracking.js
│   ├── stores
│   │   ├── useAuthStore.js
│   │   ├── useLibraryStore.js
│   │   ├── useNotificationStore.js
│   │   ├── useRecommendationStore.js
│   │   └── useWishlistStore.js
│   ├── style.css
│   └── views
│       ├── About.vue
│       ├── AdminDashboard.vue
│       ├── Checkout.vue
│       ├── CheckoutSuccess.vue
│       ├── ConverterView.vue
│       ├── CreateNews.vue
│       ├── Deals.vue
│       ├── EditNews.vue
│       ├── Favorites.vue
│       ├── FreeToPlay.vue
│       ├── FreeToPlayDetails.vue
│       ├── GameDetails.vue
│       ├── GameDetails_backup.vue
│       ├── GameHubNews.vue
│       ├── GameHubNewsDetails.vue
│       ├── Games.vue
│       ├── Home.vue
│       ├── Library.vue
│       ├── LibraryDetails.vue
│       ├── LiveNews.vue
│       ├── Login.vue
│       ├── MyReviews.vue
│       ├── NotFound.vue
│       ├── PaidGames.vue
│       ├── Profile.vue
│       ├── PurchaseHistory.vue
│       ├── Register.vue
│       └── Settings.vue
├── tmp_check_config.py
├── update_games_fallback.py
├── update_itad.py
├── update_steamcharts.py
├── update_steamdata.py
├── uploads
├── vercel.json
├── vite.config.js
└── walkthrough.md
```
</details>

## 🛠️ Setup Instructions

### Prerequisites
*   [Node.js](https://nodejs.org/) (v16 or higher recommended)
*   [Python](https://www.python.org/) (v3.9 or higher recommended)
*   NPM or Yarn

### Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/NamHung276/COS30043_Final_Project.git
    cd COS30043_Final_Project
    ```

2.  **Set up the Python Backend:**
    ```bash
    cd backend
    python -m venv venv
    
    # Activate virtual environment (Windows)
    venv\Scripts\activate
    # Or on macOS/Linux:
    # source venv/bin/activate
    
    pip install -r requirements.txt
    cd ..
    ```

3.  **Install Frontend Dependencies:**
    ```bash
    npm install
    ```

4.  **Configure Environment Variables:**
    * Create a `.env` file in the root directory and add your API keys (RAWG, NewsAPI, Firebase config).
    * Place your Firebase service account JSON file at `backend/firebase-credentials.json` for the FastAPI backend to access Firestore securely.

5.  **Run the development server (Frontend + Backend concurrently):**
    ```bash
    npm run dev
    ```
    This single command uses `concurrently` to boot up both the Vite frontend (`localhost:5173`) and the FastAPI backend (`localhost:8000`) simultaneously.

6.  **Build for production (Frontend only):**
    ```bash
    npm run build
    ```

## 📝 License

This project is created for educational purposes (COS30043 Full Stack Development).
