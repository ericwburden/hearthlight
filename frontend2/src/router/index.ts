import Vue from 'vue';
import VueRouter, { RouteConfig } from 'vue-router';
import { configRoutes } from './configure-application-routes';

Vue.use(VueRouter);

const Start = () => import(/* webpackChunkName: "start" */ '../views/Start.vue');
const Home = () => import(/* webpackChunkName: "home" */ '../views/main/Home.vue');

// Admin routes
const AdminDashboard = () => import(/* webpackChunkName: "admin" */ '../views/admin/AdminDashboard.vue');
const ConfigureApplication = () =>
  import(
    /* webpackChunkName: "admin-configure" */
    '../views/admin/config/ConfigureApplication.vue'
  );
const AdminHome = () => import(/* webpackChunkName: "admin-home" */ '../views/admin/home/AdminHome.vue');

const routes: Array<RouteConfig> = [
  {
    path: '/',
    component: Start,
    children: [
      { path: 'home', component: Home },
      {
        path: 'admin',
        component: AdminDashboard,
        children: [
          { path: '/', component: AdminHome },
          { path: 'configure', component: ConfigureApplication, children: configRoutes },
        ],
      },
    ],
  },
  {
    path: '/*',
    redirect: '/',
  },
];

const router = new VueRouter({
  mode: 'history',
  base: process.env.BASE_URL,
  routes,
});

export default router;
