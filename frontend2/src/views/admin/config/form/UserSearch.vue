<template>
  <v-container>
    <v-row>
      <v-col cols="10">
        <h2>{{ title }}</h2>
      </v-col>
      <v-col class="d-flex justify-end" cols="2">
        <v-btn icon color="error" @click="close()" large><v-icon>mdi-close-circle</v-icon></v-btn>
      </v-col>
    </v-row>
    <v-row>
      <v-col>
        <v-data-table
          :headers="headers"
          :items="users"
          :options.sync="options"
          :server-items-length="total"
          :loading="loading"
          :item-class="rowColor"
          class="elevation-1"
          @click:row="selectRow"
        >
          <template v-slot:[`item.is_active`]="{ item }">
            <v-icon v-if="item.is_active" color="success">mdi-check-circle</v-icon>
            <v-icon v-else color="secondary">mdi-close-circle-outline </v-icon>
          </template>
          <template v-slot:[`item.is_superuser`]="{ item }">
            <v-icon v-if="item.is_superuser" color="success">mdi-check-circle</v-icon>
            <v-icon v-else color="secondary">mdi-close-circle-outline </v-icon>
          </template>
        </v-data-table>
      </v-col>
    </v-row>
    <v-row>
      <v-col class="d-flex justify-end">
        <v-btn color="warning" @click="reset" class="mx-2">Reset</v-btn>
        <v-btn color="success" @click="submit" class="mx-2">Re-Assign</v-btn>
      </v-col>
    </v-row>
  </v-container>
</template>

<script lang="ts">
import { Component, Vue, Watch } from 'vue-property-decorator';
import { DataOptions } from 'vuetify';
import { IUserProfile, IUserGroup } from '@/interfaces';
import { readActiveUserGroup, readUsers } from '@/store/admin/getters';
import {
  dispatchGetNetworks,
  dispatchGetUsersNotInGroup,
  dispatchGetOneUserGroup,
  dispatchAddUserToGroup,
} from '@/store/admin/actions';

@Component
export default class UserSearch extends Vue {
  public skip = 0;
  public limit = 10;
  public loading = true;
  public selectedRow: IUserProfile | null = null;
  public options: DataOptions = {
    page: 1,
    itemsPerPage: 10,
    sortBy: ['email'],
    sortDesc: [false],
    groupBy: [],
    groupDesc: [],
    multiSort: false,
    mustSort: false,
  };
  public users: IUserProfile[] = [];
  public headers = [
    { text: 'ID', sortable: true, value: 'id', align: 'left' },
    { text: 'Email', sortable: true, value: 'email', align: 'center' },
    { text: 'Name', sortable: true, value: 'full_name', align: 'center' },
    { text: 'Active', sortable: false, value: 'is_active', align: 'center' },
    { text: 'Superuser', sortable: true, value: 'is_superuser', align: 'center' },
  ];

  get total(): number {
    return readUsers(this.$store).total_records;
  }

  get parent(): IUserGroup | null {
    return readActiveUserGroup(this.$store);
  }

  get title(): string {
    if (this.parent) {
      return `Assign existing user to: ${this.parent.name}`;
    }
    return 'Select an existing user';
  }

  public async mounted() {
    const userGroupID = parseInt(this.$route.params.id);
    await dispatchGetUsersNotInGroup(this.$store, {
      userGroupID: userGroupID,
      skip: 0,
      limit: this.options.itemsPerPage,
      sortBy: '',
      sortDesc: false,
    });
    await dispatchGetOneUserGroup(this.$store, userGroupID);
    this.users = readUsers(this.$store).records;
    this.loading = false;
  }

  @Watch('options', { deep: true })
  async onOptionsChange() {
    this.loading = true;
    const { sortBy, sortDesc, page, itemsPerPage } = this.options;

    if (sortBy.length === 1 && sortDesc.length === 1) {
      if (itemsPerPage > 0) {
        const skip = (page - 1) * itemsPerPage;
        await dispatchGetUsersNotInGroup(this.$store, {
          userGroupID: parseInt(this.$route.params.id),
          skip: skip,
          limit: itemsPerPage,
          sortBy: sortBy[0],
          sortDesc: sortDesc[0],
        });
        this.users = readUsers(this.$store).records;
      }
    }
    this.loading = false;
  }

  public rowColor(row: IUserProfile) {
    if (this.selectedRow) {
      return row.id == this.selectedRow.id ? 'success white--text' : '';
    }
    return '';
  }

  public selectRow(row: IUserProfile) {
    this.selectedRow = row;
  }

  public close() {
    this.$router.push('/admin/configure');
  }

  public reset() {
    this.options = {
      page: 1,
      itemsPerPage: 10,
      sortBy: ['email'],
      sortDesc: [false],
      groupBy: [],
      groupDesc: [],
      multiSort: false,
      mustSort: false,
    };
    this.selectedRow = null;
  }

  public async submit() {
    if (this.parent && this.selectedRow) {
      await dispatchAddUserToGroup(this.$store, { userGroupID: this.parent.id, userID: this.selectedRow.id });
    }
    await dispatchGetNetworks(this.$store);
    this.close();
  }
}
</script>
