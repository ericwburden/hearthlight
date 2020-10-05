import Vue from 'vue';
import VueRouter, { RouteConfig } from 'vue-router';

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

const ConfigureNodeForm = () =>
  import(
    /* webpackChunkName: "admin-configure-node" */
    '../views/admin/config/form/ConfigureNodeForm.vue'
  );

const NodeCreate = () =>
  import(
    /* webpackChunkName: "admin-configure-node-create" */
    '../views/admin/config/form/NodeCreate.vue'
  );

const NodeSearchForm = () =>
  import(
    /* webpackChunkName: "admin-configure-node-search" */
    '../views/admin/config/form/NodeSearchForm.vue'
  );

const UserGroupCreate = () =>
  import(
    /* webpackChunkName: "admin-configure-user-group-create" */
    '../views/admin/config/form/UserGroupCreate.vue'
  );

const UserGroupUpdate = () =>
  import(
    /* webpackChunkName: "admin-configure-user-group-update" */
    '../views/admin/config/form/UserGroupUpdate.vue'
  );

const ConfirmDelete = () =>
  import(/* webpackChunkName: "admin-configure" */ '../views/admin/config/form/ConfirmDelete.vue');

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
            children: [
              { path: 'node/:id/add-child-node', name: 'admin.configure.node.add-child-node', component: NodeCreate },
              { path: 'node/:uuid', name: 'admin.configure.node', component: ConfigureNodeForm },
              { path: 'node/:id/child-search', name: 'admin.configure.node.search', component: NodeSearchForm },
              { path: ':type/:id/delete', name: 'admin.configure.delete', component: ConfirmDelete },
              {
                path: 'node/:id/add-user-group',
                name: 'admin.configure.node.add-user-group',
                component: UserGroupCreate,
              },
              {
                path: 'user-group/:id/update',
                name: 'admin.configure.user-group.update',
                component: UserGroupUpdate,
              },
            ],
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
