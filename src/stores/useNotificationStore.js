import { defineStore } from 'pinia';
import { db, auth } from '../firebase';
import { 
  collection, 
  query, 
  where, 
  orderBy, 
  onSnapshot, 
  updateDoc, 
  doc, 
  addDoc,
  serverTimestamp,
  deleteDoc
} from 'firebase/firestore';

export const useNotificationStore = defineStore('notifications', {
  state: () => ({
    notifications: [],
    loading: false,
    unsubscribe: null,
  }),
  
  getters: {
    unreadCount: (state) => state.notifications.filter(n => !n.read).length,
    sortedNotifications: (state) => [...state.notifications].sort((a, b) => {
      const timeA = a.createdAt?.seconds || 0;
      const timeB = b.createdAt?.seconds || 0;
      return timeB - timeA;
    })
  },
  
  actions: {
    init() {
      if (this.unsubscribe) {
        this.unsubscribe();
        this.unsubscribe = null;
      }
      
      const user = auth.currentUser;
      if (!user) {
        this.notifications = [];
        return;
      }
      
      this.loading = true;
      
      const q = query(
        collection(db, 'notifications'),
        where('userId', '==', user.uid),
        orderBy('createdAt', 'desc')
      );
      
      this.unsubscribe = onSnapshot(q, (snapshot) => {
        const notifs = [];
        snapshot.forEach((doc) => {
          notifs.push({ id: doc.id, ...doc.data() });
        });
        this.notifications = notifs;
        this.loading = false;
      }, (error) => {
        console.error("Error listening to notifications:", error);
        this.loading = false;
      });
    },
    
    stopListening() {
      if (this.unsubscribe) {
        this.unsubscribe();
        this.unsubscribe = null;
      }
      this.notifications = [];
    },
    
    async markAsRead(notificationId) {
      try {
        const ref = doc(db, 'notifications', notificationId);
        await updateDoc(ref, { read: true });
      } catch (error) {
        console.error("Error marking notification as read:", error);
      }
    },
    
    async markAllAsRead() {
      try {
        const unread = this.notifications.filter(n => !n.read);
        const promises = unread.map(n => updateDoc(doc(db, 'notifications', n.id), { read: true }));
        await Promise.all(promises);
      } catch (error) {
        console.error("Error marking all as read:", error);
      }
    },

    async deleteNotification(notificationId) {
      try {
        await deleteDoc(doc(db, 'notifications', notificationId));
      } catch (error) {
        console.error("Error deleting notification:", error);
      }
    },
    
    // Helper to create a notification (can be called from admin or triggered internally)
    async createNotification(userId, title, message, type = 'system', link = null) {
      try {
        await addDoc(collection(db, 'notifications'), {
          userId,
          title,
          message,
          type,
          link,
          read: false,
          createdAt: serverTimestamp()
        });
      } catch (error) {
        console.error("Error creating notification:", error);
      }
    }
  }
});
