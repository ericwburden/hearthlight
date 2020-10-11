<template>
  <v-dialog v-model="localValue" v-bind="$attrs">
    <v-card class="pa-5">
      <user-edit-form :id="id" v-model="localValue"></user-edit-form>
    </v-card>
  </v-dialog>
</template>

<script lang="ts">
import { Component, Prop, Vue } from 'vue-property-decorator';
import UserEditForm from '@/components/forms/UserEditForm.vue';

@Component({ components: { UserEditForm } })
export default class ConfirmDeleteModal extends Vue {
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
