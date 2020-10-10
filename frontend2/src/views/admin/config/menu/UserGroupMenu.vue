<template>
  <v-sheet>
    <v-sheet class="menu-title" align="center" justify="center">
      <h2 class="font-weight-light mb-3">
        <v-icon color="secondary">mdi-account-supervisor-circle</v-icon>
        {{ props.name }}
      </h2>
    </v-sheet>
    <v-row>
      <v-col cols="12" lg="6">
        <v-card outlined>
          <v-card-title class="font-weight-light">Users</v-card-title>
          <v-container>
            <v-row>
              <v-col>
                <labeled-menu-button
                  use-icon="mdi-account-plus"
                  label="Add New"
                  color="success"
                  :to="newUserRoute"
                  icon
                ></labeled-menu-button>
              </v-col>

              <v-col>
                <labeled-menu-button
                  use-icon="mdi-account-search"
                  label="Add Existing"
                  color="info"
                  :to="existingUserRoute"
                  icon
                ></labeled-menu-button>
              </v-col>

              <v-col>
                <labeled-menu-button
                  use-icon="mdi-account-remove"
                  label="Remove"
                  color="error"
                  :to="removeUserRoute"
                  icon
                ></labeled-menu-button>
              </v-col>
            </v-row>
          </v-container>
        </v-card>
      </v-col>

      <v-col>
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
import { dispatchGetOneUserGroup } from '@/store/admin/actions';
import { readActiveUserGroup } from '@/store/admin/getters';

@Component({
  inheritAttrs: false,
  components: { LabeledMenuButton },
})
export default class UserGroupMenu extends Vue {
  public id = this.$route.params.id;
  public props: { id: number; name: string } = { id: 0, name: '' };

  async mounted() {
    await dispatchGetOneUserGroup(this.$store, parseInt(this.id));
    const userGroup = readActiveUserGroup(this.$store);
    if (userGroup) {
      this.props = {
        id: userGroup.id,
        name: userGroup.name,
      };
    }
  }

  get newUserRoute() {
    return `/admin/configure/user-group/${this.id}/add-user`;
  }

  get existingUserRoute() {
    return `/admin/configure/user-group/${this.id}/user-search/add`;
  }

  get removeUserRoute() {
    return `/admin/configure/user-group/${this.id}/user-search/remove`;
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
