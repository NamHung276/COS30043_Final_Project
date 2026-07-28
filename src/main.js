import { createApp } from "vue";
import { createPinia } from "pinia";
import App from "./App.vue";
import router from "./router";

import "bootstrap/dist/css/bootstrap.min.css";
import "bootstrap/dist/js/bootstrap.bundle.min.js";
import "./style.css";

import lazyImg from "./directives/lazyImg";

const app = createApp(App);
const pinia = createPinia();

app.use(pinia);
app.use(router);
app.directive("lazy-img", lazyImg);

app.mount("#app");
