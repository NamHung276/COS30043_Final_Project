<script>
import { auth, db } from "../firebase";
import { onAuthStateChanged } from "firebase/auth";
import { doc, getDoc, updateDoc } from "firebase/firestore";

export default {
  data() {
    return {
      currentUser: null,
      articleId: null,
      title: "",
      category: "General",
      content: "",
      image: "",
      submitting: false,
      loading: true,
      error: "",
      touched: {
        title: false,
        content: false,
      },
    };
  },

  computed: {
    titleError() {
      if (!this.touched.title) return "";
      if (!this.title.trim()) return "Title is required.";
      if (this.title.trim().length < 5)
        return "Title must be at least 5 characters.";
      return "";
    },

    contentError() {
      if (!this.touched.content) return "";
      if (!this.content.trim()) return "Content is required.";
      if (this.content.trim().length < 20)
        return "Content must be at least 20 characters.";
      return "";
    },

    isFormValid() {
      return this.title.trim().length >= 5 && this.content.trim().length >= 20;
    },
  },

  methods: {
    touch(field) {
      this.touched[field] = true;
    },

    async loadArticle() {
      this.articleId = this.$route.params.id;
      try {
        const docRef = doc(db, "news", this.articleId);
        const docSnap = await getDoc(docRef);
        
        if (docSnap.exists()) {
          const data = docSnap.data();
          
          // Only allow author or admin to edit
          if (this.currentUser && (this.currentUser.uid === data.userId || this.currentUser.role === 'admin')) {
            this.title = data.title;
            this.category = data.category;
            this.content = data.content;
            this.image = data.image && !data.image.includes('placehold.co') ? data.image : '';
          } else {
            this.$router.push("/gamehub-news");
          }
        } else {
          this.error = "Article not found.";
        }
      } catch (err) {
        console.error("Error loading article:", err);
        this.error = "Failed to load article.";
      } finally {
        this.loading = false;
      }
    },

    async saveArticle() {
      this.touched.title = true;
      this.touched.content = true;
      this.error = "";

      if (!this.isFormValid) return;

      if (!this.currentUser) {
        this.$router.push("/login");
        return;
      }

      this.submitting = true;

      try {
        await updateDoc(doc(db, "news", this.articleId), {
          title: this.title.trim(),
          category: this.category,
          content: this.content.trim(),
          image:
            this.image.trim() ||
            "https://placehold.co/600x400?text=" +
              encodeURIComponent(this.category),
        });

        this.$router.push(`/gamehub-news/${this.articleId}`);
      } catch (error) {
        console.error("Failed to update article:", error);
        this.error = "Something went wrong. Please try again.";
      } finally {
        this.submitting = false;
      }
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
      if (user) {
        this.loadArticle();
      }
    });
  },
};
</script>

<template>
  <div class="container py-4">
    <div class="section-header">
      <span class="section-icon"><i class="bi bi-pencil-square"></i></span>
      <h1 class="mb-0">Edit News Article</h1>
    </div>

    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-primary" role="status"></div>
    </div>
    
    <div v-else class="row g-4">
      <!-- Form -->
      <div class="col-md-7">
        <div class="card auth-card">
          <div class="card-body text-start p-4">
            <div v-if="error" class="alert alert-danger">
              {{ error }}
            </div>

            <div class="mb-3">
              <label for="title" class="form-label">
                <i class="bi bi-type me-1"></i>Title
              </label>
              <input
                id="title"
                v-model="title"
                type="text"
                class="form-control"
                :class="{ 'is-invalid': titleError }"
                placeholder="Article title"
                @blur="touch('title')"
              />
              <div v-if="titleError" class="invalid-feedback">
                {{ titleError }}
              </div>
            </div>

            <div class="mb-3">
              <label for="category" class="form-label">
                <i class="bi bi-tags me-1"></i>Category
              </label>
              <select id="category" v-model="category" class="form-select">
                <option>General</option>
                <option>FPS</option>
                <option>MOBA</option>
                <option>RPG</option>
                <option>MMO</option>
                <option>Battle Royale</option>
                <option>Strategy</option>
                <option>Action</option>
              </select>
            </div>

            <div class="mb-3">
              <label for="image" class="form-label">
                <i class="bi bi-image me-1"></i>Image URL (optional)
              </label>
              <input
                id="image"
                v-model="image"
                type="text"
                class="form-control"
                placeholder="https://..."
              />
              <small class="text-muted">
                Leave blank to use a placeholder image
              </small>
            </div>

            <div class="mb-4">
              <label for="content" class="form-label">
                <i class="bi bi-file-text me-1"></i>Content
              </label>
              <textarea
                id="content"
                v-model="content"
                class="form-control"
                :class="{ 'is-invalid': contentError }"
                rows="6"
                placeholder="Write your article..."
                @blur="touch('content')"
              ></textarea>
              <div v-if="contentError" class="invalid-feedback">
                {{ contentError }}
              </div>
              <small class="text-muted">
                {{ content.length }} characters
              </small>
            </div>

            <div class="d-flex gap-2">
              <button
                class="btn btn-primary"
                :disabled="submitting"
                @click="saveArticle"
              >
                <template v-if="submitting">Saving...</template>
                <template v-else
                  ><i class="bi bi-save me-1"></i>Save Changes</template
                >
              </button>

              <router-link :to="`/gamehub-news/${articleId}`" class="btn btn-outline-secondary">
                Cancel
              </router-link>
            </div>
          </div>
        </div>
      </div>

      <!-- Live Preview -->
      <div class="col-md-5">
        <div class="card sticky-top" style="top: 80px">
          <div class="card-body text-start">
            <h6 class="text-muted mb-3">
              <i class="bi bi-eye me-1"></i>Live Preview
            </h6>

            <div
              v-if="title || content"
              class="card"
              style="border: 1px solid var(--border-subtle)"
            >
              <div
                v-if="image || category"
                style="
                  height: 160px;
                  overflow: hidden;
                  border-radius: var(--radius-md) var(--radius-md) 0 0;
                "
              >
                <img
                  :src="image || `https://placehold.co/600x400?text=${encodeURIComponent(category)}`"
                  alt="Preview"
                  style="width: 100%; height: 100%; object-fit: cover"
                  @error="$event.target.src = 'https://placehold.co/600x400?text=Error'"
                />
              </div>
              <div class="card-body" style="padding: 14px">
                <span class="badge bg-primary mb-2">{{ category }}</span>
                <h6>{{ title || "Untitled" }}</h6>
                <p class="text-muted small mb-0">
                  {{
                    content
                      ? content.substring(0, 100) +
                        (content.length > 100 ? "..." : "")
                      : "No content yet..."
                  }}
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
