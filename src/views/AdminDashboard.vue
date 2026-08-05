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
  where,
  setDoc
} from "firebase/firestore";
import { Star, Newspaper, Users, Database } from "@lucide/vue";
import { backendApi } from "../services/api";
import { useNotificationStore } from "../stores/useNotificationStore";

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
      isSubmitting: false,

      // Confirmation modals
      confirmDelete: null,
      confirmRole: null,
      confirmBan: null,

      // Pagination
      lastUserDoc: null,
      hasMoreUsers: false,
      lastPostDoc: null,
      hasMorePosts: false,

      // AI Health
      aiHealth: null,
      loadingAiHealth: false,

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
        news: this.posts.filter(p => p.createdAt?.seconds > (Date.now()/1000 - 86400)).length,
        users: this.users.filter(u => u.createdAt?.seconds > (Date.now()/1000 - 86400)).length
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
        this.loadReports(),
        this.loadAiHealth()
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
    
    async loadAiHealth() {
      this.loadingAiHealth = true;
      try {
        const { data } = await backendApi.get("/admin/ai-health");
        this.aiHealth = data;
      } catch (e) {
        console.error("Failed to load AI health data", e);
        this.aiHealth = { status: "error", analysis: "Could not fetch AI Health Report. Check server connection." };
      } finally {
        this.loadingAiHealth = false;
      }
    },
    
    async testSendNotification(type) {
      if (!this.currentUser) return;
      const store = useNotificationStore();
      
      try {
        if (type === 'wishlist') {
          await store.createNotification(
            this.currentUser.uid,
            'Wishlist Alert!',
            'A game on your wishlist is now on sale for 50% off.',
            'wishlist',
            '/favorites'
          );
        } else if (type === 'system') {
          await store.createNotification(
            this.currentUser.uid,
            'System Maintenance',
            'GameHub will undergo scheduled maintenance at 2 AM PST.',
            'system',
            '/'
          );
        } else if (type === 'social') {
          await store.createNotification(
            this.currentUser.uid,
            'New Friend Request',
            'GamerGirl99 wants to be your friend.',
            'social',
            '/profile'
          );
        }
        this.toast.show(`Sent test ${type} notification to yourself!`, "success");
      } catch (err) {
        console.error(err);
        this.toast.show("Failed to send notification.", "error");
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
          return {
            uid: d.id,
            ...data,
            articleCount: "—",
            reviewCount: "—",
            mockStatus: data.status || "Active"
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
      if (!this.confirmDelete || this.isSubmitting) return;
      this.isSubmitting = true;
      try {
        await updateDoc(doc(db, "news", this.confirmDelete.id), { status: "deleted" });
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
        this.isSubmitting = false;
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
      if (!this.confirmRole || this.isSubmitting) return;
      this.isSubmitting = true;
      try {
        // Use setDoc with merge instead of updateDoc to handle older accounts
        // that might only exist in Firebase Auth but not yet in the Firestore users collection.
        await setDoc(doc(db, "users", this.confirmRole.uid), {
          role: this.confirmRole.newRole,
        }, { merge: true });
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
        this.isSubmitting = false;
      }
    },

    askBanUser(user) {
      this.confirmBan = {
        uid: user.uid,
        displayName: user.displayName || user.email,
        isBanned: user.mockStatus === 'Banned'
      };
    },

    async confirmBanAction() {
      if (!this.confirmBan || this.isSubmitting) return;
      this.isSubmitting = true;
      try {
        const newStatus = this.confirmBan.isBanned ? 'Active' : 'Banned';
        await setDoc(doc(db, "users", this.confirmBan.uid), {
          status: newStatus
        }, { merge: true });
        const u = this.users.find((u) => u.uid === this.confirmBan.uid);
        if (u) u.mockStatus = newStatus;
        
        this.toast.show(`User account has been ${newStatus.toLowerCase()}.`, "success");
        
        this.recentActivity.unshift({
          id: Date.now(),
          action: `${newStatus === 'Banned' ? 'Banned' : 'Unbanned'} user: ${this.confirmBan.displayName}`,
          time: "Just now",
          type: newStatus === 'Banned' ? 'delete' : 'approve'
        });
        if(this.recentActivity.length > 5) this.recentActivity.pop();

      } catch (e) {
        console.error(e);
        this.toast.show("Failed to update user status.", "error");
      } finally {
        this.confirmBan = null;
        this.isSubmitting = false;
      }
    },

    actionComingSoon(actionName) {
      this.toast.show(`Coming in Version 2`, "info");
    },

    async reportAction(id, actionStr, target) {
      try {
        const report = this.reportedItems.find(r => r.id === id);
        if (!report) return;

        if (actionStr === "View") {
          if (report.type === "Article") {
            this.$router.push(`/gamehub-news/${report.targetId}`);
          } else if (report.type === "Review") {
            this.$router.push(`/games/${report.gameId}`);
          } else {
            this.toast.show("Cannot view this type of content directly.", "info");
          }
          return; // Do not delete the report
        }

        if (actionStr === "Delete") {
          if (report.type === "Article") {
            await updateDoc(doc(db, "news", report.targetId), { status: "deleted" });
          } else if (report.type === "Review") {
            await updateDoc(doc(db, "reviews", report.targetId), { status: "deleted" });
          }
        }
        
        // Both Dismiss and Delete will remove the report itself
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
  <div class="admin-page" v-if="isAdmin">
    <div class="container py-5">
      <!-- Header -->
      <div class="mb-5 d-flex justify-content-between align-items-center flex-wrap gap-3">
        <div>
          <h1 class="admin-page-title display-5 fw-bold mb-2">Operations Center</h1>
          <p class="text-muted-light m-0">Manage community feed, players, flagged content, and platform activity.</p>
        </div>
        <div class="d-flex align-items-center gap-3">
           <div class="admin-profile profile-glass-card p-2 px-3 rounded-pill d-flex align-items-center gap-3">
             <div class="admin-avatar text-primary fs-3"><i class="bi bi-shield-fill"></i></div>
             <div class="admin-info d-flex flex-column pe-2">
               <span class="admin-user fw-bold m-0" style="font-size:0.95rem;">{{ currentUser?.email }}</span>
               <span class="admin-badge text-primary" style="font-size:0.65rem; font-weight:800; text-transform:uppercase">Administrator</span>
             </div>
           </div>
        </div>
      </div>

      <div class="row g-4">
        <!-- ── Sidebar ── -->
        <div class="col-lg-3">
          <aside class="gh-sidebar profile-glass-card p-3 h-100">
            <div class="sidebar-section-title">Moderation</div>
            <nav class="sidebar-nav">
              <button class="nav-btn" :class="{ active: activeTab === 'dashboard' }" @click="activeTab = 'dashboard'">
                <i class="bi bi-grid-fill me-3"></i> 
                <span>Dashboard</span>
              </button>
              <button class="nav-btn" :class="{ active: activeTab === 'reviews' }" @click="activeTab = 'reviews'">
                <i class="bi bi-flag-fill me-3"></i> 
                <span>Queue</span>
                <span class="nav-badge ms-auto" v-if="badgeCounts.reports > 0">{{ badgeCounts.reports }}</span>
              </button>
              <button class="nav-btn" :class="{ active: activeTab === 'news' }" @click="activeTab = 'news'">
                <i class="bi bi-newspaper me-3"></i> 
                <span>Feed</span>
                <span class="nav-badge ms-auto" v-if="badgeCounts.news > 0">{{ badgeCounts.news }}</span>
              </button>
              <button class="nav-btn" :class="{ active: activeTab === 'users' }" @click="activeTab = 'users'">
                <i class="bi bi-people-fill me-3"></i> 
                <span>Players</span>
                <span class="nav-badge ms-auto" v-if="badgeCounts.users > 0">{{ badgeCounts.users }}</span>
              </button>
            </nav>
          </aside>
        </div>

        <!-- ── Main Content Area ── -->
        <div class="col-lg-9">
          <div class="content-container">
        
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

          <!-- Middle Row: Reports & AI Health -->
          <div class="dashboard-grid mt-4">
            <!-- Moderation Queue Widget -->
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

            <!-- AI Health Widget -->
            <div class="gh-widget">
              <div class="widget-header">
                <div class="d-flex align-items-center gap-3">
                  <h3 class="mb-0"><i class="bi bi-cpu-fill text-primary"></i> AI Health Monitor</h3>
                  <span class="badge bg-primary rounded-pill px-2 py-1" style="font-size: 0.7rem;">Gemini Pro</span>
                </div>
                <button class="btn btn-outline-primary btn-sm rounded-pill" @click="loadAiHealth">
                  <i class="bi bi-arrow-clockwise" :class="{'spin-anim': loadingAiHealth}"></i> Refresh
                </button>
              </div>
              <div class="widget-body">
                <div v-if="loadingAiHealth" class="d-flex flex-column align-items-center justify-content-center p-4">
                  <div class="spinner-border text-primary mb-3" role="status"></div>
                  <p class="text-muted small">Gemini is analyzing system metrics...</p>
                </div>
                <div v-else-if="aiHealth" class="ai-health-content">
                  <div class="alert" :class="aiHealth.status === 'healthy' ? 'alert-success border-success' : 'alert-warning border-warning'" style="background: rgba(0,0,0,0.2);">
                    <div class="d-flex align-items-center gap-2 mb-2">
                      <i class="bi fs-5" :class="aiHealth.status === 'healthy' ? 'bi-check-circle-fill text-success' : 'bi-exclamation-triangle-fill text-warning'"></i>
                      <strong class="text-white">AI Analysis Report</strong>
                    </div>
                    <p class="mb-0 text-muted-light" style="font-size: 0.9rem; line-height: 1.5;">{{ aiHealth.analysis }}</p>
                  </div>
                  <div class="metrics-grid mt-3 d-flex gap-3">
                    <div class="metric-box bg-dark p-2 rounded flex-fill text-center border border-secondary border-opacity-25">
                      <div class="text-muted" style="font-size: 0.7rem; text-transform: uppercase;">CPU</div>
                      <div class="fw-bold fs-5 text-white" :class="{'text-danger': aiHealth.metrics?.cpu_usage_percent > 85}">{{ aiHealth.metrics?.cpu_usage_percent || 0 }}%</div>
                    </div>
                    <div class="metric-box bg-dark p-2 rounded flex-fill text-center border border-secondary border-opacity-25">
                      <div class="text-muted" style="font-size: 0.7rem; text-transform: uppercase;">Memory</div>
                      <div class="fw-bold fs-5 text-white" :class="{'text-danger': aiHealth.metrics?.memory_usage_percent > 85}">{{ aiHealth.metrics?.memory_usage_percent || 0 }}%</div>
                    </div>
                    <div class="metric-box bg-dark p-2 rounded flex-fill text-center border border-secondary border-opacity-25">
                      <div class="text-muted" style="font-size: 0.7rem; text-transform: uppercase;">Error Rate</div>
                      <div class="fw-bold fs-5 text-white" :class="{'text-danger': aiHealth.metrics?.error_rate_percent > 3}">{{ aiHealth.metrics?.error_rate_percent || 0 }}%</div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Test Notifications Widget -->
          <div class="gh-widget mt-4">
            <div class="widget-header">
              <div class="d-flex align-items-center gap-3">
                <h3 class="mb-0"><i class="bi bi-bell-fill text-info"></i> Notification System (Test)</h3>
                <span class="gh-badge badge-neutral">V2 Planned</span>
              </div>
            </div>
            <div class="widget-body">
              <p class="text-muted small mb-3">Trigger mock notifications to test the navbar bell integration. These will be sent to your own account.</p>
              <div class="d-flex flex-wrap gap-2">
                <button class="btn btn-outline-danger btn-sm" @click="testSendNotification('wishlist')">
                  <i class="bi bi-heart-fill me-1"></i> Trigger Wishlist Alert
                </button>
                <button class="btn btn-outline-primary btn-sm" @click="testSendNotification('social')">
                  <i class="bi bi-people-fill me-1"></i> Trigger Social Alert
                </button>
                <button class="btn btn-outline-info btn-sm" @click="testSendNotification('system')">
                  <i class="bi bi-info-circle-fill me-1"></i> Trigger System Alert
                </button>
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
                <caption class="visually-hidden">List of published news articles and their statuses</caption>
                <thead>
                  <tr>
                    <th scope="col">Article</th>
                    <th scope="col">Author</th>
                    <th scope="col">Status</th>
                    <th scope="col">Published Date</th>
                    <th scope="col" class="text-end">Actions</th>
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
                      <button class="btn-gh-outline me-2" @click="$router.push(`/gamehub-news/${post.id}`)">View</button>
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
                <caption class="visually-hidden">List of registered players, their activity, and account status</caption>
                <thead>
                  <tr>
                    <th scope="col">Player</th>
                    <th scope="col">Email</th>
                    <th scope="col">Articles</th>
                    <th scope="col">Reviews</th>
                    <th scope="col">Status</th>
                    <th scope="col" class="text-end">Management</th>
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
                    <td class="muted-col">{{ u.articleCount }}</td>
                    <td class="muted-col">{{ u.reviewCount }}</td>
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
                      <div v-else class="d-flex justify-content-end gap-2">
                        <button 
                          v-if="u.role !== 'admin'" 
                          class="btn-gh-outline" 
                          @click="askChangeRole(u, 'admin')">
                          Promote
                        </button>
                        <button 
                          v-else 
                          class="btn-gh-outline text-warning border-warning" 
                          @click="askChangeRole(u, 'user')">
                          Revoke
                        </button>
                        
                        <button 
                          v-if="u.mockStatus === 'Banned'"
                          class="btn-gh-outline text-success border-success" 
                          @click="askBanUser(u)">
                          Unban
                        </button>
                        <button 
                          v-else
                          class="btn-gh-danger" 
                          @click="askBanUser(u)">
                          Ban
                        </button>
                      </div>
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
      </div>
    </div>
  </div>
    <!-- ── MODALS ── -->
    
    <!-- Delete Post Modal -->
    <div class="gh-modal-overlay" v-if="confirmDelete">
      <div class="gh-modal">
        <h3 class="text-danger"><i class="bi bi-exclamation-triangle-fill"></i> Remove Article</h3>
        <p>Are you sure you want to permanently delete the article <strong>"{{ confirmDelete.title }}"</strong>?</p>
        <p class="text-muted small">This action removes the post from the Community Feed. It cannot be undone.</p>
        <div class="modal-actions">
          <button class="btn-gh-text" @click="confirmDelete = null">Cancel</button>
          <button class="btn-gh-danger-solid" @click="confirmDeletePost" :disabled="isSubmitting">Delete Article</button>
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
          <button :class="confirmRole.newRole === 'admin' ? 'btn-gh-solid' : 'btn-gh-danger-solid'" @click="confirmChangeRole" :disabled="isSubmitting">Confirm Change</button>
        </div>
      </div>
    </div>

    <!-- Ban User Modal -->
    <div class="gh-modal-overlay" v-if="confirmBan">
      <div class="gh-modal">
        <h3 :class="confirmBan.isBanned ? 'text-success' : 'text-danger'">
          <i class="bi" :class="confirmBan.isBanned ? 'bi-person-check-fill' : 'bi-person-x-fill'"></i>
          {{ confirmBan.isBanned ? 'Unban User' : 'Ban User' }}
        </h3>
        <p>
          Are you sure you want to {{ confirmBan.isBanned ? 'unban' : 'ban' }} 
          <strong>{{ confirmBan.displayName }}</strong>?
        </p>
        <p class="text-muted small" v-if="!confirmBan.isBanned">They will immediately lose access to their account and all GameHub features.</p>
        <p class="text-muted small" v-else>They will regain full access to their account.</p>
        <div class="modal-actions">
          <button class="btn-gh-text" @click="confirmBan = null">Cancel</button>
          <button :class="confirmBan.isBanned ? 'btn-gh-solid' : 'btn-gh-danger-solid'" @click="confirmBanAction" :disabled="isSubmitting">
            {{ confirmBan.isBanned ? 'Confirm Unban' : 'Confirm Ban' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* ── Variables & Reset ── */
.admin-page {
  min-height: 100vh;
  background: var(--bg-deep);
  color: var(--text-primary);
  font-family: var(--font-family);
  -webkit-font-smoothing: antialiased;
}

.admin-page-title {
  color: var(--text-primary) !important;
}

.text-muted-light {
  color: var(--overlay-text) !important;
}

.profile-glass-card {
  background: var(--bg-glass);
  border: 1px solid var(--border-glass);
  border-radius: 16px;
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  box-shadow: var(--shadow-sm);
}

.gh-sidebar {
  border-radius: 20px;
}

.sidebar-section-title {
  padding: 12px 20px 8px;
  font-size: 0.7rem;
  font-weight: 800;
  color: var(--overlay-text-muted);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.sidebar-nav {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.nav-btn {
  display: flex;
  align-items: center;
  width: 100%;
  padding: 12px 20px;
  background: transparent;
  border: none;
  border-radius: 12px;
  color: var(--text-primary);
  font-weight: 500;
  text-align: left;
  transition: all 0.2s ease;
}

.nav-btn i {
  font-size: 1.1rem;
  opacity: 0.7;
  transition: opacity 0.2s;
}

.nav-badge {
  background: #ef4444;
  color: #fff;
  font-size: 0.7rem;
  font-weight: 800;
  padding: 2px 8px;
  border-radius: 12px;
}

.nav-btn:hover {
  background: var(--overlay-light);
}

.nav-btn.active {
  background: rgba(124, 58, 237, 0.15);
  color: var(--primary-light);
  font-weight: 600;
}

.nav-btn.active i {
  color: var(--primary-light);
  opacity: 1;
}

@media (max-width: 991.98px) {
  .gh-sidebar {
    display: flex;
    overflow-x: auto;
    padding: 10px !important;
    white-space: nowrap;
    scrollbar-width: none;
    margin-bottom: 20px;
  }
  .gh-sidebar::-webkit-scrollbar {
    display: none;
  }
  .sidebar-section-title {
    display: none;
  }
  .sidebar-nav {
    flex-direction: row;
    gap: 8px;
  }
  .nav-btn {
    width: auto;
    margin-bottom: 0;
    padding: 10px 16px;
  }
}

.pane-header {
  margin-bottom: 32px;
}
.pane-title {
  font-size: 2.2rem;
  font-weight: 800;
  color: var(--text-primary);
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
  display: flex;
  align-items: center;
  gap: 20px;
  padding: 24px;
  background: var(--bg-glass);
  border: 1px solid var(--border-glass);
  border-radius: 16px;
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  transition: transform 0.2s, box-shadow 0.2s;
}
.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 12px 30px rgba(0,0,0,0.2);
}
.stat-icon {
  width: 50px;
  height: 50px;
  border-radius: 12px;
  background: var(--overlay-light);
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
  color: var(--text-primary);
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
  background: var(--overlay-light);
  border: 1px solid var(--overlay-medium);
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
  color: var(--text-primary);
  width: 100%;
}
.filter-pills {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}
.filter-pill {
  background: var(--overlay-light);
  border: 1px solid var(--overlay-medium);
  color: var(--text-secondary);
  padding: 8px 16px;
  border-radius: 20px;
  font-size: 0.85rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}
.filter-pill:hover, .filter-pill.active {
  background: rgba(124, 58, 237, 0.15);
  border-color: var(--primary);
  color: var(--text-primary);
}

/* ── Widgets ── */
.dashboard-grid {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 24px;
}
@media (max-width: 950px) {
  .dashboard-grid { grid-template-columns: 1fr; }
}

.gh-widget {
  background: var(--bg-glass);
  border: 1px solid var(--border-glass);
  border-radius: 16px;
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  overflow: hidden;
  margin-bottom: 24px;
}
.widget-header {
  padding: 24px 32px;
  border-bottom: 1px solid var(--overlay-light);
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: rgba(0,0,0,0.05);
}
.widget-header h3 {
  font-size: 1.1rem;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0;
  display: flex;
  align-items: center;
  gap: 10px;
}
.badge-count {
  background: rgba(124, 58, 237, 0.15);
  color: var(--primary-light);
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
  background: var(--overlay-light);
  padding: 20px 24px;
  border-radius: 12px;
  border: 1px solid var(--overlay-medium);
  transition: background 0.2s, border-color 0.2s;
}
.report-item:hover {
  background: var(--overlay-medium);
  border-color: var(--overlay-heavy);
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
  background: var(--overlay-medium);
  padding: 3px 8px;
  border-radius: 4px;
  color: var(--text-primary);
}
.rep-time { font-size: 0.8rem; color: var(--text-muted); }
.report-text { font-size: 1.05rem; color: var(--text-primary); }
.report-user { font-size: 0.85rem; color: var(--text-secondary); }

.report-actions-extended {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

/* Quick Actions */
.qa-btn {
  background: var(--overlay-light);
  color: var(--text-primary);
  border: 1px solid var(--overlay-light);
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
  background: rgba(124, 58, 237, 0.1); 
  border-color: rgba(124, 58, 237, 0.3);
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
  background: var(--overlay-light);
  border-radius: 12px;
  border-left: 3px solid var(--overlay-medium);
}
.act-icon {
  width: 40px; height: 40px; border-radius: 50%;
  display: flex; align-items: center; justify-content: center; font-size: 1.2rem;
}
.act-type-delete { background: rgba(239,68,68,0.1); color: #ef4444; border: 1px solid rgba(239,68,68,0.2); }
.act-type-approve { background: rgba(34,197,94,0.1); color: #22c55e; border: 1px solid rgba(34,197,94,0.2); }
.act-type-promote { background: rgba(245,158,11,0.1); color: #f59e0b; border: 1px solid rgba(245,158,11,0.2); }
.act-type-signup { background: rgba(56,189,248,0.1); color: #38bdf8; border: 1px solid rgba(56,189,248,0.2); }
.act-content { font-size: 0.95rem; color: var(--text-primary); flex: 1; }
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
  border-bottom: 1px solid var(--overlay-light);
  background: rgba(0,0,0,0.05);
}
.gh-table td {
  padding: 24px 32px;
  border-bottom: 1px solid var(--overlay-light);
  font-size: 0.95rem;
}
.gh-table tr:hover td {
  background: var(--overlay-light);
}
.row-highlight td {
  background: rgba(124, 58, 237, 0.04);
}
.primary-col { color: var(--text-primary); }
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
.user-av { background: var(--overlay-medium); color: var(--text-primary); }

.article-thumb {
  width: 48px;
  height: 48px;
  background: rgba(0,0,0,0.15);
  border: 1px solid var(--overlay-medium);
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
.badge-primary { background: rgba(124, 58, 237, 0.15); color: var(--primary-light); border: 1px solid rgba(124, 58, 237, 0.3); }
.badge-neutral { background: var(--overlay-medium); color: var(--text-muted); }
.badge-danger { background: rgba(239, 68, 68, 0.1); color: #ef4444; border: 1px solid rgba(239, 68, 68, 0.3); }
.badge-success { background: rgba(34, 197, 94, 0.15); color: #4ade80; border: 1px solid rgba(34, 197, 94, 0.3); }

/* Buttons */
.btn-gh-outline {
  background: transparent;
  border: 1px solid var(--overlay-heavy);
  color: var(--text-primary);
  padding: 8px 16px;
  border-radius: 8px;
  font-size: 0.85rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}
.btn-gh-outline:hover:not(.disabled) {
  background: var(--overlay-medium);
  border-color: var(--text-primary);
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
  color: #fff;
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
  box-shadow: 0 4px 15px rgba(124, 58, 237, 0.4);
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
.btn-gh-text:hover { color: var(--text-primary); }

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
  background: rgba(0,0,0,0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1050;
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
}
.gh-modal {
  background: var(--bg-surface);
  border: 1px solid var(--overlay-medium);
  padding: 40px;
  border-radius: 16px;
  width: 90%;
  max-width: 440px;
  box-shadow: 0 20px 60px rgba(0,0,0,0.4);
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
</style>
