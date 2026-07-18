# Walkthrough

## Summary of Changes
- **Fixed Logout Blank Screen Bug**: Resolved an issue where logging out from protected pages (like `Profile`, `Settings`, or `AdminDashboard`) would result in a blank white screen. 

### What was the cause?
The blank screen was caused by a routing conflict inside Vue Router. When the user clicked "Logout", two actions were happening simultaneously:
1. The `Navbar.vue` explicitly redirected the user to the home page (`/`).
2. The `onAuthStateChanged` listeners inside the protected pages (e.g., `Profile.vue`) detected the logout event and immediately attempted to redirect the user to `/login`.

Because `App.vue` uses a `<transition mode="out-in">` for page navigation, these two conflicting simultaneous redirects caused the transition to "freeze" mid-animation, leaving the screen completely blank as neither page finished mounting.

### How was it fixed?
- Removed the `this.$router.push("/login")` calls from the `onAuthStateChanged` lifecycle hooks inside individual protected components (`Profile.vue`, `AdminDashboard.vue`, `Settings.vue`, `Library.vue`, `Favorites.vue`, and `EditNews.vue`).
- The application already has a robust, global router guard (`router.beforeEach` in `src/router/index.js`) that handles unauthorized access to protected routes. By delegating the routing logic to the global guard and the explicit `logout()` function in the Navbar, we prevented the race condition without sacrificing any security or user experience.

### Verification
- Logging out will now smoothly redirect the user to the home page (`/`) without breaking the UI.
- The `sophia.bennett92` account, despite not having a matching record in the Firestore database, now logs out gracefully and the application state properly resets.
