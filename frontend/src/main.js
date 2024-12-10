import { createApp } from "vue";
import App from "./App.vue";
import CoreuiVue from "@coreui/vue";
import { CIcon } from "@coreui/icons-vue";
import "@coreui/coreui/dist/css/coreui.min.css";

const app = createApp(App);

app.use(CoreuiVue);
app.component("CIcon", CIcon);

app.mount("#app");
