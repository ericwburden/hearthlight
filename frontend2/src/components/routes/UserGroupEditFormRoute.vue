<template>
  <v-card class="pa-5">
    <user-group-edit-form :id="id" v-model="stay"></user-group-edit-form>
  </v-card>
</template>

<script lang="ts">
import { Component, Vue, Watch } from 'vue-property-decorator';
import UserGroupEditForm from '@/components/forms/UserGroupEditForm.vue';

@Component({ components: { UserGroupEditForm } })
export default class UserGroupEditFormRoute extends Vue {
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
