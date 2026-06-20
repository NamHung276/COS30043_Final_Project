// src/components/LikeButton.vue
<script>
import { auth, db } from '../firebase'
import { onAuthStateChanged } from 'firebase/auth'
import {
  collection,
  query,
  where,
  getDocs,
  addDoc,
  deleteDoc,
  doc
} from 'firebase/firestore'

export default {
  name: 'LikeButton',

  props: {
    articleId: {
      type: [String, Number],
      required: true
    }
  },

  data() {
    return {
      currentUser: null,
      likeCount: 0,
      userLikeDocId: null, // Firestore doc id of the current user's like, if any
      loading: true
    }
  },

  computed: {
    isLiked() {
      return this.userLikeDocId !== null
    }
  },

  watch: {
    // Re-run if the component is reused for a different article (e.g. v-for list)
    articleId() {
      this.loadLikes()
    }
  },

  methods: {
    async loadLikes() {
      this.loading = true

      const likesQuery = query(
        collection(db, 'likes'),
        where('articleId', '==', this.articleId)
      )

      const snapshot = await getDocs(likesQuery)

      this.likeCount = snapshot.size
      this.userLikeDocId = null

      if (this.currentUser) {
        const myLike = snapshot.docs.find(
          docSnap => docSnap.data().userId === this.currentUser.uid
        )
        if (myLike) {
          this.userLikeDocId = myLike.id
        }
      }

      this.loading = false
    },

    async toggleLike() {
      if (!this.currentUser) {
        this.$router.push('/login')
        return
      }

      try {
        if (this.isLiked) {
          // Unlike
          await deleteDoc(doc(db, 'likes', this.userLikeDocId))
          this.userLikeDocId = null
          this.likeCount--
        } else {
          // Like
          const newLike = await addDoc(collection(db, 'likes'), {
            articleId: this.articleId,
            userId: this.currentUser.uid
          })
          this.userLikeDocId = newLike.id
          this.likeCount++
        }
      } catch (error) {
        console.error('Failed to toggle like:', error)
      }
    }
  },

  mounted() {
    onAuthStateChanged(auth, (user) => {
      this.currentUser = user
      this.loadLikes()
    })
  }
}
</script>

<template>
  <button
    class="btn btn-sm like-button"
    :class="isLiked ? 'btn-danger' : 'btn-outline-danger'"
    :disabled="loading"
    @click.stop="toggleLike"
  >
    <span v-if="isLiked">❤️</span>
    <span v-else>🤍</span>
    {{ likeCount }}
  </button>
</template>