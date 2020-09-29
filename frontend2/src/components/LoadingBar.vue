<template>
  <div>
    <v-progress-linear
      :active="loading"
      :indeterminate="loading"
      absolute
      bottom
      :color="currentLoadingColor"
      :v-model="show"
    >
      <template v-slot="{ currentLoadingMessage }">
        <strong>{{ currentLoadingMessage }}%</strong>
      </template>
    </v-progress-linear>
  </div>
</template>

<script lang="ts"></script>
