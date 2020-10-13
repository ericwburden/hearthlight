<template>
  <v-card class="pa-5">
    <node-edit-form :id="id" v-model="stay"></node-edit-form>
  </v-card>
</template>

<script lang="ts">
import { Component, Vue, Watch } from 'vue-property-decorator';
import NodeEditForm from '@/components/forms/NodeEditForm.vue';

@Component({ components: { NodeEditForm } })
export default class NodeEditFormRoute extends Vue {
  public stay = true;
  get id(): number {
    return parseInt(this.$route.params.id);
  }

  @Watch('stay')
  public onStayChange(val: boolean) {
    if (!val) {
      this.$router.back();
    }
  }
}
</script>
