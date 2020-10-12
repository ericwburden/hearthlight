<template>
  <div>
    <v-app-bar
      app
      dark
      flat
      dense
      absolute
      prominent
      shrink-on-scroll
      fade-img-on-scroll
      color="primary"
      :src="require('../../assets/img/boots-fireplace-1600-1000.jpg')"
      scroll-target="#scroll-target"
    >
      <template v-slot:img="{ props }">
        <v-img v-bind="props" gradient="to top right, rgba(210,112,25,.7), rgba(255,189,130,.7)"></v-img>
      </template>
      <v-app-bar-nav-icon>
        <v-icon large>$vuetify.icons.hearthlight</v-icon>
      </v-app-bar-nav-icon>

      <v-toolbar-title>Administration Panel</v-toolbar-title>
      <v-spacer></v-spacer>
      <v-btn icon @click="logout"><v-icon>mdi-logout</v-icon></v-btn>

      <template v-slot:extension>
        <v-tabs align-with-title icons-and-text show-arrows>
          <v-tab to="/admin">Home<v-icon>mdi-home</v-icon></v-tab>
          <v-tab to="/admin/configure">Configure<v-icon>mdi-hammer-wrench</v-icon></v-tab>
          <v-tab to="/admin/nodes">Nodes<v-icon>mdi-family-tree</v-icon></v-tab>
          <v-tab to="/admin/user-groups">User Groups<v-icon>mdi-lock-open</v-icon></v-tab>
          <v-tab to="/admin/users">Users<v-icon>mdi-account-multiple</v-icon></v-tab>
          <v-tab>Interfaces<v-icon>mdi-book-information-variant</v-icon></v-tab>
        </v-tabs>
      </template>
    </v-app-bar>

    <v-sheet id="scroll-target" class="overflow-y-auto" max-height="97vh">
      <v-main><router-view></router-view></v-main>
    </v-sheet>

    <v-footer color="primary" app>
      <span class="white--text"> hearthlight.app &copy; {{ new Date().getFullYear() }} </span>
    </v-footer>
  </div>
</template>

<script lang="ts">
import { Component, Vue } from 'vue-property-decorator';
import { dispatchLogOut } from '@/store/main/actions';

@Component({
  components: {},
})
export default class AdminDashboard extends Vue {
  public logout() {
    dispatchLogOut(this.$store);
  }
}
</script>
