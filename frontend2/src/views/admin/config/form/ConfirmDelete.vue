<template>
  <v-container>
    <v-row>
      <v-col align="center" justify="center">
        <h2>Really delete {{ props.type }} - {{ props.name }}?</h2>
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
import { Component, Vue } from 'vue-property-decorator';
import {
  dispatchGetOneNode,
  dispatchDeleteNode,
  dispatchGetOneUserGroup,
  dispatchDeleteUserGroup,
  dispatchGetNetworks,
} from '@/store/admin/actions';
import { readActiveNode, readActiveUserGroup } from '@/store/admin/getters';

@Component
export default class ConfirmDelete extends Vue {
  public props: { id: number; name: string; type: string } = { id: -1, name: '', type: '' };
  public inType = this.$route.params.type;
  public inID = parseInt(this.$route.params.id);

  public async mounted() {
    let item = null;
    let printType = '';
    if (this.inType == 'node') {
      await dispatchGetOneNode(this.$store, this.inID);
      item = readActiveNode(this.$store);
      printType = 'Node';
    }

    if (this.inType == 'user-group') {
      await dispatchGetOneUserGroup(this.$store, this.inID);
      item = readActiveUserGroup(this.$store);
      printType = 'User Group';
    }

    if (item) {
      this.props = { id: this.inID, name: item.name, type: printType };
    }
  }

  public close() {
    this.$router.back();
  }

  public async confirm() {
    if (this.inType == 'node') {
      await dispatchDeleteNode(this.$store, this.inID);
    }
    if (this.inType == 'user-group') {
      await dispatchDeleteUserGroup(this.$store, this.inID);
    }

    await dispatchGetNetworks(this.$store);
    this.close();
  }
}
</script>
