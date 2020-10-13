<template>
  <v-container>
    <v-row>
      <v-col cols="12" sm="6">
        <h2>All Nodes/Networks</h2>
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
        <v-select v-model="searchField" label="Search by..." :items="['Name', 'Type']"></v-select>
      </v-col>
    </v-row>
    <v-row>
      <v-col>
        <v-data-table
          :headers="headers"
          :items="nodes"
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
    <node-edit-form-modal v-model="editDialog" :id="activeNodeInfo.id" max-width="500px" />
    <confirm-delete-modal
      v-model="deleteDialog"
      :type="activeNodeInfo.type"
      :id="activeNodeInfo.id"
      :name="activeNodeInfo.name"
      max-width="500px"
    />
  </v-container>
</template>

<script lang="ts">
/* eslint-disable @typescript-eslint/camelcase */
import { Component, Vue, Watch } from 'vue-property-decorator';
import { DataOptions } from 'vuetify';
import NodeEditFormModal from '@/components/modals/NodeEditFormModal.vue';
import ConfirmDeleteModal from '@/components/modals/ConfirmDeleteModal.vue';
import { INode } from '@/interfaces';
import { readAdminNodes } from '@/store/admin/getters';
import { dispatchGetNodes } from '@/store/admin/actions';

@Component({
  components: { ConfirmDeleteModal, NodeEditFormModal },
})
export default class NodeAllSearch extends Vue {
  public editDialog = false;
  public deleteDialog = false;
  public activeNodeInfo: { id: number; name: string; type: string } = { id: 0, name: '', type: '' };
  public searchTerm = '';
  public searchField = 'Name';
  public skip = 0;
  public limit = 10;
  public loading = true;
  public selectedRow: INode | null = null;
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
  public nodes: INode[] = [];
  public headers = [
    { text: 'ID', sortable: true, value: 'id', align: 'left' },
    { text: 'Parent ID', sortable: true, value: 'parent_id', align: 'left' },
    { text: 'Type', sortable: true, value: 'node_type', align: 'center' },
    { text: 'Name', sortable: true, value: 'name', align: 'center' },
    { text: 'Active', sortable: false, value: 'is_active', align: 'center' },
    { text: 'Actions', value: 'actions', sortable: false, align: 'center' },
  ];

  get total(): number {
    return readAdminNodes(this.$store).total_records;
  }

  get nodeName(): string {
    if (this.searchField == 'Name' && this.searchTerm) {
      return this.searchTerm;
    }
    return '';
  }

  get nodeType(): string {
    if (this.searchField == 'Type' && this.searchTerm) {
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
        await this.refreshNodeStore({
          skip: skip,
          limit: itemsPerPage,
          sortBy: sortBy[0],
          sortDesc: sortDesc[0],
        });
        this.nodes = readAdminNodes(this.$store).records;
      }
    }
    this.loading = false;
  }

  public async refreshNodeStore({
    skip = 0,
    limit = this.options.itemsPerPage,
    sortBy = '',
    sortDesc = false,
  }: { skip?: number; limit?: number; sortBy?: string; sortDesc?: boolean } = {}) {
    await dispatchGetNodes(this.$store, {
      skip: skip,
      limit: limit,
      sortBy: sortBy,
      sortDesc: sortDesc,
      name: this.nodeName,
      node_type: this.nodeType,
    });
  }

  public async mounted() {
    await this.reset();
    this.loading = false;
  }

  public rowColor(row: INode) {
    if (this.selectedRow) {
      return row.id == this.selectedRow.id ? 'accent brown--text font-weight-bold' : '';
    }
    return '';
  }

  public selectRow(row: INode) {
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
    await this.refreshNodeStore();
    this.nodes = readAdminNodes(this.$store).records;
  }

  public showEditModal(item: INode) {
    this.activeNodeInfo = { id: item.id, name: item.name, type: !item.parent_id ? 'network' : 'node' };
    this.editDialog = true;
  }

  public showDeleteModal(item: INode) {
    this.activeNodeInfo = { id: item.id, name: item.name, type: !item.parent_id ? 'network' : 'node' };
    this.deleteDialog = true;
  }

  get showDialogValues() {
    return this.editDialog || this.deleteDialog;
  }

  @Watch('showDialogValues')
  public async refreshOnDialogClose(val: boolean) {
    if (!val) {
      await this.refreshNodeStore();
      this.nodes = readAdminNodes(this.$store).records;
    }
  }
}
</script>
