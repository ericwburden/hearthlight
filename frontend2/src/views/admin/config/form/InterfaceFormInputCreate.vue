<template>
  <v-card outlined>
    <v-container>
      <v-row class="d-flex">
        <v-col class=" d-flex flex-grow-1">
          <v-text-field label="Column Name" v-model="columnName" required></v-text-field>
        </v-col>
        <v-col class="d-flex flex-grow-1">
          <v-select
            :items="['Boolean', 'Date', 'DateTime', 'Integer', 'String']"
            label="Column Type"
            v-model="columnType"
            required
          ></v-select>
        </v-col>
        <v-col class="d-flex justify-end align-center flex-grow-0">
          <v-btn color="success" @click="addToColumns">Save</v-btn>
        </v-col>
      </v-row>
      <v-row v-if="columnType == 'String'">
        <v-col>
          <v-text-field label="Maximum length" type="number" v-model="stringMax"></v-text-field>
        </v-col>
      </v-row>
      <foreign-key-constructor v-if="columnType == 'Integer'" v-model="foreignKeyRel"></foreign-key-constructor>
      <v-row v-if="columns.length > 0">
        <v-col>
          <v-data-table
            :headers="headers"
            :items="columns"
            item-key="column_name"
            dense
            hide-default-footer
            show-expand
            single-expand
            :expanded.sync="expanded"
          >
            <template v-slot:[`item.actions`]="{ item }">
              <v-icon class="mx-1" @click.stop="deleteColumn(item)" color="error">
                mdi-delete
              </v-icon>
            </template>
            <template v-slot:expanded-item="{ headers, item }">
              <td :colspan="headers.length" class="py-3">
                <dl>
                  <dt v-if="item.args.length > 0">Args</dt>
                  <dd v-for="arg in item.args" :key="arg">&nbsp;&nbsp;-&nbsp;&nbsp;{{ arg }}</dd>
                </dl>
              </td>
            </template>
          </v-data-table>
        </v-col>
      </v-row>
    </v-container>
  </v-card>
</template>

<script lang="ts">
import { Component, Vue, Watch } from 'vue-property-decorator';
import { FormInputTableColumn } from '@/interfaces/interface-form-input';
import ForeignKeyConstructor from '@/components/form-parts/ForeignKeyConstructor.vue';

@Component({ components: { ForeignKeyConstructor } })
export default class InterfaceFormInputCreate extends Vue {
  /* eslint-disable @typescript-eslint/camelcase */
  expanded = [];
  tableName = '';
  columnName = '';
  columnType = '';
  columnArgs: string[] = [];
  columnKwargs: Record<string, string | boolean> = {};
  columns: FormInputTableColumn[] = [];
  public headers = [
    { text: 'Column Name', sortable: true, value: 'column_name', align: 'left' },
    { text: 'Data Type', sortable: true, value: 'data_type', align: 'center' },
    { text: 'Delete Column', value: 'actions', sortable: false, align: 'center' },
  ];

  stringMax = 256;
  foreignKeyRel = '';

  public addToColumns() {
    const args = [];
    let modifiedColumnType = this.columnType;
    if (this.columnType == 'String') {
      modifiedColumnType = `String(${this.stringMax})`;
    }
    if (this.columnType == 'Integer') {
      args.push(`ForeignKey(${this.foreignKeyRel})`);
    }
    if (this.columnName != '' && this.columnType != '') {
      this.columns.push({
        column_name: this.columnName,
        data_type: modifiedColumnType,
        args: args,
      });
    }
    this.columnName = '';
    this.columnType = '';
    this.showFkFields = '';
    this.foreignKeyTable = '';
    this.foreignKeyField = '';
    this.loadingTableFields = false;
  }

  public deleteColumn(column: FormInputTableColumn) {
    this.columns = this.columns.filter((c) => c != column);
  }
}
</script>
