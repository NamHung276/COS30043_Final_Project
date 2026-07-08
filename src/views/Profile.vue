// src/views/Profile.vue
<script>
import { auth } from '../firebase'
import { onAuthStateChanged, updateProfile, updatePassword, reauthenticateWithCredential, EmailAuthProvider } from 'firebase/auth'

export default {
  name: 'ProfileView',

  inject: ['toast'],

  data() {
    return {
      currentUser: null,

      // Edit name
      newName: '',
      nameLoading: false,
      nameTouched: false,

      // Change password
      currentPassword: '',
      newPassword: '',
      confirmNewPassword: '',
      pwLoading: false,
      pwTouched: {
        currentPassword: false,
        newPassword: false,
        confirmNewPassword: false
      },

      unsubscribe: null
    }
  },

  computed: {
    userInitial() {
      if (!this.currentUser) return '?'
      const name = this.currentUser.displayName || this.currentUser.email
      return name.charAt(0).toUpperCase()
    },

    memberSince() {
      if (!this.currentUser?.metadata?.creationTime) return '—'
      return new Date(this.currentUser.metadata.creationTime).toLocaleDateString('en-AU', {
        year: 'numeric', month: 'long', day: 'numeric'
      })
    },

    // Name validation
    nameError() {
      if (!this.nameTouched) return ''
      if (!this.newName.trim()) return 'Name cannot be empty.'
      if (this.newName.trim().length < 2) return 'Name must be at least 2 characters.'
      return ''
    },

    nameUnchanged() {
      return this.newName.trim() === (this.currentUser?.displayName || '')
    },

    // Password validation
    currentPasswordError() {
      if (!this.pwTouched.currentPassword) return ''
      if (!this.currentPassword) return 'Current password is required.'
      return ''
    },

    newPasswordError() {
      if (!this.pwTouched.newPassword) return ''
      if (!this.newPassword) return 'New password is required.'
      if (this.newPassword.length < 6) return 'Password must be at least 6 characters.'
      return ''
    },

    confirmNewPasswordError() {
      if (!this.pwTouched.confirmNewPassword) return ''
      if (!this.confirmNewPassword) return 'Please confirm your new password.'
      if (this.newPassword !== this.confirmNewPassword) return 'Passwords do not match.'
      return ''
    },

    isPwFormValid() {
      return (
        !this.currentPasswordError &&
        !this.newPasswordError &&
        !this.confirmNewPasswordError &&
        this.currentPassword &&
        this.newPassword &&
        this.confirmNewPassword
      )
    },

    passwordStrength() {
      if (!this.newPassword) return 0
      let s = 0
      if (this.newPassword.length >= 6) s++
      if (this.newPassword.length >= 8) s++
      if (/[A-Z]/.test(this.newPassword)) s++
      if (/[0-9]/.test(this.newPassword)) s++
      if (/[^A-Za-z0-9]/.test(this.newPassword)) s++
      return s
    },

    strengthLabel() {
      return ['', 'Weak', 'Fair', 'Good', 'Strong', 'Very Strong'][this.passwordStrength] || ''
    },

    strengthColor() {
      return ['', '#ef4444', '#f59e0b', '#eab308', '#22c55e', '#06b6d4'][this.passwordStrength] || ''
    }
  },

  mounted() {
    this.unsubscribe = onAuthStateChanged(auth, (user) => {
      this.currentUser = user
      if (user) {
        this.newName = user.displayName || ''
      } else {
        this.$router.push('/login')
      }
    })
  },

  beforeUnmount() {
    if (this.unsubscribe) this.unsubscribe()
  },

  methods: {
    touchPw(field) {
      this.pwTouched[field] = true
    },

    async saveName() {
      this.nameTouched = true
      if (this.nameError || this.nameUnchanged || this.nameLoading) return

      this.nameLoading = true
      try {
        await updateProfile(this.currentUser, {
          displayName: this.newName.trim()
        })
        // Force refresh the local user reference
        await this.currentUser.reload()
        this.currentUser = auth.currentUser
        this.toast.show('Display name updated! ✨', 'success')
      } catch (err) {
        console.error(err)
        this.toast.show('Failed to update name. Please try again.', 'error')
      } finally {
        this.nameLoading = false
      }
    },

    async changePassword() {
      Object.keys(this.pwTouched).forEach(k => this.pwTouched[k] = true)
      if (!this.isPwFormValid || this.pwLoading) return

      this.pwLoading = true
      try {
        // Re-authenticate first
        const credential = EmailAuthProvider.credential(
          this.currentUser.email,
          this.currentPassword
        )
        await reauthenticateWithCredential(this.currentUser, credential)

        // Now update password
        await updatePassword(this.currentUser, this.newPassword)

        this.toast.show('Password changed successfully! 🔒', 'success')

        // Reset form
        this.currentPassword = ''
        this.newPassword = ''
        this.confirmNewPassword = ''
        Object.keys(this.pwTouched).forEach(k => this.pwTouched[k] = false)

      } catch (err) {
        console.error(err)
        if (err.code === 'auth/wrong-password' || err.code === 'auth/invalid-credential') {
          this.toast.show('Current password is incorrect.', 'error')
        } else if (err.code === 'auth/too-many-requests') {
          this.toast.show('Too many attempts. Please try again later.', 'warning')
        } else {
          this.toast.show('Failed to change password. Please try again.', 'error')
        }
      } finally {
        this.pwLoading = false
      }
    }
  }
}
</script>

<template>
  <div class="container py-5" v-if="currentUser">

    <!-- Page Header -->
    <div class="profile-page-header text-center mb-5">
      <div class="profile-avatar-large mx-auto mb-3">
        {{ userInitial }}
      </div>
      <h1 class="mb-1" style="font-size: 1.9rem;">
        {{ currentUser.displayName || 'Gamer' }}
      </h1>
      <p class="text-muted mb-3">{{ currentUser.email }}</p>
      <div class="d-flex justify-content-center gap-2 flex-wrap">
        <span class="profile-badge profile-badge-email">
          <i class="bi bi-envelope me-1"></i>{{ currentUser.email }}
        </span>
        <span class="profile-badge profile-badge-member">
          <i class="bi bi-calendar me-1"></i>Member since {{ memberSince }}
        </span>
      </div>
    </div>

    <div class="row justify-content-center g-4">

      <!-- ---- Edit Display Name ---- -->
      <div class="col-lg-5 col-md-6">
        <div class="card profile-section-card h-100">

          <div class="profile-section-accent" style="--accent-color: var(--primary);"></div>

          <div class="card-body p-4">
            <div class="section-header mb-4">
              <span class="profile-section-icon" style="background: rgba(59,130,246,0.15); color: var(--primary-light);">
                <i class="bi bi-person"></i>
              </span>
              <div>
                <h2 class="mb-0" style="font-size: 1.15rem;">Edit Display Name</h2>
                <p class="text-muted mb-0" style="font-size: 0.82rem;">This name appears across GameHub</p>
              </div>
            </div>

            <form @submit.prevent="saveName">
              <div class="mb-3">
                <label for="profileName" class="form-label">Display Name</label>
                <input
                  id="profileName"
                  v-model="newName"
                  type="text"
                  class="form-control"
                  :class="{
                    'is-invalid': nameError,
                    'is-valid': nameTouched && !nameError && newName
                  }"
                  placeholder="Your display name"
                  @blur="nameTouched = true"
                />
                <div v-if="nameError" class="invalid-feedback">{{ nameError }}</div>
              </div>

              <button
                type="submit"
                class="btn btn-primary w-100"
                :disabled="nameLoading || nameUnchanged"
              >
                <span v-if="nameLoading" class="spinner-border spinner-border-sm me-2"></span>
                <template v-if="nameLoading">Saving...</template>
                <template v-else><i class="bi bi-floppy me-1"></i>Save Name</template>
              </button>

              <p v-if="nameUnchanged && nameTouched" class="text-muted text-center mt-2 mb-0" style="font-size: 0.82rem;">
                No changes to save.
              </p>
            </form>
          </div>
        </div>
      </div>

      <!-- ---- Change Password ---- -->
      <div class="col-lg-5 col-md-6">
        <div class="card profile-section-card h-100">

          <div class="profile-section-accent" style="--accent-color: var(--accent);"></div>

          <div class="card-body p-4">
            <div class="section-header mb-4">
              <span class="profile-section-icon" style="background: rgba(139,92,246,0.15); color: var(--accent-light);">
                <i class="bi bi-lock"></i>
              </span>
              <div>
                <h2 class="mb-0" style="font-size: 1.15rem;">Change Password</h2>
                <p class="text-muted mb-0" style="font-size: 0.82rem;">Requires your current password</p>
              </div>
            </div>

            <form @submit.prevent="changePassword">

              <!-- Current Password -->
              <div class="mb-3">
                <label for="currentPassword" class="form-label">Current Password</label>
                <input
                  id="currentPassword"
                  v-model="currentPassword"
                  type="password"
                  class="form-control"
                  :class="{
                    'is-invalid': currentPasswordError,
                    'is-valid': pwTouched.currentPassword && !currentPasswordError && currentPassword
                  }"
                  placeholder="Enter current password"
                  @blur="touchPw('currentPassword')"
                />
                <div v-if="currentPasswordError" class="invalid-feedback">{{ currentPasswordError }}</div>
              </div>

              <!-- New Password -->
              <div class="mb-3">
                <label for="newPassword" class="form-label">New Password</label>
                <input
                  id="newPassword"
                  v-model="newPassword"
                  type="password"
                  class="form-control"
                  :class="{
                    'is-invalid': newPasswordError,
                    'is-valid': pwTouched.newPassword && !newPasswordError && newPassword
                  }"
                  placeholder="At least 6 characters"
                  @blur="touchPw('newPassword')"
                />
                <div v-if="newPasswordError" class="invalid-feedback">{{ newPasswordError }}</div>

                <!-- Strength bar -->
                <div v-if="newPassword && !newPasswordError" class="mt-2">
                  <div style="height: 4px; border-radius: 2px; background: var(--bg-glass); overflow: hidden;">
                    <div
                      :style="{
                        width: (passwordStrength / 5 * 100) + '%',
                        height: '100%',
                        background: strengthColor,
                        borderRadius: '2px',
                        transition: 'all 0.3s ease'
                      }"
                    ></div>
                  </div>
                  <small :style="{ color: strengthColor }" class="mt-1 d-block">{{ strengthLabel }}</small>
                </div>
              </div>

              <!-- Confirm New Password -->
              <div class="mb-4">
                <label for="confirmNewPassword" class="form-label">Confirm New Password</label>
                <input
                  id="confirmNewPassword"
                  v-model="confirmNewPassword"
                  type="password"
                  class="form-control"
                  :class="{
                    'is-invalid': confirmNewPasswordError,
                    'is-valid': pwTouched.confirmNewPassword && !confirmNewPasswordError && confirmNewPassword
                  }"
                  placeholder="Repeat your new password"
                  @blur="touchPw('confirmNewPassword')"
                />
                <div v-if="confirmNewPasswordError" class="invalid-feedback">{{ confirmNewPasswordError }}</div>
              </div>

              <button
                type="submit"
                class="btn w-100 btn-change-pw"
                :disabled="pwLoading"
              >
                <span v-if="pwLoading" class="spinner-border spinner-border-sm me-2"></span>
                <template v-if="pwLoading">Changing...</template>
                <template v-else><i class="bi bi-key me-1"></i>Change Password</template>
              </button>
            </form>
          </div>
        </div>
      </div>

    </div>
  </div>

  <!-- Loading state while auth resolves -->
  <div v-else class="text-center py-5">
    <div class="spinner-border" role="status"></div>
    <p class="text-muted mt-3">Loading your profile…</p>
  </div>
</template>
