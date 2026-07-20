<script>
import { auth, db } from "../firebase";
import { onAuthStateChanged } from "firebase/auth";
import {
  collection,
  getDocs,
  doc,
  getDoc,
  updateDoc,
  deleteDoc,
  orderBy,
  query,
  limit,
  startAfter,
  getCountFromServer,
  where
} from "firebase/firestore";
import { Star, Newspaper, Users, Database } from "@lucide/vue";

export default {
  name: "AdminDashboard",
  components: {
    Star,
    Newspaper,
    Users,
    Database,
  },

  inject: ["toast"],

  data() {
    return {
      activeTab: "dashboard",
      currentUser: null,
      isAdmin: false,

      // Search & Filters
      searchNews: "",
      searchUsers: "",
      filterReport: "All",
      filterRole: "All", // "All", "Admin", "Member"

      // Real Data
      users: [],
      posts: [],
      totalReviews: 0,

      // Mock Data for "GameHub Moderation Console"
      reportedItems: [],
      recentActivity: [],

      // Loading states
      loadingUsers: true,
      loadingPosts: true,

      // Confirmation modals
      confirmDelete: null,
      confirmRole: null,

      // Pagination
      lastUserDoc: null,
      hasMoreUsers: false,
      lastPostDoc: null,
      hasMorePosts: false,

      unsubscribe: null,
    };
  },

  computed: {
    adminCount() {
      return this.users.filter((u) => u.role === "admin").length;
    },
    
    // Notification Badges for Sidebar
    badgeCounts() {
      return {
        reports: this.reportedItems.length,
        news: this.posts.filter(p => p.createdAt?.seconds > (Date.now()/1000 - 86400)).length || 1, // "New" articles in last 24h
        users: this.users.filter(u => u.createdAt?.seconds > (Date.now()/1000 - 86400)).length || 3 // "New" users in last 24h
      };
    },

    // Search and Filters
    filteredPosts() {
      if (!this.searchNews) return this.posts;
      const term = this.searchNews.toLowerCase();
      return this.posts.filter(p => 
        p.title?.toLowerCase().includes(term) || 
        p.authorName?.toLowerCase().includes(term)
      );
    },

    filteredUsers() {
      let result = this.users;
      
      // Role Filter
      if (this.filterRole === "Admin") {
        result = result.filter(u => u.role === "admin");
      } else if (this.filterRole === "Member") {
        result = result.filter(u => u.role !== "admin");
      }
      
      // Search Filter
      if (this.searchUsers) {
        const term = this.searchUsers.toLowerCase();
        result = result.filter(u => 
          u.email?.toLowerCase().includes(term) || 
          u.displayName?.toLowerCase().includes(term)
        );
      }
      return result;
    },

    filteredReports() {
      if (this.filterReport === "All") return this.reportedItems;
      return this.reportedItems.filter(r => r.type.includes(this.filterReport) || r.type === this.filterReport);
    },
  },

  async mounted() {
    this.unsubscribe = onAuthStateChanged(auth, async (user) => {
      if (!user) {
        return;
      }
      this.currentUser = user;

      const snap = await getDoc(doc(db, "users", user.uid));
      if (!snap.exists() || snap.data().role !== "admin") {
        this.$router.push("/");
        return;
      }
      this.isAdmin = true;

      await Promise.all([
        this.loadUsers(),
        this.loadPosts(),
        this.loadReviewsCount(),
        this.loadReports()
      ]);
    });
  },

  beforeUnmount() {
    if (this.unsubscribe) this.unsubscribe();
  },

  methods: {
    async loadReports() {
      try {
        const snap = await getDocs(query(collection(db, "reports"), orderBy("createdAt", "desc")));
        this.reportedItems = snap.docs.map(d => {
          const data = d.data();
          return {
            id: d.id,
            ...data,
            time: this.formatDate(data.createdAt)
          };
        });
      } catch(e) {
        console.error("Failed to load reports", e);
      }
    },
    async loadReviewsCount() {
      try {
        const snap = await getDocs(collection(db, "reviews"));
        this.totalReviews = snap.docs.length;
      } catch (e) {
        console.error("Failed to load reviews count", e);
      }
    },

    async loadUsers(loadMore = false) {
      if (!loadMore) {
        this.loadingUsers = true;
        this.users = [];
      }
      try {
        let q = query(collection(db, "users"), orderBy("createdAt", "desc"), limit(10));
        if (loadMore && this.lastUserDoc) {
          q = query(collection(db, "users"), orderBy("createdAt", "desc"), startAfter(this.lastUserDoc), limit(10));
        }
        const snap = await getDocs(q);
        this.lastUserDoc = snap.docs[snap.docs.length - 1];
        this.hasMoreUsers = snap.docs.length === 10;

        const fetchedUsers = await Promise.all(snap.docs.map(async (d) => {
          const data = d.data();
          const articlesQuery = query(collection(db, "news"), where("userId", "==", d.id));
          const articlesCountSnap = await getCountFromServer(articlesQuery);
          
          const reviewsQuery = query(collection(db, "reviews"), where("userId", "==", d.id));
          const reviewsCountSnap = await getCountFromServer(reviewsQuery);

          return {
            uid: d.id,
            ...data,
            mockArticles: articlesCountSnap.data().count,
            mockReviews: reviewsCountSnap.data().count,
            mockStatus: "Active"
          };
        }));
        
        if (loadMore) {
          this.users = [...this.users, ...fetchedUsers];
        } else {
          this.users = fetchedUsers;
        }
      } catch (e) {
        console.error(e);
        this.toast.show("Failed to load users.", "error");
      } finally {
        this.loadingUsers = false;
      }
    },

    async loadPosts(loadMore = false) {
      if (!loadMore) {
        this.loadingPosts = true;
        this.posts = [];
      }
      try {
        let q = query(collection(db, "news"), orderBy("createdAt", "desc"), limit(10));
        if (loadMore && this.lastPostDoc) {
          q = query(collection(db, "news"), orderBy("createdAt", "desc"), startAfter(this.lastPostDoc), limit(10));
        }
        const snap = await getDocs(q);
        this.lastPostDoc = snap.docs[snap.docs.length - 1];
        this.hasMorePosts = snap.docs.length === 10;

        const fetchedPosts = snap.docs.map((d) => {
          const data = d.data();
          return {
            id: d.id,
            ...data,
            authorName: data.authorName || "Community Member"
          };
        });

        if (loadMore) {
          this.posts = [...this.posts, ...fetchedPosts];
        } else {
          this.posts = fetchedPosts;
        }
      } catch (e) {
        console.error(e);
        this.toast.show("Failed to load posts.", "error");
      } finally {
        this.loadingPosts = false;
      }
    },

    askDeletePost(post) {
      this.confirmDelete = { id: post.id, title: post.title };
    },

    async confirmDeletePost() {
      if (!this.confirmDelete) return;
      try {
        await deleteDoc(doc(db, "news", this.confirmDelete.id));
        this.posts = this.posts.filter((p) => p.id !== this.confirmDelete.id);
        this.toast.show("News post removed from community.", "success");
        
        // Add to activity feed
        this.recentActivity.unshift({
          id: Date.now(),
          action: `Deleted article: '${this.confirmDelete.title.substring(0,20)}...'`,
          time: "Just now",
          type: "delete"
        });
        if(this.recentActivity.length > 5) this.recentActivity.pop();

      } catch (e) {
        console.error(e);
        this.toast.show("Failed to remove post.", "error");
      } finally {
        this.confirmDelete = null;
      }
    },

    askChangeRole(user, newRole) {
      this.confirmRole = {
        uid: user.uid,
        displayName: user.displayName || user.email,
        newRole: newRole,
      };
    },

    async confirmChangeRole() {
      if (!this.confirmRole) return;
      try {
        await updateDoc(doc(db, "users", this.confirmRole.uid), {
          role: this.confirmRole.newRole,
        });
        const u = this.users.find((u) => u.uid === this.confirmRole.uid);
        if (u) u.role = this.confirmRole.newRole;
        this.toast.show(`Role updated for ${this.confirmRole.displayName}.`, "success");
        
        this.recentActivity.unshift({
          id: Date.now(),
          action: `${this.confirmRole.newRole === 'admin' ? 'Promoted' : 'Demoted'} ${this.confirmRole.displayName}`,
          time: "Just now",
          type: "promote"
        });
        if(this.recentActivity.length > 5) this.recentActivity.pop();

      } catch (e) {
        console.error(e);
        this.toast.show("Failed to update role.", "error");
      } finally {
        this.confirmRole = null;
      }
    },

    actionComingSoon(actionName) {
      this.toast.show(`Coming in Version 2`, "info");
    },

    async reportAction(id, actionStr, target) {
      try {
        const report = this.reportedItems.find(r => r.id === id);
        if (actionStr === "Delete" && report) {
          if (report.type === "Article") {
            await deleteDoc(doc(db, "news", report.targetId));
          } else if (report.type === "Review") {
            await deleteDoc(doc(db, "reviews", report.targetId));
          }
        }
        await deleteDoc(doc(db, "reports", id));
        this.reportedItems = this.reportedItems.filter(r => r.id !== id);
        
        this.toast.show(`Report action executed: ${actionStr}`, "success");
        
        if (actionStr === "Delete") {
          this.recentActivity.unshift({
            id: Date.now(),
            action: `Deleted reported content: ${target}`,
            time: "Just now",
            type: "delete"
          });
          if(this.recentActivity.length > 5) this.recentActivity.pop();
        }
      } catch(e) {
        console.error(e);
        this.toast.show("Action failed", "error");
      }
    },

    formatDate(ts) {
      if (!ts?.seconds) return "—";
      return new Date(ts.seconds * 1000).toLocaleDateString("en-US", {
        year: "numeric",
        month: "short",
        day: "numeric",
      });
    }
  },
};
</script>

<template>
  <div class="admin-wrapper" v-if="isAdmin">
    <!-- ── Sidebar ── -->
    <aside class="gh-sidebar" :class="{ 'sidebar-mobile-open': sidebarOpen }">
      <div class="sidebar-header">
        <div class="gh-logo">
          <i class="bi bi-controller"></i>
          <span>GameHub</span>
        </div>
        <span class="console-tag">Operations Center</span>
      </div>
      
      <div class="sidebar-section-title">Moderation</div>
      <nav class="sidebar-nav">
        <button class="nav-btn" :class="{ active: activeTab === 'dashboard' }" @click="activeTab = 'dashboard'">
          <i class="bi bi-grid-fill"></i> 
          <span>Dashboard</span>
        </button>
        <button class="nav-btn" :class="{ active: activeTab === 'reviews' }" @click="activeTab = 'reviews'">
          <i class="bi bi-flag-fill"></i> 
          <span>Moderation Queue</span>
          <span class="nav-badge" v-if="badgeCounts.reports > 0">{{ badgeCounts.reports }}</span>
        </button>
        <button class="nav-btn" :class="{ active: activeTab === 'news' }" @click="activeTab = 'news'">
          <i class="bi bi-newspaper"></i> 
          <span>Community Feed</span>
          <span class="nav-badge" v-if="badgeCounts.news > 0">{{ badgeCounts.news }}</span>
        </button>
        <button class="nav-btn" :class="{ active: activeTab === 'users' }" @click="activeTab = 'users'">
          <i class="bi bi-people-fill"></i> 
          <span>Players</span>
          <span class="nav-badge" v-if="badgeCounts.users > 0">{{ badgeCounts.users }}</span>
        </button>
      </nav>

      <div class="sidebar-section-title mt-4" v-show="false">System</div>
      <nav class="sidebar-nav" v-show="false">
        <button class="nav-btn" @click="actionComingSoon('Settings')">
          <i class="bi bi-gear-fill"></i> 
          <span>Platform Settings</span>
        </button>
      </nav>
      
      <div class="sidebar-footer">
        <div class="admin-profile">
          <div class="admin-avatar"><i class="bi bi-person-fill"></i></div>
          <div class="admin-info">
            <p class="admin-user">{{ currentUser?.email }}</p>
            <span class="admin-badge">Administrator</span>
          </div>
        </div>
      </div>
    </aside>

    <!-- ── Main Content Area ── -->
    <main class="gh-main">
      <div class="d-md-none d-flex align-items-center justify-content-between p-3 border-bottom border-secondary" style="background: var(--bg-dark); position: sticky; top: 0; z-index: 10;">
        <div class="gh-logo m-0" style="font-size: 1.2rem;">
          <i class="bi bi-controller"></i>
          <span>GameHub</span>
        </div>
        <button class="btn btn-outline-secondary btn-sm border-0 text-white" @click="sidebarOpen = !sidebarOpen">
          <i class="bi bi-list fs-4"></i>
        </button>
      </div>

      <div class="content-container" @click="sidebarOpen = false">
        
        <!-- ── TAB: DASHBOARD ── -->
        <div v-if="activeTab === 'dashboard'" class="gh-tab-pane fade-in">
          
          <div class="pane-header">
            <div>
              <h2 class="pane-title">Welcome back, Administrator.</h2>
              <p class="pane-subtitle">
                Current queue: <strong class="text-primary-var">{{ badgeCounts.reports }} reports</strong>, 
                <strong class="text-primary-var">{{ badgeCounts.users }} new players</strong>, 
                <strong class="text-primary-var">{{ badgeCounts.news }} articles pending</strong>.
              </p>
            </div>
          </div>
          
          <!-- Top Row: Stats -->
          <div class="dashboard-stats-row">
            <div class="stat-card">
              <div class="stat-icon"><i class="bi bi-people-fill"></i></div>
              <div class="stat-info">
                <h3>Total Players</h3>
                <div class="stat-val">{{ users.length }} <span class="stat-trend trend-up">↑ {{ badgeCounts.users }} today</span></div>
              </div>
            </div>
            <div class="stat-card">
              <div class="stat-icon"><i class="bi bi-newspaper"></i></div>
              <div class="stat-info">
                <h3>Articles</h3>
                <div class="stat-val">{{ posts.length }} <span class="stat-trend text-muted">{{ badgeCounts.news }} pending review</span></div>
              </div>
            </div>
            <div class="stat-card">
              <div class="stat-icon"><i class="bi bi-star-fill"></i></div>
              <div class="stat-info">
                <h3>Reviews</h3>
                <div class="stat-val">{{ totalReviews }} <span class="stat-trend text-danger">12 reported</span></div>
              </div>
            </div>
            <div class="stat-card">
              <div class="stat-icon text-danger"><i class="bi bi-flag-fill"></i></div>
              <div class="stat-info">
                <h3>Reports</h3>
                <div class="stat-val">{{ reportedItems.length }} <span class="stat-trend text-danger">Needs attention</span></div>
              </div>
            </div>
          </div>

          <!-- Middle Row: Reports -->
          <div class="dashboard-grid mt-4">
            <div class="gh-widget w-reports">
              <div class="widget-header">
                <div class="d-flex align-items-center gap-3">
                  <h3 class="mb-0"><i class="bi bi-exclamation-circle-fill text-warning"></i> Moderation Queue</h3>
                  <span class="gh-badge badge-neutral"><i class="bi bi-cone-striped"></i> V2 Planned</span>
                </div>
                <button class="btn-gh-text small" @click="activeTab = 'reviews'">View All</button>
              </div>
              <div class="widget-body">
                <div v-if="reportedItems.length === 0" class="empty-state">
                  <i class="bi bi-check-circle-fill text-success"></i>
                  <p>Queue is empty. Community is peaceful.</p>
                </div>
                <div v-else class="report-list">
                  <div class="report-item" v-for="report in reportedItems.slice(0, 3)" :key="report.id">
                    <div class="report-info">
                      <div class="report-meta">
                        <span class="rep-severity" :class="'sev-' + report.severity.toLowerCase()">
                          {{ report.severity === 'High' ? '🔴 HIGH PRIORITY' : (report.severity === 'Medium' ? '🟠 MEDIUM' : '🟢 LOW') }}
                        </span>
                        <span class="rep-type">{{ report.icon }} {{ report.type }}</span>
                        <span class="rep-time">{{ report.time }}</span>
                      </div>
                      <div class="report-text">
                        <strong>{{ report.reason }}</strong> in <em>{{ report.target }}</em>
                      </div>
                      <div class="report-user">Reported by {{ report.user }}</div>
                    </div>
                    <div class="report-actions-extended">
                      <button class="btn-gh-outline" @click="reportAction(report.id, 'View', report.target)">View</button>
                      <button class="btn-gh-danger" @click="reportAction(report.id, 'Delete', report.target)">Delete</button>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <div class="gh-widget w-quick" v-show="false">
              <div class="widget-header">
                <div class="d-flex align-items-center gap-3">
                  <h3 class="mb-0"><i class="bi bi-lightning-charge-fill text-primary"></i> Platform Actions</h3>
                  <span class="gh-badge badge-neutral"><i class="bi bi-cone-striped"></i> V2 Planned</span>
                </div>
              </div>
              <div class="widget-body d-flex flex-column gap-3">
                <button class="qa-btn" @click="actionComingSoon('Feature Game')"><i class="bi bi-star-fill"></i> Feature Game on Homepage</button>
                <button class="qa-btn" @click="actionComingSoon('Manage Hero Banners')"><i class="bi bi-images"></i> Manage Hero Banners</button>
                <button class="qa-btn" @click="actionComingSoon('Global Announcement')"><i class="bi bi-megaphone-fill"></i> Create Global Announcement</button>
                <button class="qa-btn" @click="actionComingSoon('News Categories')"><i class="bi bi-tags-fill"></i> Manage News Categories</button>
              </div>
            </div>
          </div>

          <!-- Bottom Row: Recent Activity -->
          <div class="gh-widget mt-4">
            <div class="widget-header">
              <h3><i class="bi bi-activity text-primary"></i> Recent Community Activity</h3>
            </div>
            <div class="widget-body">
              <div class="activity-timeline">
                <div class="activity-item" v-for="act in recentActivity" :key="act.id">
                  <div class="act-icon" :class="'act-type-' + act.type">
                    <i class="bi" :class="{
                      'bi-trash-fill': act.type === 'delete',
                      'bi-check-circle-fill': act.type === 'approve',
                      'bi-shield-fill': act.type === 'promote',
                      'bi-person-plus-fill': act.type === 'signup'
                    }"></i>
                  </div>
                  <div class="act-content"><strong>{{ act.action }}</strong> <span class="act-time">{{ act.time }}</span></div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- ── TAB: COMMUNITY FEED ── -->
        <div v-if="activeTab === 'news'" class="gh-tab-pane fade-in">
          <div class="pane-header d-flex justify-content-between align-items-end flex-wrap gap-3">
            <div>
              <h2 class="pane-title">Community Feed</h2>
              <p class="pane-subtitle">Moderate user-submitted articles and platform news.</p>
            </div>
            <div class="search-bar">
              <i class="bi bi-search"></i>
              <input type="text" v-model="searchNews" placeholder="Search articles or authors..." />
            </div>
          </div>

          <div v-if="loadingPosts" class="loading-state"><div class="spinner"></div></div>
          
          <div v-else class="gh-widget">
            <div class="widget-header">
              <h3>Published Articles ({{ filteredPosts.length }})</h3>
            </div>
            <div class="table-responsive">
              <table class="gh-table align-middle">
                <thead>
                  <tr>
                    <th>Article</th>
                    <th>Author</th>
                    <th>Status</th>
                    <th>Published Date</th>
                    <th class="text-end">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="post in filteredPosts" :key="post.id">
                    <td class="primary-col">
                      <div class="d-flex align-items-center gap-3">
                        <!-- Placeholder Thumbnail -->
                        <div class="article-thumb">
                          <i class="bi bi-newspaper"></i>
                        </div>
                        <div class="text-truncate" style="max-width: 250px; font-weight: 700;">
                          {{ post.title }}
                        </div>
                      </div>
                    </td>
                    <td>
                      <div class="user-cell">
                        <div class="avatar-sm user-av"><i class="bi bi-person-fill"></i></div>
                        <span class="muted-col">{{ post.authorName }}</span>
                      </div>
                    </td>
                    <td>
                      <span class="gh-badge badge-success"><i class="bi bi-check-circle-fill me-1"></i> Published</span>
                    </td>
                    <td class="muted-col">{{ formatDate(post.createdAt) }}</td>
                    <td class="text-end">
                      <button class="btn-gh-outline me-2" @click="$router.push(`/news/${post.id}`)">View</button>
                      <button class="btn-gh-danger" @click="askDeletePost(post)">Delete</button>
                    </td>
                  </tr>
                  <tr v-if="filteredPosts.length === 0">
                    <td colspan="5" class="py-5">
                      <div class="gh-empty-state" style="padding: 2rem 1rem;">
                        <i class="bi bi-newspaper"></i>
                        <h3>No articles found</h3>
                        <p>No articles match "{{ searchNews }}".</p>
                      </div>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
            <div class="d-flex justify-content-center mt-3" v-if="hasMorePosts && !searchNews">
              <button class="btn-gh-outline" @click="loadPosts(true)">
                <span v-if="loadingPosts" class="spinner-border spinner-border-sm me-2"></span>
                Load More Articles
              </button>
            </div>
          </div>
        </div>

        <!-- ── TAB: MODERATION QUEUE ── -->
        <div v-if="activeTab === 'reviews'" class="gh-tab-pane fade-in">
          <div class="pane-header d-flex justify-content-between align-items-end flex-wrap gap-3">
            <div>
              <h2 class="pane-title d-flex align-items-center gap-3">
                Moderation Queue 
                <span class="gh-badge badge-neutral fs-6"><i class="bi bi-cone-striped"></i> V2 Planned</span>
              </h2>
              <p class="pane-subtitle">Manage flagged reviews, inappropriate usernames, and metadata issues.</p>
            </div>
            <div class="filter-pills">
              <button class="filter-pill" :class="{ active: filterReport === 'All' }" @click="filterReport = 'All'">All</button>
              <button class="filter-pill" :class="{ active: filterReport === 'Review' }" @click="filterReport = 'Review'"><Star size="16" class="me-1" style="vertical-align: text-top;"/> Reviews</button>
              <button class="filter-pill" :class="{ active: filterReport === 'Article' }" @click="filterReport = 'Article'"><Newspaper size="16" class="me-1" style="vertical-align: text-top;"/> Articles</button>
              <button class="filter-pill" :class="{ active: filterReport === 'Player' }" @click="filterReport = 'Player'"><Users size="16" class="me-1" style="vertical-align: text-top;"/> Players</button>
              <button class="filter-pill" :class="{ active: filterReport === 'Metadata' }" @click="filterReport = 'Metadata'"><Database size="16" class="me-1" style="vertical-align: text-top;"/> Metadata</button>
            </div>
          </div>

          <div class="gh-widget">
            <div class="widget-header">
              <h3>Flagged Content Queue ({{ filteredReports.length }})</h3>
            </div>
            <div class="widget-body">
              <div v-if="filteredReports.length === 0" class="gh-empty-state">
                <i class="bi bi-shield-check text-success"></i>
                <h3>All Clear</h3>
                <p>No flagged content at the moment.</p>
              </div>
              <div v-else class="report-list">
                <div class="report-item" v-for="report in filteredReports" :key="report.id">
                  <div class="report-info">
                    <div class="report-meta">
                      <span class="rep-severity" :class="'sev-' + report.severity.toLowerCase()">
                        {{ report.severity === 'High' ? '🔴 HIGH PRIORITY' : (report.severity === 'Medium' ? '🟠 MEDIUM' : '🟢 LOW') }}
                      </span>
                      <span class="rep-type">{{ report.icon }} {{ report.type }}</span>
                      <span class="rep-time">{{ report.time }}</span>
                    </div>
                    <div class="report-text mt-1">
                      <strong>{{ report.reason }}</strong> regarding <em>{{ report.target }}</em>
                    </div>
                    <div class="report-user">Reported by {{ report.user }}</div>
                  </div>
                  <div class="report-actions-extended">
                    <button class="btn-gh-outline" @click="reportAction(report.id, 'View', report.target)">View</button>
                    <button class="btn-gh-outline" @click="reportAction(report.id, 'Warn User', report.target)">Warn User</button>
                    <button class="btn-gh-danger" @click="reportAction(report.id, 'Delete', report.target)">Delete</button>
                    <button class="btn-gh-solid small ms-2" @click="reportAction(report.id, 'Dismiss', report.target)">Dismiss</button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- ── TAB: PLAYERS ── -->
        <div v-if="activeTab === 'users'" class="gh-tab-pane fade-in">
          <div class="pane-header d-flex justify-content-between align-items-end flex-wrap gap-3">
            <div>
              <h2 class="pane-title">Player Directory</h2>
              <p class="pane-subtitle">Manage administrator privileges and player standing.</p>
            </div>
            
            <div class="d-flex gap-3 align-items-center flex-wrap">
              <div class="filter-pills">
                <button class="filter-pill" :class="{ active: filterRole === 'All' }" @click="filterRole = 'All'">All</button>
                <button class="filter-pill" :class="{ active: filterRole === 'Admin' }" @click="filterRole = 'Admin'">Admins</button>
                <button class="filter-pill" :class="{ active: filterRole === 'Member' }" @click="filterRole = 'Member'">Members</button>
              </div>
              <div class="search-bar">
                <i class="bi bi-search"></i>
                <input type="text" v-model="searchUsers" placeholder="Search players..." />
              </div>
            </div>
          </div>

          <div v-if="loadingUsers" class="loading-state"><div class="spinner"></div></div>

          <div v-else class="gh-widget">
            <div class="widget-header">
              <h3>Player Database ({{ filteredUsers.length }})</h3>
              <span class="badge-count">{{ adminCount }} Admins</span>
            </div>
            <div class="table-responsive">
              <table class="gh-table align-middle">
                <thead>
                  <tr>
                    <th>Player</th>
                    <th>Email</th>
                    <th>Articles</th>
                    <th>Reviews</th>
                    <th>Status</th>
                    <th class="text-end">Management</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="u in filteredUsers" :key="u.uid" :class="{'row-highlight': u.role === 'admin'}">
                    <td class="primary-col">
                      <div class="user-cell">
                        <div class="avatar-sm" :class="u.role === 'admin' ? 'admin-av' : 'user-av'">
                          <i class="bi" :class="u.role === 'admin' ? 'bi-shield-fill' : 'bi-person-fill'"></i>
                        </div>
                        <div>
                          <strong>{{ u.displayName || 'No Name' }}</strong>
                          <div class="small text-muted">Joined {{ formatDate(u.createdAt) }}</div>
                        </div>
                      </div>
                    </td>
                    <td class="muted-col">{{ u.email }}</td>
                    <td class="muted-col">{{ u.mockArticles }}</td>
                    <td class="muted-col">{{ u.mockReviews }}</td>
                    <td>
                      <span class="gh-badge" :class="u.mockStatus === 'Active' ? 'badge-neutral' : 'badge-danger'">
                        <i v-if="u.mockStatus === 'Active'" class="bi bi-circle-fill text-success" style="font-size: 0.5rem; vertical-align: middle; margin-right: 4px;"></i>
                        {{ u.mockStatus }}
                      </span>
                    </td>
                    <td class="text-end">
                      <div v-if="u.uid === currentUser?.uid" class="d-inline-block px-3 py-1 rounded" style="background: rgba(13, 110, 253, 0.1); border: 1px solid rgba(13, 110, 253, 0.2);">
                        <i class="bi bi-shield-fill-check text-primary me-1"></i> 
                        <span class="text-primary fw-bold" style="font-size: 0.85rem;">Administrator</span>
                      </div>
                      <button 
                        v-else-if="u.role !== 'admin'" 
                        class="btn-gh-outline" 
                        @click="askChangeRole(u, 'admin')">
                        Promote to Admin
                      </button>
                      <button 
                        v-else 
                        class="btn-gh-danger" 
                        @click="askChangeRole(u, 'user')">
                        Revoke Admin
                      </button>
                    </td>
                  </tr>
                  <tr v-if="filteredUsers.length === 0">
                    <td colspan="6" class="py-5">
                      <div class="gh-empty-state" style="padding: 2rem 1rem;">
                        <i class="bi bi-people"></i>
                        <h3>No players found</h3>
                        <p>No players match your current filters.</p>
                      </div>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
            <div class="d-flex justify-content-center mt-3" v-if="hasMoreUsers && filterRole === 'All' && !searchUsers">
              <button class="btn-gh-outline" @click="loadUsers(true)">
                <span v-if="loadingUsers" class="spinner-border spinner-border-sm me-2"></span>
                Load More Players
              </button>
            </div>
          </div>
        </div>

      </div>
    </main>

    <!-- ── MODALS ── -->
    
    <!-- Delete Post Modal -->
    <div class="gh-modal-overlay" v-if="confirmDelete">
      <div class="gh-modal">
        <h3 class="text-danger"><i class="bi bi-exclamation-triangle-fill"></i> Remove Article</h3>
        <p>Are you sure you want to permanently delete the article <strong>"{{ confirmDelete.title }}"</strong>?</p>
        <p class="text-muted small">This action removes the post from the Community Feed. It cannot be undone.</p>
        <div class="modal-actions">
          <button class="btn-gh-text" @click="confirmDelete = null">Cancel</button>
          <button class="btn-gh-danger-solid" @click="confirmDeletePost">Delete Article</button>
        </div>
      </div>
    </div>

    <!-- Change Role Modal -->
    <div class="gh-modal-overlay" v-if="confirmRole">
      <div class="gh-modal">
        <h3 :class="confirmRole.newRole === 'admin' ? 'text-primary' : 'text-danger'">
          <i class="bi" :class="confirmRole.newRole === 'admin' ? 'bi-shield-arrow-up' : 'bi-shield-x'"></i>
          Confirm Role Change
        </h3>
        <p>
          You are about to {{ confirmRole.newRole === 'admin' ? 'promote' : 'revoke admin privileges for' }} 
          <strong>{{ confirmRole.displayName }}</strong>.
        </p>
        <p class="text-muted small" v-if="confirmRole.newRole === 'admin'">They will gain full access to the Operations Center and can moderate content and players.</p>
        <p class="text-muted small" v-else>They will lose all console access immediately.</p>
        <div class="modal-actions">
          <button class="btn-gh-text" @click="confirmRole = null">Cancel</button>
          <button :class="confirmRole.newRole === 'admin' ? 'btn-gh-solid' : 'btn-gh-danger-solid'" @click="confirmChangeRole">Confirm Change</button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* ── Variables & Reset ── */
.admin-wrapper {
  display: flex;
  min-height: 100vh;
  /* Premium AAA Gaming Background */
  background-image: 
    radial-gradient(circle at top right, rgba(0, 210, 255, 0.08) 0%, transparent 60%),
    url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noiseFilter'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.8' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noiseFilter)' opacity='0.05'/%3E%3C/svg%3E"),
    linear-gradient(to bottom, #090c15, #05080f);
  background-attachment: fixed;
  color: var(--text-primary);
  font-family: var(--font-family);
  -webkit-font-smoothing: antialiased;
}

/* ── Sidebar ── */
.gh-sidebar {
  width: 280px;
  background: rgba(10, 15, 25, 0.7);
  backdrop-filter: blur(25px);
  -webkit-backdrop-filter: blur(25px);
  border-right: 1px solid rgba(255, 255, 255, 0.08);
  display: flex;
  flex-direction: column;
  flex-shrink: 0;
  height: 100vh;
  position: sticky;
  top: 0;
  z-index: 10;
}
.sidebar-header {
  padding: 30px 24px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.gh-logo {
  font-size: 1.5rem;
  font-weight: 900;
  color: #fff;
  display: flex;
  align-items: center;
  gap: 10px;
  letter-spacing: -0.02em;
}
.gh-logo i {
  color: var(--primary);
}
.console-tag {
  font-size: 0.7rem;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: var(--primary);
  padding: 3px 8px;
  background: rgba(0, 210, 255, 0.1);
  border-radius: 4px;
  align-self: flex-start;
}

.sidebar-section-title {
  padding: 24px 24px 8px;
  font-size: 0.7rem;
  font-weight: 800;
  color: rgba(255, 255, 255, 0.4);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}
.sidebar-nav {
  display: flex;
  flex-direction: column;
  padding: 0 12px;
  gap: 4px;
}
.nav-btn {
  background: transparent;
  border: none;
  color: rgba(255, 255, 255, 0.7);
  text-align: left;
  padding: 12px 16px;
  border-radius: 8px;
  font-size: 0.95rem;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 14px;
  transition: all 0.2s ease;
  position: relative;
}
.nav-btn span:first-of-type { flex: 1; }
.nav-badge {
  background: #ef4444;
  color: #fff;
  font-size: 0.7rem;
  font-weight: 800;
  padding: 2px 8px;
  border-radius: 12px;
  box-shadow: 0 0 10px rgba(239, 68, 68, 0.4);
}

.nav-btn:hover {
  background: rgba(255, 255, 255, 0.05);
  color: #fff;
  transform: translateX(4px);
}
.nav-btn.active {
  background: linear-gradient(90deg, rgba(0, 210, 255, 0.15) 0%, transparent 100%);
  color: #fff;
  border-left: 3px solid var(--primary);
  border-radius: 4px;
}
.nav-btn.active i {
  color: var(--primary);
}

.sidebar-footer {
  margin-top: auto;
  padding: 20px;
  background: rgba(0, 0, 0, 0.2);
  border-top: 1px solid rgba(255, 255, 255, 0.05);
}
.admin-profile {
  display: flex;
  align-items: center;
  gap: 12px;
}
.admin-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--primary) 0%, #3a00f5 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.2rem;
  color: #fff;
}
.admin-user {
  font-size: 0.85rem;
  font-weight: 700;
  color: #fff;
  margin: 0 0 2px;
  max-width: 150px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.admin-badge {
  font-size: 0.65rem;
  background: rgba(255, 255, 255, 0.1);
  color: rgba(255,255,255,0.7);
  padding: 2px 6px;
  border-radius: 4px;
  font-weight: 800;
  text-transform: uppercase;
}

/* ── Main Content ── */
.gh-main {
  flex: 1;
  padding: 40px;
  overflow-y: auto;
}
.content-container {
  max-width: 1200px;
  margin: 0 auto;
}
.pane-header {
  margin-bottom: 32px;
}
.pane-title {
  font-size: 2.2rem;
  font-weight: 800;
  color: #fff;
  margin: 0 0 8px;
  letter-spacing: -0.02em;
}
.pane-subtitle {
  color: var(--text-muted);
  font-size: 1rem;
  margin: 0;
}

/* ── Top Dashboard Stats ── */
.dashboard-stats-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 24px;
  margin-bottom: 24px;
}
.stat-card {
  background: rgba(255,255,255,0.02);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 16px;
  padding: 24px;
  display: flex;
  align-items: center;
  gap: 20px;
  box-shadow: 0 12px 40px rgba(0,0,0,0.3);
  transition: transform 0.2s, border-color 0.2s;
}
.stat-card:hover {
  transform: translateY(-2px);
  border-color: rgba(255,255,255,0.15);
}
.stat-icon {
  width: 50px;
  height: 50px;
  border-radius: 12px;
  background: rgba(255,255,255,0.05);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  color: var(--primary);
}
.stat-icon.text-danger { color: #ef4444; background: rgba(239,68,68,0.1); }
.stat-info h3 {
  font-size: 0.85rem;
  text-transform: uppercase;
  color: var(--text-muted);
  font-weight: 700;
  letter-spacing: 0.05em;
  margin: 0 0 4px;
}
.stat-val {
  font-size: 1.8rem;
  font-weight: 800;
  color: #fff;
  display: flex;
  align-items: baseline;
  gap: 8px;
}
.stat-trend { font-size: 0.8rem; font-weight: 600; }
.trend-up { color: #10b981; }

/* ── Search & Filters ── */
.search-bar {
  display: flex;
  align-items: center;
  background: rgba(0,0,0,0.3);
  border: 1px solid rgba(255,255,255,0.1);
  border-radius: 8px;
  padding: 10px 16px;
  width: 300px;
  transition: border-color 0.2s;
}
.search-bar:focus-within {
  border-color: var(--primary);
}
.search-bar i { color: var(--text-muted); margin-right: 10px; }
.search-bar input {
  background: transparent;
  border: none;
  outline: none;
  color: #fff;
  width: 100%;
}
.filter-pills {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}
.filter-pill {
  background: rgba(255,255,255,0.05);
  border: 1px solid rgba(255,255,255,0.1);
  color: var(--text-secondary);
  padding: 8px 16px;
  border-radius: 20px;
  font-size: 0.85rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}
.filter-pill:hover, .filter-pill.active {
  background: rgba(0, 210, 255, 0.15);
  border-color: var(--primary);
  color: #fff;
}

/* ── Widgets ── */
.dashboard-grid {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 24px;
}
@media (max-width: 950px) {
  .dashboard-grid { grid-template-columns: 1fr; }
  .gh-sidebar { width: 70px; }
  .sidebar-header span, .sidebar-section-title, .nav-btn span, .admin-info { display: none; }
  .nav-btn { justify-content: center; padding: 12px; }
  .nav-btn i { font-size: 1.2rem; margin: 0; }
  .sidebar-header { align-items: center; padding: 24px 0; }
  .gh-logo { font-size: 1.8rem; }
  .admin-avatar { margin: 0 auto; }
}

.gh-widget {
  background: rgba(255, 255, 255, 0.02);
  backdrop-filter: blur(15px);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 12px 40px rgba(0,0,0,0.3);
  margin-bottom: 24px;
}
.widget-header {
  padding: 24px 32px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: rgba(0,0,0,0.15);
}
.widget-header h3 {
  font-size: 1.1rem;
  font-weight: 700;
  color: #fff;
  margin: 0;
  display: flex;
  align-items: center;
  gap: 10px;
}
.badge-count {
  background: rgba(0, 210, 255, 0.15);
  color: var(--primary);
  padding: 4px 10px;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 800;
}
.widget-body {
  padding: 32px;
}

/* Reports */
.empty-state {
  text-align: center;
  padding: 50px 0;
  color: var(--text-muted);
}
.empty-state i { font-size: 2.5rem; margin-bottom: 16px; display: block; opacity: 0.8; }
.report-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.report-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: rgba(255,255,255,0.03);
  padding: 20px 24px;
  border-radius: 12px;
  border: 1px solid rgba(255,255,255,0.05);
  transition: background 0.2s, border-color 0.2s;
}
.report-item:hover {
  background: rgba(255,255,255,0.06);
  border-color: rgba(255,255,255,0.15);
}
.report-info { display: flex; flex-direction: column; gap: 6px; }
.report-meta { display: flex; gap: 12px; align-items: center; }
.rep-severity { font-size: 0.75rem; font-weight: 800; }
.sev-high { color: #ef4444; }
.sev-medium { color: #f97316; }
.sev-low { color: #22c55e; }

.rep-type { 
  font-weight: 800; 
  font-size: 0.7rem; 
  text-transform: uppercase; 
  background: rgba(255,255,255,0.1);
  padding: 3px 8px;
  border-radius: 4px;
  color: #fff;
}
.rep-time { font-size: 0.8rem; color: var(--text-muted); }
.report-text { font-size: 1.05rem; color: #fff; }
.report-user { font-size: 0.85rem; color: var(--text-secondary); }

.report-actions-extended {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

/* Quick Actions */
.qa-btn {
  background: rgba(255,255,255,0.03);
  color: #fff;
  border: 1px solid rgba(255,255,255,0.05);
  padding: 16px 20px;
  border-radius: 12px;
  text-align: left;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 12px;
  transition: all 0.2s;
}
.qa-btn i { font-size: 1.1rem; color: var(--primary); }
.qa-btn:hover { 
  background: rgba(0, 210, 255, 0.1); 
  border-color: rgba(0, 210, 255, 0.3);
  transform: translateY(-2px);
}

/* Activity Timeline */
.activity-timeline {
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.activity-item {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px 20px;
  background: rgba(255,255,255,0.02);
  border-radius: 12px;
  border-left: 3px solid rgba(255,255,255,0.1);
}
.act-icon {
  width: 40px; height: 40px; border-radius: 50%;
  display: flex; align-items: center; justify-content: center; font-size: 1.2rem;
}
.act-type-delete { background: rgba(239,68,68,0.1); color: #ef4444; border: 1px solid rgba(239,68,68,0.2); }
.act-type-approve { background: rgba(34,197,94,0.1); color: #22c55e; border: 1px solid rgba(34,197,94,0.2); }
.act-type-promote { background: rgba(245,158,11,0.1); color: #f59e0b; border: 1px solid rgba(245,158,11,0.2); }
.act-type-signup { background: rgba(56,189,248,0.1); color: #38bdf8; border: 1px solid rgba(56,189,248,0.2); }
.act-content { font-size: 0.95rem; color: #fff; flex: 1; }
.act-time { font-size: 0.8rem; color: var(--text-muted); float: right; }

/* ── Tables ── */
.table-responsive {
  overflow-x: auto;
}
.gh-table {
  width: 100%;
  border-collapse: collapse;
}
.gh-table th {
  text-align: left;
  padding: 20px 32px;
  font-size: 0.8rem;
  font-weight: 800;
  text-transform: uppercase;
  color: var(--text-muted);
  border-bottom: 1px solid rgba(255,255,255,0.05);
  background: rgba(0,0,0,0.1);
}
.gh-table td {
  padding: 24px 32px;
  border-bottom: 1px solid rgba(255,255,255,0.03);
  font-size: 0.95rem;
}
.gh-table tr:hover td {
  background: rgba(255,255,255,0.03);
}
.row-highlight td {
  background: rgba(0, 210, 255, 0.04);
}
.primary-col { color: #fff; }
.muted-col { color: var(--text-secondary); }

.user-cell {
  display: flex;
  align-items: center;
  gap: 16px;
}
.avatar-sm {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-size: 1.1rem;
}
.admin-av { background: linear-gradient(135deg, var(--primary) 0%, #3a00f5 100%); }
.user-av { background: rgba(255,255,255,0.1); }

.article-thumb {
  width: 48px;
  height: 48px;
  background: rgba(0,0,0,0.3);
  border: 1px solid rgba(255,255,255,0.1);
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.2rem;
  color: var(--primary);
}

/* Badges */
.gh-badge {
  font-size: 0.75rem;
  font-weight: 700;
  padding: 6px 12px;
  border-radius: 12px;
  display: inline-flex;
  align-items: center;
}
.badge-primary { background: rgba(0, 210, 255, 0.15); color: var(--primary); border: 1px solid rgba(0,210,255,0.3); }
.badge-neutral { background: rgba(255,255,255,0.1); color: var(--text-muted); }
.badge-danger { background: rgba(239, 68, 68, 0.1); color: #ef4444; border: 1px solid rgba(239, 68, 68, 0.3); }
.badge-success { background: rgba(34, 197, 94, 0.15); color: #4ade80; border: 1px solid rgba(34, 197, 94, 0.3); }

/* Buttons */
.btn-gh-outline {
  background: transparent;
  border: 1px solid rgba(255,255,255,0.2);
  color: #fff;
  padding: 8px 16px;
  border-radius: 8px;
  font-size: 0.85rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}
.btn-gh-outline:hover:not(.disabled) {
  background: rgba(255,255,255,0.1);
  border-color: #fff;
}

.btn-gh-danger {
  background: transparent;
  border: 1px solid rgba(239, 68, 68, 0.3);
  color: #ef4444;
  padding: 8px 16px;
  border-radius: 8px;
  font-size: 0.85rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}
.btn-gh-danger:hover:not(:disabled) {
  background: rgba(239, 68, 68, 0.15);
  border-color: #ef4444;
}
.btn-gh-danger:disabled {
  opacity: 0.3;
  cursor: not-allowed;
}

.btn-gh-solid {
  background: var(--primary);
  color: #000;
  border: none;
  border-radius: 8px;
  padding: 10px 20px;
  font-size: 0.9rem;
  font-weight: 700;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
}
.btn-gh-solid.small { padding: 8px 16px; font-size: 0.85rem; }
.btn-gh-solid:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 15px rgba(0, 210, 255, 0.4);
}
.btn-gh-text {
  background: transparent;
  color: var(--text-secondary);
  border: none;
  font-weight: 600;
  cursor: pointer;
  padding: 10px 16px;
}
.btn-gh-text.small { padding: 4px 10px; font-size: 0.85rem; }
.btn-gh-text:hover { color: #fff; }

.btn-gh-danger-solid {
  background: #ef4444;
  color: #fff;
  border: none;
  border-radius: 8px;
  font-weight: 700;
  cursor: pointer;
  padding: 10px 20px;
  transition: background 0.2s;
}
.btn-gh-danger-solid:hover { background: #dc2626; }

/* ── Modals ── */
.gh-modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
}
.gh-modal {
  background: var(--bg-surface);
  border: 1px solid rgba(255,255,255,0.1);
  padding: 40px;
  border-radius: 16px;
  width: 90%;
  max-width: 440px;
  box-shadow: 0 20px 60px rgba(0,0,0,0.6);
  animation: modalIn 0.3s ease-out;
}
@keyframes modalIn {
  from { opacity: 0; transform: scale(0.95) translateY(10px); }
  to { opacity: 1; transform: scale(1) translateY(0); }
}
.gh-modal h3 {
  margin: 0 0 16px;
  font-size: 1.25rem;
  font-weight: 800;
}
.gh-modal p {
  color: var(--text-secondary);
  font-size: 0.95rem;
  line-height: 1.5;
  margin: 0 0 16px;
}
.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 32px;
}

/* ── Transitions ── */
.fade-in {
  animation: fadeIn 0.4s ease;
}
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

@media (max-width: 768px) {
  .gh-sidebar {
    position: fixed;
    top: 0;
    left: -280px;
    height: 100vh;
    z-index: 1000;
    transition: left 0.3s ease;
  }
  .gh-sidebar.sidebar-mobile-open {
    left: 0;
  }
}
</style>
