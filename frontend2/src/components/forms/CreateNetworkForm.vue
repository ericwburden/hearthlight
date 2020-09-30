<template>
  <v-form v-model="valid" ref="nodeCreateForm" lazy-validation>
    <v-container>
      <v-row>
        <v-col>
          <v-text-field v-model="nodeName" :rules="nameRules" :counter="256" label="Node Name" required></v-text-field>
        </v-col>
        <v-col v-if="!network">
          <v-text-field
            v-model="nodeTypeText"
            :rules="typeRules"
            :counter="64"
            label="Node Type"
            required
          ></v-text-field>
        </v-col>
      </v-row>
      <v-row>
        <v-col class="d-flex justify-end">
          <v-btn color="warning" @click="reset" class="mx-2">Reset</v-btn>
          <v-btn color="success" @click="submit" class="mx-2">Submit</v-btn>
        </v-col>
      </v-row>
    </v-container>
  </v-form>
</template>

<script lang="ts">
/* eslint-disable @typescript-eslint/camelcase */
import { Component, Vue } from 'vue-property-decorator';
import { INodeCreate } from '@/interfaces';
import { dispatchCreateNetwork, dispatchGetNetworks } from '@/store/admin/actions';

const CreateNetworkFormProps = Vue.extend({
  props: {
    network: Boolean,
  },
});

@Component
export default class CreateNetworkForm extends CreateNetworkFormProps {
  public valid = false;
  public nodeName = '';
  public nameRules = [
    (v: string | undefined) => !!v || 'Node Name is required',
    (v: string | undefined) => (v && v.length <= 256) || 'Node Name must be less than 256 characters',
  ];

  public nodeTypeText = '';
  public typeRules = [
    (v: string | undefined) => !!v || 'Node Type is required',
    (v: string | undefined) => (v && v.length <= 64) || 'Node Type must be less than 64 characters',
  ];

  //  Needed to set the correct type in order to make form functions available
  $refs!: {
    nodeCreateForm: HTMLFormElement;
  };

  public async mounted() {
    this.reset();
  }

  public reset() {
    this.nodeName = '';
    this.nodeTypeText = '';
    this.$refs.nodeCreateForm.reset();

    // If the network prop is set, set node_type to 'network'
    if (this.network) {
      this.nodeTypeText = 'network';
    }
  }

  public async submit() {
    if (await this.$refs.nodeCreateForm.validate()) {
      const nodeCreate: INodeCreate = {
        name: this.nodeName,
        node_type: this.nodeTypeText,
      };
      await dispatchCreateNetwork(this.$store, nodeCreate);
      await dispatchGetNetworks(this.$store);
    }
  }
}
</script>
