<template>
  <v-container>
    <v-row align="center" justify="center">
      <v-spacer></v-spacer>
      <v-col align="center" justify="center">
        <v-btn class="mt-5" block elevation="2" x-large color="success" @click="createNetwork()">
          <v-icon>mdi-plus-circle-outline</v-icon>
          <span class="ml-2">New Network</span>
        </v-btn>
      </v-col>
      <v-spacer></v-spacer>
    </v-row>
    <v-row>
      <v-col md="6" sm="12" order="1" order-md="2" v-if="showForm">
        <v-card>
          <router-view :key="$route.fullPath"></router-view>
        </v-card>
      </v-col>
      <v-col md="6" sm="12" order="2" order-md="1">
        <v-card v-if="loading">
          <v-container>
            <v-skeleton-loader class="mx-auto" type="heading, list-item@5"></v-skeleton-loader>
          </v-container>
        </v-card>
        <v-card v-else>
          <v-container>
            <h2>Networks</h2>
            <v-treeview
              :items="items"
              :active.sync="active"
              :open.sync="open"
              item-key="key"
              activatable
              color="info"
              transition
              expand-icon="mdi-arrow-down-drop-circle"
              return-object
              ><template v-slot:prepend="{ item }">
                <IconWithTooltip v-if="item.type == 'network'" icon="mdi-google-circles-extended" msg="Network" />
                <IconWithTooltip v-if="item.type == 'node'" icon="mdi-circle-double" msg="Node" />
                <IconWithTooltip
                  v-if="item.type == 'user_group'"
                  icon="mdi-account-supervisor-circle"
                  msg="User Group"
                />
                <IconWithTooltip v-if="item.type == 'interface'" icon="mdi-swap-vertical-circl" msg="Interface" />
              </template>
              <template v-slot:append="{ item }">
                <!-- Node Add New Child Button -->
                <v-tooltip bottom v-if="['network', 'node'].includes(item.type)">
                  <template v-slot:activator="{ on, attrs }">
                    <v-sheet v-bind="attrs" v-on="on" class="d-inline">
                      <v-menu offset-y>
                        <template v-slot:activator="{ on, attrs }">
                          <v-btn v-if="item.id" icon color="success" v-bind="attrs" v-on="on">
                            <v-icon>mdi-layers-plus</v-icon>
                          </v-btn>
                        </template>
                        <v-list>
                          <v-list-item @click="addNodeChild(item)">Node</v-list-item>
                          <v-list-item @click="addUserGroupChild(item)">User Group</v-list-item>
                          <v-list-item @click="selectItem(item)">Interface</v-list-item>
                        </v-list>
                      </v-menu>
                    </v-sheet>
                  </template>
                  <span>Add New Child</span>
                </v-tooltip>

                <!-- Node Assign Existing Child Button -->
                <v-tooltip bottom v-if="['network', 'node'].includes(item.type)">
                  <template v-slot:activator="{ on, attrs }">
                    <v-sheet v-bind="attrs" v-on="on" class="d-inline">
                      <v-menu offset-y>
                        <template v-slot:activator="{ on, attrs }">
                          <v-btn v-if="item.id" icon color="info" v-bind="attrs" v-on="on">
                            <v-icon>mdi-layers-search</v-icon>
                          </v-btn>
                        </template>
                        <v-list>
                          <v-list-item @click="selectExistingNode(item)">Node</v-list-item>
                          <v-list-item @click="selectExistingUserGroup(item)">User Group</v-list-item>
                          <v-list-item @click="selectItem(item)">Interface</v-list-item>
                        </v-list>
                      </v-menu>
                    </v-sheet>
                  </template>
                  <span>Assign Existing Child</span>
                </v-tooltip>

                <!-- User Group Add User Buttons -->
                <v-tooltip bottom v-if="item.type == 'user_group'">
                  <template v-slot:activator="{ on, attrs }">
                    <v-btn v-if="item.id" @click="addUserToGroup(item)" icon color="success" v-bind="attrs" v-on="on">
                      <v-icon>mdi-account-plus</v-icon>
                    </v-btn>
                  </template>
                  <span>Add User</span>
                </v-tooltip>

                <v-tooltip bottom v-if="item.type == 'user_group'">
                  <template v-slot:activator="{ on, attrs }">
                    <v-btn v-if="item.id" @click="selectExistingUser(item)" icon color="info" v-bind="attrs" v-on="on">
                      <v-icon>mdi-account-search</v-icon>
                    </v-btn>
                  </template>
                  <span>Add User</span>
                </v-tooltip>

                <!-- Edit Item Button -->
                <v-tooltip bottom>
                  <template v-slot:activator="{ on, attrs }">
                    <v-btn v-if="item.id" @click="updateItem(item)" icon color="info" v-bind="attrs" v-on="on">
                      <v-icon>mdi-circle-edit-outline</v-icon>
                    </v-btn>
                  </template>
                  <span>Edit</span>
                </v-tooltip>

                <!-- Delete Item Button -->
                <v-tooltip bottom>
                  <template v-slot:activator="{ on, attrs }">
                    <v-btn v-if="item.id" @click="deleteItem(item)" icon color="error" v-bind="attrs" v-on="on">
                      <v-icon>mdi-layers-remove</v-icon>
                    </v-btn>
                  </template>
                  <span>Delete</span>
                </v-tooltip>
              </template>
            </v-treeview>
          </v-container>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script lang="ts">
import { Component, Vue, Watch } from 'vue-property-decorator';
import IconWithTooltip from '@/components/IconWithTooltip.vue';
import { readApplicationModel } from '@/store/admin/getters';
import { dispatchGetNetworks, dispatchUpdateApplicationModelChildren } from '@/store/admin/actions';
import { ApplicationModelEntry } from '@/interfaces';

@Component({
  components: { IconWithTooltip },
})
export default class ConfigureApplication extends Vue {
  loading = true;
  selected: ApplicationModelEntry | null = null;
  open: ApplicationModelEntry[] = [];
  active: ApplicationModelEntry[] = [];

  get items() {
    return readApplicationModel(this.$store);
  }

  get showForm() {
    return this.$route.name != 'admin.configure';
  }

  @Watch('open')
  async onOpen(val: ApplicationModelEntry[], oldVal: ApplicationModelEntry[]) {
    const openedItem = val.find((item) => !oldVal.includes(item));
    if (openedItem) {
      let child;
      for (child of openedItem.children) {
        if (child.type == 'node' || child.type == 'network') {
          await dispatchUpdateApplicationModelChildren(this.$store, child);
        }
      }
    }
  }

  // For now, close all the tree nodes when the form changes
  // in order to provide the opportunity to trigger the 'open'
  // watcher to load in child elements
  @Watch('$route.fullPath')
  async onFormReset() {
    this.open = [];
  }

  public async mounted() {
    await dispatchGetNetworks(this.$store);
    this.loading = false;
  }

  // Functions to manage actions on tree view items
  public selectItem(item: ApplicationModelEntry) {
    this.selected = item;
  }

  public createNetwork() {
    this.$router.push(`/admin/configure/new-network`);
  }

  public addNodeChild(node: ApplicationModelEntry) {
    this.$router.push(`/admin/configure/node/${node.id}/add-child-node`);
  }

  public addUserToGroup(userGroup: ApplicationModelEntry) {
    this.$router.push(`/admin/configure/user-group/${userGroup.id}/add-user`);
  }

  public selectExistingNode(node: ApplicationModelEntry) {
    this.$router.push(`/admin/configure/node/${node.id}/child-search`);
  }

  public selectExistingUserGroup(node: ApplicationModelEntry) {
    this.$router.push(`/admin/configure/node/${node.id}/user-group-search`);
  }

  public selectExistingUser(userGroup: ApplicationModelEntry) {
    this.$router.push(`/admin/configure/user-group/${userGroup.id}/user-search`);
  }

  public updateItem(item: ApplicationModelEntry) {
    this.selectItem(item);
    if (item.type == 'node' || item.type == 'network') {
      this.$router.push(`/admin/configure/node/${item.id}/update`);
    }
    if (item.type == 'user_group') {
      this.$router.push(`/admin/configure/user-group/${item.id}/update`);
    }
  }

  public deleteItem(item: ApplicationModelEntry) {
    this.selectItem(item);
    if (item.type == 'node' || item.type == 'network') {
      this.$router.push(`/admin/configure/node/${item.id}/delete`);
    }
    if (item.type == 'user_group') {
      this.$router.push(`/admin/configure/user-group/${item.id}/delete`);
    }
  }

  public addUserGroupChild(node: ApplicationModelEntry) {
    this.$router.push(`/admin/configure/node/${node.id}/add-user-group`);
  }
}
</script>
