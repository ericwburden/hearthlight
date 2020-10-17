<template>
  <v-menu
    ref="menu"
    v-model="menu"
    :close-on-content-click="false"
    transition="scale-transition"
    offset-y
    min-width="290px"
  >
    <template v-slot:activator="{ on, attrs }">
      <v-text-field
        v-model="formattedDate"
        :label="label"
        prepend-icon="mdi-calendar"
        readonly
        v-bind="attrs"
        v-on="on"
      ></v-text-field>
    </template>
    <v-date-picker ref="picker" v-model="date" @change="save"></v-date-picker>
  </v-menu>
</template>

<script lang="ts">
import { Component, Emit, Prop, Vue } from 'vue-property-decorator';

@Component
export default class DefaultDatePicker extends Vue {
  @Prop({ type: String, required: true, default: '' }) readonly value!: string;
  @Prop({ type: String, required: false, default: 'Date' }) readonly label!: string;

  date = this.value;
  menu = false;

  get formattedDate() {
    if (!this.date) return null;
    const [year, month, day] = this.date.split('-');
    return `${month}/${day}/${year}`;
  }

  @Emit('input')
  save() {
    return this.date;
  }
}
</script>
