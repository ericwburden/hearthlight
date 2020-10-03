<template>
  <v-container>
    <v-row>
      <v-col cols="10">
        <h2>Select an existing node</h2>
      </v-col>
      <v-col class="d-flex justify-end" cols="2">
        <v-btn icon color="error" @click="close()" large><v-icon>mdi-close-circle</v-icon></v-btn>
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
          show-select
          single-select
          class="elevation-1"
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
import { INode } from '@/interfaces';
import { readAdminNodes } from '@/store/admin/getters';
import { dispatchGetNodes } from '@/store/admin/actions';

@Component
export default class NodeSearchForm extends Vue {
  public skip = 0;
  public limit = 10;
  public loading = true;
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
  ];

  get total() {
    return readAdminNodes(this.$store).total_records;
  }

  public async mounted() {
    await dispatchGetNodes(this.$store, [0, this.options.itemsPerPage]);
    this.nodes = readAdminNodes(this.$store).records;
    this.loading = false;
  }

  @Watch('options', { deep: true })
  async onOptionsChange() {
    this.loading = true;
    console.log(this.options);
    const { sortBy, sortDesc, page, itemsPerPage } = this.options;

    if (sortBy.length === 1 && sortDesc.length === 1) {
      this.nodes = this.nodes.sort((a, b) => {
        const sortA = a[sortBy[0]];
        const sortB = b[sortBy[0]];

        if (sortA && sortB) {
          if (sortDesc[0]) {
            if (sortA < sortB) return 1;
            if (sortA > sortB) return -1;
            return 0;
          } else {
            if (sortA < sortB) return -1;
            if (sortA > sortB) return 1;
            return 0;
          }
        }
        return 0;
      });

      if (itemsPerPage > 0) {
        const skip = (page - 1) * itemsPerPage;
        await dispatchGetNodes(this.$store, [skip, itemsPerPage]);
        this.nodes = readAdminNodes(this.$store).records;
      }
    }
    this.loading = false;
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
  }

  public submit() {
    console.log(this.$route.params.id);
  }
}
</script>
