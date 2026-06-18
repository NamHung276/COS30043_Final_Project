import { initializeApp } from 'firebase/app'
import { getAuth } from 'firebase/auth'
import { getFirestore } from 'firebase/firestore'

const firebaseConfig = {
  apiKey: "AIzaSyDiaKrI7LeZ6UILnYXpUYgJmgT5w6XSjqo",
  authDomain: "gamehub-b2b01.firebaseapp.com",
  projectId: "gamehub-b2b01",
  storageBucket: "gamehub-b2b01.firebasestorage.app",
  messagingSenderId: "603569179089",
  appId: "1:603569179089:web:798b68b0bf1c92e81df8f0"
}

const app = initializeApp(firebaseConfig)

export const auth = getAuth(app)
export const db = getFirestore(app)