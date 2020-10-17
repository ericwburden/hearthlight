<template>
  <v-row>
    <v-col class="py-0">
      <default-date-picker v-model="date" :label="dateLabel"></default-date-picker>
    </v-col>
    <v-col class="py-0">
      <default-time-picker v-model="time" :label="timeLabel"></default-time-picker>
    </v-col>
  </v-row>
</template>

<script lang="ts">
import { Component, Prop, Vue } from 'vue-property-decorator';
import DefaultDatePicker from '@/components/inputs/DefaultDatePicker.vue';
import DefaultTimePicker from '@/components/inputs/DefaultTimePicker.vue';

@Component({ components: { DefaultDatePicker, DefaultTimePicker } })
export default class DefaultDateTimePicker extends Vue {
  @Prop({ type: String, required: true, default: '' }) readonly value!: string;
  @Prop({ type: String, required: false, default: 'Date' }) readonly dateLabel!: string;
  @Prop({ type: String, required: false, default: 'Time' }) readonly timeLabel!: string;

  datePart = this.date;
  timePart = this.time;

  get date() {
    if (!this.value) return '';
    return this.value.split(' ')[0];
  }

  set date(value) {
    this.datePart = value;
    if (this.timePart) {
      this.$emit('input', `${this.datePart} ${this.timePart}`);
    }
  }

  get time() {
    if (!this.value) return '';
    return this.value.split(' ')[1];
  }

  // Returns a datetime in the format YYYY-MM-DD HH:MM
  set time(value) {
    this.timePart = value;
    if (this.datePart) {
      this.$emit('input', `${this.datePart} ${this.timePart}`);
    }
  }
}
</script>
