# GameHub

**GameHub** is a modern, community-driven platform for discovering games, saving favorites, and sharing reviews. It aims to provide a rich, visually stunning experience akin to platforms like Steam, RAWG, and Epic Games. 

Built as the final project for COS30043, this application leverages Vue 3 and Firebase to deliver a responsive and interactive user experience.

## 🚀 Technologies Used

*   **Frontend Core:** Vue 3 (Composition API), Vite, Vue Router
*   **Backend & API:** Python, FastAPI, Uvicorn (Handles server-side caching, external API proxying, and custom recommendation logic)
*   **Database & Auth:** Firebase Authentication, Firestore
*   **Styling:** Vanilla CSS (Glassmorphism, CSS Variables, Custom Gradients), Bootstrap 5 (for grid layout and utility classes), Bootstrap Icons
*   **Tooling:** npm, Git

## ✨ Platform Features

*   **Browse Games:** Explore 500k+ free-to-play and premium titles with genre filters.
*   **Smart Search:** Instant title search across the full game library.
*   **Favorites & Wishlists:** Cloud-saved personal collection via Firestore, supporting list/grid views, real-time search, sorting, and genre filtering.
*   **Community Reviews:** A robust review system allowing users to rate games out of 5 stars, write detailed feedback, and vote on other community members' reviews.
*   **Live News:** Real-time gaming news powered by NewsAPI.
*   **Auth System:** User registration & login with Firebase Auth (Protected Routes, Secure Sessions).
*   **Gamer Profiles:** A dynamic, Steam-inspired user profile displaying account statistics and recent community activity.
*   **Admin Dashboard:** A moderation panel for managing user accounts and community posts.
*   **Modern Aesthetics:** Deep dark-mode design by default, utilizing glowing accents, glassmorphism cards, and micro-animations to ensure a premium look and feel.
*   **Responsive Design:** Optimised for desktop, tablet, and mobile viewing.

## 🔌 External APIs Integrated

GameHub aggregates data from multiple powerful gaming and news APIs to deliver a comprehensive experience:

*   **[RAWG Video Games Database API](https://rawg.io/apidocs):** Powers the main Games section with a massive library of 500,000+ games, rich metadata, ratings, genres, screenshots, and release information spanning all major gaming platforms.
*   **[FreeToGame API](https://www.freetogame.com/api-doc):** Provides access to 500+ free-to-play games with detailed information, genres, screenshots, system requirements, and platform availability. Drives the Free-to-Play section.
*   **[CheapShark Deals API](https://apidocs.cheapshark.com/):** Aggregates PC game deals and price comparisons from major stores like Steam, Epic, GOG, and more. Powers the Deals section to help gamers find the best prices on their favourite titles.
*   **[NewsAPI](https://newsapi.org/):** Delivers real-time gaming news and industry updates from multiple major gaming news outlets. Powers the Live News section with continuously updated articles from top gaming publications.
*   **[CoinGecko API](https://www.coingecko.com/en/api):** Provides live market data, prices, and 24-hour changes for top gaming and metaverse cryptocurrencies (e.g., FLOKI, Axie Infinity, Decentraland).

## 🚀 Future Roadmap

GameHub is continuously evolving. Planned enhancements include:

*   **Game Recommendation Engine:** AI-powered suggestions based on your favorites and play history.
*   **Advanced Search & Filtering:** Multi-tag filters, platform selection, and release date range.
*   **Social Features:** Follow friends, share collections, and compare libraries.
*   **Enhanced Admin Dashboard:** Advanced news management, analytics, and moderation tools.

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
