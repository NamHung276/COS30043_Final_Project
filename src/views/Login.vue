<script>
export default {
  data() {
    return {
      email: '',
      password: '',
      error: ''
    }
  },

  methods: {
    login() {
      this.error = ''

      const users =
        JSON.parse(
          localStorage.getItem('users')
        ) || []

      const user =
        users.find(
          user =>
            user.email === this.email &&
            user.password === this.password
        )

      if (!user) {
        this.error = 'Invalid email or password.'
        return
      }

      localStorage.setItem(
        'currentUser',
        JSON.stringify(user)
      )

      // Notify navbar to update instantly
      window.dispatchEvent(new Event('auth-updated'))

      // Redirect to home
      this.$router.push('/')
    }
  }
}
</script>

<template>
  <div class="container py-4">

    <h1 class="mb-4">Login</h1>

    <div class="row justify-content-center">
      <div class="col-md-5">

        <div class="card">
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
                  Email
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

              <div class="mb-3">
                <label
                  for="password"
                  class="form-label"
                >
                  Password
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
              >
                Login
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