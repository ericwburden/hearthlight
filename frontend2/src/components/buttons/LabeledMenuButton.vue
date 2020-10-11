<template>
  <v-container class="no-padding">
    <v-row>
      <v-col align="center" justify="center" class="btn-col">
        <v-btn @click="go()" v-bind="$attrs">
          <v-icon>{{ useIcon }}</v-icon>
        </v-btn>
      </v-col>
    </v-row>
    <v-row>
      <v-col align="center" justify="center" style="padding-top: 0;">
        <v-sheet>
          <span class="text-caption text--secondary btn-label">{{ label }}</span>
        </v-sheet>
      </v-col>
    </v-row>
  </v-container>
</template>

<script lang="ts">
import { Component, Vue } from 'vue-property-decorator';

const LabeledMenuButtonProps = Vue.extend({
  props: {
    useIcon: String,
    label: String,
    to: String,
  },
});

@Component
export default class LabeledMenuButton extends LabeledMenuButtonProps {
  public go() {
    this.$router.push(this.to);
  }
}
</script>

<style scoped>
.no-padding {
  padding: 0px;
}

.btn-label {
  line-height: 1rem;
  display: inline-block;
}

.btn-col {
  padding-bottom: 2px;
  padding-top: 2px;
}
</style>
