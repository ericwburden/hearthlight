<template>
  <v-container class="white">
    <v-row>
      <v-col align="center" justify="center">
        <h2>Really delete {{ printType }} - {{ name }}?</h2>
      </v-col>
    </v-row>
    <v-row>
      <v-col class="d-flex justify-end">
        <v-btn x-large color="warning" @click="close">Cancel</v-btn>
      </v-col>
      <v-col>
        <v-btn x-large color="error" @click="confirm">Delete</v-btn>
      </v-col>
    </v-row>
  </v-container>
</template>

<script lang="ts">
import { Component, Emit, Prop, Vue } from 'vue-property-decorator';
import { dispatchDeleteNode, dispatchDeleteUserGroup, dispatchDeleteUser } from '@/store/admin/actions';

@Component
export default class ConfirmDelete extends Vue {
  @Prop(Number) readonly id: number | undefined;
  @Prop(String) readonly name: string | undefined;
  @Prop(String) readonly type: string | undefined;
  public printType = '';

  public async mounted() {
    switch (this.type) {
      case 'node':
        this.printType = 'Node';
        break;
      case 'network':
        this.printType = 'Network';
        break;
      case 'user-group':
        this.printType = 'User Group';
        break;
      case 'user':
        this.printType = 'User';
        break;
      case 'interface':
      case 'form_input_interface':
      case 'query_interface':
        this.printType = 'Interface';
        break;
      default:
        this.printType = 'Undefined';
    }
  }

  public async confirm() {
    if (this.id) {
      switch (this.type) {
        case 'network':
        case 'node':
          await dispatchDeleteNode(this.$store, this.id);
          break;
        case 'user-group':
          await dispatchDeleteUserGroup(this.$store, this.id);
          break;
        case 'user':
          await dispatchDeleteUser(this.$store, this.id);
          break;
        case 'interface':
          alert('Implement Me!'); // TODO: Implement this
          break;
      }
    }
    this.close();
  }

  @Emit('input')
  public close() {
    return false;
  }
}
</script>
