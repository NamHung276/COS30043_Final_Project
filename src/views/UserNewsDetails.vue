<script>
import { inject } from "vue";
import { auth, db } from "../firebase";
import { onAuthStateChanged } from "firebase/auth";
import { doc, getDoc, updateDoc, deleteDoc } from "firebase/firestore";
import LikeButton from "../components/LikeButton.vue";

export default {
  components: { LikeButton },

  setup() {
    const toast = inject("toast");
    return { toast };
  },

  data() {
    return {
      article: null,
      articleId: null,
      loading: true,
      currentUser: null,
      editing: false,
      editTitle: "",
      editCategory: "",
      editContent: "",
      saving: false,
    };
  },

  computed: {
    isOwner() {
      return (
        this.currentUser &&
        this.article &&
        this.currentUser.uid === this.article.userId
      );
    },
  },

  methods: {
    async loadArticle() {
      this.loading = true;
      this.articleId = this.$route.params.id;

      const docRef = doc(db, "news", this.articleId);
      const docSnap = await getDoc(docRef);

      if (docSnap.exists()) {
        this.article = { id: docSnap.id, ...docSnap.data() };
        document.title = `${this.article.title} | GameHub`;
      } else {
        this.article = null;
      }

      this.loading = false;
    },

    startEdit() {
      this.editTitle = this.article.title;
      this.editCategory = this.article.category;
      this.editContent = this.article.content;
      this.editing = true;
    },

    cancelEdit() {
      this.editing = false;
    },

    async saveEdit() {
      if (!this.editTitle.trim() || !this.editContent.trim()) return;

      this.saving = true;

      try {
        await updateDoc(doc(db, "news", this.articleId), {
          title: this.editTitle.trim(),
          category: this.editCategory,
          content: this.editContent.trim(),
        });

        await this.loadArticle();
        this.editing = false;
        this.toast.show("Article updated successfully!", "success");
      } catch (error) {
        console.error("Failed to update article:", error);
        this.toast.show("Failed to update article.", "error");
      } finally {
        this.saving = false;
      }
    },

    async deleteArticle() {
      if (!confirm("Are you sure you want to delete this article?")) return;

      try {
        await deleteDoc(doc(db, "news", this.articleId));
        this.toast.show("Article deleted.", "info");
        this.$router.push("/gamehub-news");
      } catch (error) {
        console.error("Failed to delete article:", error);
        this.toast.show("Failed to delete article.", "error");
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
    });
    this.loadArticle();
  },
};
</script>

<template>
  <div class="container py-4">
    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
    </div>

    <div v-else-if="!article" class="alert alert-danger">
      Article not found.
    </div>

    <div v-else>
      <router-link to="/gamehub-news" class="btn btn-outline-secondary mb-3">
        ← Back to News
      </router-link>

      <!-- Edit Mode -->
      <div v-if="editing" class="card auth-card">
        <div class="card-body text-start p-4">
          <h4 class="mb-3"><i class="bi bi-pencil me-2"></i>Edit Article</h4>

          <div class="mb-3">
            <label class="form-label">Title</label>
            <input v-model="editTitle" type="text" class="form-control" />
          </div>

          <div class="mb-3">
            <label class="form-label">Category</label>
            <select v-model="editCategory" class="form-select">
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
            <label class="form-label">Content</label>
            <textarea
              v-model="editContent"
              class="form-control"
              rows="6"
            ></textarea>
          </div>

          <div class="d-flex gap-2">
            <button
              class="btn btn-success"
              :disabled="saving"
              @click="saveEdit"
            >
              <template v-if="saving">Saving...</template>
              <template v-else
                ><i class="bi bi-floppy me-1"></i>Save Changes</template
              >
            </button>
            <button class="btn btn-outline-secondary" @click="cancelEdit">
              Cancel
            </button>
          </div>
        </div>
      </div>

      <!-- Display Mode -->
      <div v-else>
        <!-- Hero Image -->
        <div class="card overflow-hidden mb-4" style="border: none">
          <div style="position: relative">
            <img
              v-lazy-img="article.image"
              :alt="article.title"
              style="width: 100%; max-height: 500px; object-fit: cover"
            />
            <div
              style="
                position: absolute;
                bottom: 0;
                left: 0;
                right: 0;
                padding: 24px 24px 20px;
                background: linear-gradient(transparent, rgba(7, 11, 20, 0.9));
              "
            >
              <div class="d-flex gap-2 mb-2">
                <span class="badge bg-secondary">
                  <i class="bi bi-person me-1"></i>Community Post
                </span>
                <span class="badge bg-primary">
                  {{ article.category }}
                </span>
              </div>
            </div>
          </div>
        </div>

        <div class="d-flex justify-content-between align-items-center mb-2">
          <h1>{{ article.title }}</h1>
          <LikeButton :article-id="article.id" />
        </div>

        <p class="text-muted">By {{ article.userName }} · {{ article.date }}</p>

        <hr style="border-color: var(--border-glass)" />

        <div class="card">
          <div class="card-body">
            <p class="fs-5" style="white-space: pre-wrap; line-height: 1.8">
              {{ article.content }}
            </p>
          </div>
        </div>

        <div v-if="isOwner" class="mt-4 d-flex gap-2">
          <button class="btn btn-outline-secondary" @click="startEdit">
            <i class="bi bi-pencil me-1"></i>Edit
          </button>
          <button class="btn btn-outline-danger" @click="deleteArticle">
            <i class="bi bi-trash me-1"></i>Delete
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
