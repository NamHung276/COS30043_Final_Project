<template>
  <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
    <div class="container">
      <router-link class="navbar-brand" to="/">
        GameHub
      </router-link>

      <div class="navbar-nav">
        <router-link class="nav-link" to="/">
          Home
        </router-link>

        <router-link class="nav-link" to="/news">
          News
        </router-link>

        <router-link class="nav-link" to="/about">
          About
        </router-link>
      </div>
    </div>
  </nav>

  <div class="container mt-4">
    <router-view />
  </div>
</template>