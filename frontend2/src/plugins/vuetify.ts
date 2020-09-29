import Vue from "vue";
import Vuetify from "vuetify/lib";
import "@mdi/font/css/materialdesignicons.css";
import HearthlightIcon from "@/components/HearthlightIcon.vue";

Vue.use(Vuetify);

export default new Vuetify({
  theme: {
    themes: {
      light: {
        primary: "#d27019",
        secondary: "#ababab",
        accent: "#ffbd82",
        success: "#519554",
        info: "#268ada",
        warning: "#dbaa17",
        error: "#ec5050",
      },
    },
  },
  icons: {
    values: {
      hearthlight: {
        component: HearthlightIcon,
      },
    },
  },
});
