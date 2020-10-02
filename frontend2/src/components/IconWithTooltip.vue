<template>
  <v-tooltip bottom>
    <template v-slot:activator="{ on, attrs }">
      <v-icon v-bind="attrs" v-on="on">{{ icon }}</v-icon>
    </template>
    <span>{{ msg }}</span>
  </v-tooltip>
</template>

<script lang="ts">
import { Component, Vue } from 'vue-property-decorator';

const IconWithTooltipProps = Vue.extend({
  props: {
    icon: String,
    msg: String,
  },
});

@Component
export default class IconWithTooltip extends IconWithTooltipProps {}
</script>
