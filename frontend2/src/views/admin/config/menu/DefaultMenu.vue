<template>
  <v-sheet>
    <v-row>
      <v-col align="center" justify="center">
        <v-btn @click="createNetwork()" fab x-large color="success">
          <v-icon>mdi-google-circles-extended</v-icon>
        </v-btn>
      </v-col>
    </v-row>
    <v-row>
      <v-col align="center" justify="center" style="padding-top: 0;">
        <v-sheet>
          <span class="text-caption text--secondary">Add New Network</span>
        </v-sheet>
      </v-col>
    </v-row>
  </v-sheet>
</template>

<script lang="ts">
import { Component, Vue } from 'vue-property-decorator';

@Component
export default class DefaultMenu extends Vue {
  public createNetwork() {
    this.$router.push(`/admin/configure/new-network`);
  }
}
</script>
