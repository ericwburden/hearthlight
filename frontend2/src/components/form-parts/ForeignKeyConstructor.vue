<template>
  <v-row>
    <v-col class="flex-grow-0" id="switch-col">
      <v-switch inset v-model="show" label="Foreign Key"></v-switch>
    </v-col>
    <transition name="slide-in">
      <v-col class="flex-grow-1 no-padding" v-if="show">
        <v-row>
          <v-col>
            <v-select required :items="tables" label="Table" v-model="table"></v-select>
          </v-col>
          <v-col>
            <v-select
              required
              :items="tableColumns"
              label="Field"
              :loading="loading"
              v-model="field"
              @change="updateValue"
            ></v-select>
          </v-col>
        </v-row>
      </v-col>
    </transition>
  </v-row>
</template>

<script lang="ts">
import { Component, Emit, Prop, Vue, Watch } from 'vue-property-decorator';
import { dispatchGetTableNames, dispatchGetColumnNames } from '@/store/utils/actions';
import { readTableNames, readColumnNames } from '@/store/utils/getters';

@Component
export default class ForeignKeyConstructor extends Vue {
  @Prop({ type: String, required: true, default: '' }) readonly value!: string;
  show = '';
  table = '';
  field = '';
  loading = false;

  get tables(): string[] {
    return readTableNames(this.$store);
  }

  get tableColumns(): string[] {
    return readColumnNames(this.$store);
  }

  get foreignKey(): string {
    return `${this.table}.${this.field}`;
  }

  @Watch('table')
  public async onTableChange(val: string) {
    this.loading = true;
    dispatchGetColumnNames(this.$store, val);
    this.loading = false;
  }

  public async mounted() {
    dispatchGetTableNames(this.$store);
  }

  @Emit('input')
  updateValue() {
    return `${this.table}.${this.field}`;
  }
}
</script>

<style scoped>
#switch-col {
  min-width: 175px;
}

.no-padding {
  padding-top: 0px;
  padding-bottom: 0px;
  padding-left: 0px;
}

.slide-in-enter-active,
.slide-in-leave-active {
  transition: all 0.5s ease;
}
.slide-in-enter,
.slide-in-leave-to {
  opacity: 0;
  transform: translateX(-24px);
}
</style>
