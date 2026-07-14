# GameHub

**GameHub** is a modern, community-driven platform for discovering games, saving favorites, and sharing reviews. It aims to provide a rich, visually stunning experience akin to platforms like Steam, RAWG, and Epic Games. 

Built as the final project for COS30043, this application leverages Vue 3 and Firebase to deliver a responsive and interactive user experience.

## 🚀 Tech Stack

*   **Frontend:** Vue 3 (Composition API), Vite, Vue Router
*   **Backend & Database:** Firebase Authentication, Firestore
*   **Styling:** Modern CSS (Glassmorphism, CSS Variables, Custom Gradients), Bootstrap (for grid layout and utility classes)

## ✨ Key Features & Progress

*   **Gamer Profiles:** A dynamic, Steam-inspired user profile displaying account statistics, recent community activity (reviews), and a preview of favorite games. Includes secure options to edit display names and passwords.
*   **Authentication & Security:** Full Firebase Authentication flow (Login, Registration, Protected Routes).
*   **Favorites System:** Users can save games to their personal collection. The Favorites page supports list/grid views, real-time search, sorting, and genre filtering.
*   **Community Reviews:** A robust review system allowing users to rate games out of 5 stars, write detailed feedback, and vote on other community members' reviews (helpful/unhelpful).
*   **Game Catalogs & Deals:** Browse through comprehensive lists of premium games and Free-to-Play titles. Discover the latest deals across multiple storefronts.
*   **Admin Dashboard:** A moderation panel for managing user accounts and community posts.
*   **Modern Aesthetics:** Deep dark-mode design by default, utilizing glowing accents, glassmorphism cards, and micro-animations to ensure a premium look and feel.

## 🛠️ Setup Instructions

### Prerequisites
*   [Node.js](https://nodejs.org/) (v16 or higher recommended)
*   NPM or Yarn

### Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/NamHung276/COS30043_Final_Project.git
    cd COS30043_Final_Project
    ```

2.  **Install dependencies:**
    ```bash
    npm install
    ```

3.  **Configure Firebase:**
    Ensure you have your Firebase configuration set up in `src/firebase.js` (or via environment variables).

4.  **Run the development server:**
    ```bash
    npm run dev
    ```

5.  **Build for production:**
    ```bash
    npm run build
    ```

## 📝 License

This project is created for educational purposes (COS30043).
