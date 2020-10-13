<template>
  <v-card class="pa-5">
    <user-edit-form :id="id" v-model="stay"></user-edit-form>
  </v-card>
</template>

<script lang="ts">
import { Component, Vue, Watch } from 'vue-property-decorator';
import UserEditForm from '@/components/forms/UserEditForm.vue';

@Component({ components: { UserEditForm } })
export default class UserEditFormRoute extends Vue {
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
