<template>
  <v-container>
    <v-row>
      <v-col cols="12" sm="8">
        <h2>All User Groups</h2>
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
    </v-row>
    <v-row>
      <v-col>
        <v-data-table
          :headers="headers"
          :items="userGroups"
          :options.sync="options"
          :server-items-length="total"
          :loading="loading"
          :item-class="rowColor"
          class="elevation-1"
          @click:row="selectRow"
        >
          <template v-slot:[`item.actions`]="{ item }">
            <v-icon class="mx-1" @click.stop="showEditModal(item)">
              mdi-circle-edit-outline
            </v-icon>
            <v-icon class="mx-1" @click.stop="showDeleteModal(item)">
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
    <user-group-edit-form-modal v-model="editDialog" :id="activeUserGroupInfo.id" max-width="500px" />
    <confirm-delete-modal
      v-model="deleteDialog"
      type="user-group"
      :id="activeUserGroupInfo.id"
      :name="activeUserGroupInfo.name"
      max-width="500px"
    />
  </v-container>
</template>

<script lang="ts">
import { Component, Vue, Watch } from 'vue-property-decorator';
import { DataOptions } from 'vuetify';
import ConfirmDeleteModal from '@/components/modals/ConfirmDeleteModal.vue';
import UserGroupEditFormModal from '@/components/modals/UserGroupEditFormModal.vue';
import { IUserGroup } from '@/interfaces';
import { readUserGroups } from '@/store/admin/getters';
import { dispatchGetUserGroups } from '@/store/admin/actions';

@Component({
  components: { ConfirmDeleteModal, UserGroupEditFormModal },
})
export default class UserGroupAllSearch extends Vue {
  public editDialog = false;
  public deleteDialog = false;
  public activeUserGroupInfo: { id: number; name: string } = { id: 0, name: '' };
  public searchTerm = '';
  public searchField = 'Name';
  public skip = 0;
  public limit = 10;
  public loading = true;
  public selectedRow: IUserGroup | null = null;
  public options: DataOptions = {
    page: 1,
    itemsPerPage: 10,
    sortBy: ['name'],
    sortDesc: [false],
    groupBy: [],
    groupDesc: [],
    multiSort: false,
    mustSort: false,
  };
  public userGroups: IUserGroup[] = [];
  public headers = [
    { text: 'ID', sortable: true, value: 'id', align: 'left' },
    { text: 'Node ID', sortable: true, value: 'node_id', align: 'left' },
    { text: 'Name', sortable: true, value: 'name', align: 'center' },
    { text: 'Actions', value: 'actions', sortable: false, align: 'center' },
  ];

  get total(): number {
    return readUserGroups(this.$store).total_records;
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
        await this.refreshUserGroupStore({
          skip: skip,
          limit: itemsPerPage,
          sortBy: sortBy[0],
          sortDesc: sortDesc[0],
        });
        this.userGroups = readUserGroups(this.$store).records;
      }
    }
    this.loading = false;
  }

  public async refreshUserGroupStore({
    skip = 0,
    limit = this.options.itemsPerPage,
    sortBy = '',
    sortDesc = false,
  }: { skip?: number; limit?: number; sortBy?: string; sortDesc?: boolean } = {}) {
    await dispatchGetUserGroups(this.$store, {
      skip: skip,
      limit: limit,
      sortBy: sortBy,
      sortDesc: sortDesc,
      name: this.searchTerm,
    });
  }

  public async mounted() {
    await this.reset();
    this.loading = false;
  }

  public rowColor(row: IUserGroup) {
    if (this.selectedRow) {
      return row.id == this.selectedRow.id ? 'accent brown--text font-weight-bold' : '';
    }
    return '';
  }

  public selectRow(row: IUserGroup) {
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
    await this.refreshUserGroupStore();
    this.userGroups = readUserGroups(this.$store).records;
  }

  public showEditModal(item: IUserGroup) {
    this.activeUserGroupInfo = { id: item.id, name: item.name };
    this.editDialog = true;
  }

  public showDeleteModal(item: IUserGroup) {
    this.activeUserGroupInfo = { id: item.id, name: item.name };
    this.deleteDialog = true;
  }

  get showDialogValues() {
    return this.editDialog || this.deleteDialog;
  }

  @Watch('showDialogValues')
  public async refreshOnDialogClose(val: boolean) {
    if (!val) {
      await this.refreshUserGroupStore();
      this.userGroups = readUserGroups(this.$store).records;
    }
  }
}
</script>
