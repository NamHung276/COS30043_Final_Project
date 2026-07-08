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

    setNewRating(rating) {
      this.newRating = rating
    },

    setEditRating(rating) {
      this.editRating = rating
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

      if (
        !confirm(
          'Delete this review?'
        )
      ) {
        return
      }

      try {
        await deleteDoc(
          doc(db, 'reviews', reviewId)
        )

        await this.loadReviews()

      } catch (error) {
        console.error(
          'Failed to delete review:',
          error
        )
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
      <div class="section-header mb-0">
        <span class="section-icon"><i class="bi bi-chat-left-text-fill"></i></span>
        <h3 class="mb-0">
          Reviews ({{ reviews.length }})
        </h3>
      </div>

      <span v-if="reviews.length" class="text-muted" style="font-size: 0.9rem;">
        <i class="bi bi-star-fill text-warning me-1"></i>{{ averageRating }} average
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
          <label class="form-label">
            Rating
          </label>
          <div class="star-rating">
            <span
              v-for="star in 5"
              :key="star"
              class="star"
              @click="setNewRating(star)"
            >
              <i :class="star <= newRating ? 'bi bi-star-fill text-warning' : 'bi bi-star'"></i>
            </span>
          </div>
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
            maxlength="1000"
            placeholder="Share your thoughts on this game..."
          ></textarea>
          <small class="text-muted">
            {{ newComment.length }}/1000 characters
          </small>
        </div>

        <button
          class="btn btn-primary"
          :disabled="submitting"
          @click="submitReview"
        >
          <template v-if="submitting">Submitting...</template>
          <template v-else><i class="bi bi-pencil-square me-1"></i>Submit Review</template>
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
      class="empty-state" style="padding: 30px 20px;"
    >
      <div class="empty-state-icon"><i class="bi bi-chat-left-dots" style="font-size:2.5rem;"></i></div>
      <h3 style="font-size: 1.1rem;">No reviews yet</h3>
      <p style="font-size: 0.9rem;">Be the first to share your thoughts!</p>
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
            <label class="form-label">Rating</label>
            <div class="star-rating">
              <span
                v-for="star in 5"
                :key="star"
                class="star"
                @click="setEditRating(star)"
              >
                <i :class="star <= editRating ? 'bi bi-star-fill text-warning' : 'bi bi-star'"></i>
              </span>
            </div>
          </div>

          <textarea
            v-model="editComment"
            class="form-control mb-2"
            rows="3"
            maxlength="1000"
          ></textarea>

          <div class="d-flex gap-2">
            <button
              class="btn btn-success btn-sm"
              @click="saveEdit(review.id)"
            >
              <i class="bi bi-floppy me-1"></i>Save
            </button>
            <button
              class="btn btn-outline-secondary btn-sm"
              @click="cancelEdit"
            >
              Cancel
            </button>
          </div>

        </div>

        <!-- Display Mode -->
        <div v-else>

          <div class="d-flex justify-content-between align-items-start">
            <div>
              <strong>{{ review.userName }}</strong>

              <span class="text-warning ms-2">
                <template v-for="s in review.rating" :key="s">
                  <i class="bi bi-star-fill"></i>
                </template>
              </span>

              <div
                v-if="review.createdAt"
                class="small text-muted"
              >
                {{ new Date(
                  review.createdAt.seconds * 1000
                ).toLocaleDateString() }}
              </div>
            </div>

            <div v-if="currentUser && review.userId === currentUser.uid" class="d-flex gap-1">
              <button
                class="btn btn-outline-secondary btn-sm"
                @click="startEdit(review)"
                aria-label="Edit review"
              >
                <i class="bi bi-pencil"></i>
              </button>
              <button
                class="btn btn-outline-danger btn-sm"
                @click="deleteReview(review.id)"
                aria-label="Delete review"
              >
                <i class="bi bi-trash"></i>
              </button>
            </div>
          </div>

          <p class="mb-0 mt-2 text-muted">
            {{ review.comment }}
          </p>

        </div>

      </div>
    </div>

  </div>
</template>