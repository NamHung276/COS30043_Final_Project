// src/components/ReviewSection.vue
<script>
import { auth, db } from '../firebase'
import { onAuthStateChanged } from 'firebase/auth'
import {
  collection,
  query,
  where,
  orderBy,
  getDocs,
  addDoc,
  updateDoc,
  deleteDoc,
  doc,
  serverTimestamp
} from 'firebase/firestore'

export default {
  name: 'ReviewSection',

  props: {
    gameId: {
      type: [String, Number],
      required: true
    }
  },

  data() {
    return {
      currentUser: null,
      reviews: [],
      loading: true,

      // Form state for creating a new review
      newRating: 5,
      newComment: '',
      submitting: false,
      formError: '',

      // Editing state
      editingReviewId: null,
      editRating: 5,
      editComment: ''
    }
  },

  computed: {
    myReview() {
      if (!this.currentUser) return null
      return this.reviews.find(
        review => review.userId === this.currentUser.uid
      )
    },

    averageRating() {
      if (this.reviews.length === 0) return 0
      const total = this.reviews.reduce(
        (sum, review) => sum + review.rating, 0
      )
      return (total / this.reviews.length).toFixed(1)
    }
  },

  methods: {
    async loadReviews() {
      this.loading = true

      const reviewsQuery = query(
        collection(db, 'reviews'),
        where('gameId', '==', this.gameId)
      )

      const snapshot = await getDocs(reviewsQuery)

      this.reviews = snapshot.docs
        .map(docSnap => ({
          id: docSnap.id,
          ...docSnap.data()
        }))
        .sort((a, b) => {
          // Newest first; fall back gracefully if timestamp missing
          const aTime = a.createdAt?.seconds || 0
          const bTime = b.createdAt?.seconds || 0
          return bTime - aTime
        })

      this.loading = false
    },

    async submitReview() {
      this.formError = ''

      if (!this.currentUser) {
        this.$router.push('/login')
        return
      }

      if (!this.newComment.trim()) {
        this.formError = 'Please write a comment before submitting.'
        return
      }

      if (this.myReview) {
        this.formError = 'You already reviewed this game. Edit your existing review instead.'
        return
      }

      this.submitting = true

      try {
        await addDoc(collection(db, 'reviews'), {
          gameId: this.gameId,
          userId: this.currentUser.uid,
          userName: this.currentUser.displayName || this.currentUser.email,
          rating: this.newRating,
          comment: this.newComment.trim(),
          createdAt: serverTimestamp()
        })

        this.newComment = ''
        this.newRating = 5
        await this.loadReviews()

      } catch (error) {
        console.error('Failed to submit review:', error)
        this.formError = 'Something went wrong. Please try again.'
      } finally {
        this.submitting = false
      }
    },

    startEdit(review) {
      this.editingReviewId = review.id
      this.editRating = review.rating
      this.editComment = review.comment
    },

    cancelEdit() {
      this.editingReviewId = null
    },

    async saveEdit(reviewId) {
      if (!this.editComment.trim()) return

      try {
        await updateDoc(doc(db, 'reviews', reviewId), {
          rating: this.editRating,
          comment: this.editComment.trim()
        })

        this.editingReviewId = null
        await this.loadReviews()

      } catch (error) {
        console.error('Failed to update review:', error)
      }
    },

    async deleteReview(reviewId) {
      try {
        await deleteDoc(doc(db, 'reviews', reviewId))
        await this.loadReviews()
      } catch (error) {
        console.error('Failed to delete review:', error)
      }
    }
  },

  mounted() {
    onAuthStateChanged(auth, (user) => {
      this.currentUser = user
    })
    this.loadReviews()
  }
}
</script>

<template>
  <div class="review-section">

    <div class="d-flex justify-content-between align-items-center mb-3">
      <h3 class="mb-0">Reviews</h3>
      <span v-if="reviews.length" class="text-muted">
        ⭐ {{ averageRating }} average ({{ reviews.length }} review{{ reviews.length === 1 ? '' : 's' }})
      </span>
    </div>

    <!-- Write a Review Form -->
    <div
      v-if="currentUser && !myReview"
      class="card mb-4"
    >
      <div class="card-body text-start">
        <h5 class="mb-3">Write a Review</h5>

        <div
          v-if="formError"
          class="alert alert-danger py-2"
        >
          {{ formError }}
        </div>

        <div class="mb-3">
          <label
            for="newRating"
            class="form-label"
          >
            Rating
          </label>
          <select
            id="newRating"
            v-model.number="newRating"
            class="form-select"
            style="max-width: 150px;"
          >
            <option :value="5">⭐⭐⭐⭐⭐ (5)</option>
            <option :value="4">⭐⭐⭐⭐ (4)</option>
            <option :value="3">⭐⭐⭐ (3)</option>
            <option :value="2">⭐⭐ (2)</option>
            <option :value="1">⭐ (1)</option>
          </select>
        </div>

        <div class="mb-3">
          <label
            for="newComment"
            class="form-label"
          >
            Comment
          </label>
          <textarea
            id="newComment"
            v-model="newComment"
            class="form-control"
            rows="3"
            placeholder="Share your thoughts on this game..."
          ></textarea>
        </div>

        <button
          class="btn btn-primary"
          :disabled="submitting"
          @click="submitReview"
        >
          {{ submitting ? 'Submitting...' : 'Submit Review' }}
        </button>
      </div>
    </div>

    <div
      v-else-if="!currentUser"
      class="alert alert-info"
    >
      <router-link to="/login">Login</router-link> to write a review.
    </div>

    <!-- Loading -->
    <div v-if="loading" class="text-center py-3">
      <div class="spinner-border spinner-border-sm text-primary" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
    </div>

    <!-- No Reviews -->
    <div
      v-else-if="reviews.length === 0"
      class="alert alert-secondary"
    >
      No reviews yet. Be the first to share your thoughts!
    </div>

    <!-- Review List -->
    <div
      v-else
      v-for="review in reviews"
      :key="review.id"
      class="card mb-3"
    >
      <div class="card-body text-start">

        <!-- Edit Mode -->
        <div v-if="editingReviewId === review.id">

          <div class="mb-2">
            <select
              v-model.number="editRating"
              class="form-select"
              style="max-width: 150px;"
            >
              <option :value="5">⭐⭐⭐⭐⭐ (5)</option>
              <option :value="4">⭐⭐⭐⭐ (4)</option>
              <option :value="3">⭐⭐⭐ (3)</option>
              <option :value="2">⭐⭐ (2)</option>
              <option :value="1">⭐ (1)</option>
            </select>
          </div>

          <textarea
            v-model="editComment"
            class="form-control mb-2"
            rows="3"
          ></textarea>

          <button
            class="btn btn-success btn-sm me-2"
            @click="saveEdit(review.id)"
          >
            Save
          </button>
          <button
            class="btn btn-secondary btn-sm"
            @click="cancelEdit"
          >
            Cancel
          </button>

        </div>

        <!-- Display Mode -->
        <div v-else>

          <div class="d-flex justify-content-between align-items-start">
            <div>
              <strong>{{ review.userName }}</strong>
              <span class="text-warning ms-2">
                {{ '⭐'.repeat(review.rating) }}
              </span>
            </div>

            <div v-if="currentUser && review.userId === currentUser.uid">
              <button
                class="btn btn-outline-secondary btn-sm me-1"
                @click="startEdit(review)"
              >
                Edit
              </button>
              <button
                class="btn btn-outline-danger btn-sm"
                @click="deleteReview(review.id)"
              >
                Delete
              </button>
            </div>
          </div>

          <p class="mb-0 mt-2">
            {{ review.comment }}
          </p>

        </div>

      </div>
    </div>

  </div>
</template>