<template>
  <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
    <div class="container">

      <router-link
        class="navbar-brand"
        to="/"
      >
        GameHub
      </router-link>

      <div class="navbar-nav">

        <router-link
          class="nav-link"
          to="/"
        >
          Home
        </router-link>

        <router-link
          class="nav-link"
          to="/games"
        >
          Games
        </router-link>

        <router-link
          class="nav-link"
          to="/news"
        >
          News
        </router-link>

        <router-link
          class="nav-link"
          to="/about"
        >
          About
        </router-link>

        <router-link
          class="nav-link"
          to="/login"
        >
          Login
        </router-link>

        <router-link
          class="nav-link"
          to="/register"
        >
          Register
        </router-link>

      </div>

    </div>
  </nav>
</template>