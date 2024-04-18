import Vue from "vue";
import VueRouter from "vue-router";
import RouterPrefetch from "vue-router-prefetch";
import App from "./App";
import router from "./router/index";
import { BootstrapVue, IconsPlugin } from 'bootstrap-vue'
// Import Bootstrap and BootstrapVue CSS files (order is important)
import 'bootstrap/dist/css/bootstrap.css'
import 'bootstrap-vue/dist/bootstrap-vue.css'
import mainSID from "./plugins/mainSID";

Vue.use(BootstrapVue)

Vue.use(IconsPlugin)
Vue.use(mainSID);
Vue.use(VueRouter);
Vue.use(RouterPrefetch);

new Vue({
    router,
    render: (h) => h(App),
}).$mount("#app");
