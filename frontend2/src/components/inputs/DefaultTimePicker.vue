<template>
  <v-menu
    ref="menu"
    v-model="menu"
    :close-on-content-click="false"
    :nudge-right="40"
    :return-value.sync="time"
    transition="scale-transition"
    offset-y
    max-width="290px"
    min-width="290px"
  >
    <template v-slot:activator="{ on, attrs }">
      <v-text-field
        v-model="time"
        :label="label"
        prepend-icon="mdi-clock-time-four-outline"
        readonly
        v-bind="attrs"
        v-on="on"
      ></v-text-field>
    </template>
    <v-time-picker v-if="menu" v-model="time" full-width @click:minute="save"></v-time-picker>
  </v-menu>
</template>

<script lang="ts">
import { Component, Emit, Prop, Vue } from 'vue-property-decorator';

@Component
export default class DefaultTimePicker extends Vue {
  @Prop({ type: String, required: true, default: '' }) readonly value!: string;
  @Prop({ type: String, required: false, default: 'Time' }) readonly label!: string;

  // Needed to set the correct type in order to make form functions available
  $refs!: {
    menu: HTMLFormElement;
  };

  time = this.value;
  menu = false;

  @Emit('input')
  save() {
    this.$refs.menu.save(this.time);
    return this.time;
  }
}
</script>
