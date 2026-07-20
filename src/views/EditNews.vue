<script>
import { auth, db, storage } from "../firebase";
import { onAuthStateChanged } from "firebase/auth";
import { doc, getDoc, updateDoc } from "firebase/firestore";
import { ref as storageRef, uploadBytes, getDownloadURL } from "firebase/storage";
import { MdEditor, MdPreview } from 'md-editor-v3';
import 'md-editor-v3/lib/style.css';
import 'md-editor-v3/lib/preview.css';

export default {
  components: { MdEditor, MdPreview },
  data() {
    return {
      currentUser: null,
      articleId: null,
      title: "",
      subtitle: "",
      category: "",
      tags: [],
      tagInput: "",
      content: "",
      image: "",
      coverImageFile: null,
      imageMode: "upload",
      submitting: false,
      loading: true,
      error: "",
      saveStatus: "✓ Saved",
      saveTimeout: null,
      editorToolbars: [
        'bold', 'italic', 'underline', '-',
        'h1', 'h2', 'h3', '-',
        'quote', 'code', '-',
        'link', 'image', 'table', '-',
        'revoke', 'next'
      ]
    };
  },
  computed: {
    isFormValid() {
      return this.title.trim().length >= 5 && this.content.trim().length >= 20 && this.category !== "";
    },
    wordCount() {
      if (!this.content) return 0;
      return this.content.trim().split(/\s+/).filter(w => w.length > 0).length;
    },
    charCount() {
      return this.content.length;
    },
    readingTime() {
      return Math.max(1, Math.ceil(this.wordCount / 200));
    },
    formattedDate() {
      return new Date().toLocaleDateString("en-AU", {
        year: "numeric",
        month: "long",
        day: "numeric",
      });
    }
  },
  watch: {
    title: 'triggerAutosave',
    subtitle: 'triggerAutosave',
    content: 'triggerAutosave',
    category: 'triggerAutosave',
    tags: {
      handler: 'triggerAutosave',
      deep: true
    },
    image: 'triggerAutosave'
  },
  methods: {
    async loadArticle() {
      this.articleId = this.$route.params.id;
      try {
        const docRef = doc(db, "news", this.articleId);
        const docSnap = await getDoc(docRef);
        
        if (docSnap.exists()) {
          const data = docSnap.data();
          
          if (this.currentUser && (this.currentUser.uid === data.userId || this.currentUser.role === 'admin')) {
            this.title = data.title || "";
            this.subtitle = data.subtitle || "";
            this.category = data.category || "";
            this.tags = data.tags || [];
            this.content = data.content || "";
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
        if (this.image) this.imageMode = 'url';
      }
    },
    triggerAutosave() {
      if (this.loading) return; // Don't trigger autosave during initial load
      this.saveStatus = "Saving...";
      if (this.saveTimeout) clearTimeout(this.saveTimeout);
      this.saveTimeout = setTimeout(() => {
        this.saveStatus = "✓ Saved";
      }, 1000);
    },
    addTag(e) {
      const val = this.tagInput.trim();
      if (val && !this.tags.includes(val)) {
        this.tags.push(val);
      }
      this.tagInput = "";
    },
    removeTag(index) {
      this.tags.splice(index, 1);
    },
    removeCover() {
      this.image = "";
      this.coverImageFile = null;
      this.imageMode = "upload";
    },
    handleCoverUpload(e) {
      const file = e.target.files[0];
      if (!file) return;
      this.coverImageFile = file;
      this.image = URL.createObjectURL(file);
    },
    async uploadImageToFirebase(file) {
      const uniqueName = `${Date.now()}_${file.name}`;
      const imgRef = storageRef(storage, `news_images/${uniqueName}`);
      await uploadBytes(imgRef, file);
      return await getDownloadURL(imgRef);
    },
    async onUploadImg(files, callback) {
      try {
        const res = await Promise.all(
          files.map((file) => this.uploadImageToFirebase(file))
        );
        callback(res.map((url) => ({ url, alt: "news image" })));
      } catch (err) {
        console.error("Failed to upload inline images:", err);
      }
    },
    async submitArticle() {
      this.error = "";
      if (!this.isFormValid) {
        this.error = "Please provide a valid headline, category, and content.";
        return;
      }
      if (!this.currentUser) {
        this.$router.push("/login");
        return;
      }

      this.submitting = true;

      try {
        let finalImageUrl = this.image;
        if (this.coverImageFile) {
          finalImageUrl = await this.uploadImageToFirebase(this.coverImageFile);
        }

        await updateDoc(doc(db, "news", this.articleId), {
          title: this.title.trim(),
          subtitle: this.subtitle.trim(),
          category: this.category,
          tags: this.tags,
          content: this.content.trim(),
          image: finalImageUrl,
          readingTime: this.readingTime,
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
  <div class="newsroom-editor-wrapper">
    <div class="newsroom-header">
      <div class="container-fluid px-4 d-flex justify-content-between align-items-center py-3">
        <div class="d-flex align-items-center gap-3">
          <router-link :to="`/gamehub-news/${articleId}`" class="btn btn-outline-secondary btn-sm px-3 rounded-pill text-decoration-none">
            <i class="bi bi-arrow-left me-1"></i> Back
          </router-link>
          <span class="text-muted small fw-bold" :class="{'text-success': saveStatus === '✓ Saved'}">{{ saveStatus }}</span>
        </div>
        
        <div class="d-flex align-items-center gap-3">
          <button class="btn btn-primary btn-sm px-4 rounded-pill fw-bold" :disabled="submitting || !isFormValid" @click="submitArticle">
            <template v-if="submitting">Saving...</template>
            <template v-else>Save Changes <i class="bi bi-send-fill ms-1"></i></template>
          </button>
        </div>
      </div>
    </div>

    <div v-if="loading" class="text-center py-5 d-flex flex-grow-1 align-items-center justify-content-center">
      <div class="spinner-border text-primary" role="status"></div>
    </div>

    <div v-else class="editor-grid">
      <!-- Editor Column (60%) -->
      <div class="editor-column">
        <div class="p-4">
          <div v-if="error" class="alert alert-danger">{{ error }}</div>

          <div class="mb-4">
            <input v-model="title" type="text" class="newsroom-headline-input" placeholder="Write a catchy headline..." />
            <input v-model="subtitle" type="text" class="newsroom-subtitle-input" placeholder="Add a brief subtitle or excerpt..." />
            
            <div class="row mt-4 g-4 align-items-start">
              <div class="col-md-7">
                <label class="form-label text-muted small fw-bold text-uppercase tracking-wider">Cover Image</label>
                <div class="cover-image-uploader">
                  <div class="image-mode-toggle mb-3" v-if="!image">
                    <button class="toggle-btn" :class="{ active: imageMode === 'upload' }" @click="imageMode = 'upload'">Upload File</button>
                    <button class="toggle-btn" :class="{ active: imageMode === 'url' }" @click="imageMode = 'url'">Image Link</button>
                  </div>

                  <!-- When there is an image -->
                  <div v-if="image" class="cover-preview-wrapper position-relative">
                    <img :src="image" alt="Cover" class="cover-preview-img" />
                    <button class="btn btn-sm btn-dark position-absolute top-0 end-0 m-2 rounded-circle shadow" @click="removeCover" title="Remove image">
                      <i class="bi bi-x-lg"></i>
                    </button>
                  </div>

                  <!-- Upload Mode -->
                  <div v-else-if="imageMode === 'upload'" class="upload-zone position-relative text-center p-4 border border-secondary border-dashed rounded upload-zone-hover">
                    <i class="bi bi-cloud-arrow-up display-6 text-muted mb-2"></i>
                    <p class="text-muted mb-0">Click or drag image here</p>
                    <input type="file" class="position-absolute top-0 start-0 w-100 h-100 opacity-0 cursor-pointer" accept="image/*" @change="handleCoverUpload" />
                  </div>

                  <!-- URL Mode -->
                  <div v-else class="url-zone">
                    <div class="input-group">
                      <span class="input-group-text bg-dark border-secondary"><i class="bi bi-link-45deg text-muted"></i></span>
                      <input v-model="image" type="text" class="form-control bg-dark border-secondary text-light" placeholder="Paste image URL..." />
                    </div>
                  </div>
                </div>
              </div>
              
              <div class="col-md-5">
                <div class="row g-3">
                  <div class="col-12">
                    <label class="form-label text-muted small fw-bold text-uppercase tracking-wider">Category</label>
                    <select v-model="category" class="form-select bg-dark border-secondary text-light">
                      <option value="" disabled>Choose Category ▼</option>
                      <option>General</option>
                      <option>FPS</option>
                      <option>MOBA</option>
                      <option>RPG</option>
                      <option>MMO</option>
                      <option>Battle Royale</option>
                      <option>Strategy</option>
                      <option>Action</option>
                      <option>Esports</option>
                    </select>
                  </div>
                  <div class="col-12">
                    <label class="form-label text-muted small fw-bold text-uppercase tracking-wider">Tags</label>
                    <div class="tags-container border border-secondary rounded p-2 bg-dark d-flex flex-wrap gap-2 align-items-center">
                      <span v-for="(tag, index) in tags" :key="index" class="badge bg-primary rounded-pill d-flex align-items-center gap-1 py-2 px-3">
                        {{ tag }}
                        <i class="bi bi-x cursor-pointer ms-1 fs-6 lh-1" @click="removeTag(index)"></i>
                      </span>
                      <input 
                        v-model="tagInput" 
                        @keydown.enter.prevent="addTag" 
                        @keydown.comma.prevent="addTag"
                        type="text" 
                        class="tag-input-borderless flex-grow-1" 
                        placeholder="Add tag..." 
                      />
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div class="newsroom-editor-container shadow-sm border border-secondary rounded overflow-hidden">
            <MdEditor 
              v-model="content" 
              theme="dark" 
              language="en-US" 
              @onUploadImg="onUploadImg" 
              :preview="false" 
              :toolbars="editorToolbars"
              :footers="[]"
            />
          </div>
          
          <div class="d-flex justify-content-end align-items-center py-2 text-muted small gap-3 mt-1">
            <span>{{ wordCount }} Words</span>
            <span>{{ charCount }} Characters</span>
            <span><i class="bi bi-clock me-1"></i> {{ readingTime }} min read</span>
          </div>
        </div>
      </div>

      <!-- Preview Column (40%) -->
      <div class="preview-column bg-preview p-4 custom-scrollbar">
        <h6 class="text-uppercase tracking-wider text-muted small fw-bold mb-4 d-flex align-items-center">
          <i class="bi bi-eye-fill me-2"></i> Live Preview
        </h6>
        
        <div class="live-preview-content">
          <!-- Placeholder Hero -->
          <div v-if="!image" class="preview-hero-placeholder mb-4 d-flex flex-column align-items-center justify-content-center text-muted">
            <i class="bi bi-image display-4 mb-2 opacity-50"></i>
            <span class="fw-bold">No Cover Image</span>
            <span class="small opacity-75">1920×1080 recommended</span>
          </div>
          <!-- Real Hero -->
          <div v-else class="preview-hero mb-4">
            <img :src="image" alt="Cover" class="w-100 rounded-3" style="aspect-ratio: 16/9; object-fit: cover;" />
          </div>

          <!-- Metadata -->
          <div class="preview-meta d-flex align-items-center flex-wrap gap-3 mb-3 text-muted small">
            <span v-if="category" class="badge bg-primary px-2 py-1 rounded-pill">{{ category }}</span>
            <span class="d-flex align-items-center"><i class="bi bi-person-circle me-2 fs-6"></i> {{ currentUser?.displayName || currentUser?.email || 'Author Name' }}</span>
            <span class="d-flex align-items-center"><i class="bi bi-calendar3 me-2"></i> {{ formattedDate }}</span>
            <span class="d-flex align-items-center"><i class="bi bi-clock me-2"></i> {{ readingTime }} min read</span>
          </div>

          <!-- Title -->
          <h1 class="preview-title text-light fw-bold mb-2">{{ title || 'Untitled Article' }}</h1>
          
          <!-- Subtitle -->
          <h2 v-if="subtitle" class="preview-subtitle text-muted fw-normal fs-5 mb-3">{{ subtitle }}</h2>

          <!-- Tags -->
          <div v-if="tags.length" class="mb-4 d-flex gap-2 flex-wrap">
            <span v-for="tag in tags" :key="tag" class="badge bg-secondary bg-opacity-25 text-light rounded-pill px-3 py-2 fw-normal border border-secondary border-opacity-50">#{{ tag }}</span>
          </div>

          <hr class="border-secondary opacity-25 mb-4" />

          <!-- Body -->
          <div class="preview-body">
            <MdPreview :modelValue="content" theme="dark" language="en-US" class="news-markdown-preview" />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.newsroom-editor-wrapper {
  height: calc(100vh - 70px);
  background: var(--bg-deep);
  display: flex;
  flex-direction: column;
}
.newsroom-header {
  background: var(--bg-base);
  border-bottom: 1px solid var(--border-subtle);
  flex-shrink: 0;
  z-index: 100;
}
.editor-grid {
  display: grid;
  grid-template-columns: 60% 40%;
  flex-grow: 1;
  overflow: hidden;
}
.editor-column {
  overflow-y: auto;
  background: var(--bg-deep);
}
.preview-column {
  overflow-y: auto;
  border-left: 1px solid var(--border-subtle);
}
.bg-preview {
  background-color: #141922;
}

.newsroom-headline-input {
  width: 100%;
  background: transparent;
  border: none;
  font-size: 2.5rem;
  font-weight: 800;
  color: var(--text-main);
  outline: none;
  margin-bottom: 8px;
}
.newsroom-headline-input::placeholder {
  color: var(--text-muted);
  opacity: 0.5;
}
.newsroom-subtitle-input {
  width: 100%;
  background: transparent;
  border: none;
  font-size: 1.2rem;
  font-weight: 400;
  color: var(--text-secondary);
  outline: none;
}
.newsroom-subtitle-input::placeholder {
  color: var(--text-muted);
  opacity: 0.5;
}

.tracking-wider { letter-spacing: 0.05em; }
.cursor-pointer { cursor: pointer; }
.border-dashed { border-style: dashed !important; border-color: rgba(255,255,255,0.2) !important; }
.upload-zone-hover { transition: background 0.2s, border-color 0.2s; }
.upload-zone-hover:hover { background: rgba(255,255,255,0.02); border-color: var(--primary) !important; }
.image-mode-toggle { display: flex; gap: 4px; background: rgba(0,0,0,0.3); padding: 4px; border-radius: 8px; width: fit-content; }
.toggle-btn { background: transparent; border: none; color: var(--text-muted); padding: 6px 14px; border-radius: 6px; font-size: 0.85rem; font-weight: 500; transition: 0.2s; }
.toggle-btn.active { background: var(--bg-surface); color: var(--text-main); box-shadow: 0 2px 4px rgba(0,0,0,0.2); }
.cover-preview-img {
  width: 100%;
  height: 200px;
  object-fit: cover;
  border-radius: 12px;
  border: 1px solid var(--border-glass);
}
.tag-input-borderless {
  background: transparent;
  border: none;
  color: var(--text-main);
  outline: none;
  min-width: 100px;
}

.newsroom-editor-container {
  min-height: 500px;
}
:deep(.md-editor) {
  height: calc(100vh - 480px);
  min-height: 500px;
}

/* Custom Scrollbar */
.custom-scrollbar::-webkit-scrollbar {
  width: 8px;
}
.custom-scrollbar::-webkit-scrollbar-track {
  background: rgba(0,0,0,0.1);
}
.custom-scrollbar::-webkit-scrollbar-thumb {
  background: rgba(255,255,255,0.1);
  border-radius: 4px;
}
.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background: rgba(255,255,255,0.2);
}

/* Custom Preview Styles exactly matching GameHubNewsDetails */
.preview-hero-placeholder {
  width: 100%;
  aspect-ratio: 16/9;
  background: rgba(255,255,255,0.02);
  border: 1px dashed rgba(255,255,255,0.1);
  border-radius: 12px;
}
.preview-title {
  font-size: 2.2rem;
  line-height: 1.2;
}

.news-markdown-preview {
  background: transparent !important;
  color: var(--text-secondary);
}
:deep(.md-editor-preview) {
  font-size: 1.0625rem;
  line-height: 1.9;
  word-break: break-word;
}
:deep(.md-editor-preview h1), :deep(.md-editor-preview h2), :deep(.md-editor-preview h3) {
  color: var(--text-primary);
  margin-top: 1.5em;
  margin-bottom: 0.5em;
}
:deep(.md-editor-preview img) {
  border-radius: 8px;
  max-width: 100%;
}
:deep(.md-editor-preview > p:first-of-type::first-letter) {
  font-size: 3.5rem;
  font-weight: 900;
  float: left;
  margin-right: 8px;
  line-height: 0.8;
  color: var(--text-primary);
  background: var(--gradient-primary);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  font-family: var(--font-display, sans-serif);
}
</style>
