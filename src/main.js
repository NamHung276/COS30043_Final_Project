// src/main.js
import { createApp } from 'vue'
import './style.css'
import App from './App.vue'
import router from './router'

import 'bootstrap/dist/css/bootstrap.min.css'
import 'bootstrap/dist/js/bootstrap.bundle.min.js'

// Replace the following line with the code below if "import 'bootstrap/dist/js/bootstrap.bundle.min.js'" does not work
// import * as bootstrap from 'bootstrap'
// window.bootstrap = bootstrap


import lazyImg from './directives/lazyImg'

const app = createApp(App)

app.use(router)
app.directive('lazy-img', lazyImg)

app.mount('#app')