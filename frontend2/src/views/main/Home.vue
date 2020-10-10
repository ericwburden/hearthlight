<template>
  <v-main class="secondary" fill-height>
    <v-parallax :src="require('../../assets/img/boots-fireplace-1600-1000.jpg')">
      <v-row align="center" justify="center">
        <v-col class="text-center" cols="12">
          <h1 class="display-4 mb-4">hearthlight</h1>
          <h4 class="display-1 subheading">welcome home</h4>
        </v-col>
      </v-row>
    </v-parallax>
    <v-container pt-5> <login-form></login-form></v-container>
    <v-spacer></v-spacer>
  </v-main>
</template>

<script lang="ts">
import { Component, Vue } from 'vue-property-decorator';
import LoginForm from '@/components/LoginForm.vue';

@Component({
  components: { LoginForm },
})
export default class Home extends Vue {}
</script>
