<script>
export default {
  data() {
    return {
      name: '',
      email: '',
      password: '',
      confirmPassword: '',
      error: '',
      success: ''
    }
  },

  methods: {
    register() {

      this.error = ''
      this.success = ''

      if (
        !this.name ||
        !this.email ||
        !this.password ||
        !this.confirmPassword
      ) {
        this.error = 'All fields are required.'
        return
      }

      if (
        this.password !==
        this.confirmPassword
      ) {
        this.error = 'Passwords do not match.'
        return
      }

      const users =
        JSON.parse(
          localStorage.getItem('users')
        ) || []

      const existingUser =
        users.find(
          user => user.email === this.email
        )

      if (existingUser) {
        this.error =
          'Email already registered.'
        return
      }

      users.push({
        name: this.name,
        email: this.email,
        password: this.password
      })

      localStorage.setItem(
        'users',
        JSON.stringify(users)
      )

      this.success =
        'Registration successful!'

      this.name = ''
      this.email = ''
      this.password = ''
      this.confirmPassword = ''
    }
  }
}
</script>

<template>
  <div class="container py-4">

    <h1 class="mb-4">
      Register
    </h1>

    <div
      v-if="error"
      class="alert alert-danger"
    >
      {{ error }}
    </div>

    <div
      v-if="success"
      class="alert alert-success"
    >
      {{ success }}
    </div>

    <form @submit.prevent="register">

      <div class="mb-3">
        <label class="form-label">
          Name
        </label>

        <input
          v-model="name"
          type="text"
          class="form-control"
        >
      </div>

      <div class="mb-3">
        <label class="form-label">
          Email
        </label>

        <input
          v-model="email"
          type="email"
          class="form-control"
        >
      </div>

      <div class="mb-3">
        <label class="form-label">
          Password
        </label>

        <input
          v-model="password"
          type="password"
          class="form-control"
        >
      </div>

      <div class="mb-3">
        <label class="form-label">
          Confirm Password
        </label>

        <input
          v-model="confirmPassword"
          type="password"
          class="form-control"
        >
      </div>

      <button
        type="submit"
        class="btn btn-primary"
      >
        Register
      </button>

    </form>

  </div>
</template>