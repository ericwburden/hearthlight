import Vue from 'vue';
import VueRouter, { RouteConfig } from 'vue-router';

Vue.use(VueRouter);

const Start = () => import(/* webpackChunkName: "start" */ '../views/Start.vue');
const Home = () => import(/* webpackChunkName: "home" */ '../views/main/Home.vue');

// Admin routes
const AdminDashboard = () => import(/* webpackChunkName: "admin" */ '../views/admin/AdminDashboard.vue');
const ConfigureApplication = () =>
  import(/* webpackChunkName: "admin-configure" */ '../views/admin/ConfigureApplication.vue');
const ConfigureNodeForm = () =>
  import(/* webpackChunkName: "admin-configure-node" */ '@/components/forms/ConfigureNodeForm.vue');

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
          {
            path: 'configure',
            name: 'admin.configure',
            component: ConfigureApplication,
            children: [{ path: 'node/:uuid', name: 'admin.configure.node', component: ConfigureNodeForm }],
          },
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
