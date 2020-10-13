<template>
  <v-dialog v-model="localValue" v-bind="$attrs">
    <v-card class="pa-5">
      <user-group-edit-form :id="id" v-model="localValue"></user-group-edit-form>
    </v-card>
  </v-dialog>
</template>

<script lang="ts">
import { Component, Prop, Vue } from 'vue-property-decorator';
import UserGroupEditForm from '@/components/forms/UserGroupEditForm.vue';

@Component({ components: { UserGroupEditForm } })
export default class UserGroupEditFormModal extends Vue {
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
