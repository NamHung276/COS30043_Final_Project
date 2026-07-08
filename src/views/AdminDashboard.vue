// src/views/AdminDashboard.vue
<script>
import { auth, db } from '../firebase'
import { onAuthStateChanged } from 'firebase/auth'
import {
  collection, getDocs, doc, getDoc,
  updateDoc, deleteDoc, orderBy, query
} from 'firebase/firestore'

export default {
  name: 'AdminDashboard',

  inject: ['toast'],

  data() {
    return {
      activeTab: 'overview',
      currentUser: null,
      isAdmin: false,

      // Data
      users: [],
      posts: [],

      // Loading states
      loadingUsers: true,
      loadingPosts: true,

      // Confirmation modal
      confirmDelete: null, // { id, title }
      confirmRole: null,   // { uid, displayName, newRole }

      unsubscribe: null
    }
  },

  computed: {
    totalUsers() { return this.users.length },
    totalPosts() { return this.posts.length },
    adminCount() { return this.users.filter(u => u.role === 'admin').length },

    recentPosts() {
      return [...this.posts]
        .sort((a, b) => (b.createdAt?.seconds || 0) - (a.createdAt?.seconds || 0))
        .slice(0, 5)
    },

    recentUsers() {
      return [...this.users]
        .sort((a, b) => (b.createdAt?.seconds || 0) - (a.createdAt?.seconds || 0))
        .slice(0, 5)
    }
  },

  async mounted() {
    this.unsubscribe = onAuthStateChanged(auth, async (user) => {
      if (!user) {
        this.$router.push('/login')
        return
      }
      this.currentUser = user

      // Verify admin
      const snap = await getDoc(doc(db, 'users', user.uid))
      if (!snap.exists() || snap.data().role !== 'admin') {
        this.$router.push('/')
        return
      }
      this.isAdmin = true

      // Load data
      this.loadUsers()
      this.loadPosts()
    })
  },

  beforeUnmount() {
    if (this.unsubscribe) this.unsubscribe()
  },

  methods: {
    async loadUsers() {
      this.loadingUsers = true
      try {
        const q = query(collection(db, 'users'), orderBy('createdAt', 'desc'))
        const snap = await getDocs(q)
        this.users = snap.docs.map(d => ({ uid: d.id, ...d.data() }))
      } catch (e) {
        console.error(e)
        this.toast.show('Failed to load users.', 'error')
      } finally {
        this.loadingUsers = false
      }
    },

    async loadPosts() {
      this.loadingPosts = true
      try {
        const q = query(collection(db, 'news'), orderBy('createdAt', 'desc'))
        const snap = await getDocs(q)
        this.posts = snap.docs.map(d => ({ id: d.id, ...d.data() }))
      } catch (e) {
        console.error(e)
        this.toast.show('Failed to load posts.', 'error')
      } finally {
        this.loadingPosts = false
      }
    },

    askDeletePost(post) {
      this.confirmDelete = { id: post.id, title: post.title }
    },

    async confirmDeletePost() {
      if (!this.confirmDelete) return
      try {
        await deleteDoc(doc(db, 'news', this.confirmDelete.id))
        this.posts = this.posts.filter(p => p.id !== this.confirmDelete.id)
        this.toast.show('Post deleted successfully.', 'success')
      } catch (e) {
        console.error(e)
        this.toast.show('Failed to delete post.', 'error')
      } finally {
        this.confirmDelete = null
      }
    },

    askChangeRole(user) {
      this.confirmRole = {
        uid: user.uid,
        displayName: user.displayName || user.email,
        newRole: user.role === 'admin' ? 'user' : 'admin'
      }
    },

    async confirmChangeRole() {
      if (!this.confirmRole) return
      try {
        await updateDoc(doc(db, 'users', this.confirmRole.uid), {
          role: this.confirmRole.newRole
        })
        const u = this.users.find(u => u.uid === this.confirmRole.uid)
        if (u) u.role = this.confirmRole.newRole
        this.toast.show(
          `${this.confirmRole.displayName} is now ${this.confirmRole.newRole === 'admin' ? 'an Admin' : 'a regular User'}.`,
          'success'
        )
      } catch (e) {
        console.error(e)
        this.toast.show('Failed to update role.', 'error')
      } finally {
        this.confirmRole = null
      }
    },

    formatDate(ts) {
      if (!ts?.seconds) return '—'
      return new Date(ts.seconds * 1000).toLocaleDateString('en-AU', {
        year: 'numeric', month: 'short', day: 'numeric'
      })
    }
  }
}
</script>

<template>
  <div class="container py-4" v-if="isAdmin">

    <!-- Page Header -->
    <div class="admin-header mb-4">
      <div class="d-flex align-items-center gap-3 flex-wrap">
        <div class="admin-header-icon"><i class="bi bi-shield-fill"></i></div>
        <div>
          <h1 class="mb-0" style="font-size: 1.8rem;">Admin Dashboard</h1>
          <p class="text-muted mb-0" style="font-size: 0.88rem;">
            Logged in as <strong>{{ currentUser?.email }}</strong>
          </p>
        </div>
      </div>
    </div>

    <!-- Tabs -->
    <div class="admin-tabs mb-4">
      <button
        class="admin-tab-btn"
        :class="{ active: activeTab === 'overview' }"
        @click="activeTab = 'overview'"
        id="tab-overview"
      >
        <i class="bi bi-bar-chart me-1"></i>Overview
      </button>
      <button
        class="admin-tab-btn"
        :class="{ active: activeTab === 'users' }"
        @click="activeTab = 'users'"
        id="tab-users"
      >
        <i class="bi bi-people me-1"></i>Users
        <span v-if="totalUsers > 0" class="admin-tab-count">{{ totalUsers }}</span>
      </button>
      <button
        class="admin-tab-btn"
        :class="{ active: activeTab === 'content' }"
        @click="activeTab = 'content'"
        id="tab-content"
      >
        <i class="bi bi-newspaper me-1"></i>Content
        <span v-if="totalPosts > 0" class="admin-tab-count">{{ totalPosts }}</span>
      </button>
    </div>

    <!-- ══════════════════════════
         TAB: OVERVIEW
         ══════════════════════════ -->
    <div v-if="activeTab === 'overview'">

      <!-- Stat Cards -->
      <div class="row g-4 mb-5">
        <div class="col-6 col-md-3">
          <div class="card admin-stat-card" style="--stat-accent: #3b82f6;">
            <div class="admin-stat-icon" style="background: rgba(59,130,246,0.15); color: #60a5fa;"><i class="bi bi-people"></i></div>
            <div class="admin-stat-number" style="background: linear-gradient(135deg, #3b82f6, #60a5fa); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;">
              <span v-if="loadingUsers" class="admin-stat-skeleton"></span>
              <template v-else>{{ totalUsers }}</template>
            </div>
            <div class="admin-stat-label">Registered Users</div>
          </div>
        </div>
        <div class="col-6 col-md-3">
          <div class="card admin-stat-card" style="--stat-accent: #8b5cf6;">
            <div class="admin-stat-icon" style="background: rgba(139,92,246,0.15); color: #a78bfa;"><i class="bi bi-newspaper"></i></div>
            <div class="admin-stat-number" style="background: linear-gradient(135deg, #8b5cf6, #a78bfa); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;">
              <span v-if="loadingPosts" class="admin-stat-skeleton"></span>
              <template v-else>{{ totalPosts }}</template>
            </div>
            <div class="admin-stat-label">Community Posts</div>
          </div>
        </div>
        <div class="col-6 col-md-3">
          <div class="card admin-stat-card" style="--stat-accent: #f59e0b;">
            <div class="admin-stat-icon" style="background: rgba(245,158,11,0.15); color: #fcd34d;"><i class="bi bi-shield-fill"></i></div>
            <div class="admin-stat-number" style="background: linear-gradient(135deg, #f59e0b, #fcd34d); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;">
              <span v-if="loadingUsers" class="admin-stat-skeleton"></span>
              <template v-else>{{ adminCount }}</template>
            </div>
            <div class="admin-stat-label">Admin Accounts</div>
          </div>
        </div>
        <div class="col-6 col-md-3">
          <div class="card admin-stat-card" style="--stat-accent: #22c55e;">
            <div class="admin-stat-icon" style="background: rgba(34,197,94,0.15); color: #86efac;"><i class="bi bi-check-circle-fill"></i></div>
            <div class="admin-stat-number" style="background: linear-gradient(135deg, #22c55e, #86efac); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;">
              <span v-if="loadingUsers" class="admin-stat-skeleton"></span>
              <template v-else>{{ totalUsers - adminCount }}</template>
            </div>
            <div class="admin-stat-label">Regular Users</div>
          </div>
        </div>
      </div>

      <!-- Recent Activity -->
      <div class="row g-4">

        <!-- Recent Users -->
        <div class="col-md-6">
          <div class="card h-100">
            <div class="card-body">
              <div class="d-flex align-items-center justify-content-between mb-3">
                <h5 class="card-title mb-0"><i class="bi bi-clock me-1"></i>Recent Signups</h5>
                <button
                  v-if="!loadingUsers && recentUsers.length > 0"
                  class="btn btn-sm btn-ghost-primary"
                  @click="activeTab = 'users'"
                >
                  View all →
                </button>
              </div>

              <!-- Skeleton loading -->
              <div v-if="loadingUsers">
                <div v-for="n in 3" :key="n" class="admin-list-item">
                  <div class="admin-skeleton-avatar"></div>
                  <div class="flex-grow-1">
                    <div class="admin-skeleton-line" style="width: 55%;"></div>
                    <div class="admin-skeleton-line" style="width: 75%; margin-top: 6px; height: 10px;"></div>
                  </div>
                  <div class="admin-skeleton-line" style="width: 50px; height: 22px; border-radius: 20px;"></div>
                </div>
              </div>

              <!-- Empty state -->
              <div v-else-if="recentUsers.length === 0" class="admin-empty-state">
                <div class="admin-empty-icon"><i class="bi bi-people"></i></div>
                <p class="admin-empty-text">No users yet.</p>
                <p class="admin-empty-sub">Users will appear here after they register.</p>
              </div>

              <div v-else>
                <div
                  v-for="u in recentUsers"
                  :key="u.uid"
                  class="admin-list-item"
                >
                  <div class="admin-user-avatar-sm">{{ (u.displayName || u.email || '?').charAt(0).toUpperCase() }}</div>
                  <div class="flex-grow-1 min-w-0">
                    <div class="admin-user-name">{{ u.displayName || '—' }}</div>
                    <div class="admin-user-email">{{ u.email }}</div>
                  </div>
                    <span class="admin-role-badge" :class="u.role === 'admin' ? 'role-admin' : 'role-user'">
                      <template v-if="u.role === 'admin'"><i class="bi bi-shield-fill me-1"></i>Admin</template>
                      <template v-else><i class="bi bi-person me-1"></i>User</template>
                    </span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Recent Posts -->
        <div class="col-md-6">
          <div class="card h-100">
            <div class="card-body">
              <div class="d-flex align-items-center justify-content-between mb-3">
                <h5 class="card-title mb-0"><i class="bi bi-clock me-1"></i>Recent Posts</h5>
                <button
                  v-if="!loadingPosts && recentPosts.length > 0"
                  class="btn btn-sm btn-ghost-primary"
                  @click="activeTab = 'content'"
                >
                  View all →
                </button>
              </div>

              <!-- Skeleton loading -->
              <div v-if="loadingPosts">
                <div v-for="n in 3" :key="n" class="admin-list-item">
                  <div class="admin-skeleton-post-icon"></div>
                  <div class="flex-grow-1">
                    <div class="admin-skeleton-line" style="width: 80%;"></div>
                    <div class="admin-skeleton-line" style="width: 50%; margin-top: 6px; height: 10px;"></div>
                  </div>
                  <div class="admin-skeleton-line" style="width: 55px; height: 22px; border-radius: 20px;"></div>
                </div>
              </div>

              <!-- Empty state -->
              <div v-else-if="recentPosts.length === 0" class="admin-empty-state">
                <div class="admin-empty-icon"><i class="bi bi-newspaper"></i></div>
                <p class="admin-empty-text">No posts yet.</p>
                <p class="admin-empty-sub">Community posts will appear here once submitted.</p>
              </div>

              <div v-else>
                <div
                  v-for="p in recentPosts"
                  :key="p.id"
                  class="admin-list-item admin-list-item-hoverable"
                >
                  <div class="admin-post-icon"><i class="bi bi-newspaper"></i></div>
                  <div class="flex-grow-1 min-w-0">
                    <RouterLink
                      :to="{ name: 'UserNewsDetails', params: { id: p.id } }"
                      class="admin-post-title admin-post-link"
                    >
                      {{ p.title }}
                    </RouterLink>
                    <div class="admin-post-meta">by {{ p.userName }} · {{ formatDate(p.createdAt) }}</div>
                  </div>
                  <div class="d-flex align-items-center gap-2">
                    <span v-if="p.category" class="admin-category-badge">{{ p.category }}</span>
                    <button
                      class="btn-icon-danger"
                      title="Delete post"
                      @click="askDeletePost(p)"
                    ><i class="bi bi-trash"></i></button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

      </div>
    </div>

    <!-- ══════════════════════════
         TAB: USERS
         ══════════════════════════ -->
    <div v-else-if="activeTab === 'users'">

      <div v-if="loadingUsers" class="text-center py-5">
        <div class="spinner-border"></div>
        <p class="text-muted mt-3">Loading users…</p>
      </div>

      <div v-else-if="users.length === 0" class="admin-empty-state-full">
        <div class="admin-empty-icon-lg"><i class="bi bi-people"></i></div>
        <h3>No users found</h3>
        <p class="text-muted">Users will appear here after they register.</p>
      </div>

      <div v-else class="card">
        <div class="card-body p-0">
          <div class="table-responsive">
            <table class="table admin-table mb-0">
              <thead>
                <tr>
                  <th>User</th>
                  <th>Email</th>
                  <th>Role</th>
                  <th>Joined</th>
                  <th class="text-end">Action</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="u in users" :key="u.uid">
                  <td>
                    <div class="d-flex align-items-center gap-2">
                      <div class="admin-user-avatar-sm">{{ (u.displayName || u.email || '?').charAt(0).toUpperCase() }}</div>
                      <span>{{ u.displayName || '—' }}</span>
                    </div>
                  </td>
                  <td class="text-muted" style="font-size: 0.85rem;">{{ u.email }}</td>
                  <td>
                    <span class="admin-role-badge" :class="u.role === 'admin' ? 'role-admin' : 'role-user'">
                      <template v-if="u.role === 'admin'"><i class="bi bi-shield-fill me-1"></i>Admin</template>
                      <template v-else><i class="bi bi-person me-1"></i>User</template>
                    </span>
                  </td>
                  <td class="text-muted" style="font-size: 0.82rem;">{{ formatDate(u.createdAt) }}</td>
                  <td class="text-end">
                    <!-- Can't demote yourself -->
                    <button
                      v-if="u.uid !== currentUser?.uid"
                      class="btn btn-sm"
                      :class="u.role === 'admin' ? 'btn-outline-danger' : 'btn-outline-primary'"
                      @click="askChangeRole(u)"
                    >
                      {{ u.role === 'admin' ? 'Demote' : 'Promote' }}
                    </button>
                    <span v-else class="admin-you-badge">You</span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>

    <!-- ══════════════════════════
         TAB: CONTENT
         ══════════════════════════ -->
    <div v-else-if="activeTab === 'content'">

      <div v-if="loadingPosts" class="text-center py-5">
        <div class="spinner-border"></div>
        <p class="text-muted mt-3">Loading posts…</p>
      </div>

      <div v-else-if="posts.length === 0" class="admin-empty-state-full">
        <div class="admin-empty-icon-lg"><i class="bi bi-newspaper"></i></div>
        <h3>No community posts yet</h3>
        <p class="text-muted">Posts submitted by users will appear here.</p>
      </div>

      <div v-else class="card">
        <div class="card-body p-0">
          <div class="table-responsive">
            <table class="table admin-table mb-0">
              <thead>
                <tr>
                  <th>Title</th>
                  <th>Category</th>
                  <th>Author</th>
                  <th>Date</th>
                  <th class="text-end">Action</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="p in posts" :key="p.id">
                  <td>
                    <RouterLink
                      :to="{ name: 'UserNewsDetails', params: { id: p.id } }"
                      class="admin-post-title-cell admin-post-link"
                    >
                      {{ p.title }}
                    </RouterLink>
                    <div class="admin-post-preview">{{ p.content?.substring(0, 80) }}…</div>
                  </td>
                  <td>
                    <span v-if="p.category" class="admin-category-badge">{{ p.category }}</span>
                    <span v-else class="text-muted">—</span>
                  </td>
                  <td class="text-muted" style="font-size: 0.82rem;">{{ p.userName || '—' }}</td>
                  <td class="text-muted" style="font-size: 0.82rem;">{{ p.date || formatDate(p.createdAt) }}</td>
                  <td class="text-end">
                    <button class="btn btn-sm btn-outline-danger" @click="askDeletePost(p)">
                      <i class="bi bi-trash me-1"></i>Delete
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>

    <!-- ══ DELETE CONFIRMATION MODAL ══ -->
    <Teleport to="body">
      <div v-if="confirmDelete" class="admin-modal-backdrop" @click.self="confirmDelete = null">
        <div class="admin-modal">
          <div class="admin-modal-icon"><i class="bi bi-trash3"></i></div>
          <h4>Delete Post?</h4>
          <p class="text-muted">
            Are you sure you want to permanently delete<br>
            <strong>"{{ confirmDelete.title }}"</strong>?<br>
            <small>This cannot be undone.</small>
          </p>
          <div class="d-flex gap-2 justify-content-center mt-3">
            <button class="btn btn-outline-secondary" @click="confirmDelete = null">Cancel</button>
            <button class="btn btn-danger" @click="confirmDeletePost">Delete</button>
          </div>
        </div>
      </div>
    </Teleport>

    <!-- ══ ROLE CHANGE CONFIRMATION MODAL ══ -->
    <Teleport to="body">
      <div v-if="confirmRole" class="admin-modal-backdrop" @click.self="confirmRole = null">
        <div class="admin-modal">
          <div class="admin-modal-icon">
            <template v-if="confirmRole.newRole === 'admin'"><i class="bi bi-shield-fill"></i></template>
            <template v-else><i class="bi bi-person"></i></template>
          </div>
          <h4>{{ confirmRole.newRole === 'admin' ? 'Promote to Admin?' : 'Demote to User?' }}</h4>
          <p class="text-muted">
            <strong>{{ confirmRole.displayName }}</strong> will be changed to
            <strong>{{ confirmRole.newRole }}</strong>.
          </p>
          <div class="d-flex gap-2 justify-content-center mt-3">
            <button class="btn btn-outline-secondary" @click="confirmRole = null">Cancel</button>
            <button
              class="btn"
              :class="confirmRole.newRole === 'admin' ? 'btn-primary' : 'btn-danger'"
              @click="confirmChangeRole"
            >
              Confirm
            </button>
          </div>
        </div>
      </div>
    </Teleport>

  </div>

  <!-- Loading while auth resolves -->
  <div v-else class="text-center py-5">
    <div class="spinner-border" role="status"></div>
    <p class="text-muted mt-3">Verifying permissions…</p>
  </div>
</template>
