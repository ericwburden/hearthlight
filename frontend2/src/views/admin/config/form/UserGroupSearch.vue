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
          :items="userGroups"
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
import { INode, IUserGroup, IUserGroupUpdate } from '@/interfaces';
import { readActiveNode, readUserGroups } from '@/store/admin/getters';
import {
  dispatchGetNetworks,
  dispatchGetUserGroups,
  dispatchGetOneNode,
  dispatchUpdateUserGroup,
} from '@/store/admin/actions';

@Component
export default class NodeSearch extends Vue {
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
  ];

  get total(): number {
    return readUserGroups(this.$store).total_records;
  }

  get node(): INode | null {
    return readActiveNode(this.$store);
  }

  get title(): string {
    if (this.node) {
      return `Assign existing user group to: ${this.node.name}`;
    }
    return 'Select an existing node';
  }

  public async mounted() {
    await dispatchGetUserGroups(this.$store, {
      skip: 0,
      limit: this.options.itemsPerPage,
      sortBy: '',
      sortDesc: false,
    });
    await dispatchGetOneNode(this.$store, parseInt(this.$route.params.id));
    this.userGroups = readUserGroups(this.$store).records;
    this.loading = false;
  }

  @Watch('options', { deep: true })
  async onOptionsChange() {
    this.loading = true;
    const { sortBy, sortDesc, page, itemsPerPage } = this.options;

    if (sortBy.length === 1 && sortDesc.length === 1) {
      if (itemsPerPage > 0) {
        const skip = (page - 1) * itemsPerPage;
        await dispatchGetUserGroups(this.$store, {
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

  public rowColor(row: IUserGroup) {
    if (this.selectedRow) {
      return row.id == this.selectedRow.id ? 'success white--text' : '';
    }
    return '';
  }

  public selectRow(row: IUserGroup) {
    this.selectedRow = row;
  }

  public close() {
    this.$router.push('/admin/configure');
  }

  public reset() {
    this.options = {
      page: 1,
      itemsPerPage: 10,
      sortBy: ['name'],
      sortDesc: [false],
      groupBy: [],
      groupDesc: [],
      multiSort: false,
      mustSort: false,
    };
    this.selectedRow = null;
  }

  public async submit() {
    if (this.node && this.selectedRow) {
      const userGroupUpdate: IUserGroupUpdate = {
        /* eslint-disable @typescript-eslint/camelcase */
        node_id: this.node.id,
      };
      await dispatchUpdateUserGroup(this.$store, { id: this.selectedRow.id, object: userGroupUpdate });
    }
    await dispatchGetNetworks(this.$store);
    this.close();
  }
}
</script>
