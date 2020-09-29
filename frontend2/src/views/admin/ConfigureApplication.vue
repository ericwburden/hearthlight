<template>
  <v-container>
    <v-row align="center" justify="center">
      <v-spacer></v-spacer>
      <v-col align="center" justify="center">
        <v-btn class="mt-5" block elevation="2" x-large color="success">
          <v-icon>mdi-plus-circle-outline</v-icon>
          <span class="ml-2">New Network</span>
        </v-btn>
      </v-col>
      <v-spacer></v-spacer>
    </v-row>
  </v-container>
</template>

<script lang="ts">
import { Component, Vue } from 'vue-property-decorator';

@Component({
  components: {},
})
export default class ConfigureApplication extends Vue {}
</script>
