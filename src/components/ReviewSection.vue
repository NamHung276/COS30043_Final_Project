<script>
import { auth, db } from "../firebase";
import { onAuthStateChanged } from "firebase/auth";
import {
  collection,
  query,
  where,
  getDocs,
  addDoc,
  updateDoc,
  deleteDoc,
  doc,
  serverTimestamp,
} from "firebase/firestore";

export default {
  name: "ReviewSection",

  inject: ["toast"],

  props: {
    gameId: {
      type: [String, Number],
      required: true,
    },
    gameTitle: {
      type: String,
      default: "",
    },
  },

  data() {
    return {
      currentUser: null,
      reviews: [],
      loading: true,
      sortBy: "newest",

      // Form state for creating a new review
      newRating: 5,
      newComment: "",
      submitting: false,
      formError: "",

      // Editing state
      editingReviewId: null,
      editRating: 5,
      editComment: "",
    };
  },

  computed: {
    myReview() {
      if (!this.currentUser) return null;
      return this.reviews.find(
        (review) => review.userId === this.currentUser.uid,
      );
    },

    averageRating() {
      if (this.reviews.length === 0) return 0;
      const total = this.reviews.reduce(
        (sum, review) => sum + review.rating,
        0,
      );
      return (total / this.reviews.length).toFixed(1);
    },

    averageRatingLabel() {
      if (!this.reviews.length) return "";
      const r = parseFloat(this.averageRating);
      if (r >= 4.5) return "Excellent";
      if (r >= 4.0) return "Good";
      if (r >= 3.0) return "Mixed";
      return "Poor";
    },

    averageRatingClass() {
      if (!this.reviews.length) return "";
      const r = parseFloat(this.averageRating);
      if (r >= 4.5) return "rating-excellent";
      if (r >= 4.0) return "rating-good";
      if (r >= 3.0) return "rating-mixed";
      return "rating-poor";
    },

    ratingStats() {
      const stats = { 5: 0, 4: 0, 3: 0, 2: 0, 1: 0 };
      this.reviews.forEach((r) => {
        if (stats[r.rating] !== undefined) {
          stats[r.rating]++;
        }
      });
      return [5, 4, 3, 2, 1].map((stars) => ({
        stars,
        count: stats[stars],
      }));
    },

    sortedReviews() {
      const list = [...this.reviews];

      switch (this.sortBy) {
        case "highest":
          return list.sort((a, b) => b.rating - a.rating);
        case "lowest":
          return list.sort((a, b) => a.rating - b.rating);
        case "oldest":
          return list.sort(
            (a, b) => (a.createdAt?.seconds || 0) - (b.createdAt?.seconds || 0),
          );
        default:
          return list.sort(
            (a, b) => (b.createdAt?.seconds || 0) - (a.createdAt?.seconds || 0),
          );
      }
    },
  },

  methods: {
    async loadReviews() {
      this.loading = true;

      const reviewsQuery = query(
        collection(db, "reviews"),
        where("gameId", "==", this.gameId),
      );

      const snapshot = await getDocs(reviewsQuery);

      this.reviews = snapshot.docs.map((docSnap) => ({
        id: docSnap.id,
        ...docSnap.data(),
      }));

      this.loading = false;
    },

    setNewRating(rating) {
      this.newRating = rating;
    },

    setEditRating(rating) {
      this.editRating = rating;
    },

    async submitReview() {
      this.formError = "";

      if (!this.currentUser) {
        this.$router.push("/login");
        return;
      }

      if (!this.newComment.trim()) {
        this.formError = "Please write a comment before submitting.";
        return;
      }

      if (this.myReview) {
        this.formError =
          "You already reviewed this game. Edit your existing review instead.";
        return;
      }

      this.submitting = true;

      try {
        await addDoc(collection(db, "reviews"), {
          gameId: this.gameId,
          gameName: this.gameTitle,
          userId: this.currentUser.uid,
          userName: this.currentUser.displayName || this.currentUser.email,
          rating: this.newRating,
          comment: this.newComment.trim(),
          likes: [],
          dislikes: [],
          createdAt: serverTimestamp(),
        });

        this.newComment = "";
        this.newRating = 5;
        await this.loadReviews();
      } catch (error) {
        console.error("Failed to submit review:", error);
        this.formError = "Something went wrong. Please try again.";
      } finally {
        this.submitting = false;
      }
    },

    startEdit(review) {
      this.editingReviewId = review.id;
      this.editRating = review.rating;
      this.editComment = review.comment;
    },

    cancelEdit() {
      this.editingReviewId = null;
    },

    async saveEdit(reviewId) {
      if (!this.editComment.trim()) return;

      try {
        await updateDoc(doc(db, "reviews", reviewId), {
          rating: this.editRating,
          comment: this.editComment.trim(),
        });

        this.editingReviewId = null;
        await this.loadReviews();
      } catch (error) {
        console.error("Failed to update review:", error);
        this.toast?.show("Failed to save changes. Please try again.", "error");
      }
    },

    async deleteReview(reviewId) {
      if (!confirm("Delete this review?")) {
        return;
      }

      try {
        await deleteDoc(doc(db, "reviews", reviewId));

        await this.loadReviews();
      } catch (error) {
        console.error("Failed to delete review:", error);
        this.toast?.show("Failed to delete review. Please try again.", "error");
      }
    },

    async toggleVote(reviewId, type) {
      if (!this.currentUser) {
        this.$router.push("/login");
        return;
      }

      const uid = this.currentUser.uid;
      const review = this.reviews.find((r) => r.id === reviewId);
      if (!review) return;

      // Snapshot previous state so we can roll back if the write fails
      const prevLikes = [...(review.likes || [])];
      const prevDislikes = [...(review.dislikes || [])];

      let likes = [...prevLikes];
      let dislikes = [...prevDislikes];

      if (type === "like") {
        if (likes.includes(uid)) {
          likes = likes.filter((id) => id !== uid);
        } else {
          likes.push(uid);
          dislikes = dislikes.filter((id) => id !== uid);
        }
      } else {
        if (dislikes.includes(uid)) {
          dislikes = dislikes.filter((id) => id !== uid);
        } else {
          dislikes.push(uid);
          likes = likes.filter((id) => id !== uid);
        }
      }

      review.likes = likes;
      review.dislikes = dislikes;

      try {
        await updateDoc(doc(db, "reviews", reviewId), { likes, dislikes });
      } catch (error) {
        console.error("Failed to vote:", error);
        // Roll back the optimistic update since the write didn't actually succeed
        review.likes = prevLikes;
        review.dislikes = prevDislikes;
        this.toast?.show(
          "Failed to save your vote. Please try again.",
          "error",
        );
      }
    },

    timeAgo(seconds) {
      if (!seconds) return "Just now";
      const now = Math.floor(Date.now() / 1000);
      const diff = now - seconds;

      if (diff < 60) return "Just now";
      if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
      if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`;
      if (diff < 2592000) return `${Math.floor(diff / 86400)}d ago`;
      if (diff < 31536000) return `${Math.floor(diff / 2592000)}mo ago`;
      return `${Math.floor(diff / 31536000)}y ago`;
    },

    getAvatarColor(name) {
      const colors = [
        "#f56565",
        "#ed8936",
        "#ecc94b",
        "#48bb78",
        "#38b2ac",
        "#4299e1",
        "#667eea",
        "#9f7aea",
        "#ed64a6",
      ];
      if (!name) return colors[0];
      let hash = 0;
      for (let i = 0; i < name.length; i++)
        hash = name.charCodeAt(i) + ((hash << 5) - hash);
      return colors[Math.abs(hash) % colors.length];
    },
  },

  beforeUnmount() {
    if (this.unsubscribe) {
      this.unsubscribe();
    }
  },

  mounted() {
    this.unsubscribe = onAuthStateChanged(auth, (user) => {
      this.currentUser = user;
    });
    this.loadReviews();
  },
};
</script>

<template>
  <div class="review-section">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <div class="section-header mb-0">
        <h3 class="mb-0 gd-title-sm text-white">Community Reviews</h3>
        <p class="text-muted mb-0 small mt-1">
          {{ reviews.length }} reviews from GameHub players
        </p>
      </div>

      <div v-if="reviews.length" class="d-flex align-items-center gap-3">
        <select v-model="sortBy" class="gd-glass-select">
          <option value="newest">Newest</option>
          <option value="oldest">Oldest</option>
          <option value="highest">Highest Rating</option>
          <option value="lowest">Lowest Rating</option>
        </select>
      </div>
    </div>

    <!-- Average Review Card -->
    <div
      v-if="reviews.length"
      class="gd-glass-card mb-4 p-4 d-flex flex-wrap gap-5 align-items-center"
    >
      <div class="text-center" style="min-width: 140px">
        <h2 class="display-3 fw-bold mb-1" :class="averageRatingClass">
          {{ averageRating }}
        </h2>
        <div
          class="mb-1"
          :class="averageRatingClass"
          style="font-size: 1.15rem"
        >
          <template v-for="s in 5" :key="s">
            <i
              :class="
                s <= Math.round(averageRating)
                  ? 'bi bi-star-fill'
                  : 'bi bi-star'
              "
            ></i>
          </template>
        </div>
        <div class="fw-bold fs-5 mt-2" :class="averageRatingClass">
          {{ averageRatingLabel }}
        </div>
      </div>

      <div class="flex-grow-1" style="max-width: 400px">
        <div
          v-for="stat in ratingStats"
          :key="stat.stars"
          class="d-flex align-items-center gap-3 mb-2"
        >
          <span
            class="text-warning text-nowrap"
            style="width: 75px; font-size: 0.85rem"
          >
            <template v-for="s in stat.stars" :key="'sf' + s"
              ><i class="bi bi-star-fill"></i
            ></template>
            <template v-for="s in 5 - stat.stars" :key="'s' + s"
              ><i class="bi bi-star" style="opacity: 0.3"></i
            ></template>
          </span>
          <div
            class="progress flex-grow-1"
            style="
              height: 6px;
              background-color: var(--overlay-medium);
              border-radius: 4px;
              overflow: hidden;
            "
          >
            <div
              class="progress-bar"
              style="background-color: #ecc94b"
              :style="{ width: (stat.count / reviews.length) * 100 + '%' }"
            ></div>
          </div>
          <span
            class="text-muted text-end"
            style="min-width: 25px; font-size: 0.85rem"
            >{{ stat.count }}</span
          >
        </div>
      </div>
    </div>

    <!-- Login Prompt -->
    <div
      v-if="!currentUser"
      class="gd-glass-card p-5 text-center mb-4 login-prompt-box"
    >
      <h4 class="text-white mb-3">Want to share your experience?</h4>
      <router-link to="/login" class="btn gd-btn-primary px-4 py-2"
        >Login to Review</router-link
      >
    </div>

    <!-- Write a Review Form -->
    <div v-if="currentUser && !myReview" class="gd-glass-card mb-4">
      <div class="gd-review-card-body text-start">
        <h5 class="mb-4 text-white">Write a Review</h5>

        <div v-if="formError" class="alert alert-danger py-2">
          {{ formError }}
        </div>

        <div class="mb-3">
          <label
            class="form-label text-muted small text-uppercase fw-bold letter-spacing-1"
          >
            Rating
          </label>
          <div class="star-rating d-block">
            <span
              v-for="star in 5"
              :key="star"
              class="star"
              @click="setNewRating(star)"
            >
              <i
                :class="
                  star <= newRating
                    ? 'bi bi-star-fill text-warning'
                    : 'bi bi-star' + ' text-muted'
                "
              ></i>
            </span>
          </div>
        </div>

        <div class="mb-3">
          <div class="d-flex justify-content-between align-items-end mb-1">
            <label
              for="newComment"
              class="form-label text-muted small text-uppercase fw-bold letter-spacing-1 mb-0"
            >
              Comment
            </label>
            <small
              :class="{
                'text-danger fw-bold': newComment.length >= 980,
                'text-warning fw-bold':
                  newComment.length >= 900 && newComment.length < 980,
                'text-muted': newComment.length < 900,
              }"
            >
              {{ newComment.length }} / 1000
            </small>
          </div>
          <textarea
            id="newComment"
            v-model="newComment"
            class="gd-review-input"
            rows="4"
            maxlength="1000"
            placeholder="Share your thoughts on this game..."
            aria-label="Comment text area"
          ></textarea>
        </div>

        <button
          class="gd-btn-primary"
          :disabled="submitting"
          @click="submitReview"
        >
          <template v-if="submitting">Submitting...</template>
          <template v-else>Submit Review</template>
        </button>
      </div>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
    </div>

    <!-- Empty State -->
    <div
      v-else-if="reviews.length === 0"
      class="gd-glass-card text-center p-5 mb-4 empty-state-box"
    >
      <div class="mb-3" style="font-size: 3rem">🎮</div>
      <h4 class="text-white mb-2">Be the first to review!</h4>
      <p class="text-muted">Share your experience and help other players.</p>
    </div>

    <!-- Review List -->
    <div v-else class="reviews-container">
      <div
        v-for="(review, index) in sortedReviews"
        :key="review.id"
        class="gd-glass-card mb-4 p-4 staggered-review-card"
        :style="{ animationDelay: index * 0.08 + 's' }"
      >
        <!-- Edit Mode -->
        <div v-if="editingReviewId === review.id">
          <div class="mb-3">
            <label
              class="form-label text-muted small text-uppercase fw-bold letter-spacing-1"
              >Rating</label
            >
            <div class="star-rating d-block">
              <span
                v-for="star in 5"
                :key="star"
                class="star"
                @click="setEditRating(star)"
              >
                <i
                  :class="
                    star <= editRating
                      ? 'bi bi-star-fill text-warning'
                      : 'bi bi-star' + ' text-muted'
                  "
                ></i>
              </span>
            </div>
          </div>

          <div class="mb-3">
            <div class="d-flex justify-content-between align-items-end mb-1">
              <label
                class="form-label text-muted small text-uppercase fw-bold letter-spacing-1 mb-0"
                >Comment</label
              >
              <small
                :class="{
                  'text-danger fw-bold': editComment.length >= 980,
                  'text-warning fw-bold':
                    editComment.length >= 900 && editComment.length < 980,
                  'text-muted': editComment.length < 900,
                }"
              >
                {{ editComment.length }} / 1000
              </small>
            </div>
            <textarea
              v-model="editComment"
              class="gd-review-input"
              rows="4"
              maxlength="1000"
            ></textarea>
          </div>

          <div class="d-flex gap-3 mt-3">
            <button class="gd-btn-primary" @click="saveEdit(review.id)">
              Save Changes
            </button>
            <button class="gd-btn-secondary" @click="cancelEdit">Cancel</button>
          </div>
        </div>

        <!-- Display Mode -->
        <div v-else>
          <div class="d-flex gap-3">
            <!-- Left: Avatar -->
            <div class="review-avatar-container">
              <div
                class="review-avatar"
                :style="{
                  backgroundColor: getAvatarColor(review.userName),
                  boxShadow: `0 0 20px ${getAvatarColor(review.userName)}40`,
                }"
              >
                {{ (review.userName || "A").charAt(0).toUpperCase() }}
              </div>
            </div>

            <!-- Right: Content -->
            <div class="flex-grow-1 min-width-0">
              <div
                class="d-flex justify-content-between align-items-start flex-wrap gap-2"
              >
                <div>
                  <div class="d-flex align-items-center gap-2 mb-1">
                    <strong class="fs-5 text-white">{{
                      review.userName
                    }}</strong>
                    <span class="gd-badge-reviewer"
                      ><i class="bi bi-controller"></i> Reviewer</span
                    >
                  </div>
                  <div class="d-flex align-items-center flex-wrap gap-2 mb-2">
                    <span class="text-warning" style="font-size: 0.9rem">
                      <template v-for="s in review.rating" :key="'sr' + s"
                        ><i class="bi bi-star-fill"></i
                      ></template>
                      <template v-for="s in 5 - review.rating" :key="'se' + s"
                        ><i class="bi bi-star"></i
                      ></template>
                    </span>
                    <span class="text-white fw-bold" style="font-size: 0.85rem">
                      {{
                        review.rating >= 4
                          ? "Recommended"
                          : review.rating === 3
                            ? "Mixed"
                            : "Not Recommended"
                      }}
                    </span>
                    <span class="text-muted small"
                      >• Reviewed {{ timeAgo(review.createdAt?.seconds) }}</span
                    >
                  </div>
                </div>

                <div
                  v-if="currentUser && review.userId === currentUser.uid"
                  class="d-flex gap-2 action-btns"
                >
                  <button
                    class="btn-icon"
                    @click="startEdit(review)"
                    title="Edit"
                    aria-label="Edit review"
                  >
                    <i class="bi bi-pencil-fill"></i>
                  </button>
                  <button
                    class="btn-icon btn-icon-danger"
                    @click="deleteReview(review.id)"
                    title="Delete"
                    aria-label="Delete review"
                  >
                    <i class="bi bi-trash-fill"></i>
                  </button>
                </div>
              </div>

              <hr class="gd-divider my-3" />

              <p
                class="text-light"
                style="
                  line-height: 1.7;
                  white-space: pre-wrap;
                  font-size: 0.95rem;
                "
              >
                {{ review.comment }}
              </p>

              <div class="d-flex gap-2 mt-4">
                <button
                  class="btn-vote"
                  :class="{ active: review.likes?.includes(currentUser?.uid) }"
                  @click="toggleVote(review.id, 'like')"
                >
                  <i
                    :class="
                      review.likes?.includes(currentUser?.uid)
                        ? 'bi bi-hand-thumbs-up-fill'
                        : 'bi bi-hand-thumbs-up'
                    "
                  ></i>
                  <span>{{ review.likes?.length || 0 }}</span>
                </button>
                <button
                  class="btn-vote"
                  :class="{
                    active: review.dislikes?.includes(currentUser?.uid),
                  }"
                  @click="toggleVote(review.id, 'dislike')"
                >
                  <i
                    :class="
                      review.dislikes?.includes(currentUser?.uid)
                        ? 'bi bi-hand-thumbs-down-fill'
                        : 'bi bi-hand-thumbs-down'
                    "
                  ></i>
                  <span>{{ review.dislikes?.length || 0 }}</span>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* Glassmorphism General */
.gd-glass-card {
  background: var(--bg-glass);
  border: 1px solid var(--border-glass);
  border-radius: 16px;
  backdrop-filter: blur(12px);
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.15);
}

.gd-title-sm {
  font-weight: 800;
  letter-spacing: -0.02em;
}

/* Average Rating Colors */
.rating-excellent {
  color: #22c55e;
} /* Green */
.rating-good {
  color: #3b82f6;
} /* Blue */
.rating-mixed {
  color: #eab308;
} /* Yellow */
.rating-poor {
  color: #ef4444;
} /* Red */

/* Dropdown */
.gd-glass-select {
  background: var(--overlay-medium);
  border: 1px solid var(--border-glass);
  color: var(--text-primary);
  border-radius: 99px;
  padding: 8px 18px;
  outline: none;
  font-size: 0.85rem;
  font-weight: 600;
  transition: all 0.3s ease;
  backdrop-filter: blur(10px);
  cursor: pointer;
}
.gd-glass-select:focus,
.gd-glass-select:hover {
  border-color: #7c3aed;
  box-shadow: 0 0 15px rgba(124, 58, 237, 0.25);
  background: var(--overlay-heavy);
}
.gd-glass-select option {
  background: #1e1e24;
  color: white;
}

/* Buttons */
.gd-btn-primary {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  background: linear-gradient(135deg, #7c3aed, #4aa3ff);
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 12px;
  font-weight: 700;
  text-decoration: none;
  transition:
    transform 0.2s ease,
    box-shadow 0.2s ease,
    filter 0.2s ease;
}
.gd-btn-primary:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(124, 58, 237, 0.4);
  filter: brightness(1.1);
  color: white;
}
.gd-btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.gd-btn-secondary {
  background: var(--overlay-medium);
  color: var(--text-primary);
  border: 1px solid var(--border-subtle);
  padding: 12px 24px;
  border-radius: 12px;
  font-weight: 700;
  transition: all 0.2s;
}
.gd-btn-secondary:hover {
  background: var(--overlay-heavy);
  border-color: var(--border-glass);
}

/* Form Elements */
.gd-review-input {
  width: 100%;
  background: var(--overlay-light);
  border: 1px solid var(--border-glass);
  color: var(--text-primary);
  border-radius: 12px;
  padding: 16px;
  resize: vertical;
  transition: all 0.3s ease;
  font-size: 0.95rem;
}
.gd-review-input:focus {
  outline: none;
  border-color: #7c3aed;
  background: var(--overlay-medium);
  box-shadow: 0 0 0 3px rgba(124, 58, 237, 0.15);
}

.letter-spacing-1 {
  letter-spacing: 0.05em;
}

.star-rating {
  font-size: 1.5rem;
  cursor: pointer;
}
.star-rating .star {
  transition: transform 0.2s cubic-bezier(0.34, 1.56, 0.64, 1);
  display: inline-block;
}
.star-rating .star:hover {
  transform: scale(1.2);
}

/* Avatar */
.review-avatar {
  width: 54px;
  height: 54px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: 800;
  font-size: 1.5rem;
  flex-shrink: 0;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
  border: 2px solid rgba(255, 255, 255, 0.1);
}

/* Badges */
.gd-badge-reviewer {
  background: rgba(124, 58, 237, 0.15);
  color: #c4b5fd;
  border: 1px solid rgba(124, 58, 237, 0.3);
  padding: 4px 10px;
  border-radius: 20px;
  font-size: 0.7rem;
  font-weight: 700;
  letter-spacing: 0.03em;
  text-transform: uppercase;
  display: inline-flex;
  align-items: center;
  gap: 4px;
}

.gd-divider {
  border-color: var(--border-subtle);
  opacity: 0.5;
}

/* Icon Buttons (Edit/Delete) */
.btn-icon {
  background: transparent;
  border: none;
  color: var(--text-muted);
  width: 36px;
  height: 36px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
}
.btn-icon:hover {
  background: rgba(124, 58, 237, 0.15);
  color: #a78bfa;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(124, 58, 237, 0.2);
}
.btn-icon-danger:hover {
  background: rgba(239, 68, 68, 0.15);
  color: #f87171;
  box-shadow: 0 4px 12px rgba(239, 68, 68, 0.2);
}

/* Vote Buttons */
.btn-vote {
  background: var(--overlay-medium);
  border: 1px solid var(--border-glass);
  color: var(--text-muted);
  padding: 6px 14px;
  border-radius: 20px;
  font-size: 0.85rem;
  font-weight: 600;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  transition: all 0.2s ease;
}
.btn-vote:hover {
  background: var(--overlay-heavy);
  color: var(--text-primary);
  border-color: var(--border-subtle);
}
.btn-vote.active {
  background: rgba(124, 58, 237, 0.2);
  border-color: #7c3aed;
  color: #c4b5fd;
}
.btn-vote.active i {
  color: #a78bfa;
}

/* Animations */
.staggered-review-card {
  opacity: 0;
  transform: translateY(20px);
  animation: fadeSlideUp 0.6s cubic-bezier(0.16, 1, 0.3, 1) forwards;
}

@keyframes fadeSlideUp {
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.gd-review-card-body {
  padding: 30px;
}

.login-prompt-box,
.empty-state-box {
  animation: fadeSlideUp 0.6s cubic-bezier(0.16, 1, 0.3, 1) forwards;
}
</style>
