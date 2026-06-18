<script>
import { auth } from '../firebase'
import {
  createUserWithEmailAndPassword,
  updateProfile
} from 'firebase/auth'

export default {
  data() {
    return {
      name: '',
      email: '',
      password: '',
      confirmPassword: '',
      error: '',
      success: '',
      loading: false,
      touched: {
        name: false,
        email: false,
        password: false,
        confirmPassword: false
      }
    }
  },

  computed: {
    nameError() {
      if (!this.touched.name) return ''
      if (!this.name) return 'Name is required.'
      if (this.name.length < 2) return 'Name must be at least 2 characters.'
      return ''
    },

    emailError() {
      if (!this.touched.email) return ''
      if (!this.email) return 'Email is required.'
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
      if (!emailRegex.test(this.email)) return 'Please enter a valid email.'
      return ''
    },

    passwordError() {
      if (!this.touched.password) return ''
      if (!this.password) return 'Password is required.'
      if (this.password.length < 6) return 'Password must be at least 6 characters.'
      return ''
    },

    confirmPasswordError() {
      if (!this.touched.confirmPassword) return ''
      if (!this.confirmPassword) return 'Please confirm your password.'
      if (this.password !== this.confirmPassword) return 'Passwords do not match.'
      return ''
    },

    isFormValid() {
      return (
        !this.nameError &&
        !this.emailError &&
        !this.passwordError &&
        !this.confirmPasswordError &&
        this.name &&
        this.email &&
        this.password &&
        this.confirmPassword
      )
    }
  },

  methods: {
    touch(field) {
      this.touched[field] = true
    },

    async register() {
      // Touch all fields to show all errors at once
      Object.keys(this.touched).forEach(
        field => this.touched[field] = true
      )

      this.error = ''
      this.success = ''

      if (!this.isFormValid) return

      this.loading = true

      try {
        const userCredential = await createUserWithEmailAndPassword(
          auth,
          this.email,
          this.password
        )

        // Save the display name on the Firebase user profile
        await updateProfile(userCredential.user, {
          displayName: this.name
        })

        this.success = 'Registration successful! Redirecting to login...'

        setTimeout(() => {
          this.$router.push('/login')
        }, 1500)

      } catch (error) {
        if (error.code === 'auth/email-already-in-use') {
          this.error = 'Email already registered.'
        } else if (error.code === 'auth/invalid-email') {
          this.error = 'Invalid email address.'
        } else if (error.code === 'auth/weak-password') {
          this.error = 'Password is too weak.'
        } else {
          this.error = 'Registration failed. Please try again.'
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
  <div class="container py-4">

    <h1 class="mb-4">Register</h1>

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

            <div
              v-if="success"
              class="alert alert-success"
            >
              {{ success }}
            </div>

            <form @submit.prevent="register">

              <!-- Name -->
              <div class="mb-3">
                <label
                  for="name"
                  class="form-label"
                >
                  Name
                </label>
                <input
                  id="name"
                  v-model="name"
                  type="text"
                  class="form-control"
                  :class="{
                    'is-invalid': nameError,
                    'is-valid': touched.name && !nameError && name
                  }"
                  placeholder="Your full name"
                  @blur="touch('name')"
                >
                <div
                  v-if="nameError"
                  class="invalid-feedback"
                >
                  {{ nameError }}
                </div>
              </div>

              <!-- Email -->
              <div class="mb-3">
                <label
                  for="regEmail"
                  class="form-label"
                >
                  Email
                </label>
                <input
                  id="regEmail"
                  v-model="email"
                  type="email"
                  class="form-control"
                  :class="{
                    'is-invalid': emailError,
                    'is-valid': touched.email && !emailError && email
                  }"
                  placeholder="your@email.com"
                  @blur="touch('email')"
                >
                <div
                  v-if="emailError"
                  class="invalid-feedback"
                >
                  {{ emailError }}
                </div>
              </div>

              <!-- Password -->
              <div class="mb-3">
                <label
                  for="regPassword"
                  class="form-label"
                >
                  Password
                </label>
                <input
                  id="regPassword"
                  v-model="password"
                  type="password"
                  class="form-control"
                  :class="{
                    'is-invalid': passwordError,
                    'is-valid': touched.password && !passwordError && password
                  }"
                  placeholder="At least 6 characters"
                  @blur="touch('password')"
                >
                <div
                  v-if="passwordError"
                  class="invalid-feedback"
                >
                  {{ passwordError }}
                </div>
              </div>

              <!-- Confirm Password -->
              <div class="mb-4">
                <label
                  for="confirmPassword"
                  class="form-label"
                >
                  Confirm Password
                </label>
                <input
                  id="confirmPassword"
                  v-model="confirmPassword"
                  type="password"
                  class="form-control"
                  :class="{
                    'is-invalid': confirmPasswordError,
                    'is-valid': touched.confirmPassword && !confirmPasswordError && confirmPassword
                  }"
                  placeholder="Repeat your password"
                  @blur="touch('confirmPassword')"
                >
                <div
                  v-if="confirmPasswordError"
                  class="invalid-feedback"
                >
                  {{ confirmPasswordError }}
                </div>
              </div>

              <button
                type="submit"
                class="btn btn-primary w-100"
                :disabled="loading"
              >
                {{ loading ? 'Registering...' : 'Register' }}
              </button>

            </form>

            <p class="text-center mt-3 mb-0 small">
              Already have an account?
              <router-link to="/login">
                Login here
              </router-link>
            </p>

          </div>
        </div>

      </div>
    </div>

  </div>
</template>