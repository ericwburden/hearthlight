<template>
  <v-container>
    <v-row align="center" justify="center">
      <v-spacer></v-spacer>
      <v-col align="center" justify="center">
        <v-btn class="mt-5" block elevation="2" x-large color="success" @click="showForm('network')">
          <v-icon>mdi-plus-circle-outline</v-icon>
          <span class="ml-2">New Network</span>
        </v-btn>
      </v-col>
      <v-spacer></v-spacer>
    </v-row>
    <v-row>
      <v-col>
        <h2>Networks</h2>
        <v-treeview
          :load-children="fetchChildren"
          activatable
          color="info"
          transition
          :items="items"
          expand-icon="mdi-arrow-down-drop-circle"
        >
          <template v-slot:append="{ item }">
            <!-- Node Button -->
            <v-tooltip bottom v-if="['network', 'node'].includes(item.type)">
              <template v-slot:activator="{ on, attrs }">
                <v-btn v-if="item.id" @click="identify(item)" icon color="success" v-bind="attrs" v-on="on">
                  <v-icon>mdi-playlist-plus</v-icon>
                </v-btn>
              </template>
              <span>Add Child</span>
            </v-tooltip>

            <!-- User Group Button -->
            <v-tooltip bottom v-if="item.type == 'user_group'">
              <template v-slot:activator="{ on, attrs }">
                <v-btn v-if="item.id" @click="identify(item)" icon color="success" v-bind="attrs" v-on="on">
                  <v-icon>mdi-account-plus</v-icon>
                </v-btn>
              </template>
              <span>Add User</span>
            </v-tooltip>

            <v-tooltip bottom>
              <template v-slot:activator="{ on, attrs }">
                <v-btn v-if="item.id" @click="identify(item)" icon color="info" v-bind="attrs" v-on="on">
                  <v-icon>mdi-circle-edit-outline</v-icon>
                </v-btn>
              </template>
              <span>Edit</span>
            </v-tooltip>

            <v-tooltip bottom>
              <template v-slot:activator="{ on, attrs }">
                <v-btn v-if="item.id" @click="identify(item)" icon color="error" v-bind="attrs" v-on="on">
                  <v-icon>mdi-delete</v-icon>
                </v-btn>
              </template>
              <span>Delete</span>
            </v-tooltip>
          </template>
        </v-treeview>
      </v-col>
      <v-divider class="mx-4" vertical></v-divider>
      <v-col>
        <v-row>
          <v-col v-if="form != ''" class="d-flex justify-end">
            <v-btn icon color="error" @click="showForm('')" large><v-icon>mdi-close-circle</v-icon></v-btn>
          </v-col>
        </v-row>
        <v-row>
          <v-col v-if="form == 'network'"><CreateNetworkForm network/></v-col>
        </v-row>
      </v-col>
    </v-row>
  </v-container>
</template>

<script lang="ts">
import { Component, Vue, Watch } from 'vue-property-decorator';
import CreateNetworkForm from '@/components/forms/CreateNetworkForm.vue';
import { readNetworks } from '@/store/admin/getters';
import { dispatchGetNetworks } from '@/store/admin/actions';
import { api } from '@/api';
import { INodeList, INode, INodeChildList, INodeChild } from '@/interfaces';

interface TreeViewEntry {
  id?: number | undefined;
  name: string;
  type: string;
  children?: TreeViewEntry[];
}

@Component({
  components: { CreateNetworkForm },
})
export default class ConfigureApplication extends Vue {
  items: TreeViewEntry[] = [];
  form = '';

  public identify(item: TreeViewEntry) {
    alert(item.id);
  }

  get networks() {
    return readNetworks(this.$store);
  }

  @Watch('networks')
  onNetworksChanged(val: INodeList) {
    this.items = val.nodes.map((network: INode) => {
      return {
        id: network.id,
        type: 'network',
        name: network.name,
        children: [],
      };
    });
  }

  public async mounted() {
    await dispatchGetNetworks(this.$store);
  }

  public parseChildList(cl: INodeChildList) {
    let name = '';
    switch (cl.child_type) {
      case 'user_group':
        name = 'User Groups';
        break;
      case 'node':
        name = 'Nodes';
        break;
      case 'interface':
        name = 'Interfaces';
        break;
      default:
        'Other';
    }
    return {
      name: name,
      type: 'list',
      children: this.parseChildren(cl.children, cl.child_type),
    };
  }

  public parseChildren(children: INodeChild[], type: string) {
    return children.map((c) => {
      return { id: c.child_id, name: c.child_name, type: type, children: [] };
    });
  }

  public async fetchChildren(item: TreeViewEntry) {
    if (item.id) {
      const result = api
        .getNodeChildren(this.$store.getters.token, item.id)
        .then((res) => {
          res.data.child_lists.map((cl) => {
            const child = this.parseChildList(cl);
            console.log(child);
            if (item.children && child) {
              item.children.push(child);
            }
          });
        })
        .catch((err) => console.warn(err));
      console.log(item);
      return result;
    }
  }

  public showForm(formName: string) {
    this.form = formName;
  }
}
</script>
