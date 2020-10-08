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

const NodeCreate = () =>
  import(
    /* webpackChunkName: "admin-configure-node-create" */
    '../views/admin/config/form/NodeCreate.vue'
  );

const NodeUpdate = () =>
  import(
    /* webpackChunkName: "admin-configure-node-update" */
    '../views/admin/config/form/NodeUpdate.vue'
  );

const NodeSearch = () =>
  import(
    /* webpackChunkName: "admin-configure-node-search" */
    '../views/admin/config/form/NodeSearch.vue'
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

const UserGroupSearch = () =>
  import(/* webpackChunkName: "admin-configure-user-group-search" */ '../views/admin/config/form/UserGroupSearch.vue');

const UserCreate = () =>
  import(
    /* webpackChunkName: "admin-configure-user-group-add-user" */
    '../views/admin/config/form/UserCreate.vue'
  );

const UserSearch = () =>
  import(/* webpackChunkName: "admin-configure-user-search" */ '../views/admin/config/form/UserSearch.vue');

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
              { path: 'new-network', name: 'admin.configure.new-network', component: NodeCreate },
              { path: 'node/:id/add-child-node', name: 'admin.configure.node.add-child-node', component: NodeCreate },
              { path: 'node/:id/update', name: 'admin.configure.node.update', component: NodeUpdate },
              { path: 'node/:id/child-search', name: 'admin.configure.node.search', component: NodeSearch },
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
              {
                path: 'node/:id/user-group-search',
                name: 'admin.configure.node.add-child-user-group',
                component: UserGroupSearch,
              },
              { path: 'user-group/:id/add-user', name: 'admin.configure.user-group.add-user', component: UserCreate },
              {
                path: 'user-group/:id/user-search/:operation',
                name: 'admin.configure.user-group.user-search',
                component: UserSearch,
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
