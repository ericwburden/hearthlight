<template>
  <router-view></router-view>
</template>

<script lang="ts">
import { Component, Vue } from 'vue-property-decorator';
import { Route } from 'vue-router';
import { store } from '@/store';
import { dispatchCheckLoggedIn } from '@/store/main/actions';
import { readIsLoggedIn, readHasAdminAccess } from '@/store/main/getters';

const startRouteGuard = async (to: Route, from: Route, next: Function) => {
  await dispatchCheckLoggedIn(store);
  if (readIsLoggedIn(store)) {
    if (readHasAdminAccess(store)) {
      if (to.path === '/' || to.path === '/home') {
        next('/admin');
      } else {
        next();
      }
    } else {
      if (to.path === '/' || to.path === '/home') {
        next('/user');
      } else {
        next();
      }
    }
  } else if (readIsLoggedIn(store) === false) {
    if (to.path === '/' || (to.path as string).startsWith('/main')) {
      next('/home');
    } else {
      next();
    }
  }
};

@Component
export default class Start extends Vue {
  public beforeRouteEnter(to: Route, from: Route, next: Function) {
    startRouteGuard(to, from, next);
  }

  public beforeRouteUpdate(to: Route, from: Route, next: Function) {
    startRouteGuard(to, from, next);
  }
}
</script>
