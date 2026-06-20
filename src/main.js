// src/main.js
import { createApp } from 'vue'
import './style.css'
import App from './App.vue'
import router from './router'

import 'bootstrap/dist/css/bootstrap.min.css'
import 'bootstrap/dist/js/bootstrap.bundle.min.js'

import lazyImg from './directives/lazyImg'

const app = createApp(App)

app.use(router)
app.directive('lazy-img', lazyImg)

app.mount('#app')