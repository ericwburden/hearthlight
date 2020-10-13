import { RouteConfig } from 'vue-router';

const DefaultMenu = () =>
  import(/* webpackChunkName: "admin-configure-default-menu" */ '@/views/admin/config/menu/DefaultMenu.vue');

const NodeMenu = () =>
  import(/* webpackChunkName: "admin-configure-node-menu" */ '@/views/admin/config/menu/NodeMenu.vue');

const UserGroupMenu = () =>
  import(/* webpackChunkName: "admin-configure-user-group-menu" */ '@/views/admin/config/menu/UserGroupMenu.vue');

const NodeCreate = () =>
  import(/* webpackChunkName: "admin-configure-node-create" */ '../views/admin/config/form/NodeCreate.vue');

const NodeEditFormRoute = () =>
  import(/* webpackChunkName: "admin-configure-node-update" */ '@/components/routes/NodeEditFormRoute.vue');

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

const UserGroupEditFormRoute = () =>
  import(/* webpackChunkName: "admin-configure-user-group-update" */ '@/components/routes/UserGroupEditFormRoute.vue');

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

export const configRoutes: Array<RouteConfig> = [
  // Menus
  { path: '/', name: 'admin.configure.default.menu', component: DefaultMenu },
  { path: 'node/:id', name: 'admin.configure.node.menu', component: NodeMenu },
  { path: 'user-group/:id', name: 'admin.configure.user-group.menu', component: UserGroupMenu },
  { path: 'new-network', name: 'admin.configure.new-network', component: NodeCreate },
  { path: 'node/:id/add-child-node', name: 'admin.configure.node.add-child-node', component: NodeCreate },
  { path: 'node/:id/update', name: 'admin.configure.node.update', component: NodeEditFormRoute },
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
    component: UserGroupEditFormRoute,
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
];
