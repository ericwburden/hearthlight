<template>
  <v-dialog v-model="localValue" v-bind="$attrs">
    <v-card class="pa-5">
      <node-edit-form :id="id" v-model="localValue"></node-edit-form>
    </v-card>
  </v-dialog>
</template>

<script lang="ts">
import { Component, Prop, Vue } from 'vue-property-decorator';
import NodeEditForm from '@/components/forms/NodeEditForm.vue';

@Component({ components: { NodeEditForm } })
export default class NodeEditFormModal extends Vue {
  @Prop(Number) readonly id: number | undefined;
  @Prop({ type: Boolean, required: true, default: false }) readonly value!: boolean;

  get localValue() {
    return this.value;
  }

  set localValue(value) {
    this.$emit('input', value);
  }
}
</script>
