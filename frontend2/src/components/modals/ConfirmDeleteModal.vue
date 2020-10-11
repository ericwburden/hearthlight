<template>
  <v-dialog v-model="localValue" v-bind="$attrs"
    ><confirm-delete v-model="localValue" :id="id" :name="name" :type="type"
  /></v-dialog>
</template>

<script lang="ts">
import { Component, Prop, Vue } from 'vue-property-decorator';
import ConfirmDelete from '@/components/forms/ConfirmDelete.vue';

@Component({ components: { ConfirmDelete } })
export default class ConfirmDeleteModal extends Vue {
  @Prop(Number) readonly id: number | undefined;
  @Prop(String) readonly name: string | undefined;
  @Prop(String) readonly type: string | undefined;
  @Prop({ type: Boolean, required: true, default: false }) readonly value!: boolean;

  get localValue() {
    return this.value;
  }

  set localValue(value) {
    this.$emit('input', value);
  }
}
</script>
