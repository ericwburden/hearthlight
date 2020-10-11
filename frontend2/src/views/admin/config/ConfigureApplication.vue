<template>
  <v-container align="center" justify="center">
    <v-row align="center" justify="center" ref="menuRow">
      <v-col lg="6" sm="8" xs="12">
        <vertical-slide-fade>
          <router-view :key="$route.fullPath"></router-view>
        </vertical-slide-fade>
      </v-col>
    </v-row>
    <v-row align="center" justify="center">
      <v-col lg="6" sm="8" xs="12" v-if="items.length > 0">
        <v-sheet v-if="loading">
          <v-container>
            <v-skeleton-loader class="mx-auto" type="heading, list-item@5"></v-skeleton-loader>
          </v-container>
        </v-sheet>
        <v-sheet v-else>
          <v-container>
            <v-treeview
              :items="items"
              :active.sync="active"
              :open.sync="open"
              item-key="key"
              activatable
              color="info"
              transition
              expand-icon="mdi-arrow-down-drop-circle"
              return-object
              ><template v-slot:prepend="{ item }">
                <icon-with-tooltip v-if="item.type == 'network'" icon="mdi-google-circles-extended" msg="Network" />
                <icon-with-tooltip v-if="item.type == 'node'" icon="mdi-circle-double" msg="Node" />
                <icon-with-tooltip
                  v-if="item.type == 'user_group'"
                  icon="mdi-account-supervisor-circle"
                  msg="User Group"
                />
                <icon-with-tooltip v-if="item.type == 'interface'" icon="mdi-swap-vertical-circle" msg="Interface" />
              </template>
            </v-treeview>
          </v-container>
        </v-sheet>
      </v-col>
    </v-row>
  </v-container>
</template>

<script lang="ts">
import { Component, Vue, Watch } from 'vue-property-decorator';
import IconWithTooltip from '@/components/IconWithTooltip.vue';
import VerticalSlideFade from '@/components/transition/VerticalSlideFade.vue';
import { readApplicationModel } from '@/store/admin/getters';
import { dispatchGetNetworks, dispatchUpdateApplicationModelChildren } from '@/store/admin/actions';
import { ApplicationModelEntry } from '@/interfaces';

@Component({
  components: { IconWithTooltip, VerticalSlideFade },
})
export default class ConfigureApplication extends Vue {
  loading = true;
  selected: ApplicationModelEntry | null = null;
  open: ApplicationModelEntry[] = [];
  active: ApplicationModelEntry[] = [];

  get items() {
    return readApplicationModel(this.$store);
  }

  @Watch('active')
  async onSelectTreeViewItem(val: ApplicationModelEntry[]) {
    if (val[0]) {
      const id = val[0].id;
      switch (val[0].type) {
        case 'node':
        case 'network':
          this.$router.push(`/admin/configure/node/${id}`);
          break;
        case 'user_group':
          this.$router.push(`/admin/configure/user-group/${id}`);
          break;
        default:
          break;
      }
    }
  }

  @Watch('open')
  async onOpen(val: ApplicationModelEntry[], oldVal: ApplicationModelEntry[]) {
    const openedItem = val.find((item) => !oldVal.includes(item));
    if (openedItem) {
      let child;
      for (child of openedItem.children) {
        if (child.type == 'node' || child.type == 'network') {
          await dispatchUpdateApplicationModelChildren(this.$store, child);
        }
      }
    }
  }

  // For now, close all the tree nodes when the form changes
  // in order to provide the opportunity to trigger the 'open'
  // watcher to load in child elements
  // TODO: Handle changes to the application model better
  @Watch('$route.fullPath')
  async onFormReset(val: string) {
    if (val == '/admin/configure') {
      this.active = [];
      this.open = [];
    }
  }

  public async mounted() {
    await dispatchGetNetworks(this.$store);
    this.loading = false;
  }
}
</script>
