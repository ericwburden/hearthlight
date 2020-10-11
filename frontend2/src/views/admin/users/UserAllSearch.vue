<template>
  <v-container>
    <v-row>
      <v-col cols="12" sm="6">
        <h2>All Users</h2>
      </v-col>
      <v-col align="end" justify="end" cols="12" sm="4">
        <v-text-field
          clearable
          v-model="searchTerm"
          append-icon="mdi-magnify"
          label="Search"
          @click:append="search"
          @click:clear="clear"
          @keyup.enter="search"
        ></v-text-field>
      </v-col>
      <v-col cols="12" sm="2">
        <v-select v-model="searchField" label="Search by..." :items="['Full Name', 'Email']"></v-select>
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
          <template v-slot:[`item.actions`]="{ item }">
            <v-icon class="mx-1" @click.stop="showEditForm(item)">
              mdi-circle-edit-outline
            </v-icon>
            <v-icon class="mx-1">
              mdi-delete
            </v-icon>
          </template>
        </v-data-table>
      </v-col>
    </v-row>
    <v-row>
      <v-col class="d-flex justify-end">
        <v-btn color="warning" @click="reset" class="mx-2">Reset</v-btn>
      </v-col>
    </v-row>
    <v-dialog v-model="editDialog" max-width="500px">
      <v-card class="pa-5">
        <user-edit-form :id="activeUserID" @submit="handleEditDialog"></user-edit-form>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script lang="ts">
import { Component, Vue, Watch } from 'vue-property-decorator';
import { DataOptions } from 'vuetify';
import UserEditForm from '@/components/forms/UserEditForm.vue';
import { IUserProfile } from '@/interfaces';
import { readUsers } from '@/store/admin/getters';
import { dispatchGetUsers } from '@/store/admin/actions';

@Component({
  components: { UserEditForm },
})
export default class UserAllSearch extends Vue {
  public editDialog = false;
  public activeUserID: number | null = null;
  public searchTerm = '';
  public searchField = 'Full Name';
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
    { text: 'Actions', value: 'actions', sortable: false, align: 'center' },
  ];

  get total(): number {
    return readUsers(this.$store).total_records;
  }

  get fullName(): string {
    if (this.searchField == 'Full Name' && this.searchTerm) {
      return this.searchTerm;
    }
    return '';
  }

  get email(): string {
    if (this.searchField == 'Email' && this.searchTerm) {
      return this.searchTerm;
    }
    return '';
  }

  public async search() {
    await this.updateTable();
  }

  public async clear() {
    this.searchTerm = '';
    await this.updateTable();
  }

  @Watch('options', { deep: true })
  async onOptionsChange() {
    await this.updateTable();
  }

  public async updateTable() {
    this.loading = true;
    const { sortBy, sortDesc, page, itemsPerPage } = this.options;

    if (sortBy.length === 1 && sortDesc.length === 1) {
      if (itemsPerPage > 0) {
        const skip = (page - 1) * itemsPerPage;
        await this.refreshUserStore({
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

  public async refreshUserStore({
    skip = 0,
    limit = this.options.itemsPerPage,
    sortBy = '',
    sortDesc = false,
  }: { skip?: number; limit?: number; sortBy?: string; sortDesc?: boolean } = {}) {
    await dispatchGetUsers(this.$store, {
      skip: skip,
      limit: limit,
      sortBy: sortBy,
      sortDesc: sortDesc,
      fullName: this.fullName,
      email: this.email,
    });
  }

  public async mounted() {
    await this.reset();
    this.loading = false;
  }

  public rowColor(row: IUserProfile) {
    if (this.selectedRow) {
      return row.id == this.selectedRow.id ? 'accent brown--text font-weight-bold' : '';
    }
    return '';
  }

  public selectRow(row: IUserProfile) {
    this.selectedRow = row;
  }

  public async reset() {
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
    this.searchTerm = '';
    this.selectedRow = null;
    await this.refreshUserStore();
    this.users = readUsers(this.$store).records;
  }

  public showEditForm(item: IUserProfile) {
    this.editDialog = true;
    this.activeUserID = item.id;
  }

  public handleEditDialog(result: boolean) {
    if (result) {
      this.editDialog = false;
    }
  }
}
</script>
