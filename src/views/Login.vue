// src/views/Login.vue
<script>
import { auth } from '../firebase'
import { signInWithEmailAndPassword } from 'firebase/auth'

export default {
  data() {
    return {
      email: '',
      password: '',
      error: '',
      loading: false
    }
  },

  methods: {
    async login() {
      this.error = ''
      this.loading = true

      try {
        await signInWithEmailAndPassword(
          auth,
          this.email,
          this.password
        )

        // Redirect to home
        // Navbar updates automatically via onAuthStateChanged
        this.$router.push('/')

      } catch (error) {
        if (
          error.code === 'auth/invalid-credential' ||
          error.code === 'auth/wrong-password' ||
          error.code === 'auth/user-not-found'
        ) {
          this.error = 'Invalid email or password.'
        } else if (error.code === 'auth/invalid-email') {
          this.error = 'Invalid email address.'
        } else if (error.code === 'auth/too-many-requests') {
          this.error = 'Too many attempts. Please try again later.'
        } else {
          this.error = 'Login failed. Please try again.'
        }
        console.error(error)
      } finally {
        this.loading = false
      }
    }
  }
}
</script>

<template>
  <div class="container py-5">

    <div class="row justify-content-center">
      <div class="col-md-5">

        <div class="text-center mb-4">
          <h1 style="font-size: 2rem;">Welcome Back</h1>
          <p class="text-muted">Sign in to your GameHub account</p>
        </div>

        <div class="card auth-card">
          <div class="card-body text-start p-4">

            <div
              v-if="error"
              class="alert alert-danger"
            >
              {{ error }}
            </div>

            <form @submit.prevent="login">

              <div class="mb-3">
                <label
                  for="email"
                  class="form-label"
                >
                  📧 Email
                </label>
                <input
                  id="email"
                  v-model="email"
                  type="email"
                  class="form-control"
                  placeholder="Enter your email"
                  required
                >
              </div>

              <div class="mb-4">
                <label
                  for="password"
                  class="form-label"
                >
                  🔒 Password
                </label>
                <input
                  id="password"
                  v-model="password"
                  type="password"
                  class="form-control"
                  placeholder="Enter your password"
                  required
                >
              </div>

              <button
                type="submit"
                class="btn btn-primary w-100"
                :disabled="loading"
              >
                {{ loading ? 'Signing in...' : '🎮 Login' }}
              </button>

            </form>

            <p class="text-center mt-3 mb-0 small">
              Don't have an account?
              <router-link to="/register">
                Register here
              </router-link>
            </p>

          </div>
        </div>

      </div>
    </div>

  </div>
</template>