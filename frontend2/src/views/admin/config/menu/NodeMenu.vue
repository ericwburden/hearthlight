<template>
  <v-sheet>
    <v-sheet class="menu-title" align="center" justify="center">
      <h2 class="font-weight-light mb-3">
        <v-icon color="secondary">{{ props.icon }}</v-icon>
        {{ props.name }}
      </h2>
    </v-sheet>
    <v-row>
      <v-col cols="12" lg="4">
        <v-card outlined>
          <v-card-title class="font-weight-light">Add New</v-card-title>
          <v-container>
            <v-row>
              <v-col>
                <labeled-menu-button
                  use-icon="mdi-google-circles-extended"
                  label="Network"
                  color="success"
                  to="/admin/configure/new-network"
                  icon
                ></labeled-menu-button>
              </v-col>

              <v-col>
                <labeled-menu-button
                  use-icon="mdi-circle-double"
                  label="Child Node"
                  color="success"
                  :to="newNodeRoute"
                  icon
                ></labeled-menu-button>
              </v-col>

              <v-col>
                <labeled-menu-button
                  use-icon="mdi-account-supervisor-circle"
                  label="User Group"
                  color="success"
                  :to="newUserGroupRoute"
                  icon
                ></labeled-menu-button>
              </v-col>
            </v-row>
          </v-container>
        </v-card>
      </v-col>

      <v-col cols="6" lg="4">
        <v-card outlined>
          <v-card-title class="font-weight-light">Assign Existing</v-card-title>
          <v-container>
            <v-row>
              <v-col>
                <labeled-menu-button
                  use-icon="mdi-circle-double"
                  label="Child Node"
                  color="info"
                  :to="existingNodeRoute"
                  icon
                ></labeled-menu-button>
              </v-col>

              <v-col>
                <labeled-menu-button
                  use-icon="mdi-account-supervisor-circle"
                  label="User Group"
                  color="info"
                  :to="existingUserGroupRoute"
                  icon
                ></labeled-menu-button>
              </v-col>
            </v-row>
          </v-container>
        </v-card>
      </v-col>

      <v-col cols="6" lg="4">
        <v-card outlined>
          <v-card-title class="font-weight-light">Other Actions</v-card-title>
          <v-container>
            <v-row>
              <v-col>
                <labeled-menu-button
                  use-icon="mdi-circle-edit-outline"
                  label="Edit"
                  color="info"
                  :to="updateRoute"
                  icon
                ></labeled-menu-button>
              </v-col>

              <v-col>
                <labeled-menu-button
                  use-icon="mdi-layers-remove"
                  label="Delete"
                  color="error"
                  :to="deleteRoute"
                  icon
                ></labeled-menu-button>
              </v-col>
            </v-row>
          </v-container>
        </v-card>
      </v-col>
    </v-row>
  </v-sheet>
</template>

<script lang="ts">
import { Component, Vue } from 'vue-property-decorator';
import LabeledMenuButton from '@/components/buttons/LabeledMenuButton.vue';
import { dispatchGetOneNode } from '@/store/admin/actions';
import { readActiveNode } from '@/store/admin/getters';

@Component({
  inheritAttrs: false,
  components: { LabeledMenuButton },
})
export default class NodeMenu extends Vue {
  public id = this.$route.params.id;
  public props: { id: number; name: string; icon: string } = { id: 0, name: '', icon: '' };

  async mounted() {
    await dispatchGetOneNode(this.$store, parseInt(this.id));
    const parentNode = readActiveNode(this.$store);
    if (parentNode) {
      this.props = {
        id: parentNode.id,
        name: parentNode.name,
        icon: parentNode.node_type == 'network' ? 'mdi-google-circles-extended' : 'mdi-circle-double',
      };
    }
  }

  get newNodeRoute() {
    return `/admin/configure/node/${this.id}/add-child-node`;
  }

  get newUserGroupRoute() {
    return `/admin/configure/node/${this.id}/add-user-group`;
  }

  get existingNodeRoute() {
    return `/admin/configure/node/${this.id}/child-search`;
  }

  get existingUserGroupRoute() {
    return `/admin/configure/node/${this.id}/user-group-search`;
  }

  get updateRoute() {
    return `/admin/configure/node/${this.id}/update`;
  }

  get deleteRoute() {
    return `/admin/configure/node/${this.id}/delete`;
  }
}
</script>

<style scoped>
.v-card__title {
  margin: 4px 16px 4px 8px;
  padding: 0px;
  position: absolute;
  top: -1.5rem;
  background-color: white;
}
</style>
